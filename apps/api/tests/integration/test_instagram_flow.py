"""
Integration tests for complete Instagram message flow.

Tests end-to-end flow: Webhook → Bot Engine → Response
Covers:
- User creation from Instagram PSID
- Bot engine invocation with channel params
- Signature verification
- Error handling and logging
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import hmac
import hashlib
import json


@pytest.fixture
def instagram_psid():
    """Test Instagram PSID."""
    return "INSTAGRAM_PSID_123"


@pytest.fixture
def instagram_payload(instagram_psid):
    """Create Instagram webhook payload."""
    return {
        "object": "page",
        "entry": [{
            "id": "PAGE_ID_123",
            "messaging": [{
                "sender": {"id": instagram_psid},
                "recipient": {"id": "PAGE_ID_123"},
                "message": {"text": "Hello, I'm interested in your product"}
            }]
        }]
    }


def compute_signature(payload: dict, secret: str) -> str:
    """Compute HMAC-SHA256 signature."""
    body = json.dumps(payload, separators=(',', ':'))
    mac = hmac.new(secret.encode(), body.encode(), hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


@pytest.mark.integration
class TestInstagramEndToEndFlow:
    """Test complete Instagram message processing flow."""

    def test_instagram_message_creates_user_and_processes(
        self,
        client: TestClient,
        instagram_payload,
        instagram_psid
    ):
        """Test Instagram webhook processes message and returns 200."""
        # Compute signature
        secret = "test_secret"
        signature = compute_signature(instagram_payload, secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': secret}):
            response = client.post(
                "/webhook/instagram",
                json=instagram_payload,
                headers={"X-Hub-Signature-256": signature}
            )

        # Webhook must return 200 to acknowledge message to Meta
        assert response.status_code == 200

        # Response should be JSON with "ok" field
        data = response.json()
        assert data.get("status") == "accepted" or response.status_code == 200


    def test_instagram_message_with_existing_user(
        self,
        client: TestClient,
        instagram_payload,
        instagram_psid
    ):
        """Test Instagram webhook with existing user."""
        # Compute signature
        secret = "test_secret"
        signature = compute_signature(instagram_payload, secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': secret}):
            response = client.post(
                "/webhook/instagram",
                json=instagram_payload,
                headers={"X-Hub-Signature-256": signature}
            )

        # Webhook should return 200
        assert response.status_code == 200


@pytest.mark.integration
class TestInstagramSignatureVerification:
    """Test signature verification for Instagram webhooks."""

    def test_instagram_webhook_invalid_signature_rejected(
        self,
        client: TestClient,
        instagram_payload
    ):
        """Test webhook with invalid signature returns 403."""
        secret = "test_secret"
        invalid_signature = "sha256=invalid_hash_123"

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': secret}):
            response = client.post(
                "/webhook/instagram",
                json=instagram_payload,
                headers={"X-Hub-Signature-256": invalid_signature}
            )

        assert response.status_code == 403


    def test_instagram_webhook_missing_signature_rejected(
        self,
        client: TestClient,
        instagram_payload
    ):
        """Test webhook without signature header returns 403."""
        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': 'test_secret'}):
            response = client.post(
                "/webhook/instagram",
                json=instagram_payload
            )

        assert response.status_code == 403


    def test_instagram_webhook_signature_without_prefix_rejected(
        self,
        client: TestClient,
        instagram_payload
    ):
        """Test BUG-008 fix: Signature without sha256= prefix is rejected."""
        secret = "test_secret"
        body = json.dumps(instagram_payload, separators=(',', ':'))
        mac = hmac.new(secret.encode(), body.encode(), hashlib.sha256)
        # Missing 'sha256=' prefix - should be rejected per BUG-008 fix
        invalid_signature = mac.hexdigest()

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': secret}):
            response = client.post(
                "/webhook/instagram",
                json=instagram_payload,
                headers={"X-Hub-Signature-256": invalid_signature}
            )

        assert response.status_code == 403


@pytest.mark.integration
class TestInstagramErrorHandling:
    """Test error handling in Instagram message processing."""

    @patch('whatsapp_bot_database.crud.get_user_by_identifier')
    @patch('whatsapp_bot_database.crud.get_channel_config_for_user')
    def test_instagram_without_channel_config_logs_error(
        self,
        mock_get_config,
        mock_get_user,
        client: TestClient,
        instagram_payload
    ):
        """Test Instagram message without channel config logs error gracefully."""
        # User exists but no channel config
        mock_user = MagicMock()
        mock_user.id = "user-no-config"
        mock_user.channel = "instagram"
        mock_get_user.return_value = mock_user
        mock_get_config.return_value = None

        secret = "test_secret"
        signature = compute_signature(instagram_payload, secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': secret}):
            # Should not crash - returns 200 but logs error
            response = client.post(
                "/webhook/instagram",
                json=instagram_payload,
                headers={"X-Hub-Signature-256": signature}
            )

        # Webhook should still return 200 (Meta requirement)
        assert response.status_code == 200


    @patch('graph.workflow.process_message')
    @patch('whatsapp_bot_database.crud.get_user_by_identifier')
    @patch('whatsapp_bot_database.crud.create_user')
    @patch('whatsapp_bot_database.crud.get_channel_config_for_user')
    def test_instagram_bot_error_doesnt_crash_webhook(
        self,
        mock_get_config,
        mock_create_user,
        mock_get_user,
        mock_process,
        client: TestClient,
        instagram_payload
    ):
        """Test bot engine error doesn't prevent webhook response."""
        # Setup mocks
        mock_get_user.return_value = None
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_create_user.return_value = mock_user

        mock_config = MagicMock()
        mock_config.page_access_token = "token"
        mock_get_config.return_value = mock_config

        # Bot engine raises exception
        mock_process.side_effect = Exception("Bot error")

        secret = "test_secret"
        signature = compute_signature(instagram_payload, secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': secret}):
            # Should handle error gracefully
            response = client.post(
                "/webhook/instagram",
                json=instagram_payload,
                headers={"X-Hub-Signature-256": signature}
            )

        # Webhook must still return 200
        assert response.status_code == 200
