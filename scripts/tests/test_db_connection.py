"""Quick test script to verify Supabase connection and tables."""

import asyncio
import sys
from pathlib import Path

# Add packages to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "packages" / "database"))

from whatsapp_bot_database.connection import AsyncSessionLocal
from whatsapp_bot_database import crud


async def test_connection():
    """Test database connection and verify tables."""
    print("=" * 60)
    print("Testing Supabase Connection")
    print("=" * 60)
    print()
    
    try:
        async with AsyncSessionLocal() as db:
            # Test 1: Get all configs
            print("✓ Test 1: Loading configurations...")
            configs = await crud.get_all_configs(db)
            print(f"  Found {len(configs)} configurations")
            
            # Test 2: Get a specific config
            print("\n✓ Test 2: Getting system_prompt...")
            system_prompt = await crud.get_config(db, "system_prompt")
            if system_prompt:
                print(f"  System prompt: {system_prompt[:50]}...")
            
            # Test 3: Count users
            print("\n✓ Test 3: Counting users...")
            users = await crud.get_all_active_users(db, limit=10)
            print(f"  Found {len(users)} users")
            
            print("\n" + "=" * 60)
            print("✅ All tests passed! Database is working correctly.")
            print("=" * 60)
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
