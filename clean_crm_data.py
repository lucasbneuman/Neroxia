import asyncio
import os
from dotenv import load_dotenv

# Load environment variables (for DB URL)
load_dotenv()

from neroxia_database.connection import get_db
from sqlalchemy import text

async def clean_data():
    print("Cleaning CRM data...")
    async for session in get_db():
        try:
            # Delete in order of dependencies
            print("Deleting notes...")
            await session.execute(text("DELETE FROM notes"))
            
            print("Deleting user_tags...")
            await session.execute(text("DELETE FROM user_tags"))
            
            print("Deleting deals...")
            await session.execute(text("DELETE FROM deals"))
            
            print("Deleting tags...")
            await session.execute(text("DELETE FROM tags"))
            
            await session.commit()
            print("CRM data cleaned successfully.")
        except Exception as e:
            print(f"Error cleaning data: {e}")
            await session.rollback()
        break

if __name__ == "__main__":
    asyncio.run(clean_data())
