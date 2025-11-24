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
    print("Note: Password must be at least 6 characters for Supabase")

    # Try to create the admin user
    user = await create_user(
        email="admin@example.com",
        password="admin123",  # Supabase requires 6+ chars
        metadata={"name": "Admin User"}
    )

    if user:
        print(f"\nSuccess! Test user created successfully!")
        print(f"  Email: admin@example.com")
        print(f"  Password: admin123")
        print(f"  User ID: {user['id']}")
        print(f"\nEmail is auto-confirmed for development.")
    else:
        print("\nFailed to create test user.")
        print("User may already exist. Trying alternative email...")

        # Try with a unique email
        import time
        timestamp = str(int(time.time()))
        alt_email = f"admin{timestamp}@test.local"

        user = await create_user(
            email=alt_email,
            password="admin123",
            metadata={"name": "Admin User"}
        )

        if user:
            print(f"\nSuccess! Alternative test user created:")
            print(f"  Email: {alt_email}")
            print(f"  Password: admin123")
            print(f"  User ID: {user['id']}")
        else:
            print("\nStill failed. Check Supabase connection and credentials.")


if __name__ == "__main__":
    asyncio.run(main())
