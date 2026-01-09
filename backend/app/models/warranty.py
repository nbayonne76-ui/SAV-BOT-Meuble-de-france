# backend/app/models/warranty.py
"""
Modèles de données pour la gestion des garanties
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from enum import Enum


class WarrantyType(str, Enum):
    """Types de garantie"""
    STANDARD = "standard"
    EXTENDED = "extended"
    PREMIUM = "premium"


class WarrantyStatus(str, Enum):
    """Statuts de garantie"""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    CLAIMED = "claimed"


class WarrantyCoverage(BaseModel):
    """Couverture d'un composant"""
    covered: bool = True
    duration_years: int
    end_date: datetime
    exclusions: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "covered": True,
                "duration_years": 2,
                "end_date": "2026-04-20T00:00:00",
                "exclusions": ["stains", "tears", "burns"]
            }
        }


class WarrantyClaim(BaseModel):
    """Historique de réclamation garantie"""
    claim_id: str
    date: datetime
    type: str
    description: str
    status: str
    resolution: Optional[str] = None
    cost: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "claim_id": "CLM-2024-001",
                "date": "2024-06-10T10:30:00",
                "type": "cushion_sagging",
                "description": "Affaissement des coussins",
                "status": "resolved",
                "resolution": "cushion_replacement",
                "cost": 0.0
            }
        }


class Warranty(BaseModel):
    """Modèle complet de garantie produit"""

    warranty_id: str
    order_number: str
    product_sku: str
    product_name: str
    customer_id: str

    # Dates
    purchase_date: datetime
    delivery_date: datetime
    start_date: datetime
    end_date: datetime

    # Type et statut
    type: WarrantyType = WarrantyType.STANDARD
    status: WarrantyStatus = WarrantyStatus.ACTIVE

    # Couvertures par composant
    coverage: Dict[str, WarrantyCoverage]

    # Historique
    claims_history: List[WarrantyClaim] = Field(default_factory=list)

    # Documents
    certificate_url: Optional[str] = None
    invoice_url: Optional[str] = None

    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def is_active(self) -> bool:
        """Vérifie si la garantie est active"""
        return (
            self.status == WarrantyStatus.ACTIVE and
            datetime.now() < self.end_date
        )

    def is_component_covered(self, component: str, issue_date: Optional[datetime] = None) -> bool:
        """
        Vérifie si un composant est couvert à une date donnée

        Args:
            component: Nom du composant (structure, fabric, mechanisms, etc.)
            issue_date: Date du problème (défaut: aujourd'hui)

        Returns:
            True si couvert, False sinon
        """
        if issue_date is None:
            issue_date = datetime.now()

        if component not in self.coverage:
            return False

        component_coverage = self.coverage[component]

        return (
            component_coverage.covered and
            issue_date < component_coverage.end_date
        )

    def get_remaining_days(self, component: str = None) -> int:
        """
        Retourne le nombre de jours restants de garantie

        Args:
            component: Composant spécifique (optionnel)

        Returns:
            Nombre de jours restants (0 si expirée)
        """
        if component and component in self.coverage:
            end_date = self.coverage[component].end_date
        else:
            end_date = self.end_date

        remaining = (end_date - datetime.now()).days
        return max(0, remaining)

    def get_claims_count(self) -> int:
        """Retourne le nombre de réclamations"""
        return len(self.claims_history)

    def has_exclusion(self, component: str, exclusion: str) -> bool:
        """
        Vérifie si une exclusion s'applique à un composant

        Args:
            component: Nom du composant
            exclusion: Type d'exclusion (ex: "stains", "tears")

        Returns:
            True si l'exclusion s'applique
        """
        if component not in self.coverage:
            return True

        return exclusion in self.coverage[component].exclusions

    class Config:
        json_schema_extra = {
            "example": {
                "warranty_id": "WAR-2024-12345",
                "order_number": "CMD-2024-12345",
                "product_sku": "MDF-CAP-TEMPLE-01",
                "product_name": "Canapé d'angle TEMPLE",
                "customer_id": "CUST-12345",
                "purchase_date": "2024-03-15T10:00:00",
                "delivery_date": "2024-04-20T14:30:00",
                "start_date": "2024-04-20T00:00:00",
                "end_date": "2026-04-20T00:00:00",
                "type": "standard",
                "status": "active",
                "coverage": {
                    "structure": {
                        "covered": True,
                        "duration_years": 5,
                        "end_date": "2029-04-20T00:00:00",
                        "exclusions": []
                    },
                    "fabric": {
                        "covered": True,
                        "duration_years": 2,
                        "end_date": "2026-04-20T00:00:00",
                        "exclusions": ["stains", "tears", "burns"]
                    },
                    "mechanisms": {
                        "covered": True,
                        "duration_years": 3,
                        "end_date": "2027-04-20T00:00:00",
                        "exclusions": []
                    }
                },
                "claims_history": []
            }
        }


class WarrantyCheck(BaseModel):
    """Résultat d'une vérification de garantie"""

    warranty_id: str
    is_valid: bool
    is_covered: bool
    component: str
    days_remaining: int
    exclusions_apply: List[str] = Field(default_factory=list)
    reason: Optional[str] = None
    recommendation: Optional[str] = None
    warranty_start_date: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "warranty_id": "WAR-2024-12345",
                "is_valid": True,
                "is_covered": True,
                "component": "cushions",
                "days_remaining": 456,
                "exclusions_apply": [],
                "reason": "Garantie active, composant couvert",
                "warranty_start_date": datetime.now(),
                "recommendation": "Eligible pour remplacement gratuit"
            }
        }
