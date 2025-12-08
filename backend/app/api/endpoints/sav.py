# backend/app/api/endpoints/sav.py
"""
Endpoints API pour le système SAV automatisé
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.services.sav_workflow_engine import sav_workflow_engine, SAVTicket
from app.services.evidence_collector import evidence_collector, EvidenceType
from app.services.warranty_service import warranty_service
from app.models.warranty import Warranty, WarrantyType

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
async def create_claim(request: CreateClaimRequest):
    """
    Crée une nouvelle réclamation SAV et lance le workflow automatique

    Returns:
        Ticket SAV créé avec analyse complète
    """

    try:
        logger.info(f"📥 Nouvelle réclamation SAV: {request.order_number}")

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

        # Lancer le workflow SAV
        ticket = await sav_workflow_engine.process_new_claim(
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

        logger.info(f"✅ Réclamation traitée: {ticket.ticket_id} | {ticket.status}")

        return response

    except Exception as e:
        logger.error(f"❌ Erreur création réclamation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.post("/add-evidence")
async def add_evidence(request: AddEvidenceRequest):
    """
    Ajoute une preuve (photo, vidéo) à un ticket SAV

    Returns:
        Analyse de la preuve et statut de complétude
    """

    try:
        logger.info(f"📸 Ajout preuve pour ticket: {request.ticket_id}")

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
            f"✅ Preuve ajoutée: {evidence_analysis.quality} | "
            f"Complétude: {completeness.completeness_score:.0f}%"
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Erreur ajout preuve: {str(e)}")
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
        logger.error(f"❌ Erreur récupération ticket: {str(e)}")
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
        logger.error(f"❌ Erreur récupération historique: {str(e)}")
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
        logger.error(f"❌ Erreur récupération exigences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/tickets")
async def get_all_tickets():
    """
    📊 NOUVEAU: Récupère tous les tickets SAV pour le tableau de bord

    Returns:
        Liste de tous les tickets avec leurs détails
    """

    try:
        logger.info("📊 Récupération de tous les tickets SAV")

        tickets_list = []

        for ticket_id, ticket in sav_workflow_engine.active_tickets.items():
            ticket_summary = {
                "ticket_id": ticket.ticket_id,
                "customer_id": ticket.customer_id,
                "customer_name": getattr(ticket, 'customer_name', 'Client'),
                "order_number": ticket.order_number,
                "product_name": ticket.product_name,
                "problem_description": ticket.problem_description[:100] + "..." if len(ticket.problem_description) > 100 else ticket.problem_description,
                "problem_category": ticket.problem_category,
                "priority": ticket.priority,
                "priority_score": ticket.priority_score,
                "status": ticket.status,
                "warranty_covered": ticket.warranty_check_result.is_covered if ticket.warranty_check_result else False,
                "auto_resolved": ticket.auto_resolved,
                "created_at": ticket.created_at.isoformat(),
                "sla_response_deadline": ticket.sla_response_deadline.isoformat() if ticket.sla_response_deadline else None,
                "evidence_count": len(ticket.evidences),

                # 🎯 NOUVEAU: Données pour analyse de ton
                "tone": ticket.tone_analysis.tone if ticket.tone_analysis else None,
                "urgency": ticket.tone_analysis.urgency if ticket.tone_analysis else None,
                "emotion_score": ticket.tone_analysis.emotion_score if ticket.tone_analysis else 0,

                # 🎯 NOUVEAU: Validation client
                "validation_status": getattr(ticket, 'validation_status', 'pending'),
                "validation_required": ticket.client_summary.validation_required if ticket.client_summary else False
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

        logger.info(f"✅ {len(tickets_list)} tickets récupérés")

        return {
            "success": True,
            "total_tickets": len(tickets_list),
            "tickets": tickets_list
        }

    except Exception as e:
        logger.error(f"❌ Erreur récupération tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/ticket/{ticket_id}/dossier")
async def generate_client_dossier(ticket_id: str):
    """
    📄 NOUVEAU: Génère le dossier client complet au format structuré

    Returns:
        Dossier client avec toutes les informations de la réclamation
    """

    try:
        logger.info(f"📄 Génération du dossier client pour: {ticket_id}")

        if ticket_id not in sav_workflow_engine.active_tickets:
            raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} non trouvé")

        ticket = sav_workflow_engine.active_tickets[ticket_id]

        # Générer le dossier client complet
        dossier = {
            # 🎫 INFORMATIONS TICKET
            "ticket": {
                "ticket_id": ticket.ticket_id,
                "created_at": ticket.created_at.isoformat(),
                "status": ticket.status,
                "priority": ticket.priority,
                "priority_score": ticket.priority_score
            },

            # 👤 INFORMATIONS CLIENT
            "client": {
                "customer_id": ticket.customer_id,
                "customer_name": getattr(ticket, 'customer_name', 'Client'),
                "customer_tier": getattr(ticket, 'customer_tier', 'standard'),
                "order_number": ticket.order_number
            },

            # 🛋️ INFORMATIONS PRODUIT
            "produit": {
                "product_sku": ticket.product_sku,
                "product_name": ticket.product_name,
                "product_value": getattr(ticket, 'product_value', 0),
                "purchase_date": ticket.warranty_check_result.warranty_start_date.isoformat() if ticket.warranty_check_result else None,
                "delivery_date": ticket.warranty_check_result.warranty_start_date.isoformat() if ticket.warranty_check_result else None
            },

            # ⚠️ PROBLÈME
            "probleme": {
                "description": ticket.problem_description,
                "category": ticket.problem_category,
                "subcategory": ticket.problem_subcategory,
                "severity": ticket.problem_severity,
                "confidence": ticket.problem_confidence
            },

            # 🎭 ANALYSE TON
            "analyse_ton": {
                "tone": ticket.tone_analysis.tone if ticket.tone_analysis else "calm",
                "urgency": ticket.tone_analysis.urgency if ticket.tone_analysis else "low",
                "emotion_score": ticket.tone_analysis.emotion_score if ticket.tone_analysis else 0,
                "urgency_score": ticket.tone_analysis.urgency_score if ticket.tone_analysis else 0,
                "detected_keywords": ticket.tone_analysis.detected_keywords if ticket.tone_analysis else [],
                "recommended_response_time": ticket.tone_analysis.recommended_response_time if ticket.tone_analysis else "48h",
                "requires_human_empathy": ticket.tone_analysis.requires_human_empathy if ticket.tone_analysis else False,
                "explanation": ticket.tone_analysis.explanation if ticket.tone_analysis else ""
            },

            # 🛡️ GARANTIE
            "garantie": {
                "covered": ticket.warranty_check_result.is_covered if ticket.warranty_check_result else False,
                "component": ticket.warranty_check_result.component if ticket.warranty_check_result else None,
                "warranty_type": ticket.warranty_check_result.warranty_type if ticket.warranty_check_result else None,
                "expiry_date": ticket.warranty_check_result.warranty_expiry_date.isoformat() if ticket.warranty_check_result else None,
                "reason": ticket.warranty_check_result.reason if ticket.warranty_check_result else None
            },

            # 📸 PREUVES
            "preuves": [
                {
                    "evidence_id": evidence.evidence_id,
                    "type": evidence.type,
                    "url": evidence.file_url,
                    "description": evidence.description,
                    "uploaded_at": evidence.uploaded_at.isoformat()
                }
                for evidence in ticket.evidences
            ],

            # ⏰ SLA
            "sla": {
                "response_deadline": ticket.sla_response_deadline.isoformat() if ticket.sla_response_deadline else None,
                "intervention_deadline": ticket.sla_intervention_deadline.isoformat() if ticket.sla_intervention_deadline else None
            },

            # ✅ RÉSOLUTION
            "resolution": {
                "auto_resolved": ticket.auto_resolved,
                "resolution_type": ticket.resolution_type,
                "resolution_description": ticket.resolution_description
            },

            # 📧 RÉCAPITULATIF CLIENT
            "recapitulatif": {
                "summary_id": ticket.client_summary.summary_id if ticket.client_summary else None,
                "validation_required": ticket.client_summary.validation_required if ticket.client_summary else False,
                "validation_link": ticket.client_summary.validation_link if ticket.client_summary else None,
                "validation_status": getattr(ticket, 'validation_status', 'pending'),
                "email_body": ticket.client_summary.email_body if ticket.client_summary else None,
                "sms_body": ticket.client_summary.sms_body if ticket.client_summary else None
            },

            # 📜 HISTORIQUE
            "historique": [
                {
                    "action_id": action.action_id,
                    "timestamp": action.timestamp.isoformat(),
                    "actor": action.actor,
                    "action_type": action.action_type,
                    "description": action.description
                }
                for action in ticket.actions
            ]
        }

        logger.info(f"✅ Dossier généré: {ticket_id}")

        return {
            "success": True,
            "dossier": dossier
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur génération dossier: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


# ============ FONCTIONS UTILITAIRES ============

def _generate_next_steps(ticket: SAVTicket) -> List[str]:
    """Génère les prochaines étapes selon l'état du ticket"""

    next_steps = []

    if ticket.auto_resolved:
        next_steps.append("✅ Votre demande a été traitée automatiquement")
        next_steps.append(f"📋 Solution: {ticket.resolution_description}")

        if ticket.resolution_type == "auto_replacement":
            next_steps.append("📦 Une pièce de remplacement sera expédiée sous 48h")
            next_steps.append("📧 Vous recevrez un email de confirmation avec le numéro de suivi")
        elif ticket.resolution_type == "technician_dispatch":
            next_steps.append("👷 Un technicien vous contactera pour planifier l'intervention")
            next_steps.append(f"⏰ Délai maximal: {ticket.sla_intervention_deadline.strftime('%d/%m/%Y')}")

    elif ticket.status == "escalated_to_human":
        next_steps.append("⚠️ Votre demande nécessite une analyse approfondie")
        next_steps.append("👤 Un conseiller SAV vous contactera rapidement")
        next_steps.append(f"📞 Contact prévu avant: {ticket.sla_response_deadline.strftime('%d/%m/%Y à %H:%M')}")

    elif ticket.status == "evidence_collection":
        next_steps.append("📸 Veuillez fournir les preuves requises")
        next_steps.append("⬆️ Uploadez vos photos/vidéos via le bouton ci-dessous")
        next_steps.append("✅ Une fois les preuves reçues, votre demande sera traitée")

    elif ticket.status == "awaiting_technician":
        next_steps.append("👷 Un technicien sera assigné à votre demande")
        next_steps.append(f"⏰ Intervention prévue avant: {ticket.sla_intervention_deadline.strftime('%d/%m/%Y')}")

    # Toujours inclure le numéro de ticket
    next_steps.append(f"🎫 Conservez votre numéro de ticket: {ticket.ticket_id}")

    return next_steps
