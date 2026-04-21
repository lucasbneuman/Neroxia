"""Authentication router using Supabase Auth."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, EmailStr

from ..core.supabase import supabase, verify_supabase_token

router = APIRouter(prefix="/auth", tags=["auth"])


# Pydantic models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    user_metadata: dict
    created_at: str


# Dependency to get current user from token
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Extract and verify user from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token with Supabase
    user = await verify_supabase_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Login with email and password using Supabase Auth.
    
    Returns access token, refresh token, and user data.
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password,
        })
        
        if not response.session or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "user_metadata": response.user.user_metadata or {},
                "created_at": response.user.created_at,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        )


@router.post("/signup", response_model=TokenResponse)
async def signup(credentials: SignupRequest):
    """
    Sign up a new user with email and password.
    
    Automatically creates:
    - Supabase Auth user
    - User profile
    - Free trial subscription
    
    Returns access token, refresh token, and user data.
    """
    try:
        # Prepare user metadata
        user_metadata = {}
        if credentials.name:
            user_metadata["name"] = credentials.name
        
        # Create Supabase Auth user
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password,
            "options": {
                "data": user_metadata
            }
        })
        
        if not response.session or not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signup failed. Email may already be registered.",
            )
        
        user_id = response.user.id
        
        # Import database dependencies
        from ..database import get_db
        from neroxia_database.subscription_crud import (
            create_user_profile,
            create_user_subscription,
            get_subscription_plan_by_name,
        )
        
        # Create user profile and subscription in database
        async with get_db() as db:
            # Create user profile
            await create_user_profile(
                db=db,
                auth_user_id=user_id,
                company_name=None,
                phone=None,
                timezone="UTC",
                language="es",
                role="owner",
            )
            
            # Get free trial plan
            trial_plan = await get_subscription_plan_by_name(db, "free_trial")
            if trial_plan:
                # Create trial subscription
                await create_user_subscription(
                    db=db,
                    user_id=user_id,
                    plan_id=trial_plan.id,
                    status="trial",
                    trial_days=14,
                )
        
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "user_metadata": response.user.user_metadata or {},
                "created_at": response.user.created_at,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {str(e)}",
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user by invalidating the session.
    """
    try:
        supabase.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest):
    """
    Refresh access token using refresh token.
    """
    try:
        response = supabase.auth.refresh_session(request.refresh_token)
        
        if not response.session or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "user_metadata": response.user.user_metadata or {},
                "created_at": response.user.created_at,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    """
    return current_user

