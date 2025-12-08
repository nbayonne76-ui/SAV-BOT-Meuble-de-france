# backend/app/services/problem_detector.py
"""
Moteur de détection et classification automatique des problèmes SAV
"""

import logging
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProblemDetectionResult:
    """Résultat de détection de problème"""
    primary_category: str
    confidence: float
    matched_keywords: List[str]
    severity: str
    warranty_component: str
    all_detected_categories: List[Dict]
    needs_clarification: bool = False


class ProblemDetectionEngine:
    """
    Moteur NLP de détection et classification des problèmes
    """

    def __init__(self):
        # Configuration des catégories de problèmes
        self.problem_categories = {
            "structural": {
                "keywords": [
                    "cassé", "fissure", "effondré", "instable", "penche",
                    "pied cassé", "s'effondre", "craqué", "rompu", "fendu",
                    "danger", "risque", "chute", "brisé"
                ],
                "severity_range": ["P0", "P1"],
                "warranty_component": "structure",
                "base_priority": 30,
                "description": "Problème structurel"
            },
            "mechanism": {
                "keywords": [
                    "bloqué", "grince", "dur", "ne fonctionne plus", "mécanisme",
                    "relax", "convertible", "ne se déplie plus", "coincé",
                    "ressort", "vérin", "ne marche plus", "en panne"
                ],
                "severity_range": ["P1", "P2"],
                "warranty_component": "mechanisms",
                "base_priority": 25,
                "description": "Problème mécanique"
            },
            "fabric": {
                "keywords": [
                    "tache", "déchirure", "décoloration", "usure", "tissu",
                    "cuir", "trou", "accroc", "pelage", "pâli", "délavé",
                    "abimé", "usé"
                ],
                "severity_range": ["P2", "P3"],
                "warranty_component": "fabric",
                "base_priority": 10,
                "description": "Problème de revêtement"
            },
            "cushions": {
                "keywords": [
                    "affaissement", "mousse", "coussin", "s'affaisse", "creux",
                    "aplati", "déformé", "mou", "confort", "s'aplatit"
                ],
                "severity_range": ["P2"],
                "warranty_component": "cushions",
                "base_priority": 15,
                "description": "Problème de coussins"
            },
            "delivery": {
                "keywords": [
                    "livraison", "retard", "endommagé à l'arrivée", "manquant",
                    "colis", "transport", "livreur", "pas reçu", "délai",
                    "abimé livraison"
                ],
                "severity_range": ["P1"],
                "warranty_component": "delivery",
                "base_priority": 20,
                "description": "Problème de livraison"
            },
            "assembly": {
                "keywords": [
                    "pièce manquante", "vis", "notice", "montage", "assemblage",
                    "manque", "incomplet", "instructions", "mode d'emploi"
                ],
                "severity_range": ["P2"],
                "warranty_component": "assembly",
                "base_priority": 15,
                "description": "Problème de montage"
            },
            "smell": {
                "keywords": [
                    "odeur", "sent", "pue", "mauvaise odeur", "chimique",
                    "forte odeur"
                ],
                "severity_range": ["P2", "P3"],
                "warranty_component": "fabric",
                "base_priority": 12,
                "description": "Problème d'odeur"
            },
            "dimensions": {
                "keywords": [
                    "taille", "dimension", "mesure", "ne rentre pas",
                    "trop grand", "trop petit", "erreur taille"
                ],
                "severity_range": ["P2"],
                "warranty_component": "general",
                "base_priority": 18,
                "description": "Problème de dimensions"
            }
        }

        # Mots-clés de gravité critique
        self.critical_keywords = [
            "danger", "blessure", "risque", "effondre", "cassé net",
            "urgent", "immédiat", "grave", "accident"
        ]

        # Mots-clés d'urgence haute
        self.urgent_keywords = [
            "inutilisable", "ne fonctionne plus", "complètement",
            "totalement", "impossible", "bloqué"
        ]

        # Mots-clés de gravité modérée
        self.moderate_keywords = [
            "gêne", "léger", "petit", "peu", "légèrement",
            "un peu", "parfois"
        ]

    def detect_problem_type(self, description: str) -> ProblemDetectionResult:
        """
        Détecte le type de problème depuis la description

        Args:
            description: Description du problème par le client

        Returns:
            ProblemDetectionResult avec détails de détection
        """

        description_lower = description.lower()
        detected_categories = []

        # Analyse de chaque catégorie
        for category, config in self.problem_categories.items():
            matches = []
            for keyword in config["keywords"]:
                if keyword in description_lower:
                    matches.append(keyword)

            if matches:
                confidence = self._calculate_confidence(
                    matches,
                    config["keywords"],
                    description_lower
                )

                detected_categories.append({
                    "category": category,
                    "confidence": confidence,
                    "matched_keywords": matches,
                    "severity_range": config["severity_range"],
                    "warranty_component": config["warranty_component"],
                    "description": config["description"]
                })

        # Trier par confiance décroissante
        detected_categories.sort(key=lambda x: x["confidence"], reverse=True)

        # Vérifier si clarification nécessaire
        needs_clarification = len(detected_categories) == 0 or (
            len(detected_categories) > 1 and
            abs(detected_categories[0]["confidence"] - detected_categories[1]["confidence"]) < 0.2
        )

        # Résultat principal
        if detected_categories:
            primary = detected_categories[0]

            # Déterminer sévérité basée sur mots-clés
            severity = self.classify_severity(primary["category"], description_lower)

            logger.info(
                f"🔍 Problème détecté: {primary['category']} "
                f"(confiance: {primary['confidence']:.2f}, sévérité: {severity})"
            )

            return ProblemDetectionResult(
                primary_category=primary["category"],
                confidence=primary["confidence"],
                matched_keywords=primary["matched_keywords"],
                severity=severity,
                warranty_component=primary["warranty_component"],
                all_detected_categories=detected_categories,
                needs_clarification=needs_clarification
            )
        else:
            logger.warning(f"⚠️ Impossible de classifier le problème: {description[:50]}...")
            return ProblemDetectionResult(
                primary_category="unknown",
                confidence=0.0,
                matched_keywords=[],
                severity="P3",
                warranty_component="general",
                all_detected_categories=[],
                needs_clarification=True
            )

    def _calculate_confidence(
        self,
        matches: List[str],
        all_keywords: List[str],
        description: str
    ) -> float:
        """
        Calcule un score de confiance

        Args:
            matches: Mots-clés trouvés
            all_keywords: Tous les mots-clés possibles
            description: Description complète

        Returns:
            Score de confiance entre 0 et 1
        """

        # Facteur 1: Ratio de mots-clés matchés
        keyword_ratio = len(matches) / len(all_keywords)

        # Facteur 2: Nombre total de matches
        match_count_score = min(len(matches) / 3, 1.0)  # Plafonné à 3 matches

        # Facteur 3: Longueur des matches (préférer matches longs)
        avg_match_length = sum(len(m) for m in matches) / len(matches)
        length_score = min(avg_match_length / 15, 1.0)

        # Facteur 4: Position dans le texte (début = plus important)
        first_match_pos = description.find(matches[0])
        position_score = 1.0 - (first_match_pos / max(len(description), 1))
        position_score = max(0, min(position_score, 1.0))

        # Score final pondéré
        confidence = (
            keyword_ratio * 0.3 +
            match_count_score * 0.3 +
            length_score * 0.2 +
            position_score * 0.2
        )

        return min(confidence, 1.0)

    def classify_severity(self, problem_type: str, description: str) -> str:
        """
        Classifie la gravité du problème

        Args:
            problem_type: Type de problème détecté
            description: Description (lowercase)

        Returns:
            Priorité: P0, P1, P2, or P3
        """

        # P0 - CRITIQUE (danger immédiat)
        if any(kw in description for kw in self.critical_keywords):
            return "P0"

        # P1 - HAUTE (fonction principale inutilisable)
        if any(kw in description for kw in self.urgent_keywords):
            return "P1"

        # P2 - MOYENNE (gêne mais utilisable)
        if any(kw in description for kw in self.moderate_keywords):
            return "P2"

        # Sinon, utiliser la plage par défaut du type
        config = self.problem_categories.get(problem_type, {})
        severity_range = config.get("severity_range", ["P3"])

        # Prendre la priorité la plus haute de la plage
        return severity_range[0] if severity_range else "P3"

    def extract_symptoms(self, description: str) -> List[str]:
        """
        Extrait les symptômes spécifiques du problème

        Args:
            description: Description du problème

        Returns:
            Liste de symptômes identifiés
        """

        symptoms = []
        description_lower = description.lower()

        # Patterns de symptômes
        symptom_patterns = {
            "duration": r"(?:depuis|il y a|ça fait)\s+(\d+\s+(?:jour|semaine|mois|an)s?)",
            "frequency": r"(?:tout le temps|parfois|souvent|rarement|toujours)",
            "location": r"(?:côté|partie|zone|endroit)\s+(?:gauche|droit|haut|bas|milieu)",
            "intensity": r"(?:très|assez|peu|légèrement|énormément)\s+(?:fort|faible|grave|gênant)"
        }

        for symptom_type, pattern in symptom_patterns.items():
            matches = re.findall(pattern, description_lower)
            if matches:
                symptoms.append(f"{symptom_type}: {matches[0]}")

        return symptoms


# Instance globale
problem_detector = ProblemDetectionEngine()
