# backend/app/services/tone_analyzer.py
"""
Analyseur de ton et urgence du client
Détecte le niveau d'émotion et urgence pour adapter la réponse
"""

import logging
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ToneLevel(str, Enum):
    """Niveaux de ton détectés"""
    CALM = "calm"              # Calme, neutre
    CONCERNED = "concerned"    # Préoccupé
    FRUSTRATED = "frustrated"  # Frustré
    ANGRY = "angry"            # En colère
    URGENT = "urgent"          # Urgent/critique


class UrgencyLevel(str, Enum):
    """Niveaux d'urgence"""
    LOW = "low"           # Basse - peut attendre
    MEDIUM = "medium"     # Moyenne - traitement normal
    HIGH = "high"         # Haute - prioritaire
    CRITICAL = "critical" # Critique - immédiat


@dataclass
class ToneAnalysis:
    """Résultat de l'analyse de ton"""
    tone: ToneLevel
    urgency: UrgencyLevel
    emotion_score: float  # 0-100 (0=calme, 100=très émotionnel)
    urgency_score: float  # 0-100 (0=pas urgent, 100=critique)
    detected_keywords: List[str]
    recommended_response_time: str  # "24h", "48h", "72h"
    requires_human_empathy: bool
    explanation: str


class ToneAnalyzer:
    """
    Analyse le ton et l'urgence du message client
    """

    def __init__(self):
        # Mots-clés de ton CALME
        self.calm_keywords = [
            "bonjour", "merci", "s'il vous plaît", "pourriez-vous",
            "j'aimerais", "question", "renseignement", "information"
        ]

        # Mots-clés de PRÉOCCUPATION
        self.concerned_keywords = [
            "inquiet", "préoccupé", "soucieux", "bizarre", "étrange",
            "anormal", "inhabituel", "pourquoi", "comment se fait-il"
        ]

        # Mots-clés de FRUSTRATION
        self.frustrated_keywords = [
            "déçu", "mécontent", "problème", "encore", "toujours",
            "ça fait plusieurs fois", "ça dure depuis", "pas normal",
            "inacceptable", "inadmissible", "honte", "scandale"
        ]

        # Mots-clés de COLÈRE
        self.angry_keywords = [
            "furieux", "en colère", "outré", "honteux", "arnaque",
            "escroquerie", "inadmissible", "exige", "je veux",
            "immédiatement", "tout de suite", "c'est une honte",
            "!!!", "catastrophe", "désastre"
        ]

        # Mots-clés d'URGENCE CRITIQUE
        self.urgent_keywords = [
            "urgent", "immédiat", "danger", "risque", "blessure",
            "enfant", "bébé", "cassé net", "effondré", "chute",
            "accident", "sanguin", "coupure", "éclats", "verre brisé",
            "tombé", "instable", "penche"
        ]

        # Indicateurs temporels d'urgence
        self.time_urgency_keywords = [
            "aujourd'hui", "maintenant", "ce soir", "urgent",
            "au plus vite", "dès que possible", "rapidement"
        ]

        # Multiplicateurs d'émotion
        self.emotion_amplifiers = [
            "vraiment", "totalement", "complètement", "absolument",
            "très", "trop", "extrêmement", "terriblement"
        ]

        # Ponctuation émotionnelle
        self.emotional_punctuation = ["!!!", "!!", "???"]

    def analyze_tone(self, message: str) -> ToneAnalysis:
        """
        Analyse le ton et l'urgence d'un message

        Args:
            message: Message du client

        Returns:
            ToneAnalysis avec ton, urgence et recommandations
        """

        message_lower = message.lower()
        detected_keywords = []

        # 1. Détecter les mots-clés par catégorie
        calm_matches = [kw for kw in self.calm_keywords if kw in message_lower]
        concerned_matches = [kw for kw in self.concerned_keywords if kw in message_lower]
        frustrated_matches = [kw for kw in self.frustrated_keywords if kw in message_lower]
        angry_matches = [kw for kw in self.angry_keywords if kw in message_lower]
        urgent_matches = [kw for kw in self.urgent_keywords if kw in message_lower]
        time_urgent_matches = [kw for kw in self.time_urgency_keywords if kw in message_lower]

        # 2. Vérifier amplificateurs et ponctuation
        has_amplifiers = any(amp in message_lower for amp in self.emotion_amplifiers)
        has_emotional_punctuation = any(punct in message for punct in self.emotional_punctuation)

        # 3. Calculer les scores
        emotion_score = 0.0
        urgency_score = 0.0

        # Score d'émotion (0-100)
        if urgent_matches:
            emotion_score += 90
            detected_keywords.extend(urgent_matches)
        if angry_matches:
            emotion_score += 70
            detected_keywords.extend(angry_matches)
        if frustrated_matches:
            emotion_score += 50
            detected_keywords.extend(frustrated_matches)
        if concerned_matches:
            emotion_score += 30
            detected_keywords.extend(concerned_matches)
        if calm_matches:
            emotion_score = max(0, emotion_score - 20)  # Réduit l'émotion
            detected_keywords.extend(calm_matches)

        # Amplification
        if has_amplifiers:
            emotion_score *= 1.2
        if has_emotional_punctuation:
            emotion_score *= 1.3
        if message.isupper():  # TOUT EN MAJUSCULES
            emotion_score *= 1.5

        # Cap à 100
        emotion_score = min(100, emotion_score)

        # Score d'urgence (0-100)
        if urgent_matches:
            urgency_score += 80
        if time_urgent_matches:
            urgency_score += 40
        if angry_matches:
            urgency_score += 30
        if frustrated_matches:
            urgency_score += 20

        # Cap à 100
        urgency_score = min(100, urgency_score)

        # 4. Déterminer le ton
        tone = self._determine_tone(
            calm_matches, concerned_matches, frustrated_matches,
            angry_matches, urgent_matches, emotion_score
        )

        # 5. Déterminer l'urgence
        urgency = self._determine_urgency(urgency_score, urgent_matches)

        # 6. Temps de réponse recommandé
        response_time = self._get_response_time(urgency, tone)

        # 7. Empathie humaine requise ?
        requires_empathy = emotion_score >= 60 or urgency_score >= 70

        # 8. Explication
        explanation = self._generate_explanation(tone, urgency, emotion_score, urgency_score)

        logger.info(
            f"📊 Analyse ton: {tone} | Urgence: {urgency} | "
            f"Émotion: {emotion_score:.0f} | Urgence score: {urgency_score:.0f}"
        )

        return ToneAnalysis(
            tone=tone,
            urgency=urgency,
            emotion_score=emotion_score,
            urgency_score=urgency_score,
            detected_keywords=detected_keywords[:10],  # Top 10
            recommended_response_time=response_time,
            requires_human_empathy=requires_empathy,
            explanation=explanation
        )

    def _determine_tone(
        self,
        calm_matches: List[str],
        concerned_matches: List[str],
        frustrated_matches: List[str],
        angry_matches: List[str],
        urgent_matches: List[str],
        emotion_score: float
    ) -> ToneLevel:
        """Détermine le ton dominant"""

        if urgent_matches or emotion_score >= 90:
            return ToneLevel.URGENT
        elif angry_matches or emotion_score >= 70:
            return ToneLevel.ANGRY
        elif frustrated_matches or emotion_score >= 50:
            return ToneLevel.FRUSTRATED
        elif concerned_matches or emotion_score >= 30:
            return ToneLevel.CONCERNED
        else:
            return ToneLevel.CALM

    def _determine_urgency(
        self,
        urgency_score: float,
        urgent_matches: List[str]
    ) -> UrgencyLevel:
        """Détermine le niveau d'urgence"""

        if urgent_matches or urgency_score >= 80:
            return UrgencyLevel.CRITICAL
        elif urgency_score >= 50:
            return UrgencyLevel.HIGH
        elif urgency_score >= 25:
            return UrgencyLevel.MEDIUM
        else:
            return UrgencyLevel.LOW

    def _get_response_time(self, urgency: UrgencyLevel, tone: ToneLevel) -> str:
        """Retourne le délai de réponse recommandé"""

        if urgency == UrgencyLevel.CRITICAL or tone == ToneLevel.URGENT:
            return "4h"
        elif urgency == UrgencyLevel.HIGH or tone == ToneLevel.ANGRY:
            return "24h"
        elif urgency == UrgencyLevel.MEDIUM or tone == ToneLevel.FRUSTRATED:
            return "48h"
        else:
            return "72h"

    def _generate_explanation(
        self,
        tone: ToneLevel,
        urgency: UrgencyLevel,
        emotion_score: float,
        urgency_score: float
    ) -> str:
        """Génère une explication de l'analyse"""

        tone_labels = {
            ToneLevel.CALM: "neutre et calme",
            ToneLevel.CONCERNED: "préoccupé",
            ToneLevel.FRUSTRATED: "frustré",
            ToneLevel.ANGRY: "en colère",
            ToneLevel.URGENT: "urgent et critique"
        }

        urgency_labels = {
            UrgencyLevel.LOW: "faible",
            UrgencyLevel.MEDIUM: "moyenne",
            UrgencyLevel.HIGH: "haute",
            UrgencyLevel.CRITICAL: "critique"
        }

        explanation = (
            f"Ton du client: {tone_labels[tone]} (score émotion: {emotion_score:.0f}/100). "
            f"Urgence: {urgency_labels[urgency]} (score: {urgency_score:.0f}/100). "
        )

        if tone in [ToneLevel.ANGRY, ToneLevel.URGENT]:
            explanation += "⚠️ Nécessite une réponse rapide et empathique."
        elif tone == ToneLevel.FRUSTRATED:
            explanation += "Nécessite une réponse professionnelle et rassurante."
        else:
            explanation += "Réponse standard appropriée."

        return explanation


# Instance globale
tone_analyzer = ToneAnalyzer()
