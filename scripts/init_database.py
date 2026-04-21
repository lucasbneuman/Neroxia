"""Initialize database tables for Neroxia."""

import asyncio
import sys
from pathlib import Path

# Add packages to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "packages" / "database"))

from neroxia_database.connection import engine
from neroxia_database.models import Base


async def init_db():
    """Create all database tables."""
    print("Initializing database tables...")
    
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        print("[OK] Database tables created successfully!")
        print("\nCreated tables:")
        print("- users")
        print("- messages")
        print("- follow_ups")
        print("- configs")

    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await engine.dispose()
    
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("Neroxia - Database Initialization")
    print("=" * 50)
    print()
    
    success = asyncio.run(init_db())
    
    if success:
        print("\n[OK] Database initialization complete!")
        sys.exit(0)
    else:
        print("\n[ERROR] Database initialization failed!")
        sys.exit(1)
