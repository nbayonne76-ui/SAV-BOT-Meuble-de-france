# backend/app/services/priority_scorer.py
"""
Système de calcul de priorité multi-critères pour les tickets SAV
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

from app.core.constants import (
    PRIORITY_SLA_TIMES,
    PROBLEM_TYPE_WEIGHTS,
    SEVERITY_WEIGHTS,
    CUSTOMER_TIER_WEIGHTS,
    CRITICAL_KEYWORDS_SCORE,
    SCORE_TO_PRIORITY_THRESHOLDS
)

logger = logging.getLogger(__name__)


@dataclass
class PriorityScore:
    """Résultat du calcul de priorité"""
    total_score: int
    priority: str  # P0, P1, P2, P3
    factors: List[str]
    explanation: str
    response_time_hours: int
    intervention_time_hours: int


class PriorityScorer:
    """
    Système de scoring automatique de priorité SAV
    """

    def __init__(self):
        # Configuration des temps de réponse par priorité - importée depuis constants.py
        self.response_times = PRIORITY_SLA_TIMES

    def calculate_priority(
        self,
        problem_category: str,
        problem_severity: str,
        days_since_purchase: int,
        under_warranty: bool,
        customer_tier: str = "standard",
        has_critical_keywords: bool = False,
        previous_claims_count: int = 0,
        product_value: float = 0.0
    ) -> PriorityScore:
        """
        Calcule la priorité d'un ticket SAV basé sur multiples critères

        Args:
            problem_category: Type de problème (structural, mechanism, etc.)
            problem_severity: Sévérité détectée (P0-P3)
            days_since_purchase: Nombre de jours depuis l'achat
            under_warranty: Si sous garantie
            customer_tier: Niveau de fidélité (vip, gold, silver, standard)
            has_critical_keywords: Si mots-clés critiques détectés
            previous_claims_count: Nombre de réclamations précédentes
            product_value: Valeur du produit en euros

        Returns:
            PriorityScore avec score total et priorité finale
        """

        score = 0
        factors = []

        # FACTEUR 1: Type de problème (0-30 points)
        problem_score = PROBLEM_TYPE_WEIGHTS.get(problem_category, 10)
        score += problem_score
        factors.append(f"Type problème ({problem_category}): +{problem_score}")

        # FACTEUR 2: Sévérité initiale (0-25 points)
        severity_score = SEVERITY_WEIGHTS.get(problem_severity, 10)
        score += severity_score
        factors.append(f"Sévérité ({problem_severity}): +{severity_score}")

        # FACTEUR 3: Âge du produit (0-20 points)
        if days_since_purchase < 7:
            age_score = 20  # Produit très récent
        elif days_since_purchase < 30:
            age_score = 18  # Premier mois
        elif days_since_purchase < 90:
            age_score = 15  # Premiers 3 mois
        elif days_since_purchase < 365:
            age_score = 10  # Première année
        elif days_since_purchase < 730:
            age_score = 8   # Deuxième année
        else:
            age_score = 5   # Plus ancien

        score += age_score
        factors.append(f"Âge produit ({days_since_purchase}j): +{age_score}")

        # FACTEUR 4: Statut garantie (0-15 points)
        if under_warranty:
            warranty_score = 15
        else:
            warranty_score = 5
        score += warranty_score
        factors.append(f"Garantie ({'active' if under_warranty else 'expirée'}): +{warranty_score}")

        # FACTEUR 5: Niveau client (0-15 points)
        tier_score = CUSTOMER_TIER_WEIGHTS.get(customer_tier.lower(), 0)
        score += tier_score
        factors.append(f"Fidélité ({customer_tier}): +{tier_score}")

        # FACTEUR 6: Mots-clés critiques (0-20 points)
        if has_critical_keywords:
            score += CRITICAL_KEYWORDS_SCORE
            factors.append(f"Urgence détectée: +{CRITICAL_KEYWORDS_SCORE}")

        # FACTEUR 7: Historique réclamations (0-10 points)
        if previous_claims_count == 0:
            history_score = 10  # Première réclamation = priorité
        elif previous_claims_count == 1:
            history_score = 8
        elif previous_claims_count == 2:
            history_score = 5
        else:
            history_score = 3  # Client récurrent (potentiellement problématique)

        score += history_score
        factors.append(f"Historique ({previous_claims_count} réclamations): +{history_score}")

        # FACTEUR 8: Valeur produit (0-5 points)
        if product_value > 3000:
            value_score = 5
        elif product_value > 2000:
            value_score = 4
        elif product_value > 1000:
            value_score = 3
        else:
            value_score = 2

        score += value_score
        factors.append(f"Valeur produit ({product_value}€): +{value_score}")

        # CLASSIFICATION FINALE
        if score >= SCORE_TO_PRIORITY_THRESHOLDS["P0"] or problem_severity == "P0":
            priority = "P0"
        elif score >= SCORE_TO_PRIORITY_THRESHOLDS["P1"]:
            priority = "P1"
        elif score >= SCORE_TO_PRIORITY_THRESHOLDS["P2"]:
            priority = "P2"
        else:
            priority = "P3"

        # Temps de réponse
        times = self.response_times[priority]

        # Explication
        explanation = self._generate_explanation(
            priority=priority,
            score=score,
            problem_category=problem_category,
            under_warranty=under_warranty
        )

        logger.info(
            f"📊 Score priorité: {score}/100 → {priority} "
            f"(Réponse: {times['response_hours']}h, Intervention: {times['intervention_hours']}h)"
        )

        return PriorityScore(
            total_score=score,
            priority=priority,
            factors=factors,
            explanation=explanation,
            response_time_hours=times["response_hours"],
            intervention_time_hours=times["intervention_hours"]
        )

    def _generate_explanation(
        self,
        priority: str,
        score: int,
        problem_category: str,
        under_warranty: bool
    ) -> str:
        """
        Génère une explication humaine de la priorité

        Args:
            priority: Priorité calculée
            score: Score total
            problem_category: Catégorie du problème
            under_warranty: Si sous garantie

        Returns:
            Explication textuelle
        """

        explanations = {
            "P0": (
                f"🔴 CRITIQUE (score: {score}/100) - "
                "Danger immédiat ou produit totalement inutilisable. "
                "Intervention urgente requise."
            ),
            "P1": (
                f"🟠 HAUTE (score: {score}/100) - "
                "Fonction principale affectée. "
                "Intervention rapide nécessaire."
            ),
            "P2": (
                f"🟡 MOYENNE (score: {score}/100) - "
                "Défaut gênant mais produit utilisable. "
                "Intervention programmée dans les jours qui viennent."
            ),
            "P3": (
                f"🟢 BASSE (score: {score}/100) - "
                "Demande d'information ou défaut mineur. "
                "Traitement standard."
            )
        }

        base_explanation = explanations.get(priority, f"Score: {score}/100")

        # Ajouter contexte garantie
        warranty_context = (
            " Prise en charge gratuite sous garantie."
            if under_warranty
            else " Intervention payante (hors garantie)."
        )

        return base_explanation + warranty_context

    def should_auto_resolve(self, priority_score: PriorityScore, evidence_complete: bool) -> bool:
        """
        Détermine si le cas peut être résolu automatiquement

        Args:
            priority_score: Score de priorité calculé
            evidence_complete: Si les preuves sont complètes

        Returns:
            True si résolution auto possible
        """

        # Critères de résolution automatique
        auto_resolve_conditions = [
            priority_score.priority in ["P2", "P3"],  # Priorités basses
            evidence_complete,  # Preuves complètes
            priority_score.total_score < 70  # Score pas trop élevé
        ]

        return all(auto_resolve_conditions)

    def should_escalate_to_human(self, priority_score: PriorityScore) -> bool:
        """
        Détermine si escalade vers humain nécessaire

        Args:
            priority_score: Score de priorité

        Returns:
            True si escalade nécessaire
        """

        # Escalade si:
        escalate_conditions = [
            priority_score.priority == "P0",  # Toujours escalader P0
            priority_score.total_score >= 85,  # Score très élevé
        ]

        return any(escalate_conditions)


# Instance globale
priority_scorer = PriorityScorer()
