"""LangGraph workflow compilation and execution."""

from typing import Any, Dict

from langgraph.graph import StateGraph, END

from .state import ConversationState
from .nodes import (
    welcome_node,
    intent_classifier_node,
    sentiment_analyzer_node,
    data_collector_node,
    router_node,
    conversation_node,
    closing_node,
    payment_node,
    follow_up_node,
    handoff_node,
    summary_node,
)
from neroxia_shared import get_logger

logger = get_logger(__name__)


def create_sales_graph():
    """
    Create and compile the sales conversation graph.

    Flow:
    1. welcome_node (if first message)
    2. intent_classifier_node (always)
    3. sentiment_analyzer_node (always)
    4. data_collector_node (always)
    5. router_node (decides next step)
        → conversation_node (default)
        → closing_node (high intent)
        → payment_node (ready to pay)
        → follow_up_node (leaving)
        → handoff_node (needs attention)
    6. END

    Returns:
        Compiled StateGraph
    """
    logger.info("Creating sales conversation graph")

    # Initialize graph
    workflow = StateGraph(ConversationState)

    # Add all nodes
    workflow.add_node("welcome", welcome_node)
    workflow.add_node("intent_classifier", intent_classifier_node)
    workflow.add_node("sentiment_analyzer", sentiment_analyzer_node)
    workflow.add_node("data_collector", data_collector_node)
    workflow.add_node("conversation", conversation_node)
    workflow.add_node("closing", closing_node)
    workflow.add_node("payment", payment_node)
    workflow.add_node("follow_up", follow_up_node)
    workflow.add_node("handoff", handoff_node)
    workflow.add_node("summary", summary_node)

    # Set entry point
    workflow.set_entry_point("welcome")

    # Define edges (sequential analysis pipeline)
    workflow.add_edge("welcome", "intent_classifier")
    workflow.add_edge("intent_classifier", "sentiment_analyzer")
    workflow.add_edge("sentiment_analyzer", "data_collector")

    # Conditional routing from data_collector
    workflow.add_conditional_edges(
        "data_collector",
        router_node,  # Router function determines next node
        {
            "conversation": "conversation",
            "closing": "closing",
            "payment": "payment",
            "follow_up": "follow_up",
            "handoff": "handoff",
        },
    )

    # End points
    workflow.add_edge("conversation", END)
    workflow.add_edge("closing", "payment")  # Closing leads to payment
    workflow.add_edge("payment", "summary")  # Generate summary after payment
    workflow.add_edge("follow_up", "summary")  # Generate summary after follow-up
    workflow.add_edge("summary", END)  # Summary leads to end
    workflow.add_edge("handoff", END)

    # Compile graph
    graph = workflow.compile()

    logger.info("Sales conversation graph compiled successfully")

    return graph


# Global graph instance
sales_graph = None


def get_sales_graph():
    """Get the compiled sales graph instance."""
    global sales_graph
    if sales_graph is None:
        sales_graph = create_sales_graph()
    return sales_graph


async def process_message(
    user_phone: str = None,
    message: str = None,
    conversation_history: list = None,
    config: Dict[str, Any] = None,
    db_session: Any = None,
    db_user: Any = None,
    # Multi-channel support (Phase 4B)
    user_identifier: str = None,
    channel: str = "whatsapp",
    channel_config: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Process a user message through the sales graph.

    Args:
        user_phone: User's phone number (DEPRECATED - use user_identifier)
        message: User's message text
        conversation_history: List of previous messages (BaseMessage objects)
        config: Configuration dict
        db_session: Database session for CRUD operations
        db_user: Database User object (for HubSpot sync)
        user_identifier: Phone or PSID (replaces user_phone for multi-channel)
        channel: Channel type - "whatsapp", "instagram", "messenger" (default: "whatsapp")
        channel_config: Channel-specific config (page_access_token, page_id for Meta channels)

    Returns:
        Updated state dict with response
    """
    # Backwards compatibility: use user_phone if user_identifier not provided
    if user_identifier is None and user_phone is not None:
        user_identifier = user_phone
        logger.info(f"[Backwards Compat] Using user_phone as user_identifier: {user_phone}")

    if user_identifier is None:
        raise ValueError("Either user_identifier or user_phone must be provided")

    logger.info(f"Processing message from {user_identifier} via {channel}")

    from langchain_core.messages import HumanMessage

    # Get graph
    graph = get_sales_graph()

    # Ensure channel_config is a dict (not None)
    if channel_config is None:
        channel_config = {}

    # Prepare initial state with multi-channel support
    initial_state: ConversationState = {
        "messages": conversation_history + [HumanMessage(content=message)],
        # Backwards compatibility: keep user_phone for WhatsApp or when identifier is phone
        "user_phone": user_identifier if channel == "whatsapp" else user_phone,
        # Multi-channel fields
        "channel": channel,
        "user_identifier": user_identifier,
        "channel_config": channel_config,
        # User info
        "user_name": None,  # Will be populated from DB or extracted
        "user_email": None,
        "intent_score": 0.0,
        "sentiment": "neutral",
        "stage": "welcome",
        "conversation_mode": "AUTO",
        "collected_data": {},
        "payment_link_sent": False,
        "follow_up_scheduled": None,
        "follow_up_count": 0,
        "current_response": None,
        "conversation_summary": None,
        "config": config,
        "db_session": db_session,
        "db_user": db_user,  # Pass user object for HubSpot sync
    }

    try:
        # Execute graph
        result = await graph.ainvoke(initial_state)

        logger.info("Graph execution completed successfully")

        return result

    except Exception as e:
        import traceback
        logger.error(f"Error executing graph: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Return fallback response
        return {
            **initial_state,
            "current_response": "I apologize, I'm having trouble responding right now. Could you please try again?",
        }
