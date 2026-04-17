#!/usr/bin/env python
"""Script to check Supabase authentication status and users."""

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

print("[INFO] Checking Supabase configuration...")
print(f"[INFO] Loading .env from: {env_path}")
print()

# Check environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_ANON_KEY: {SUPABASE_ANON_KEY[:20]}..." if SUPABASE_ANON_KEY else "SUPABASE_ANON_KEY: Not set")
print(f"SUPABASE_SERVICE_KEY: {SUPABASE_SERVICE_KEY[:20]}..." if SUPABASE_SERVICE_KEY else "SUPABASE_SERVICE_KEY: Not set")
print()

# Try to import and initialize Supabase
try:
    from supabase import create_client, Client
    print("[OK] Supabase package is installed")
except ImportError as e:
    print(f"[ERROR] Supabase package not installed: {e}")
    sys.exit(1)

# Check if credentials are set
if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("[ERROR] Supabase credentials not configured in .env")
    sys.exit(1)

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("[OK] Supabase client initialized")
except Exception as e:
    print(f"[ERROR] Failed to initialize Supabase client: {e}")
    sys.exit(1)

# Check if we can connect to Supabase
try:
    # Try to get the current session (should be None if not logged in)
    response = supabase.auth.get_session()
    print(f"[OK] Connected to Supabase successfully")
    print(f"[INFO] Current session: {response}")
except Exception as e:
    print(f"[ERROR] Failed to connect to Supabase: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("SUPABASE AUTH STATUS")
print("=" * 60)
print()

# Try to sign in with admin credentials to test
print("[TEST] Attempting to sign in with admin@test.com / admin123...")
try:
    response = supabase.auth.sign_in_with_password({
        "email": "admin@test.com",
        "password": "admin123"
    })

    if response.session and response.user:
        print(f"[OK] Login successful!")
        print(f"  User ID: {response.user.id}")
        print(f"  Email: {response.user.email}")
        print(f"  Created at: {response.user.created_at}")
    else:
        print("[FAIL] Login failed - no session or user returned")
except Exception as e:
    print(f"[FAIL] Login failed: {e}")
    print()
    print("[INFO] This might mean:")
    print("  1. User doesn't exist - need to create it")
    print("  2. Wrong password")
    print("  3. Email not confirmed")

print()

# If service key is available, try to list users
if SUPABASE_SERVICE_KEY:
    print("[INFO] Service key available - attempting to list users...")
    try:
        admin_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

        # Note: The Supabase Python client doesn't have direct admin API access
        # We would need to use the REST API directly or the GoTrue admin endpoints
        print("[INFO] Admin client initialized")
        print("[INFO] To list users, you need to use Supabase Dashboard or REST API")
        print(f"[INFO] Dashboard URL: {SUPABASE_URL.replace('https://', 'https://supabase.com/dashboard/project/')}")
    except Exception as e:
        print(f"[ERROR] Failed to initialize admin client: {e}")
else:
    print("[INFO] No service key - cannot access admin functions")

print()
print("=" * 60)
print("RECOMMENDATIONS")
print("=" * 60)
print()
print("Option 1: Create user via Supabase Dashboard")
print("  1. Go to: https://supabase.com/dashboard")
print("  2. Select your project")
print("  3. Go to Authentication > Users")
print("  4. Click 'Add User'")
print("  5. Email: admin@test.com")
print("  6. Password: admin123")
print("  7. Auto Confirm User: YES")
print()
print("Option 2: Create user via signup endpoint")
print("  curl -X POST http://localhost:8000/auth/signup \\")
print('    -H "Content-Type: application/json" \\')
print('    -d \'{"email": "admin@test.com", "password": "admin123", "name": "Admin"}\'')
print()
print("Option 3: Update frontend to accept email instead of username")
print("  - Update login form to have email field")
print("  - Update validation to check for email format")
