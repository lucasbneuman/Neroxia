"""Create test user for development."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.supabase import create_user


async def main():
    """Create admin test user."""
    print("Creating test user...")

    user = await create_user(
        email="admin@example.com",
        password="admin",
        metadata={"name": "Admin User"}
    )

    if user:
        print(f"✅ Test user created successfully!")
        print(f"   Email: admin@example.com")
        print(f"   Password: admin")
        print(f"   User ID: {user['id']}")
    else:
        print("❌ Failed to create test user")
        print("   User may already exist or there was an error")


if __name__ == "__main__":
    asyncio.run(main())
