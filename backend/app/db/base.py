# backend/app/db/base.py
"""
Database base and model imports.
Import all models here for Alembic to detect them.
"""
from app.models.user import Base, UserDB, APIKeyDB

# Import all models here for Alembic autogenerate to work
__all__ = [
    "Base",
    "UserDB",
    "APIKeyDB",
]
