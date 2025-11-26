"""Configuration management router."""

import sys
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from whatsapp_bot_shared import get_logger

# Add bot-engine to Python path
bot_engine_path = Path(__file__).parent.parent.parent.parent / "bot-engine" / "src"
if str(bot_engine_path) not in sys.path:
    sys.path.insert(0, str(bot_engine_path))

# Import bot-engine services
from services.config_manager import get_config_manager

from ..database import get_db
from .auth import get_current_user

logger = get_logger(__name__)

router = APIRouter(prefix="/config", tags=["config"])


class ConfigUpdate(BaseModel):
    """Configuration update request."""
    configs: Dict[str, Any]


@router.get("/")
async def get_config(
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all configuration settings for the authenticated user.

    Returns all bot configuration including system prompts, product info,
    and behavior settings.

    Cached for 5 minutes to improve performance.
    """
    try:
        # Extract user_id from JWT token
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid user token: missing user ID"
            )
        
        config_manager = get_config_manager()
        configs = await config_manager.load_all_configs(db, user_id=user_id)

        # Add caching headers (5 minutes)
        response.headers["Cache-Control"] = "private, max-age=300"

        logger.info(f"Retrieved {len(configs)} configuration settings for user {user_id}")
        return {"configs": configs}
    
    except Exception as e:
        logger.error(f"Error retrieving configuration: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve configuration: {str(e)}"
        )


@router.put("/")
async def update_config(
    config_update: ConfigUpdate,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update configuration settings for the authenticated user.

    Accepts a dictionary of configuration key-value pairs to update.
    Only provided keys will be updated, others remain unchanged.

    Invalidates cache to ensure fresh data on next GET.
    """
    try:
        # Extract user_id from JWT token
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid user token: missing user ID"
            )
        
        config_manager = get_config_manager()

        # Clear cache before saving
        config_manager.clear_cache()

        # Save all provided configs
        await config_manager.save_all_configs(db, config_update.configs, user_id=user_id)

        logger.info(f"Updated {len(config_update.configs)} configuration settings for user {user_id}")

        # Return updated configs with no-cache header
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

        updated_configs = await config_manager.load_all_configs(db, user_id=user_id)
        return {
            "status": "success",
            "message": f"Updated {len(config_update.configs)} settings",
            "configs": updated_configs
        }
    
    except Exception as e:
        logger.error(f"Error updating configuration: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update configuration: {str(e)}"
        )


@router.post("/reset")
async def reset_config(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Reset configuration to defaults for the authenticated user.
    
    Clears cache and reinitializes with default values.
    """
    try:
        # Extract user_id from JWT token
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid user token: missing user ID"
            )
        
        config_manager = get_config_manager()
        
        # Clear cache
        config_manager.clear_cache()
        
        # Reinitialize defaults
        await config_manager.initialize_defaults(db, user_id=user_id)
        
        # Load fresh configs
        configs = await config_manager.load_all_configs(db, user_id=user_id)
        
        logger.info(f"Configuration reset to defaults for user {user_id}")
        return {
            "status": "success",
            "message": "Configuration reset to defaults",
            "configs": configs
        }
    
    except Exception as e:
        logger.error(f"Error resetting configuration: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset configuration: {str(e)}"
        )
