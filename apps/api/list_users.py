"""List all Supabase Auth users."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.supabase import supabase_admin


def main():
    """List all users in Supabase Auth."""
    if not supabase_admin:
        print("Error: Supabase admin client not available")
        return

    try:
        # List users using admin client
        response = supabase_admin.auth.admin.list_users()

        if hasattr(response, 'users') and response.users:
            print(f"\nFound {len(response.users)} users:\n")
            for user in response.users:
                print(f"  Email: {user.email}")
                print(f"  ID: {user.id}")
                print(f"  Created: {user.created_at}")
                print(f"  Email Confirmed: {user.email_confirmed_at is not None}")
                print(f"  Metadata: {user.user_metadata}")
                print()
        else:
            print("No users found")

    except Exception as e:
        print(f"Error listing users: {e}")


if __name__ == "__main__":
    main()
