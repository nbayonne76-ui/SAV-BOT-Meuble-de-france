# backend/app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""

    # API Keys
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")

    # Database
    DATABASE_URL: str = Field(default="sqlite:///./chatbot.db", env="DATABASE_URL")
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")

    # File Storage
    UPLOAD_DIR: str = Field(default="../uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: str = Field(default="jpg,jpeg,png,heic,mp4,mov,avi", env="ALLOWED_EXTENSIONS")

    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://localhost:3000", env="CORS_ORIGINS")

    # Application
    APP_NAME: str = Field(default="Meuble de France Chatbot", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get allowed extensions as a list"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        case_sensitive = True

# Create global settings instance
settings = Settings()
