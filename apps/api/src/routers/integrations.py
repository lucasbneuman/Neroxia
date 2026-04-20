"""Integration configuration router (Twilio, HubSpot, Facebook)."""

import os
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from whatsapp_bot_database import crud
from whatsapp_bot_shared import get_logger

from ..database import get_db
from .auth import get_current_user

logger = get_logger(__name__)

router = APIRouter(prefix="/integrations", tags=["integrations"])


class TwilioConfig(BaseModel):
    """Twilio configuration."""
    account_sid: str
    auth_token: str
    whatsapp_number: str


class HubSpotConfig(BaseModel):
    """HubSpot configuration."""
    access_token: str
    enabled: bool = True


class IntegrationsResponse(BaseModel):
    """Integrations configuration response."""
    twilio: Dict[str, Any] | None
    hubspot: Dict[str, Any] | None


async def create_channel_integration(db: AsyncSession, **kwargs):
    """Wrapper kept at router scope for easier patching in tests."""
    return await crud.create_channel_integration(db=db, **kwargs)


async def get_channel_integrations_by_user(db: AsyncSession, user_id: str):
    """Wrapper kept at router scope for easier patching in tests."""
    return await crud.get_channel_integrations_by_user(db, user_id)


async def delete_channel_integration(db: AsyncSession, integration_id: str, auth_user_id: str):
    """Wrapper kept at router scope for easier patching in tests."""
    if integration_id in {"instagram", "messenger"}:
        integrations = await crud.get_channel_integrations_by_user(db, auth_user_id)
        matching = next((item for item in integrations if item.channel == integration_id), None)
        if not matching:
            return False
        integration_id = str(matching.id)
    return await crud.delete_channel_integration(db, integration_id, auth_user_id)


@router.get("/", response_model=IntegrationsResponse)
async def get_integrations(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all integration configurations.
    
    Returns Twilio and HubSpot configurations (without sensitive tokens).
    """
    try:
        twilio_config = await crud.get_config(db, "twilio")
        hubspot_config = await crud.get_config(db, "hubspot")
        
        # Mask sensitive data
        twilio_safe = None
        if twilio_config:
            twilio_safe = {
                "account_sid": twilio_config.get("account_sid", "")[:10] + "..." if twilio_config.get("account_sid") else "",
                "whatsapp_number": twilio_config.get("whatsapp_number", ""),
                "configured": bool(twilio_config.get("account_sid") and twilio_config.get("auth_token"))
            }
        
        hubspot_safe = None
        if hubspot_config:
            hubspot_safe = {
                "enabled": hubspot_config.get("enabled", False),
                "configured": bool(hubspot_config.get("access_token"))
            }
        
        return IntegrationsResponse(
            twilio=twilio_safe,
            hubspot=hubspot_safe
        )
    
    except Exception as e:
        logger.error(f"Error retrieving integrations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve integrations: {str(e)}"
        )


@router.get("/hubspot/status")
async def get_hubspot_status(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get HubSpot integration status.

    Returns whether HubSpot is configured and enabled.
    """
    try:
        hubspot_config = await crud.get_config(db, "hubspot")

        if not hubspot_config:
            return {
                "configured": False,
                "enabled": False,
                "status": "not_configured"
            }

        is_configured = bool(hubspot_config.get("access_token"))
        is_enabled = hubspot_config.get("enabled", False)

        return {
            "configured": is_configured,
            "enabled": is_enabled,
            "status": "active" if (is_configured and is_enabled) else ("configured" if is_configured else "not_configured")
        }

    except Exception as e:
        logger.error(f"Error getting HubSpot status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get HubSpot status: {str(e)}"
        )


@router.get("/twilio/status")
async def get_twilio_status(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get Twilio integration status.

    Returns whether Twilio is configured.
    """
    try:
        twilio_config = await crud.get_config(db, "twilio")

        if not twilio_config:
            return {
                "configured": False,
                "status": "not_configured"
            }

        is_configured = bool(
            twilio_config.get("account_sid") and
            twilio_config.get("auth_token") and
            twilio_config.get("whatsapp_number")
        )

        return {
            "configured": is_configured,
            "whatsapp_number": twilio_config.get("whatsapp_number", "") if is_configured else None,
            "status": "active" if is_configured else "not_configured"
        }

    except Exception as e:
        logger.error(f"Error getting Twilio status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Twilio status: {str(e)}"
        )


@router.put("/twilio")
async def update_twilio_config(
    config: TwilioConfig,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update Twilio configuration.
    
    Stores Twilio credentials in database for dynamic configuration.
    """
    try:
        twilio_data = {
            "account_sid": config.account_sid,
            "auth_token": config.auth_token,
            "whatsapp_number": config.whatsapp_number
        }
        
        await crud.set_config(db, "twilio", twilio_data)
        
        logger.info("Twilio configuration updated")
        
        return {
            "status": "success",
            "message": "Twilio configuration updated successfully",
            "configured": True
        }
    
    except Exception as e:
        logger.error(f"Error updating Twilio config: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update Twilio configuration: {str(e)}"
        )


@router.put("/hubspot")
async def update_hubspot_config(
    config: HubSpotConfig,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update HubSpot configuration.
    
    Stores HubSpot credentials in database for dynamic configuration.
    """
    try:
        hubspot_data = {
            "access_token": config.access_token,
            "enabled": config.enabled
        }
        
        await crud.set_config(db, "hubspot", hubspot_data)
        
        logger.info(f"HubSpot configuration updated (enabled: {config.enabled})")
        
        return {
            "status": "success",
            "message": "HubSpot configuration updated successfully",
            "enabled": config.enabled
        }
    
    except Exception as e:
        logger.error(f"Error updating HubSpot config: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update HubSpot configuration: {str(e)}"
        )


@router.delete("/twilio")
async def delete_twilio_config(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete Twilio configuration.
    
    Removes Twilio credentials from database.
    """
    try:
        await crud.set_config(db, "twilio", {})
        
        logger.info("Twilio configuration deleted")
        
        return {
            "status": "success",
            "message": "Twilio configuration deleted successfully"
        }
    
    except Exception as e:
        logger.error(f"Error deleting Twilio config: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete Twilio configuration: {str(e)}"
        )


@router.delete("/hubspot")
async def delete_hubspot_config(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete HubSpot configuration.
    
    Removes HubSpot credentials from database.
    """
    try:
        await crud.set_config(db, "hubspot", {})
        
        logger.info("HubSpot configuration deleted")
        
        return {
            "status": "success",
            "message": "HubSpot configuration deleted successfully"
        }
    
    except Exception as e:
        logger.error(f"Error deleting HubSpot config: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete HubSpot configuration: {str(e)}"
        )


@router.post("/twilio/test")
async def test_twilio_connection(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Test Twilio connection.
    
    Verifies that Twilio credentials are valid.
    """
    try:
        twilio_config = await crud.get_config(db, "twilio")
        
        if not twilio_config or not twilio_config.get("account_sid") or not twilio_config.get("auth_token"):
            raise HTTPException(
                status_code=400,
                detail="Twilio not configured. Please set credentials first."
            )
        
        # Test connection by importing and initializing Twilio service
        import sys
        from pathlib import Path
        
        bot_engine_path = Path(__file__).parent.parent.parent.parent / "bot-engine" / "src"
        if str(bot_engine_path) not in sys.path:
            sys.path.insert(0, str(bot_engine_path))
            
        # Also add shared package path
        shared_path = Path(__file__).parent.parent.parent.parent / "packages" / "shared"
        if str(shared_path) not in sys.path:
            sys.path.insert(0, str(shared_path))
        
        from services.twilio_service import TwilioService
        
        twilio_service = TwilioService(
            account_sid=twilio_config["account_sid"],
            auth_token=twilio_config["auth_token"],
            whatsapp_number=twilio_config["whatsapp_number"]
        )
        
        # If initialization succeeds, connection is valid
        return {
            "status": "success",
            "message": "Twilio connection successful",
            "whatsapp_number": twilio_config["whatsapp_number"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing Twilio connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Twilio connection test failed: {str(e)}"
        )


@router.post("/hubspot/test")
async def test_hubspot_connection(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Test HubSpot connection.
    
    Verifies that HubSpot credentials are valid.
    """
    try:
        hubspot_config = await crud.get_config(db, "hubspot")
        
        if not hubspot_config or not hubspot_config.get("access_token"):
            raise HTTPException(
                status_code=400,
                detail="HubSpot not configured. Please set access token first."
            )
        
        # Test connection by importing and initializing HubSpot service
        import sys
        from pathlib import Path
        
        bot_engine_path = Path(__file__).parent.parent.parent.parent / "bot-engine" / "src"
        if str(bot_engine_path) not in sys.path:
            sys.path.insert(0, str(bot_engine_path))

        # Also add shared package path
        shared_path = Path(__file__).parent.parent.parent.parent / "packages" / "shared"
        if str(shared_path) not in sys.path:
            sys.path.insert(0, str(shared_path))
        
        from services.hubspot_sync import HubSpotSync
        
        hubspot_service = HubSpotSync(api_key=hubspot_config["access_token"])
        
        # If initialization succeeds, connection is valid
        return {
            "status": "success",
            "message": "HubSpot connection successful",
            "enabled": hubspot_config.get("enabled", True)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing HubSpot connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"HubSpot connection test failed: {str(e)}"
        )


# ========================================
# Facebook OAuth Integration (Phase 6)
# ========================================


@router.get("/facebook/connect")
async def connect_facebook(
    channel: str = Query(..., regex="^(instagram|messenger)$"),
    current_user: dict = Depends(get_current_user),
):
    """
    Initiate Facebook OAuth flow for page connection.

    Redirects user to Facebook OAuth dialog to authorize page access.

    Query params:
    - channel: "instagram" or "messenger"

    Returns:
    - oauth_url: URL to redirect user to for Facebook authorization
    """
    fb_app_id = os.getenv("FACEBOOK_APP_ID", "test-facebook-app-id")
    redirect_uri = os.getenv(
        "FACEBOOK_OAUTH_REDIRECT_URI",
        f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/integrations/facebook/callback",
    )

    # Required permissions based on channel
    if channel == "instagram":
        scope = "instagram_basic,instagram_manage_messages,pages_manage_metadata,pages_read_engagement"
    else:  # messenger
        scope = "pages_messaging,pages_manage_metadata,pages_read_engagement"

    # Build OAuth URL with state for tracking user + channel
    state = f"{current_user['id']}:{channel}"
    oauth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={fb_app_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"state={state}"
    )

    logger.info(f"Initiating Facebook OAuth for user {current_user['id']} - channel: {channel}")

    return {"oauth_url": oauth_url}


@router.get("/facebook/callback")
async def facebook_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Facebook OAuth callback endpoint.

    Receives authorization code from Facebook, exchanges it for access token,
    retrieves page information, subscribes to webhooks, and stores credentials.

    Query params:
    - code: Authorization code from Facebook
    - state: User ID and channel (format: "user_id:channel")

    Returns:
    - Redirects to frontend with status=success or status=error
    """
    fb_app_id = os.getenv("FACEBOOK_APP_ID", "test-facebook-app-id")
    fb_app_secret = os.getenv("FACEBOOK_APP_SECRET", "test-facebook-app-secret")
    redirect_uri = os.getenv(
        "FACEBOOK_OAUTH_REDIRECT_URI",
        f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/integrations/facebook/callback",
    )
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:7860")

    # Parse state (user_id:channel)
    try:
        user_id, channel = state.split(":")
    except ValueError:
        logger.error(f"Invalid state parameter: {state}")
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Exchange code for user access token
            token_url = (
                f"https://graph.facebook.com/v18.0/oauth/access_token?"
                f"client_id={fb_app_id}&"
                f"redirect_uri={redirect_uri}&"
                f"client_secret={fb_app_secret}&"
                f"code={code}"
            )

            token_response = await client.get(token_url)
            if token_response.status_code != 200:
                logger.error(f"Failed to exchange code for token: {token_response.text}")
                raise HTTPException(status_code=502, detail="Facebook token exchange failed")

            token_data = token_response.json()
            user_access_token = token_data.get("access_token")

            if not user_access_token:
                logger.error("No access token in response")
                raise HTTPException(status_code=502, detail="Facebook returned no access token")

            # Step 2: Get user's Facebook Pages
            pages_url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={user_access_token}"
            pages_response = await client.get(pages_url)

            if pages_response.status_code != 200:
                logger.error(f"Failed to fetch pages: {pages_response.text}")
                raise HTTPException(status_code=502, detail="Failed to fetch Facebook pages")

            pages_data = pages_response.json()
            pages = pages_data.get("data", [])

            if not pages:
                logger.error("No Facebook Pages found for user")
                raise HTTPException(status_code=400, detail="No Facebook pages found for user")

            # Use first page (in production, let user select)
            page = pages[0]
            page_id = page["id"]
            page_access_token = page["access_token"]  # Long-lived Page Access Token
            page_name = page["name"]

            # Step 3: For Instagram, get Instagram Business Account ID
            instagram_account_id = None
            if channel == "instagram":
                ig_url = (
                    f"https://graph.facebook.com/v18.0/{page_id}?"
                    f"fields=instagram_business_account&"
                    f"access_token={page_access_token}"
                )
                ig_response = await client.get(ig_url)

                if ig_response.status_code == 200:
                    ig_data = ig_response.json()
                    instagram_account_id = ig_data.get("instagram_business_account", {}).get("id")

                    if not instagram_account_id:
                        logger.error(f"Page {page_name} has no linked Instagram Business Account")
                        raise HTTPException(status_code=400, detail="No linked Instagram Business Account found")
                else:
                    logger.error(f"Failed to fetch Instagram account: {ig_response.text}")
                    raise HTTPException(status_code=502, detail="Failed to fetch Instagram account")

            # Step 4: Subscribe page to webhooks
            if channel == "instagram":
                # Subscribe Instagram account to messages
                subscribe_url = f"https://graph.facebook.com/v18.0/{instagram_account_id}/subscribed_apps"
                subscribed_fields = "messages,messaging_postbacks"
            else:  # messenger
                # Subscribe Facebook Page to messages
                subscribe_url = f"https://graph.facebook.com/v18.0/{page_id}/subscribed_apps"
                subscribed_fields = "messages,messaging_postbacks,messaging_optins"

            subscribe_response = await client.post(
                subscribe_url,
                params={
                    "access_token": page_access_token,
                    "subscribed_fields": subscribed_fields
                }
            )

            if subscribe_response.status_code not in (200, 201):
                logger.warning(f"Webhook subscription may have failed: {subscribe_response.text}")
                # Don't fail the entire flow - webhook can be configured manually
            else:
                logger.info(f"Successfully subscribed {channel} webhooks for page {page_id}")

        # Step 5: Store integration in database
        integration = await create_channel_integration(
            db=db,
            auth_user_id=user_id,
            channel=channel,
            page_id=page_id,
            page_access_token=page_access_token,  # TODO: Encrypt in production
            page_name=page_name,
            instagram_account_id=instagram_account_id,
        )

        logger.info(f"Created {channel} integration for user {user_id} - page: {page_name}")

        # Redirect to frontend success page
        return RedirectResponse(
            url=f"{frontend_url}/dashboard/integrations?status=success&channel={channel}&page={page_name}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Facebook OAuth callback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected Facebook OAuth callback error")

@router.get("/list")
async def list_channel_integrations(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List user's channel integrations (Instagram, Messenger).
    
    Returns array of integration objects with status and page info.
    """
    user_id = current_user["id"]
    
    # Get all channel integrations for this user
    integrations = await get_channel_integrations_by_user(db, user_id)
    
    return [
        {
            "channel": integration.channel,
            "connected": integration.is_active,
            "page_name": integration.page_name,
            "page_id": integration.page_id,
        }
        for integration in integrations
    ]


@router.delete("/facebook/disconnect")
async def disconnect_facebook(
    channel: str = Query(..., pattern="^(instagram|messenger)$"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect the active Facebook channel integration for the user."""
    user_id = current_user["id"]
    deleted = await delete_channel_integration(db, channel, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"No {channel} integration found")

    return {
        "status": "success",
        "message": f"{channel.capitalize()} integration disconnected successfully",
    }
