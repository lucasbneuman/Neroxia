"""Integration tests for multi-channel workflow (Phase 4B)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process_message_whatsapp_backwards_compat(sample_config):
    """Test WhatsApp flow with backwards compatible signature (user_phone)."""
    from graph.workflow import process_message
    from langchain_core.messages import HumanMessage

    # Mock LLM responses
    with patch('services.llm_service.get_llm_service') as mock_llm_getter:
        mock_llm = MagicMock()
        mock_llm.analyze_intent = AsyncMock(return_value=0.5)
        mock_llm.analyze_sentiment = AsyncMock(return_value="neutral")
        mock_llm.extract_data = AsyncMock(return_value={})
        mock_llm.generate_response = AsyncMock(return_value="Hello! How can I help you?")
        mock_llm.analyze_conversation_trends = MagicMock(return_value={
            "recommendation": "continue",
            "confidence": 0.8
        })
        mock_llm.build_adaptive_system_prompt = MagicMock(
            return_value="You are a helpful sales assistant."
        )
        mock_llm_getter.return_value = mock_llm

        # Mock RAG service
        with patch('services.rag_service.get_rag_service') as mock_rag_getter:
            mock_rag = MagicMock()
            mock_rag.get_collection_stats = MagicMock(return_value={'total_chunks': 0})
            mock_rag_getter.return_value = mock_rag

            # Mock HubSpot service
            with patch('services.hubspot_sync.get_hubspot_service') as mock_hubspot_getter:
                mock_hubspot = MagicMock()
                mock_hubspot.enabled = False
                mock_hubspot_getter.return_value = mock_hubspot

                # Test with old signature (user_phone only)
                result = await process_message(
                    user_phone="+1234567890",
                    message="Hello",
                    conversation_history=[],
                    config=sample_config,
                    db_session=None,
                    db_user=None
                )

                # Verify state was initialized correctly
                assert result["channel"] == "whatsapp"
                assert result["user_identifier"] == "+1234567890"
                assert result["user_phone"] == "+1234567890"
                assert result["current_response"] is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process_message_instagram(sample_config):
    """Test Instagram flow with new multi-channel signature."""
    from graph.workflow import process_message
    from langchain_core.messages import HumanMessage

    # Mock LLM responses
    with patch('services.llm_service.get_llm_service') as mock_llm_getter:
        mock_llm = MagicMock()
        mock_llm.analyze_intent = AsyncMock(return_value=0.5)
        mock_llm.analyze_sentiment = AsyncMock(return_value="neutral")
        mock_llm.extract_data = AsyncMock(return_value={})
        mock_llm.generate_response = AsyncMock(return_value="Hello from Instagram!")
        mock_llm.analyze_conversation_trends = MagicMock(return_value={
            "recommendation": "continue",
            "confidence": 0.8
        })
        mock_llm.build_adaptive_system_prompt = MagicMock(
            return_value="You are a helpful sales assistant."
        )
        mock_llm_getter.return_value = mock_llm

        # Mock RAG service
        with patch('services.rag_service.get_rag_service') as mock_rag_getter:
            mock_rag = MagicMock()
            mock_rag.get_collection_stats = MagicMock(return_value={'total_chunks': 0})
            mock_rag_getter.return_value = mock_rag

            # Mock HubSpot service
            with patch('services.hubspot_sync.get_hubspot_service') as mock_hubspot_getter:
                mock_hubspot = MagicMock()
                mock_hubspot.enabled = False
                mock_hubspot_getter.return_value = mock_hubspot

                # Test Instagram flow
                result = await process_message(
                    user_identifier="1234567890",  # PSID
                    message="Hello",
                    conversation_history=[],
                    config=sample_config,
                    channel="instagram",
                    channel_config={
                        "page_access_token": "test-token",
                        "page_id": "test-page-id"
                    },
                    db_session=None,
                    db_user=None
                )

                # Verify Instagram-specific state
                assert result["channel"] == "instagram"
                assert result["user_identifier"] == "1234567890"
                assert result["user_phone"] is None  # No phone for Instagram
                assert result["channel_config"]["page_access_token"] == "test-token"
                assert result["current_response"] is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process_message_messenger(sample_config):
    """Test Messenger flow with new multi-channel signature."""
    from graph.workflow import process_message

    # Mock LLM responses
    with patch('services.llm_service.get_llm_service') as mock_llm_getter:
        mock_llm = MagicMock()
        mock_llm.analyze_intent = AsyncMock(return_value=0.7)
        mock_llm.analyze_sentiment = AsyncMock(return_value="positive")
        mock_llm.extract_data = AsyncMock(return_value={
            "email": "user@example.com"
        })
        mock_llm.generate_response = AsyncMock(return_value="Hello from Messenger!")
        mock_llm.analyze_conversation_trends = MagicMock(return_value={
            "recommendation": "continue",
            "confidence": 0.8
        })
        mock_llm.build_adaptive_system_prompt = MagicMock(
            return_value="You are a helpful sales assistant."
        )
        mock_llm_getter.return_value = mock_llm

        # Mock RAG service
        with patch('services.rag_service.get_rag_service') as mock_rag_getter:
            mock_rag = MagicMock()
            mock_rag.get_collection_stats = MagicMock(return_value={'total_chunks': 0})
            mock_rag_getter.return_value = mock_rag

            # Mock HubSpot service
            with patch('services.hubspot_sync.get_hubspot_service') as mock_hubspot_getter:
                mock_hubspot = MagicMock()
                mock_hubspot.enabled = False
                mock_hubspot_getter.return_value = mock_hubspot

                # Test Messenger flow
                result = await process_message(
                    user_identifier="9876543210",  # PSID
                    message="I'm interested in your product",
                    conversation_history=[],
                    config=sample_config,
                    channel="messenger",
                    channel_config={
                        "page_access_token": "messenger-token",
                        "page_id": "messenger-page-id"
                    },
                    db_session=None,
                    db_user=None
                )

                # Verify Messenger-specific state
                assert result["channel"] == "messenger"
                assert result["user_identifier"] == "9876543210"
                assert result["user_phone"] is None  # No phone for Messenger
                assert result["channel_config"]["page_access_token"] == "messenger-token"
                assert result["user_email"] == "user@example.com"  # LLM extracted email
                assert result["current_response"] is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_data_collector_phone_optional_for_meta(sample_config):
    """Test that data_collector_node doesn't require phone for Instagram/Messenger."""
    from graph.nodes import data_collector_node
    from langchain_core.messages import HumanMessage

    # Mock LLM service
    with patch('services.llm_service.get_llm_service') as mock_llm_getter:
        mock_llm = MagicMock()
        mock_llm.extract_data = AsyncMock(return_value={
            "name": "John Doe",
            "email": "john@example.com"
        })
        mock_llm_getter.return_value = mock_llm

        # Mock HubSpot service
        with patch('services.hubspot_sync.get_hubspot_service') as mock_hubspot_getter:
            mock_hubspot = MagicMock()
            mock_hubspot.enabled = False
            mock_hubspot_getter.return_value = mock_hubspot

            # Create state for Instagram (no phone)
            state = {
                "messages": [HumanMessage(content="My name is John Doe")],
                "user_phone": None,  # No phone for Instagram
                "channel": "instagram",
                "user_identifier": "1234567890",  # PSID
                "channel_config": {"page_access_token": "token"},
                "user_name": None,
                "user_email": None,
                "collected_data": {},
                "config": sample_config,
                "db_session": None,
                "db_user": None,
            }

            # Run data collector
            updates = await data_collector_node(state)

            # Verify data was collected even without phone
            assert updates.get("user_name") == "John Doe"
            assert updates.get("user_email") == "john@example.com"
            assert "collected_data" in updates


@pytest.mark.integration
@pytest.mark.asyncio
async def test_workflow_raises_error_without_identifier(sample_config):
    """Test that process_message raises error if neither user_identifier nor user_phone provided."""
    from graph.workflow import process_message

    with pytest.raises(ValueError, match="Either user_identifier or user_phone must be provided"):
        await process_message(
            message="Hello",
            conversation_history=[],
            config=sample_config,
            db_session=None,
            db_user=None
        )
