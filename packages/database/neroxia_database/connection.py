"""Database connection configuration for PostgreSQL/Supabase."""

import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env in project root (4 levels up from this file)
env_path = Path(__file__).parent.parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback: try loading from current directory
    load_dotenv()

# Read database URL from environment
# For Supabase: postgresql+asyncpg://user:pass@host:port/database
# For local dev: postgresql+asyncpg://localhost:5432/neroxia
DATABASE_URL = os.getenv(
    "SUPABASE_DATABASE_URL",
    os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost:5432/neroxia")
)

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine with connection pooling where the driver supports it.
engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,  # Verify connections before using
}

if not DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update(
        {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 3600,  # Recycle connections after 1 hour
        }
    )

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
