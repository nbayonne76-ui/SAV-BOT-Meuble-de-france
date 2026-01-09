# backend/app/repositories/ticket_repository.py
"""
Repository for SAV Ticket CRUD operations with async database persistence
"""
import logging
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.ticket import TicketDB
from app.services.sav_workflow_engine import SAVTicket

logger = logging.getLogger(__name__)


class TicketRepository:
    """Repository for ticket database operations"""

    @staticmethod
    def _ticket_to_db(ticket: SAVTicket) -> Dict:
        """Convert SAVTicket dataclass to database dict"""
        return {
            "ticket_id": ticket.ticket_id,
            "customer_id": ticket.customer_id,
            "customer_name": getattr(ticket, 'customer_name', None),
            "order_number": ticket.order_number,
            "product_sku": ticket.product_sku,
            "product_name": ticket.product_name,
            "problem_description": ticket.problem_description,
            "problem_category": ticket.problem_category,
            "problem_severity": ticket.problem_severity,
            "problem_confidence": ticket.problem_confidence,
            "warranty_id": ticket.warranty_id,
            "warranty_status": ticket.warranty_check_result.reason if ticket.warranty_check_result else None,
            "priority": ticket.priority,
            "priority_score": ticket.priority_score,
            "priority_factors": ticket.priority_factors,
            "status": ticket.status.value if hasattr(ticket.status, 'value') else ticket.status,
            "auto_resolved": ticket.auto_resolved,
            "resolution_type": ticket.resolution_type.value if ticket.resolution_type and hasattr(ticket.resolution_type, 'value') else None,
            "resolution_description": ticket.resolution_description,
            "tone_category": ticket.tone_analysis.tone.value if ticket.tone_analysis and hasattr(ticket.tone_analysis.tone, 'value') else (str(ticket.tone_analysis.tone) if ticket.tone_analysis else None),
            "tone_score": ticket.tone_analysis.emotion_score if ticket.tone_analysis else None,
            "tone_keywords": ticket.tone_analysis.detected_keywords if ticket.tone_analysis else [],
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
            "sla_response_deadline": ticket.sla_response_deadline,
            "sla_intervention_deadline": ticket.sla_intervention_deadline,
            "resolved_at": getattr(ticket, 'resolved_at', None),
            "evidence": [
                {
                    "evidence_id": e.evidence_id,
                    "type": e.type,
                    "url": e.url,
                    "description": e.description,
                    "uploaded_at": e.uploaded_at.isoformat() if e.uploaded_at else None,
                    "verified": e.verified,
                    "quality_score": e.quality_score
                }
                for e in (getattr(ticket, 'evidence', None) or getattr(ticket, 'evidences', []))
            ],
            "attachments": getattr(ticket, 'attachments', []),
            "actions": [
                {
                    "action_id": a.action_id,
                    "timestamp": a.timestamp.isoformat() if a.timestamp else None,
                    "actor": a.actor,
                    "action_type": a.action_type,
                    "description": a.description,
                    "metadata": a.metadata
                }
                for a in ticket.actions
            ],
            "notes": getattr(ticket, 'notes', []),
            "client_summary": {
                "summary_id": getattr(ticket.client_summary, 'summary_id', None),
                "problem_summary": getattr(ticket.client_summary, 'problem_summary', None),
                "warranty_status": getattr(ticket.client_summary, 'warranty_status', None),
                "priority": getattr(ticket.client_summary, 'priority', None),
                "next_steps": getattr(ticket.client_summary, 'next_steps', None),
                "response_deadline": getattr(ticket.client_summary, 'response_deadline', None),
                "validation_required": getattr(ticket.client_summary, 'validation_required', False),
                "email_body": getattr(ticket.client_summary, 'email_body', ''),
                "sms_body": getattr(ticket.client_summary, 'sms_body', '')
            } if ticket.client_summary else None,
            "source": getattr(ticket, 'source', 'chat')
        }

    @staticmethod
    async def create(db: AsyncSession, ticket: SAVTicket) -> TicketDB:
        """Create a new ticket in database"""
        try:
            ticket_data = TicketRepository._ticket_to_db(ticket)
            db_ticket = TicketDB(**ticket_data)
            db.add(db_ticket)
            await db.commit()
            await db.refresh(db_ticket)
            logger.info(f"Ticket {ticket.ticket_id} saved to database")
            return db_ticket
        except Exception as e:
            logger.error(f"Error saving ticket {ticket.ticket_id}: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def get_by_id(db: AsyncSession, ticket_id: str) -> Optional[TicketDB]:
        """Get ticket by ID"""
        result = await db.execute(select(TicketDB).where(TicketDB.ticket_id == ticket_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, limit: int = 100, offset: int = 0) -> List[TicketDB]:
        """Get all tickets with pagination"""
        result = await db.execute(
            select(TicketDB)
            .order_by(desc(TicketDB.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_customer(db: AsyncSession, customer_id: str) -> List[TicketDB]:
        """Get tickets for a specific customer"""
        result = await db.execute(
            select(TicketDB)
            .where(TicketDB.customer_id == customer_id)
            .order_by(desc(TicketDB.created_at))
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_status(db: AsyncSession, status: str) -> List[TicketDB]:
        """Get tickets by status"""
        result = await db.execute(
            select(TicketDB)
            .where(TicketDB.status == status)
            .order_by(desc(TicketDB.created_at))
        )
        return list(result.scalars().all())

    @staticmethod
    async def update(db: AsyncSession, ticket: SAVTicket) -> TicketDB:
        """Update existing ticket"""
        try:
            result = await db.execute(select(TicketDB).where(TicketDB.ticket_id == ticket.ticket_id))
            db_ticket = result.scalar_one_or_none()
            if not db_ticket:
                logger.warning(f"Ticket {ticket.ticket_id} not found, creating new")
                return await TicketRepository.create(db, ticket)

            ticket_data = TicketRepository._ticket_to_db(ticket)
            for key, value in ticket_data.items():
                setattr(db_ticket, key, value)

            db_ticket.updated_at = datetime.now()
            await db.commit()
            await db.refresh(db_ticket)
            logger.info(f"Ticket {ticket.ticket_id} updated in database")
            return db_ticket
        except Exception as e:
            logger.error(f"Error updating ticket {ticket.ticket_id}: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def delete(db: AsyncSession, ticket_id: str) -> bool:
        """Delete ticket"""
        try:
            result = await db.execute(select(TicketDB).where(TicketDB.ticket_id == ticket_id))
            db_ticket = result.scalar_one_or_none()
            if db_ticket:
                await db.delete(db_ticket)
                await db.commit()
                logger.info(f"Ticket {ticket_id} deleted from database")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting ticket {ticket_id}: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def count(db: AsyncSession) -> int:
        """Count total tickets"""
        result = await db.execute(select(TicketDB))
        return len(result.scalars().all())


# Singleton instance
ticket_repository = TicketRepository()
