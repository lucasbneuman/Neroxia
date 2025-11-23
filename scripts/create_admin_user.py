#!/usr/bin/env python
"""Script to create admin user in Supabase."""

import os
import sys
from pathlib import Path

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

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("[ERROR] SUPABASE_URL or SUPABASE_SERVICE_KEY not set in .env")
    sys.exit(1)

# Create admin client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("=" * 60)
print("CREATING ADMIN USER IN SUPABASE")
print("=" * 60)
print()

# User credentials
email = input("Enter email (default: admin@example.com): ").strip() or "admin@example.com"
password = input("Enter password (default: admin123): ").strip() or "admin123"
name = input("Enter name (default: Admin User): ").strip() or "Admin User"

print()
print(f"Creating user with:")
print(f"  Email: {email}")
print(f"  Password: {'*' * len(password)}")
print(f"  Name: {name}")
print()

try:
    # Create user using admin API
    response = supabase.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True,  # Auto-confirm the email
        "user_metadata": {
            "name": name
        }
    })

    if response and response.user:
        print("[SUCCESS] User created successfully!")
        print(f"  User ID: {response.user.id}")
        print(f"  Email: {response.user.email}")
        print(f"  Email Confirmed: {response.user.email_confirmed_at is not None}")
        print()
        print("You can now login with:")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print()
        print("Go to: http://localhost:3000/login")
    else:
        print("[ERROR] Failed to create user - no user data returned")

except Exception as e:
    print(f"[ERROR] Failed to create user: {e}")
    print()
    print("This might mean:")
    print("  1. User already exists with this email")
    print("  2. Invalid Supabase credentials")
    print("  3. Insufficient permissions")
    sys.exit(1)
