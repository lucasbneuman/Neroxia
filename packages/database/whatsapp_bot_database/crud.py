"""CRUD operations for database models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from .models import ChannelIntegration, Config, Deal, FollowUp, Message, Note, Tag, User, UserTag


# ============================================================================
# USER OPERATIONS
# ============================================================================


async def get_user_by_phone(db: AsyncSession, phone: str, auth_user_id: Optional[str] = None) -> Optional[User]:
    """
    Retrieve user by phone number.

    Args:
        db: Database session
        phone: User's phone number
        auth_user_id: Optional SaaS user ID to filter by

    Returns:
        User object if found, None otherwise
    """
    query = select(User).where(User.phone == phone)
    if auth_user_id:
        query = query.where(User.auth_user_id == auth_user_id)
        
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int, auth_user_id: Optional[str] = None) -> Optional[User]:
    """
    Retrieve user by ID.

    Args:
        db: Database session
        user_id: User's ID
        auth_user_id: Optional SaaS user ID to filter by

    Returns:
        User object if found, None otherwise
    """
    query = select(User).where(User.id == user_id)
    if auth_user_id:
        query = query.where(User.auth_user_id == auth_user_id)

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_identifier(
    db: AsyncSession,
    identifier: str,
    channel: str,
    auth_user_id: Optional[str] = None
) -> Optional[User]:
    """
    Get user by phone (WhatsApp) or channel_user_id (Instagram/Messenger).

    Args:
        db: Database session
        identifier: Phone number or PSID
        channel: 'whatsapp', 'instagram', or 'messenger'
        auth_user_id: Tenant ID for multi-tenant filtering

    Returns:
        User object or None
    """
    if channel == "whatsapp":
        # Use existing phone lookup
        return await get_user_by_phone(db, identifier, auth_user_id)
    else:
        # Lookup by channel_user_id
        query = select(User).where(
            User.channel == channel,
            User.channel_user_id == identifier
        )

        if auth_user_id:
            query = query.where(User.auth_user_id == auth_user_id)

        result = await db.execute(query)
        return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    phone: Optional[str] = None,
    name: Optional[str] = None,
    email: Optional[str] = None,
    channel: str = "whatsapp",
    channel_user_id: Optional[str] = None,
    channel_username: Optional[str] = None,
    channel_profile_pic_url: Optional[str] = None,
    auth_user_id: Optional[str] = None,
    **kwargs
) -> User:
    """
    Create a new user with multi-channel support.

    Args:
        db: Database session
        phone: Phone number (nullable for Instagram/Messenger)
        name: User's name
        email: User's email (optional)
        channel: 'whatsapp', 'instagram', or 'messenger'
        channel_user_id: PSID for Instagram/Messenger
        channel_username: @username for Instagram
        channel_profile_pic_url: Profile picture URL
        auth_user_id: Tenant ID
        **kwargs: Additional User model fields

    Returns:
        Created User object
    """
    user = User(
        phone=phone,
        name=name or "Unknown User",
        email=email,
        channel=channel,
        channel_user_id=channel_user_id,
        channel_username=channel_username,
        channel_profile_pic_url=channel_profile_pic_url,
        auth_user_id=auth_user_id,
        **kwargs
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user_id: int, **kwargs: Any) -> Optional[User]:
    """
    Update user fields.

    Args:
        db: Database session
        user_id: User's ID
        **kwargs: Fields to update

    Returns:
        Updated User object if found, None otherwise
    """
    user = await get_user_by_id(db, user_id)
    if user:
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
    return user


async def get_all_active_users(
    db: AsyncSession,
    limit: int = 100,
    offset: int = 0,
    auth_user_id: Optional[str] = None,
    channel: Optional[str] = None
) -> List[User]:
    """
    Get all active users with optional channel filtering.

    Args:
        db: Database session
        limit: Maximum users to return
        offset: Pagination offset
        auth_user_id: Filter by tenant
        channel: Filter by channel ('whatsapp', 'instagram', 'messenger')

    Returns:
        List of User objects
    """
    query = select(User).where(User.total_messages > 0)

    if auth_user_id:
        query = query.where(User.auth_user_id == auth_user_id)

    if channel:
        query = query.where(User.channel == channel)

    query = query.order_by(desc(User.last_message_at)).limit(limit).offset(offset)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_users_by_mode(db: AsyncSession, mode: str, auth_user_id: Optional[str] = None) -> List[User]:
    """
    Get all users in a specific conversation mode.

    Args:
        db: Database session
        mode: Conversation mode (AUTO/MANUAL/NEEDS_ATTENTION)
        auth_user_id: Optional SaaS user ID to filter by

    Returns:
        List of User objects
    """
    query = select(User).where(User.conversation_mode == mode)

    if auth_user_id:
        query = query.where(User.auth_user_id == auth_user_id)

    query = query.order_by(desc(User.last_message_at))

    result = await db.execute(query)
    return list(result.scalars().all())


# ============================================================================
# CHANNEL INTEGRATION OPERATIONS
# ============================================================================


async def create_channel_integration(
    db: AsyncSession,
    auth_user_id: str,
    channel: str,
    page_id: str,
    page_access_token: str,
    page_name: Optional[str] = None,
    instagram_account_id: Optional[str] = None,
    webhook_verify_token: Optional[str] = None
) -> ChannelIntegration:
    """
    Create new channel integration for a tenant.

    Args:
        db: Database session
        auth_user_id: Tenant ID
        channel: 'instagram' or 'messenger'
        page_id: Facebook Page ID
        page_access_token: Long-lived Page Access Token
        page_name: Facebook Page name
        instagram_account_id: Instagram Business Account ID (for Instagram only)
        webhook_verify_token: Custom webhook verification token

    Returns:
        Created ChannelIntegration object
    """
    integration = ChannelIntegration(
        auth_user_id=auth_user_id,
        channel=channel,
        page_id=page_id,
        page_access_token=page_access_token,
        page_name=page_name,
        instagram_account_id=instagram_account_id,
        webhook_verify_token=webhook_verify_token,
        is_active=True
    )

    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return integration


async def get_channel_integration(
    db: AsyncSession,
    auth_user_id: str,
    channel: str
) -> Optional[ChannelIntegration]:
    """
    Get active channel integration for a tenant.

    Args:
        db: Database session
        auth_user_id: Tenant ID
        channel: 'instagram' or 'messenger'

    Returns:
        ChannelIntegration object or None
    """
    query = select(ChannelIntegration).where(
        ChannelIntegration.auth_user_id == auth_user_id,
        ChannelIntegration.channel == channel,
        ChannelIntegration.is_active == True
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_channel_integration_by_page(
    db: AsyncSession,
    page_id: str,
    channel: str
) -> Optional[ChannelIntegration]:
    """
    Get integration by Facebook Page ID.

    Used in webhooks to identify which tenant the message belongs to.

    Args:
        db: Database session
        page_id: Facebook Page ID
        channel: 'instagram' or 'messenger'

    Returns:
        ChannelIntegration object or None
    """
    query = select(ChannelIntegration).where(
        ChannelIntegration.page_id == page_id,
        ChannelIntegration.channel == channel,
        ChannelIntegration.is_active == True
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_channel_integration(
    db: AsyncSession,
    integration_id: int,
    **kwargs
) -> ChannelIntegration:
    """
    Update existing channel integration.

    Args:
        db: Database session
        integration_id: Integration ID
        **kwargs: Fields to update

    Returns:
        Updated ChannelIntegration object

    Raises:
        ValueError: If integration not found
    """
    query = select(ChannelIntegration).where(ChannelIntegration.id == integration_id)
    result = await db.execute(query)
    integration = result.scalar_one_or_none()

    if not integration:
        raise ValueError(f"Integration {integration_id} not found")

    for key, value in kwargs.items():
        if hasattr(integration, key):
            setattr(integration, key, value)

    integration.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(integration)
    return integration


async def get_channel_config_for_user(
    db: AsyncSession,
    user: User
) -> Dict[str, Any]:
    """
    Get channel-specific config for sending messages to a user.

    For WhatsApp: Returns empty dict (uses env vars)
    For Instagram/Messenger: Returns page_access_token and page_id

    Args:
        db: Database session
        user: User object with channel and auth_user_id

    Returns:
        Dict with channel config or empty dict

    Raises:
        ValueError: If no active integration found for Meta channels
    """
    if user.channel == "whatsapp":
        return {}  # Twilio uses env vars

    # For Meta channels, get integration
    # Query by auth_user_id and channel
    # Assumption: One integration per tenant per channel
    query = select(ChannelIntegration).where(
        ChannelIntegration.auth_user_id == user.auth_user_id,
        ChannelIntegration.channel == user.channel,
        ChannelIntegration.is_active == True
    ).limit(1)

    result = await db.execute(query)
    integration = result.scalar_one_or_none()

    if not integration:
        raise ValueError(f"No active {user.channel} integration for user {user.id}")

    return {
        "page_access_token": integration.page_access_token,
        "page_id": integration.page_id
    }


async def deactivate_channel_integration(
    db: AsyncSession,
    integration_id: int
) -> ChannelIntegration:
    """
    Deactivate (soft delete) a channel integration.

    Args:
        db: Database session
        integration_id: Integration ID

    Returns:
        Updated ChannelIntegration object
    """
    return await update_channel_integration(db, integration_id, is_active=False)


async def get_channel_integrations_by_user(
    db: AsyncSession,
    auth_user_id: str
) -> list[ChannelIntegration]:
    """
    Get all channel integrations for a tenant.

    Args:
        db: Database session
        auth_user_id: Tenant ID

    Returns:
        List of ChannelIntegration objects (both active and inactive)
    """
    query = select(ChannelIntegration).where(
        ChannelIntegration.auth_user_id == auth_user_id
    ).order_by(ChannelIntegration.created_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


# ============================================================================
# MESSAGE OPERATIONS
# ============================================================================


async def create_message(
    db: AsyncSession,
    user_id: int,
    message_text: str,
    sender: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Message:
    """
    Create a new message.

    Args:
        db: Database session
        user_id: User's ID
        message_text: Message content
        sender: 'user' or 'bot'
        metadata: Optional metadata (intent, sentiment, etc.)

    Returns:
        Created Message object
    """
    message = Message(user_id=user_id, message_text=message_text, sender=sender, message_metadata=metadata)
    db.add(message)

    # Update user's message count and last message time
    user = await get_user_by_id(db, user_id)
    if user:
        user.total_messages += 1
        user.last_message_at = datetime.utcnow()

    await db.commit()
    await db.refresh(message)
    return message


async def get_user_messages(db: AsyncSession, user_id: int, limit: int = 50) -> List[Message]:
    """
    Get conversation history for a user.

    Args:
        db: Database session
        user_id: User's ID
        limit: Maximum number of messages to retrieve

    Returns:
        List of Message objects ordered by timestamp
    """
    result = await db.execute(
        select(Message)
        .where(Message.user_id == user_id)
        .order_by(Message.timestamp)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_recent_messages(db: AsyncSession, user_id: int, count: int = 10) -> List[Message]:
    """
    Get most recent messages for a user.

    Args:
        db: Database session
        user_id: User's ID
        count: Number of recent messages to retrieve

    Returns:
        List of Message objects ordered by timestamp (most recent last)
    """
    result = await db.execute(
        select(Message)
        .where(Message.user_id == user_id)
        .order_by(desc(Message.timestamp))
        .limit(count)
    )
    messages = list(result.scalars().all())
    return list(reversed(messages))  # Return in chronological order


# ============================================================================
# FOLLOW-UP OPERATIONS
# ============================================================================


async def create_follow_up(
    db: AsyncSession,
    user_id: int,
    scheduled_time: datetime,
    message: str,
    follow_up_count: int = 0,
    job_id: Optional[str] = None,
) -> FollowUp:
    """
    Create a follow-up task.

    Args:
        db: Database session
        user_id: User's ID
        scheduled_time: When to send the follow-up
        message: Message to send
        follow_up_count: Current follow-up count for this user
        job_id: APScheduler job ID

    Returns:
        Created FollowUp object
    """
    follow_up = FollowUp(
        user_id=user_id,
        scheduled_time=scheduled_time,
        message=message,
        follow_up_count=follow_up_count,
        job_id=job_id,
    )
    db.add(follow_up)
    await db.commit()
    await db.refresh(follow_up)
    return follow_up


async def get_pending_follow_ups(db: AsyncSession) -> List[FollowUp]:
    """
    Get all pending follow-ups.

    Args:
        db: Database session

    Returns:
        List of pending FollowUp objects
    """
    result = await db.execute(
        select(FollowUp)
        .where(FollowUp.status == "pending")
        .order_by(FollowUp.scheduled_time)
    )
    return list(result.scalars().all())


async def get_user_follow_ups(db: AsyncSession, user_id: int) -> List[FollowUp]:
    """
    Get all follow-ups for a specific user.

    Args:
        db: Database session
        user_id: User's ID

    Returns:
        List of FollowUp objects
    """
    result = await db.execute(
        select(FollowUp)
        .where(FollowUp.user_id == user_id)
        .order_by(desc(FollowUp.created_at))
    )
    return list(result.scalars().all())


async def get_tenant_follow_ups(db: AsyncSession, auth_user_id: str) -> List[FollowUp]:
    """
    Get all follow-ups for a tenant.

    Args:
        db: Database session
        auth_user_id: SaaS user ID

    Returns:
        List of FollowUp objects
    """
    result = await db.execute(
        select(FollowUp)
        .join(User)
        .where(User.auth_user_id == auth_user_id)
        .order_by(FollowUp.scheduled_time)
    )
    return list(result.scalars().all())


async def update_follow_up_status(db: AsyncSession, follow_up_id: int, status: str) -> Optional[FollowUp]:
    """
    Update follow-up status.

    Args:
        db: Database session
        follow_up_id: FollowUp ID
        status: New status (pending/sent/cancelled)

    Returns:
        Updated FollowUp object if found, None otherwise
    """
    result = await db.execute(select(FollowUp).where(FollowUp.id == follow_up_id))
    follow_up = result.scalar_one_or_none()
    if follow_up:
        follow_up.status = status
        await db.commit()
        await db.refresh(follow_up)
    return follow_up


async def cancel_user_pending_follow_ups(db: AsyncSession, user_id: int) -> int:
    """
    Cancel all pending follow-ups for a user.

    Args:
        db: Database session
        user_id: User's ID

    Returns:
        Number of follow-ups cancelled
    """
    result = await db.execute(
        select(FollowUp)
        .where(FollowUp.user_id == user_id, FollowUp.status == "pending")
    )
    follow_ups = result.scalars().all()

    count = 0
    for follow_up in follow_ups:
        follow_up.status = "cancelled"
        count += 1

    await db.commit()
    return count


# ============================================================================
# CONFIG OPERATIONS
# ============================================================================


async def get_config(db: AsyncSession, key: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get configuration value by key for a specific user.

    Args:
        db: Database session
        key: Configuration key
        user_id: User ID (UUID from auth.users) - required for multi-tenant

    Returns:
        Configuration value (JSON) if found, None otherwise
    """
    if user_id:
        # Multi-tenant: filter by user_id
        result = await db.execute(
            select(Config).where(Config.key == key, Config.user_id == user_id)
        )
    else:
        # Legacy: no user_id filter (will be blocked by RLS if enabled)
        result = await db.execute(select(Config).where(Config.key == key))
    
    config = result.scalar_one_or_none()
    return config.value if config else None


async def set_config(db: AsyncSession, key: str, value: Dict[str, Any], user_id: Optional[str] = None) -> Config:
    """
    Set configuration value for a specific user (create or update).

    Args:
        db: Database session
        key: Configuration key
        value: Configuration value (will be stored as JSON)
        user_id: User ID (UUID from auth.users) - required for multi-tenant

    Returns:
        Config object
    """
    if user_id:
        # Multi-tenant: filter by user_id
        result = await db.execute(
            select(Config).where(Config.key == key, Config.user_id == user_id)
        )
    else:
        # Legacy: no user_id filter
        result = await db.execute(select(Config).where(Config.key == key))
    
    config = result.scalar_one_or_none()

    if config:
        config.value = value
        config.updated_at = datetime.utcnow()
    else:
        # Create new config with user_id
        config = Config(key=key, value=value, user_id=user_id)
        db.add(config)

    await db.commit()
    await db.refresh(config)
    return config


async def get_all_configs(db: AsyncSession, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get all configuration values for a specific user.

    Args:
        db: Database session
        user_id: User ID (UUID from auth.users) - required for multi-tenant

    Returns:
        Dictionary mapping config keys to values
    """
    if user_id:
        # Multi-tenant: filter by user_id
        result = await db.execute(select(Config).where(Config.user_id == user_id))
    else:
        # Legacy: no user_id filter (will be blocked by RLS if enabled)
        result = await db.execute(select(Config))
    
    configs = result.scalars().all()
    return {config.key: config.value for config in configs}


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================


async def init_default_configs(db: AsyncSession) -> None:
    """
    Initialize default configuration values if they don't exist.

    Args:
        db: Database session
    """
    defaults = {
        "system_prompt": "You are a friendly and professional sales assistant. Your goal is to help customers find the right product and complete their purchase smoothly.",
        "payment_link": "https://example.com/pay",
        "response_delay": 1.0,  # seconds
        "text_audio_ratio": 0,  # 0-100, 0 = text only
        "use_emojis": True,
        "tts_voice": "nova",
        "rag_enabled": False,
    }

    for key, value in defaults.items():
        existing = await get_config(db, key)
        if existing is None:
            await set_config(db, key, value)


# ============================================================================
# CRM - DEAL OPERATIONS
# ============================================================================


async def create_deal(
    db: AsyncSession,
    user_id: int,
    title: str,
    value: float = 0.0,
    stage: str = "new_lead",
    source: str = "whatsapp",
    probability: int = 10,
    expected_close_date: Optional[datetime] = None
) -> Deal:
    """
    Create deal with channel source tracking.

    Args:
        db: Database session
        user_id: User ID
        title: Deal title
        value: Deal value
        stage: Deal stage
        source: 'whatsapp', 'instagram', 'messenger', or 'test'
        probability: Win probability
        expected_close_date: Expected close date

    Returns:
        Created Deal object

    Raises:
        ValueError: If source is invalid
    """
    # Validate source
    valid_sources = ["whatsapp", "instagram", "messenger", "test"]
    if source not in valid_sources:
        raise ValueError(f"Invalid source. Must be one of: {valid_sources}")

    deal = Deal(
        user_id=user_id,
        title=title,
        value=value,
        stage=stage,
        source=source,
        probability=probability,
        expected_close_date=expected_close_date
    )
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal


async def get_deal_by_id(db: AsyncSession, deal_id: int) -> Optional[Deal]:
    """Get deal by ID."""
    result = await db.execute(
        select(Deal).options(joinedload(Deal.user)).where(Deal.id == deal_id)
    )
    return result.scalar_one_or_none()


async def get_user_deals(db: AsyncSession, user_id: int) -> List[Deal]:
    """Get all deals for a user."""
    result = await db.execute(
        select(Deal).where(Deal.user_id == user_id).order_by(desc(Deal.created_at))
    )
    return list(result.scalars().all())


async def get_all_deals(
    db: AsyncSession,
    stage: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Deal]:
    """Get all deals with optional filtering."""
    query = select(Deal).options(joinedload(Deal.user)).order_by(desc(Deal.created_at))
    
    if stage:
        query = query.where(Deal.stage == stage)
        
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_deal(db: AsyncSession, deal_id: int, **kwargs: Any) -> Optional[Deal]:
    """Update deal fields. Marks as manually_qualified if stage is changed."""
    deal = await get_deal_by_id(db, deal_id)
    if deal:
        # If stage is being updated, mark as manually qualified
        if "stage" in kwargs:
            kwargs["manually_qualified"] = True
        
        for key, value in kwargs.items():
            if hasattr(deal, key):
                setattr(deal, key, value)
        
        # Auto-update probability based on stage if not explicitly provided
        if "stage" in kwargs and "probability" not in kwargs:
            stage_probs = {
                "new_lead": 10,
                "qualified": 25,
                "in_conversation": 50,
                "proposal_sent": 75,
                "won": 100,
                "lost": 0
            }
            if kwargs["stage"] in stage_probs:
                deal.probability = stage_probs[kwargs["stage"]]
                
        deal.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(deal)
    return deal


async def mark_deal_won(db: AsyncSession, deal_id: int, won_date: Optional[datetime] = None) -> Optional[Deal]:
    """Mark deal as won."""
    return await update_deal(
        db, 
        deal_id, 
        stage="won", 
        probability=100, 
        won_date=won_date or datetime.utcnow()
    )


async def mark_deal_lost(db: AsyncSession, deal_id: int, reason: str) -> Optional[Deal]:
    """Mark deal as lost."""
    return await update_deal(
        db, 
        deal_id, 
        stage="lost", 
        probability=0, 
        lost_date=datetime.utcnow(),
        lost_reason=reason
    )


async def delete_deal(db: AsyncSession, deal_id: int) -> bool:
    """Delete a deal."""
    deal = await get_deal_by_id(db, deal_id)
    if deal:
        await db.delete(deal)
        await db.commit()
        return True
    return False


# ============================================================================
# CRM - NOTE OPERATIONS
# ============================================================================


async def create_note(
    db: AsyncSession,
    user_id: int,
    content: str,
    created_by: str,  # UUID string
    deal_id: Optional[int] = None,
    note_type: str = "note"
) -> Note:
    """Create a new note."""
    note = Note(
        user_id=user_id,
        deal_id=deal_id,
        content=content,
        note_type=note_type,
        created_by=created_by
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def get_user_notes(db: AsyncSession, user_id: int) -> List[Note]:
    """Get all notes for a user."""
    result = await db.execute(
        select(Note).where(Note.user_id == user_id).order_by(desc(Note.created_at))
    )
    return list(result.scalars().all())


async def delete_note(db: AsyncSession, note_id: int) -> bool:
    """Delete a note."""
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if note:
        await db.delete(note)
        await db.commit()
        return True
    return False


# ============================================================================
# CRM - TAG OPERATIONS
# ============================================================================


async def create_tag(db: AsyncSession, name: str, color: str = "#6B7280") -> Tag:
    """Create a new tag."""
    tag = Tag(name=name, color=color)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def get_all_tags(db: AsyncSession) -> List[Tag]:
    """Get all tags."""
    result = await db.execute(select(Tag).order_by(Tag.name))
    return list(result.scalars().all())


async def add_tag_to_user(db: AsyncSession, user_id: int, tag_id: int) -> UserTag:
    """Assign tag to user."""
    user_tag = UserTag(user_id=user_id, tag_id=tag_id)
    db.add(user_tag)
    try:
        await db.commit()
        await db.refresh(user_tag)
        return user_tag
    except Exception:
        await db.rollback()
        # Likely already exists
        result = await db.execute(
            select(UserTag).where(UserTag.user_id == user_id, UserTag.tag_id == tag_id)
        )
        return result.scalar_one()


async def remove_tag_from_user(db: AsyncSession, user_id: int, tag_id: int) -> bool:
    """Remove tag from user."""
    result = await db.execute(
        select(UserTag).where(UserTag.user_id == user_id, UserTag.tag_id == tag_id)
    )
    user_tag = result.scalar_one_or_none()
    if user_tag:
        await db.delete(user_tag)
        await db.commit()
        return True
    return False


async def get_user_tags(db: AsyncSession, user_id: int) -> List[Tag]:
    """Get all tags for a user."""
    result = await db.execute(
        select(Tag)
        .join(UserTag, Tag.id == UserTag.tag_id)
        .where(UserTag.user_id == user_id)
    )
    return list(result.scalars().all())


# ============================================================================
# CRM - DASHBOARD METRICS
# ============================================================================


async def get_crm_metrics(db: AsyncSession) -> Dict[str, Any]:
    """Get CRM dashboard metrics."""
    # Total active deals (not won/lost)
    active_deals_result = await db.execute(
        select(Deal).where(Deal.stage.notin_(["won", "lost"]))
    )
    active_deals = list(active_deals_result.scalars().all())
    
    # Won deals
    won_deals_result = await db.execute(
        select(Deal).where(Deal.stage == "won")
    )
    won_deals = list(won_deals_result.scalars().all())
    
    # Total revenue
    total_revenue = sum(deal.value for deal in won_deals)
    
    # Conversion rate
    total_deals_count = await db.scalar(select(func.count(Deal.id)))
    conversion_rate = (len(won_deals) / total_deals_count * 100) if total_deals_count > 0 else 0
    
    return {
        "total_active_deals": len(active_deals),
        "total_won_deals": len(won_deals),
        "total_revenue": total_revenue,
        "conversion_rate": round(conversion_rate, 2)
    }


# ============================================================================
# CRM - STAGE SYNCHRONIZATION
# ============================================================================

# Mapping from User.stage (bot conversation) to Deal.stage (CRM)
STAGE_MAPPING = {
    "welcome": "new_lead",
    "qualifying": "qualified",
    "closing": "in_conversation",
    "sold": "proposal_sent",
}


async def sync_deal_stage_from_user(
    db: AsyncSession,
    user_id: int,
    new_user_stage: str,
    force: bool = False
) -> Optional[Deal]:
    """
    Sync deal stage when user conversation stage changes.
    Only updates if manually_qualified=False or force=True.
    
    Args:
        db: Database session
        user_id: User ID
        new_user_stage: New stage from User.stage
        force: If True, update even if manually_qualified=True
        
    Returns:
        Updated deal or None if no deal found or update skipped
    """
    # Get user's active deal (most recent non-won/lost)
    result = await db.execute(
        select(Deal)
        .where(Deal.user_id == user_id)
        .where(Deal.stage.notin_(["won", "lost"]))
        .order_by(desc(Deal.created_at))
        .limit(1)
    )
    deal = result.scalar_one_or_none()
    
    if not deal:
        return None
    
    # Skip if manually qualified (unless forced)
    if deal.manually_qualified and not force:
        return None
    
    # Map user stage to deal stage
    new_deal_stage = STAGE_MAPPING.get(new_user_stage)
    if not new_deal_stage:
        return None
    
    # Update deal stage (without marking as manually qualified)
    deal.stage = new_deal_stage
    
    # Update probability based on stage
    stage_probs = {
        "new_lead": 10,
        "qualified": 25,
        "in_conversation": 50,
        "proposal_sent": 75,
    }
    if new_deal_stage in stage_probs:
        deal.probability = stage_probs[new_deal_stage]
    
    deal.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(deal)
    
    return deal


async def get_user_active_deal(db: AsyncSession, user_id: int) -> Optional[Deal]:
    """Get user's most recent active deal (not won/lost)."""
    result = await db.execute(
        select(Deal)
        .options(joinedload(Deal.user))
        .where(Deal.user_id == user_id)
        .where(Deal.stage.notin_(["won", "lost"]))
        .order_by(desc(Deal.created_at))
        .limit(1)
    )
    return result.scalar_one_or_none()
