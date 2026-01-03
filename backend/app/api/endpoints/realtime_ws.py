# backend/app/api/endpoints/realtime_ws.py
"""
WebSocket Proxy pour OpenAI Realtime API
Fait le relais entre le frontend et OpenAI Realtime API
"""
import asyncio
import os
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import websockets
import json

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def realtime_websocket_proxy(websocket: WebSocket):
    """
    Proxy WebSocket entre le frontend et OpenAI Realtime API

    Le navigateur ne peut pas envoyer de headers personnalisés avec WebSocket,
    donc ce proxy backend fait le relais avec les bons headers d'authentification.

    Flux:
    Frontend (WebSocket) <-> Backend Proxy (ce endpoint) <-> OpenAI Realtime API (WebSocket)
    """
    # Accepter la connexion du frontend
    await websocket.accept()
    logger.info("✅ Frontend connecté au proxy WebSocket")

    # Obtenir la clé API
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        await websocket.send_json({
            "type": "error",
            "error": {"message": "Clé API OpenAI non configurée"}
        })
        await websocket.close()
        return

    openai_ws = None

    try:
        # Se connecter à OpenAI Realtime API
        realtime_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "OpenAI-Beta": "realtime=v1"
        }

        logger.info("🔌 Connexion à OpenAI Realtime API...")
        openai_ws = await websockets.connect(
            realtime_url,
            additional_headers=headers
        )
        logger.info("✅ Connecté à OpenAI Realtime API")

        # Créer deux tâches asynchrones pour le relais bidirectionnel
        async def frontend_to_openai():
            """Relayer messages du frontend vers OpenAI"""
            try:
                while True:
                    # Recevoir message du frontend
                    data = await websocket.receive_text()
                    logger.debug(f"📤 Frontend → OpenAI: {data[:100]}...")

                    # Envoyer à OpenAI
                    await openai_ws.send(data)
            except WebSocketDisconnect:
                logger.info("Frontend déconnecté")
            except Exception as e:
                logger.error(f"Erreur frontend→OpenAI: {e}")

        async def openai_to_frontend():
            """Relayer messages d'OpenAI vers le frontend"""
            try:
                async for message in openai_ws:
                    logger.debug(f"📥 OpenAI → Frontend: {message[:100]}...")

                    # Envoyer au frontend
                    await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Erreur OpenAI→frontend: {e}")

        # Lancer les deux tâches en parallèle
        await asyncio.gather(
            frontend_to_openai(),
            openai_to_frontend()
        )

    except websockets.exceptions.WebSocketException as e:
        logger.error(f"❌ Erreur WebSocket OpenAI: {e}")
        await websocket.send_json({
            "type": "error",
            "error": {"message": f"Erreur connexion OpenAI: {str(e)}"}
        })
    except Exception as e:
        logger.error(f"❌ Erreur inattendue: {e}")
        await websocket.send_json({
            "type": "error",
            "error": {"message": f"Erreur serveur: {str(e)}"}
        })
    finally:
        # Fermer les connexions
        if openai_ws:
            await openai_ws.close()
            logger.info("🔌 Connexion OpenAI fermée")

        await websocket.close()
        logger.info("🔌 Connexion frontend fermée")
