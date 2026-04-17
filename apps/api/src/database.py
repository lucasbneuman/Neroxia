"""Database session dependency for FastAPI.

This module imports the shared database connection from packages/database.
"""

from whatsapp_bot_database.connection import get_db, engine, AsyncSessionLocal

__all__ = ["get_db", "engine", "AsyncSessionLocal"]
