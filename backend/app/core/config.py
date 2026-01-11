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
        # DEBUG defaults to False for security - explicitly set to True for development
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
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

        # HTTPS Enforcement
        # In production (DEBUG=False), HTTPS is enforced by default
        # Set ENFORCE_HTTPS=false to disable (not recommended)
        self.ENFORCE_HTTPS = os.getenv("ENFORCE_HTTPS", "true" if not self.DEBUG else "false").lower() == "true"

        # ===================
        # Database Settings
        # ===================
        database_url = os.getenv("DATABASE_URL")

        # Check if DATABASE_URL is set
        if not database_url or database_url.strip() == "":
            if not self.DEBUG:
                # In production, DATABASE_URL is REQUIRED
                raise ValueError(
                    "DATABASE_URL environment variable is required in production! "
                    "Please set a PostgreSQL connection string. "
                    "Example: postgresql://user:password@host:port/database"
                )
            else:
                # In development, fall back to SQLite
                print("[WARNING] DATABASE_URL not set - using SQLite for development")
                database_url = "sqlite:///./chatbot.db"
                print(f"[INFO] Using SQLite: {database_url}")
        else:
            # CRITICAL: Strip whitespace and newlines that might be in the environment variable
            database_url = database_url.strip()

            # Redact sensitive connection info from logs
            db_type = database_url.split('://')[0] if '://' in database_url else 'unknown'
            print(f"[DEBUG] DATABASE_URL found: {db_type}://***")

            # Transform PostgreSQL URLs for SQLAlchemy compatibility
            # Railway/Heroku provide postgresql:// but SQLAlchemy needs postgresql+psycopg2://
            if database_url.startswith("postgresql://"):
                database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
                print("[INFO] Transformed postgresql:// to postgresql+psycopg2://")
            elif database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
                print("[INFO] Transformed postgres:// to postgresql+psycopg2://")

        self.DATABASE_URL = database_url

        # Validate: SQLite not allowed in production
        if not self.DEBUG and self.DATABASE_URL.startswith("sqlite"):
            raise ValueError(
                "SQLite is not supported in production! "
                "Please configure a PostgreSQL DATABASE_URL."
            )

        # Slow Query Logging (Performance Monitoring)
        # Log queries that take longer than this threshold (in milliseconds)
        self.SLOW_QUERY_THRESHOLD_MS = int(os.getenv("SLOW_QUERY_THRESHOLD_MS", "1000"))  # 1 second

        # Memory Usage Alerting Thresholds
        # Memory usage thresholds in MB for alerting
        self.MEMORY_WARNING_THRESHOLD_MB = int(os.getenv("MEMORY_WARNING_THRESHOLD_MB", "500"))  # 500 MB
        self.MEMORY_CRITICAL_THRESHOLD_MB = int(os.getenv("MEMORY_CRITICAL_THRESHOLD_MB", "1000"))  # 1 GB
        # Memory usage percentage thresholds (relative to system memory)
        self.MEMORY_WARNING_PERCENT = int(os.getenv("MEMORY_WARNING_PERCENT", "70"))  # 70%
        self.MEMORY_CRITICAL_PERCENT = int(os.getenv("MEMORY_CRITICAL_PERCENT", "85"))  # 85%

        # ===================
        # Redis Settings
        # ===================
        redis_url = os.getenv("REDIS_URL")

        if not redis_url:
            if not self.DEBUG:
                # In production, warn about memory cache limitations
                print("[WARNING] REDIS_URL not set - using in-memory cache")
                print("[WARNING] Memory cache will not work correctly with multiple workers!")
                print("[INFO] For production, configure a Redis instance")
                redis_url = "memory://"
            else:
                # In development, memory cache is fine
                redis_url = "memory://"

        self.REDIS_URL = redis_url

        # ===================
        # API Keys
        # ===================
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not self.OPENAI_API_KEY:
            raise ValueError(
                "[ERROR] OPENAI_API_KEY not found in environment! "
                "Please set it in your .env file."
            )

        # Validate OpenAI API key format
        openai_key = self.OPENAI_API_KEY.strip()
        if not openai_key.startswith("sk-"):
            raise ValueError(
                "[ERROR] Invalid OPENAI_API_KEY format! "
                "OpenAI API keys must start with 'sk-' (secret key) or 'sk-proj-' (project key). "
                "Please check your API key at https://platform.openai.com/api-keys"
            )

        # Validate key length (OpenAI keys are typically 51+ characters)
        if len(openai_key) < 20:
            raise ValueError(
                "[ERROR] OPENAI_API_KEY appears to be too short! "
                "Valid OpenAI API keys are typically 51+ characters. "
                "Please verify your API key."
            )

        self.OPENAI_API_KEY = openai_key

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
        # Request Limits (DoS Prevention)
        # ===================
        # Maximum request body size for JSON/form data (5MB)
        self.MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "5242880"))  # 5MB
        # Request timeout in seconds (30s)
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
        # Maximum concurrent requests per IP (100)
        self.MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))

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
            (
                "http://localhost:5173,"
                "http://localhost:5174,"
                "http://localhost:5173,"
                "http://localhost:5175,"
                "http://localhost:5176,"
                "http://localhost:3000,"
                "http://127.0.0.1:5173,"
                "http://127.0.0.1:5174,"
                "http://127.0.0.1:5175,"
                "https://proactive-nurturing-production.up.railway.app,"
                "http://127.0.0.1:5176"
            )
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
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
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

# Log configuration status (safe info only - NO SENSITIVE DATA)
if settings.DEBUG:
    print(f"[CONFIG] App: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"[CONFIG] Debug mode: {settings.DEBUG}")
    # Only show database type, not connection string
    db_type = settings.DATABASE_URL.split('://')[0] if '://' in settings.DATABASE_URL else 'unknown'
    print(f"[CONFIG] Database type: {db_type}")
    # Never log the actual API key, just confirm it's loaded
    print(f"[CONFIG] OpenAI API Key: {'[OK] Loaded' if settings.OPENAI_API_KEY else '[X] Missing'}")
    print(f"[CONFIG] HTTPS Enforcement: {'[OK] Enabled' if settings.ENFORCE_HTTPS else '[X] Disabled'}")
    print(f"[CONFIG] Redis: {'[OK] Configured' if not settings.REDIS_URL.startswith('memory') else 'In-memory'}")
    print(f"[CONFIG] Cloudinary: {'[OK] Configured' if settings.USE_CLOUDINARY else 'Local storage'}")


# Helper functions for backwards compatibility
def get_cors_origins_list():
    """Get list of CORS origins"""
    return settings.cors_origins_list


def get_allowed_extensions_list():
    """Get list of allowed file extensions"""
    return settings.allowed_extensions_list
