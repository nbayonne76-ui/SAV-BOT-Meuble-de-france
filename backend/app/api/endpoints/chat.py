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
from app.services.chatbot import MeubledeFranceChatbot
from app.core.config import settings
from app.core.rate_limit import limiter, RateLimits
from app.api.deps import get_current_user, OptionalAuth
from app.models.user import UserDB
from app.db.session import get_db
from sqlalchemy.orm import Session

# .env is loaded centrally in `app.core.config`; avoid reloading it here

logger = logging.getLogger(__name__)
router = APIRouter()

# Global chatbot instance (in production, use Redis-based session management)
chatbot_instances = {}


class ChatRequest(BaseModel):
    """Chat request with validation"""
    message: str = Field("", max_length=4000)  # Allow empty message if photos present
    session_id: Optional[str] = Field("default", max_length=100)
    order_number: Optional[str] = Field(None, max_length=50)
    photos: Optional[List[str]] = Field(default_factory=list)

    @validator('message')
    def sanitize_message(cls, v):
        """Sanitize message input"""
        # Allow empty message if user is sending photos only
        if not v or not v.strip():
            return ""  # Return empty string for photo-only messages
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
    session_id: str | None
    requires_validation: Optional[bool] = False
    ticket_id: Optional[str] = None
    should_close_session: Optional[bool] = False


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


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
@limiter.limit(RateLimits.CHAT_MESSAGE)
async def chat(
    request: Request,
    chat_request: ChatRequest,
    current_user: Optional[UserDB] = Depends(OptionalAuth()),
    db: Session = Depends(get_db)
):
    """
    Send a message to the chatbot.

    Rate limited to 30 requests per minute.
    Authentication is optional but provides better session management.
    """
    try:
        # Use user ID for session if authenticated
        session_id = chat_request.session_id
        if current_user:
            session_id = f"user-{current_user.id}-{chat_request.session_id}"

        logger.info(f"Chat request (session: {session_id}, authenticated: {current_user is not None})")

        # Get API key from settings (loaded at startup)
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in configuration")

        # Get or create chatbot instance
        if session_id not in chatbot_instances:
            logger.info(f"Creating new chatbot for session: {session_id}")
            chatbot_instances[session_id] = MeubledeFranceChatbot(api_key=api_key)
        else:
            logger.info(f"Using existing chatbot for session: {session_id}")

        chatbot = chatbot_instances[session_id]

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
            photos=chat_request.photos,
            db_session=db
        )

        if "error" in result:
            logger.error(f"Chatbot error: {result['error']}")
            return ChatResponse(
                response=result["response"],
                language=result.get("language", "fr"),
                conversation_type=result.get("conversation_type", "general"),
                session_id=session_id
            )

        # Extract validation info from ticket_data
        ticket_data = result.get("ticket_data", {})
        requires_validation = ticket_data.get("requires_validation", False) if ticket_data else False
        ticket_id = ticket_data.get("ticket_id") if ticket_data else None

        return ChatResponse(
            response=result["response"],
            language=result.get("language", "fr"),
            conversation_type=result.get("conversation_type", "general"),
            session_id=session_id,
            requires_validation=requires_validation,
            ticket_id=ticket_id,
            should_close_session=result.get("should_close_session", False)
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

    if full_session_id in chatbot_instances:
        del chatbot_instances[full_session_id]
        logger.info(f"Session cleared: {full_session_id}")
        return {"success": True, "message": "Session cleared"}

    return {"success": False, "message": "Session not found"}


@router.post("/validate/{ticket_id}", status_code=status.HTTP_200_OK)
@limiter.limit(RateLimits.API_WRITE)
async def validate_ticket(
    request: Request,
    ticket_id: str,
    current_user: Optional[UserDB] = Depends(OptionalAuth()),
    db: Session = Depends(get_db)
):
    """
    Validate a ticket and persist it to the database.
    This is called when the user clicks "Valider" on the recap.
    """
    try:
        # Import here to avoid circular imports
        from app.services.sav_workflow_engine import sav_workflow_engine

        # Validate ticket ID format
        if not re.match(r'^SAV-\d{8}-\d+$', ticket_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ticket ID format"
            )

        # Set database session for persistence
        sav_workflow_engine.db_session = db

        # Validate the ticket
        result = sav_workflow_engine.validate_ticket(ticket_id)

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Ticket not found")
            )

        logger.info(f"✅ Ticket {ticket_id} validé avec succès")

        return {
            "success": True,
            "message": "Ticket validé et créé dans le système",
            "ticket_id": result.get("ticket_id"),
            "response": "✅ Parfait ! Votre demande a été enregistrée.\n\nVotre ticket a été créé avec succès. Notre équipe va traiter votre demande dans les meilleurs délais.\n\nVous recevrez une confirmation par email avec le numéro de suivi.\n\nY a-t-il autre chose pour laquelle je peux vous aider ?"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur validation ticket: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}" if settings.DEBUG else "An error occurred"
        )


@router.post("/cancel/{ticket_id}", status_code=status.HTTP_200_OK)
@limiter.limit(RateLimits.API_WRITE)
async def cancel_ticket(
    request: Request,
    ticket_id: str,
    current_user: Optional[UserDB] = Depends(OptionalAuth())
):
    """
    Cancel a ticket that is pending validation.
    This is called when the user clicks "Modifier" on the recap.
    """
    try:
        # Import here to avoid circular imports
        from app.services.sav_workflow_engine import sav_workflow_engine

        # Validate ticket ID format
        if not re.match(r'^SAV-\d{8}-\d+$', ticket_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ticket ID format"
            )

        # Cancel the ticket
        result = sav_workflow_engine.cancel_ticket(ticket_id)

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Ticket not found")
            )

        logger.info(f"❌ Ticket {ticket_id} annulé par l'utilisateur")

        return {
            "success": True,
            "message": "Ticket annulé",
            "response": "D'accord, je recommence. Pouvez-vous me redonner les informations corrigées ?"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur annulation ticket: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}" if settings.DEBUG else "An error occurred"
        )


@router.get("/sessions/count", status_code=status.HTTP_200_OK)
@limiter.limit(RateLimits.API_READ)
async def get_session_count(request: Request):
    """
    Get the current number of active sessions.
    Useful for monitoring.
    """
    return {
        "active_sessions": len(chatbot_instances),
        "session_ids": list(chatbot_instances.keys())[:10] if settings.DEBUG else []
    }
