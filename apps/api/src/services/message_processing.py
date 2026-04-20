"""Shared message processing service used by authenticated and public channels."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from whatsapp_bot_database import crud
from whatsapp_bot_shared import get_logger

# Add bot-engine to Python path
bot_engine_path = Path(__file__).parent.parent.parent.parent / "bot-engine" / "src"
if str(bot_engine_path) not in sys.path:
    sys.path.insert(0, str(bot_engine_path))

from graph.workflow import process_message

logger = get_logger(__name__)


def build_conversation_history(
    stored_messages: List[Any],
    provided_history: Optional[List[Dict[str, str]]] = None,
) -> list[Any]:
    """Build LangChain history either from provided history or stored messages."""
    conversation_history: list[Any] = []

    if provided_history:
        for message in provided_history:
            sender = message.get("sender")
            text = message.get("text", "")
            if sender == "user":
                conversation_history.append(HumanMessage(content=text))
            elif sender in {"bot", "assistant"}:
                conversation_history.append(AIMessage(content=text))
        return conversation_history

    for stored in stored_messages:
        if stored.sender == "user":
            conversation_history.append(HumanMessage(content=stored.message_text))
        elif stored.sender == "bot":
            conversation_history.append(AIMessage(content=stored.message_text))
    return conversation_history


async def process_incoming_message(
    *,
    db: AsyncSession,
    auth_user_id: str,
    identifier: str,
    channel: str,
    message: str,
    config: Optional[Dict[str, Any]] = None,
    history: Optional[List[Dict[str, str]]] = None,
    user_defaults: Optional[Dict[str, Any]] = None,
    inbound_metadata: Optional[Dict[str, Any]] = None,
    outbound_metadata: Optional[Dict[str, Any]] = None,
    create_test_deal: bool = False,
) -> Dict[str, Any]:
    """Process a message through the bot workflow and persist conversation state."""
    if not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    logger.info("Processing %s message for identifier=%s", channel, identifier)

    defaults = dict(user_defaults or {})
    defaults.setdefault("name", "Unknown User")

    user, is_new_user = await crud.get_or_create_user(
        db=db,
        identifier=identifier,
        channel=channel,
        auth_user_id=auth_user_id,
        defaults=defaults,
    )

    if is_new_user:
        logger.info("Created new %s user for tenant %s", channel, auth_user_id)

    should_create_deal = is_new_user or create_test_deal
    if should_create_deal:
        try:
            deal_source = "test" if create_test_deal else channel
            title_identifier = user.phone or user.channel_user_id or identifier
            deal_title = f"[TEST] {title_identifier}" if create_test_deal else f"Lead: {title_identifier}"
            existing_deal = await crud.get_user_active_deal(db, user.id)
            if existing_deal is None:
                await crud.create_deal(
                    db,
                    user_id=user.id,
                    title=deal_title,
                    value=0.0,
                    stage="new_lead",
                    source=deal_source,
                    probability=10,
                )
        except Exception as deal_error:
            logger.error("Failed to create deal: %s", deal_error)

    stored_messages = await crud.get_user_messages(db, user.id, limit=20)
    conversation_history = build_conversation_history(stored_messages, history)

    resolved_config = config or await crud.get_all_configs(db, user_id=auth_user_id) or {}

    try:
        result = await process_message(
            user_phone=user.phone or identifier,
            message=message,
            conversation_history=conversation_history,
            config=resolved_config,
            db_session=db,
            db_user=user,
        )
    except Exception as workflow_error:
        logger.error("Workflow execution error: %s", workflow_error, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Bot workflow error: {workflow_error}") from workflow_error

    bot_response = result.get("current_response", "I'm sorry, I couldn't process that.")

    await crud.create_message(
        db=db,
        user_id=user.id,
        message_text=message,
        sender="user",
        metadata=inbound_metadata,
        channel=channel,
    )
    await crud.create_message(
        db=db,
        user_id=user.id,
        message_text=bot_response,
        sender="bot",
        metadata=outbound_metadata or inbound_metadata,
        channel=channel,
    )

    updated_user = await crud.update_user(
        db=db,
        user_id=user.id,
        name=result.get("user_name") or user.name,
        email=result.get("user_email") or user.email,
        intent_score=result.get("intent_score"),
        sentiment=result.get("sentiment"),
        stage=result.get("stage"),
        conversation_mode=result.get("conversation_mode", "AUTO"),
    )

    return {
        "response": bot_response,
        "user_phone": updated_user.phone if updated_user else user.phone,
        "user_name": (updated_user.name if updated_user else user.name),
        "intent_score": result.get("intent_score", 0.0),
        "sentiment": result.get("sentiment", "neutral"),
        "stage": result.get("stage", "welcome"),
        "conversation_mode": result.get("conversation_mode", "AUTO"),
        "channel": channel,
        "user_id": user.id,
        "channel_user_id": user.channel_user_id,
    }
