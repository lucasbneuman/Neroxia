"""Integration configuration router (Twilio, HubSpot)."""

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

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
