# ═══════════════════════════════════════════════════════════════════════════════
# 📋 CONFIGURATION CHATBOT SAV - BB EXPANSION MOBILIER DE FRANCE
# ═══════════════════════════════════════════════════════════════════════════════
# Généré à partir du formulaire client
# Date: 2025-12-13
# ═══════════════════════════════════════════════════════════════════════════════

from typing import Dict, Any


class ChatbotConfig:
    """Configuration centralisée du chatbot SAV"""

    # ───────────────────────────────────────────────────────────────────────────
    # 🏢 INFORMATIONS ENTREPRISE
    # ───────────────────────────────────────────────────────────────────────────
    ENTREPRISE_NOM = "BB Expansion Mobilier de France"
    ENTREPRISE_SIGLE = "MdF"
    ENTREPRISE_EMAIL_SAV = "clientelegroupe@gmail.com"
    ENTREPRISE_TELEPHONE = None  # Non défini
    ENTREPRISE_SITE_WEB = "https://www.mobilier-de-france.com"  # Pour le test

    # ───────────────────────────────────────────────────────────────────────────
    # 🎨 COULEURS & BRANDING
    # ───────────────────────────────────────────────────────────────────────────
    COULEUR_FOND_RGB = (32, 37, 63)
    COULEUR_FOND_HEX = "#20253F"
    COULEUR_TEXTE_RGB = (255, 255, 255)
    COULEUR_TEXTE_HEX = "#FFFFFF"
    COULEUR_ACCENT = "#3B82F6"
    POLICE_PRINCIPALE = "Segoe UI Variable Display Semib"

    # ───────────────────────────────────────────────────────────────────────────
    # 💬 MESSAGES D'ACCUEIL
    # ───────────────────────────────────────────────────────────────────────────
    MESSAGE_ACCUEIL_FR = (
        "Bonjour ! Je suis votre assistant SAV Mobilier de France. "
        "Décrivez-moi votre problème avec votre numéro de commande, "
        "je m'occupe du reste !"
    )
    MESSAGE_ACCUEIL_EN = (
        "Hello! I am your Mobilier de France customer support assistant. "
        "Describe your problem with your order number, I'll take care of the rest!"
    )
    MESSAGE_ACCUEIL_AR = (
        "مرحباً! أنا مساعد خدمة العملاء لشركة Mobilier de France. "
        "صف لي مشكلتك مع رقم طلبك، وسأتولى الأمر!"
    )

    # Message d'accueil général (header)
    MESSAGE_BIENVENUE_FR = (
        "Bonjour et bienvenue au service clientèle du groupe Mobilier de France. "
        "Nous sommes à votre écoute pour un accompagnement personnalisé."
    )
    MESSAGE_BIENVENUE_EN = (
        "Hello and welcome to the Customer Service of the Mobilier de France Group. "
        "We are here to listen and provide you with personalized support."
    )

    # ───────────────────────────────────────────────────────────────────────────
    # 🧠 INTELLIGENCE ARTIFICIELLE
    # ───────────────────────────────────────────────────────────────────────────
    MODELE_IA = "gpt-3.5-turbo"  # Économique
    BUDGET_IA = "faible"  # < 50€/mois
    LONGUEUR_REPONSES = "courte"  # 300 mots
    MAX_TOKENS = 300  # Équivalent ~300 mots
    TEMPERATURE = 0.7  # Créativité modérée

    # ───────────────────────────────────────────────────────────────────────────
    # 🎯 SLA (SERVICE LEVEL AGREEMENT) - DÉLAIS DE RÉPONSE
    # ───────────────────────────────────────────────────────────────────────────
    SLA = {
        "P0": {
            "nom": "CRITIQUE",
            "heures": 4,
            "description": "Problème bloquant nécessitant une intervention immédiate"
        },
        "P1": {
            "nom": "URGENT",
            "heures": 24,
            "description": "Problème important mais contournable temporairement"
        },
        "P2": {
            "nom": "NORMAL",
            "heures": 48,
            "description": "Demande standard sans urgence"
        },
        "P3": {
            "nom": "FAIBLE",
            "heures": 72,
            "description": "Question ou demande d'information"
        }
    }

    # ───────────────────────────────────────────────────────────────────────────
    # 🛡️ GARANTIES (EN ANNÉES)
    # ───────────────────────────────────────────────────────────────────────────
    GARANTIES = {
        "structure": {
            "duree_annees": 5,
            "description": "Pieds, cadre, ossature du meuble",
            "exemples": ["pieds cassés", "cadre déformé", "structure instable"]
        },
        "tissu": {
            "duree_annees": 2,
            "description": "Revêtement textile ou cuir",
            "exemples": ["déchirure", "usure prématurée", "décoloration"]
        },
        "mecanismes": {
            "duree_annees": 3,
            "description": "Canapé-lit, relax, mécanismes électriques",
            "exemples": ["mécanisme bloqué", "moteur défectueux", "problème d'ouverture"]
        },
        "coussins": {
            "duree_annees": 2,
            "description": "Garnissage et maintien des coussins",
            "exemples": ["affaissement", "perte de fermeté", "déformation"]
        }
    }

    # ───────────────────────────────────────────────────────────────────────────
    # 📤 UPLOAD DE FICHIERS
    # ───────────────────────────────────────────────────────────────────────────
    TAILLE_MAX_FICHIER_MB = 10
    TAILLE_MAX_FICHIER_BYTES = 10 * 1024 * 1024  # 10 MB en bytes
    NOMBRE_MAX_FICHIERS = 10
    TYPES_FICHIERS_ACCEPTES = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "video/mp4",
        "video/webm",
        "application/pdf"
    ]

    # ───────────────────────────────────────────────────────────────────────────
    # 🔔 NOTIFICATIONS
    # ───────────────────────────────────────────────────────────────────────────
    NOTIFICATION_EMAIL = True
    NOTIFICATION_SMS = False
    EMAIL_EQUIPE_SAV = "equipe-sav@mobilierdefrance.fr"

    # ───────────────────────────────────────────────────────────────────────────
    # 🎙️ MODE VOCAL
    # ───────────────────────────────────────────────────────────────────────────
    VOICE_MODEL_TRANSCRIPTION = "whisper-1"
    VOICE_MODEL_TTS = "tts-1"
    VOICE_NAME = "nova"  # Voix féminine chaleureuse
    VOICE_ENREGISTREMENT_MAX_SECONDES = 10

    @classmethod
    def get_message_accueil(cls, langue: str = "fr") -> str:
        """Récupère le message d'accueil dans la langue demandée"""
        messages = {
            "fr": cls.MESSAGE_ACCUEIL_FR,
            "en": cls.MESSAGE_ACCUEIL_EN,
            "ar": cls.MESSAGE_ACCUEIL_AR
        }
        return messages.get(langue.lower(), cls.MESSAGE_ACCUEIL_FR)

    @classmethod
    def get_sla_heures(cls, priorite: str) -> int:
        """Récupère le délai SLA en heures pour une priorité donnée"""
        return cls.SLA.get(priorite.upper(), cls.SLA["P2"])["heures"]

    @classmethod
    def get_garantie_duree(cls, type_garantie: str) -> int:
        """Récupère la durée de garantie en années pour un type donné"""
        return cls.GARANTIES.get(type_garantie.lower(), {}).get("duree_annees", 2)

    @classmethod
    def detecter_type_garantie(cls, description_probleme: str) -> str:
        """Détecte automatiquement le type de garantie à partir de la description"""
        description_lower = description_probleme.lower()

        # Structure
        mots_cles_structure = ["pied", "cadre", "ossature", "structure", "cassé", "instable"]
        if any(mot in description_lower for mot in mots_cles_structure):
            return "structure"

        # Tissu
        mots_cles_tissu = ["tissu", "cuir", "déchiré", "usé", "décoloré", "tache"]
        if any(mot in description_lower for mot in mots_cles_tissu):
            return "tissu"

        # Mécanismes
        mots_cles_mecanismes = ["mécanisme", "canapé-lit", "relax", "électrique", "moteur", "bloqué"]
        if any(mot in description_lower for mot in mots_cles_mecanismes):
            return "mecanismes"

        # Coussins
        mots_cles_coussins = ["coussin", "garnissage", "affaissement", "fermeté", "déformation"]
        if any(mot in description_lower for mot in mots_cles_coussins):
            return "coussins"

        # Par défaut, renvoyer structure (garantie la plus longue)
        return "structure"

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire pour l'API"""
        return {
            "entreprise": {
                "nom": cls.ENTREPRISE_NOM,
                "sigle": cls.ENTREPRISE_SIGLE,
                "email_sav": cls.ENTREPRISE_EMAIL_SAV,
                "telephone": cls.ENTREPRISE_TELEPHONE,
                "site_web": cls.ENTREPRISE_SITE_WEB
            },
            "couleurs": {
                "fond_hex": cls.COULEUR_FOND_HEX,
                "texte_hex": cls.COULEUR_TEXTE_HEX,
                "accent": cls.COULEUR_ACCENT
            },
            "ia": {
                "modele": cls.MODELE_IA,
                "budget": cls.BUDGET_IA,
                "max_tokens": cls.MAX_TOKENS
            },
            "sla": cls.SLA,
            "garanties": cls.GARANTIES,
            "upload": {
                "taille_max_mb": cls.TAILLE_MAX_FICHIER_MB,
                "nombre_max": cls.NOMBRE_MAX_FICHIERS
            },
            "notifications": {
                "email": cls.NOTIFICATION_EMAIL,
                "sms": cls.NOTIFICATION_SMS,
                "email_equipe": cls.EMAIL_EQUIPE_SAV
            }
        }


# Instance globale de configuration
config = ChatbotConfig()
