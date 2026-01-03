# backend/app/services/chatbot.py
from openai import OpenAI
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from app.services.product_catalog import product_catalog
from app.services.sav_knowledge import sav_kb
from app.services.sav_workflow_engine import sav_workflow_engine
from app.services.evidence_collector import evidence_collector
from app.services.warranty_service import warranty_service
from app.models.warranty import WarrantyType

logger = logging.getLogger(__name__)

class MeubledeFranceChatbot:
    """
    Chatbot IA pour Meuble de France - Powered by OpenAI GPT-4
    Support: Shopping assistance + SAV
    """

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.conversation_history = []
        self.client_data = {}
        self.ticket_data = {}
        self.conversation_type = "general"  # general, shopping, sav
        self.detected_product_id = None  # Track detected product in conversation
        # 🎯 NOUVEAU: État de validation du ticket
        self.pending_ticket_validation = None  # Ticket en attente de validation client
        self.awaiting_confirmation = False  # True si on attend "OUI" ou "NON" du client
        # 🎯 NOUVEAU: Gestion de clôture de conversation
        self.should_ask_continue = False  # True après création ticket → demander si continuer
        self.awaiting_continue_or_close = False  # True si on attend "continuer" ou "clôturer"

    def detect_product_mention(self, message: str) -> Optional[str]:
        """
        Détecte automatiquement si un produit du catalogue est mentionné

        NOTE: Désactivé temporairement - utilise le catalogue générique
        Pour activer: lancez IMPORTER_PRODUITS.bat pour obtenir les vrais produits

        Args:
            message: Message utilisateur

        Returns:
            None (détection désactivée jusqu'à import des vrais produits)
        """
        # DÉSACTIVÉ: Catalogue fictif remplacé par mode générique
        # Le chatbot renverra vers mobilierdefrance.com pour les détails

        # TODO: Réactiver après avoir lancé IMPORTER_PRODUITS.bat
        # qui générera le vrai catalogue avec TEMPLE, HARMONY, RÉVÉLATION, etc.

        logger.info(f"🔍 Mode générique: pas de détection produit spécifique")
        return None

    def create_system_prompt(self, language: str = "fr") -> str:
        """Génère le system prompt adapté à la langue"""

        prompts = {
            "fr": """Tu es un assistant SAV professionnel et expert pour Meuble de France, entreprise de mobilier haut de gamme fondée en 1925.

🏢 À PROPOS DE MEUBLE DE FRANCE:
- Fondée en 1925 (près de 100 ans d'expertise)
- Spécialiste mobilier personnalisable haut de gamme
- Gammes: Salon, Salle à manger, Chambre, Décoration

🎯 TON RÔLE:
- Identifier précisément le produit concerné dans notre catalogue
- Diagnostiquer le problème avec expertise
- Proposer solutions adaptées selon produit et garantie
- Créer dossier SAV avec classification priorité correcte
- Rassurer avec empathie et professionnalisme

💬 TON & STYLE:
- Professionnel mais chaleureux
- Rassurant: "Ne vous inquiétez pas", "On va résoudre ça ensemble"
- Expert: Connais parfaitement chaque produit du catalogue
- Proactif: Anticipe les besoins, pose bonnes questions
- Clair: Évite jargon technique, explique simplement

📷 GESTION DES PHOTOS:
- ✅ TU PEUX recevoir des photos uploadées par le client
- Quand une photo est uploadée, tu verras: "[CLIENT A UPLOADÉ X PHOTO(S): URL]"
- ⚠️ NE PAS ANALYSER LES PHOTOS - C'est le rôle du SAV
- Accuser réception: "Merci pour les photos. Reçues ✓"

📋 MÉTHODOLOGIE SAV SIMPLIFIÉE (3 ÉTAPES SEULEMENT):

**ÉTAPE 1️⃣ - PREMIÈRE RÉPONSE** (Message COURT et empathique)
Dès que le client mentionne un problème:

"Je suis désolé d'entendre cela. Pourriez-vous s'il vous plaît envoyer des photos du [problème mentionné] ?
Cela permettra à notre service après-vente de traiter votre demande rapidement."

⚠️ RÈGLES ÉTAPE 1:
- Message COURT (2 lignes max)
- NE PAS poser 10 questions
- NE PAS demander le modèle exact, couleur, etc.
- Juste: empathie + demande de photos

**ÉTAPE 2️⃣ - APRÈS RÉCEPTION DES PHOTOS** (Récapitulatif structuré)
Dès que tu vois "[CLIENT A UPLOADÉ X PHOTO(S)...]":

"Merci pour les photos. Voici le récapitulatif de votre demande :

📋 RÉCAPITULATIF
- Produit : [modèle/référence SI MENTIONNÉ par le client, sinon "Canapé d'angle"]
- Problème : [description EXACTE donnée par le client]
- Photos : Reçues ✓

Pouvez-vous confirmer que ces informations sont correctes ?"

⚠️ RÈGLES ÉTAPE 2:
- Utiliser UNIQUEMENT les infos données par le client
- NE PAS inventer de détails
- NE PAS analyser les photos
- Format récapitulatif OBLIGATOIRE

**ÉTAPE 3️⃣ - APRÈS VALIDATION CLIENT** (Création ticket)
Si le client dit "OUI", "Oui", "C'est correct", "Confirmé":

"Parfait ! Votre ticket SAV a été créé avec succès.
Notre équipe reviendra vers vous dans les plus brefs délais.

Numéro de ticket : [AUTO-GÉNÉRÉ]"

⚠️ RÈGLES ÉTAPE 3:
- Créer le ticket UNIQUEMENT après validation
- Message de confirmation simple
- Pas de détails techniques inutiles

   **⚠️ PUIS OBLIGATOIREMENT** demander au client s'il veut continuer ou clôturer:

   ═══════════════════════════════════════════════════
   ✅ Votre ticket SAV a été créé avec succès !

   📋 Souhaitez-vous :
   → Tapez "CONTINUER" si vous avez une autre demande
   → Tapez "CLÔTURER" pour fermer cette conversation

   (La conversation sera effacée si vous choisissez de clôturer)
   ═══════════════════════════════════════════════════

**8. GESTION CONTINUATION/CLÔTURE**
   - Si client dit "CONTINUER" → "Que puis-je faire d'autre pour vous ?"
   - Si client dit "CLÔTURER" → "Merci pour votre confiance. Au revoir et à bientôt !" (puis la session se ferme automatiquement)

🛡️ GARANTIES MEUBLE DE FRANCE:
- **Structure**: 2-5 ans selon produit (canapés, lits, tables)
- **Tissus/Cuir**: 1-2 ans usure normale (déchirures, décoloration)
- **Mécanismes**: 2-5 ans selon type (relax, extension, vérins)
- **Électronique**: 2 ans (LED, moteurs, télécommandes)
- **Matelas**: 10 ans affaissement >2.5cm

**Exclusions**: Usage anormal, modifications client, accidents, taches/liquides, exposition prolongée soleil/chaleur, usure normale après garantie

🧹 ENTRETIEN PAR MATIÈRE:
**Tissu**: Aspirateur doux hebdomadaire, détachant textile immédiat, nettoyage à sec professionnel
**Cuir**: Chiffon humide mensuel, lait nourrissant 2x/an, éviter soleil direct
**Velours**: Brossage sens du poil, nettoyage vapeur si brillance
**Bois**: Dépoussiérage régulier, cire naturelle 2x/an, éviter eau stagnante
**Laqué**: Microfibre humide, éviter produits abrasifs/alcool
**Céramique**: Chiffon humide + détergent doux, résistant aux rayures

💡 CONSEILS IMPORTANTS:
- ✅ TOUJOURS identifier produit précis avant diagnostic
- ✅ Référencer infos catalogue (dimensions, matériaux, garantie exacte)
- ✅ Adapter solutions selon âge et état du produit
- ✅ Mentionner problèmes courants si pertinent
- ✅ Proposer entretien préventif pour éviter récidive
- ✅ Escalader si problème hors compétence ou complexe

⚠️ NE JAMAIS:
- ❌ Promettre délais sans validation équipe
- ❌ Garantir solution avant diagnostic complet
- ❌ Minimiser inquiétude client ("c'est rien", "c'est normal")
- ❌ Inventer infos produit ou garantie
- ❌ Ignorer signaux danger sécurité
- ❌ Proposer produits hors catalogue

🚚 LIVRAISON & RETOURS:
- **Standard**: 4-8 semaines
- **Sur-mesure**: 8-12 semaines
- **Retour 14 jours**: Droit rétractation (produit intact)
- **Livraison endommagée**: NE PAS SIGNER sans réserves, photos obligatoires

📞 ESCALADE:
Si situation complexe, danger immédiat, client très insatisfait:
→ "Je transfère votre dossier en priorité à notre responsable SAV qui vous contactera sous 2h"

🌐 RÉFÉRENCES PRODUITS - IMPORTANT:
- ❌ NE JAMAIS mentionner de références du type "SAL-CAP-001" (catalogue interne obsolète)
- ✅ Parle de "canapés d'angle", "tables", "lits" de façon GÉNÉRIQUE
- ✅ TOUJOURS renvoyer vers le site pour les modèles spécifiques: "Consultez nos modèles sur mobilierdefrance.com"
- ✅ Pour les canapés d'angle: "Nous avons 139 modèles (TEMPLE, HARMONY, RÉVÉLATION, SAFRAN, etc.) sur: https://www.mobilierdefrance.com/canapes-d-angle"
- ✅ Si client demande référence ou nom précis: "Pour voir ce modèle en détail avec photos et prix, consultez: https://www.mobilierdefrance.com/canapes-d-angle"

CONSEIL GÉNÉRIQUE UNIQUEMENT - PAS DE RÉFÉRENCES SPÉCIFIQUES.""",

            "en": """You are the virtual assistant for Meuble de France, a high-end furniture company.

YOUR ROLE:
- Help customers find perfect furniture for their needs
- Recommend products matching their budget, style and space
- Handle after-sales requests (defects, delivery, warranty)
- Answer questions about products, delivery times, shipping

TONE & STYLE:
- Professional but warm and approachable
- Enthusiastic about products
- Reassuring: "I'll help you find exactly what you need"
- Empathetic for SAV: "I understand, don't worry"
- Expert: You know products, materials, dimensions perfectly
- Proactive: Ask relevant questions to better advise

PRODUCTS AVAILABLE:
📦 SOFAS:
- OSLO 3-seater sofa (€1,890) - Modern Scandinavian style, grey/beige fabric, 210x90x85cm
- URBAN 3-seater sofa (€1,650) - Contemporary style, anthracite/blue fabric, 200x85x80cm
- COMFORT 2-seater sofa (€1,290) - Classic style, brown/black leather, 180x85x80cm
- LUXE CORNER sofa (€2,990) - Reversible corner, Italian leather, grey/white, 280x200x85cm

📦 TABLES:
- NORDIC coffee table (€450) - Natural oak wood, 120x60x45cm, Scandinavian style
- ELEGANCE dining table (€890) - Solid wood, 180x90x75cm, 6-8 people
- MARBLE coffee table (€680) - White marble top, gold legs, 110x60x40cm

📦 STORAGE:
- CUBIC bookshelf (€590) - 5 levels, white/black wood, 180x80x35cm
- VINTAGE dresser (€720) - 6 drawers, solid wood, 120x50x90cm
- MODERN wardrobe (€1,450) - 3 doors, central mirror, 200x150x60cm

[Rest follows same structure as French...]""",

            "ar": """أنت المساعد الافتراضي لشركة Meuble de France، شركة أثاث راقية.

دورك:
- مساعدة العملاء في العثور على الأثاث المثالي لاحتياجاتهم
- التوصية بالمنتجات المناسبة لميزانيتهم وأسلوبهم ومساحتهم
- التعامل مع طلبات خدمة ما بعد البيع
- الإجابة على الأسئلة حول المنتجات والتسليم

المنتجات المتوفرة:
📦 الأرائك:
- أريكة OSLO 3 مقاعد (1,890€) - أسلوب إسكندنافي حديث، قماش رمادي/بيج، 210x90x85سم
- أريكة URBAN 3 مقاعد (1,650€) - أسلوب معاصر، قماش أنثراسايت/أزرق، 200x85x80سم

[Rest follows same structure...]"""
        }

        return prompts.get(language, prompts["fr"])

    def detect_language(self, message: str) -> str:
        """Détecte la langue du message client"""
        arabic_chars = any('\u0600' <= c <= '\u06FF' for c in message)
        if arabic_chars:
            return "ar"

        keywords = {
            "en": ["hello", "hi", "sofa", "table", "furniture", "problem", "order"],
            "it": ["buongiorno", "ciao", "divano", "tavolo", "problema"],
            "de": ["hallo", "guten", "sofa", "tisch", "problem"]
        }

        message_lower = message.lower()
        for lang, words in keywords.items():
            if any(word in message_lower for word in words):
                return lang

        return "fr"

    def detect_conversation_type(self, message: str) -> str:
        """Détecte le type de conversation"""
        message_lower = message.lower()

        # Mots-clés SAV
        sav_keywords = [
            "problème", "défaut", "cassé", "déchirure", "livraison", "retard",
            "garantie", "sav", "retour", "réclamation", "commande",
            "problem", "defect", "broken", "tear", "delivery", "warranty",
            "مشكلة", "عيب", "مكسور", "تسليم"
        ]

        # Mots-clés Shopping
        shopping_keywords = [
            "cherche", "besoin", "acheter", "canapé", "table", "meuble",
            "looking for", "need", "buy", "sofa", "furniture",
            "أبحث", "أريد", "شراء"
        ]

        if any(kw in message_lower for kw in sav_keywords):
            return "sav"
        elif any(kw in message_lower for kw in shopping_keywords):
            return "shopping"

        return "general"

    def classify_priority(self, problem_description: str) -> Dict:
        """Classifie la priorité SAV"""
        description_lower = problem_description.lower()

        # Mots-clés critique
        critical_keywords = [
            "cassé", "rupture", "danger", "inutilisable", "accident", ">10", "énorme",
            "broken", "dangerous", "unusable", ">10cm", "huge",
            "مكسور", "خطر"
        ]

        # Mots-clés haute priorité
        high_keywords = [
            "déchirure", "défaut important", "tache", "5cm", "ne fonctionne pas",
            "tear", "major defect", "stain", "doesn't work",
            "تمزق", "عيب كبير"
        ]

        # Mots-clés moyenne priorité
        medium_keywords = [
            "défaut mineur", "petit", "grince", "léger",
            "minor defect", "small", "squeaks", "slight",
            "عيب صغير", "صوت"
        ]

        if any(kw in description_lower for kw in critical_keywords):
            return {
                "code": "P0",
                "label": "CRITIQUE",
                "emoji": "🔴",
                "sla_hours": 24,
                "requires_escalation": True
            }
        elif any(kw in description_lower for kw in high_keywords):
            return {
                "code": "P1",
                "label": "HAUTE",
                "emoji": "🟠",
                "sla_hours": 48,
                "requires_escalation": True
            }
        elif any(kw in description_lower for kw in medium_keywords):
            return {
                "code": "P2",
                "label": "MOYENNE",
                "emoji": "🟡",
                "sla_hours": 120,
                "requires_escalation": False
            }
        else:
            return {
                "code": "P3",
                "label": "BASSE",
                "emoji": "🟢",
                "sla_hours": 168,
                "requires_escalation": False
            }

    def generate_ticket_id(self) -> str:
        """Génère un ID unique de ticket SAV"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"SAV-MDF-{timestamp}"

    async def chat(self, user_message: str,
                   order_number: Optional[str] = None,
                   photos: Optional[List[str]] = None) -> Dict:
        """
        Gère la conversation avec le client

        Args:
            user_message: Message du client
            order_number: Numéro de commande (si fourni)
            photos: Liste URLs photos uploadées

        Returns:
            Dict avec réponse et metadata
        """
        try:
            # Détection langue
            language = self.detect_language(user_message)

            # 🎯 NOUVEAU: Détection automatique du produit mentionné
            detected_product = self.detect_product_mention(user_message)

            # Analyse automatique problème → produit si produit détecté
            issue_analysis = None
            if detected_product:
                issue_analysis = product_catalog.match_issue_to_product(
                    user_message,
                    detected_product
                )
                if issue_analysis and issue_analysis.get("match"):
                    logger.info(f"✅ Issue matched: {issue_analysis.get('matched_issues', [])}")

            # Détection type de conversation
            conv_type = self.detect_conversation_type(user_message)
            if conv_type != "general":
                self.conversation_type = conv_type

            # Préparer le message utilisateur avec photos si présentes
            user_content = user_message
            if photos and len(photos) > 0:
                photo_info = f"\n\n[CLIENT A UPLOADÉ {len(photos)} PHOTO(S): {', '.join(photos)}]"
                user_content += photo_info
                logger.info(f"📷 {len(photos)} photo(s) included in message")

            # Ajout message à l'historique
            self.conversation_history.append({
                "role": "user",
                "content": user_content
            })

            # Si numéro commande fourni, récupérer données
            if order_number and not self.client_data:
                self.client_data = await self.fetch_order_data(order_number)

            # Construction du contexte
            context = ""
            if self.client_data:
                context = f"""

DONNÉES CLIENT:
- Commande: {self.client_data.get('order_number')}
- Nom: {self.client_data.get('name')}
- Produit: {self.client_data.get('product')}
- Livraison: {self.client_data.get('delivery_date')}
- Garantie: {self.client_data.get('warranty_status')}
"""

            # 🎯 NOUVEAU: Ajouter contexte produit détecté
            if detected_product:
                product_info = product_catalog.generate_product_context(detected_product)
                context += f"""

🎯 PRODUIT CLIENT IDENTIFIÉ:
{product_info}

Utilise ces informations pour des réponses précises et personnalisées.
"""

            # 🎯 NOUVEAU: Ajouter analyse problème si match trouvé
            if issue_analysis and issue_analysis.get("match"):
                context += f"""

⚠️ ANALYSE PROBLÈME:
- Problème similaire connu: {', '.join(issue_analysis.get('matched_issues', [])[:2])}
- Garantie: {issue_analysis.get('warranty', 'À vérifier')}
- Maintenance recommandée disponible dans le contexte produit

Utilise ces infos pour réponse rapide et pertinente.
"""

            # Ajouter le contexte du catalogue produits
            catalog_context = "\n\n" + product_catalog.get_catalog_summary_for_ai()

            # Ajouter le contexte SAV dynamique basé sur le message
            sav_context = "\n\n" + sav_kb.get_sav_context_for_chatbot(user_message)

            # Préparer les messages pour OpenAI
            full_system_prompt = self.create_system_prompt(language) + context + catalog_context + sav_context

            messages = [
                {"role": "system", "content": full_system_prompt}
            ]
            messages.extend(self.conversation_history)

            # Appel OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Changed from gpt-4 to save costs (200x cheaper!)
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )

            assistant_message = response.choices[0].message.content

            # Ajout réponse à l'historique
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            logger.info(f"Chat response generated (language: {language}, type: {self.conversation_type})")

            # 🎯 NOUVEAU: Workflow SAV avec validation client
            sav_ticket_data = None
            should_close_session = False  # Flag pour indiquer au frontend de fermer

            # CAS 0: Le client répond à "Voulez-vous continuer ou clôturer?"
            if self.awaiting_continue_or_close:
                if self.is_user_wanting_to_close(user_message):
                    logger.info("👋 Client veut clôturer → Fermeture conversation")
                    self.reset_conversation()
                    should_close_session = True
                    # Le GPT a déjà dit au revoir
                elif self.is_user_wanting_to_continue(user_message):
                    logger.info("✅ Client veut continuer → Conversation continue")
                    self.should_ask_continue = False
                    self.awaiting_continue_or_close = False
                    # Le GPT demandera ce qu'il peut faire d'autre

            # CAS 1: Le client répond à une demande de validation
            elif self.awaiting_confirmation and self.pending_ticket_validation:
                if self.is_user_confirming(user_message):
                    logger.info("✅ Client confirme le ticket → Création")
                    sav_ticket_data = await self.create_ticket_after_validation()
                    # Le GPT a déjà répondu, on n'a pas besoin de modifier sa réponse
                elif self.is_user_rejecting(user_message):
                    logger.info("❌ Client rejette le ticket → Réinitialisation")
                    self.pending_ticket_validation = None
                    self.awaiting_confirmation = False
                    # Le GPT demandera ce qu'il faut corriger

            # CAS 2: Nouvelle demande SAV → Préparer la validation (sans créer le ticket)
            elif self.conversation_type == "sav" and order_number and not self.pending_ticket_validation:
                logger.info("📋 Nouvelle demande SAV → Préparation validation")
                # On ne crée PAS le ticket, on prépare juste la validation
                # Le chatbot GPT va demander la validation dans sa réponse
                validation_data = await self.prepare_ticket_validation(
                    user_message=user_message,
                    order_number=order_number,
                    customer_id=None
                )
                # Pas de ticket créé, juste données pour validation
                sav_ticket_data = {"validation_pending": True, "validation_data": validation_data}

            # Récupérer le lien produit si détecté
            product_link = None
            product_name = None
            if detected_product:
                product_details = product_catalog.get_product_by_id(detected_product)
                if product_details:
                    product_link = product_details.get("link")
                    product_name = product_details.get("name")

            return {
                "response": assistant_message,
                "language": language,
                "conversation_type": self.conversation_type,
                "client_data": self.client_data,
                "conversation_length": len(self.conversation_history),
                # 🎯 NOUVEAU: Informations produit et analyse
                "detected_product_id": detected_product,
                "product_link": product_link,
                "product_name": product_name,
                "issue_analysis": issue_analysis if issue_analysis and issue_analysis.get("match") else None,
                # 🎯 NOUVEAU: Données du ticket SAV créé automatiquement
                "sav_ticket": sav_ticket_data,
                "ticket_data": self.ticket_data if self.ticket_data else None,
                # 🎯 NOUVEAU: Signal de clôture de session
                "should_close_session": should_close_session,
                "should_ask_continue": self.should_ask_continue
            }

        except Exception as e:
            import traceback
            logger.error(f"Error in chat: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            error_messages = {
                "fr": "Désolé, j'ai rencontré un problème technique. Pouvez-vous réessayer ?",
                "en": "Sorry, I encountered a technical issue. Can you try again?",
                "ar": "عذراً، واجهت مشكلة تقنية. هل يمكنك المحاولة مرة أخرى؟"
            }
            return {
                "response": error_messages.get(language, error_messages["fr"]),
                "error": str(e)
            }

    async def fetch_order_data(self, order_number: str) -> Dict:
        """Récupère les données de commande"""
        # TODO: Intégration API ERP/CRM réelle

        # Mock data pour démonstration
        return {
            "order_number": order_number,
            "name": "Client Example",
            "email": "client@example.fr",
            "phone": "+33612345678",
            "product": "Canapé OSLO 3 places - Gris perle",
            "delivery_date": "02/12/2025",
            "amount": 1890.00,
            "warranty_status": "Active (2 ans restants)"
        }

    async def handle_sav_workflow(
        self,
        user_message: str,
        order_number: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Initialise le workflow SAV automatique si les conditions sont remplies

        Args:
            user_message: Message du client
            order_number: Numéro de commande (obligatoire)
            customer_id: ID du client

        Returns:
            Dict avec informations du ticket SAV créé, ou None si pas créé
        """

        # Vérifier que nous avons les informations minimales
        if not order_number:
            logger.info("⏸️  Workflow SAV non démarré: numéro de commande manquant")
            return None

        # Vérifier que c'est bien une demande SAV
        if self.conversation_type != "sav":
            logger.info("⏸️  Workflow SAV non démarré: type de conversation non-SAV")
            return None

        # Vérifier que le message contient une description de problème
        if len(user_message.strip()) < 20:
            logger.info("⏸️  Workflow SAV non démarré: description trop courte")
            return None

        try:
            logger.info(f"🚀 Initialisation workflow SAV pour commande {order_number}")

            # Récupérer ou créer les données client si nécessaire
            if not self.client_data:
                self.client_data = await self.fetch_order_data(order_number)

            # Déterminer customer_id (utiliser email comme ID si non fourni)
            if not customer_id:
                customer_id = self.client_data.get("email", "unknown")

            # Informations produit
            product_name = self.client_data.get("product", "Produit non spécifié")
            product_sku = "UNKNOWN-SKU"  # TODO: Ajouter SKU dans fetch_order_data

            # Dates (utiliser des dates par défaut si non disponibles)
            delivery_date_str = self.client_data.get("delivery_date", datetime.now().strftime("%d/%m/%Y"))
            try:
                # Parser la date de livraison (format: "02/12/2025")
                delivery_date = datetime.strptime(delivery_date_str, "%d/%m/%Y")
            except:
                delivery_date = datetime.now()

            # Date d'achat (supposer 30 jours avant la livraison)
            purchase_date = delivery_date - timedelta(days=30) if delivery_date else datetime.now()

            # Créer ou récupérer la garantie
            warranty = await warranty_service.create_warranty(
                order_number=order_number,
                product_sku=product_sku,
                product_name=product_name,
                customer_id=customer_id,
                purchase_date=purchase_date,
                delivery_date=delivery_date,
                warranty_type=WarrantyType.STANDARD
            )

            # Lancer le workflow SAV automatique
            ticket = await sav_workflow_engine.process_new_claim(
                customer_id=customer_id,
                order_number=order_number,
                product_sku=product_sku,
                product_name=product_name,
                problem_description=user_message,
                warranty=warranty,
                customer_tier="standard",  # TODO: Récupérer le vrai tier du client
                product_value=self.client_data.get("amount", 0.0)
            )

            # Générer message de demande de preuves
            evidence_message = evidence_collector.generate_evidence_request_message(
                problem_category=ticket.problem_category,
                priority=ticket.priority
            )

            # Sauvegarder le ticket dans les données de conversation
            self.ticket_data = {
                "ticket_id": ticket.ticket_id,
                "status": ticket.status,
                "priority": {
                    "code": ticket.priority,
                    "label": self._get_priority_label(ticket.priority),
                    "emoji": self._get_priority_emoji(ticket.priority),
                    "sla_hours": self._get_sla_hours(ticket.priority),
                    "requires_escalation": ticket.status == "escalated_to_human"
                },
                "problem_category": ticket.problem_category,
                "problem_severity": ticket.problem_severity,
                "warranty_covered": ticket.warranty_check_result.is_covered if ticket.warranty_check_result else False,
                "auto_resolved": ticket.auto_resolved,
                "resolution_type": ticket.resolution_type,
                "resolution_description": ticket.resolution_description,
                "evidence_requirements": evidence_message,
                "created_at": ticket.created_at.isoformat(),
                "language": self.detect_language(user_message),
                "problem_description": user_message
            }

            logger.info(
                f"✅ Workflow SAV initialisé: {ticket.ticket_id} | "
                f"Priorité: {ticket.priority} | Status: {ticket.status}"
            )

            return self.ticket_data

        except Exception as e:
            logger.error(f"❌ Erreur initialisation workflow SAV: {str(e)}")
            return None

    def _get_priority_label(self, priority: str) -> str:
        """Retourne le label de priorité"""
        labels = {
            "P0": "CRITIQUE",
            "P1": "HAUTE",
            "P2": "MOYENNE",
            "P3": "BASSE"
        }
        return labels.get(priority, "INCONNUE")

    def _get_priority_emoji(self, priority: str) -> str:
        """Retourne l'emoji de priorité"""
        emojis = {
            "P0": "🔴",
            "P1": "🟠",
            "P2": "🟡",
            "P3": "🟢"
        }
        return emojis.get(priority, "⚪")

    def _get_sla_hours(self, priority: str) -> int:
        """Retourne le SLA en heures"""
        slas = {
            "P0": 4,
            "P1": 24,
            "P2": 120,
            "P3": 168
        }
        return slas.get(priority, 168)

    def is_user_confirming(self, message: str) -> bool:
        """
        Vérifie si le message du client est une confirmation (OUI/YES/CONFIRMER)
        """
        message_lower = message.lower().strip()
        confirmation_keywords = [
            "oui", "yes", "ok", "d'accord", "confirme", "confirmer",
            "valider", "valide", "exact", "correct", "c'est bon",
            "je confirme", "tout est bon", "parfait"
        ]
        return any(keyword in message_lower for keyword in confirmation_keywords)

    def is_user_rejecting(self, message: str) -> bool:
        """
        Vérifie si le message du client est un refus (NON/NO)
        """
        message_lower = message.lower().strip()
        rejection_keywords = [
            "non", "no", "pas correct", "erreur", "faux", "incorrect",
            "modifier", "changer", "corriger"
        ]
        return any(keyword in message_lower for keyword in rejection_keywords)

    def is_user_wanting_to_continue(self, message: str) -> bool:
        """
        Vérifie si le client veut continuer la conversation
        """
        message_lower = message.lower().strip()
        continue_keywords = [
            "continuer", "poursuivre", "oui", "yes", "encore",
            "autre chose", "j'ai une autre question", "je voudrais",
            "continue", "carry on"
        ]
        return any(keyword in message_lower for keyword in continue_keywords)

    def is_user_wanting_to_close(self, message: str) -> bool:
        """
        Vérifie si le client veut clôturer la conversation
        """
        message_lower = message.lower().strip()
        close_keywords = [
            "clôturer", "cloturer", "fermer", "terminer", "fin",
            "arrêter", "arreter", "non merci", "c'est tout",
            "merci au revoir", "bye", "close", "end", "stop"
        ]
        return any(keyword in message_lower for keyword in close_keywords)

    async def prepare_ticket_validation(
        self,
        user_message: str,
        order_number: str,
        customer_id: Optional[str] = None
    ) -> Dict:
        """
        Prépare le ticket SAV pour validation client SANS le créer
        Analyse le problème et génère un récapitulatif pour confirmation

        Returns:
            Dict avec analyse complète et récapitulatif de validation
        """
        try:
            logger.info(f"📋 Préparation validation ticket pour: {order_number}")

            # Récupérer données client
            if not self.client_data:
                self.client_data = await self.fetch_order_data(order_number)

            if not customer_id:
                customer_id = self.client_data.get("email", "unknown")

            product_name = self.client_data.get("product", "Produit non spécifié")
            product_sku = "UNKNOWN-SKU"
            customer_name = self.client_data.get("name", "Client")

            # Dates
            delivery_date_str = self.client_data.get("delivery_date", datetime.now().strftime("%d/%m/%Y"))
            try:
                delivery_date = datetime.strptime(delivery_date_str, "%d/%m/%Y")
            except:
                delivery_date = datetime.now()

            purchase_date = delivery_date - timedelta(days=30)

            # Créer garantie (pour vérification uniquement)
            warranty = await warranty_service.create_warranty(
                order_number=order_number,
                product_sku=product_sku,
                product_name=product_name,
                customer_id=customer_id,
                purchase_date=purchase_date,
                delivery_date=delivery_date,
                warranty_type=WarrantyType.STANDARD
            )

            # Analyser le problème (SANS créer le ticket)
            from app.services.problem_detector import problem_detector
            from app.services.priority_scorer import priority_scorer
            from app.services.warranty_service import warranty_service as ws

            problem_result = problem_detector.detect_problem_type(user_message)
            warranty_check = ws.check_warranty_coverage(
                warranty=warranty,
                problem_description=user_message,
                problem_type=problem_result.primary_category
            )

            days_since_purchase = (datetime.now() - purchase_date).days
            priority_result = priority_scorer.calculate_priority(
                problem_category=problem_result.primary_category,
                problem_severity=problem_result.severity,
                days_since_purchase=days_since_purchase,
                under_warranty=warranty_check.is_covered,
                customer_tier="standard",
                has_critical_keywords=problem_result.severity == "P0",
                previous_claims_count=0,
                product_value=self.client_data.get("amount", 0.0)
            )

            # Sauvegarder pour validation ultérieure
            self.pending_ticket_validation = {
                "customer_id": customer_id,
                "customer_name": customer_name,
                "order_number": order_number,
                "product_sku": product_sku,
                "product_name": product_name,
                "problem_description": user_message,
                "warranty": warranty,
                "problem_category": problem_result.primary_category,
                "problem_severity": problem_result.severity,
                "problem_confidence": problem_result.confidence,
                "warranty_covered": warranty_check.is_covered,
                "warranty_component": warranty_check.component,
                "priority": priority_result.priority,
                "priority_score": priority_result.total_score,
                "priority_explanation": priority_result.explanation,
                "purchase_date": purchase_date,
                "delivery_date": delivery_date
            }

            self.awaiting_confirmation = True

            logger.info(f"✅ Validation préparée: {priority_result.priority} | {problem_result.primary_category}")

            return self.pending_ticket_validation

        except Exception as e:
            logger.error(f"❌ Erreur préparation validation: {str(e)}")
            raise

    async def create_ticket_after_validation(self) -> Dict:
        """
        Crée le ticket SAV après validation du client
        Utilise les données stockées dans pending_ticket_validation

        Returns:
            Ticket SAV créé
        """
        if not self.pending_ticket_validation:
            raise ValueError("Aucun ticket en attente de validation")

        try:
            data = self.pending_ticket_validation

            logger.info(f"✅ Création ticket après validation: {data['order_number']}")

            # Créer le ticket SAV complet
            ticket = await sav_workflow_engine.process_new_claim(
                customer_id=data["customer_id"],
                order_number=data["order_number"],
                product_sku=data["product_sku"],
                product_name=data["product_name"],
                problem_description=data["problem_description"],
                warranty=data["warranty"],
                customer_tier="standard",
                product_value=self.client_data.get("amount", 0.0)
            )

            # Générer message preuves
            evidence_message = evidence_collector.generate_evidence_request_message(
                problem_category=ticket.problem_category,
                priority=ticket.priority
            )

            # Sauvegarder ticket
            self.ticket_data = {
                "ticket_id": ticket.ticket_id,
                "status": ticket.status,
                "priority": {
                    "code": ticket.priority,
                    "label": self._get_priority_label(ticket.priority),
                    "emoji": self._get_priority_emoji(ticket.priority),
                    "sla_hours": self._get_sla_hours(ticket.priority),
                    "requires_escalation": ticket.status == "escalated_to_human"
                },
                "problem_category": ticket.problem_category,
                "problem_severity": ticket.problem_severity,
                "warranty_covered": ticket.warranty_check_result.is_covered if ticket.warranty_check_result else False,
                "auto_resolved": ticket.auto_resolved,
                "resolution_type": ticket.resolution_type,
                "resolution_description": ticket.resolution_description,
                "evidence_requirements": evidence_message,
                "created_at": ticket.created_at.isoformat(),
                "language": "fr",
                "problem_description": data["problem_description"]
            }

            # Réinitialiser l'état de validation
            self.pending_ticket_validation = None
            self.awaiting_confirmation = False

            # 🎯 NOUVEAU: Demander si le client veut continuer ou clôturer
            self.should_ask_continue = True
            self.awaiting_continue_or_close = True

            logger.info(f"🎫 Ticket créé: {ticket.ticket_id} → Demande continuation")

            return self.ticket_data

        except Exception as e:
            logger.error(f"❌ Erreur création ticket: {str(e)}")
            raise

    def reset_conversation(self):
        """
        Réinitialise complètement la conversation
        Utilisé quand le client veut clôturer
        """
        logger.info("🔄 Réinitialisation complète de la conversation")
        self.conversation_history = []
        self.client_data = {}
        self.ticket_data = {}
        self.pending_ticket_validation = None
        self.awaiting_confirmation = False
        self.should_ask_continue = False
        self.awaiting_continue_or_close = False
        self.conversation_type = "general"

    def generate_summary(self) -> str:
        """Génère le bilan de conversation"""

        if not self.ticket_data:
            return "Aucun ticket SAV créé pour cette conversation."

        priority_info = self.ticket_data.get('priority', {})

        summary = f"""
═══════════════════════════════════════════════════════
         BILAN CONVERSATION - MEUBLE DE FRANCE
═══════════════════════════════════════════════════════

📅 DATE: {datetime.now().strftime('%d/%m/%Y - %H:%M')}
🆔 TICKET: {self.ticket_data.get('ticket_id')}
🔢 COMMANDE: {self.client_data.get('order_number', 'N/A')}

👤 CLIENT:
├── Nom: {self.client_data.get('name', 'N/A')}
├── Email: {self.client_data.get('email', 'N/A')}
├── Tél: {self.client_data.get('phone', 'N/A')}
└── Langue: {self.ticket_data.get('language', 'Français')}

🛋️ PRODUIT CONCERNÉ:
├── Article: {self.client_data.get('product', 'N/A')}
├── Livraison: {self.client_data.get('delivery_date', 'N/A')}
└── Garantie: {self.client_data.get('warranty_status', 'N/A')}

⚠️ PROBLÈME SIGNALÉ:
{self.ticket_data.get('problem_description', 'N/A')}

🎯 CLASSIFICATION:
{priority_info.get('emoji')} PRIORITÉ: {priority_info.get('label')} ({priority_info.get('code')})
SLA: < {priority_info.get('sla_hours')}h

✅ ACTIONS PRISES:
├── Dossier SAV créé
├── Photos uploadées: {len(self.ticket_data.get('photos', []))}
├── Notification équipe: {'Oui' if priority_info.get('requires_escalation') else 'Non'}
└── Email confirmation envoyé

───────────────────────────────────────────────────────
PROCHAINES ÉTAPES:
{self._generate_next_steps()}
───────────────────────────────────────────────────────

Généré automatiquement par Chatbot Meuble de France
═══════════════════════════════════════════════════════
"""
        return summary

    def _generate_next_steps(self) -> str:
        """Génère les prochaines étapes selon la priorité"""
        priority = self.ticket_data.get('priority', {}).get('code')

        steps = {
            "P0": "1. Appel équipe qualité < 24h\n2. Évaluation: Remplacement urgent\n3. Organisation enlèvement immédiat",
            "P1": "1. Email équipe SAV < 48h\n2. Évaluation solution\n3. Contact client sous 2 jours",
            "P2": "1. Traitement standard < 5 jours\n2. Proposition solution\n3. Suivi sous 1 semaine",
            "P3": "1. Réponse sous 7 jours\n2. Information fournie\n3. Clôture si satisfait"
        }

        return steps.get(priority, "Prochaines étapes à définir")
