from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from whatsapp_bot_database import crud
from whatsapp_bot_database.models import Message, User
from whatsapp_bot_shared.helpers import format_phone_number

from ..database import get_db
from .auth import get_current_user

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/", response_model=List[dict])
async def get_conversations(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all active conversations."""
    users = await crud.get_all_active_users(db, limit=limit)
    
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

        result.append({
            "id": user.id,
            "phone": user.phone,
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
            "total_messages": user.total_messages
        })
    
    return result


@router.get("/pending", response_model=List[dict])
async def get_pending_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get conversations that need attention (NEEDS_ATTENTION or MANUAL mode)."""
    users = await crud.get_all_active_users(db, limit=100)
    
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
                "phone": user.phone,
                "name": user.name or "Unknown",
                "lastMessage": last_message,
                "timestamp": user.last_message_at,
                "mode": user.conversation_mode,
                "stage": user.stage,
                "sentiment": user.sentiment
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
    user = await crud.get_user_by_phone(db, formatted_phone)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "phone": user.phone,
        "name": user.name,
        "email": user.email,
        "stage": user.stage,
        "sentiment": user.sentiment,
        "intent_score": user.intent_score,
        "conversation_mode": user.conversation_mode,
        "conversation_summary": user.conversation_summary,
        "last_message_at": user.last_message_at,
        "created_at": user.created_at,
        "updated_at": user.updated_at
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
    
    user = await crud.get_user_by_phone(db, formatted_phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    messages = await crud.get_user_messages(db, user.id, limit=limit)
    
    # Format for frontend
    result = []
    for msg in messages:
        sender_type = "user" if msg.sender == "user" else msg.sender
        # Frontend expects: message_text, created_at, user_id, sender
        
        result.append({
            "id": msg.id,
            "user_id": msg.user_id,
            "message_text": msg.message_text,
            "sender": sender_type,
            "created_at": msg.timestamp.isoformat() if msg.timestamp else None,
            "metadata": msg.message_metadata
        })
        
    return result


@router.post("/{phone}/take-control")
async def take_control(
    phone: str, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Take manual control of a conversation."""
    formatted_phone = format_phone_number(phone)
    user = await crud.get_user_by_phone(db, formatted_phone)
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
    user = await crud.get_user_by_phone(db, formatted_phone)
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
    user = await crud.get_user_by_phone(db, formatted_phone)
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
    user = await crud.get_user_by_phone(db, formatted_phone)
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
