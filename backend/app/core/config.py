# backend/app/core/config.py
"""
Configuration management with environment validation
"""
import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Charger le .env depuis le repertoire backend
backend_dir = Path(__file__).parent.parent.parent
env_path = backend_dir / ".env"

# Load .env file
if env_path.exists():
    load_dotenv(env_path, override=True)
else:
    # Try parent directory
    parent_env = backend_dir.parent / ".env"
    if parent_env.exists():
        load_dotenv(parent_env, override=True)


class Settings:
    """Application settings loaded from environment variables"""

    def __init__(self):
        # ===================
        # Core Settings
        # ===================
        self.APP_NAME = os.getenv("APP_NAME", "Mobilier de France Chatbot")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.DEBUG = os.getenv("DEBUG", "True").lower() == "true"
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))

        # ===================
        # Security Settings
        # ===================
        # Secret key for JWT - MUST be set in production
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        if not self.SECRET_KEY:
            if self.DEBUG:
                # Generate a random key for development
                self.SECRET_KEY = secrets.token_urlsafe(32)
            else:
                raise ValueError(
                    "SECRET_KEY must be set in production! "
                    "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )

        # JWT Settings
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

        # ===================
        # Database Settings
        # ===================
        database_url = os.getenv("DATABASE_URL")

        # Debug: Check if DATABASE_URL is set
        if not database_url or database_url.strip() == "":
            print("[WARNING] DATABASE_URL environment variable is not set or is empty!")
            if not self.DEBUG:
                print("[ERROR] DATABASE_URL is required in production!")
                print("[INFO] Available environment variables:", list(os.environ.keys())[:10])
            database_url = "sqlite:///./chatbot.db"
            print(f"[INFO] Falling back to SQLite: {database_url}")
        else:
            print(f"[DEBUG] DATABASE_URL found: {database_url[:20]}...")

            # Transform PostgreSQL URLs for SQLAlchemy compatibility
            # Railway provides postgresql:// but SQLAlchemy needs postgresql+psycopg2://
            if database_url.startswith("postgresql://"):
                database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
                print("[INFO] Transformed postgresql:// to postgresql+psycopg2://")
            elif database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
                print("[INFO] Transformed postgres:// to postgresql+psycopg2://")

        self.DATABASE_URL = database_url

        # Warn if using SQLite in non-debug mode
        if not self.DEBUG and self.DATABASE_URL.startswith("sqlite"):
            print("[WARNING] Using SQLite in production is not recommended!")

        # ===================
        # Redis Settings
        # ===================
        self.REDIS_URL = os.getenv("REDIS_URL", "memory://")  # Use memory in development

        # ===================
        # API Keys
        # ===================
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not self.OPENAI_API_KEY:
            raise ValueError(
                "[ERROR] OPENAI_API_KEY not found in environment! "
                "Please set it in your .env file."
            )

        # ===================
        # Upload Settings
        # ===================
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "../uploads")
        self.MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
        self.ALLOWED_EXTENSIONS = os.getenv(
            "ALLOWED_EXTENSIONS",
            "jpg,jpeg,png,gif,heic,mp4,mov,avi,webm"
        )

        # ===================
        # Cloudinary Settings
        # ===================
        self.CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
        self.CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
        self.CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
        self.USE_CLOUDINARY = bool(
            self.CLOUDINARY_CLOUD_NAME and
            self.CLOUDINARY_API_KEY and
            self.CLOUDINARY_API_SECRET
        )

        # ===================
        # CORS Settings
        # ===================
        self.CORS_ORIGINS = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175,http://127.0.0.1:5176"
        )

        # ===================
        # Rate Limiting
        # ===================
        self.RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "100/minute")
        self.RATE_LIMIT_AUTH = os.getenv("RATE_LIMIT_AUTH", "5/minute")

        # ===================
        # Computed Properties
        # ===================
        self.cors_origins_list = [
            origin.strip() for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]
        self.allowed_extensions_list = [
            ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")
            if ext.strip()
        ]

    def __repr__(self):
        """Safe representation without exposing secrets"""
        return (
            f"Settings("
            f"APP_NAME={self.APP_NAME!r}, "
            f"DEBUG={self.DEBUG}, "
            f"HOST={self.HOST!r}, "
            f"PORT={self.PORT}"
            f")"
        )


# Create global settings instance
settings = Settings()

# Log configuration status (safe info only)
if settings.DEBUG:
    print(f"[CONFIG] App: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"[CONFIG] Debug mode: {settings.DEBUG}")
    print(f"[CONFIG] Database: {settings.DATABASE_URL.split('://')[0]}://***")
    print(f"[CONFIG] OpenAI API Key loaded: {'Yes' if settings.OPENAI_API_KEY else 'No'}")


# Helper functions for backwards compatibility
def get_cors_origins_list():
    """Get list of CORS origins"""
    return settings.cors_origins_list


def get_allowed_extensions_list():
    """Get list of allowed file extensions"""
    return settings.allowed_extensions_list
