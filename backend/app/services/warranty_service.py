# backend/app/services/warranty_service.py
"""
Service de gestion des garanties
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from app.models.warranty import (
    Warranty,
    WarrantyCheck,
    WarrantyType,
    WarrantyStatus,
    WarrantyCoverage,
    WarrantyClaim
)

logger = logging.getLogger(__name__)


class WarrantyService:
    """
    Service de vérification et gestion des garanties
    """

    def __init__(self):
        # Mapping des problèmes vers les composants
        self.problem_to_component = {
            "affaissement": "cushions",
            "coussin": "cushions",
            "mousse": "cushions",
            "structure": "structure",
            "pied": "structure",
            "cassé": "structure",
            "fissure": "structure",
            "mécanisme": "mechanisms",
            "relax": "mechanisms",
            "convertible": "mechanisms",
            "tache": "fabric",
            "tissu": "fabric",
            "cuir": "fabric",
            "déchirure": "fabric",
            "décoloration": "fabric"
        }

    def check_warranty_coverage(
        self,
        warranty: Warranty,
        problem_description: str,
        problem_type: str = None
    ) -> WarrantyCheck:
        """
        Vérifie si un problème est couvert par la garantie

        Args:
            warranty: Objet garantie
            problem_description: Description du problème
            problem_type: Type de problème (optionnel)

        Returns:
            WarrantyCheck avec résultat de vérification
        """

        # Déterminer le composant concerné
        component = self._identify_component(problem_description, problem_type)

        # Vérifier si garantie active
        if not warranty.is_active():
            return WarrantyCheck(
                warranty_id=warranty.warranty_id,
                is_valid=False,
                is_covered=False,
                component=component,
                days_remaining=0,
                reason="Garantie expirée",
                recommendation="Devis d'intervention payante disponible"
            )

        # Vérifier si composant couvert
        if not warranty.is_component_covered(component):
            return WarrantyCheck(
                warranty_id=warranty.warranty_id,
                is_valid=True,
                is_covered=False,
                component=component,
                days_remaining=warranty.get_remaining_days(),
                reason=f"Composant '{component}' non couvert ou garantie expirée pour ce composant",
                recommendation="Intervention payante possible"
            )

        # Vérifier exclusions
        exclusions = self._check_exclusions(warranty, component, problem_description)

        if exclusions:
            return WarrantyCheck(
                warranty_id=warranty.warranty_id,
                is_valid=True,
                is_covered=False,
                component=component,
                days_remaining=warranty.get_remaining_days(component),
                exclusions_apply=exclusions,
                reason=f"Exclusions applicables: {', '.join(exclusions)}",
                recommendation="Non éligible garantie - Intervention payante possible"
            )

        # Tout est OK - Couvert
        return WarrantyCheck(
            warranty_id=warranty.warranty_id,
            is_valid=True,
            is_covered=True,
            component=component,
            days_remaining=warranty.get_remaining_days(component),
            exclusions_apply=[],
            reason="Garantie active, composant couvert, aucune exclusion",
            recommendation="Éligible pour réparation/remplacement gratuit sous garantie"
        )

    def _identify_component(self, description: str, problem_type: str = None) -> str:
        """
        Identifie le composant concerné depuis la description

        Args:
            description: Description du problème
            problem_type: Type de problème (optionnel)

        Returns:
            Nom du composant
        """

        description_lower = description.lower()

        # Chercher dans les mots-clés
        for keyword, component in self.problem_to_component.items():
            if keyword in description_lower:
                logger.info(f"Composant identifié: {component} (mot-clé: {keyword})")
                return component

        # Si type de problème fourni
        if problem_type:
            if "structural" in problem_type:
                return "structure"
            elif "mechanism" in problem_type:
                return "mechanisms"
            elif "fabric" in problem_type or "cushion" in problem_type:
                return "fabric"

        # Par défaut: composant général
        logger.warning(f"Impossible d'identifier composant précis depuis: {description}")
        return "general"

    def _check_exclusions(
        self,
        warranty: Warranty,
        component: str,
        description: str
    ) -> List[str]:
        """
        Vérifie si des exclusions s'appliquent

        Args:
            warranty: Objet garantie
            component: Composant concerné
            description: Description du problème

        Returns:
            Liste des exclusions qui s'appliquent
        """

        if component not in warranty.coverage:
            return []

        description_lower = description.lower()
        applicable_exclusions = []

        # Vérifier chaque exclusion
        for exclusion in warranty.coverage[component].exclusions:
            # Mapping exclusions → mots-clés
            exclusion_keywords = {
                "stains": ["tache", "tâche", "sali", "sale"],
                "tears": ["déchirure", "déchiré", "accroc", "trou"],
                "burns": ["brûlure", "brulure", "cigarette"],
                "scratches": ["rayure", "griffure", "érafflure"],
                "misuse": ["mauvais usage", "usage anormal", "accident"],
                "water_damage": ["eau", "humidité", "mouillé", "inondation"],
                "pet_damage": ["animal", "chien", "chat", "griffe"]
            }

            if exclusion in exclusion_keywords:
                keywords = exclusion_keywords[exclusion]
                if any(kw in description_lower for kw in keywords):
                    applicable_exclusions.append(exclusion)
                    logger.info(f"Exclusion applicable: {exclusion}")

        return applicable_exclusions

    async def create_warranty(
        self,
        order_number: str,
        product_sku: str,
        product_name: str,
        customer_id: str,
        purchase_date: datetime,
        delivery_date: datetime,
        warranty_type: WarrantyType = WarrantyType.STANDARD
    ) -> Warranty:
        """
        Crée une nouvelle garantie

        Args:
            order_number: Numéro de commande
            product_sku: SKU du produit
            product_name: Nom du produit
            customer_id: ID client
            purchase_date: Date d'achat
            delivery_date: Date de livraison
            warranty_type: Type de garantie

        Returns:
            Objet Warranty créé
        """

        # Générer ID garantie
        warranty_id = f"WAR-{datetime.now().strftime('%Y%m%d')}-{order_number.split('-')[-1]}"

        # Dates de garantie (commence à la livraison)
        start_date = delivery_date
        end_date = delivery_date + timedelta(days=730)  # 2 ans standard

        # Configuration des couvertures par défaut
        coverage = {
            "structure": WarrantyCoverage(
                covered=True,
                duration_years=5,
                end_date=delivery_date + timedelta(days=1825),  # 5 ans
                exclusions=[]
            ),
            "fabric": WarrantyCoverage(
                covered=True,
                duration_years=2,
                end_date=delivery_date + timedelta(days=730),  # 2 ans
                exclusions=["stains", "tears", "burns", "pet_damage"]
            ),
            "mechanisms": WarrantyCoverage(
                covered=True,
                duration_years=3,
                end_date=delivery_date + timedelta(days=1095),  # 3 ans
                exclusions=[]
            ),
            "cushions": WarrantyCoverage(
                covered=True,
                duration_years=2,
                end_date=delivery_date + timedelta(days=730),  # 2 ans
                exclusions=["stains"]
            )
        }

        warranty = Warranty(
            warranty_id=warranty_id,
            order_number=order_number,
            product_sku=product_sku,
            product_name=product_name,
            customer_id=customer_id,
            purchase_date=purchase_date,
            delivery_date=delivery_date,
            start_date=start_date,
            end_date=end_date,
            type=warranty_type,
            status=WarrantyStatus.ACTIVE,
            coverage=coverage,
            claims_history=[]
        )

        logger.info(f"✅ Garantie créée: {warranty_id} pour commande {order_number}")

        return warranty

    async def add_claim(
        self,
        warranty: Warranty,
        claim_type: str,
        description: str,
        resolution: str = None,
        cost: float = 0.0
    ) -> Warranty:
        """
        Ajoute une réclamation à l'historique

        Args:
            warranty: Objet garantie
            claim_type: Type de réclamation
            description: Description
            resolution: Résolution (optionnel)
            cost: Coût (optionnel)

        Returns:
            Warranty mis à jour
        """

        claim_id = f"CLM-{datetime.now().strftime('%Y%m%d')}-{len(warranty.claims_history) + 1:03d}"

        claim = WarrantyClaim(
            claim_id=claim_id,
            date=datetime.now(),
            type=claim_type,
            description=description,
            status="pending" if not resolution else "resolved",
            resolution=resolution,
            cost=cost
        )

        warranty.claims_history.append(claim)
        warranty.updated_at = datetime.now()

        logger.info(f"✅ Réclamation ajoutée: {claim_id} pour garantie {warranty.warranty_id}")

        return warranty


# Instance globale
warranty_service = WarrantyService()
