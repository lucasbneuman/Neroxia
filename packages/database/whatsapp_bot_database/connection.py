"""Database connection configuration for PostgreSQL/Supabase."""

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Read database URL from environment
# For Supabase: postgresql+asyncpg://user:pass@host:port/database
# For local dev: postgresql+asyncpg://localhost:5432/sales_bot
DATABASE_URL = os.getenv(
    "SUPABASE_DATABASE_URL",
    os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost:5432/sales_bot")
)

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)

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
