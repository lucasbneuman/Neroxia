"""
Meta (Instagram + Facebook Messenger) webhook router.

Handles incoming webhooks from Meta's Graph API for both Instagram Direct Messages
and Facebook Messenger, including signature verification and message processing.
"""

from fastapi import APIRouter, Request, Query, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import hmac
import hashlib
import os
from typing import Dict, Any
import logging

from ..database import get_db
from whatsapp_bot_database import crud
from whatsapp_bot_database.models import ChannelIntegration

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhooks"])


# ========================================
# Instagram Webhooks
# ========================================

@router.get("/instagram")
async def instagram_webhook_verify(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
):
    """
    Verify Instagram webhook during Meta setup.

    Meta sends GET with hub.mode, hub.challenge, hub.verify_token.
    Return hub.challenge if verify_token matches.
    """
    if hub_mode != "subscribe":
        logger.warning(f"Invalid hub.mode: {hub_mode}")
        raise HTTPException(status_code=400, detail="Invalid hub.mode")

    expected_token = os.getenv("FACEBOOK_VERIFY_TOKEN")
    if not expected_token:
        logger.error("FACEBOOK_VERIFY_TOKEN not configured")
        raise HTTPException(status_code=500, detail="Verify token not configured")

    if hub_verify_token != expected_token:
        logger.warning("Instagram webhook verification failed: token mismatch")
        raise HTTPException(status_code=403, detail="Invalid verify token")

    logger.info("Instagram webhook verified successfully")
    return int(hub_challenge)


@router.post("/instagram")
async def instagram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Receive Instagram Direct Messages.

    Webhook payload structure:
    {
      "object": "page",
      "entry": [{
        "id": "PAGE_ID",
        "time": 1234567890,
        "messaging": [{
          "sender": {"id": "USER_PSID"},
          "recipient": {"id": "PAGE_ID"},
          "timestamp": 1234567890,
          "message": {"mid": "MESSAGE_ID", "text": "Hello!"}
        }]
      }]
    }

    Note: Message processing is done in background to avoid blocking webhook response.
    Meta expects 200 OK within 20 seconds.
    """
    # Verify signature
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not _verify_webhook_signature(body, signature):
        logger.warning("Instagram webhook signature verification failed")
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()

    # Process webhook events in background
    if payload.get("object") == "page":
        for entry in payload.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                # Process each message in background
                background_tasks.add_task(_process_instagram_message, messaging_event, db)

    # Return immediately to Meta
    return {"status": "ok"}


# ========================================
# Messenger Webhooks
# ========================================

@router.get("/messenger")
async def messenger_webhook_verify(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
):
    """Verify Messenger webhook during Meta setup."""
    if hub_mode != "subscribe":
        logger.warning(f"Invalid hub.mode: {hub_mode}")
        raise HTTPException(status_code=400, detail="Invalid hub.mode")

    expected_token = os.getenv("FACEBOOK_VERIFY_TOKEN")
    if not expected_token:
        logger.error("FACEBOOK_VERIFY_TOKEN not configured")
        raise HTTPException(status_code=500, detail="Verify token not configured")

    if hub_verify_token != expected_token:
        logger.warning("Messenger webhook verification failed: token mismatch")
        raise HTTPException(status_code=403, detail="Invalid verify token")

    logger.info("Messenger webhook verified successfully")
    return int(hub_challenge)


@router.post("/messenger")
async def messenger_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Receive Facebook Messenger messages.

    Note: Message processing is done in background to avoid blocking webhook response.
    Meta expects 200 OK within 20 seconds.
    """
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not _verify_webhook_signature(body, signature):
        logger.warning("Messenger webhook signature verification failed")
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()

    # Process webhook events in background
    if payload.get("object") == "page":
        for entry in payload.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                # Process each message in background
                background_tasks.add_task(_process_messenger_message, messaging_event, db)

    # Return immediately to Meta
    return {"status": "ok"}


# ========================================
# Helper Functions
# ========================================

def _verify_webhook_signature(body: bytes, signature: str) -> bool:
    """
    Verify Meta webhook signature using HMAC-SHA256.

    Signature format: sha256=<hash>
    """
    app_secret = os.getenv("FACEBOOK_APP_SECRET")

    if not app_secret or not signature:
        logger.error("Missing app_secret or signature header")
        return False

    # Reject signatures without proper format
    if "=" not in signature or not signature.startswith("sha256="):
        logger.error("Invalid signature format - missing sha256= prefix")
        return False

    # Remove 'sha256=' prefix
    expected_signature = signature.split("=")[1]

    # Compute HMAC
    mac = hmac.new(
        app_secret.encode(),
        msg=body,
        digestmod=hashlib.sha256
    )
    computed_signature = mac.hexdigest()

    return hmac.compare_digest(computed_signature, expected_signature)


async def _process_instagram_message(event: Dict[str, Any], db: AsyncSession):
    """
    Process incoming Instagram Direct Message.

    Calls bot engine to generate response and sends it back via Meta Graph API.
    """
    sender_psid = event.get("sender", {}).get("id")
    recipient_page_id = event.get("recipient", {}).get("id")
    message = event.get("message", {})
    message_text = message.get("text", "")

    if not message_text:
        logger.debug("Skipping non-text Instagram message")
        return  # Skip non-text messages for now

    logger.info(f"Processing Instagram message from PSID: {sender_psid}")

    # Get integration to identify tenant
    integration = await _get_integration(db, recipient_page_id, "instagram")
    if not integration:
        logger.warning(f"No integration found for Instagram page: {recipient_page_id}")
        return

    user = await crud.get_user_by_identifier(
        db,
        sender_psid,
        "instagram",
        integration.auth_user_id,
    )
    created = False
    if not user:
        user = await crud.create_user(
            db,
            name=sender_psid,
            identifier=sender_psid,
            phone=sender_psid,
            channel="instagram",
            auth_user_id=integration.auth_user_id,
        )
        created = True

    if created:
        logger.info(f"Created new Instagram user: {user.id}")

    # Save incoming message
    await crud.create_message(
        db,
        user_id=user.id,
        message=message_text,
        is_user=True,
        channel="instagram",
        channel_message_id=message.get("mid")
    )
    await db.commit()

    # Get channel config for bot engine
    try:
        channel_config = await crud.get_channel_config_for_user(db, user)
    except ValueError as e:
        logger.error(f"No channel config for Instagram user {sender_psid}: {e}")
        return

    # Call bot engine to process message
    try:
        # Import bot workflow
        import sys
        from pathlib import Path

        bot_engine_path = Path(__file__).parent.parent.parent.parent / "bot-engine" / "src"
        if str(bot_engine_path) not in sys.path:
            sys.path.insert(0, str(bot_engine_path))

        from graph.workflow import process_message

        # Get conversation history
        messages = await crud.get_messages(db, user.id, limit=20)
        conversation_history = []  # Convert to LangChain format if needed

        # Get config
        config = await crud.get_config(db, "bot") or {}

        # Process message through bot engine
        state = await process_message(
            user_identifier=sender_psid,
            message=message_text,
            conversation_history=conversation_history,
            config=config,
            db_session=db,
            db_user=user,
            channel="instagram",
            channel_config=channel_config,
        )

        # Response is sent automatically by MessageSender in bot engine
        logger.info(f"Processed Instagram message from {sender_psid} - bot response sent")

    except Exception as e:
        logger.error(f"Error calling bot engine for Instagram message: {e}", exc_info=True)
        # Don't raise - webhook should always return 200 OK


async def _process_messenger_message(event: Dict[str, Any], db: AsyncSession):
    """
    Process incoming Facebook Messenger message.

    Calls bot engine to generate response and sends it back via Meta Graph API.
    """
    sender_psid = event.get("sender", {}).get("id")
    recipient_page_id = event.get("recipient", {}).get("id")
    message = event.get("message", {})
    message_text = message.get("text", "")

    if not message_text:
        logger.debug("Skipping non-text Messenger message")
        return

    logger.info(f"Processing Messenger message from PSID: {sender_psid}")

    # Get integration to identify tenant
    integration = await _get_integration(db, recipient_page_id, "messenger")
    if not integration:
        logger.warning(f"No integration found for Messenger page: {recipient_page_id}")
        return

    user = await crud.get_user_by_identifier(
        db,
        sender_psid,
        "messenger",
        integration.auth_user_id,
    )
    created = False
    if not user:
        user = await crud.create_user(
            db,
            name=sender_psid,
            identifier=sender_psid,
            phone=sender_psid,
            channel="messenger",
            auth_user_id=integration.auth_user_id,
        )
        created = True

    if created:
        logger.info(f"Created new Messenger user: {user.id}")

    # Save incoming message
    await crud.create_message(
        db,
        user_id=user.id,
        message=message_text,
        is_user=True,
        channel="messenger",
        channel_message_id=message.get("mid")
    )
    await db.commit()

    # Get channel config for bot engine
    try:
        channel_config = await crud.get_channel_config_for_user(db, user)
    except ValueError as e:
        logger.error(f"No channel config for Messenger user {sender_psid}: {e}")
        return

    # Call bot engine to process message
    try:
        # Import bot workflow
        import sys
        from pathlib import Path

        bot_engine_path = Path(__file__).parent.parent.parent.parent / "bot-engine" / "src"
        if str(bot_engine_path) not in sys.path:
            sys.path.insert(0, str(bot_engine_path))

        from graph.workflow import process_message

        # Get conversation history
        messages = await crud.get_messages(db, user.id, limit=20)
        conversation_history = []  # Convert to LangChain format if needed

        # Get config
        config = await crud.get_config(db, "bot") or {}

        # Process message through bot engine
        state = await process_message(
            user_identifier=sender_psid,
            message=message_text,
            conversation_history=conversation_history,
            config=config,
            db_session=db,
            db_user=user,
            channel="messenger",
            channel_config=channel_config,
        )

        # Response is sent automatically by MessageSender in bot engine
        logger.info(f"Processed Messenger message from {sender_psid} - bot response sent")

    except Exception as e:
        logger.error(f"Error calling bot engine for Messenger message: {e}", exc_info=True)
        # Don't raise - webhook should always return 200 OK


async def _get_integration(
    db: AsyncSession,
    page_id: str,
    channel: str
) -> ChannelIntegration:
    """Get active channel integration by page ID."""
    return await crud.get_channel_integration_by_page(db, page_id, channel)
