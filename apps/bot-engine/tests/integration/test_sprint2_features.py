"""Unit tests for Sprint 2 features: Adaptive Personalization & Probabilistic Router."""

import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage

from services.llm_service import LLMService
from graph.nodes import calculate_routing_scores, router_node


@pytest.fixture
def llm_service():
    """Create an LLM service instance for testing."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        service = LLMService(openai_api_key="test-key")
        return service


# ============================================================================
# FEATURE 1: Conversation Trends Analysis
# ============================================================================

def test_conversation_trends_new_conversation(llm_service):
    """Test trends analysis for new conversations (< 3 messages)."""
    messages = [
        HumanMessage(content="Hola"),
    ]

    trends = llm_service.analyze_conversation_trends(
        messages,
        current_sentiment="neutral",
        current_intent=0.5
    )

    assert trends["sentiment_trend"] == "new_conversation"
    assert trends["intent_trend"] == "initial"
    assert trends["engagement_level"] == "high"
    assert trends["message_count"] == 1
    assert trends["recommendation"] == "welcome_warmly"


def test_conversation_trends_declining_sentiment(llm_service):
    """Test trends when sentiment is declining."""
    messages = [
        HumanMessage(content="Hola"),
        AIMessage(content="¡Hola!"),
        HumanMessage(content="¿Cuánto cuesta?"),
        AIMessage(content="$100"),
        HumanMessage(content="Es muy caro"),
    ]

    trends = llm_service.analyze_conversation_trends(
        messages,
        current_sentiment="negative",
        current_intent=0.3
    )

    assert trends["sentiment_trend"] == "declining"
    assert trends["recommendation"] == "empathize_and_support"


def test_conversation_trends_high_intent(llm_service):
    """Test trends when intent is increasing."""
    messages = [HumanMessage(content=f"Message {i}") for i in range(5)]

    trends = llm_service.analyze_conversation_trends(
        messages,
        current_sentiment="positive",
        current_intent=0.75
    )

    assert trends["intent_trend"] == "increasing"
    assert trends["recommendation"] == "introduce_urgency"


def test_conversation_trends_high_engagement(llm_service):
    """Test trends with high engagement (many messages)."""
    messages = [HumanMessage(content=f"Message {i}") for i in range(12)]

    trends = llm_service.analyze_conversation_trends(
        messages,
        current_sentiment="positive",
        current_intent=0.5
    )

    assert trends["engagement_level"] == "high"
    assert trends["recommendation"] == "maintain_momentum"


# ============================================================================
# FEATURE 2: Adaptive System Prompt Building
# ============================================================================

def test_adaptive_prompt_empathize_support(llm_service):
    """Test adaptive prompt for declining sentiment."""
    base_prompt = "You are a sales assistant"

    trends = {
        "recommendation": "empathize_and_support",
        "sentiment_trend": "declining",
        "engagement_level": "medium",
        "message_count": 5
    }

    adaptive_prompt = llm_service.build_adaptive_system_prompt(
        base_prompt,
        trends,
        current_sentiment="negative",
        current_intent=0.3
    )

    assert "AJUSTE DE TONO" in adaptive_prompt
    assert "empático" in adaptive_prompt.lower()
    assert "frustración" in adaptive_prompt.lower()


def test_adaptive_prompt_introduce_urgency(llm_service):
    """Test adaptive prompt for high intent."""
    base_prompt = "You are a sales assistant"

    trends = {
        "recommendation": "introduce_urgency",
        "intent_trend": "increasing",
        "engagement_level": "high",
        "message_count": 8
    }

    adaptive_prompt = llm_service.build_adaptive_system_prompt(
        base_prompt,
        trends,
        current_sentiment="positive",
        current_intent=0.8
    )

    assert "ESTRATEGIA DE CIERRE" in adaptive_prompt
    assert "llamado a la acción" in adaptive_prompt.lower()
    assert "0.80" in adaptive_prompt  # Should show intent score


def test_adaptive_prompt_maintain_momentum(llm_service):
    """Test adaptive prompt for high engagement."""
    base_prompt = "You are a sales assistant"

    trends = {
        "recommendation": "maintain_momentum",
        "engagement_level": "high",
        "message_count": 12
    }

    adaptive_prompt = llm_service.build_adaptive_system_prompt(
        base_prompt,
        trends,
        current_sentiment="neutral",
        current_intent=0.5
    )

    assert "MANTENER ENGAGEMENT" in adaptive_prompt
    assert "12 mensajes" in adaptive_prompt


def test_adaptive_prompt_low_engagement(llm_service):
    """Test adaptive prompt for low engagement."""
    base_prompt = "You are a sales assistant"

    trends = {
        "recommendation": "standard_approach",
        "engagement_level": "low",
        "message_count": 3
    }

    adaptive_prompt = llm_service.build_adaptive_system_prompt(
        base_prompt,
        trends,
        current_sentiment="neutral",
        current_intent=0.4
    )

    assert "INICIO DE CONVERSACIÓN" in adaptive_prompt
    assert "amigable" in adaptive_prompt.lower()


# ============================================================================
# FEATURE 3: Probabilistic Router - Scoring
# ============================================================================

def test_routing_scores_high_intent(sample_conversation_state):
    """Test routing scores with high intent."""
    sample_conversation_state["intent_score"] = 0.9
    sample_conversation_state["sentiment"] = "positive"
    sample_conversation_state["collected_data"] = {
        "name": "John",
        "email": "john@example.com",
        "phone": "123456789",
        "needs": "CRM software"
    }

    scores = calculate_routing_scores(sample_conversation_state)

    # Closing should have highest score
    assert scores["closing"] > scores["conversation"]
    assert scores["closing"] > scores["follow_up"]


def test_routing_scores_low_intent(sample_conversation_state):
    """Test routing scores with low intent."""
    sample_conversation_state["intent_score"] = 0.2
    sample_conversation_state["sentiment"] = "neutral"

    scores = calculate_routing_scores(sample_conversation_state)

    # Follow_up or conversation should have highest score
    assert scores["follow_up"] > scores["closing"]


def test_routing_scores_negative_sentiment(sample_conversation_state):
    """Test routing scores with negative sentiment."""
    sample_conversation_state["intent_score"] = 0.5
    sample_conversation_state["sentiment"] = "negative"

    scores = calculate_routing_scores(sample_conversation_state)

    # Handoff should have elevated score
    assert scores["handoff"] > 0.1


def test_routing_scores_high_data_completeness(sample_conversation_state):
    """Test routing scores with complete user data."""
    sample_conversation_state["intent_score"] = 0.6
    sample_conversation_state["collected_data"] = {
        "name": "Jane",
        "email": "jane@example.com",
        "phone": "987654321",
        "needs": "Sales automation"
    }

    scores = calculate_routing_scores(sample_conversation_state)

    # Closing score should be boosted by data completeness
    assert scores["closing"] > 0.2


def test_routing_scores_conversation_momentum(sample_conversation_state):
    """Test routing scores with high message count."""
    sample_conversation_state["intent_score"] = 0.6
    sample_conversation_state["messages"] = [
        HumanMessage(content=f"Message {i}") if i % 2 == 0
        else AIMessage(content=f"Response {i}")
        for i in range(15)
    ]

    scores = calculate_routing_scores(sample_conversation_state)

    # High momentum should boost closing score
    assert scores["closing"] > 0.25


def test_routing_scores_normalization(sample_conversation_state):
    """Test that routing scores are normalized to probabilities."""
    scores = calculate_routing_scores(sample_conversation_state)

    # Sum of all scores should be approximately 1.0
    total = sum(scores.values())
    assert 0.99 <= total <= 1.01


# ============================================================================
# FEATURE 4: Probabilistic Router - Decision Making
# ============================================================================

def test_router_deterministic_needs_attention(sample_conversation_state):
    """Test router prioritizes NEEDS_ATTENTION deterministically."""
    sample_conversation_state["conversation_mode"] = "NEEDS_ATTENTION"
    sample_conversation_state["intent_score"] = 0.9  # Even with high intent

    route = router_node(sample_conversation_state)

    assert route == "handoff"


def test_router_deterministic_payment_flow(sample_conversation_state):
    """Test router handles payment flow deterministically."""
    sample_conversation_state["stage"] = "closing"
    sample_conversation_state["payment_link_sent"] = False

    route = router_node(sample_conversation_state)

    assert route == "payment"


def test_router_probabilistic_high_intent(sample_conversation_state):
    """Test probabilistic routing with high intent."""
    sample_conversation_state["intent_score"] = 0.85
    sample_conversation_state["sentiment"] = "positive"
    sample_conversation_state["collected_data"] = {
        "name": "Alice",
        "email": "alice@example.com"
    }

    route = router_node(sample_conversation_state)

    # Should route to closing or conversation (not follow_up)
    assert route in ["closing", "conversation"]


def test_router_probabilistic_low_intent(sample_conversation_state):
    """Test probabilistic routing with low intent."""
    sample_conversation_state["intent_score"] = 0.15
    sample_conversation_state["sentiment"] = "neutral"

    route = router_node(sample_conversation_state)

    # Should route to conversation or follow_up
    assert route in ["conversation", "follow_up"]


def test_router_probabilistic_negative_sentiment(sample_conversation_state):
    """Test probabilistic routing with persistent negative sentiment."""
    sample_conversation_state["intent_score"] = 0.5
    sample_conversation_state["sentiment"] = "negative"
    sample_conversation_state["messages"] = [
        HumanMessage(content="Message 1"),
        AIMessage(content="Response 1"),
        HumanMessage(content="Message 2"),
        AIMessage(content="Response 2"),
        HumanMessage(content="Message 3 (negative)"),
    ]

    route = router_node(sample_conversation_state)

    # Should route to handoff with persistent negative
    assert route == "handoff"


def test_router_threshold_closing(sample_conversation_state):
    """Test router requires high confidence for closing."""
    # Set up state that barely qualifies for closing
    sample_conversation_state["intent_score"] = 0.5
    sample_conversation_state["sentiment"] = "neutral"
    sample_conversation_state["collected_data"] = {}

    route = router_node(sample_conversation_state)

    # With low confidence, should default to conversation
    assert route == "conversation"


def test_router_logging(sample_conversation_state, caplog):
    """Test router logs decision reasoning."""
    import logging
    caplog.set_level(logging.INFO)

    sample_conversation_state["intent_score"] = 0.7
    sample_conversation_state["sentiment"] = "positive"

    route = router_node(sample_conversation_state)

    # Check that logging includes probabilistic info
    assert "Probabilistic routing" in caplog.text
    assert "score:" in caplog.text


# ============================================================================
# INTEGRATION TEST: Full Adaptive Conversation Flow
# ============================================================================

def test_full_adaptive_flow_declining_sentiment(llm_service, sample_conversation_state):
    """Integration test: Full flow with declining sentiment."""
    # Simulate declining sentiment conversation
    sample_conversation_state["messages"] = [
        HumanMessage(content="Hola"),
        AIMessage(content="¡Hola! ¿Cómo puedo ayudarte?"),
        HumanMessage(content="¿Cuánto cuesta?"),
        AIMessage(content="Cuesta $100"),
        HumanMessage(content="Es muy caro, no me convence"),
    ]
    sample_conversation_state["sentiment"] = "negative"
    sample_conversation_state["intent_score"] = 0.3

    # Analyze trends
    trends = llm_service.analyze_conversation_trends(
        sample_conversation_state["messages"],
        current_sentiment="negative",
        current_intent=0.3
    )

    # Build adaptive prompt
    base_prompt = "You are a sales assistant"
    adaptive_prompt = llm_service.build_adaptive_system_prompt(
        base_prompt,
        trends,
        current_sentiment="negative",
        current_intent=0.3
    )

    # Calculate routing
    scores = calculate_routing_scores(sample_conversation_state)

    # Assertions
    assert trends["recommendation"] == "empathize_and_support"
    assert "AJUSTE DE TONO" in adaptive_prompt
    assert scores["handoff"] > 0  # Should consider handoff
