"""Unit tests for MetaSenderService (Instagram/Messenger)."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from services.meta_sender import MetaSenderService, Channel


@pytest.mark.anyio
async def test_instagram_character_truncation():
    """Test Instagram messages are truncated to 1000 characters."""
    # Mock httpx
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message_id": "mid.12345"}

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client  # Context manager support
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        service = MetaSenderService(
            page_access_token="test-token",
            page_id="page123",
            channel=Channel.INSTAGRAM
        )

        # Send message > 1000 chars
        long_message = "A" * 1500
        result = await service.send_message(
            recipient_id="1234567890",
            message_text=long_message,
            truncate=True
        )

    # Verify message was truncated
    call_args = mock_client.post.call_args
    sent_message = call_args.kwargs["json"]["message"]["text"]

    assert len(sent_message) == 1000  # Exactly 1000 chars
    assert sent_message.endswith("...")  # Has ellipsis
    assert result["status"] == "sent"


@pytest.mark.anyio
async def test_messenger_character_truncation():
    """Test Messenger messages are truncated to 2000 characters."""
    # Mock httpx
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message_id": "mid.67890"}

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        service = MetaSenderService(
            page_access_token="test-token",
            page_id="page456",
            channel=Channel.MESSENGER
        )

        # Send message > 2000 chars
        long_message = "B" * 2500
        result = await service.send_message(
            recipient_id="9876543210",
            message_text=long_message,
            truncate=True
        )

    # Verify message was truncated
    call_args = mock_client.post.call_args
    sent_message = call_args.kwargs["json"]["message"]["text"]

    assert len(sent_message) == 2000  # Exactly 2000 chars
    assert sent_message.endswith("...")  # Has ellipsis
    assert result["status"] == "sent"


@pytest.mark.anyio
async def test_no_truncation_when_disabled():
    """Test message fails when truncate=False and message exceeds limit."""
    service = MetaSenderService(
        page_access_token="test-token",
        page_id="page123",
        channel=Channel.INSTAGRAM
    )

    # Send message > 1000 chars with truncate=False
    long_message = "C" * 1500
    result = await service.send_message(
        recipient_id="1234567890",
        message_text=long_message,
        truncate=False
    )

    # Should fail without sending
    assert result["status"] == "failed"
    assert "exceeds 1000 character limit" in result["error"]
    assert result["message_id"] is None


@pytest.mark.anyio
async def test_successful_message_send():
    """Test successful message send returns correct response."""
    # Mock httpx
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message_id": "mid.success123"}

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        service = MetaSenderService(
            page_access_token="test-token",
            page_id="page123",
            channel=Channel.INSTAGRAM
        )

        result = await service.send_message(
            recipient_id="1234567890",
            message_text="Hello, world!"
        )

    # Verify response
    assert result["status"] == "sent"
    assert result["recipient_id"] == "1234567890"
    assert result["message_id"] == "mid.success123"
    assert result["error"] is None

    # Verify API call
    call_args = mock_client.post.call_args
    assert call_args.args[0] == "https://graph.facebook.com/v18.0/page123/messages"
    assert call_args.kwargs["params"]["access_token"] == "test-token"
    assert call_args.kwargs["json"]["recipient"]["id"] == "1234567890"
    assert call_args.kwargs["json"]["message"]["text"] == "Hello, world!"


@pytest.mark.anyio
async def test_retry_on_rate_limit():
    """Test retry logic on HTTP 429 rate limit."""
    # Mock httpx - first 2 calls fail with 429, third succeeds
    mock_responses = [
        MagicMock(status_code=429),
        MagicMock(status_code=429),
        MagicMock(status_code=200, json=lambda: {"message_id": "mid.retry123"})
    ]

    mock_client = AsyncMock()
    mock_client.post.side_effect = mock_responses

    with patch("httpx.AsyncClient", return_value=mock_client):
        with patch("asyncio.sleep", new_callable=AsyncMock):  # Mock sleep to speed up test
            service = MetaSenderService(
                page_access_token="test-token",
                page_id="page123",
                channel=Channel.INSTAGRAM
            )

            result = await service.send_message(
                recipient_id="1234567890",
                message_text="Retry test"
            )

    # Should succeed after retries
    assert result["status"] == "sent"
    assert result["message_id"] == "mid.retry123"
    assert mock_client.post.call_count == 3  # 2 failures + 1 success


@pytest.mark.anyio
async def test_retry_on_meta_rate_limit_error_code():
    """Test retry logic on Meta API rate limit error codes (4, 17, 32, 613)."""
    # Mock httpx - first call fails with error code 4, second succeeds
    mock_error_response = MagicMock(
        status_code=400,
        text='{"error": {"code": 4, "message": "Rate limit exceeded"}}',
        json=lambda: {"error": {"code": 4, "message": "Rate limit exceeded"}}
    )
    mock_success_response = MagicMock(
        status_code=200,
        json=lambda: {"message_id": "mid.retry456"}
    )

    mock_client = AsyncMock()
    mock_client.post.side_effect = [mock_error_response, mock_success_response]

    with patch("httpx.AsyncClient", return_value=mock_client):
        with patch("asyncio.sleep", new_callable=AsyncMock):
            service = MetaSenderService(
                page_access_token="test-token",
                page_id="page123",
                channel=Channel.INSTAGRAM
            )

            result = await service.send_message(
                recipient_id="1234567890",
                message_text="Error code retry test"
            )

    # Should succeed after retry
    assert result["status"] == "sent"
    assert result["message_id"] == "mid.retry456"
    assert mock_client.post.call_count == 2


@pytest.mark.anyio
async def test_max_retries_exhausted():
    """Test failure after max retries exhausted."""
    # Mock httpx - all 3 attempts fail with 429
    mock_response = MagicMock(status_code=429)

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        with patch("asyncio.sleep", new_callable=AsyncMock):
            service = MetaSenderService(
                page_access_token="test-token",
                page_id="page123",
                channel=Channel.INSTAGRAM
            )

            result = await service.send_message(
                recipient_id="1234567890",
                message_text="Max retry test"
            )

    # Should fail after max retries
    assert result["status"] == "failed"
    assert result["message_id"] is None
    assert "Rate limit exceeded" in result["error"]
    assert mock_client.post.call_count == 3  # MAX_RETRIES


@pytest.mark.anyio
async def test_non_retryable_error():
    """Test non-retryable errors fail immediately."""
    # Mock httpx - 401 Unauthorized (not retryable)
    mock_response = MagicMock(
        status_code=401,
        text='{"error": {"code": 190, "message": "Invalid OAuth token"}}',
        json=lambda: {"error": {"code": 190, "message": "Invalid OAuth token"}}
    )

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        service = MetaSenderService(
            page_access_token="invalid-token",
            page_id="page123",
            channel=Channel.INSTAGRAM
        )

        result = await service.send_message(
            recipient_id="1234567890",
            message_text="Auth error test"
        )

    # Should fail immediately without retry
    assert result["status"] == "failed"
    assert "Invalid OAuth token" in result["error"]
    assert mock_client.post.call_count == 1  # No retries


@pytest.mark.anyio
async def test_timeout_exception():
    """Test timeout exceptions trigger retry."""
    # Mock httpx - first 2 timeouts, third succeeds
    mock_success = MagicMock(status_code=200, json=lambda: {"message_id": "mid.timeout123"})

    mock_client = AsyncMock()
    mock_client.post.side_effect = [
        httpx.TimeoutException("Timeout 1"),
        httpx.TimeoutException("Timeout 2"),
        mock_success
    ]

    with patch("httpx.AsyncClient", return_value=mock_client):
        with patch("asyncio.sleep", new_callable=AsyncMock):
            service = MetaSenderService(
                page_access_token="test-token",
                page_id="page123",
                channel=Channel.INSTAGRAM
            )

            result = await service.send_message(
                recipient_id="1234567890",
                message_text="Timeout test"
            )

    # Should succeed after retries
    assert result["status"] == "sent"
    assert result["message_id"] == "mid.timeout123"
    assert mock_client.post.call_count == 3


@pytest.mark.anyio
async def test_typing_indicator_on():
    """Test sending typing_on indicator."""
    # Mock httpx
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"recipient_id": "1234567890"}

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        service = MetaSenderService(
            page_access_token="test-token",
            page_id="page123",
            channel=Channel.INSTAGRAM
        )

        result = await service.send_typing_indicator(
            recipient_id="1234567890",
            typing_on=True
        )

    # Verify response
    assert result["status"] == "sent"
    assert result["recipient_id"] == "1234567890"
    assert result["message_id"] is None  # Typing indicators don't have message IDs

    # Verify API call
    call_args = mock_client.post.call_args
    assert call_args.kwargs["json"]["sender_action"] == "typing_on"


@pytest.mark.anyio
async def test_typing_indicator_off():
    """Test sending typing_off indicator."""
    # Mock httpx
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_client):
        service = MetaSenderService(
            page_access_token="test-token",
            page_id="page123",
            channel=Channel.MESSENGER
        )

        result = await service.send_typing_indicator(
            recipient_id="9876543210",
            typing_on=False
        )

    # Verify API call
    call_args = mock_client.post.call_args
    assert call_args.kwargs["json"]["sender_action"] == "typing_off"
    assert result["status"] == "sent"


@pytest.mark.anyio
async def test_truncate_message_helper():
    """Test _truncate_message helper function."""
    # Test truncation
    result = MetaSenderService._truncate_message("A" * 100, 50)
    assert len(result) == 50
    assert result.endswith("...")
    assert result == ("A" * 47) + "..."

    # Test no truncation needed
    result = MetaSenderService._truncate_message("Short", 100)
    assert result == "Short"


def test_httpx_import_error():
    """Test that MetaSenderService raises error when httpx is not installed."""
    # Temporarily remove httpx
    import services.meta_sender as meta_module
    original_httpx = meta_module.httpx
    meta_module.httpx = None

    try:
        with pytest.raises(ImportError) as exc_info:
            MetaSenderService(
                page_access_token="test-token",
                page_id="page123",
                channel=Channel.INSTAGRAM
            )
        assert "httpx is required" in str(exc_info.value)
    finally:
        # Restore httpx
        meta_module.httpx = original_httpx
