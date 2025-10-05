"""
Database configuration and session management
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from backend.core.config import settings

# For SQLite (simpler for local development)
if "sqlite" in settings.DATABASE_URL:
    # Async SQLite - ensure it has the right driver
    if "aiosqlite" not in settings.DATABASE_URL:
        db_url = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
    else:
        db_url = settings.DATABASE_URL

    engine = create_async_engine(
        db_url,
        echo=False,
        future=True
    )
    # Sync engine for migrations
    sync_url = db_url.replace("+aiosqlite", "")
    sync_engine = create_engine(
        sync_url,
        echo=False
    )
else:
    # PostgreSQL
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
        pool_size=10,
        max_overflow=20
    )
    sync_engine = create_engine(
        settings.DATABASE_URL.replace("+asyncpg", ""),
        echo=False
    )

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

SessionLocal = sessionmaker(
    sync_engine,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Dependency to get database session
async def get_db():
    """Get database session for dependency injection"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_db():
    """Get sync database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()