"""Unit tests for LLM optimizations implemented on 2025-11-24."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from services.llm_service import LLMService


@pytest.fixture
def llm_service():
    """Create an LLM service instance for testing."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        service = LLMService(openai_api_key="test-key")
        return service


# ============================================================================
# OPTIMIZATION #1: Intent Classifier with Context
# ============================================================================

@pytest.mark.asyncio
async def test_intent_classifier_first_message_greeting(llm_service):
    """Test intent classification for first message greeting."""
    mock_response = MagicMock()
    mock_response.content = '{"category": "interested", "score": 0.45}'

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    llm_service.gpt4o_mini = mock_llm

    # Test first message (no history)
    result = await llm_service.classify_intent("Hola", conversation_history=[])

    assert result["category"] == "interested"
    assert 0.4 <= result["score"] <= 0.6

    # Verify prompt includes context about first message
    call_args = mock_llm.ainvoke.call_args[0][0]
    prompt_content = call_args[0].content
    assert "primer mensaje" in prompt_content.lower()


@pytest.mark.asyncio
async def test_intent_classifier_with_conversation_history(llm_service):
    """Test intent classification considers conversation history."""
    mock_response = MagicMock()
    mock_response.content = '{"category": "ready_to_buy", "score": 0.75}'

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    llm_service.gpt4o_mini = mock_llm

    # Create conversation history
    history = [
        HumanMessage(content="Hola"),
        AIMessage(content="¡Hola! ¿Cómo puedo ayudarte?"),
        HumanMessage(content="¿Cuánto cuesta?"),
        AIMessage(content="Cuesta $100"),
    ]

    result = await llm_service.classify_intent(
        "Quiero comprarlo ahora",
        conversation_history=history
    )

    assert result["category"] == "ready_to_buy"
    assert result["score"] >= 0.6

    # Verify prompt mentions interaction number
    call_args = mock_llm.ainvoke.call_args[0][0]
    prompt_content = call_args[0].content
    assert "interacción #" in prompt_content.lower()


@pytest.mark.asyncio
async def test_intent_classifier_custom_prompt(llm_service):
    """Test intent classification with custom prompt from config."""
    mock_response = MagicMock()
    mock_response.content = '{"category": "interested", "score": 0.5}'

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    llm_service.gpt4o_mini = mock_llm

    custom_config = {
        "intent_prompt": "Custom prompt: analyze {message}. Context: {context}"
    }

    result = await llm_service.classify_intent(
        "Test message",
        conversation_history=[],
        config=custom_config
    )

    # Verify custom prompt was used
    call_args = mock_llm.ainvoke.call_args[0][0]
    prompt_content = call_args[0].content
    assert "Custom prompt" in prompt_content
    assert "Test message" in prompt_content


# ============================================================================
# OPTIMIZATION #2: Data Extraction Improved Validation
# ============================================================================

@pytest.mark.asyncio
async def test_data_extraction_short_name_accepted(llm_service):
    """Test that short valid names are accepted (e.g., 'Jo', 'Li')."""
    mock_response = MagicMock()
    mock_response.content = '{"name": "Jo"}'

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    llm_service.gpt4o_mini = mock_llm

    data = await llm_service.extract_data("Me llamo Jo")

    assert "name" in data
    assert data["name"] == "Jo"


@pytest.mark.asyncio
async def test_data_extraction_greeting_rejected(llm_service):
    """Test that greetings like 'Hola' are NOT extracted as names."""
    mock_response = MagicMock()
    mock_response.content = '{"name": null}'

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    llm_service.gpt4o_mini = mock_llm

    data = await llm_service.extract_data("Hola")

    # Should not extract "Hola" as a name
    assert "name" not in data or data.get("name") is None


@pytest.mark.asyncio
async def test_data_extraction_international_email(llm_service):
    """Test international email formats are accepted."""
    mock_response = MagicMock()
    mock_response.content = '{"email": "user@empresa.co.uk"}'

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    llm_service.gpt4o_mini = mock_llm

    data = await llm_service.extract_data("Mi email es user@empresa.co.uk")

    assert "email" in data
    assert data["email"] == "user@empresa.co.uk"


@pytest.mark.asyncio
async def test_data_extraction_international_phone(llm_service):
    """Test international phone formats are accepted."""
    mock_response = MagicMock()
    mock_response.content = '{"phone": "+54 11 1234-5678"}'

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    llm_service.gpt4o_mini = mock_llm

    data = await llm_service.extract_data("Mi número es +54 11 1234-5678")

    assert "phone" in data
    assert data["phone"] == "+54 11 1234-5678"


@pytest.mark.asyncio
async def test_data_extraction_custom_prompt(llm_service):
    """Test data extraction with custom prompt from config."""
    mock_response = MagicMock()
    mock_response.content = '{"name": "Test User"}'

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    llm_service.gpt4o_mini = mock_llm

    custom_config = {
        "data_extraction_prompt": "Extract from: {message}"
    }

    data = await llm_service.extract_data(
        "My name is Test User",
        config=custom_config
    )

    # Verify custom prompt was used
    call_args = mock_llm.ainvoke.call_args[0][0]
    prompt_content = call_args[0].content
    assert "Extract from:" in prompt_content


# ============================================================================
# OPTIMIZATION #3: RAG Context Optimization
# ============================================================================

@pytest.mark.asyncio
async def test_rag_context_includes_instructions(llm_service):
    """Test that RAG context includes clear usage instructions."""
    mock_response = MagicMock()
    mock_response.content = "Response based on documentation"

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    llm_service.gpt4o = mock_llm

    messages = [HumanMessage(content="What is the product?")]
    rag_context = "Product info: Our product is a sales bot with AI capabilities."

    response = await llm_service.generate_response(
        messages=messages,
        system_prompt="You are a sales assistant",
        rag_context=rag_context
    )

    # Verify RAG context includes enhanced instructions
    call_args = mock_llm.ainvoke.call_args[0][0]
    system_message = call_args[0]

    assert isinstance(system_message, SystemMessage)
    assert "DOCUMENTACIÓN OFICIAL" in system_message.content
    assert "PRIORIDAD ABSOLUTA" in system_message.content
    assert "CITACIÓN NATURAL" in system_message.content
    assert "Product info: Our product is a sales bot" in system_message.content


@pytest.mark.asyncio
async def test_rag_context_without_rag(llm_service):
    """Test that prompt works correctly without RAG context."""
    mock_response = MagicMock()
    mock_response.content = "Normal response"

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    llm_service.gpt4o = mock_llm

    messages = [HumanMessage(content="Hello")]

    response = await llm_service.generate_response(
        messages=messages,
        system_prompt="You are a helpful assistant",
        rag_context=None
    )

    # Verify no RAG instructions when no context
    call_args = mock_llm.ainvoke.call_args[0][0]
    system_message = call_args[0]

    assert "DOCUMENTACIÓN OFICIAL" not in system_message.content


# ============================================================================
# OPTIMIZATION #4: Context Window Optimization
# ============================================================================

def test_context_optimization_short_conversation(llm_service):
    """Test that short conversations are not modified."""
    messages = [
        HumanMessage(content=f"Message {i}") for i in range(10)
    ]

    optimized = llm_service.prepare_optimized_context(messages, max_messages=12)

    # Should return all messages unchanged
    assert len(optimized) == 10
    assert optimized == messages


def test_context_optimization_long_conversation(llm_service):
    """Test that long conversations are optimized with summary."""
    messages = [
        HumanMessage(content=f"User message {i}") if i % 2 == 0
        else AIMessage(content=f"Bot response {i}")
        for i in range(20)
    ]

    optimized = llm_service.prepare_optimized_context(
        messages,
        max_messages=12,
        preserve_start=2,
        preserve_end=6
    )

    # Should have: 2 start + 1 summary + 6 end = 9 messages
    assert len(optimized) == 9

    # First 2 should be original
    assert optimized[0] == messages[0]
    assert optimized[1] == messages[1]

    # Middle should be summary
    assert isinstance(optimized[2], SystemMessage)
    assert "Resumen de" in optimized[2].content

    # Last 6 should be original
    assert optimized[-6:] == messages[-6:]


def test_context_optimization_preserves_structure(llm_service):
    """Test that context optimization preserves message types."""
    messages = [
        HumanMessage(content="Hello"),
        AIMessage(content="Hi"),
        HumanMessage(content="How are you?"),
        AIMessage(content="Good"),
        HumanMessage(content="Question 1"),
        AIMessage(content="Answer 1"),
        HumanMessage(content="Question 2"),
        AIMessage(content="Answer 2"),
        HumanMessage(content="Question 3"),
        AIMessage(content="Answer 3"),
        HumanMessage(content="Question 4"),
        AIMessage(content="Answer 4"),
        HumanMessage(content="Latest question"),
        AIMessage(content="Latest answer"),
    ]

    optimized = llm_service.prepare_optimized_context(messages, max_messages=10)

    # Should have start + summary + end
    assert len(optimized) < len(messages)

    # All should be BaseMessage objects
    from langchain_core.messages import BaseMessage
    assert all(isinstance(msg, BaseMessage) for msg in optimized)


def test_quick_summary_creation(llm_service):
    """Test that quick summary is created without calling LLM."""
    messages = [
        HumanMessage(content="I need help with sales automation"),
        AIMessage(content="I can help you with that"),
        HumanMessage(content="What features do you offer?"),
        AIMessage(content="We offer CRM integration and analytics"),
    ]

    summary = llm_service._create_quick_summary(messages)

    assert isinstance(summary, str)
    assert len(summary) > 0
    assert len(summary) <= 200  # Should be truncated
    assert "Cliente mencionó:" in summary or "Bot respondió sobre:" in summary


# ============================================================================
# INTEGRATION TEST: All Optimizations Together
# ============================================================================

@pytest.mark.asyncio
async def test_full_conversation_with_all_optimizations(llm_service):
    """Integration test: Long conversation with custom prompts, RAG, and context optimization."""
    mock_response = MagicMock()
    mock_response.content = "Comprehensive response"

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    llm_service.gpt4o = mock_llm

    # Create long conversation
    messages = [
        HumanMessage(content=f"Message {i}") if i % 2 == 0
        else AIMessage(content=f"Response {i}")
        for i in range(20)
    ]

    # Add custom config and RAG
    config = {
        "use_emojis": True,
        "max_words_per_response": 100,
    }
    rag_context = "Product documentation: Advanced features available"

    response = await llm_service.generate_response(
        messages=messages,
        system_prompt="You are a sales assistant",
        use_emojis=True,
        rag_context=rag_context,
        config=config
    )

    assert response == "Comprehensive response"

    # Verify optimizations were applied
    call_args = mock_llm.ainvoke.call_args[0][0]

    # Should have: system prompt + optimized messages
    # Optimized messages should be < 20 (original count)
    message_count = len([msg for msg in call_args if isinstance(msg, (HumanMessage, AIMessage, SystemMessage))])
    assert message_count < 20 + 1  # +1 for system message

    # System message should include RAG instructions
    system_msg = call_args[0]
    assert "DOCUMENTACIÓN OFICIAL" in system_msg.content
    assert "Product documentation" in system_msg.content
