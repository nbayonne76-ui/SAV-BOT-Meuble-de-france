# backend/app/db/session.py
"""
Database session management with async support
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool, NullPool
from typing import AsyncGenerator

from app.core.config import settings
from app.core.slow_query_logger import setup_slow_query_logging

# Create async engine based on database URL
# Convert sync URLs to async variants
async_database_url = settings.DATABASE_URL

if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite async - use aiosqlite driver
    async_database_url = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
    # SQLite-specific configuration for development
    engine = create_async_engine(
        async_database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG
    )
elif settings.DATABASE_URL.startswith("postgresql+psycopg2://"):
    # PostgreSQL async - use asyncpg driver
    async_database_url = settings.DATABASE_URL.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    # PostgreSQL configuration for production
    engine = create_async_engine(
        async_database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG
    )
else:
    # Fallback - assume it's already async compatible
    engine = create_async_engine(
        async_database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG
    )

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async dependency to get database session.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            items = result.scalars().all()
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables asynchronously.
    Call this at application startup.
    """
    from app.models.user import Base as UserBase
    from app.models.ticket import Base as TicketBase

    # Setup slow query logging for performance monitoring
    setup_slow_query_logging(engine)

    # Create all tables asynchronously
    async with engine.begin() as conn:
        await conn.run_sync(UserBase.metadata.create_all)
        await conn.run_sync(TicketBase.metadata.create_all)


async def close_db():
    """
    Close database connections asynchronously.
    Call this at application shutdown.
    """
    await engine.dispose()
