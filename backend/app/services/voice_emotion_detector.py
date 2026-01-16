"""
Voice Emotion Detection Service

Analyzes customer voice transcriptions to detect emotional state and automatically
assign appropriate ticket priority based on the template system:

- Angry (fache) -> P0 (Priority 4) - URGENT < 1h
- Irritated (enerve) -> P1 (Priority 3) - HIGH < 2h
- Desperate (desespere) -> P2 (Priority 2) - MEDIUM < 4h
- Sad (triste) -> P2 (Priority 2) - MEDIUM < 8h
- Calm (calme) -> P3 (Priority 1) - LOW < 24h
"""
import logging
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
from app.core.config import settings
import httpx

logger = logging.getLogger(__name__)


class VoiceEmotionDetector:
    """
    Detects emotional state from voice transcriptions using Claude/GPT analysis
    """

    # Emotion to priority mapping (based on template)
    EMOTION_PRIORITY_MAP = {
        "fache": {"priority": "P0", "urgency": "urgent", "sla_hours": 1, "description": "Client tres mecontent - Action immediate"},
        "enerve": {"priority": "P1", "urgency": "high", "sla_hours": 2, "description": "Client irrite - Reponse rapide"},
        "desespere": {"priority": "P2", "urgency": "medium", "sla_hours": 4, "description": "Client decourage - Traitement prioritaire"},
        "triste": {"priority": "P2", "urgency": "medium", "sla_hours": 8, "description": "Client decu - Traitement standard"},
        "calme": {"priority": "P3", "urgency": "low", "sla_hours": 24, "description": "Client serein - Traitement normal"}
    }

    # Keywords that indicate specific emotions
    EMOTION_KEYWORDS = {
        "fache": [
            "inacceptable", "scandale", "honte", "intolerable", "furieux", "colere",
            "inadmissible", "degoutant", "honteux", "marre", "exaspere"
        ],
        "enerve": [
            "agace", "enerve", "irrite", "contrarie", "embete", "frustre",
            "mecontente", "insatisfait", "pas content", "decu"
        ],
        "desespere": [
            "desespere", "desesper", "ne sais plus quoi faire", "au bout du rouleau",
            "plus de solution", "abandonne", "sans issue"
        ],
        "triste": [
            "triste", "peine", "decu", "decevant", "desole", "navr", "chagrin",
            "malheureux", "attrist"
        ],
        "calme": [
            "comprends", "merci", "patient", "normal", "ok", "d'accord",
            "pas grave", "tranquille", "serein", "calme"
        ]
    }

    def __init__(self):
        """Initialize the emotion detector with OpenAI client"""
        http_client = httpx.Client(verify=False, timeout=30.0)
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            http_client=http_client
        )
        logger.info("Voice emotion detector initialized")

    async def analyze_emotion(
        self,
        transcript: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Analyze the emotional state from a voice transcript

        Args:
            transcript: The transcribed text from voice
            conversation_history: Optional conversation context

        Returns:
            Dict with:
                - emotion: str (fache, enerve, desespere, triste, calme)
                - confidence: float (0-1)
                - indicators: List[str] (reasons for this classification)
                - priority: str (P0-P3)
                - urgency: str
                - sla_hours: int
        """
        try:
            logger.info(f"Analyzing emotion from transcript: {transcript[:100]}...")

            # First, do a quick keyword-based analysis
            keyword_emotion, keyword_confidence, keyword_indicators = self._keyword_analysis(transcript)

            # Then enhance with AI analysis
            ai_emotion, ai_confidence, ai_indicators = await self._ai_analysis(
                transcript, conversation_history
            )

            # Combine results (weighted: AI 70%, Keywords 30%)
            final_emotion, final_confidence, final_indicators = self._combine_results(
                keyword_emotion, keyword_confidence, keyword_indicators,
                ai_emotion, ai_confidence, ai_indicators
            )

            # Get priority information
            priority_info = self.EMOTION_PRIORITY_MAP.get(final_emotion, self.EMOTION_PRIORITY_MAP["calme"])

            result = {
                "emotion": final_emotion,
                "confidence": final_confidence,
                "indicators": final_indicators,
                "priority": priority_info["priority"],
                "urgency": priority_info["urgency"],
                "sla_hours": priority_info["sla_hours"],
                "description": priority_info["description"]
            }

            logger.info(f"Emotion detected: {final_emotion} (confidence: {final_confidence:.2f}, priority: {priority_info['priority']})")
            return result

        except Exception as e:
            logger.error(f"Error analyzing emotion: {e}")
            # Default to calm with low confidence if analysis fails
            return {
                "emotion": "calme",
                "confidence": 0.5,
                "indicators": ["Analyse par defaut (erreur)"],
                "priority": "P3",
                "urgency": "low",
                "sla_hours": 24,
                "description": "Client serein - Traitement normal"
            }

    def _keyword_analysis(self, text: str) -> Tuple[str, float, List[str]]:
        """
        Analyze emotion based on keyword matching

        Returns: (emotion, confidence, indicators)
        """
        text_lower = text.lower()
        emotion_scores = {emotion: 0 for emotion in self.EMOTION_KEYWORDS}
        found_keywords = {emotion: [] for emotion in self.EMOTION_KEYWORDS}

        # Count keyword matches for each emotion
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotion_scores[emotion] += 1
                    found_keywords[emotion].append(keyword)

        # Find the emotion with highest score
        if max(emotion_scores.values()) == 0:
            # No keywords found, default to calm
            return "calme", 0.3, ["Aucun mot-cle emotionnel detecte"]

        best_emotion = max(emotion_scores, key=emotion_scores.get)
        score = emotion_scores[best_emotion]

        # Calculate confidence (normalize to 0-1 range)
        confidence = min(0.3 + (score * 0.2), 0.9)  # Max 0.9 for keyword-only

        indicators = [
            f"Mots-cles detectes: {', '.join(found_keywords[best_emotion][:3])}"
        ]

        return best_emotion, confidence, indicators

    async def _ai_analysis(
        self,
        transcript: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Tuple[str, float, List[str]]:
        """
        Use AI (GPT) to analyze emotion from transcript

        Returns: (emotion, confidence, indicators)
        """
        try:
            # Build context from conversation history
            context = ""
            if conversation_history:
                context = "\n".join([
                    f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                    for msg in conversation_history[-3:]  # Last 3 messages
                ])

            prompt = f"""Analyse l'etat emotionnel du client a partir de sa transcription vocale.

Contexte de conversation (3 derniers messages):
{context if context else "Aucun contexte"}

Transcription actuelle:
"{transcript}"

Classe l'emotion dans UNE SEULE de ces categories:
- fache: Client tres mecontent, agressif, en colere
- enerve: Client irrite, frustre, contrarie
- desespere: Client desespere, ne sait plus quoi faire
- triste: Client decu, peine, attrist
- calme: Client serein, comprehensif, patient

Reponds UNIQUEMENT au format JSON:
{{
  "emotion": "fache|enerve|desespere|triste|calme",
  "confidence": 0.0-1.0,
  "indicators": ["raison 1", "raison 2", "raison 3"]
}}

Exemples d'indicateurs:
- Utilisation de mots agressifs
- Tone eleve suggere
- Repetitions excessives
- Phrases courtes et abruptes
- Utilisation de formules de politesse
- Langage calme et pose
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cheap for emotion detection
                messages=[
                    {"role": "system", "content": "Tu es un expert en analyse emotionnelle de service client. Reponds UNIQUEMENT en JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Low temperature for consistent results
                max_tokens=200
            )

            result_text = response.choices[0].message.content.strip()

            # Parse JSON response
            import json
            # Extract JSON from markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            emotion = result.get("emotion", "calme")
            confidence = float(result.get("confidence", 0.5))
            indicators = result.get("indicators", [])

            # Validate emotion
            if emotion not in self.EMOTION_KEYWORDS:
                logger.warning(f"Invalid emotion from AI: {emotion}, defaulting to calme")
                emotion = "calme"
                confidence = 0.5

            return emotion, confidence, indicators

        except Exception as e:
            logger.error(f"Error in AI emotion analysis: {e}")
            return "calme", 0.5, ["Erreur analyse IA"]

    def _combine_results(
        self,
        keyword_emotion: str, keyword_confidence: float, keyword_indicators: List[str],
        ai_emotion: str, ai_confidence: float, ai_indicators: List[str]
    ) -> Tuple[str, float, List[str]]:
        """
        Combine keyword and AI results with weighted average

        AI weight: 70%
        Keyword weight: 30%

        Returns: (final_emotion, final_confidence, combined_indicators)
        """
        # If both agree, high confidence
        if keyword_emotion == ai_emotion:
            final_emotion = ai_emotion
            final_confidence = min(keyword_confidence * 0.3 + ai_confidence * 0.7, 0.95)
            combined_indicators = keyword_indicators + ai_indicators
        else:
            # Disagree - trust AI more but reduce confidence
            final_emotion = ai_emotion if ai_confidence > keyword_confidence else keyword_emotion
            final_confidence = max(ai_confidence, keyword_confidence) * 0.8  # Reduce confidence due to disagreement
            combined_indicators = [
                f"Analyse mixte (IA: {ai_emotion}, Mots-cles: {keyword_emotion})"
            ] + ai_indicators + keyword_indicators

        # Ensure confidence is in valid range
        final_confidence = max(0.0, min(1.0, final_confidence))

        return final_emotion, final_confidence, combined_indicators[:5]  # Max 5 indicators

    def get_priority_for_emotion(self, emotion: str) -> Dict:
        """
        Get priority information for a given emotion

        Args:
            emotion: The detected emotion

        Returns:
            Dict with priority, urgency, sla_hours, description
        """
        return self.EMOTION_PRIORITY_MAP.get(emotion, self.EMOTION_PRIORITY_MAP["calme"])


# Singleton instance
_voice_emotion_detector: Optional[VoiceEmotionDetector] = None


def get_voice_emotion_detector() -> VoiceEmotionDetector:
    """Get or create the voice emotion detector singleton"""
    global _voice_emotion_detector
    if _voice_emotion_detector is None:
        _voice_emotion_detector = VoiceEmotionDetector()
    return _voice_emotion_detector
