"""Bot message processing router."""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from whatsapp_bot_database import crud
from whatsapp_bot_shared import get_logger

# Add bot-engine to Python path
bot_engine_path = Path(__file__).parent.parent.parent.parent / "bot-engine" / "src"
if str(bot_engine_path) not in sys.path:
    sys.path.insert(0, str(bot_engine_path))

# Import bot-engine workflow
from graph.workflow import process_message

from ..database import get_db

logger = get_logger(__name__)

router = APIRouter(prefix="/bot", tags=["bot"])


class HistoryMessage(BaseModel):
    """Message in conversation history."""
    text: str
    sender: str  # 'user' or 'bot'


class MessageRequest(BaseModel):
    """Message processing request."""
    phone: str
    message: str
    config: Dict[str, Any] = {}
    history: Optional[List[HistoryMessage]] = None  # Optional history for test chat


class MessageResponse(BaseModel):
    """Message processing response."""
    response: str
    user_phone: str
    user_name: str | None
    intent_score: float
    sentiment: str
    stage: str
    conversation_mode: str


@router.post("/process", response_model=MessageResponse)
async def process_bot_message(
    request: MessageRequest,
    db: AsyncSession = Depends(get_db),
    req: Request = None  # For rate limiting
):
    """
    Process a message through the bot-engine workflow.

    This endpoint:
    1. Gets or creates user from database
    2. Loads conversation history
    3. Processes message through LangGraph workflow
    4. Saves response to database
    5. Returns bot response
    """
    try:
        logger.info(f"Processing message from {request.phone}")

        # Get or create user
        user = await crud.get_user_by_phone(db, request.phone)
        if not user:
            user = await crud.create_user(db, phone=request.phone)
            logger.info(f"Created new user: {request.phone}")

        # Load conversation history
        from langchain_core.messages import HumanMessage, AIMessage
        conversation_history = []
        
        if request.history:
            # Use provided history (for test chat)
            logger.info(f"Using provided history: {len(request.history)} messages")
            for msg in request.history:
                if msg.sender == "user":
                    conversation_history.append(HumanMessage(content=msg.text))
                elif msg.sender == "bot":
                    conversation_history.append(AIMessage(content=msg.text))
        else:
            # Load from database (for real conversations)
            messages_data = await crud.get_user_messages(db, user.id, limit=20)
            for msg in reversed(messages_data):  # Oldest first
                if msg.sender == "user":
                    conversation_history.append(HumanMessage(content=msg.message_text))
                elif msg.sender == "bot":
                    conversation_history.append(AIMessage(content=msg.message_text))

        # Load configuration (use provided config or load from DB)
        config = request.config
        if not config:
            # Load default config from database
            config_data = await crud.get_all_configs(db)
            config = config_data or {}

        # Process message through workflow
        logger.info(f"Calling process_message with phone={request.phone}, history_len={len(conversation_history)}")
        
        try:
            result = await process_message(
                user_phone=request.phone,
                message=request.message,
                conversation_history=conversation_history,
                config=config,
                db_session=db,
                db_user=user
            )
            logger.info(f"process_message completed successfully")
        except Exception as workflow_error:
            logger.error(f"Workflow execution error: {workflow_error}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Bot workflow error: {str(workflow_error)}"
            )

        # Extract response
        bot_response = result.get("current_response", "I'm sorry, I couldn't process that.")
        logger.info(f"Bot response: {bot_response[:100]}...")

        # Save user message to database
        await crud.create_message(
            db=db,
            user_id=user.id,
            message_text=request.message,
            sender="user"
        )

        # Save bot response to database
        await crud.create_message(
            db=db,
            user_id=user.id,
            message_text=bot_response,
            sender="bot"
        )

        # Update user state
        await crud.update_user(
            db=db,
            user_id=user.id,
            name=result.get("user_name"),
            email=result.get("user_email"),
            intent_score=result.get("intent_score"),
            sentiment=result.get("sentiment"),
            stage=result.get("stage"),
            conversation_mode=result.get("conversation_mode", "AUTO")
        )

        logger.info(f"Message processed successfully for {request.phone}")

        return MessageResponse(
            response=bot_response,
            user_phone=request.phone,
            user_name=result.get("user_name"),
            intent_score=result.get("intent_score", 0.0),
            sentiment=result.get("sentiment", "neutral"),
            stage=result.get("stage", "welcome"),
            conversation_mode=result.get("conversation_mode", "AUTO")
        )

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/health")
async def bot_health():
    """Check if bot-engine is available."""
    try:
        # Try importing the workflow
        from graph.workflow import get_sales_graph
        graph = get_sales_graph()

        return {
            "status": "healthy",
            "bot_engine": "available",
            "graph": "compiled"
        }
    except Exception as e:
        logger.error(f"Bot health check failed: {e}")
        return {
            "status": "unhealthy",
            "bot_engine": "unavailable",
            "error": str(e)
        }
