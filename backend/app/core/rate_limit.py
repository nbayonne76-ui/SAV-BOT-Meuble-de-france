# backend/app/core/rate_limit.py
"""
Rate limiting configuration using slowapi
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, Response
from typing import Callable
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting.
    Uses user ID if authenticated, otherwise IP address.
    """
    # Try to get user from request state (set by auth middleware)
    user = getattr(request.state, "user", None)
    if user:
        return f"user:{user.id}"

    # Fall back to IP address
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_identifier,
    default_limits=["100/minute"],  # Default rate limit
    storage_uri=settings.REDIS_URL if not settings.DEBUG else "memory://",
    strategy="fixed-window"
)


# Rate limit presets for different endpoint types
class RateLimits:
    """Predefined rate limits for different endpoint types"""

    # Authentication endpoints (strict)
    AUTH_LOGIN = "5/minute"
    AUTH_REGISTER = "3/minute"
    AUTH_PASSWORD_RESET = "3/minute"

    # Chat endpoints (moderate)
    CHAT_MESSAGE = "30/minute"
    CHAT_SESSION = "60/minute"

    # Upload endpoints (strict due to resource usage)
    UPLOAD_FILE = "10/minute"
    UPLOAD_BULK = "3/minute"

    # API endpoints (standard)
    API_READ = "100/minute"
    API_WRITE = "30/minute"

    # Admin endpoints (relaxed for admins)
    ADMIN_READ = "200/minute"
    ADMIN_WRITE = "60/minute"

    # Public endpoints (generous)
    PUBLIC_READ = "200/minute"


def setup_rate_limiter(app):
    """
    Configure rate limiter for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    logger.info("Rate limiter configured")


def rate_limit_key_user(request: Request) -> str:
    """Key function that uses authenticated user ID"""
    return get_identifier(request)


def rate_limit_key_ip(request: Request) -> str:
    """Key function that always uses IP address"""
    return get_remote_address(request)


# Custom rate limit exceeded handler with more info
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.
    Provides more helpful error messages.
    """
    from fastapi.responses import JSONResponse

    logger.warning(f"Rate limit exceeded: {get_identifier(request)} - {exc.detail}")

    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": "rate_limit_exceeded",
            "detail": "Too many requests. Please slow down.",
            "retry_after": exc.detail.split("per")[0].strip() if exc.detail else "60 seconds"
        },
        headers={
            "Retry-After": "60",
            "X-RateLimit-Limit": str(exc.detail) if exc.detail else "unknown"
        }
    )
