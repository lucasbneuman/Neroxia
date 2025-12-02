"""User management router - profiles, settings, and account management."""

from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, EmailStr

from ..core.supabase import supabase
from ..routers.auth import get_current_user
from packages.database.whatsapp_bot_database import AsyncSessionLocal
from packages.database.whatsapp_bot_database.subscription_crud import (
    create_user_profile,
    delete_user_profile,
    get_user_profile,
    update_user_profile,
)

router = APIRouter(prefix="/users", tags=["users"])


# ============================================================================
# Pydantic Models
# ============================================================================


class UserProfileResponse(BaseModel):
    """User profile response model."""

    id: int
    auth_user_id: str
    company_name: Optional[str]
    phone: Optional[str]
    timezone: str
    language: str
    avatar_url: Optional[str]
    role: str
    onboarding_completed: bool
    onboarding_step: int
    preferences: Optional[dict]
    created_at: str
    updated_at: str


class UpdateProfileRequest(BaseModel):
    """Update profile request model."""

    company_name: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    preferences: Optional[dict] = None


class UpdatePasswordRequest(BaseModel):
    """Update password request model."""

    current_password: str
    new_password: str


class UpdateSettingsRequest(BaseModel):
    """Update user settings/preferences."""

    preferences: dict


# ============================================================================
# Helper Functions
# ============================================================================


async def get_db():
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


# ============================================================================
# Endpoints
# ============================================================================


@router.get("/profile", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get current user's profile.

    Returns extended profile information including company, preferences, etc.
    """
    user_id = current_user["id"]

    profile = await get_user_profile(db, user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    return {
        "id": profile.id,
        "auth_user_id": profile.auth_user_id,
        "company_name": profile.company_name,
        "phone": profile.phone,
        "timezone": profile.timezone,
        "language": profile.language,
        "avatar_url": profile.avatar_url,
        "role": profile.role,
        "onboarding_completed": profile.onboarding_completed,
        "onboarding_step": profile.onboarding_step,
        "preferences": profile.preferences or {},
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
    }


@router.put("/profile", response_model=UserProfileResponse)
async def update_current_user_profile(
    profile_data: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Update current user's profile.

    Allows updating company name, phone, timezone, language, and preferences.
    """
    user_id = current_user["id"]

    # Filter out None values
    update_data = {k: v for k, v in profile_data.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    profile = await update_user_profile(db, user_id, **update_data)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    return {
        "id": profile.id,
        "auth_user_id": profile.auth_user_id,
        "company_name": profile.company_name,
        "phone": profile.phone,
        "timezone": profile.timezone,
        "language": profile.language,
        "avatar_url": profile.avatar_url,
        "role": profile.role,
        "onboarding_completed": profile.onboarding_completed,
        "onboarding_step": profile.onboarding_step,
        "preferences": profile.preferences or {},
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
    }


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Upload user avatar image.

    Uploads to Supabase Storage and updates profile with avatar URL.
    """
    user_id = current_user["id"]

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    # Validate file size (max 5MB)
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB",
        )

    try:
        # Upload to Supabase Storage
        file_path = f"avatars/{user_id}/{file.filename}"

        storage_response = supabase.storage.from_("user-avatars").upload(
            file_path, file_content, {"content-type": file.content_type}
        )

        # Get public URL
        avatar_url = supabase.storage.from_("user-avatars").get_public_url(file_path)

        # Update profile
        profile = await update_user_profile(db, user_id, avatar_url=avatar_url)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found",
            )

        return {
            "status": "success",
            "avatar_url": avatar_url,
            "message": "Avatar uploaded successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload avatar: {str(e)}",
        )


@router.put("/password")
async def change_password(
    password_data: UpdatePasswordRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Change user password.

    Requires current password for verification.
    """
    try:
        # Verify current password by attempting to sign in
        email = current_user["email"]
        verify_response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password_data.current_password}
        )

        if not verify_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect",
            )

        # Update password
        supabase.auth.update_user({"password": password_data.new_password})

        return {
            "status": "success",
            "message": "Password updated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update password: {str(e)}",
        )


@router.get("/settings")
async def get_user_settings(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Get user settings/preferences.

    Returns user preferences like notifications, theme, etc.
    """
    user_id = current_user["id"]

    profile = await get_user_profile(db, user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    return {
        "preferences": profile.preferences or {},
        "timezone": profile.timezone,
        "language": profile.language,
    }


@router.put("/settings")
async def update_user_settings(
    settings_data: UpdateSettingsRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Update user settings/preferences.

    Updates preferences like notifications, theme, date format, etc.
    """
    user_id = current_user["id"]

    profile = await update_user_profile(db, user_id, preferences=settings_data.preferences)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    return {
        "status": "success",
        "message": "Settings updated successfully",
        "preferences": profile.preferences,
    }


@router.delete("/account")
async def delete_account(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Delete user account.

    WARNING: This action is irreversible and will delete all user data.
    """
    user_id = current_user["id"]

    try:
        # Delete user profile
        await delete_user_profile(db, user_id)

        # Delete Supabase auth user
        # Note: This requires service role key
        supabase.auth.admin.delete_user(user_id)

        return {
            "status": "success",
            "message": "Account deleted successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}",
        )


@router.post("/onboarding/complete")
async def complete_onboarding(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Mark onboarding as completed.

    Called when user finishes the onboarding wizard.
    """
    user_id = current_user["id"]

    profile = await update_user_profile(
        db, user_id, onboarding_completed=True, onboarding_step=999
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    return {
        "status": "success",
        "message": "Onboarding completed",
    }


@router.put("/onboarding/step")
async def update_onboarding_step(
    step: int,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Update current onboarding step.

    Tracks user progress through onboarding wizard.
    """
    user_id = current_user["id"]

    profile = await update_user_profile(db, user_id, onboarding_step=step)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    return {
        "status": "success",
        "current_step": step,
    }
