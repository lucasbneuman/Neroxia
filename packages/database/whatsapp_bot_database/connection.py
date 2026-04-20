"""Database connection configuration for PostgreSQL/Supabase."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
# Look for .env in project root (4 levels up from this file)
env_path = Path(__file__).parent.parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback: try loading from current directory
    load_dotenv()

def _normalize_async_database_url(database_url: str) -> str:
    """Ensure SQLAlchemy gets an async-compatible URL."""
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    return database_url


def _load_database_url() -> str:
    """Load database URL with safe test/dev defaults."""
    raw_url = os.getenv(
        "SUPABASE_DATABASE_URL",
        os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/sales_bot.db"),
    )
    return _normalize_async_database_url(raw_url)


DATABASE_URL = _load_database_url()

engine_kwargs = {"echo": False}
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    engine_kwargs.update(
        {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }
    )

# Create async engine with connection pooling
engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    """Dependency for getting async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
