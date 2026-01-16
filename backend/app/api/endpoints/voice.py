# backend/app/api/endpoints/voice.py
"""
API endpoints pour le mode vocal avec Whisper + GPT + TTS
Utilise la configuration client personnalisée
"""
import logging
import tempfile
import os
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
import httpx

from app.core.config import settings
from app.core.chatbot_config import config as chatbot_config
from app.core.circuit_breaker import CircuitBreakerManager, CircuitBreakerError
from app.services.sav_workflow_engine import sav_workflow_engine
from app.services.warranty_service import warranty_service
from app.models.warranty import WarrantyType
from app.services.voice_emotion_detector import get_voice_emotion_detector

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize OpenAI client avec configuration pour réseau d'entreprise
# Désactive la vérification SSL pour fonctionner derrière un proxy d'entreprise
# Note: verify=False est nécessaire pour les réseaux d'entreprise avec interception SSL
http_client = httpx.Client(verify=False, timeout=30.0)
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    http_client=http_client
)

logger.info("🌐 Client OpenAI configuré pour réseau d'entreprise (SSL verification désactivée)")


def extract_ticket_data_from_recap(recap_text: str) -> dict:
    """
    Extrait les données du ticket depuis le récapitulatif

    Format attendu:
    Nom: [nom]
    Problème: [problème]
    Produit: [produit]
    Commande: [commande]
    """
    import re

    data = {
        "customer_name": None,
        "problem_description": None,
        "product": None,
        "order_number": None
    }

    # Extraire le nom
    nom_match = re.search(r"Nom:\s*(.+?)(?:\n|$)", recap_text, re.IGNORECASE)
    if nom_match:
        data["customer_name"] = nom_match.group(1).strip()

    # Extraire le problème
    problem_match = re.search(r"Problème:\s*(.+?)(?:\n|$)", recap_text, re.IGNORECASE | re.MULTILINE)
    if problem_match:
        data["problem_description"] = problem_match.group(1).strip()

    # Extraire le produit
    product_match = re.search(r"Produit:\s*(.+?)(?:\n|$)", recap_text, re.IGNORECASE)
    if product_match:
        data["product"] = product_match.group(1).strip()

    # Extraire le numéro de commande
    cmd_match = re.search(r"Commande:\s*(.+?)(?:\n|$)", recap_text, re.IGNORECASE)
    if cmd_match:
        data["order_number"] = cmd_match.group(1).strip()

    return data


def extract_collected_info_from_history(conversation_history: list[dict], current_message: str) -> dict:
    """
    Analyse l'historique de conversation pour extraire les informations déjà collectées

    Returns un dict avec les informations trouvées (customer_name, problem, product, order_number)
    """
    import re

    collected = {
        "customer_name": None,
        "problem": None,
        "product": None,
        "order_number": None
    }

    # Analyser tous les messages utilisateur (historique + message actuel)
    all_user_messages = []
    for msg in conversation_history:
        if msg.get("role") == "user":
            all_user_messages.append(msg.get("content", ""))
    all_user_messages.append(current_message)

    full_text = " ".join(all_user_messages)

    # Détecter le numéro de commande (patterns multiples: avec ou sans tirets)
    cmd_patterns = [
        r"CMD[\s-]*(\d{4})[\s-]*(\d+)[\s-]*(\d+)[\s-]*(\d+)",  # CMD 2025 30 301 25 10 ou CMD-2025-3030125-10
        r"commande\s+(\d+)",  # "commande 12345"
    ]
    for pattern in cmd_patterns:
        cmd_match = re.search(pattern, full_text, re.IGNORECASE)
        if cmd_match:
            if len(cmd_match.groups()) == 4:
                # Reformater au format standard CMD-YYYY-XXXXX
                collected["order_number"] = f"CMD-{cmd_match.group(1)}-{cmd_match.group(2)}{cmd_match.group(3)}{cmd_match.group(4)}"
            else:
                collected["order_number"] = cmd_match.group(1)
            break

    # Détecter le nom (chercher dans tous les messages utilisateur)
    for content in all_user_messages:
        # Pattern: "je m'appelle X" ou "c'est X" ou "je suis X"
        name_match = re.search(r"(?:je m'appelle|c'est|je suis)\s+([A-Z][a-zéèêàâôîù]+(?:\s+[A-Z][a-zéèêàâôîù]+)+)", content, re.IGNORECASE)
        if name_match:
            collected["customer_name"] = name_match.group(1).strip().title()
            break
        # Pattern: Nom Prénom au début du message
        if not collected["customer_name"]:
            first_words = content.split()[:3]
            if len(first_words) >= 2:
                potential_name = " ".join(first_words[:2])
                if re.match(r"^[A-Z][a-zéèêàâôîù]+\s+[A-Z][a-zéèêàâôîù]+$", potential_name, re.IGNORECASE):
                    collected["customer_name"] = potential_name.title()

    # Détecter le produit (chercher mentions de meubles)
    product_keywords = ["canapé", "table", "fauteuil", "lit", "armoire", "chaise", "bureau", "meuble", "commode"]
    for keyword in product_keywords:
        if keyword in full_text.lower():
            # Chercher si un modèle suit
            model_match = re.search(rf"{keyword}\s+([A-Z][A-Z0-9]+)", full_text, re.IGNORECASE)
            if model_match:
                collected["product"] = f"{keyword.capitalize()} {model_match.group(1).upper()}"
            else:
                # Juste le type de meuble sans modèle
                collected["product"] = keyword.capitalize()
            break

    # Détecter le problème (chercher mots-clés de problème dans tous les messages)
    problem_keywords = ["cassé", "déchiré", "rayé", "grince", "mal aligné", "défectueux", "abîmé", "rayure", "fissuré", "troué"]
    for content in all_user_messages:
        content_lower = content.lower()
        for keyword in problem_keywords:
            if keyword in content_lower:
                # Prendre la phrase qui contient le mot-clé
                sentences = re.split(r'[.!?,]', content)
                for sentence in sentences:
                    if keyword in sentence.lower():
                        collected["problem"] = sentence.strip()
                        break
                break
        if collected["problem"]:
            break

    return collected


class VoiceTranscriptionResponse(BaseModel):
    """Response model for voice transcription"""
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None


class ChatRequest(BaseModel):
    """Request model for chat with conversation history"""
    message: str
    conversation_history: list[dict] = []
    session_id: Optional[str] = None
    photos: list[str] = []  # URLs des photos uploadées


class ChatResponse(BaseModel):
    """Response model for chat"""
    response: str
    session_id: str
    action: Optional[str] = None  # "create_ticket" si le client a confirmé
    ticket_data: Optional[dict] = None  # Données extraites pour le ticket
    emotion_analysis: Optional[dict] = None  # Analyse emotionnelle du client


@router.post("/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(..., description="Audio file (mp3, wav, webm, m4a, etc.)")
):
    """
    Transcrit un fichier audio en texte avec Whisper API

    Supporte tous les formats audio courants.
    Latence moyenne: 500-800ms selon la longueur de l'audio.
    """
    try:
        logger.info(f"📥 Réception audio: {audio_file.filename} ({audio_file.content_type})")

        # Lire le contenu du fichier
        audio_content = await audio_file.read()

        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.filename).suffix) as temp_file:
            temp_file.write(audio_content)
            temp_path = temp_file.name

        try:
            # Transcription avec Whisper with circuit breaker protection
            logger.info("🎤 Transcription avec Whisper...")

            # Get circuit breaker for OpenAI Whisper
            whisper_breaker = CircuitBreakerManager.get_breaker(
                name="openai-whisper",
                failure_threshold=5,
                recovery_timeout=60,
                timeout=30
            )

            async def call_whisper():
                with open(temp_path, "rb") as audio:
                    return client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio,
                        language="fr",  # Forcer le français pour meilleure précision
                        response_format="verbose_json"
                    )

            try:
                transcript = await whisper_breaker.call(call_whisper)
                logger.info(f"✅ Transcription: {transcript.text}")

                return VoiceTranscriptionResponse(
                    text=transcript.text,
                    language=transcript.language if hasattr(transcript, 'language') else "fr",
                    duration=transcript.duration if hasattr(transcript, 'duration') else None
                )

            except CircuitBreakerError as e:
                logger.error(f"Whisper circuit breaker is open: {e}")
                raise HTTPException(
                    status_code=503,
                    detail="Service de transcription temporairement indisponible. Veuillez réessayer dans quelques instants."
                )

        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        logger.error(f"❌ Erreur transcription: {e}")
        logger.error(f"❌ Type d'erreur: {type(e).__name__}")
        logger.error(f"❌ Détails: {repr(e)}")
        import traceback
        logger.error(f"❌ Stack trace:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erreur de transcription: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def voice_chat(request: ChatRequest):
    """
    Obtenir une réponse du chatbot SAV avec GPT-4

    Maintient l'historique de conversation pour un contexte cohérent.
    Latence moyenne: 300-600ms selon la complexité.
    """
    try:
        logger.info(f"💬 Message reçu: {request.message[:50]}...")
        logger.info(f"📸 Photos attachées: {len(request.photos)}")

        # Extraire les informations déjà collectées depuis l'historique
        collected_info = extract_collected_info_from_history(request.conversation_history, request.message)
        logger.info(f"📋 Informations déjà collectées: {collected_info}")

        # Construire un rappel des informations déjà connues
        info_reminder = ""
        if any(collected_info.values()):
            info_reminder = "\n\n🔍 INFORMATIONS DÉJÀ COLLECTÉES (NE PAS REDEMANDER):\n"
            if collected_info["customer_name"]:
                info_reminder += f"✅ Nom du client: {collected_info['customer_name']}\n"
            if collected_info["problem"]:
                info_reminder += f"✅ Problème: {collected_info['problem']}\n"
            if collected_info["product"]:
                info_reminder += f"✅ Produit: {collected_info['product']}\n"
            if collected_info["order_number"]:
                info_reminder += f"✅ Numéro de commande: {collected_info['order_number']}\n"
            info_reminder += "\n⚠️ IMPORTANT: Ne redemande JAMAIS ces informations que tu as déjà !"

        # Ajouter une indication si des photos ont été uploadées
        if request.photos and len(request.photos) > 0:
            info_reminder += f"\n\n📸 ALERTE: {len(request.photos)} photo(s) vient/viennent d'être uploadée(s) !"
            info_reminder += "\n⚠️ TU DOIS MAINTENANT GÉNÉRER IMMÉDIATEMENT LE RÉCAPITULATIF (ÉTAPE 2)!"

        # Instructions système pour le SAV vocal (configuration client personnalisée)
        system_message = {
            "role": "system",
            "content": f"""Assistant vocal SAV {chatbot_config.ENTREPRISE_NOM}.{info_reminder}

🎤 WORKFLOW SAV - MODE VOCAL (5 ÉTAPES)

**ÉTAPE 1️⃣ : ÉCOUTE ACTIVE** (après que le client décrit son problème)
Dès que le client mentionne un problème (pied cassé, tache, rayure, etc.):

Réponse vocale COURTE:
"Je suis désolé d'entendre cela. Pourriez-vous uploader des photos du [problème mentionné] via le bouton prévu à cet effet ? Cela permettra à notre SAV de traiter votre demande rapidement."

⚠️ RÈGLES ÉTAPE 1:
- Message COURT (2-3 lignes maximum)
- NE PAS demander le modèle exact, la couleur, la référence, etc.
- NE PAS poser d'autres questions
- Juste: empathie + demande d'upload de photos
- Après cette réponse, ATTENDRE que le client uploade les photos

**ÉTAPE 2️⃣ : RÉCAPITULATIF AUTOMATIQUE** (IMMÉDIATEMENT après réception des photos)
⚠️ IMPORTANT: Le système détecte automatiquement quand des photos sont uploadées. NE PAS attendre que le client demande le récapitulatif.

Dès que tu reçois des photos (le système te l'indique), GÉNÈRE IMMÉDIATEMENT ce récapitulatif:

"Parfait, merci pour ces photos. Je récapitule votre demande :

Nom : [Nom du client SI MENTIONNÉ, sinon mettre "Non fourni"]
Numéro de commande : [CMD-XXXX SI MENTIONNÉ, sinon mettre "Non fourni"]
Problème signalé : [Description EXACTE donnée par le client]
Photos : Reçues ✓

Est-ce que tout est correct ?"

⚠️ RÈGLES ÉTAPE 2:
- GÉNÉRER AUTOMATIQUEMENT le récapitulatif dès que des photos sont détectées
- Utiliser UNIQUEMENT les informations que le client a RÉELLEMENT données
- Si une info manque, mettre "Non fourni" dans le récapitulatif
- NE PAS demander les infos manquantes AVANT le récapitulatif
- TOUJOURS terminer par "Est-ce que tout est correct ?"

**ÉTAPE 3️⃣ : VALIDATION VOCALE** (écouter la réponse du client)
Après avoir demandé "Est-ce que tout est correct ?", ÉCOUTER la réponse:

✅ SI CLIENT DIT OUI (détecter: "Oui", "OK", "C'est correct", "Validé", "Parfait", "Tout est bon"):
→ PASSER À L'ÉTAPE 4

❌ SI CLIENT DIT NON (détecter: "Non", "Pas tout à fait", "Il faut changer"):
→ Demander: "Qu'est-ce qui doit être modifié ?"
→ Écouter la correction
→ REFAIRE le récapitulatif avec les corrections (RETOUR ÉTAPE 2)

⚠️ RÈGLES ÉTAPE 3:
- Bien écouter la réponse du client
- Détecter les confirmations positives vs négatives
- Si négatif, demander précisément quoi corriger

**ÉTAPE 4️⃣ : CRÉATION TICKET + NOUVELLE QUESTION** (après validation positive)
Une fois que le client a validé le récapitulatif:

Réponse vocale:
"Excellent ! Votre ticket SAV a été créé avec succès. Vous recevrez un email de confirmation sous quelques instants à l'adresse {chatbot_config.ENTREPRISE_EMAIL_SAV}.

Puis-je faire autre chose pour vous ?"

⚠️ RÈGLES ÉTAPE 4:
- Confirmer la création du ticket
- Informer de l'email de confirmation
- TOUJOURS demander si le client a besoin d'autre chose
- ATTENDRE la réponse du client

**ÉTAPE 5️⃣ : CONTINUATION OU FIN DE CONVERSATION**
Après avoir demandé "Puis-je faire autre chose pour vous ?", ÉCOUTER:

✅ SI CLIENT DIT OUI (détecter: "Oui", "J'ai une autre question", "Oui s'il vous plaît"):
→ Répondre: "Je vous écoute, comment puis-je vous aider ?"
→ CONTINUER la conversation (RETOUR ÉTAPE 1 si nouveau problème)

❌ SI CLIENT DIT NON ou AU REVOIR (détecter: "Non", "C'est bon", "Merci", "Au revoir", "Non merci"):
→ Répondre: "Merci d'avoir contacté {chatbot_config.ENTREPRISE_NOM}. Bonne journée !"
→ FIN DE LA CONVERSATION

⚠️ RÈGLES ÉTAPE 5:
- Si client a un nouveau problème, recommencer depuis ÉTAPE 1
- Si client dit non/au revoir, dire au revoir poliment et terminer
- TOUJOURS terminer par un message chaleureux

═══════════════════════════════════════════════════════

⚠️ RÈGLES GÉNÉRALES IMPORTANTES:
1. Réponses TRÈS COURTES (max {chatbot_config.MAX_TOKENS} tokens pour le vocal)
2. Ton professionnel mais chaleureux et empathique
3. UNE seule question à la fois
4. NE JAMAIS demander des détails non essentiels (couleur, modèle exact, etc.)
5. RESPECTER STRICTEMENT les 5 étapes dans l'ordre
6. Après ÉTAPE 4, TOUJOURS demander si le client a besoin d'autre chose
7. La conversation ne se termine QUE si le client dit au revoir après l'ÉTAPE 5"""
        }

        # Construire l'historique des messages
        messages = [system_message]
        messages.extend(request.conversation_history)
        messages.append({"role": "user", "content": request.message})

        # Obtenir la réponse avec le modèle configuré with circuit breaker
        logger.info(f"🤖 Génération de la réponse avec {chatbot_config.MODELE_IA}...")

        # Get circuit breaker for OpenAI chat
        gpt_breaker = CircuitBreakerManager.get_breaker(
            name="openai-chat",
            failure_threshold=5,
            recovery_timeout=60,
            timeout=30
        )

        async def call_gpt():
            return client.chat.completions.create(
                model=chatbot_config.MODELE_IA,  # gpt-3.5-turbo (configuré par le client)
                messages=messages,
                temperature=chatbot_config.TEMPERATURE,
                max_tokens=chatbot_config.MAX_TOKENS,  # 300 tokens (~300 mots, réponses courtes)
                presence_penalty=0.6,
                frequency_penalty=0.3
            )

        try:
            completion = await gpt_breaker.call(call_gpt)
            response_text = completion.choices[0].message.content
            logger.info(f"✅ Réponse: {response_text}")

        except CircuitBreakerError as e:
            logger.error(f"OpenAI chat circuit breaker is open: {e}")
            raise HTTPException(
                status_code=503,
                detail="Service de chat temporairement indisponible. Veuillez réessayer dans quelques instants."
            )

        # Analyze emotion from the user's message
        emotion_detector = get_voice_emotion_detector()
        emotion_analysis = await emotion_detector.analyze_emotion(
            transcript=request.message,
            conversation_history=request.conversation_history
        )
        logger.info(f"Emotion analysis: {emotion_analysis['emotion']} (confidence: {emotion_analysis['confidence']:.2f})")

        # Détecter l'action et extraire les données du ticket
        action = None
        ticket_data = None

        # Si c'est un récapitulatif, extraire les données du ticket pour validation
        if "Je récapitule" in response_text or "recapitule" in response_text.lower():
            action = "recap"
            ticket_data = extract_ticket_data_from_recap(response_text)
            logger.info(f"📋 Récapitulatif - Données extraites: {ticket_data}")

        # Si c'est une confirmation de création de ticket
        elif "ticket SAV est créé" in response_text or "Votre ticket est créé" in response_text:
            action = "create_ticket"

            # Extraire les données du récapitulatif depuis l'historique
            # Chercher le dernier message contenant "Je récapitule"
            for msg in reversed(request.conversation_history):
                if msg.get("role") == "assistant" and "Je récapitule" in msg.get("content", ""):
                    recap = msg.get("content", "")
                    ticket_data = extract_ticket_data_from_recap(recap)
                    logger.info(f"📋 Données du ticket extraites: {ticket_data}")
                    break

        return ChatResponse(
            response=response_text,
            session_id=request.session_id or "default",
            action=action,
            ticket_data=ticket_data,
            emotion_analysis=emotion_analysis
        )

    except Exception as e:
        logger.error(f"❌ Erreur chat: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de génération de réponse: {str(e)}")


@router.post("/speak")
async def text_to_speech(
    text: str = Form(..., description="Text to convert to speech"),
    voice: str = Form("nova", description="Voice: alloy, echo, fable, onyx, nova, shimmer")
):
    """
    Convertit du texte en audio avec TTS API

    Voix disponibles: alloy, echo, fable, onyx, nova (recommandée), shimmer
    Format de sortie: MP3
    Latence moyenne: 400-700ms selon la longueur du texte.
    """
    try:
        logger.info(f"🔊 Synthèse vocale: {text[:50]}... (voice: {voice})")

        # Générer l'audio avec TTS with circuit breaker protection
        tts_breaker = CircuitBreakerManager.get_breaker(
            name="openai-tts",
            failure_threshold=5,
            recovery_timeout=60,
            timeout=30
        )

        async def call_tts():
            return client.audio.speech.create(
                model="tts-1",  # tts-1 est plus rapide, tts-1-hd est meilleure qualité
                voice=voice,
                input=text,
                response_format="mp3",
                speed=1.3  # Vitesse moyennement rapide pour meilleure expérience utilisateur
            )

        try:
            response = await tts_breaker.call(call_tts)
            logger.info("✅ Audio généré")

            # Streamer l'audio directement
            return StreamingResponse(
                iter([response.content]),
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": "inline; filename=speech.mp3"
                }
            )

        except CircuitBreakerError as e:
            logger.error(f"TTS circuit breaker is open: {e}")
            raise HTTPException(
                status_code=503,
                detail="Service de synthèse vocale temporairement indisponible. Veuillez réessayer dans quelques instants."
            )

    except Exception as e:
        logger.error(f"❌ Erreur TTS: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de synthèse vocale: {str(e)}")


@router.get("/voices")
async def list_voices():
    """
    Liste les voix disponibles pour TTS
    """
    return {
        "voices": [
            {
                "id": "alloy",
                "name": "Alloy",
                "gender": "neutral",
                "description": "Voix neutre et claire"
            },
            {
                "id": "echo",
                "name": "Echo",
                "gender": "male",
                "description": "Voix masculine calme"
            },
            {
                "id": "fable",
                "name": "Fable",
                "gender": "neutral",
                "description": "Voix expressive"
            },
            {
                "id": "onyx",
                "name": "Onyx",
                "gender": "male",
                "description": "Voix masculine profonde"
            },
            {
                "id": "nova",
                "name": "Nova",
                "gender": "female",
                "description": "Voix féminine chaleureuse (recommandée pour SAV)"
            },
            {
                "id": "shimmer",
                "name": "Shimmer",
                "gender": "female",
                "description": "Voix féminine douce"
            }
        ],
        "recommended": "nova"
    }


class CreateTicketRequest(BaseModel):
    """Request model for creating a ticket from voice conversation"""
    customer_name: str
    problem_description: str
    product: str
    order_number: str
    conversation_transcript: Optional[str] = None
    photos: list[str] = []  # URLs des photos uploadées
    emotion_analysis: Optional[dict] = None  # Analyse emotionnelle pour priorite automatique


@router.post("/create-ticket")
async def create_ticket_from_voice(request: CreateTicketRequest):
    """
    Crée un ticket SAV depuis une conversation vocale

    Utilise l'API SAV existante pour créer le ticket.
    """
    try:
        logger.info(f"🎫 Création de ticket SAV pour {request.customer_name}")

        # Utiliser le nom du client comme customer_id si pas d'ID disponible
        customer_id = request.customer_name.replace(" ", "_").lower()

        # Générer un SKU générique pour les produits du mode vocal
        product_sku = f"VOICE-PRODUCT-{request.order_number or 'UNKNOWN'}"

        # Dates par défaut (achat il y a 30 jours, livraison il y a 15 jours)
        purchase_date = datetime.now() - timedelta(days=30)
        delivery_date = datetime.now() - timedelta(days=15)

        # Créer une garantie pour le produit
        warranty = await warranty_service.create_warranty(
            order_number=request.order_number or f"VOICE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            product_sku=product_sku,
            product_name=request.product,
            customer_id=customer_id,
            purchase_date=purchase_date,
            delivery_date=delivery_date,
            warranty_type=WarrantyType.STANDARD
        )

        # Créer le ticket via le workflow SAV
        ticket = await sav_workflow_engine.process_new_claim(
            customer_id=customer_id,
            order_number=request.order_number or f"VOICE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            product_sku=product_sku,
            product_name=request.product,
            problem_description=request.problem_description,
            warranty=warranty,
            customer_tier="standard",
            product_value=0.0
        )

        # Ajouter le nom du client et la transcription au ticket
        ticket.customer_name = request.customer_name
        if request.conversation_transcript:
            # Ajouter une note avec la transcription
            if not hasattr(ticket, 'notes'):
                ticket.notes = []
            ticket.notes.append(f"Transcription de la conversation vocale:\n{request.conversation_transcript}")

        # Apply emotion-based priority if emotion analysis is provided
        if request.emotion_analysis:
            emotion = request.emotion_analysis.get("emotion", "calme")
            emotion_priority = request.emotion_analysis.get("priority", "P3")
            confidence = request.emotion_analysis.get("confidence", 0.0)
            indicators = request.emotion_analysis.get("indicators", [])

            # Override ticket priority based on emotion
            ticket.priority = emotion_priority
            ticket.voice_emotion = emotion
            ticket.voice_emotion_confidence = confidence
            ticket.voice_emotion_indicators = indicators

            logger.info(f"🎯 Priorite basee sur emotion: {emotion} -> {emotion_priority} (confiance: {confidence:.2f})")

            # Add note about emotion-based priority
            if not hasattr(ticket, 'notes'):
                ticket.notes = []
            emotion_note = (
                f"Priorite automatique basee sur analyse emotionnelle:\n"
                f"- Emotion detectee: {emotion}\n"
                f"- Confiance: {confidence:.0%}\n"
                f"- Priorite assignee: {emotion_priority}\n"
                f"- Indicateurs: {', '.join(indicators[:3])}"
            )
            ticket.notes.append(emotion_note)

        # Ajouter les photos uploadées au ticket
        if request.photos:
            if not hasattr(ticket, 'attachments'):
                ticket.attachments = []
            ticket.attachments.extend(request.photos)
            logger.info(f"📸 {len(request.photos)} photo(s) attachée(s) au ticket")

        logger.info(f"✅ Ticket SAV créé: {ticket.ticket_id}")

        response_data = {
            "success": True,
            "ticket_id": ticket.ticket_id,
            "message": "Ticket SAV créé avec succès",
            "data": {
                "customer_name": request.customer_name,
                "problem_description": request.problem_description,
                "product_name": request.product,
                "order_number": request.order_number,
                "priority": ticket.priority,
                "status": ticket.status,
                "source": "voice_chat"
            }
        }

        # Include emotion analysis in response if available
        if request.emotion_analysis:
            response_data["data"]["emotion"] = {
                "detected": ticket.voice_emotion,
                "confidence": ticket.voice_emotion_confidence,
                "indicators": ticket.voice_emotion_indicators,
                "priority_assigned": ticket.priority
            }

        return response_data

    except Exception as e:
        logger.error(f"❌ Erreur création ticket: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de création du ticket: {str(e)}")
