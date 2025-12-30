# backend/app/api/endpoints/chat.py
"""
Chat endpoint with rate limiting and input validation
"""
from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import logging
import os
import re
import html
from pathlib import Path
from dotenv import load_dotenv

from app.services.chatbot import MeubledeFranceChatbot
from app.core.config import settings
from app.core.rate_limit import limiter, RateLimits
from app.api.deps import get_current_user, OptionalAuth
from app.models.user import UserDB
from app.services.sav_workflow_engine import sav_workflow_engine
from app.services.warranty_service import warranty_service
from app.models.warranty import WarrantyType
from app.services.session_manager import get_session_manager
from datetime import datetime, timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# Dependency: Get OpenAI API key from settings
def get_openai_api_key() -> str:
    """Get OpenAI API key from configuration"""
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not configured"
        )
    return settings.OPENAI_API_KEY


class ChatRequest(BaseModel):
    """Chat request with validation"""
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = Field("default", max_length=100)
    order_number: Optional[str] = Field(None, max_length=50)
    photos: Optional[List[str]] = Field(default_factory=list)

    @validator('message')
    def sanitize_message(cls, v):
        """Sanitize message input"""
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        # Remove null bytes
        v = v.replace('\x00', '')
        # Limit consecutive newlines
        v = re.sub(r'\n{3,}', '\n\n', v)
        return v.strip()

    @validator('session_id')
    def validate_session_id(cls, v):
        """Validate session ID format"""
        if v:
            # Only allow alphanumeric, hyphens, underscores
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError('Invalid session ID format')
        return v

    @validator('order_number')
    def validate_order_number(cls, v):
        """Validate order number format if provided"""
        if v:
            # Clean and validate format CMD-XXXX-XXXXX
            v = v.strip().upper()
            if not re.match(r'^CMD-\d{4}-\d{5}$', v):
                # Try to clean up common variations
                cleaned = re.sub(r'[^A-Z0-9-]', '', v)
                if not re.match(r'^CMD-?\d{4}-?\d{5}$', cleaned):
                    raise ValueError('Invalid order number format. Expected: CMD-XXXX-XXXXX')
        return v

    @validator('photos')
    def validate_photos(cls, v):
        """Validate photo paths"""
        if v and len(v) > 10:
            raise ValueError('Maximum 10 photos allowed')
        return v


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    language: str
    conversation_type: str
    session_id: str
    sav_ticket: Optional[dict] = None
    ticket_data: Optional[dict] = None
    should_close_session: bool = False
    should_ask_continue: bool = False


def extract_order_number(message: str) -> Optional[str]:
    """
    Extract order number from message automatically.
    Supports formats: CMD-XXXX-XXXXX, CMD-XXXXXXXXXX, etc.
    """
    patterns = [
        r'CMD-\d{4}-\d{5}',
        r'CMD-\d{10}',
        r'commande[:\s]+CMD-\d{4}-\d{5}',
        r'commande[:\s]+CMD-\d{10}',
        r'n[°o\s]+commande[:\s]+CMD-\d{4}-\d{5}',
        r'CMD\d{4}\d{5}',
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            order_num = match.group(0)
            if 'commande' in order_num.lower():
                order_num = re.search(r'CMD-?\d+', order_num, re.IGNORECASE).group(0)
            if '-' not in order_num:
                if len(order_num) == 13:
                    order_num = f"CMD-{order_num[3:7]}-{order_num[7:]}"
            logger.info(f"Order number detected: {order_num}")
            return order_num

    return None


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
@limiter.limit(RateLimits.CHAT_MESSAGE)
async def chat(
    request: Request,
    chat_request: ChatRequest,
    current_user: Optional[UserDB] = Depends(OptionalAuth()),
    api_key: str = Depends(get_openai_api_key)
):
    """
    Send a message to the chatbot.

    Rate limited to 30 requests per minute.
    Authentication is optional but provides better session management.
    Uses dependency injection for OpenAI API key.
    """
    try:
        # Use user ID for session if authenticated
        session_id = chat_request.session_id
        if current_user:
            session_id = f"user-{current_user.id}-{chat_request.session_id}"

        logger.info(f"Chat request (session: {session_id}, authenticated: {current_user is not None})")

        # Get or create session using session manager
        session_manager = get_session_manager()
        session = await session_manager.get_or_create_session(
            session_id=session_id,
            user_id=current_user.id if current_user else None
        )

        # Create chatbot instance with API key from dependency
        # Note: chatbot is stateless, state is managed by session_manager
        chatbot = MeubledeFranceChatbot(
            api_key=api_key,
            timeout=30
        )

        # Restore chatbot state from session
        chatbot.conversation_history = session.conversation_history or []
        if hasattr(session, 'sav_context'):
            chatbot.conversation_type = session.conversation_type or "general"

        # Auto-detect order number
        order_number = chat_request.order_number
        if not order_number:
            order_number = extract_order_number(chat_request.message)
            if order_number:
                logger.info(f"Auto-detected order: {order_number}")

        # Process message
        result = await chatbot.chat(
            user_message=chat_request.message,
            order_number=order_number,
            photos=chat_request.photos
        )

        # Save chatbot state back to session
        await session_manager.update_session(
            session_id=session_id,
            conversation_history=chatbot.conversation_history,
            conversation_type=chatbot.conversation_type,
            message_count=len(chatbot.conversation_history)
        )

        if "error" in result:
            logger.error(f"Chatbot error: {result['error']}")
            return ChatResponse(
                response=result["response"],
                language=result.get("language", "fr"),
                conversation_type=result.get("conversation_type", "general"),
                session_id=session_id
            )

        # Include ticket data if available
        logger.info(f"Chat result includes sav_ticket: {result.get('sav_ticket') is not None}")
        logger.info(f"Chat result includes ticket_data: {result.get('ticket_data') is not None}")

        return ChatResponse(
            response=result["response"],
            language=result.get("language", "fr"),
            conversation_type=result.get("conversation_type", "general"),
            session_id=session_id,
            sav_ticket=result.get("sav_ticket"),
            ticket_data=result.get("ticket_data"),
            should_close_session=result.get("should_close_session", False),
            should_ask_continue=result.get("should_ask_continue", False)
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        logger.error(f"Chat endpoint error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}" if settings.DEBUG else "An error occurred"
        )


@router.delete("/{session_id}", status_code=status.HTTP_200_OK)
@limiter.limit(RateLimits.API_WRITE)
async def clear_session(
    request: Request,
    session_id: str,
    current_user: Optional[UserDB] = Depends(OptionalAuth())
):
    """
    Clear a chat session.

    If authenticated, only clears sessions belonging to the user.
    """
    # Validate session_id
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )

    # If authenticated, prefix with user ID
    if current_user:
        full_session_id = f"user-{current_user.id}-{session_id}"
    else:
        full_session_id = session_id

    # Delete session using session manager
    session_manager = get_session_manager()
    deleted = await session_manager.delete_session(full_session_id)

    if deleted:
        logger.info(f"Session cleared: {full_session_id}")
        return {"success": True, "message": "Session cleared"}

    return {"success": False, "message": "Session not found"}


@router.get("/sessions/count", status_code=status.HTTP_200_OK)
@limiter.limit(RateLimits.API_READ)
async def get_session_count(request: Request):
    """
    Get the current number of active sessions.
    Useful for monitoring. Now uses Redis-backed session storage.
    """
    session_manager = get_session_manager()
    count = await session_manager.get_session_count()

    return {
        "active_sessions": count,
        "storage_backend": "redis" if "redis" in settings.REDIS_URL else "memory"
    }


class CreateTicketRequest(BaseModel):
    """Request model for creating a ticket from text chat"""
    customer_name: str
    problem_description: str
    product: str
    order_number: Optional[str] = None
    conversation_transcript: Optional[str] = None
    session_id: Optional[str] = None


@router.post("/create-ticket")
@limiter.limit(RateLimits.API_WRITE)
async def create_ticket_from_chat(
    request: Request,
    ticket_request: CreateTicketRequest,
    current_user: Optional[UserDB] = Depends(OptionalAuth())
):
    """
    Crée un ticket SAV depuis une conversation textuelle

    Utilise l'API SAV existante pour créer le ticket.
    """
    try:
        logger.info(f"🎫 Création de ticket SAV (chat) pour {ticket_request.customer_name}")

        # Utiliser le nom du client comme customer_id si pas d'ID disponible
        customer_id = ticket_request.customer_name.replace(" ", "_").lower()

        # Générer un SKU générique pour les produits du chat textuel
        product_sku = f"CHAT-PRODUCT-{ticket_request.order_number or 'UNKNOWN'}"

        # Dates par défaut (achat il y a 30 jours, livraison il y a 15 jours)
        purchase_date = datetime.now() - timedelta(days=30)
        delivery_date = datetime.now() - timedelta(days=15)

        # Créer une garantie pour le produit
        warranty = await warranty_service.create_warranty(
            order_number=ticket_request.order_number or f"CHAT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            product_sku=product_sku,
            product_name=ticket_request.product,
            customer_id=customer_id,
            purchase_date=purchase_date,
            delivery_date=delivery_date,
            warranty_type=WarrantyType.STANDARD
        )

        # Créer le ticket via le workflow SAV
        ticket = await sav_workflow_engine.process_new_claim(
            customer_id=customer_id,
            order_number=ticket_request.order_number or f"CHAT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            product_sku=product_sku,
            product_name=ticket_request.product,
            problem_description=ticket_request.problem_description,
            warranty=warranty,
            customer_tier="standard",
            product_value=0.0
        )

        # Ajouter le nom du client et la transcription au ticket
        ticket.customer_name = ticket_request.customer_name
        if ticket_request.conversation_transcript:
            # Ajouter une note avec la transcription
            if not hasattr(ticket, 'notes'):
                ticket.notes = []
            ticket.notes.append(f"Transcription de la conversation textuelle:\n{ticket_request.conversation_transcript}")

        logger.info(f"✅ Ticket SAV créé (chat): {ticket.ticket_id}")

        return {
            "success": True,
            "ticket_id": ticket.ticket_id,
            "message": "Ticket SAV créé avec succès",
            "data": {
                "customer_name": ticket_request.customer_name,
                "problem_description": ticket_request.problem_description,
                "product_name": ticket_request.product,
                "order_number": ticket_request.order_number,
                "priority": ticket.priority,
                "status": ticket.status,
                "source": "text_chat"
            }
        }

    except Exception as e:
        logger.error(f"❌ Erreur création ticket (chat): {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de création du ticket: {str(e)}")
