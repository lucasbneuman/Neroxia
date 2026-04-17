"""Unit tests for MessageSender (multi-channel dispatcher)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.message_sender import MessageSender


@pytest.mark.anyio
async def test_whatsapp_routing():
    """Test MessageSender routes WhatsApp messages to Twilio."""
    # Mock TwilioService
    mock_twilio = MagicMock()
    mock_twilio.send_message.return_value = {
        "sid": "SM12345",
        "status": "queued",
        "to": "whatsapp:+1234567890"
    }

    with patch("services.message_sender.get_twilio_service", return_value=mock_twilio):
        result = await MessageSender.send_message(
            channel="whatsapp",
            recipient_identifier="+1234567890",
            message_text="Hello from WhatsApp",
            channel_config=None  # WhatsApp doesn't need config
        )

    # Verify Twilio was called
    mock_twilio.send_message.assert_called_once_with("+1234567890", "Hello from WhatsApp")

    # Verify response format
    assert result["status"] == "sent"
    assert result["channel"] == "whatsapp"
    assert result["recipient"] == "+1234567890"
    assert result["message_id"] == "SM12345"
    assert result["error"] is None


@pytest.mark.anyio
async def test_instagram_routing():
    """Test MessageSender routes Instagram messages to Meta Graph API."""
    # Mock MetaSenderService
    mock_meta = AsyncMock()
    mock_meta.send_message.return_value = {
        "status": "sent",
        "recipient_id": "1234567890",
        "message_id": "mid.12345",
        "error": None
    }

    with patch("services.message_sender.MetaSenderService", return_value=mock_meta):
        result = await MessageSender.send_message(
            channel="instagram",
            recipient_identifier="1234567890",
            message_text="Hello from Instagram",
            channel_config={
                "page_access_token": "test-token",
                "page_id": "page123"
            }
        )

    # Verify Meta sender was called
    mock_meta.send_message.assert_called_once_with("1234567890", "Hello from Instagram")

    # Verify response format
    assert result["status"] == "sent"
    assert result["channel"] == "instagram"
    assert result["recipient"] == "1234567890"  # Normalized from recipient_id
    assert result["message_id"] == "mid.12345"
    assert result["error"] is None


@pytest.mark.anyio
async def test_messenger_routing():
    """Test MessageSender routes Messenger messages to Meta Graph API."""
    # Mock MetaSenderService
    mock_meta = AsyncMock()
    mock_meta.send_message.return_value = {
        "status": "sent",
        "recipient_id": "9876543210",
        "message_id": "mid.67890",
        "error": None
    }

    with patch("services.message_sender.MetaSenderService", return_value=mock_meta):
        result = await MessageSender.send_message(
            channel="messenger",
            recipient_identifier="9876543210",
            message_text="Hello from Messenger",
            channel_config={
                "page_access_token": "test-token-2",
                "page_id": "page456"
            }
        )

    # Verify Meta sender was called
    mock_meta.send_message.assert_called_once_with("9876543210", "Hello from Messenger")

    # Verify response format
    assert result["status"] == "sent"
    assert result["channel"] == "messenger"
    assert result["recipient"] == "9876543210"
    assert result["message_id"] == "mid.67890"
    assert result["error"] is None


@pytest.mark.anyio
async def test_unsupported_channel_error():
    """Test MessageSender raises error for unsupported channel."""
    result = await MessageSender.send_message(
        channel="telegram",  # Not supported
        recipient_identifier="test123",
        message_text="Hello",
        channel_config=None
    )

    # Should return error response
    assert result["status"] == "failed"
    assert result["channel"] == "telegram"
    assert result["recipient"] == "test123"
    assert result["message_id"] is None
    assert "Unsupported channel" in result["error"]
    assert "telegram" in result["error"]


@pytest.mark.anyio
async def test_missing_channel_config_error():
    """Test MessageSender fails when Meta channel lacks config."""
    result = await MessageSender.send_message(
        channel="instagram",
        recipient_identifier="1234567890",
        message_text="Hello",
        channel_config=None  # Missing required config
    )

    # Should return error response
    assert result["status"] == "failed"
    assert result["channel"] == "instagram"
    assert result["recipient"] == "1234567890"
    assert result["message_id"] is None
    assert "channel_config is required" in result["error"]


@pytest.mark.anyio
async def test_missing_page_access_token():
    """Test MessageSender fails when page_access_token is missing."""
    result = await MessageSender.send_message(
        channel="instagram",
        recipient_identifier="1234567890",
        message_text="Hello",
        channel_config={
            "page_id": "page123"  # Missing page_access_token
        }
    )

    # Should return error response
    assert result["status"] == "failed"
    assert "page_access_token is required" in result["error"]


@pytest.mark.anyio
async def test_missing_page_id():
    """Test MessageSender fails when page_id is missing."""
    result = await MessageSender.send_message(
        channel="messenger",
        recipient_identifier="1234567890",
        message_text="Hello",
        channel_config={
            "page_access_token": "test-token"  # Missing page_id
        }
    )

    # Should return error response
    assert result["status"] == "failed"
    assert "page_id is required" in result["error"]


@pytest.mark.anyio
async def test_twilio_delivery_failure():
    """Test MessageSender handles Twilio delivery failures."""
    # Mock Twilio returning failed status
    mock_twilio = MagicMock()
    mock_twilio.send_message.return_value = {
        "sid": "SM12345",
        "status": "failed",
        "error_message": "Invalid phone number"
    }

    with patch("services.message_sender.get_twilio_service", return_value=mock_twilio):
        result = await MessageSender.send_message(
            channel="whatsapp",
            recipient_identifier="+invalid",
            message_text="Hello",
            channel_config=None
        )

    # Should return failed status
    assert result["status"] == "failed"
    assert result["channel"] == "whatsapp"
    assert result["message_id"] == "SM12345"


@pytest.mark.anyio
async def test_meta_sender_exception_handling():
    """Test MessageSender handles exceptions from Meta sender."""
    # Mock MetaSenderService throwing exception
    mock_meta = AsyncMock()
    mock_meta.send_message.side_effect = Exception("Network error")

    with patch("services.message_sender.MetaSenderService", return_value=mock_meta):
        result = await MessageSender.send_message(
            channel="instagram",
            recipient_identifier="1234567890",
            message_text="Hello",
            channel_config={
                "page_access_token": "test-token",
                "page_id": "page123"
            }
        )

    # Should return error response
    assert result["status"] == "failed"
    assert result["channel"] == "instagram"
    assert result["message_id"] is None
    assert "Network error" in result["error"]


@pytest.mark.anyio
async def test_case_insensitive_channel():
    """Test MessageSender handles channel names case-insensitively."""
    mock_twilio = MagicMock()
    mock_twilio.send_message.return_value = {
        "sid": "SM12345",
        "status": "queued"
    }

    with patch("services.message_sender.get_twilio_service", return_value=mock_twilio):
        # Test uppercase channel name
        result = await MessageSender.send_message(
            channel="WHATSAPP",
            recipient_identifier="+1234567890",
            message_text="Hello",
            channel_config=None
        )

    assert result["status"] == "sent"
    assert result["channel"] == "whatsapp"  # Lowercased
