# backend/app/db/__init__.py
"""
Database module with async support
"""
from app.db.session import get_db, init_db, close_db, AsyncSessionLocal, engine

__all__ = ["get_db", "init_db", "close_db", "AsyncSessionLocal", "SessionLocal", "engine"]

# Backwards compatibility alias
SessionLocal = AsyncSessionLocal
