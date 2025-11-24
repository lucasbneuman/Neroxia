#!/usr/bin/env python
"""Simple script to test Supabase connection."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
env_path = project_root / '.env'
load_dotenv(env_path)

print("=" * 80)
print("SUPABASE CONNECTION TEST")
print("=" * 80)
print()

# Get credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")

# Step 1: Check environment variables
print("1. Checking environment variables...")
print(f"   SUPABASE_URL: {SUPABASE_URL}")
print(f"   SUPABASE_SERVICE_KEY: {'SET (' + str(len(SUPABASE_SERVICE_KEY)) + ' chars)' if SUPABASE_SERVICE_KEY else 'NOT SET'}")
print(f"   SUPABASE_DATABASE_URL: {SUPABASE_DATABASE_URL if SUPABASE_DATABASE_URL else 'NOT SET'}")
print()

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY or not SUPABASE_DATABASE_URL:
    print("[ERROR] Missing required environment variables!")
    print()
    print("Please check your .env file and make sure you have:")
    print("  - SUPABASE_URL")
    print("  - SUPABASE_SERVICE_KEY")
    print("  - SUPABASE_DATABASE_URL")
    print()
    print("See SUPABASE_FIX_GUIDE.md for instructions.")
    sys.exit(1)

# Step 2: Test Supabase API
print("2. Testing Supabase API connection...")
try:
    from supabase import create_client, Client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    # Simple test - try to get project info through auth
    result = supabase.auth.admin.list_users(page=1, per_page=1)
    print(f"   [OK] Supabase API is reachable")
    print(f"   [OK] Service key is valid")
except Exception as e:
    print(f"   [FAILED] Supabase API error: {e}")
    print()
    print("   Possible causes:")
    print("   1. Invalid SUPABASE_SERVICE_KEY")
    print("   2. Invalid SUPABASE_URL")
    print("   3. Supabase project doesn't exist or is paused")
    print()
    print("   Please check SUPABASE_FIX_GUIDE.md for instructions.")
    sys.exit(1)

print()

# Step 3: Test database connection
print("3. Testing database connection...")
try:
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    # Create engine
    engine = create_async_engine(SUPABASE_DATABASE_URL, echo=False)

    async def test_db():
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            return result.scalar()

    # Run test
    loop = asyncio.get_event_loop()
    test_result = loop.run_until_complete(test_db())

    if test_result == 1:
        print(f"   [OK] Database connection successful")
        print(f"   [OK] Can execute queries")

    # Cleanup
    loop.run_until_complete(engine.dispose())

except Exception as e:
    print(f"   [FAILED] Database connection error: {e}")
    print()
    print("   Possible causes:")
    print("   1. Invalid database password in SUPABASE_DATABASE_URL")
    print("   2. Wrong database hostname")
    print("   3. Missing 'postgresql+asyncpg://' prefix")
    print("   4. Database is not accessible")
    print()
    print("   Please check SUPABASE_FIX_GUIDE.md for instructions.")
    sys.exit(1)

print()

# Step 4: Verify database tables
print("4. Checking database tables...")
try:
    async def check_tables():
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            return tables

    loop = asyncio.get_event_loop()
    tables = loop.run_until_complete(check_tables())

    print(f"   [OK] Found {len(tables)} tables:")
    for table in tables:
        print(f"       - {table}")

    # Cleanup
    loop.run_until_complete(engine.dispose())

except Exception as e:
    print(f"   [WARNING] Could not list tables: {e}")
    print("   This might be okay if tables haven't been created yet.")

print()
print("=" * 80)
print("[SUCCESS] All Supabase connection tests passed!")
print("=" * 80)
print()
print("Next steps:")
print("1. Restart your API server")
print("2. Test the /config/ endpoint in the frontend")
print("3. Try the test chat")
print()
