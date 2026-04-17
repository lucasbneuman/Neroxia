"""Setup admin user for development."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.supabase import create_user


async def main():
    """Create admin user with confirmed email."""
    print("=" * 60)
    print("SETTING UP ADMIN USER FOR DEVELOPMENT")
    print("=" * 60)

    # Try multiple email formats
    test_emails = [
        ("admin@salesbot.dev", "admin123"),
        ("admin.bot@gmail.com", "admin123"),
        ("salesbot.admin@gmail.com", "admin123"),
    ]

    for email, password in test_emails:
        print(f"\nTrying to create: {email}")

        user = await create_user(
            email=email,
            password=password,
            metadata={"name": "Admin User", "role": "admin"}
        )

        if user:
            print(f"\n✓ SUCCESS! Admin user created:")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
            print(f"  User ID: {user['id']}")
            print(f"\n  Email is auto-confirmed for development.")
            print(f"\n  Update your frontend to use these credentials!")
            return

        print(f"  × Failed (user may already exist)")

    print("\n" + "=" * 60)
    print("All attempts failed. Users may already exist.")
    print("Try logging in with:")
    print("  Email: admin.salesbot@gmail.com")
    print("  Password: admin123")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
