"""Database models and CRUD operations package."""

from .connection import AsyncSessionLocal, engine, get_db
from .crud import (
    cancel_user_pending_follow_ups,
    create_follow_up,
    create_message,
    create_user,
    get_all_active_users,
    get_all_configs,
    get_config,
    get_pending_follow_ups,
    get_recent_messages,
    get_user_by_id,
    get_user_by_phone,
    get_user_follow_ups,
    get_user_messages,
    get_users_by_mode,
    init_default_configs,
    set_config,
    update_follow_up_status,
    update_user,
)
from .models import Base, Config, FollowUp, Message, User

__all__ = [
    # Connection
    "engine",
    "AsyncSessionLocal",
    "get_db",
    # Models
    "Base",
    "User",
    "Message",
    "FollowUp",
    "Config",
    # CRUD - User operations
    "get_user_by_phone",
    "get_user_by_id",
    "create_user",
    "update_user",
    "get_all_active_users",
    "get_users_by_mode",
    # CRUD - Message operations
    "create_message",
    "get_user_messages",
    "get_recent_messages",
    # CRUD - Follow-up operations
    "create_follow_up",
    "get_pending_follow_ups",
    "get_user_follow_ups",
    "update_follow_up_status",
    "cancel_user_pending_follow_ups",
    # CRUD - Config operations
    "get_config",
    "set_config",
    "get_all_configs",
    "init_default_configs",
]
