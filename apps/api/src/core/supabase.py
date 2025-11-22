"""Supabase client configuration and authentication helpers."""

import os
from typing import Optional, Dict, Any
from supabase import create_client, Client

# Load Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError(
        "Missing required Supabase environment variables. "
        "Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file."
    )

# Create Supabase clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Admin client for server-side operations (requires service key)
supabase_admin: Optional[Client] = None
if SUPABASE_SERVICE_KEY:
    supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


async def verify_supabase_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Supabase JWT token and return user data.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User data dict if valid, None if invalid
    """
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
    if not supabase_admin:
        raise ValueError("Admin client not configured. Set SUPABASE_SERVICE_KEY.")
    
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
    if not supabase_admin:
        raise ValueError("Admin client not configured. Set SUPABASE_SERVICE_KEY.")
    
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
