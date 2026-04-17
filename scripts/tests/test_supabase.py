"""Simple test to check Supabase connection."""
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

async def test_connection():
    """Test raw connection to Supabase."""
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    
    db_url = os.getenv('SUPABASE_DATABASE_URL')
    print(f"Testing connection to: {db_url[:50]}...")
    
    try:
        engine = create_async_engine(db_url, echo=True)
        
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Connection successful!")
            print(f"Result: {result.scalar()}")
            
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
