# backend/app/main.py
"""
Main FastAPI application with security features enabled
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import time
import asyncio
import signal
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import setup_security_middleware
from app.core.rate_limit import setup_rate_limiter
from app.core.request_limits import setup_request_limits
from app.core.redis import CacheManager
from app.core.circuit_breaker import get_circuit_stats
from app.core.slow_query_logger import get_query_stats
from app.core.memory_monitor import get_memory_status, get_memory_usage, trigger_garbage_collection
from app.core.env_validator import validate_environment
from app.core.secure_static_files import create_secure_static_files
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
    Handles graceful initialization and shutdown of all resources.
    """
    # Startup
    startup_time = time.time()
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Environment: {'DEVELOPMENT' if settings.DEBUG else 'PRODUCTION'}")
    logger.info("=" * 60)

    # Validate environment variables first
    try:
        validation_summary = validate_environment()
        logger.info(
            f"✅ Environment validation passed: "
            f"{validation_summary['total_passed']} checks, "
            f"{validation_summary['total_warnings']} warnings"
        )
    except Exception as e:
        logger.critical(f"❌ Environment validation failed: {e}")
        logger.critical("Application cannot start with invalid configuration")
        raise

    # Track initialization failures
    init_failures = []

    # Initialize database tables
    app.state.db_available = False
    try:
        await init_db()
        app.state.db_available = True
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        app.state.db_available = False
        logger.error(f"❌ Database initialization failed: {e}")
        init_failures.append(("database", str(e)))

    # Initialize cache (Redis or in-memory)
    try:
        CacheManager.initialize(settings.REDIS_URL)
        cache_type = 'Redis' if not settings.REDIS_URL.startswith('memory') else 'In-memory'
        logger.info(f"✅ Cache initialized: {cache_type}")
    except Exception as e:
        logger.error(f"❌ Cache initialization failed: {e}")
        init_failures.append(("cache", str(e)))

    # Initialize storage
    try:
        StorageManager.initialize("local", base_path=settings.UPLOAD_DIR)
        logger.info("✅ Storage initialized successfully")
    except Exception as e:
        logger.error(f"❌ Storage initialization failed: {e}")
        init_failures.append(("storage", str(e)))

    # Initialize Cloudinary if configured
    try:
        CloudinaryService.initialize()
        if settings.USE_CLOUDINARY:
            logger.info(f"✅ Cloudinary initialized: {settings.CLOUDINARY_CLOUD_NAME}")
        else:
            logger.info("ℹ️  Cloudinary not configured - using local storage")
    except Exception as e:
        logger.error(f"⚠️  Cloudinary initialization failed: {e}")
        # Cloudinary is optional, so don't add to critical failures

    # Create necessary directories
    try:
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(settings.UPLOAD_DIR, "photos").mkdir(parents=True, exist_ok=True)
        Path(settings.UPLOAD_DIR, "videos").mkdir(parents=True, exist_ok=True)
        logger.info("✅ Upload directories created")
    except Exception as e:
        logger.error(f"❌ Failed to create upload directories: {e}")
        init_failures.append(("directories", str(e)))

    # Report initialization status
    startup_duration = round((time.time() - startup_time) * 1000, 2)
    logger.info("=" * 60)
    if init_failures:
        logger.warning(f"⚠️  Application started with {len(init_failures)} initialization failures")
        for component, error in init_failures:
            logger.warning(f"   - {component}: {error}")
    else:
        logger.info("✅ All components initialized successfully")

    logger.info(f"🚀 Application ready in {startup_duration}ms")

    if not settings.DEBUG:
        logger.info("🔒 Running in PRODUCTION mode - security features enabled")
    else:
        logger.info(f"📖 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")

    logger.info("=" * 60)

    # Application is running
    yield

    # Graceful shutdown
    shutdown_time = time.time()
    logger.info("=" * 60)
    logger.info("🛑 Initiating graceful shutdown...")
    logger.info("=" * 60)

    # Give in-flight requests time to complete
    logger.info("⏳ Waiting for in-flight requests to complete (max 30s)...")
    await asyncio.sleep(0.5)  # Brief pause to allow current requests to finish

    # Close cache connection
    try:
        logger.info("📦 Closing cache connection...")
        await CacheManager.close()
        logger.info("✅ Cache connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing cache: {e}")

    # Close database connections
    try:
        logger.info("🗄️  Closing database connections...")
        await close_db()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")

    # Final cleanup
    shutdown_duration = round((time.time() - shutdown_time) * 1000, 2)
    logger.info("=" * 60)
    logger.info(f"✅ Graceful shutdown completed in {shutdown_duration}ms")
    logger.info(f"👋 {settings.APP_NAME} stopped")
    logger.info("=" * 60)


# API Metadata for enhanced documentation
api_description = """
## 🛋️ Meuble de France - Chatbot Intelligent

API complète pour le chatbot de service client et SAV de Meuble de France.

### 🎯 Fonctionnalités Principales

* **💬 Chat Multilingue** - Support français, anglais et arabe
* **🎤 Interactions Vocales** - Transcription et synthèse vocale avec OpenAI Whisper et TTS
* **📸 Support Multimédia** - Upload et analyse d'images/vidéos
* **🎫 Gestion des Tickets** - Création et suivi automatisé des tickets SAV
* **🔍 Recherche Produits** - Recherche intelligente dans le catalogue
* **❓ FAQ Dynamique** - Base de connaissances enrichie
* **🔐 Authentification** - JWT avec refresh tokens et API keys
* **📊 Analytics** - Suivi des interactions et métriques

### 🔒 Sécurité

Cette API implémente de nombreuses mesures de sécurité:

* Rate limiting avec Redis
* Protection DoS (request size limits & timeouts)
* Circuit breakers pour les services externes
* Validation complète des entrées
* Headers de sécurité (CSP, HSTS, etc.)
* Chiffrement des tokens JWT
* Monitoring de performance et mémoire

### 📚 Documentation

* **Swagger UI**: `/docs` (mode développement)
* **ReDoc**: `/redoc` (mode développement)
* **OpenAPI Schema**: `/openapi.json` (mode développement)

### 🏥 Monitoring

* **Health Check**: `GET /health` - Statut basique de l'application
* **Readiness Check**: `GET /ready` - Vérification complète des dépendances
* **Query Stats**: `GET /query-stats` - Performance des requêtes SQL
* **Memory Status**: `GET /memory` - Utilisation mémoire et alertes
* **Circuit Breakers**: `GET /circuit-breakers` - État des services externes
* **Environment**: `GET /env-status` - Validation de la configuration

### 🔑 Authentification

Deux méthodes d'authentification disponibles:

1. **JWT Tokens** (utilisateurs)
   - Login via `/api/auth/login`
   - Refresh via `/api/auth/refresh`
   - Bearer token dans header `Authorization`

2. **API Keys** (applications)
   - Création via `/api/auth/api-keys`
   - Key dans header `X-API-Key`

### 📞 Support

Pour toute question technique, contactez l'équipe de développement.

---

*Généré avec FastAPI et Claude Code*
"""

api_tags_metadata = [
    {
        "name": "Health",
        "description": "Endpoints de monitoring et vérification de l'état de l'application. "
                      "Utilisez `/health` pour les load balancers et `/ready` pour les vérifications complètes.",
    },
    {
        "name": "Authentication",
        "description": "Gestion de l'authentification utilisateur et des API keys. "
                      "Supporte JWT avec refresh tokens et authentification par API key.",
    },
    {
        "name": "Chat",
        "description": "Interface de chat intelligent multilingue. "
                      "Support du contexte conversationnel, détection de langue, et réponses personnalisées.",
    },
    {
        "name": "Upload",
        "description": "Upload et gestion de fichiers multimédias (images, vidéos, audio). "
                      "Support de Cloudinary pour le stockage en production.",
    },
    {
        "name": "Products",
        "description": "Recherche et consultation du catalogue de produits. "
                      "Filtrage par catégories, prix, disponibilité.",
    },
    {
        "name": "Tickets",
        "description": "Gestion complète des tickets SAV. "
                      "Création, suivi, mise à jour, et résolution automatique.",
    },
    {
        "name": "FAQ",
        "description": "Base de connaissances et questions fréquentes. "
                      "Recherche sémantique et catégorisation.",
    },
    {
        "name": "SAV",
        "description": "Services après-vente: garanties, interventions, tickets. "
                      "Vérification de garantie et gestion des demandes.",
    },
    {
        "name": "Voice",
        "description": "Services vocaux: transcription (Whisper) et synthèse (TTS). "
                      "Support multilingue avec détection automatique.",
    },
    {
        "name": "Realtime",
        "description": "API temps réel pour conversations vocales et streaming. "
                      "WebSocket et HTTP streaming disponibles.",
    },
]

# Create FastAPI app with enhanced documentation
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=api_description,
    summary="API de chatbot intelligent pour service client et SAV",
    # Contact and license information
    contact={
        "name": "Meuble de France - Équipe Technique",
        "url": "https://meuble-de-france.com",
        "email": "support@meuble-de-france.com",
    },
    license_info={
        "name": "Propriétaire",
        "url": "https://meuble-de-france.com/licence",
    },
    # Tags metadata for better organization
    openapi_tags=api_tags_metadata,
    # Disable docs in production for security
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    # Servers configuration
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Serveur de développement local"
        },
        {
            "url": "https://api.meuble-de-france.com",
            "description": "Serveur de production"
        }
    ] if settings.DEBUG else [],
    # Application lifecycle
    lifespan=lifespan,
    # Disable automatic trailing slash redirects
    redirect_slashes=False,
    # Terms of service
    terms_of_service="https://meuble-de-france.com/terms",
)

# Setup rate limiter
setup_rate_limiter(app)

# Setup request limits (size and timeout)
setup_request_limits(app)

# Setup security middleware
setup_security_middleware(app)

# Setup response compression (GZip)
# Compress responses > 500 bytes to reduce bandwidth
app.add_middleware(GZipMiddleware, minimum_size=500)
logger.info("Response compression enabled (GZip, min size: 500 bytes)")

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

# CRITICAL: Always include Railway frontend URL in production
railway_frontend_url = "https://proactive-nurturing-production.up.railway.app"
if railway_frontend_url not in cors_origins:
    cors_origins.append(railway_frontend_url)
    logger.info(f"✅ Added Railway frontend URL to CORS: {railway_frontend_url}")

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

# Mount uploads directory with security headers
uploads_path = Path(settings.UPLOAD_DIR)
if uploads_path.exists():
    app.mount(
        "/uploads",
        create_secure_static_files(
            directory=str(uploads_path),
            cache_max_age=86400,  # 24 hours for uploaded media files
            add_csp=True
        ),
        name="uploads"
    )
    logger.info(f"✅ Uploads directory mounted with security headers at /uploads")

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

    # Check memory status
    memory_status = get_memory_status()

    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "uptime_seconds": round(time.time() - process.create_time(), 2),
        "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
        "memory_status": memory_status["status"],  # ok, warning, critical
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

    # Check memory usage
    memory_status = get_memory_status()
    memory_healthy = memory_status["status"] != "critical"

    checks["memory"] = {
        "healthy": memory_healthy,
        "status": memory_status["status"],
        "rss_mb": memory_status["usage"]["process"]["rss_mb"],
        "percent_of_system": memory_status["usage"]["process"]["percent_of_system"],
        "alert_level": memory_status["alert_level"],
        "messages": memory_status["messages"] if memory_status["messages"] else None
    }

    # Calculate overall readiness
    critical_checks = ["database", "cache", "uploads_directory"]
    critical_ready = all(checks[key]["healthy"] for key in critical_checks)

    # External services and memory are important but not critical for startup
    # Memory warning is ok, but critical memory should prevent readiness
    all_ready = critical_ready and all_breakers_healthy and memory_healthy

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


@app.get("/query-stats", tags=["Health"])
async def query_statistics():
    """
    Database query performance statistics.
    Returns metrics on query execution times and slow query detection.
    """
    stats = get_query_stats()

    # Determine if performance is concerning
    slow_query_percentage = stats.get("slow_query_percentage", 0)
    performance_status = "good"

    if slow_query_percentage > 10:
        performance_status = "critical"
    elif slow_query_percentage > 5:
        performance_status = "warning"

    return {
        "performance_status": performance_status,
        "stats": stats,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/memory", tags=["Health"])
async def memory_status():
    """
    Memory usage monitoring endpoint.
    Returns current memory usage with threshold checks and alerts.
    """
    status = get_memory_status()
    return {
        **status,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/memory/usage", tags=["Health"])
async def memory_usage_detail():
    """
    Detailed memory usage without threshold checks.
    Returns process and system memory metrics.
    """
    usage = get_memory_usage()
    return {
        "usage": usage,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/memory/gc", tags=["Health"])
async def garbage_collect():
    """
    Manually trigger garbage collection.
    Useful for freeing memory when approaching thresholds.
    """
    result = trigger_garbage_collection()
    return {
        "success": True,
        "gc_result": result,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/env-status", tags=["Health"])
async def environment_status():
    """
    Environment variable validation status.
    Re-runs validation checks and returns current configuration status.
    Useful for debugging configuration issues.
    """
    try:
        summary = validate_environment()
        return {
            "valid": summary["valid"],
            "errors": summary["errors"],
            "warnings": summary["warnings"],
            "passed_checks": summary["passed_checks"],
            "summary": {
                "total_errors": summary["total_errors"],
                "total_warnings": summary["total_warnings"],
                "total_passed": summary["total_passed"]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
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
    """
    Return the ASGI application.

    This makes the callable suitable as a factory for uvicorn when invoked as
    `uvicorn app.main:main` — uvicorn will call this function and receive the
    FastAPI `app` instance instead of nesting server runs.
    """
    return app


def run_server():
    """
    Run the application with graceful shutdown handling.
    This contains the previous behavior of `main()` when executed directly.
    """
    # Signal handler for graceful shutdown
    def signal_handler(signum, frame):
        """Handle shutdown signals (SIGTERM, SIGINT)"""
        signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        logger.info(f"Received {signal_name} signal, initiating graceful shutdown...")

    # Register signal handlers (not on Windows in development due to reload)
    if not settings.DEBUG:
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    # Configure uvicorn with graceful shutdown settings
    config = uvicorn.Config(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
        access_log=settings.DEBUG,
        # Graceful shutdown settings
        timeout_keep_alive=5,  # Keep-alive timeout
        timeout_graceful_shutdown=30,  # Max time to wait for shutdown
    )

    server = uvicorn.Server(config)

    try:
        logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
        server.run()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        logger.info("Server stopped")


if __name__ == "__main__":
    run_server()
