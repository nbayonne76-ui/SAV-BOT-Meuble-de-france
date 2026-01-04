# backend/app/core/chatbot_config.py
"""
Configuration du chatbot vocal
"""

class ChatbotConfig:
    """Configuration pour le chatbot vocal"""

    # Informations entreprise
    ENTREPRISE_NOM = "Mobilier de France"
    ENTREPRISE_EMAIL_SAV = "sav@mobilierdefrance.com"

    # Configuration IA
    MODELE_IA = "gpt-4o-mini"  # 200x moins cher que gpt-4, excellente qualité
    TEMPERATURE = 0.7
    MAX_TOKENS = 300  # Réponses courtes pour le vocal

# Instance globale
config = ChatbotConfig()
