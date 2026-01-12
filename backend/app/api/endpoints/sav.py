# backend/app/api/endpoints/sav.py
"""
Endpoints API pour le système SAV automatisé
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.sav_workflow_engine import sav_workflow_engine, SAVTicket
from app.services.evidence_collector import evidence_collector, EvidenceType
from app.services.warranty_service import warranty_service
from app.models.warranty import Warranty, WarrantyType
from app.db.session import get_db
from app.repositories.ticket_repository import ticket_repository

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sav", tags=["SAV"])


# ============ MODÈLES DE REQUÊTES ============

class CreateClaimRequest(BaseModel):
    """Requête de création de réclamation SAV"""
    customer_id: str
    order_number: str
    product_sku: str
    product_name: str
    problem_description: str
    purchase_date: str  # ISO format
    delivery_date: str  # ISO format
    customer_tier: str = "standard"
    product_value: float = 0.0


class AddEvidenceRequest(BaseModel):
    """Requête d'ajout de preuve"""
    ticket_id: str
    evidence_type: str  # photo, video, document
    evidence_url: str
    file_size_bytes: int
    description: str
    metadata: Optional[dict] = None


class TicketStatusRequest(BaseModel):
    """Requête de statut de ticket"""
    ticket_id: str


# ============ ENDPOINTS ============

@router.post("/create-claim")
async def create_claim(request: CreateClaimRequest, db: AsyncSession = Depends(get_db)):
    """
    Crée une nouvelle réclamation SAV et lance le workflow automatique (avec persistence DB)

    Returns:
        Ticket SAV créé avec analyse complète
    """

    try:
        logger.info(f"Nouvelle réclamation SAV: {request.order_number}")

        # Parser les dates
        purchase_date = datetime.fromisoformat(request.purchase_date.replace('Z', '+00:00'))
        delivery_date = datetime.fromisoformat(request.delivery_date.replace('Z', '+00:00'))

        # Créer ou récupérer la garantie
        # NOTE: Dans un vrai système, on récupérerait depuis la DB
        warranty = await warranty_service.create_warranty(
            order_number=request.order_number,
            product_sku=request.product_sku,
            product_name=request.product_name,
            customer_id=request.customer_id,
            purchase_date=purchase_date,
            delivery_date=delivery_date,
            warranty_type=WarrantyType.STANDARD
        )

        # Créer workflow engine avec session DB pour persistence
        from app.services.sav_workflow_engine import SAVWorkflowEngine
        workflow_with_db = SAVWorkflowEngine(db_session=db)

        # Lancer le workflow SAV
        ticket = await workflow_with_db.process_new_claim(
            customer_id=request.customer_id,
            order_number=request.order_number,
            product_sku=request.product_sku,
            product_name=request.product_name,
            problem_description=request.problem_description,
            warranty=warranty,
            customer_tier=request.customer_tier,
            product_value=request.product_value
        )

        # Générer le message de demande de preuves
        evidence_message = evidence_collector.generate_evidence_request_message(
            problem_category=ticket.problem_category,
            priority=ticket.priority
        )

        # Construire la réponse
        response = {
            "success": True,
            "ticket": {
                "ticket_id": ticket.ticket_id,
                "status": ticket.status,
                "priority": ticket.priority,
                "priority_score": ticket.priority_score,
                "problem_category": ticket.problem_category,
                "problem_severity": ticket.problem_severity,
                "problem_confidence": ticket.problem_confidence,
                "warranty_covered": ticket.warranty_check_result.is_covered if ticket.warranty_check_result else False,
                "warranty_component": ticket.warranty_check_result.component if ticket.warranty_check_result else None,
                "auto_resolved": ticket.auto_resolved,
                "resolution_type": ticket.resolution_type,
                "resolution_description": ticket.resolution_description,
                "sla_response_deadline": ticket.sla_response_deadline.isoformat() if ticket.sla_response_deadline else None,
                "sla_intervention_deadline": ticket.sla_intervention_deadline.isoformat() if ticket.sla_intervention_deadline else None,
                "created_at": ticket.created_at.isoformat()
            },
            "evidence_requirements": evidence_message,
            "next_steps": _generate_next_steps(ticket)
        }

        logger.info(f"Réclamation traitée: {ticket.ticket_id} | {ticket.status}")

        return response

    except Exception as e:
        logger.error(f"Erreur création réclamation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.post("/add-evidence")
async def add_evidence(request: AddEvidenceRequest):
    """
    Ajoute une preuve (photo, vidéo) à un ticket SAV

    Returns:
        Analyse de la preuve et statut de complétude
    """

    try:
        logger.info(f"Ajout preuve pour ticket: {request.ticket_id}")

        # Analyser la qualité de la preuve
        evidence_analysis = evidence_collector.analyze_evidence(
            evidence_id=f"{request.ticket_id}-EVD",
            evidence_type=EvidenceType(request.evidence_type),
            file_url=request.evidence_url,
            file_size_bytes=request.file_size_bytes,
            description=request.description,
            metadata=request.metadata
        )

        # Ajouter la preuve au ticket
        ticket = sav_workflow_engine.add_evidence(
            ticket_id=request.ticket_id,
            evidence_type=request.evidence_type,
            evidence_url=request.evidence_url,
            description=request.description
        )

        # Vérifier la complétude
        completeness = evidence_collector.check_completeness(
            problem_category=ticket.problem_category,
            evidences=[
                {
                    "type": e.type,
                    "quality_score": getattr(e, "quality_score", 0)
                }
                for e in ticket.evidences
            ],
            problem_severity=ticket.problem_severity
        )

        response = {
            "success": True,
            "evidence_analysis": {
                "quality": evidence_analysis.quality,
                "quality_score": evidence_analysis.quality_score,
                "issues": evidence_analysis.issues,
                "strengths": evidence_analysis.strengths,
                "recommendations": evidence_analysis.recommendations,
                "verified": evidence_analysis.verified
            },
            "completeness": {
                "is_complete": completeness.is_complete,
                "completeness_score": completeness.completeness_score,
                "missing_items": completeness.missing_items,
                "additional_requests": completeness.additional_requests,
                "can_proceed": completeness.can_proceed
            },
            "ticket_status": ticket.status,
            "evidence_count": len(ticket.evidences)
        }

        logger.info(
            f"Preuve ajoutée: {evidence_analysis.quality} | "
            f"Complétude: {completeness.completeness_score:.0f}%"
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur ajout preuve: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ajout: {str(e)}")


@router.get("/ticket/{ticket_id}")
async def get_ticket_status(ticket_id: str):
    """
    Récupère le statut complet d'un ticket SAV

    Returns:
        Détails complets du ticket
    """

    try:
        summary = sav_workflow_engine.get_ticket_summary(ticket_id)

        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])

        return {
            "success": True,
            "ticket": summary
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/ticket/{ticket_id}/history")
async def get_ticket_history(ticket_id: str):
    """
    Récupère l'historique complet des actions d'un ticket

    Returns:
        Liste chronologique des actions
    """

    try:
        if ticket_id not in sav_workflow_engine.active_tickets:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} non trouvé")

        ticket = sav_workflow_engine.active_tickets[ticket_id]

        return {
            "success": True,
            "ticket_id": ticket_id,
            "actions": [
                {
                    "action_id": action.action_id,
                    "timestamp": action.timestamp.isoformat(),
                    "actor": action.actor,
                    "action_type": action.action_type,
                    "description": action.description,
                    "metadata": action.metadata
                }
                for action in ticket.actions
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération historique: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/evidence-requirements/{problem_category}")
async def get_evidence_requirements(problem_category: str, priority: str = "P2"):
    """
    Récupère les exigences de preuves pour une catégorie de problème

    Returns:
        Message formaté avec les exigences
    """

    try:
        message = evidence_collector.generate_evidence_request_message(
            problem_category=problem_category,
            priority=priority
        )

        requirements = evidence_collector.requirements_by_category.get(
            problem_category,
            {"min_photos": 2, "min_videos": 0}
        )

        return {
            "success": True,
            "message": message,
            "requirements": requirements
        }

    except Exception as e:
        logger.error(f"Erreur récupération exigences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/tickets")
async def get_all_tickets(request: Request, db: AsyncSession = Depends(get_db)):
    """
    NOUVEAU: Récupère tous les tickets SAV pour le tableau de bord (depuis la base de données)

    Returns:
        Liste de tous les tickets avec leurs détails
    """

    try:
        # If DB initialization failed at startup, return 503 with helpful message
        if getattr(request.app.state, "db_available", False) is False:
            logger.error("Database unavailable - cannot fetch tickets")
            raise HTTPException(status_code=503, detail="Database temporarily unavailable. Please try again later.")

        logger.info("Récupération de tous les tickets SAV depuis la base de données")

        # Récupérer les tickets depuis la base de données
        try:
            db_tickets = await ticket_repository.get_all(db, limit=100)
        except (ConnectionRefusedError, OSError) as conn_err:
            logger.error(f"Database connection error when fetching tickets: {conn_err}")
            raise HTTPException(status_code=503, detail="Database connection refused. Please check DB configuration and availability.")

        tickets_list = []

        for db_ticket in db_tickets:
            ticket_summary = {
                "ticket_id": db_ticket.ticket_id,
                "customer_id": db_ticket.customer_id,
                "customer_name": db_ticket.customer_name or 'Client',
                "order_number": db_ticket.order_number,
                "product_name": db_ticket.product_name,
                "problem_description": db_ticket.problem_description[:100] + "..." if db_ticket.problem_description and len(db_ticket.problem_description) > 100 else db_ticket.problem_description,
                "problem_category": db_ticket.problem_category,
                "priority": db_ticket.priority,
                "priority_score": db_ticket.priority_score,
                "status": db_ticket.status,
                "warranty_covered": db_ticket.warranty_status == "covered" if db_ticket.warranty_status else False,
                "auto_resolved": db_ticket.auto_resolved,
                "created_at": db_ticket.created_at.isoformat() if db_ticket.created_at else None,
                "sla_response_deadline": db_ticket.sla_response_deadline.isoformat() if db_ticket.sla_response_deadline else None,
                "evidence_count": len(db_ticket.evidence) if db_ticket.evidence else 0,

                # NOUVEAU: Données pour analyse de ton
                "tone": db_ticket.tone_category,
                "urgency": "high" if db_ticket.priority in ["P0", "P1"] else "medium" if db_ticket.priority == "P2" else "low",
                "emotion_score": db_ticket.tone_score or 0,

                # NOUVEAU: Validation client
                "validation_status": getattr(db_ticket, 'validation_status', 'pending'),
                "validation_required": db_ticket.client_summary.get('validation_required', False) if db_ticket.client_summary else False
            }

            tickets_list.append(ticket_summary)

        # Trier par priorité et date de création (plus récent d'abord)
        tickets_list.sort(
            key=lambda t: (
                {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(t["priority"], 4),
                t["created_at"]
            ),
            reverse=False
        )

        logger.info(f"{len(tickets_list)} tickets récupérés")

        return {
            "success": True,
            "total_tickets": len(tickets_list),
            "tickets": tickets_list
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erreur récupération tickets: {e}")
        # Return 503 for connectivity issues when the message indicates 'refused'
        if "refused" in str(e).lower() or isinstance(e, (ConnectionRefusedError, OSError)):
            raise HTTPException(status_code=503, detail="Database connection refused. Please check DB configuration and availability.")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/ticket/{ticket_id}/dossier")
async def generate_client_dossier(ticket_id: str, db: AsyncSession = Depends(get_db)):
    """
    NOUVEAU: Génère le dossier client complet au format structuré (depuis la base de données)

    Returns:
        Dossier client avec toutes les informations de la réclamation
    """

    try:
        logger.info(f"Génération du dossier client pour: {ticket_id}")

        # Récupérer depuis la base de données
        db_ticket = await ticket_repository.get_by_id(db, ticket_id)

        if not db_ticket:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} non trouvé")

        # Générer le dossier client complet depuis les données de la base
        dossier = {
            # INFORMATIONS TICKET
            "ticket": {
                "ticket_id": db_ticket.ticket_id,
                "created_at": db_ticket.created_at.isoformat() if db_ticket.created_at else None,
                "updated_at": db_ticket.updated_at.isoformat() if db_ticket.updated_at else None,
                "status": db_ticket.status,
                "priority": db_ticket.priority,
                "priority_score": db_ticket.priority_score,
                "priority_factors": db_ticket.priority_factors,
                "source": db_ticket.source or "chat"
            },

            # INFORMATIONS CLIENT
            "client": {
                "customer_id": db_ticket.customer_id,
                "customer_name": db_ticket.customer_name or 'Client',
                "order_number": db_ticket.order_number
            },

            # INFORMATIONS PRODUIT
            "produit": {
                "product_sku": db_ticket.product_sku,
                "product_name": db_ticket.product_name
            },

            # PROBLÈME
            "probleme": {
                "description": db_ticket.problem_description,
                "category": db_ticket.problem_category,
                "severity": db_ticket.problem_severity,
                "confidence": db_ticket.problem_confidence
            },

            # ANALYSE TON
            "analyse_ton": {
                "tone": db_ticket.tone_category,
                "emotion_score": db_ticket.tone_score,
                "detected_keywords": db_ticket.tone_keywords or []
            },

            # GARANTIE
            "garantie": {
                "warranty_id": db_ticket.warranty_id,
                "warranty_status": db_ticket.warranty_status
            },

            # PREUVES
            "preuves": db_ticket.evidence or [],

            # PIÈCES JOINTES
            "attachments": db_ticket.attachments or [],

            # SLA
            "sla": {
                "response_deadline": db_ticket.sla_response_deadline.isoformat() if db_ticket.sla_response_deadline else None,
                "intervention_deadline": db_ticket.sla_intervention_deadline.isoformat() if db_ticket.sla_intervention_deadline else None
            },

            # RÉSOLUTION
            "resolution": {
                "auto_resolved": db_ticket.auto_resolved,
                "resolution_type": db_ticket.resolution_type,
                "resolution_description": db_ticket.resolution_description,
                "resolved_at": db_ticket.resolved_at.isoformat() if db_ticket.resolved_at else None
            },

            # RÉCAPITULATIF CLIENT
            "recapitulatif": db_ticket.client_summary or {},

            # HISTORIQUE
            "historique": db_ticket.actions or [],

            # NOTES
            "notes": db_ticket.notes or []
        }

        logger.info(f"Dossier généré depuis la base de données: {ticket_id}")

        return {
            "success": True,
            "dossier": dossier
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur génération dossier: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


# ============ FONCTIONS UTILITAIRES ============

def _generate_next_steps(ticket: SAVTicket) -> List[str]:
    """Génère les prochaines étapes selon l'état du ticket"""

    next_steps = []

    if ticket.auto_resolved:
        next_steps.append("Votre demande a été traitée automatiquement")
        next_steps.append(f"Solution: {ticket.resolution_description}")

        if ticket.resolution_type == "auto_replacement":
            next_steps.append("Une pièce de remplacement sera expédiée sous 48h")
            next_steps.append("Vous recevrez un email de confirmation avec le numéro de suivi")
        elif ticket.resolution_type == "technician_dispatch":
            next_steps.append("Un technicien vous contactera pour planifier l'intervention")
            next_steps.append(f"⏰ Délai maximal: {ticket.sla_intervention_deadline.strftime('%d/%m/%Y')}")

    elif ticket.status == "escalated_to_human":
        next_steps.append("️ Votre demande nécessite une analyse approfondie")
        next_steps.append("Un conseiller SAV vous contactera rapidement")
        next_steps.append(f"Contact prévu avant: {ticket.sla_response_deadline.strftime('%d/%m/%Y à %H:%M')}")

    elif ticket.status == "evidence_collection":
        next_steps.append("Veuillez fournir les preuves requises")
        next_steps.append("⬆️ Uploadez vos photos/vidéos via le bouton ci-dessous")
        next_steps.append("Une fois les preuves reçues, votre demande sera traitée")

    elif ticket.status == "awaiting_technician":
        next_steps.append("Un technicien sera assigné à votre demande")
        next_steps.append(f"⏰ Intervention prévue avant: {ticket.sla_intervention_deadline.strftime('%d/%m/%Y')}")

    # Toujours inclure le numéro de ticket
    next_steps.append(f"Conservez votre numéro de ticket: {ticket.ticket_id}")

    return next_steps
