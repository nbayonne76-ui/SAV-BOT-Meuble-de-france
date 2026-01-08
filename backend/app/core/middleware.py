# backend/app/core/middleware.py
"""
Security middleware for headers, request validation, and logging
"""
import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    Similar to helmet.js for Node.js.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Strict Transport Security (HSTS) in production
        # - max-age=63072000 (2 years) - tells browsers to always use HTTPS
        # - includeSubDomains - applies to all subdomains
        # - preload - eligible for browser preload lists
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

        # Content Security Policy (relaxed for API)
        if not settings.DEBUG:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' https:;"
            )

        # Ensure Set-Cookie headers have Secure flag in production
        if not settings.DEBUG:
            set_cookie = response.headers.get("set-cookie")
            if set_cookie and "Secure" not in set_cookie:
                # Add Secure flag to cookies in production
                if not set_cookie.endswith(";"):
                    set_cookie += ";"
                set_cookie += " Secure; HttpOnly; SameSite=Strict"
                response.headers["set-cookie"] = set_cookie

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests with timing information.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Start timing
        start_time = time.time()

        # Get client info
        client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
        if "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()

        # Log request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - Client: {client_ip}"
        )

        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"Status: {response.status_code} - Duration: {duration_ms:.2f}ms"
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"Error: {str(e)} - Duration: {duration_ms:.2f}ms"
            )
            raise


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit request body size.
    """

    def __init__(self, app: ASGIApp, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check content-length header
        content_length = request.headers.get("content-length")
        if content_length:
            if int(content_length) > self.max_size:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=413,
                    content={
                        "success": False,
                        "error": "request_too_large",
                        "detail": f"Request body too large. Maximum size is {self.max_size // (1024*1024)}MB"
                    }
                )

        return await call_next(request)


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to redirect HTTP requests to HTTPS in production.
    Only applies when ENFORCE_HTTPS is enabled.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip redirect if HTTPS enforcement is disabled or already HTTPS
        if not settings.ENFORCE_HTTPS:
            return await call_next(request)

        # Check if request is HTTP (not HTTPS)
        # In production behind a proxy, check X-Forwarded-Proto header
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "")
        is_https = (
            request.url.scheme == "https" or
            forwarded_proto.lower() == "https"
        )

        if not is_https:
            # Redirect to HTTPS version
            from fastapi.responses import RedirectResponse
            https_url = str(request.url).replace("http://", "https://", 1)
            logger.info(f"🔒 Redirecting HTTP to HTTPS: {request.url.path}")
            return RedirectResponse(url=https_url, status_code=301)

        return await call_next(request)


class TrustedHostMiddleware:
    """
    Middleware to validate the Host header against trusted hosts.
    Prevents host header injection attacks.
    """

    def __init__(self, app: ASGIApp, allowed_hosts: list[str] = None):
        self.app = app
        self.allowed_hosts = allowed_hosts or ["*"]

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            host = headers.get(b"host", b"").decode("latin-1")

            if "*" not in self.allowed_hosts:
                host_without_port = host.split(":")[0]
                if host_without_port not in self.allowed_hosts:
                    from starlette.responses import PlainTextResponse
                    response = PlainTextResponse("Invalid host header", status_code=400)
                    await response(scope, receive, send)
                    return

        await self.app(scope, receive, send)


def setup_security_middleware(app):
    """
    Configure all security middleware for the application.

    Args:
        app: FastAPI application instance
    """
    # Add middleware in reverse order (last added = first executed)

    # Request size limit
    app.add_middleware(RequestSizeLimitMiddleware, max_size=settings.MAX_FILE_SIZE)

    # Request logging
    app.add_middleware(RequestLoggingMiddleware)

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # HTTPS redirect (only when enforced)
    if settings.ENFORCE_HTTPS:
        app.add_middleware(HTTPSRedirectMiddleware)
        logger.info("🔒 HTTPS enforcement enabled - HTTP requests will be redirected")

    logger.info("Security middleware configured")


# Input sanitization utilities
import re
import html


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize a string input to prevent XSS and injection attacks.

    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not value:
        return value

    # Truncate to max length
    value = value[:max_length]

    # HTML escape
    value = html.escape(value)

    # Remove null bytes
    value = value.replace("\x00", "")

    # Remove control characters except newlines and tabs
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)

    return value


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal and other attacks.

    Args:
        filename: Input filename

    Returns:
        Sanitized filename
    """
    if not filename:
        return filename

    # Remove path components
    filename = filename.split("/")[-1]
    filename = filename.split("\\")[-1]

    # Remove dangerous characters
    filename = re.sub(r'[<>:"|?*]', '_', filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:250] + ("." + ext if ext else "")

    return filename


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
