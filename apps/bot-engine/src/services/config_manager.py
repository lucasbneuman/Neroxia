"""Configuration manager for loading and saving application settings."""

from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from whatsapp_bot_database import crud
from whatsapp_bot_shared import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """Manager for application configuration."""

    DEFAULT_CONFIG = {
        # IMPORTANTE: Estos son valores VACÍOS por defecto
        # El bot NO debe responder hasta que se configure correctamente
        "system_prompt": "",
        "welcome_message": "",
        "payment_link": "",
        "response_delay_minutes": 0.5,  # Delay en minutos
        "text_audio_ratio": 0,
        "use_emojis": True,
        "tts_voice": "nova",
        "multi_part_messages": False,  # Enviar mensajes en múltiples partes
        "max_words_per_response": 100,  # Límite de palabras por respuesta
        # Producto/Servicio
        "product_name": "",
        "product_description": "",
        "product_features": "",
        "product_benefits": "",
        "product_price": "",
        "product_target_audience": "",
        # Prompts editables
        "welcome_prompt": "",
        "intent_prompt": "",
        "sentiment_prompt": "",
        "data_extraction_prompt": "",
        "closing_prompt": "",
    }

    def __init__(self):
        """Initialize configuration manager."""
        self._cache: Dict[str, Any] = {}
        logger.info("Config manager initialized")

    async def load_config(self, db: AsyncSession, key: str, user_id: Optional[str] = None, default: Any = None) -> Any:
        """
        Load a configuration value for a specific user.

        Args:
            db: Database session
            key: Configuration key
            user_id: User ID (UUID from auth.users) - required for multi-tenant
            default: Default value if not found

        Returns:
            Configuration value
        """
        # Check cache first (cache key includes user_id)
        cache_key = f"{user_id}:{key}" if user_id else key
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Load from database
        value = await crud.get_config(db, key, user_id=user_id)

        if value is None:
            # Use default or fall back to DEFAULT_CONFIG
            value = default if default is not None else self.DEFAULT_CONFIG.get(key)
            logger.info(f"Config '{key}' not found for user {user_id}, using default: {value}")
        else:
            logger.info(f"Loaded config '{key}' for user {user_id}: {value}")

        # Cache it
        self._cache[cache_key] = value
        return value

    async def save_config(self, db: AsyncSession, key: str, value: Any, user_id: Optional[str] = None) -> None:
        """
        Save a configuration value for a specific user.

        Args:
            db: Database session
            key: Configuration key
            value: Configuration value
            user_id: User ID (UUID from auth.users) - required for multi-tenant
        """
        await crud.set_config(db, key, value, user_id=user_id)
        
        # Cache it (cache key includes user_id)
        cache_key = f"{user_id}:{key}" if user_id else key
        self._cache[cache_key] = value
        logger.info(f"Saved config '{key}' for user {user_id}: {value}")

    async def load_all_configs(self, db: AsyncSession, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Load all configuration values for a specific user.

        Args:
            db: Database session
            user_id: User ID (UUID from auth.users) - required for multi-tenant

        Returns:
            Dict of all configurations
        """
        configs = await crud.get_all_configs(db, user_id=user_id)

        # Merge with defaults (defaults for missing keys)
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in configs:
                configs[key] = value

        # Update cache (cache keys include user_id)
        if user_id:
            for key, value in configs.items():
                cache_key = f"{user_id}:{key}"
                self._cache[cache_key] = value
        else:
            self._cache.update(configs)

        logger.info(f"Loaded {len(configs)} configurations for user {user_id}")
        return configs

    async def save_all_configs(self, db: AsyncSession, configs: Dict[str, Any], user_id: Optional[str] = None) -> None:
        """
        Save multiple configurations in a single transaction (optimized) for a specific user.

        Args:
            db: Database session
            configs: Dict of configurations to save
            user_id: User ID (UUID from auth.users) - required for multi-tenant
        """
        from sqlalchemy.future import select
        from whatsapp_bot_database.models import Config
        from datetime import datetime

        # Batch operation: prepare all upserts then commit once
        for key, value in configs.items():
            # Fetch existing config for this user
            if user_id:
                result = await db.execute(
                    select(Config).where(Config.key == key, Config.user_id == user_id)
                )
            else:
                result = await db.execute(select(Config).where(Config.key == key))
            
            config = result.scalar_one_or_none()

            if config:
                # Update existing
                config.value = value
                config.updated_at = datetime.utcnow()
            else:
                # Create new
                config = Config(key=key, value=value, user_id=user_id)
                db.add(config)

            # Update cache immediately (cache key includes user_id)
            cache_key = f"{user_id}:{key}" if user_id else key
            self._cache[cache_key] = value

        # Single commit for all changes
        await db.commit()

        logger.info(f"Saved {len(configs)} configurations in batch for user {user_id}")

    def get_cached(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value from cache.

        Args:
            key: Configuration key
            default: Default value if not in cache

        Returns:
            Cached value or default
        """
        return self._cache.get(key, default)

    def clear_cache(self) -> None:
        """Clear the configuration cache."""
        self._cache.clear()
        logger.info("Config cache cleared")

    async def initialize_defaults(self, db: AsyncSession, user_id: Optional[str] = None) -> None:
        """
        Initialize default configurations in database for a specific user if they don't exist.

        Args:
            db: Database session
            user_id: User ID (UUID from auth.users) - required for multi-tenant
        """
        for key, value in self.DEFAULT_CONFIG.items():
            existing = await crud.get_config(db, key, user_id=user_id)
            if existing is None:
                await crud.set_config(db, key, value, user_id=user_id)
                logger.info(f"Initialized default config '{key}' for user {user_id}: {value}")

        # Load all into cache
        await self.load_all_configs(db, user_id=user_id)

    async def get_twilio_config(self, db: AsyncSession) -> Dict[str, str]:
        """
        Get Twilio configuration from database with environment variable fallback.
        
        Args:
            db: Database session
            
        Returns:
            Dict with account_sid, auth_token, and whatsapp_number
        """
        import os
        
        # Try to load from database first
        twilio_config = await crud.get_config(db, "twilio")
        
        if twilio_config and twilio_config.get("account_sid") and twilio_config.get("auth_token"):
            logger.info("Loaded Twilio config from database")
            return twilio_config
        
        # Fallback to environment variables
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
        if account_sid and auth_token:
            logger.info("Loaded Twilio config from environment variables")
            return {
                "account_sid": account_sid,
                "auth_token": auth_token,
                "whatsapp_number": whatsapp_number or ""
            }
        
        logger.warning("Twilio not configured in database or environment")
        return {}

    async def get_hubspot_config(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Get HubSpot configuration from database with environment variable fallback.
        
        Args:
            db: Database session
            
        Returns:
            Dict with access_token and enabled flag
        """
        import os
        
        # Try to load from database first
        hubspot_config = await crud.get_config(db, "hubspot")
        
        if hubspot_config and hubspot_config.get("access_token"):
            logger.info("Loaded HubSpot config from database")
            return hubspot_config
        
        # Fallback to environment variables
        access_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
        
        if access_token:
            logger.info("Loaded HubSpot config from environment variables")
            return {
                "access_token": access_token,
                "enabled": True
            }
        
        logger.warning("HubSpot not configured in database or environment")
        return {"enabled": False}


# Global instance (will be initialized in app.py)
config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global config manager instance."""
    global config_manager
    if config_manager is None:
        config_manager = ConfigManager()
    return config_manager
