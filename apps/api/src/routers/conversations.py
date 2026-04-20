from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from whatsapp_bot_database import crud
from whatsapp_bot_database.models import Message, User
from whatsapp_bot_shared.helpers import format_phone_number

from ..database import get_db
from .auth import get_current_user

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _extract_origin_host(metadata: Optional[dict]) -> Optional[str]:
    """Extract a readable hostname from stored web metadata."""
    if not metadata:
        return None
    origin = metadata.get("origin")
    if not origin:
        return None
    return origin.replace("https://", "").replace("http://", "")


def _conversation_identifier(user) -> str:
    """Return the best identifier to show for a conversation."""
    return user.phone or user.channel_user_id or f"user-{user.id}"


async def _serialize_message(msg) -> dict:
    return {
        "id": msg.id,
        "user_id": msg.user_id,
        "message_text": msg.message_text,
        "sender": "user" if msg.sender == "user" else msg.sender,
        "created_at": msg.timestamp.isoformat() if msg.timestamp else None,
        "metadata": msg.message_metadata,
        "message_metadata": msg.message_metadata,
        "channel": getattr(msg, "channel", None),
    }


async def _load_user_by_id_or_404(db: AsyncSession, user_id: int, auth_user_id: str):
    user = await crud.get_user_by_id(db, user_id, auth_user_id=auth_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=List[dict])
async def get_conversations(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all active conversations."""
    users = await crud.get_all_active_users(db, limit=limit, auth_user_id=current_user["id"])
    
    # Format for frontend
    result = []
    for user in users:
        # Get last message content if available
        last_message = "No messages"
        if user.last_message_at:
            # We would need to fetch the actual last message content, 
            # but for now let's just return the user info
            # Optimization: Add last_message_content to User model or fetch here
            recent = await crud.get_recent_messages(db, user.id, count=1)
            if recent:
                last_message = recent[0].message_text
        origin_host = None
        recent = await crud.get_recent_messages(db, user.id, count=1)
        if recent:
            origin_host = _extract_origin_host(recent[0].message_metadata)

        result.append({
            "id": user.id,
            "phone": user.phone,
            "displayIdentifier": _conversation_identifier(user),
            "name": user.name or "Unknown",
            "email": user.email,
            "lastMessage": last_message,
            "timestamp": user.last_message_at,
            "unread": 0,  # TODO: Implement unread count
            "isHandedOff": user.conversation_mode != "AUTO",
            "mode": user.conversation_mode,
            "stage": user.stage,
            "sentiment": user.sentiment,
            "conversation_summary": user.conversation_summary,
            "total_messages": user.total_messages,
            "channel": user.channel,
            "channel_user_id": user.channel_user_id,
            "originHost": origin_host,
        })
    
    return result


@router.get("/pending", response_model=List[dict])
async def get_pending_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get conversations that need attention (NEEDS_ATTENTION or MANUAL mode)."""
    users = await crud.get_all_active_users(db, limit=100, auth_user_id=current_user["id"])
    
    # Filter for conversations needing attention
    result = []
    for user in users:
        if user.conversation_mode in ["NEEDS_ATTENTION", "MANUAL"]:
            # Get last message
            last_message = "No messages"
            if user.last_message_at:
                recent = await crud.get_recent_messages(db, user.id, count=1)
                if recent:
                    last_message = recent[0].message_text
            
            result.append({
                "id": user.id,
                "phone": user.phone,
                "displayIdentifier": _conversation_identifier(user),
                "name": user.name or "Unknown",
                "lastMessage": last_message,
                "timestamp": user.last_message_at,
                "mode": user.conversation_mode,
                "stage": user.stage,
                "sentiment": user.sentiment,
                "channel": user.channel,
            })
    
    return result


@router.get("/{phone}", response_model=dict)
async def get_user_details(
    phone: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed user information including collected data."""
    formatted_phone = format_phone_number(phone)
    user = await crud.get_user_by_phone(db, formatted_phone, auth_user_id=current_user["id"])
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "phone": user.phone,
        "display_identifier": _conversation_identifier(user),
        "name": user.name,
        "email": user.email,
        "channel": user.channel,
        "channel_user_id": user.channel_user_id,
        "stage": user.stage,
        "sentiment": user.sentiment,
        "intent_score": user.intent_score,
        "conversation_mode": user.conversation_mode,
        "conversation_summary": user.conversation_summary,
        "last_message_at": user.last_message_at,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }


@router.get("/id/{user_id}", response_model=dict)
async def get_user_details_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed user information using the canonical user id."""
    user = await _load_user_by_id_or_404(db, user_id, current_user["id"])

    recent = await crud.get_recent_messages(db, user.id, count=1)
    origin_host = _extract_origin_host(recent[0].message_metadata) if recent else None

    return {
        "id": user.id,
        "phone": user.phone,
        "display_identifier": _conversation_identifier(user),
        "name": user.name,
        "email": user.email,
        "channel": user.channel,
        "channel_user_id": user.channel_user_id,
        "origin_host": origin_host,
        "stage": user.stage,
        "sentiment": user.sentiment,
        "intent_score": user.intent_score,
        "conversation_mode": user.conversation_mode,
        "conversation_summary": user.conversation_summary,
        "last_message_at": user.last_message_at,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "total_messages": user.total_messages,
        "whatsapp_profile_name": user.whatsapp_profile_name,
        "country_code": user.country_code,
        "phone_formatted": user.phone_formatted,
        "first_contact_timestamp": user.first_contact_timestamp,
        "media_count": user.media_count,
        "location_shared": user.location_shared,
    }


@router.get("/{phone}/messages", response_model=List[dict])
async def get_messages(
    phone: str, 
    limit: int = 50, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get messages for a specific conversation."""
    # Ensure phone format
    formatted_phone = format_phone_number(phone)
    
    user = await crud.get_user_by_phone(db, formatted_phone, auth_user_id=current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    messages = await crud.get_user_messages(db, user.id, limit=limit)
    
    # Format for frontend
    result = []
    for msg in messages:
        result.append(await _serialize_message(msg))
        
    return result


@router.get("/id/{user_id}/messages", response_model=List[dict])
async def get_messages_by_user_id(
    user_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get messages using the canonical user id."""
    user = await _load_user_by_id_or_404(db, user_id, current_user["id"])
    messages = await crud.get_user_messages(db, user.id, limit=limit)
    return [await _serialize_message(msg) for msg in messages]


@router.post("/{phone}/take-control")
async def take_control(
    phone: str, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Take manual control of a conversation."""
    formatted_phone = format_phone_number(phone)
    user = await crud.get_user_by_phone(db, formatted_phone, auth_user_id=current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    updated_user = await crud.update_user(db, user.id, conversation_mode="MANUAL")
    return {"status": "success", "mode": updated_user.conversation_mode}


@router.post("/{phone}/return-to-bot")
async def return_to_bot(
    phone: str, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Return conversation control to the bot."""
    formatted_phone = format_phone_number(phone)
    user = await crud.get_user_by_phone(db, formatted_phone, auth_user_id=current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    updated_user = await crud.update_user(db, user.id, conversation_mode="AUTO")
    return {"status": "success", "mode": updated_user.conversation_mode}


@router.post("/{phone}/send")
async def send_message(
    phone: str, 
    message: dict, # Expects {"message": "text"}
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Send a manual message to the user."""
    formatted_phone = format_phone_number(phone)
    user = await crud.get_user_by_phone(db, formatted_phone, auth_user_id=current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    message_text = message.get("message")
    if not message_text:
        raise HTTPException(status_code=400, detail="Message text required")
        
    # Save to database
    new_msg = await crud.create_message(
        db=db,
        user_id=user.id,
        message_text=message_text,
        sender="agent",
        metadata={"mode": "manual", "agent": current_user.get("username")}
    )
    
    # TODO: Trigger actual sending via Twilio/WhatsApp service
    # This would require migrating the Twilio service to a shared package or calling it here
    
    return {"status": "success", "message_id": new_msg.id}


@router.post("/id/{user_id}/send")
async def send_message_by_user_id(
    user_id: int,
    message: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Send a manual message to a user using canonical user id."""
    user = await _load_user_by_id_or_404(db, user_id, current_user["id"])
    message_text = message.get("message")
    if not message_text:
        raise HTTPException(status_code=400, detail="Message text required")
    new_msg = await crud.create_message(
        db=db,
        user_id=user.id,
        message_text=message_text,
        sender="agent",
        metadata={"mode": "manual", "agent": current_user.get("username")},
        channel=user.channel,
    )
    return {"status": "success", "message_id": new_msg.id}


@router.delete("/{phone}/clear")
async def clear_conversation_history(
    phone: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Clear conversation message history for a user.
    
    This deletes all messages but preserves the user record and their configuration.
    Useful for clearing test conversations without losing user data.
    """
    formatted_phone = format_phone_number(phone)
    user = await crud.get_user_by_phone(db, formatted_phone, auth_user_id=current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete all messages for this user
    # Note: This requires a new CRUD function
    from sqlalchemy import delete
    from whatsapp_bot_database.models import Message
    
    stmt = delete(Message).where(Message.user_id == user.id)
    await db.execute(stmt)
    await db.commit()
    
    return {
        "status": "success",
        "message": f"Cleared message history for {user.name or user.phone}",
        "user_preserved": True
    }


@router.delete("/id/{user_id}/clear")
async def clear_conversation_history_by_user_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Clear message history using canonical user id."""
    user = await _load_user_by_id_or_404(db, user_id, current_user["id"])

    from sqlalchemy import delete
    from whatsapp_bot_database.models import Message

    stmt = delete(Message).where(Message.user_id == user.id)
    await db.execute(stmt)
    await db.commit()
    return {
        "status": "success",
        "message": f"Cleared message history for {user.name or _conversation_identifier(user)}",
        "user_preserved": True,
    }


@router.delete("/{phone}")
async def delete_conversation(
    phone: str,
    delete_from_crm: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete entire conversation including user and all messages.
    
    Args:
        phone: User's phone number
        delete_from_crm: If True, also delete user's deals from CRM
    
    Returns:
        Status message with deletion details
    """
    formatted_phone = format_phone_number(phone)
    user = await crud.get_user_by_phone(db, formatted_phone, auth_user_id=current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_name = user.name or user.phone
    user_id = user.id
    
    # Delete from CRM if requested
    deals_deleted = 0
    if delete_from_crm:
        # Get all user's deals
        deals = await crud.get_user_deals(db, user_id)
        for deal in deals:
            await crud.delete_deal(db, deal.id)
            deals_deleted += 1
    
    # Delete all messages
    from sqlalchemy import delete
    from whatsapp_bot_database.models import Message
    
    stmt = delete(Message).where(Message.user_id == user_id)
    result = await db.execute(stmt)
    messages_deleted = result.rowcount
    
    # Delete user
    from whatsapp_bot_database.models import User
    stmt = delete(User).where(User.id == user_id)
    await db.execute(stmt)
    await db.commit()
    
    return {
        "status": "success",
        "message": f"Deleted conversation for {user_name}",
        "messages_deleted": messages_deleted,
        "deals_deleted": deals_deleted if delete_from_crm else 0,
        "crm_deleted": delete_from_crm
    }


@router.delete("/id/{user_id}")
async def delete_conversation_by_user_id(
    user_id: int,
    delete_from_crm: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete an entire conversation using canonical user id."""
    user = await _load_user_by_id_or_404(db, user_id, current_user["id"])
    user_name = user.name or _conversation_identifier(user)

    deals_deleted = 0
    if delete_from_crm:
        deals = await crud.get_user_deals(db, user.id)
        for deal in deals:
            await crud.delete_deal(db, deal.id)
            deals_deleted += 1

    from sqlalchemy import delete
    from whatsapp_bot_database.models import Message, User

    stmt = delete(Message).where(Message.user_id == user.id)
    result = await db.execute(stmt)
    messages_deleted = result.rowcount
    stmt = delete(User).where(User.id == user.id)
    await db.execute(stmt)
    await db.commit()

    return {
        "status": "success",
        "message": f"Deleted conversation for {user_name}",
        "messages_deleted": messages_deleted,
        "deals_deleted": deals_deleted if delete_from_crm else 0,
        "crm_deleted": delete_from_crm,
    }
