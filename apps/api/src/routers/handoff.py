"""Handoff management router for human takeover."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from whatsapp_bot_database import crud
from whatsapp_bot_shared import get_logger

from ..database import get_db
from .auth import get_current_user

logger = get_logger(__name__)

router = APIRouter(prefix="/handoff", tags=["handoff"])


class HandoffTakeRequest(BaseModel):
    """Request to take over a conversation."""
    agent_name: Optional[str] = None


class HandoffSendRequest(BaseModel):
    """Request to send a manual message."""
    message: str


@router.post("/{phone}/take")
async def take_conversation(
    phone: str,
    request: HandoffTakeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Take over a conversation from the bot.
    
    Changes conversation_mode to MANUAL, pausing the bot.
    The human agent can now send messages manually.
    """
    try:
        # Get user by phone
        user = await crud.get_user_by_phone(db, phone)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User not found: {phone}"
            )
        
        # Update conversation mode to MANUAL
        await crud.update_user(
            db=db,
            user_id=user.id,
            conversation_mode="MANUAL"
        )
        
        agent_name = request.agent_name or current_user.get("email", "Agent")
        logger.info(f"Conversation taken over by {agent_name} for user {phone}")
        
        return {
            "status": "success",
            "message": f"Conversation taken over by {agent_name}",
            "phone": phone,
            "conversation_mode": "MANUAL",
            "agent": agent_name
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error taking conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to take conversation: {str(e)}"
        )


@router.post("/{phone}/return")
async def return_conversation(
    phone: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Return a conversation to the bot.
    
    Changes conversation_mode back to AUTO, allowing the bot to respond.
    """
    try:
        # Get user by phone
        user = await crud.get_user_by_phone(db, phone)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User not found: {phone}"
            )
        
        # Update conversation mode to AUTO
        await crud.update_user(
            db=db,
            user_id=user.id,
            conversation_mode="AUTO"
        )
        
        logger.info(f"Conversation returned to bot for user {phone}")
        
        return {
            "status": "success",
            "message": "Conversation returned to bot",
            "phone": phone,
            "conversation_mode": "AUTO"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error returning conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to return conversation: {str(e)}"
        )


@router.post("/{phone}/send")
async def send_manual_message(
    phone: str,
    request: HandoffSendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Send a manual message to a user.
    
    This endpoint allows human agents to send messages directly to users.
    The message is saved to the conversation history as coming from the bot.
    
    Note: This does NOT send the message via WhatsApp - that should be done
    through the Twilio service separately. This only saves it to the database.
    """
    try:
        # Get user by phone
        user = await crud.get_user_by_phone(db, phone)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User not found: {phone}"
            )
        
        # Check if conversation is in MANUAL mode
        if user.conversation_mode != "MANUAL":
            logger.warning(
                f"Sending manual message to {phone} but conversation_mode is {user.conversation_mode}"
            )
        
        # Save message to database
        await crud.create_message(
            db=db,
            user_id=user.id,
            message_text=request.message,
            sender="bot",  # Manual messages are saved as bot messages
            metadata={"manual": True, "agent": current_user.get("email")}
        )
        
        logger.info(f"Manual message sent to {phone} by {current_user.get('email')}")
        
        return {
            "status": "success",
            "message": "Message saved to conversation history",
            "phone": phone,
            "sent_message": request.message,
            "note": "Message saved to database. Send via WhatsApp separately."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending manual message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send manual message: {str(e)}"
        )


@router.get("/{phone}/status")
async def get_handoff_status(
    phone: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the current handoff status for a conversation.
    
    Returns information about whether the conversation is in AUTO, MANUAL,
    or NEEDS_ATTENTION mode.
    """
    try:
        # Get user by phone
        user = await crud.get_user_by_phone(db, phone)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User not found: {phone}"
            )
        
        return {
            "phone": phone,
            "conversation_mode": user.conversation_mode,
            "stage": user.stage,
            "sentiment": user.sentiment,
            "intent_score": user.intent_score,
            "is_bot_active": user.conversation_mode == "AUTO",
            "needs_attention": user.conversation_mode == "NEEDS_ATTENTION",
            "is_manual": user.conversation_mode == "MANUAL"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting handoff status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get handoff status: {str(e)}"
        )
