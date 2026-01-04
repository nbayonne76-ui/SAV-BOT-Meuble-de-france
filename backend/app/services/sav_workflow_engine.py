# backend/app/services/sav_workflow_engine.py
"""
Moteur de workflow automatisé pour le traitement SAV
Orchestre l'ensemble du processus de la réception à la résolution
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from app.services.warranty_service import warranty_service
from app.services.problem_detector import problem_detector
from app.services.priority_scorer import priority_scorer
from app.services.tone_analyzer import tone_analyzer, ToneAnalysis
from app.services.client_summary_generator import client_summary_generator, ClientSummary
from app.models.warranty import Warranty, WarrantyCheck

logger = logging.getLogger(__name__)


class TicketStatus(str, Enum):
    """États possibles d'un ticket SAV"""
    NEW = "new"
    PROBLEM_ANALYSIS = "problem_analysis"
    WARRANTY_CHECK = "warranty_check"
    EVIDENCE_COLLECTION = "evidence_collection"
    PRIORITY_ASSESSMENT = "priority_assessment"
    DECISION_PENDING = "decision_pending"
    AUTO_RESOLVED = "auto_resolved"
    ESCALATED_TO_HUMAN = "escalated_to_human"
    AWAITING_TECHNICIAN = "awaiting_technician"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ResolutionType(str, Enum):
    """Types de résolution possibles"""
    AUTO_REPLACEMENT = "auto_replacement"
    AUTO_REPAIR = "auto_repair"
    AUTO_REFUND = "auto_refund"
    HUMAN_INTERVENTION = "human_intervention"
    TECHNICIAN_DISPATCH = "technician_dispatch"
    SPARE_PARTS_ORDER = "spare_parts_order"
    CUSTOMER_EDUCATION = "customer_education"
    NOT_COVERED = "not_covered"


@dataclass
class Evidence:
    """Preuve fournie par le client"""
    evidence_id: str
    type: str  # photo, video, document
    url: str
    description: str
    uploaded_at: datetime
    verified: bool = False
    quality_score: float = 0.0


@dataclass
class TicketAction:
    """Action effectuée sur le ticket"""
    action_id: str
    timestamp: datetime
    actor: str  # system, human, customer
    action_type: str
    description: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class SAVTicket:
    """Ticket SAV complet"""
    ticket_id: str
    customer_id: str
    order_number: str
    product_sku: str
    product_name: str

    # Problème
    problem_description: str
    problem_category: Optional[str] = None
    problem_severity: Optional[str] = None
    problem_confidence: Optional[float] = None

    # Garantie
    warranty_id: Optional[str] = None
    warranty_check_result: Optional[WarrantyCheck] = None

    # Priorité
    priority: Optional[str] = None
    priority_score: Optional[int] = None
    priority_factors: List[str] = field(default_factory=list)

    # État et résolution
    status: TicketStatus = TicketStatus.NEW
    resolution_type: Optional[ResolutionType] = None
    resolution_description: Optional[str] = None

    # Preuves
    evidences: List[Evidence] = field(default_factory=list)
    evidence_complete: bool = False

    # Actions et historique
    actions: List[TicketAction] = field(default_factory=list)

    # Métadonnées
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    sla_response_deadline: Optional[datetime] = None
    sla_intervention_deadline: Optional[datetime] = None
    assigned_to: Optional[str] = None

    # 🎯 NOUVEAU: Analyse de ton et récapitulatif client
    tone_analysis: Optional[ToneAnalysis] = None
    client_summary: Optional[ClientSummary] = None
    validation_status: str = "pending"  # pending, validated, cancelled

    # Métriques
    auto_resolved: bool = False
    time_to_first_response: Optional[timedelta] = None
    time_to_resolution: Optional[timedelta] = None


class SAVWorkflowEngine:
    """
    Moteur de workflow automatisé pour le traitement SAV
    Implémente le processus complet de bout en bout
    """

    def __init__(self, db_session=None):
        self.active_tickets: Dict[str, SAVTicket] = {}
        self.db_session = db_session  # Optional database session for persistence

        # Configuration des preuves requises par catégorie
        self.evidence_requirements = {
            "structural": {
                "min_photos": 3,
                "require_video": True,
                "description": "Photos de la structure cassée/fissurée + vidéo montrant le problème"
            },
            "mechanism": {
                "min_photos": 2,
                "require_video": True,
                "description": "Photos du mécanisme + vidéo démontrant le blocage"
            },
            "fabric": {
                "min_photos": 2,
                "require_video": False,
                "description": "Photos claires de la zone affectée"
            },
            "cushions": {
                "min_photos": 2,
                "require_video": False,
                "description": "Photos de l'affaissement + vue d'ensemble"
            },
            "delivery": {
                "min_photos": 3,
                "require_video": False,
                "description": "Photos des dommages + emballage + bon de livraison"
            }
        }

    def _persist_ticket(self, ticket: SAVTicket):
        """Persist ticket to database if db_session is available"""
        if self.db_session:
            try:
                from app.repositories.ticket_repository import ticket_repository
                existing = ticket_repository.get_by_id(self.db_session, ticket.ticket_id)
                if existing:
                    ticket_repository.update(self.db_session, ticket)
                else:
                    ticket_repository.create(self.db_session, ticket)
            except Exception as e:
                logger.error(f"Erreur persistence ticket {ticket.ticket_id}: {e}")
                # Ne pas lever l'exception pour ne pas bloquer le workflow
        else:
            logger.debug(f"Ticket {ticket.ticket_id} non persisté (pas de session DB)")

    async def process_new_claim(
        self,
        customer_id: str,
        order_number: str,
        product_sku: str,
        product_name: str,
        problem_description: str,
        warranty: Warranty,
        customer_tier: str = "standard",
        product_value: float = 0.0
    ) -> SAVTicket:
        """
        Point d'entrée principal : traite une nouvelle réclamation

        Args:
            customer_id: ID du client
            order_number: Numéro de commande
            product_sku: SKU du produit
            product_name: Nom du produit
            problem_description: Description du problème
            warranty: Objet garantie
            customer_tier: Niveau de fidélité
            product_value: Valeur du produit

        Returns:
            SAVTicket créé et traité
        """

        logger.info(f"🎫 Nouvelle réclamation SAV: {order_number}")

        # 1. Créer le ticket
        ticket = await self._create_ticket(
            customer_id=customer_id,
            order_number=order_number,
            product_sku=product_sku,
            product_name=product_name,
            problem_description=problem_description,
            warranty_id=warranty.warranty_id
        )

        # 2. Analyser le problème
        ticket = await self._analyze_problem(ticket, problem_description)

        # 🎯 2b. Analyser le ton et l'urgence du client
        ticket = self._analyze_tone(ticket, problem_description)

        # 3. Vérifier la garantie
        ticket = await self._check_warranty(ticket, warranty, problem_description)

        # 4. Calculer la priorité
        ticket = await self._calculate_priority(
            ticket=ticket,
            warranty=warranty,
            customer_tier=customer_tier,
            product_value=product_value
        )

        # 5. Définir les SLA
        ticket = self._set_sla_deadlines(ticket)

        # 6. Déterminer les preuves requises
        ticket = self._determine_evidence_requirements(ticket)

        # 7. Décision automatique
        ticket = await self._make_automated_decision(ticket, warranty)

        # 🎯 8. Générer le récapitulatif client pour validation
        ticket = self._generate_client_summary(ticket)

        # Sauvegarder le ticket en mémoire
        self.active_tickets[ticket.ticket_id] = ticket

        # 🎯 NOUVEAU: Ne persister en base que si validation non requise
        # Si validation requise, attendre la confirmation de l'utilisateur
        if not (ticket.client_summary and ticket.client_summary.validation_required):
            self._persist_ticket(ticket)
            logger.info(f"✅ Ticket {ticket.ticket_id} persisté en base (pas de validation requise)")
        else:
            logger.info(f"⏳ Ticket {ticket.ticket_id} en attente de validation utilisateur (non persisté)")

        logger.info(
            f"✅ Ticket {ticket.ticket_id} traité: "
            f"{ticket.status} | Priorité: {ticket.priority} | "
            f"Auto-résolu: {ticket.auto_resolved} | "
            f"Validation requise: {ticket.client_summary.validation_required if ticket.client_summary else False}"
        )

        return ticket

    async def _create_ticket(
        self,
        customer_id: str,
        order_number: str,
        product_sku: str,
        product_name: str,
        problem_description: str,
        warranty_id: str
    ) -> SAVTicket:
        """Crée un nouveau ticket SAV"""

        ticket_id = f"SAV-{datetime.now().strftime('%Y%m%d')}-{order_number.split('-')[-1]}"

        ticket = SAVTicket(
            ticket_id=ticket_id,
            customer_id=customer_id,
            order_number=order_number,
            product_sku=product_sku,
            product_name=product_name,
            problem_description=problem_description,
            warranty_id=warranty_id,
            status=TicketStatus.NEW
        )

        # Ajouter action
        ticket.actions.append(TicketAction(
            action_id=f"{ticket_id}-ACT-001",
            timestamp=datetime.now(),
            actor="system",
            action_type="ticket_created",
            description="Ticket SAV créé automatiquement"
        ))

        logger.info(f"📝 Ticket créé: {ticket_id}")
        return ticket

    async def _analyze_problem(
        self,
        ticket: SAVTicket,
        problem_description: str
    ) -> SAVTicket:
        """Analyse automatique du problème"""

        ticket.status = TicketStatus.PROBLEM_ANALYSIS

        # Utiliser le moteur de détection
        detection_result = problem_detector.detect_problem_type(problem_description)

        ticket.problem_category = detection_result.primary_category
        ticket.problem_severity = detection_result.severity
        ticket.problem_confidence = detection_result.confidence

        # Ajouter action
        ticket.actions.append(TicketAction(
            action_id=f"{ticket.ticket_id}-ACT-{len(ticket.actions) + 1:03d}",
            timestamp=datetime.now(),
            actor="system",
            action_type="problem_analyzed",
            description=f"Problème détecté: {detection_result.primary_category} (confiance: {detection_result.confidence:.2f})",
            metadata={
                "category": detection_result.primary_category,
                "severity": detection_result.severity,
                "confidence": detection_result.confidence,
                "matched_keywords": detection_result.matched_keywords
            }
        ))

        logger.info(
            f"🔍 Problème analysé pour {ticket.ticket_id}: "
            f"{detection_result.primary_category} | {detection_result.severity}"
        )

        return ticket

    async def _check_warranty(
        self,
        ticket: SAVTicket,
        warranty: Warranty,
        problem_description: str
    ) -> SAVTicket:
        """Vérifie la couverture garantie"""

        ticket.status = TicketStatus.WARRANTY_CHECK

        # Vérifier la garantie
        warranty_check = warranty_service.check_warranty_coverage(
            warranty=warranty,
            problem_description=problem_description,
            problem_type=ticket.problem_category
        )

        ticket.warranty_check_result = warranty_check

        # Ajouter action
        ticket.actions.append(TicketAction(
            action_id=f"{ticket.ticket_id}-ACT-{len(ticket.actions) + 1:03d}",
            timestamp=datetime.now(),
            actor="system",
            action_type="warranty_checked",
            description=f"Garantie vérifiée: {'Couvert' if warranty_check.is_covered else 'Non couvert'}",
            metadata={
                "is_covered": warranty_check.is_covered,
                "component": warranty_check.component,
                "reason": warranty_check.reason,
                "days_remaining": warranty_check.days_remaining
            }
        ))

        logger.info(
            f"🔒 Garantie vérifiée pour {ticket.ticket_id}: "
            f"{'✅ Couvert' if warranty_check.is_covered else '❌ Non couvert'}"
        )

        return ticket

    async def _calculate_priority(
        self,
        ticket: SAVTicket,
        warranty: Warranty,
        customer_tier: str,
        product_value: float
    ) -> SAVTicket:
        """Calcule la priorité du ticket"""

        ticket.status = TicketStatus.PRIORITY_ASSESSMENT

        # Calculer les jours depuis l'achat
        days_since_purchase = (datetime.now() - warranty.purchase_date).days

        # Calculer la priorité
        priority_result = priority_scorer.calculate_priority(
            problem_category=ticket.problem_category,
            problem_severity=ticket.problem_severity,
            days_since_purchase=days_since_purchase,
            under_warranty=ticket.warranty_check_result.is_covered if ticket.warranty_check_result else False,
            customer_tier=customer_tier,
            has_critical_keywords=ticket.problem_severity == "P0",
            previous_claims_count=len(warranty.claims_history),
            product_value=product_value
        )

        ticket.priority = priority_result.priority
        ticket.priority_score = priority_result.total_score
        ticket.priority_factors = priority_result.factors

        # Ajouter action
        ticket.actions.append(TicketAction(
            action_id=f"{ticket.ticket_id}-ACT-{len(ticket.actions) + 1:03d}",
            timestamp=datetime.now(),
            actor="system",
            action_type="priority_calculated",
            description=priority_result.explanation,
            metadata={
                "priority": priority_result.priority,
                "score": priority_result.total_score,
                "factors": priority_result.factors
            }
        ))

        logger.info(
            f"📊 Priorité calculée pour {ticket.ticket_id}: "
            f"{priority_result.priority} (score: {priority_result.total_score})"
        )

        return ticket

    def _set_sla_deadlines(self, ticket: SAVTicket) -> SAVTicket:
        """Définit les deadlines SLA selon la priorité"""

        sla_times = {
            "P0": {"response_hours": 4, "intervention_hours": 24},
            "P1": {"response_hours": 24, "intervention_hours": 48},
            "P2": {"response_hours": 120, "intervention_hours": 168},
            "P3": {"response_hours": 168, "intervention_hours": 336}
        }

        times = sla_times.get(ticket.priority, sla_times["P3"])

        ticket.sla_response_deadline = ticket.created_at + timedelta(hours=times["response_hours"])
        ticket.sla_intervention_deadline = ticket.created_at + timedelta(hours=times["intervention_hours"])

        logger.info(
            f"⏰ SLA défini pour {ticket.ticket_id}: "
            f"Réponse avant {ticket.sla_response_deadline.strftime('%Y-%m-%d %H:%M')}"
        )

        return ticket

    def _determine_evidence_requirements(self, ticket: SAVTicket) -> SAVTicket:
        """Détermine les preuves requises"""

        ticket.status = TicketStatus.EVIDENCE_COLLECTION

        requirements = self.evidence_requirements.get(
            ticket.problem_category,
            {"min_photos": 2, "require_video": False, "description": "Photos du problème"}
        )

        # Ajouter action
        ticket.actions.append(TicketAction(
            action_id=f"{ticket.ticket_id}-ACT-{len(ticket.actions) + 1:03d}",
            timestamp=datetime.now(),
            actor="system",
            action_type="evidence_requirements_set",
            description=f"Preuves requises: {requirements['description']}",
            metadata=requirements
        ))

        logger.info(f"📸 Preuves requises pour {ticket.ticket_id}: {requirements['description']}")

        return ticket

    async def _make_automated_decision(
        self,
        ticket: SAVTicket,
        warranty: Warranty
    ) -> SAVTicket:
        """Prend une décision automatique sur le traitement"""

        ticket.status = TicketStatus.DECISION_PENDING

        # Critères de décision automatique
        can_auto_resolve = self._can_auto_resolve(ticket)
        must_escalate = self._must_escalate_to_human(ticket)

        if must_escalate:
            # Escalade vers humain
            ticket = await self._escalate_to_human(ticket)

        elif can_auto_resolve and ticket.warranty_check_result.is_covered:
            # Résolution automatique
            ticket = await self._auto_resolve(ticket, warranty)

        else:
            # Nécessite intervention mais pas critique
            ticket = await self._assign_to_technician(ticket)

        ticket.updated_at = datetime.now()
        return ticket

    def _can_auto_resolve(self, ticket: SAVTicket) -> bool:
        """Détermine si résolution automatique possible"""

        # Conditions pour auto-résolution
        conditions = [
            ticket.priority in ["P2", "P3"],  # Priorités basses uniquement
            ticket.problem_confidence >= 0.7,  # Confiance élevée dans la détection
            ticket.warranty_check_result.is_covered if ticket.warranty_check_result else False,
            ticket.priority_score < 70,  # Score pas trop élevé
            ticket.problem_category in ["fabric", "cushions", "smell", "assembly"]  # Catégories simples
        ]

        return all(conditions)

    def _must_escalate_to_human(self, ticket: SAVTicket) -> bool:
        """Détermine si escalade obligatoire"""

        # Conditions d'escalade
        conditions = [
            ticket.priority == "P0",  # Toujours escalader P0
            ticket.priority_score >= 85,  # Score critique
            ticket.problem_category == "structural",  # Problèmes structurels
            ticket.problem_confidence < 0.5,  # Incertitude dans la détection
            not ticket.warranty_check_result.is_covered if ticket.warranty_check_result else True  # Hors garantie
        ]

        return any(conditions)

    async def _auto_resolve(self, ticket: SAVTicket, warranty: Warranty) -> SAVTicket:
        """Résolution automatique du ticket"""

        ticket.status = TicketStatus.AUTO_RESOLVED
        ticket.auto_resolved = True

        # Déterminer le type de résolution
        if ticket.problem_category in ["fabric", "cushions"]:
            ticket.resolution_type = ResolutionType.AUTO_REPLACEMENT
            ticket.resolution_description = (
                f"Remplacement automatique du composant {ticket.warranty_check_result.component} "
                f"sous garantie. Pièce de remplacement commandée."
            )
        elif ticket.problem_category == "smell":
            ticket.resolution_type = ResolutionType.CUSTOMER_EDUCATION
            ticket.resolution_description = (
                "Odeur normale sur produit neuf. Disparition prévue sous 2-3 semaines. "
                "Aérer régulièrement la pièce."
            )
        else:
            ticket.resolution_type = ResolutionType.AUTO_REPAIR
            ticket.resolution_description = (
                f"Réparation automatique programmée pour {ticket.warranty_check_result.component}. "
                f"Technicien contactera le client sous 24h."
            )

        # Ajouter action
        ticket.actions.append(TicketAction(
            action_id=f"{ticket.ticket_id}-ACT-{len(ticket.actions) + 1:03d}",
            timestamp=datetime.now(),
            actor="system",
            action_type="auto_resolved",
            description=ticket.resolution_description,
            metadata={
                "resolution_type": ticket.resolution_type,
                "auto_resolved": True
            }
        ))

        # Calculer temps de résolution
        ticket.time_to_resolution = datetime.now() - ticket.created_at

        logger.info(
            f"✅ Auto-résolution pour {ticket.ticket_id}: {ticket.resolution_type} "
            f"(temps: {ticket.time_to_resolution})"
        )

        return ticket

    async def _escalate_to_human(self, ticket: SAVTicket) -> SAVTicket:
        """Escalade vers un opérateur humain"""

        ticket.status = TicketStatus.ESCALATED_TO_HUMAN
        ticket.auto_resolved = False

        # Ajouter action
        ticket.actions.append(TicketAction(
            action_id=f"{ticket.ticket_id}-ACT-{len(ticket.actions) + 1:03d}",
            timestamp=datetime.now(),
            actor="system",
            action_type="escalated_to_human",
            description=f"Escalade vers opérateur humain - Priorité {ticket.priority}",
            metadata={
                "reason": "Critères d'escalade automatique atteints",
                "priority": ticket.priority,
                "score": ticket.priority_score
            }
        ))

        logger.warning(
            f"⚠️  Escalade humaine pour {ticket.ticket_id}: "
            f"Priorité {ticket.priority} | Score {ticket.priority_score}"
        )

        return ticket

    async def _assign_to_technician(self, ticket: SAVTicket) -> SAVTicket:
        """Assigne le ticket à un technicien"""

        ticket.status = TicketStatus.AWAITING_TECHNICIAN
        ticket.resolution_type = ResolutionType.TECHNICIAN_DISPATCH

        # Ajouter action
        ticket.actions.append(TicketAction(
            action_id=f"{ticket.ticket_id}-ACT-{len(ticket.actions) + 1:03d}",
            timestamp=datetime.now(),
            actor="system",
            action_type="assigned_to_technician",
            description=f"Assigné à un technicien - Intervention requise",
            metadata={
                "priority": ticket.priority,
                "sla_deadline": ticket.sla_intervention_deadline.isoformat()
            }
        ))

        logger.info(f"👷 Ticket {ticket.ticket_id} assigné à technicien")

        return ticket

    def add_evidence(
        self,
        ticket_id: str,
        evidence_type: str,
        evidence_url: str,
        description: str
    ) -> SAVTicket:
        """Ajoute une preuve au ticket"""

        if ticket_id not in self.active_tickets:
            raise ValueError(f"Ticket {ticket_id} non trouvé")

        ticket = self.active_tickets[ticket_id]

        evidence_id = f"{ticket_id}-EVD-{len(ticket.evidences) + 1:03d}"

        evidence = Evidence(
            evidence_id=evidence_id,
            type=evidence_type,
            url=evidence_url,
            description=description,
            uploaded_at=datetime.now()
        )

        ticket.evidences.append(evidence)

        # Vérifier si preuves complètes
        requirements = self.evidence_requirements.get(ticket.problem_category, {})

        photo_count = sum(1 for e in ticket.evidences if e.type == "photo")
        video_count = sum(1 for e in ticket.evidences if e.type == "video")

        min_photos = requirements.get("min_photos", 2)
        require_video = requirements.get("require_video", False)

        if photo_count >= min_photos and (not require_video or video_count > 0):
            ticket.evidence_complete = True
            logger.info(f"✅ Preuves complètes pour {ticket_id}")

        ticket.updated_at = datetime.now()

        return ticket

    def _analyze_tone(self, ticket: SAVTicket, problem_description: str) -> SAVTicket:
        """
        Analyse le ton et l'urgence du message client

        Args:
            ticket: Ticket SAV
            problem_description: Description du problème

        Returns:
            Ticket mis à jour avec analyse de ton
        """

        # Analyser le ton avec le ToneAnalyzer
        tone_analysis = tone_analyzer.analyze_tone(problem_description)

        # Sauvegarder l'analyse
        ticket.tone_analysis = tone_analysis

        # Ajuster les SLA selon l'urgence détectée
        if tone_analysis.urgency == "critical" and not ticket.sla_response_deadline:
            # Urgence critique : réponse < 4h
            ticket.sla_response_deadline = ticket.created_at + timedelta(hours=4)
        elif tone_analysis.urgency == "high":
            # Haute urgence : réponse < 24h
            ticket.sla_response_deadline = ticket.created_at + timedelta(hours=24)

        # Ajouter action
        ticket.actions.append(TicketAction(
            action_id=f"{ticket.ticket_id}-ACT-{len(ticket.actions) + 1:03d}",
            timestamp=datetime.now(),
            actor="system",
            action_type="tone_analyzed",
            description=tone_analysis.explanation,
            metadata={
                "tone": tone_analysis.tone,
                "urgency": tone_analysis.urgency,
                "emotion_score": tone_analysis.emotion_score,
                "urgency_score": tone_analysis.urgency_score,
                "requires_empathy": tone_analysis.requires_human_empathy
            }
        ))

        logger.info(
            f"🎭 Ton analysé pour {ticket.ticket_id}: {tone_analysis.tone} | "
            f"Urgence: {tone_analysis.urgency} | Empathie requise: {tone_analysis.requires_human_empathy}"
        )

        return ticket

    def _generate_client_summary(self, ticket: SAVTicket) -> SAVTicket:
        """
        Génère le récapitulatif client pour validation

        Args:
            ticket: Ticket SAV

        Returns:
            Ticket mis à jour avec récapitulatif
        """

        # Préparer les données client (mock - à remplacer par vraies données)
        client_data = {
            "name": ticket.customer_id.split("@")[0] if "@" in ticket.customer_id else "Client",
            "order_number": ticket.order_number,
            "product": ticket.product_name
        }

        # Préparer les données ticket
        ticket_data = {
            "ticket_id": ticket.ticket_id,
            "status": ticket.status,
            "priority": {
                "code": ticket.priority,
                "label": self._get_priority_label(ticket.priority),
                "emoji": self._get_priority_emoji(ticket.priority)
            },
            "problem_description": ticket.problem_description,
            "problem_category": ticket.problem_category,
            "warranty_covered": ticket.warranty_check_result.is_covered if ticket.warranty_check_result else False,
            "auto_resolved": ticket.auto_resolved,
            "resolution_type": ticket.resolution_type,
            "resolution_description": ticket.resolution_description
        }

        # Préparer l'analyse de ton si disponible
        tone_analysis_dict = None
        if ticket.tone_analysis:
            tone_analysis_dict = {
                "recommended_response_time": ticket.tone_analysis.recommended_response_time,
                "requires_empathy": ticket.tone_analysis.requires_human_empathy
            }

        # Générer le récapitulatif
        client_summary = client_summary_generator.generate_summary(
            ticket_data=ticket_data,
            client_data=client_data,
            tone_analysis=tone_analysis_dict
        )

        # Sauvegarder le récapitulatif
        ticket.client_summary = client_summary

        # Ajouter action
        ticket.actions.append(TicketAction(
            action_id=f"{ticket.ticket_id}-ACT-{len(ticket.actions) + 1:03d}",
            timestamp=datetime.now(),
            actor="system",
            action_type="summary_generated",
            description=f"Récapitulatif client généré - Validation requise: {client_summary.validation_required}",
            metadata={
                "summary_id": client_summary.summary_id,
                "validation_required": client_summary.validation_required,
                "validation_link": client_summary.validation_link
            }
        ))

        logger.info(
            f"📧 Récapitulatif généré pour {ticket.ticket_id}: {client_summary.summary_id} | "
            f"Validation requise: {client_summary.validation_required}"
        )

        return ticket

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

    def validate_ticket(self, ticket_id: str) -> Dict:
        """
        Valide un ticket et le persiste en base de données

        Args:
            ticket_id: ID du ticket à valider

        Returns:
            Dict avec le statut de validation
        """
        if ticket_id not in self.active_tickets:
            logger.error(f"❌ Ticket {ticket_id} non trouvé pour validation")
            return {"success": False, "error": f"Ticket {ticket_id} non trouvé"}

        ticket = self.active_tickets[ticket_id]

        # Mettre à jour le statut de validation
        ticket.validation_status = "validated"
        ticket.updated_at = datetime.now()

        # Ajouter une action
        ticket.actions.append(TicketAction(
            action_id=f"{ticket.ticket_id}-ACT-{len(ticket.actions) + 1:03d}",
            timestamp=datetime.now(),
            actor="customer",
            action_type="ticket_validated",
            description="Ticket validé par le client",
            metadata={"validation_time": datetime.now().isoformat()}
        ))

        # Persister en base de données
        self._persist_ticket(ticket)

        logger.info(f"✅ Ticket {ticket_id} validé et persisté en base de données")

        return {
            "success": True,
            "ticket_id": ticket.ticket_id,
            "status": ticket.status,
            "validation_status": ticket.validation_status
        }

    def cancel_ticket(self, ticket_id: str) -> Dict:
        """
        Annule un ticket en attente de validation

        Args:
            ticket_id: ID du ticket à annuler

        Returns:
            Dict avec le statut d'annulation
        """
        if ticket_id not in self.active_tickets:
            logger.error(f"❌ Ticket {ticket_id} non trouvé pour annulation")
            return {"success": False, "error": f"Ticket {ticket_id} non trouvé"}

        ticket = self.active_tickets[ticket_id]

        # Mettre à jour le statut
        ticket.validation_status = "cancelled"
        ticket.status = TicketStatus.CANCELLED
        ticket.updated_at = datetime.now()

        # Ajouter une action
        ticket.actions.append(TicketAction(
            action_id=f"{ticket.ticket_id}-ACT-{len(ticket.actions) + 1:03d}",
            timestamp=datetime.now(),
            actor="customer",
            action_type="ticket_cancelled",
            description="Ticket annulé par le client",
            metadata={"cancellation_time": datetime.now().isoformat()}
        ))

        # Retirer de la liste active
        del self.active_tickets[ticket_id]

        logger.info(f"❌ Ticket {ticket_id} annulé par le client")

        return {
            "success": True,
            "ticket_id": ticket.ticket_id,
            "validation_status": "cancelled"
        }

    def get_ticket_summary(self, ticket_id: str) -> Dict:
        """Génère un résumé du ticket pour le chatbot"""

        if ticket_id not in self.active_tickets:
            return {"error": f"Ticket {ticket_id} non trouvé"}

        ticket = self.active_tickets[ticket_id]

        return {
            "ticket_id": ticket.ticket_id,
            "status": ticket.status,
            "priority": ticket.priority,
            "problem_category": ticket.problem_category,
            "warranty_covered": ticket.warranty_check_result.is_covered if ticket.warranty_check_result else False,
            "auto_resolved": ticket.auto_resolved,
            "resolution_type": ticket.resolution_type,
            "resolution_description": ticket.resolution_description,
            "sla_response_deadline": ticket.sla_response_deadline.isoformat() if ticket.sla_response_deadline else None,
            "evidence_complete": ticket.evidence_complete,
            "actions_count": len(ticket.actions),
            "created_at": ticket.created_at.isoformat(),
            "time_to_resolution": str(ticket.time_to_resolution) if ticket.time_to_resolution else None
        }


# Instance globale
sav_workflow_engine = SAVWorkflowEngine()
