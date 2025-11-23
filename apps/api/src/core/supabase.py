"""Supabase client configuration and authentication helpers."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env in project root (3 levels up from this file)
env_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback: try loading from current directory
    load_dotenv()

# Try to import Supabase (optional dependency)
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    print("Warning: supabase package not installed. Supabase authentication disabled.")
    SUPABASE_AVAILABLE = False
    Client = None

# Load Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Create Supabase clients only if available and configured
supabase: Optional[Client] = None
supabase_admin: Optional[Client] = None

if SUPABASE_AVAILABLE:
    if SUPABASE_URL and SUPABASE_ANON_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Admin client for server-side operations (requires service key)
        if SUPABASE_SERVICE_KEY:
            supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    else:
        print("Warning: Supabase credentials not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY in .env")


async def verify_supabase_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Supabase JWT token and return user data.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User data dict if valid, None if invalid
    """
    if not SUPABASE_AVAILABLE or not supabase:
        return None
        
    try:
        # Get user from token
        response = supabase.auth.get_user(token)
        
        if response and response.user:
            return {
                "id": response.user.id,
                "email": response.user.email,
                "user_metadata": response.user.user_metadata,
                "created_at": response.user.created_at,
            }
        return None
    except Exception as e:
        print(f"Token verification error: {e}")
        return None


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get user by ID using admin client.
    
    Args:
        user_id: Supabase user ID
        
    Returns:
        User data dict if found, None otherwise
    """
    if not SUPABASE_AVAILABLE or not supabase_admin:
        raise ValueError("Supabase admin client not available. Install supabase package and set SUPABASE_SERVICE_KEY.")
    
    try:
        response = supabase_admin.auth.admin.get_user_by_id(user_id)
        if response and response.user:
            return {
                "id": response.user.id,
                "email": response.user.email,
                "user_metadata": response.user.user_metadata,
                "created_at": response.user.created_at,
            }
        return None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None


async def create_user(email: str, password: str, metadata: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
    """
    Create a new user using admin client.
    
    Args:
        email: User email
        password: User password
        metadata: Optional user metadata
        
    Returns:
        Created user data dict if successful, None otherwise
    """
    if not SUPABASE_AVAILABLE or not supabase_admin:
        raise ValueError("Supabase admin client not available. Install supabase package and set SUPABASE_SERVICE_KEY.")
    
    try:
        response = supabase_admin.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": metadata or {}
        })
        
        if response and response.user:
            return {
                "id": response.user.id,
                "email": response.user.email,
                "user_metadata": response.user.user_metadata,
            }
        return None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None
