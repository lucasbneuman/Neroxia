#!/usr/bin/env python
"""Script to verify Supabase connection and get correct database URL."""

import os
import sys
from pathlib import Path
import asyncio
import socket

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
env_path = project_root / '.env'
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")

print("=" * 80)
print("SUPABASE CONNECTION DIAGNOSTICS")
print("=" * 80)
print()

# Step 1: Check environment variables
print("1. Environment Variables Check:")
print(f"   SUPABASE_URL: {SUPABASE_URL}")
print(f"   SUPABASE_SERVICE_KEY: {'*' * 20 if SUPABASE_SERVICE_KEY else 'NOT SET'}")
print(f"   SUPABASE_DATABASE_URL: {SUPABASE_DATABASE_URL}")
print()

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("[ERROR] Missing Supabase credentials in .env file")
    sys.exit(1)

# Step 2: Test Supabase API connection
print("2. Testing Supabase API Connection:")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    # Try to query auth users to verify connection
    response = supabase.auth.admin.list_users()
    print(f"   ✅ Supabase API is reachable")
    print(f"   ✅ Authentication working")
    print(f"   ✅ Found {len(response) if response else 0} users in auth system")
except Exception as e:
    print(f"   ❌ Failed to connect to Supabase API: {e}")
    sys.exit(1)

print()

# Step 3: Extract database hostname from SUPABASE_DATABASE_URL
print("3. Database URL Analysis:")
if SUPABASE_DATABASE_URL:
    # Parse the database URL
    import re
    # Format: postgresql+asyncpg://user:password@hostname:port/database
    match = re.search(r'@([^:]+):(\d+)', SUPABASE_DATABASE_URL)
    if match:
        db_hostname = match.group(1)
        db_port = match.group(2)
        print(f"   Hostname: {db_hostname}")
        print(f"   Port: {db_port}")

        # Step 4: Test DNS resolution
        print()
        print("4. DNS Resolution Test:")
        try:
            ip_address = socket.gethostbyname(db_hostname)
            print(f"   ✅ Hostname resolves to: {ip_address}")
        except socket.gaierror as e:
            print(f"   ❌ DNS resolution failed: {e}")
            print()
            print("   This is the ROOT CAUSE of the 500 errors!")
            print()
            print("   SOLUTION:")
            print("   The database hostname cannot be resolved. You need to get the")
            print("   correct connection string from your Supabase dashboard:")
            print()
            print("   1. Go to: https://supabase.com/dashboard")
            print("   2. Select your project")
            print("   3. Go to: Settings → Database")
            print("   4. Look for 'Connection string' section")
            print("   5. Select 'URI' format")
            print("   6. Copy the connection string")
            print()
            print("   Expected formats:")
            print("   - Direct: postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres")
            print("   - Pooler: postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres")
            print()
            print("   Then update your .env file:")
            print(f"   SUPABASE_DATABASE_URL=postgresql+asyncpg://[CONNECTION_STRING_FROM_DASHBOARD]")
            print()
            sys.exit(1)
    else:
        print("   ❌ Could not parse database URL")
else:
    print("   ❌ SUPABASE_DATABASE_URL not set")

print()

# Step 5: Test database connection
print("5. Testing Database Connection:")
try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    # Create engine
    engine = create_async_engine(SUPABASE_DATABASE_URL, echo=False)

    async def test_connection():
        async with engine.connect() as conn:
            result = await conn.execute("SELECT version()")
            version = result.scalar()
            return version

    # Test connection
    loop = asyncio.get_event_loop()
    version = loop.run_until_complete(test_connection())

    print(f"   ✅ Database connection successful!")
    print(f"   ✅ PostgreSQL version: {version}")

    # Close engine
    loop.run_until_complete(engine.dispose())

except Exception as e:
    print(f"   ❌ Database connection failed: {e}")
    print()
    print("   This confirms the database URL is incorrect.")
    print("   Please follow the steps above to get the correct connection string.")
    sys.exit(1)

print()
print("=" * 80)
print("✅ ALL CHECKS PASSED - Supabase connection is healthy!")
print("=" * 80)
