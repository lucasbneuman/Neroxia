"""Configuration management router."""

import sys
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
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
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all configuration settings.
    
    Returns all bot configuration including system prompts, product info,
    and behavior settings.
    """
    try:
        config_manager = get_config_manager()
        configs = await config_manager.load_all_configs(db)
        
        logger.info(f"Retrieved {len(configs)} configuration settings")
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
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update configuration settings.
    
    Accepts a dictionary of configuration key-value pairs to update.
    Only provided keys will be updated, others remain unchanged.
    """
    try:
        config_manager = get_config_manager()
        
        # Save all provided configs
        await config_manager.save_all_configs(db, config_update.configs)
        
        logger.info(f"Updated {len(config_update.configs)} configuration settings")
        
        # Return updated configs
        updated_configs = await config_manager.load_all_configs(db)
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
    Reset configuration to defaults.
    
    Clears cache and reinitializes with default values.
    """
    try:
        config_manager = get_config_manager()
        
        # Clear cache
        config_manager.clear_cache()
        
        # Reinitialize defaults
        await config_manager.initialize_defaults(db)
        
        # Load fresh configs
        configs = await config_manager.load_all_configs(db)
        
        logger.info("Configuration reset to defaults")
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
