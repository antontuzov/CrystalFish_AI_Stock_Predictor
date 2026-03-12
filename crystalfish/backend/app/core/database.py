"""
Database configuration for CrystalFish
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

from app.core.config import get_settings

settings = get_settings()

# Async engine for FastAPI
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_size=20,
    max_overflow=0,
)

# Sync engine for Celery tasks
sync_engine = create_engine(
    settings.DATABASE_URL_SYNC,
    echo=settings.DEBUG,
    future=True,
    pool_size=10,
    max_overflow=0,
)

# Session makers
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

SyncSessionLocal = sessionmaker(
    sync_engine,
    expire_on_commit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_db():
    """Get sync database session for Celery"""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)