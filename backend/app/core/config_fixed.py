# backend/app/core/config_fixed.py
"""
Configuration simplifiée qui charge directement depuis .env
sans utiliser pydantic_settings qui semble avoir des problèmes de cache
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger le .env depuis le répertoire backend
backend_dir = Path(__file__).parent.parent.parent
env_path = backend_dir / ".env"

print(f"🔍 Chargement .env depuis: {env_path}")
print(f"   Fichier existe: {env_path.exists()}")

# Forcer le rechargement
load_dotenv(env_path, override=True)

# Charger les variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "../uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,heic,mp4,mov,avi")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
APP_NAME = os.getenv("APP_NAME", "Meuble de France Chatbot")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

# Validation
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY non trouvée dans .env!")

print(f"✅ OPENAI_API_KEY chargée: {OPENAI_API_KEY[:20]}...")

# Helper properties
def get_cors_origins_list():
    return [origin.strip() for origin in CORS_ORIGINS.split(",")]

def get_allowed_extensions_list():
    return [ext.strip() for ext in ALLOWED_EXTENSIONS.split(",")]

# Créer un objet settings compatible
class Settings:
    def __init__(self):
        self.OPENAI_API_KEY = OPENAI_API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.DATABASE_URL = DATABASE_URL
        self.REDIS_URL = REDIS_URL
        self.HOST = HOST
        self.PORT = PORT
        self.DEBUG = DEBUG
        self.UPLOAD_DIR = UPLOAD_DIR
        self.MAX_FILE_SIZE = MAX_FILE_SIZE
        self.ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS
        self.CORS_ORIGINS = CORS_ORIGINS
        self.APP_NAME = APP_NAME
        self.APP_VERSION = APP_VERSION
        self.cors_origins_list = get_cors_origins_list()
        self.allowed_extensions_list = get_allowed_extensions_list()

settings = Settings()
