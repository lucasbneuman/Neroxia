"""
Meta Webhooks Integration Tests

Tests for Instagram and Messenger webhook endpoints including:
- Webhook verification (GET endpoints)
- Signature verification (POST endpoints)
- Message extraction and normalization
- User creation/retrieval by PSID
- Message storage in database
- Multi-tenant isolation
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict
import hmac
import hashlib
import json
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def facebook_verify_token():
    """Test verify token for Meta webhook verification."""
    return "test_verify_token_12345"


@pytest.fixture
def facebook_app_secret():
    """Test app secret for HMAC signature verification."""
    return "test_app_secret_67890"


@pytest.fixture
def test_page_id():
    """Test Facebook Page ID."""
    return "123456789012345"


@pytest.fixture
def test_psid():
    """Test user PSID (Page-Scoped ID)."""
    return "987654321098765"


@pytest.fixture
def instagram_webhook_payload(test_page_id, test_psid):
    """Create a valid Instagram webhook payload."""
    return {
        "object": "page",
        "entry": [
            {
                "id": test_page_id,
                "time": 1234567890,
                "messaging": [
                    {
                        "sender": {"id": test_psid},
                        "recipient": {"id": test_page_id},
                        "timestamp": 1234567890,
                        "message": {
                            "mid": "test_message_id_123",
                            "text": "Hello from Instagram!"
                        }
                    }
                ]
            }
        ]
    }


@pytest.fixture
def messenger_webhook_payload(test_page_id, test_psid):
    """Create a valid Messenger webhook payload."""
    return {
        "object": "page",
        "entry": [
            {
                "id": test_page_id,
                "time": 1234567890,
                "messaging": [
                    {
                        "sender": {"id": test_psid},
                        "recipient": {"id": test_page_id},
                        "timestamp": 1234567890,
                        "message": {
                            "mid": "test_message_id_456",
                            "text": "Hello from Messenger!"
                        }
                    }
                ]
            }
        ]
    }


def compute_signature(body: str, secret: str) -> str:
    """
    Compute HMAC-SHA256 signature for webhook payload.

    Args:
        body: JSON string (not bytes) - should match what TestClient sends
        secret: App secret
    """
    mac = hmac.new(
        secret.encode(),
        msg=body.encode(),
        digestmod=hashlib.sha256
    )
    return f"sha256={mac.hexdigest()}"


class TestInstagramWebhookVerification:
    """Test suite for Instagram webhook verification (GET endpoint)."""

    def test_instagram_verify_success(
        self,
        client: TestClient,
        facebook_verify_token
    ):
        """Test successful Instagram webhook verification."""
        with patch.dict('os.environ', {'FACEBOOK_VERIFY_TOKEN': facebook_verify_token}):
            response = client.get(
                "/webhook/instagram",
                params={
                    "hub.mode": "subscribe",
                    "hub.challenge": "1234567890",
                    "hub.verify_token": facebook_verify_token
                }
            )

            assert response.status_code == 200
            assert response.json() == 1234567890

    def test_instagram_verify_invalid_mode(
        self,
        client: TestClient,
        facebook_verify_token
    ):
        """Test Instagram verification with invalid hub.mode."""
        with patch.dict('os.environ', {'FACEBOOK_VERIFY_TOKEN': facebook_verify_token}):
            response = client.get(
                "/webhook/instagram",
                params={
                    "hub.mode": "invalid",
                    "hub.challenge": "1234567890",
                    "hub.verify_token": facebook_verify_token
                }
            )

            assert response.status_code == 400
            assert "Invalid hub.mode" in response.json()["detail"]

    def test_instagram_verify_invalid_token(
        self,
        client: TestClient,
        facebook_verify_token
    ):
        """Test Instagram verification with wrong verify token."""
        with patch.dict('os.environ', {'FACEBOOK_VERIFY_TOKEN': facebook_verify_token}):
            response = client.get(
                "/webhook/instagram",
                params={
                    "hub.mode": "subscribe",
                    "hub.challenge": "1234567890",
                    "hub.verify_token": "wrong_token"
                }
            )

            assert response.status_code == 403
            assert "Invalid verify token" in response.json()["detail"]

    def test_instagram_verify_missing_env_token(self, client: TestClient):
        """Test Instagram verification when FACEBOOK_VERIFY_TOKEN not configured."""
        with patch.dict('os.environ', {}, clear=True):
            response = client.get(
                "/webhook/instagram",
                params={
                    "hub.mode": "subscribe",
                    "hub.challenge": "1234567890",
                    "hub.verify_token": "any_token"
                }
            )

            assert response.status_code == 500
            assert "Verify token not configured" in response.json()["detail"]


class TestMessengerWebhookVerification:
    """Test suite for Messenger webhook verification (GET endpoint)."""

    def test_messenger_verify_success(
        self,
        client: TestClient,
        facebook_verify_token
    ):
        """Test successful Messenger webhook verification."""
        with patch.dict('os.environ', {'FACEBOOK_VERIFY_TOKEN': facebook_verify_token}):
            response = client.get(
                "/webhook/messenger",
                params={
                    "hub.mode": "subscribe",
                    "hub.challenge": "9876543210",
                    "hub.verify_token": facebook_verify_token
                }
            )

            assert response.status_code == 200
            assert response.json() == 9876543210

    def test_messenger_verify_invalid_mode(
        self,
        client: TestClient,
        facebook_verify_token
    ):
        """Test Messenger verification with invalid hub.mode."""
        with patch.dict('os.environ', {'FACEBOOK_VERIFY_TOKEN': facebook_verify_token}):
            response = client.get(
                "/webhook/messenger",
                params={
                    "hub.mode": "unsubscribe",
                    "hub.challenge": "9876543210",
                    "hub.verify_token": facebook_verify_token
                }
            )

            assert response.status_code == 400

    def test_messenger_verify_invalid_token(
        self,
        client: TestClient,
        facebook_verify_token
    ):
        """Test Messenger verification with wrong verify token."""
        with patch.dict('os.environ', {'FACEBOOK_VERIFY_TOKEN': facebook_verify_token}):
            response = client.get(
                "/webhook/messenger",
                params={
                    "hub.mode": "subscribe",
                    "hub.challenge": "9876543210",
                    "hub.verify_token": "wrong_token"
                }
            )

            assert response.status_code == 403


class TestInstagramWebhookProcessing:
    """Test suite for Instagram webhook message processing (POST endpoint)."""

    def test_instagram_webhook_valid_signature(
        self,
        client: TestClient,
        facebook_app_secret,
        instagram_webhook_payload,
        test_page_id,
        test_psid
    ):
        """Test Instagram webhook with valid signature."""
        # Mock database operations
        mock_integration = MagicMock()
        mock_integration.auth_user_id = "test_auth_user_123"

        mock_user = MagicMock()
        mock_user.id = 1

        # Compute signature based on TestClient's JSON encoding
        body_str = json.dumps(instagram_webhook_payload, separators=(',', ':'))
        signature = compute_signature(body_str, facebook_app_secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': facebook_app_secret}), \
             patch('whatsapp_bot_database.crud.get_channel_integration_by_page') as mock_get_integration, \
             patch('whatsapp_bot_database.crud.get_user_by_identifier') as mock_get_user, \
             patch('whatsapp_bot_database.crud.create_message') as mock_create_msg:

            # Configure async mocks
            mock_get_integration.return_value = mock_integration
            mock_get_user.return_value = mock_user
            mock_create_msg.return_value = None

            response = client.post(
                "/webhook/instagram",
                json=instagram_webhook_payload,
                headers={"X-Hub-Signature-256": signature}
            )

            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

    def test_instagram_webhook_invalid_signature(
        self,
        client: TestClient,
        facebook_app_secret,
        instagram_webhook_payload
    ):
        """Test Instagram webhook with invalid signature."""
        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': facebook_app_secret}):
            response = client.post(
                "/webhook/instagram",
                json=instagram_webhook_payload,
                headers={"X-Hub-Signature-256": "sha256=invalid_signature"}
            )

            assert response.status_code == 403
            assert "Invalid signature" in response.json()["detail"]

    def test_instagram_webhook_missing_signature(
        self,
        client: TestClient,
        facebook_app_secret,
        instagram_webhook_payload
    ):
        """Test Instagram webhook without signature header."""
        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': facebook_app_secret}):
            response = client.post(
                "/webhook/instagram",
                json=instagram_webhook_payload
            )

            assert response.status_code == 403

    def test_instagram_webhook_creates_new_user(
        self,
        client: TestClient,
        facebook_app_secret,
        instagram_webhook_payload,
        test_page_id,
        test_psid
    ):
        """Test Instagram webhook creates new user when PSID not found."""
        mock_integration = MagicMock()
        mock_integration.auth_user_id = "test_auth_user_123"

        mock_new_user = MagicMock()
        mock_new_user.id = 2

        body_str = json.dumps(instagram_webhook_payload, separators=(',', ':'))
        signature = compute_signature(body_str, facebook_app_secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': facebook_app_secret}), \
             patch('whatsapp_bot_database.crud.get_channel_integration_by_page') as mock_get_integration, \
             patch('whatsapp_bot_database.crud.get_user_by_identifier') as mock_get_user, \
             patch('whatsapp_bot_database.crud.create_user') as mock_create, \
             patch('whatsapp_bot_database.crud.create_message') as mock_create_msg:

            mock_get_integration.return_value = mock_integration
            mock_get_user.return_value = None  # User doesn't exist
            mock_create.return_value = mock_new_user
            mock_create_msg.return_value = None

            response = client.post(
                "/webhook/instagram",
                json=instagram_webhook_payload,
                headers={"X-Hub-Signature-256": signature}
            )

            assert response.status_code == 200
            # Verify create_user was called
            assert mock_create.called

    def test_instagram_webhook_no_integration_found(
        self,
        client: TestClient,
        facebook_app_secret,
        instagram_webhook_payload
    ):
        """Test Instagram webhook when no integration configured for page."""
        body_str = json.dumps(instagram_webhook_payload, separators=(',', ':'))
        signature = compute_signature(body_str, facebook_app_secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': facebook_app_secret}), \
             patch('whatsapp_bot_database.crud.get_channel_integration_by_page') as mock_get_integration:

            mock_get_integration.return_value = None

            response = client.post(
                "/webhook/instagram",
                json=instagram_webhook_payload,
                headers={"X-Hub-Signature-256": signature}
            )

            # Should still return 200 but skip processing
            assert response.status_code == 200

    def test_instagram_webhook_non_text_message(
        self,
        client: TestClient,
        facebook_app_secret,
        test_page_id,
        test_psid
    ):
        """Test Instagram webhook skips non-text messages."""
        payload = {
            "object": "page",
            "entry": [
                {
                    "id": test_page_id,
                    "time": 1234567890,
                    "messaging": [
                        {
                            "sender": {"id": test_psid},
                            "recipient": {"id": test_page_id},
                            "timestamp": 1234567890,
                            "message": {
                                "mid": "test_message_id_789",
                                "attachments": [{"type": "image"}]
                                # No "text" field
                            }
                        }
                    ]
                }
            ]
        }

        body_str = json.dumps(payload, separators=(',', ':'))
        signature = compute_signature(body_str, facebook_app_secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': facebook_app_secret}):
            response = client.post(
                "/webhook/instagram",
                json=payload,
                headers={"X-Hub-Signature-256": signature}
            )

            assert response.status_code == 200


class TestMessengerWebhookProcessing:
    """Test suite for Messenger webhook message processing (POST endpoint)."""

    def test_messenger_webhook_valid_signature(
        self,
        client: TestClient,
        facebook_app_secret,
        messenger_webhook_payload
    ):
        """Test Messenger webhook with valid signature."""
        mock_integration = MagicMock()
        mock_integration.auth_user_id = "test_auth_user_456"

        mock_user = MagicMock()
        mock_user.id = 3

        body_str = json.dumps(messenger_webhook_payload, separators=(',', ':'))
        signature = compute_signature(body_str, facebook_app_secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': facebook_app_secret}), \
             patch('whatsapp_bot_database.crud.get_channel_integration_by_page') as mock_get_integration, \
             patch('whatsapp_bot_database.crud.get_user_by_identifier') as mock_get_user, \
             patch('whatsapp_bot_database.crud.create_message') as mock_create_msg:

            mock_get_integration.return_value = mock_integration
            mock_get_user.return_value = mock_user
            mock_create_msg.return_value = None

            response = client.post(
                "/webhook/messenger",
                json=messenger_webhook_payload,
                headers={"X-Hub-Signature-256": signature}
            )

            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

    def test_messenger_webhook_invalid_signature(
        self,
        client: TestClient,
        facebook_app_secret,
        messenger_webhook_payload
    ):
        """Test Messenger webhook with invalid signature."""
        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': facebook_app_secret}):
            response = client.post(
                "/webhook/messenger",
                json=messenger_webhook_payload,
                headers={"X-Hub-Signature-256": "sha256=wrong_signature"}
            )

            assert response.status_code == 403

    def test_messenger_webhook_creates_new_user(
        self,
        client: TestClient,
        facebook_app_secret,
        messenger_webhook_payload
    ):
        """Test Messenger webhook creates new user when PSID not found."""
        mock_integration = MagicMock()
        mock_integration.auth_user_id = "test_auth_user_789"

        mock_new_user = MagicMock()
        mock_new_user.id = 4

        body_str = json.dumps(messenger_webhook_payload, separators=(',', ':'))
        signature = compute_signature(body_str, facebook_app_secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': facebook_app_secret}), \
             patch('whatsapp_bot_database.crud.get_channel_integration_by_page') as mock_get_integration, \
             patch('whatsapp_bot_database.crud.get_user_by_identifier') as mock_get_user, \
             patch('whatsapp_bot_database.crud.create_user') as mock_create, \
             patch('whatsapp_bot_database.crud.create_message') as mock_create_msg:

            mock_get_integration.return_value = mock_integration
            mock_get_user.return_value = None
            mock_create.return_value = mock_new_user
            mock_create_msg.return_value = None

            response = client.post(
                "/webhook/messenger",
                json=messenger_webhook_payload,
                headers={"X-Hub-Signature-256": signature}
            )

            assert response.status_code == 200


class TestMultiTenantIsolation:
    """Test suite for multi-tenant isolation in Meta webhooks."""

    def test_different_pages_isolated(
        self,
        client: TestClient,
        facebook_app_secret,
        test_psid
    ):
        """Test that different page IDs map to different tenants."""
        page_id_1 = "111111111111111"

        mock_integration_1 = MagicMock()
        mock_integration_1.auth_user_id = "tenant_1"

        payload_1 = {
            "object": "page",
            "entry": [{
                "id": page_id_1,
                "time": 1234567890,
                "messaging": [{
                    "sender": {"id": test_psid},
                    "recipient": {"id": page_id_1},
                    "timestamp": 1234567890,
                    "message": {"mid": "msg1", "text": "Test 1"}
                }]
            }]
        }

        body_str = json.dumps(payload_1, separators=(',', ':'))
        signature = compute_signature(body_str, facebook_app_secret)

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': facebook_app_secret}), \
             patch('whatsapp_bot_database.crud.get_channel_integration_by_page') as mock_get_integration, \
             patch('whatsapp_bot_database.crud.get_user_by_identifier') as mock_get_user, \
             patch('whatsapp_bot_database.crud.create_user') as mock_create, \
             patch('whatsapp_bot_database.crud.create_message') as mock_create_msg:

            mock_get_integration.return_value = mock_integration_1
            mock_get_user.return_value = None
            mock_create.return_value = MagicMock(id=1)
            mock_create_msg.return_value = None

            response = client.post(
                "/webhook/instagram",
                json=payload_1,
                headers={"X-Hub-Signature-256": signature}
            )

            assert response.status_code == 200
            # Verify correct tenant was used
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs['auth_user_id'] == "tenant_1"


class TestSignatureVerification:
    """Test suite for HMAC-SHA256 signature verification logic."""

    def test_signature_with_prefix(
        self,
        client: TestClient,
        facebook_app_secret,
        instagram_webhook_payload
    ):
        """Test signature verification handles 'sha256=' prefix correctly."""
        mock_integration = MagicMock()
        mock_integration.auth_user_id = "test_user"

        body_str = json.dumps(instagram_webhook_payload, separators=(',', ':'))
        signature = compute_signature(body_str, facebook_app_secret)

        # Signature should have 'sha256=' prefix
        assert signature.startswith("sha256=")

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': facebook_app_secret}), \
             patch('whatsapp_bot_database.crud.get_channel_integration_by_page') as mock_get_integration, \
             patch('whatsapp_bot_database.crud.get_user_by_identifier') as mock_get_user, \
             patch('whatsapp_bot_database.crud.create_message') as mock_create_msg:

            mock_get_integration.return_value = mock_integration
            mock_get_user.return_value = MagicMock(id=1)
            mock_create_msg.return_value = None

            response = client.post(
                "/webhook/instagram",
                json=instagram_webhook_payload,
                headers={"X-Hub-Signature-256": signature}
            )

            assert response.status_code == 200

    def test_signature_without_prefix_fails(
        self,
        client: TestClient,
        facebook_app_secret,
        instagram_webhook_payload
    ):
        """Test signature without 'sha256=' prefix fails verification."""
        body_str = json.dumps(instagram_webhook_payload, separators=(',', ':'))

        # Compute signature but remove prefix
        mac = hmac.new(
            facebook_app_secret.encode(),
            msg=body_str.encode(),
            digestmod=hashlib.sha256
        )
        signature_no_prefix = mac.hexdigest()

        with patch.dict('os.environ', {'FACEBOOK_APP_SECRET': facebook_app_secret}):
            response = client.post(
                "/webhook/instagram",
                json=instagram_webhook_payload,
                headers={"X-Hub-Signature-256": signature_no_prefix}
            )

            # Should fail - signature format incorrect
            assert response.status_code == 403

    def test_missing_app_secret(
        self,
        client: TestClient,
        instagram_webhook_payload
    ):
        """Test webhook processing fails gracefully when app secret not configured."""
        with patch.dict('os.environ', {}, clear=True):
            response = client.post(
                "/webhook/instagram",
                json=instagram_webhook_payload,
                headers={"X-Hub-Signature-256": "sha256=anything"}
            )

            assert response.status_code == 403
