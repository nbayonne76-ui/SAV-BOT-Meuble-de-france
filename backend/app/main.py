# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import logging
from pathlib import Path

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.endpoints import chat, upload, products, tickets, faq, sav

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Chatbot intelligent pour Meuble de France",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory
uploads_path = Path(settings.UPLOAD_DIR)
if uploads_path.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(faq.router, prefix="/api/faq", tags=["FAQ"])
app.include_router(sav.router, prefix="/api", tags=["SAV"])

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📝 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"🔧 Debug mode: {settings.DEBUG}")

    # Create necessary directories
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.UPLOAD_DIR, "photos").mkdir(parents=True, exist_ok=True)
    Path(settings.UPLOAD_DIR, "videos").mkdir(parents=True, exist_ok=True)

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("👋 Shutting down application")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )

def main():
    """Main function to run the application"""
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

if __name__ == "__main__":
    main()
