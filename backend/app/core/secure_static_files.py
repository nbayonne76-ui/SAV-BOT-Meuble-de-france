# backend/app/core/secure_static_files.py
"""
Secure static file serving with security headers.
Extends FastAPI's StaticFiles with additional security headers.
"""
from typing import Optional
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.types import Scope, Receive, Send


class SecureStaticFiles(StaticFiles):
    """
    StaticFiles with security headers.

    Adds security headers to all static file responses to prevent
    common vulnerabilities like MIME sniffing, clickjacking, etc.
    """

    def __init__(
        self,
        *args,
        cache_max_age: int = 3600,
        add_csp: bool = True,
        **kwargs
    ):
        """
        Initialize secure static files handler.

        Args:
            cache_max_age: Cache-Control max-age in seconds (default: 3600 = 1 hour)
            add_csp: Whether to add Content-Security-Policy header
            *args, **kwargs: Arguments passed to StaticFiles
        """
        super().__init__(*args, **kwargs)
        self.cache_max_age = cache_max_age
        self.add_csp = add_csp

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handle static file requests and add security headers.
        """
        if scope["type"] != "http":
            await super().__call__(scope, receive, send)
            return

        # Intercept the send function to add headers
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                # Get the path to determine content type
                path = scope.get("path", "")

                # Security Headers
                security_headers = self._get_security_headers(path)

                # Add headers to response
                for header_name, header_value in security_headers.items():
                    headers.append(
                        (header_name.encode(), header_value.encode())
                    )

                message["headers"] = headers

            await send(message)

        await super().__call__(scope, receive, send_with_headers)

    def _get_security_headers(self, path: str) -> dict:
        """
        Get security headers for static file response.

        Args:
            path: Request path

        Returns:
            Dictionary of header name -> header value
        """
        headers = {}

        # X-Content-Type-Options: Prevent MIME sniffing
        # Ensures browsers respect the Content-Type header
        headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: Prevent clickjacking
        # SAMEORIGIN allows framing from same origin
        headers["X-Frame-Options"] = "SAMEORIGIN"

        # Referrer-Policy: Control referrer information
        # strict-origin-when-cross-origin provides good balance of privacy and functionality
        headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Cache-Control: Enable caching for static files
        # public: can be cached by any cache
        # max-age: how long to cache in seconds
        # immutable: file won't change (optional, good for versioned assets)
        if self._is_cacheable(path):
            headers["Cache-Control"] = f"public, max-age={self.cache_max_age}"
        else:
            # For non-cacheable files (e.g., HTML)
            headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

        # Content-Security-Policy: Restrict resource loading
        # This is a restrictive policy for static files
        if self.add_csp:
            csp_directives = [
                "default-src 'self'",  # Only load resources from same origin
                "img-src 'self' data: https:",  # Allow images from self, data URLs, and HTTPS
                "media-src 'self' https:",  # Allow media from self and HTTPS
                "object-src 'none'",  # Disable plugins (Flash, etc.)
                "base-uri 'self'",  # Restrict base tag URLs
                "form-action 'self'",  # Restrict form submissions
            ]
            headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # X-XSS-Protection: Enable browser XSS protection (legacy, but doesn't hurt)
        # mode=block: Block page if XSS detected
        headers["X-XSS-Protection"] = "1; mode=block"

        # Cross-Origin-Resource-Policy: Control cross-origin access
        # same-origin: Only same-origin requests can access
        headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # Permissions-Policy: Disable sensitive browser features
        # Prevents static files from accessing camera, microphone, etc.
        permissions = [
            "camera=()",
            "microphone=()",
            "geolocation=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()"
        ]
        headers["Permissions-Policy"] = ", ".join(permissions)

        return headers

    def _is_cacheable(self, path: str) -> bool:
        """
        Determine if a file should be cached based on its path.

        Args:
            path: Request path

        Returns:
            True if file should be cached, False otherwise
        """
        # Cache images, videos, and other media files
        cacheable_extensions = {
            # Images
            ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico",
            ".bmp", ".tiff", ".heic",
            # Videos
            ".mp4", ".webm", ".mov", ".avi", ".mkv",
            # Audio
            ".mp3", ".wav", ".ogg", ".m4a",
            # Fonts
            ".woff", ".woff2", ".ttf", ".otf", ".eot",
            # Documents (if you serve them)
            ".pdf",
        }

        # Check if path ends with cacheable extension
        path_lower = path.lower()
        return any(path_lower.endswith(ext) for ext in cacheable_extensions)


def create_secure_static_files(
    directory: str,
    cache_max_age: int = 3600,
    add_csp: bool = True,
    **kwargs
) -> SecureStaticFiles:
    """
    Create a SecureStaticFiles instance with sensible defaults.

    Args:
        directory: Directory to serve static files from
        cache_max_age: Cache-Control max-age in seconds (default: 3600 = 1 hour)
        add_csp: Whether to add Content-Security-Policy header
        **kwargs: Additional arguments passed to StaticFiles

    Returns:
        SecureStaticFiles instance

    Example:
        app.mount(
            "/uploads",
            create_secure_static_files(
                directory="uploads",
                cache_max_age=86400  # 24 hours
            ),
            name="uploads"
        )
    """
    return SecureStaticFiles(
        directory=directory,
        cache_max_age=cache_max_age,
        add_csp=add_csp,
        **kwargs
    )
