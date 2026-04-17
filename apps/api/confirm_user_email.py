"""Confirm email for existing Supabase users."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.supabase import supabase_admin


def main():
    """Confirm email for admin@example.com."""
    if not supabase_admin:
        print("Error: Supabase admin client not available")
        return

    email = "admin@example.com"
    print(f"Confirming email for {email}...")

    try:
        # List all users to find the one we want
        response = supabase_admin.auth.admin.list_users()

        if not hasattr(response, 'users') or not response.users:
            print("No users found in database")
            return

        # Find the target user
        target_user = None
        for user in response.users:
            if user.email == email:
                target_user = user
                break

        if not target_user:
            print(f"User {email} not found")
            print("\nAvailable users:")
            for user in response.users:
                print(f"  - {user.email}")
            return

        # Update user to confirm email and set password
        update_response = supabase_admin.auth.admin.update_user_by_id(
            target_user.id,
            {
                "email_confirm": True,
                "password": "admin123"  # Reset to known password
            }
        )

        if update_response and update_response.user:
            print(f"\nSuccess!")
            print(f"  Email: {email}")
            print(f"  Password: admin123 (updated)")
            print(f"  Email Confirmed: True")
            print(f"\nYou can now login with these credentials.")
        else:
            print("Failed to update user")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
