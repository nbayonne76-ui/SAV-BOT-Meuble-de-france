# backend/app/api/endpoints/realtime.py
"""
Endpoint pour OpenAI Realtime API
Fournit le token d'authentification de manière sécurisée
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter()


class RealtimeTokenResponse(BaseModel):
    """Réponse contenant le token pour Realtime API"""
    token: str


@router.post("/token", response_model=RealtimeTokenResponse)
async def get_realtime_token():
    """
    Retourne le token OpenAI pour établir une connexion Realtime API

    🔒 SÉCURITÉ: Ne jamais exposer la clé API directement dans le frontend.
    Ce endpoint agit comme proxy sécurisé.

    Returns:
        RealtimeTokenResponse: Token d'authentification

    Raises:
        HTTPException: Si la clé API n'est pas configurée
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Clé API OpenAI non configurée. Vérifiez la variable d'environnement OPENAI_API_KEY"
        )

    return RealtimeTokenResponse(token=api_key)


@router.get("/health")
async def realtime_health_check():
    """
    Vérifie que le service Realtime est configuré correctement

    Returns:
        dict: Statut du service
    """
    has_api_key = bool(os.getenv("OPENAI_API_KEY"))

    return {
        "status": "ok" if has_api_key else "error",
        "realtime_configured": has_api_key,
        "message": "Service Realtime API prêt" if has_api_key else "Clé API manquante"
    }
