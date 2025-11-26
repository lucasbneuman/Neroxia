"""
Script to clear all test conversation data from the database.
This will delete all users, messages, and related data.
Use with caution - this is irreversible!
"""

import asyncio
import sys
from pathlib import Path

# Add packages to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "packages" / "database" / "src"))
sys.path.insert(0, str(project_root / "packages" / "shared" / "src"))

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from whatsapp_bot_database.models import User, Message
from whatsapp_bot_shared import get_logger
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


async def clear_all_test_data():
    """Clear all users and messages from the database."""
    
    # Get database URL from environment
    database_url = os.getenv("SUPABASE_DATABASE_URL")
    if not database_url:
        logger.error("SUPABASE_DATABASE_URL not found in environment variables")
        return False
    
    # Create async engine
    engine = create_async_engine(database_url, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    try:
        async with async_session() as session:
            # Delete all messages first (foreign key constraint)
            logger.info("Deleting all messages...")
            await session.execute(delete(Message))
            
            # Delete all users
            logger.info("Deleting all users...")
            await session.execute(delete(User))
            
            # Commit the transaction
            await session.commit()
            
            logger.info("✅ Successfully cleared all test data!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error clearing test data: {e}", exc_info=True)
        return False
    finally:
        await engine.dispose()


async def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("⚠️  WARNING: This will delete ALL users and messages!")
    print("="*60)
    
    # Ask for confirmation
    response = input("\nAre you sure you want to continue? (yes/no): ")
    
    if response.lower() != "yes":
        print("❌ Operation cancelled.")
        return
    
    print("\n🗑️  Clearing all test data...\n")
    success = await clear_all_test_data()
    
    if success:
        print("\n✅ All test data has been cleared successfully!")
        print("You can now start fresh with new test conversations.")
    else:
        print("\n❌ Failed to clear test data. Check the logs above.")


if __name__ == "__main__":
    asyncio.run(main())
