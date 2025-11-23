"""Initialize database tables for the sales bot."""

import asyncio
import sys
from pathlib import Path

# Add packages to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "packages" / "database"))

from whatsapp_bot_database.connection import engine
from whatsapp_bot_database.models import Base


async def init_db():
    """Create all database tables."""
    print("Initializing database tables...")
    
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables created successfully!")
        print("\nCreated tables:")
        print("- users")
        print("- messages")
        print("- follow_ups")
        print("- configs")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await engine.dispose()
    
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("Sales Bot - Database Initialization")
    print("=" * 50)
    print()
    
    success = asyncio.run(init_db())
    
    if success:
        print("\n✅ Database initialization complete!")
        sys.exit(0)
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)
