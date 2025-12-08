# backend/app/api/endpoints/tickets.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Mock tickets storage (in production, use database)
mock_tickets = []

class TicketCreate(BaseModel):
    order_number: str
    problem_description: str
    priority: str
    photos: Optional[List[str]] = []

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_ticket(ticket: TicketCreate):
    """Create a new SAV ticket"""
    try:
        new_ticket = {
            "ticket_id": f"SAV-MDF-{len(mock_tickets)+1:05d}",
            "order_number": ticket.order_number,
            "problem_description": ticket.problem_description,
            "priority": ticket.priority,
            "photos": ticket.photos,
            "status": "nouveau",
            "created_at": "2025-12-03"
        }

        mock_tickets.append(new_ticket)
        logger.info(f"Ticket created: {new_ticket['ticket_id']}")

        return {
            "success": True,
            "ticket": new_ticket
        }
    except Exception as e:
        logger.error(f"Create ticket error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )

@router.get("/", status_code=status.HTTP_200_OK)
async def list_tickets(limit: int = 10):
    """Get list of tickets"""
    return {
        "success": True,
        "tickets": mock_tickets[:limit],
        "total": len(mock_tickets)
    }

@router.get("/{ticket_id}", status_code=status.HTTP_200_OK)
async def get_ticket(ticket_id: str):
    """Get ticket details"""
    ticket = next((t for t in mock_tickets if t.get('ticket_id') == ticket_id), None)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} non trouvé"
        )

    return {
        "success": True,
        "ticket": ticket
    }
