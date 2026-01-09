#!/usr/bin/env python3
"""
Database initialization script for Railway deployment
Runs Alembic migrations to set up tables
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from alembic.config import Config
from alembic import command


def init_database():
    """Initialize database with Alembic migrations"""

    print("🚀 Starting database initialization...")

    # Check if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        sys.exit(1)

    # Mask password in URL for logging
    masked_url = database_url.split("@")[1] if "@" in database_url else database_url
    print(f"✅ Database URL configured: ...@{masked_url}")

    # Configure Alembic
    alembic_cfg = Config("alembic.ini")

    try:
        # Run migrations to latest version
        print("📦 Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations completed successfully!")

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()
