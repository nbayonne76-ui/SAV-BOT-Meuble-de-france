# backend/app/main.py
"""
Main FastAPI application with security features enabled
"""
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import List
import uvicorn
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import setup_security_middleware
from app.core.rate_limit import setup_rate_limiter
from app.core.redis import CacheManager
from app.db.session import init_db, close_db
from app.api.endpoints import chat, upload, products, tickets, faq, sav, auth
from app.services.storage import StorageManager

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Initialize database tables
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Initialize cache (Redis or in-memory)
    try:
        CacheManager.initialize(settings.REDIS_URL)
        logger.info(f"Cache initialized: {'Redis' if not settings.REDIS_URL.startswith('memory') else 'In-memory'}")
    except Exception as e:
        logger.error(f"Cache initialization failed: {e}")

    # Initialize storage
    try:
        StorageManager.initialize("local", base_path=settings.UPLOAD_DIR)
        logger.info("Storage initialized successfully")
    except Exception as e:
        logger.error(f"Storage initialization failed: {e}")

    # Create necessary directories
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.UPLOAD_DIR, "photos").mkdir(parents=True, exist_ok=True)
    Path(settings.UPLOAD_DIR, "videos").mkdir(parents=True, exist_ok=True)

    if not settings.DEBUG:
        logger.info("Running in PRODUCTION mode - security features enabled")
    else:
        logger.info(f"API Documentation: http://{settings.HOST}:{settings.PORT}/docs")

    yield

    # Shutdown
    logger.info("Shutting down application")

    # Close cache connection
    try:
        await CacheManager.close()
        logger.info("Cache connection closed")
    except Exception as e:
        logger.error(f"Error closing cache: {e}")

    close_db()


# Create FastAPI app with conditional docs
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Chatbot intelligent pour Meuble de France - Service client et SAV",
    # Disable docs in production
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
    redirect_slashes=False  # Disable automatic trailing slash redirects to fix 307 on uploads
)

# Setup rate limiter
setup_rate_limiter(app)

# Setup security middleware
setup_security_middleware(app)

# CORS Configuration - more restrictive in production
if settings.DEBUG:
    # Development: allow all configured origins
    cors_origins = settings.cors_origins_list
else:
    # Production: only allow specific origins
    cors_origins = [
        origin for origin in settings.cors_origins_list
        if not origin.startswith("http://localhost")
    ]
    # Fallback if no production origins configured
    if not cors_origins:
        cors_origins = settings.cors_origins_list

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"],
    expose_headers=["X-Request-ID", "X-Response-Time", "X-RateLimit-Limit", "Retry-After"],
    max_age=600  # Cache preflight for 10 minutes
)

# Fix for 307 redirect issue - handle /api/upload without trailing slash
# IMPORTANT: This must be defined BEFORE including the upload router
# This route forwards to the upload handler to avoid redirect that loses POST data
@app.post("/api/upload", include_in_schema=False)
async def upload_no_slash_redirect(files: List[UploadFile] = File(...)):
    """Direct handler for /api/upload (without trailing slash) to avoid 307 redirect"""
    from app.api.endpoints.upload import _upload_files_handler
    return await _upload_files_handler(files)

# Mount uploads directory
uploads_path = Path(settings.UPLOAD_DIR)
if uploads_path.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# Include routers
# Authentication (public endpoints)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# Protected endpoints
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
# Upload router removed - using direct route above to avoid 307 redirect
# app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(faq.router, prefix="/api/faq", tags=["FAQ"])
app.include_router(sav.router, prefix="/api", tags=["SAV"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with basic app info"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "disabled"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.
    Returns basic health status.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check endpoint.
    Verifies all dependencies are available.
    """
    from app.core.redis import CacheManager

    # Check database
    db_ready = True
    try:
        from sqlalchemy import text
        from app.db.session import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_ready = False

    # Check cache (Redis or memory)
    cache_ready = False
    try:
        cache = CacheManager.get_cache()
        cache_ready = await cache.ping()
    except Exception:
        cache_ready = False

    checks = {
        "database": db_ready,
        "cache": cache_ready,
        "uploads_dir": Path(settings.UPLOAD_DIR).exists()
    }

    all_ready = all(checks.values())

    return {
        "ready": all_ready,
        "checks": checks
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler.
    In production, hides internal error details.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[{request_id}] Unhandled exception: {str(exc)}", exc_info=True)

    if settings.DEBUG:
        detail = str(exc)
    else:
        detail = "An internal error occurred. Please try again later."

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "internal_server_error",
            "detail": detail,
            "request_id": request_id
        }
    )


def main():
    """Main function to run the application"""
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
        access_log=settings.DEBUG
    )


if __name__ == "__main__":
    main()
