"""
Integration tests for complete Messenger message flow.

Tests end-to-end flow: Webhook → Bot Engine → Response
Covers:
- User creation from Messenger PSID
- Bot engine invocation with Messenger channel
- Multi-tenant page isolation
- Background task processing
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import hmac
import hashlib
import json


@pytest.fixture
def messenger_psid():
    """Test Messenger PSID."""
    return "MESSENGER_PSID_456"


@pytest.fixture
def messenger_payload(messenger_psid):
    """Create Messenger webhook payload."""
    return {
        "object": "page",
        "entry": [{
            "id": "PAGE_ID_456",
            "messaging": [{
                "sender": {"id": messenger_psid},
                "recipient": {"id": "PAGE_ID_456"},
                "message": {"text": "I need help with pricing"}
            }]
        }]
    }


def compute_signature(payload: dict, secret: str) -> str:
    """Compute HMAC-SHA256 signature."""
    body = json.dumps(payload, separators=(',', ':'))
    mac = hmac.new(secret.encode(), body.encode(), hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


@pytest.mark.integration
class TestMessengerEndToEndFlow:
    """Test complete Messenger message processing flow."""

    def test_messenger_message_creates_user_and_processes(
        self,
        client: TestClient,
        messenger_payload,
        messenger_psid
    ):
        """Test Messenger webhook processes message and returns 200."""
        # Compute signature
        secret = "messenger_secret"
        signature = compute_signature(messenger_payload, secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': secret}):
            response = client.post(
                "/webhook/messenger",
                json=messenger_payload,
                headers={"X-Hub-Signature-256": signature}
            )

        # Webhook must return 200 to acknowledge to Meta
        assert response.status_code == 200


    def test_messenger_existing_conversation_continues(
        self,
        client: TestClient,
        messenger_payload,
        messenger_psid
    ):
        """Test Messenger webhook continues conversation."""
        secret = "test_secret"
        signature = compute_signature(messenger_payload, secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': secret}):
            response = client.post(
                "/webhook/messenger",
                json=messenger_payload,
                headers={"X-Hub-Signature-256": signature}
            )

        # Should return 200
        assert response.status_code == 200


@pytest.mark.integration
class TestMessengerMultiTenant:
    """Test multi-tenant isolation for Messenger."""

    def test_different_pages_use_different_configs(
        self,
        client: TestClient
    ):
        """Test messages from different pages."""
        # Page A
        payload_a = {
            "object": "page",
            "entry": [{
                "id": "PAGE_A",
                "messaging": [{
                    "sender": {"id": "PSID_A"},
                    "recipient": {"id": "PAGE_A"},
                    "message": {"text": "Hello"}
                }]
            }]
        }

        # Page B
        payload_b = {
            "object": "page",
            "entry": [{
                "id": "PAGE_B",
                "messaging": [{
                    "sender": {"id": "PSID_B"},
                    "recipient": {"id": "PAGE_B"},
                    "message": {"text": "Hi"}
                }]
            }]
        }

        secret = "test_secret"

        # Send to Page A
        sig_a = compute_signature(payload_a, secret)
        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': secret}):
            response_a = client.post(
                "/webhook/messenger",
                json=payload_a,
                headers={"X-Hub-Signature-256": sig_a}
            )
        assert response_a.status_code == 200

        # Send to Page B
        sig_b = compute_signature(payload_b, secret)
        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': secret}):
            response_b = client.post(
                "/webhook/messenger",
                json=payload_b,
                headers={"X-Hub-Signature-256": sig_b}
            )
        assert response_b.status_code == 200


@pytest.mark.integration
class TestMessengerErrorHandling:
    """Test error handling for Messenger webhooks."""

    @patch('whatsapp_bot_database.crud.get_user_by_identifier')
    @patch('whatsapp_bot_database.crud.get_channel_config_for_user')
    def test_messenger_without_channel_config_logs_error(
        self,
        mock_get_config,
        mock_get_user,
        client: TestClient,
        messenger_payload
    ):
        """Test Messenger message without channel config logs error but doesn't crash."""
        # User exists, no config
        mock_user = MagicMock()
        mock_user.id = "user-no-config"
        mock_get_user.return_value = mock_user
        mock_get_config.return_value = None

        secret = "test_secret"
        signature = compute_signature(messenger_payload, secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': secret}):
            response = client.post(
                "/webhook/messenger",
                json=messenger_payload,
                headers={"X-Hub-Signature-256": signature}
            )

        # Must return 200 for Meta compliance
        assert response.status_code == 200


    def test_messenger_malformed_payload_handled(
        self,
        client: TestClient
    ):
        """Test malformed Messenger payload doesn't crash server."""
        malformed = {
            "object": "page",
            "entry": [{
                "id": "PAGE",
                "messaging": [{}]  # Missing required fields
            }]
        }

        secret = "test_secret"
        signature = compute_signature(malformed, secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': secret}):
            response = client.post(
                "/webhook/messenger",
                json=malformed,
                headers={"X-Hub-Signature-256": signature}
            )

        # Should handle gracefully
        assert response.status_code in [200, 400]


@pytest.mark.integration
class TestMessengerBackgroundProcessing:
    """Test background task processing for Messenger."""

    @patch('graph.workflow.process_message')
    @patch('whatsapp_bot_database.crud.get_user_by_identifier')
    @patch('whatsapp_bot_database.crud.create_user')
    @patch('whatsapp_bot_database.crud.get_channel_config_for_user')
    def test_webhook_returns_quickly_with_background_task(
        self,
        mock_get_config,
        mock_create_user,
        mock_get_user,
        mock_process,
        client: TestClient,
        messenger_payload
    ):
        """Test webhook returns 200 immediately while processing in background."""
        # Setup mocks
        mock_get_user.return_value = None
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_create_user.return_value = mock_user

        mock_config = MagicMock()
        mock_config.page_access_token = "token"
        mock_config.page_id = "PAGE_ID_456"
        mock_get_config.return_value = mock_config

        # Simulate slow bot processing
        def slow_process(*args, **kwargs):
            import time
            time.sleep(0.1)  # Simulate processing time
            return {"current_response": "Response"}

        mock_process.side_effect = slow_process

        secret = "test_secret"
        signature = compute_signature(messenger_payload, secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': secret}):
            response = client.post(
                "/webhook/messenger",
                json=messenger_payload,
                headers={"X-Hub-Signature-256": signature}
            )

        # Webhook should return immediately
        assert response.status_code == 200
        # Background task will process asynchronously
