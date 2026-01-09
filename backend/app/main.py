# backend/app/main.py
"""
Main FastAPI application with security features enabled
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import logging
import time
from pathlib import Path
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import setup_security_middleware
from app.core.rate_limit import setup_rate_limiter
from app.core.redis import CacheManager
from app.core.circuit_breaker import get_circuit_stats
from app.db.session import init_db, close_db
from app.api.endpoints import chat, upload, products, tickets, faq, sav, auth, voice, realtime, realtime_ws
from app.services.storage import StorageManager
from app.services.cloudinary_storage import CloudinaryService

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
        await init_db()
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

    # Initialize Cloudinary if configured
    try:
        CloudinaryService.initialize()
        if settings.USE_CLOUDINARY:
            logger.info(f"Cloudinary initialized: {settings.CLOUDINARY_CLOUD_NAME}")
        else:
            logger.info("Cloudinary not configured - using local storage")
    except Exception as e:
        logger.error(f"Cloudinary initialization failed: {e}")

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

    # Close database connections
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


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

logger.info(f"CORS allowed origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"],
    expose_headers=["X-Request-ID", "X-Response-Time", "X-RateLimit-Limit", "Retry-After"],
    max_age=600  # Cache preflight for 10 minutes
)

# Mount uploads directory
uploads_path = Path(settings.UPLOAD_DIR)
if uploads_path.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# Include routers
# Authentication (public endpoints)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# Protected endpoints
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
# Upload router now works correctly with redirect_slashes=False
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(faq.router, prefix="/api/faq", tags=["FAQ"])
app.include_router(sav.router, prefix="/api", tags=["SAV"])
# Voice mode endpoints
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(realtime.router, prefix="/api/realtime", tags=["Realtime"])
app.include_router(realtime_ws.router, prefix="/api/realtime-ws", tags=["Realtime WebSocket"])


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
    Basic health check endpoint for load balancers.
    Simple liveness probe - returns 200 if app is running.
    For detailed checks, use /ready endpoint.
    """
    import psutil
    import os

    # Get process info
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "uptime_seconds": round(time.time() - process.create_time(), 2),
        "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
        "cpu_percent": process.cpu_percent(),
        "threads": process.num_threads()
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Comprehensive readiness check endpoint.
    Verifies all dependencies are available with detailed status.
    """
    import time
    from app.core.redis import CacheManager
    from app.core.circuit_breaker import get_circuit_stats

    checks = {}

    # Check database
    db_start = time.time()
    db_ready = True
    db_error = None
    try:
        from sqlalchemy import text
        from app.db.session import engine
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_ready = False
        db_error = str(e)
    db_time = round((time.time() - db_start) * 1000, 2)

    checks["database"] = {
        "healthy": db_ready,
        "response_time_ms": db_time,
        "error": db_error
    }

    # Check cache (Redis or memory)
    cache_start = time.time()
    cache_ready = False
    cache_error = None
    cache_type = "unknown"
    try:
        cache = CacheManager.get_cache()
        cache_ready = await cache.ping()
        cache_type = "redis" if not settings.REDIS_URL.startswith("memory") else "memory"
    except Exception as e:
        cache_ready = False
        cache_error = str(e)
    cache_time = round((time.time() - cache_start) * 1000, 2)

    checks["cache"] = {
        "healthy": cache_ready,
        "type": cache_type,
        "response_time_ms": cache_time,
        "error": cache_error
    }

    # Check uploads directory
    uploads_exists = Path(settings.UPLOAD_DIR).exists()
    uploads_writable = False
    try:
        if uploads_exists:
            test_file = Path(settings.UPLOAD_DIR) / ".health_check"
            test_file.touch()
            test_file.unlink()
            uploads_writable = True
    except Exception as e:
        uploads_writable = False

    checks["uploads_directory"] = {
        "healthy": uploads_exists and uploads_writable,
        "exists": uploads_exists,
        "writable": uploads_writable,
        "path": str(settings.UPLOAD_DIR)
    }

    # Check OpenAI API (via circuit breaker stats)
    circuit_stats = get_circuit_stats()
    openai_healthy = True
    openai_breakers = ["openai", "openai-whisper", "openai-chat", "openai-tts"]

    openai_status = {}
    for breaker_name in openai_breakers:
        if breaker_name in circuit_stats:
            breaker = circuit_stats[breaker_name]
            is_healthy = breaker["state"] == "closed"
            openai_healthy = openai_healthy and is_healthy
            openai_status[breaker_name] = {
                "state": breaker["state"],
                "success_rate": breaker["success_rate"],
                "total_calls": breaker["total_calls"]
            }

    checks["openai_api"] = {
        "healthy": openai_healthy,
        "breakers": openai_status,
        "configured": bool(settings.OPENAI_API_KEY)
    }

    # Check Cloudinary (if configured)
    if settings.USE_CLOUDINARY:
        cloudinary_healthy = True
        cloudinary_status = {}

        if "cloudinary" in circuit_stats:
            breaker = circuit_stats["cloudinary"]
            cloudinary_healthy = breaker["state"] == "closed"
            cloudinary_status = {
                "state": breaker["state"],
                "success_rate": breaker["success_rate"],
                "total_calls": breaker["total_calls"]
            }

        checks["cloudinary"] = {
            "healthy": cloudinary_healthy,
            "breaker": cloudinary_status,
            "configured": True,
            "cloud_name": settings.CLOUDINARY_CLOUD_NAME
        }
    else:
        checks["cloudinary"] = {
            "healthy": True,  # Not required if not configured
            "configured": False,
            "message": "Cloudinary not configured - using local storage"
        }

    # Check circuit breakers overall health
    all_breakers_healthy = all(
        breaker["state"] == "closed"
        for breaker in circuit_stats.values()
    )

    checks["circuit_breakers"] = {
        "healthy": all_breakers_healthy,
        "total": len(circuit_stats),
        "open": sum(1 for b in circuit_stats.values() if b["state"] == "open"),
        "half_open": sum(1 for b in circuit_stats.values() if b["state"] == "half_open")
    }

    # Calculate overall readiness
    critical_checks = ["database", "cache", "uploads_directory"]
    critical_ready = all(checks[key]["healthy"] for key in critical_checks)

    # External services are important but not critical for startup
    all_ready = critical_ready and all_breakers_healthy

    return {
        "ready": all_ready,
        "critical_ready": critical_ready,  # Can start if critical services are up
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/circuit-breakers", tags=["Health"])
async def circuit_breaker_status():
    """
    Circuit breaker status endpoint.
    Returns statistics for all registered circuit breakers.
    """
    stats = get_circuit_stats()

    # Calculate overall health
    all_closed = all(
        breaker["state"] == "closed"
        for breaker in stats.values()
    )

    return {
        "healthy": all_closed,
        "breakers": stats,
        "summary": {
            "total": len(stats),
            "closed": sum(1 for b in stats.values() if b["state"] == "closed"),
            "open": sum(1 for b in stats.values() if b["state"] == "open"),
            "half_open": sum(1 for b in stats.values() if b["state"] == "half_open")
        }
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
