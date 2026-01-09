# backend/app/core/request_limits.py
"""
Request size and timeout middleware for DoS prevention.
"""
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp
import asyncio
from typing import Callable

from app.core.config import settings

logger = logging.getLogger(__name__)


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce maximum request body size.
    Prevents DoS attacks from large payload submissions.
    """

    def __init__(self, app: ASGIApp, max_size: int):
        super().__init__(app)
        self.max_size = max_size
        self.max_size_mb = round(max_size / 1024 / 1024, 2)

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Check request body size before processing.
        """
        # Skip for file uploads (handled separately by upload endpoint)
        if request.url.path.startswith("/api/upload"):
            return await call_next(request)

        # Check Content-Length header
        content_length = request.headers.get("content-length")
        if content_length:
            content_length = int(content_length)
            if content_length > self.max_size:
                logger.warning(
                    f"Request rejected: body size {content_length} bytes "
                    f"exceeds limit of {self.max_size} bytes ({self.max_size_mb}MB) "
                    f"from {request.client.host} to {request.url.path}"
                )
                return JSONResponse(
                    status_code=413,
                    content={
                        "success": False,
                        "error": "payload_too_large",
                        "detail": f"Request body exceeds maximum size of {self.max_size_mb}MB",
                        "max_size_bytes": self.max_size
                    }
                )

        return await call_next(request)


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce request timeouts.
    Prevents long-running requests from exhausting resources.
    """

    def __init__(self, app: ASGIApp, timeout: int):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Wrap request processing with a timeout.
        """
        try:
            # Wrap the request with a timeout
            response = await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout
            )
            return response

        except asyncio.TimeoutError:
            logger.error(
                f"Request timeout after {self.timeout}s: "
                f"{request.method} {request.url.path} from {request.client.host}"
            )
            return JSONResponse(
                status_code=504,
                content={
                    "success": False,
                    "error": "gateway_timeout",
                    "detail": f"Request exceeded maximum processing time of {self.timeout}s",
                    "timeout_seconds": self.timeout
                }
            )


def setup_request_limits(app):
    """
    Setup request limit middleware.

    Args:
        app: FastAPI application instance
    """
    # Add request size limit middleware
    app.add_middleware(
        RequestSizeLimitMiddleware,
        max_size=settings.MAX_REQUEST_SIZE
    )

    logger.info(
        f"Request size limit enabled: {round(settings.MAX_REQUEST_SIZE / 1024 / 1024, 2)}MB"
    )

    # Add request timeout middleware
    app.add_middleware(
        RequestTimeoutMiddleware,
        timeout=settings.REQUEST_TIMEOUT
    )

    logger.info(f"Request timeout enabled: {settings.REQUEST_TIMEOUT}s")
