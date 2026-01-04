# backend/app/repositories/__init__.py
"""
Database repositories for data access
"""
from app.repositories.ticket_repository import ticket_repository

__all__ = ["ticket_repository"]
