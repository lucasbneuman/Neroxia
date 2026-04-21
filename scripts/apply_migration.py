"""Apply SQL migration script."""

import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from packages.database.neroxia_database import AsyncSessionLocal

async def apply_migration():
    """Apply the subscription tables migration."""
    migration_file = project_root / "packages" / "database" / "migrations" / "004_add_subscription_tables.sql"
    
    if not migration_file.exists():
        print(f"Error: Migration file not found at {migration_file}")
        return

    print(f"Reading migration file: {migration_file.name}")
    with open(migration_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    print("Applying migration...")
    async with AsyncSessionLocal() as session:
        try:
            # Split content into statements
            # Simple split by semicolon might break if semicolon is in strings
            # But for this specific migration file it should be fine as long as we handle newlines
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            
            for statement in statements:
                # Skip empty statements
                if not statement.strip():
                    continue
                    
                print(f"Executing: {statement[:50]}...")
                await session.execute(text(statement))
            
            await session.commit()
            print("✅ Migration applied successfully!")
        except Exception as e:
            await session.rollback()
            print(f"❌ Error applying migration: {str(e)}")
            raise

if __name__ == "__main__":
    asyncio.run(apply_migration())
