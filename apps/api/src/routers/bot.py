"""Bot message processing router."""

from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from whatsapp_bot_shared import get_logger

from ..database import get_db
from .auth import get_current_user
from ..services.message_processing import process_incoming_message

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
    current_user: dict = Depends(get_current_user),
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
    logger.info("Processing message from %s", request.phone)
    history = None
    if request.history:
        history = [{"text": msg.text, "sender": msg.sender} for msg in request.history]

    result = await process_incoming_message(
        db=db,
        auth_user_id=current_user["id"],
        identifier=request.phone,
        channel="whatsapp",
        message=request.message,
        config=request.config,
        history=history,
        user_defaults={"name": "Unknown User"},
        create_test_deal=bool(request.history),
    )

    return MessageResponse(
        response=result["response"],
        user_phone=result["user_phone"] or request.phone,
        user_name=result.get("user_name"),
        intent_score=result["intent_score"],
        sentiment=result["sentiment"],
        stage=result["stage"],
        conversation_mode=result["conversation_mode"],
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
