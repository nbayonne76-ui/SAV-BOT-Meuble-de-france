# backend/app/api/endpoints/chat.py
# Fixed: Load API key directly from .env to avoid caching issues

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import logging
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from app.services.chatbot import MeubledeFranceChatbot
from app.core.config import settings

# Force reload .env to get fresh API key
backend_dir = Path(__file__).parent.parent.parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path, override=True)

logger = logging.getLogger(__name__)
router = APIRouter()

# Global chatbot instance (in production, use proper session management)
chatbot_instances = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    order_number: Optional[str] = None
    photos: Optional[List[str]] = []

class ChatResponse(BaseModel):
    response: str
    language: str
    conversation_type: str
    session_id: str

def extract_order_number(message: str) -> Optional[str]:
    """
    Extrait automatiquement le numéro de commande du message
    Formats supportés: CMD-XXXX-XXXXX, CMD-XXXXXXXXXX, etc.
    """
    # Pattern pour détecter CMD-XXXX-XXXXX ou CMD-XXXXXXXXXX
    patterns = [
        r'CMD-\d{4}-\d{5}',  # CMD-2024-12345
        r'CMD-\d{10}',        # CMD-2024123456
        r'commande[:\s]+CMD-\d{4}-\d{5}',  # commande: CMD-2024-12345
        r'commande[:\s]+CMD-\d{10}',
        r'n[°o\s]+commande[:\s]+CMD-\d{4}-\d{5}',
        r'CMD\d{4}\d{5}',     # CMD202412345 (sans tirets)
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            order_num = match.group(0)
            # Nettoyer le préfixe si présent
            if 'commande' in order_num.lower():
                order_num = re.search(r'CMD-?\d+', order_num, re.IGNORECASE).group(0)
            # Normaliser le format avec tirets
            if not '-' in order_num:
                # CMD202412345 -> CMD-2024-12345
                if len(order_num) == 13:  # CMD + 10 chiffres
                    order_num = f"CMD-{order_num[3:7]}-{order_num[7:]}"
            logger.info(f"✅ Numéro de commande détecté: {order_num}")
            return order_num

    logger.info("ℹ️  Aucun numéro de commande détecté dans le message")
    return None

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest):
    """
    Send a message to the chatbot
    """
    try:
        logger.info(f"Chat request received (session: {request.session_id})")

        # Get API key directly from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        # 🎯 CORRECTION: Utiliser une instance par session au lieu de créer un nouveau chatbot à chaque message
        if request.session_id not in chatbot_instances:
            logger.info(f"Creating NEW chatbot for session: {request.session_id}")
            chatbot_instances[request.session_id] = MeubledeFranceChatbot(api_key=api_key)
        else:
            logger.info(f"Using EXISTING chatbot for session: {request.session_id}")

        chatbot = chatbot_instances[request.session_id]

        # 🎯 NOUVEAU: Détecter automatiquement le numéro de commande si non fourni
        order_number = request.order_number
        if not order_number:
            order_number = extract_order_number(request.message)
            if order_number:
                logger.info(f"📋 Commande détectée: {order_number}")

        # Process message
        result = await chatbot.chat(
            user_message=request.message,
            order_number=order_number,
            photos=request.photos
        )

        if "error" in result:
            logger.error(f"Chatbot error: {result['error']}")
            # Still return the error message to user
            return ChatResponse(
                response=result["response"],
                language=result.get("language", "fr"),
                conversation_type=result.get("conversation_type", "general"),
                session_id=request.session_id
            )

        return ChatResponse(
            response=result["response"],
            language=result.get("language", "fr"),
            conversation_type=result.get("conversation_type", "general"),
            session_id=request.session_id
        )

    except Exception as e:
        import traceback
        logger.error(f"Chat endpoint error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {str(e)}"
        )

@router.delete("/{session_id}", status_code=status.HTTP_200_OK)
async def clear_session(session_id: str):
    """
    Clear a chat session
    """
    if session_id in chatbot_instances:
        del chatbot_instances[session_id]
        logger.info(f"Session cleared: {session_id}")
        return {"success": True, "message": "Session cleared"}
    return {"success": False, "message": "Session not found"}
