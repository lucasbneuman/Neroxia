"""
Integration tests for Facebook OAuth flow.

Tests OAuth integration with Facebook for Instagram and Messenger:
- OAuth URL generation
- Token exchange
- Page token retrieval
- Instagram account linking
- Token storage in database
- Webhook subscription
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import json


@pytest.fixture
def oauth_state():
    """OAuth state parameter."""
    return "user_123:instagram"


@pytest.fixture
def auth_code():
    """OAuth authorization code."""
    return "test_auth_code_abc123"


@pytest.fixture
def mock_facebook_responses():
    """Mock Facebook API responses."""
    return {
        "token_exchange": {
            "access_token": "user_long_lived_token",
            "token_type": "bearer",
            "expires_in": 5184000
        },
        "pages_list": {
            "data": [
                {
                    "id": "page_123",
                    "name": "Test Business Page",
                    "access_token": "page_access_token_123"
                }
            ]
        },
        "instagram_account": {
            "instagram_business_account": {
                "id": "ig_account_123"
            }
        },
        "webhook_subscribe": {
            "success": True
        }
    }


@pytest.mark.integration
class TestFacebookOAuthConnection:
    """Test Facebook OAuth connection flow."""

    def test_facebook_connect_returns_oauth_url(
        self,
        client: TestClient
    ):
        """Test /integrations/facebook/connect returns OAuth URL."""
        # Mock authenticated user
        with patch('src.routers.integrations.get_current_user') as mock_user:
            mock_user.return_value = {"id": "user_123"}

            response = client.get(
                "/integrations/facebook/connect",
                params={"channel": "instagram"}
            )

        assert response.status_code == 200
        data = response.json()

        # Verify OAuth URL structure
        assert "oauth_url" in data
        oauth_url = data["oauth_url"]
        assert "facebook.com" in oauth_url
        assert "instagram_basic" in oauth_url or "pages_messaging" in oauth_url
        assert "state=" in oauth_url

        # State should include user ID and channel
        assert "user_123" in oauth_url
        assert "instagram" in oauth_url


    def test_facebook_connect_messenger_channel(
        self,
        client: TestClient
    ):
        """Test OAuth URL for Messenger channel."""
        with patch('src.routers.integrations.get_current_user') as mock_user:
            mock_user.return_value = {"id": "user_456"}

            response = client.get(
                "/integrations/facebook/connect",
                params={"channel": "messenger"}
            )

        assert response.status_code == 200
        oauth_url = response.json()["oauth_url"]

        # Messenger should request pages_messaging scope
        assert "pages_messaging" in oauth_url
        assert "messenger" in oauth_url


@pytest.mark.integration
class TestFacebookOAuthCallback:
    """Test OAuth callback processing."""

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    @patch('src.routers.integrations.create_channel_integration')
    @patch('src.routers.integrations.get_db')
    async def test_callback_stores_tokens_in_database(
        self,
        mock_get_db,
        mock_create_integration,
        mock_http_client,
        oauth_state,
        auth_code,
        mock_facebook_responses
    ):
        """Test OAuth callback stores tokens in database."""
        from src.routers.integrations import facebook_callback

        # Mock database session
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Mock integration creation
        mock_integration = MagicMock()
        mock_integration.id = "integration_123"
        mock_create_integration.return_value = mock_integration

        # Mock HTTP responses
        mock_response = MagicMock()
        mock_response.status_code = 200

        # Return different responses for different URLs
        def json_side_effect():
            # Determine which endpoint was called based on call count
            call_count = mock_http_client.return_value.__aenter__.return_value.get.call_count
            if call_count == 1:  # Token exchange
                return mock_facebook_responses["token_exchange"]
            elif call_count == 2:  # Pages list
                return mock_facebook_responses["pages_list"]
            elif call_count == 3:  # Instagram account
                return mock_facebook_responses["instagram_account"]
            else:
                return mock_facebook_responses["webhook_subscribe"]

        mock_response.json = MagicMock(side_effect=json_side_effect)

        mock_http = MagicMock()
        mock_http.get = AsyncMock(return_value=mock_response)
        mock_http.post = AsyncMock(return_value=mock_response)
        mock_http_client.return_value.__aenter__.return_value = mock_http

        # Call callback
        result = await facebook_callback(
            code=auth_code,
            state=oauth_state,
            db=mock_db
        )

        # Verify integration was created
        mock_create_integration.assert_called_once()
        call_args = mock_create_integration.call_args[1]

        assert call_args["channel"] == "instagram"
        assert call_args["page_id"] == "page_123"
        assert call_args["page_access_token"] == "page_access_token_123"
        assert call_args["instagram_account_id"] == "ig_account_123"


    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    @patch('src.routers.integrations.create_channel_integration')
    @patch('src.routers.integrations.get_db')
    async def test_callback_subscribes_webhook(
        self,
        mock_get_db,
        mock_create_integration,
        mock_http_client,
        oauth_state,
        auth_code,
        mock_facebook_responses
    ):
        """Test callback subscribes to webhook."""
        from src.routers.integrations import facebook_callback

        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        mock_integration = MagicMock()
        mock_create_integration.return_value = mock_integration

        # Track POST calls
        post_calls = []

        async def mock_post(*args, **kwargs):
            post_calls.append((args, kwargs))
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {"success": True}
            return response

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            mock_facebook_responses["token_exchange"],
            mock_facebook_responses["pages_list"],
            mock_facebook_responses["instagram_account"]
        ]

        mock_http = MagicMock()
        mock_http.get = AsyncMock(return_value=mock_response)
        mock_http.post = mock_post
        mock_http_client.return_value.__aenter__.return_value = mock_http

        await facebook_callback(
            code=auth_code,
            state=oauth_state,
            db=mock_db
        )

        # Verify webhook subscription was attempted
        assert len(post_calls) > 0
        # Check if any POST was to subscribed_apps endpoint
        subscribed = any("subscribed_apps" in str(call) for call in post_calls)
        assert subscribed


@pytest.mark.integration
class TestOAuthErrorHandling:
    """Test OAuth error handling."""

    def test_callback_invalid_state_format(
        self,
        client: TestClient,
        auth_code
    ):
        """Test callback with invalid state format."""
        with patch('src.routers.integrations.get_db'):
            response = client.get(
                "/integrations/facebook/callback",
                params={
                    "code": auth_code,
                    "state": "invalid_state_format"  # Missing user_id:channel format
                }
            )

        # Should handle gracefully
        assert response.status_code in [400, 500]


    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    @patch('src.routers.integrations.get_db')
    async def test_callback_facebook_api_error(
        self,
        mock_get_db,
        mock_http_client,
        oauth_state,
        auth_code
    ):
        """Test callback handles Facebook API errors."""
        from src.routers.integrations import facebook_callback

        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Simulate Facebook API error
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "message": "Invalid OAuth code",
                "type": "OAuthException"
            }
        }

        mock_http = MagicMock()
        mock_http.get = AsyncMock(return_value=mock_response)
        mock_http_client.return_value.__aenter__.return_value = mock_http

        # Should raise exception or return error
        with pytest.raises(Exception):
            await facebook_callback(
                code=auth_code,
                state=oauth_state,
                db=mock_db
            )


@pytest.mark.integration
class TestOAuthMultiplePagesHandling:
    """Test OAuth with multiple Facebook pages."""

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    @patch('src.routers.integrations.create_channel_integration')
    @patch('src.routers.integrations.get_db')
    async def test_callback_handles_multiple_pages(
        self,
        mock_get_db,
        mock_create_integration,
        mock_http_client,
        oauth_state,
        auth_code
    ):
        """Test callback with user having multiple Facebook pages."""
        from src.routers.integrations import facebook_callback

        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        mock_integration = MagicMock()
        mock_create_integration.return_value = mock_integration

        # Multiple pages response
        multiple_pages = {
            "data": [
                {
                    "id": "page_1",
                    "name": "Page One",
                    "access_token": "token_1"
                },
                {
                    "id": "page_2",
                    "name": "Page Two",
                    "access_token": "token_2"
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            {"access_token": "user_token"},
            multiple_pages,
            {"instagram_business_account": {"id": "ig_123"}}
        ]

        mock_http = MagicMock()
        mock_http.get = AsyncMock(return_value=mock_response)
        mock_http.post = AsyncMock(return_value=mock_response)
        mock_http_client.return_value.__aenter__.return_value = mock_http

        result = await facebook_callback(
            code=auth_code,
            state=oauth_state,
            db=mock_db
        )

        # Should use first page by default
        call_args = mock_create_integration.call_args[1]
        assert call_args["page_id"] == "page_1"


@pytest.mark.integration
class TestOAuthDisconnection:
    """Test OAuth disconnection/removal."""

    @patch('src.routers.integrations.delete_channel_integration')
    @patch('src.routers.integrations.get_current_user')
    def test_disconnect_integration(
        self,
        mock_user,
        mock_delete,
        client: TestClient
    ):
        """Test disconnecting Facebook integration."""
        mock_user.return_value = {"id": "user_123"}
        mock_delete.return_value = True

        response = client.delete(
            "/integrations/facebook/disconnect",
            params={"channel": "instagram"}
        )

        assert response.status_code == 200
        mock_delete.assert_called_once()


@pytest.mark.integration
class TestOAuthIntegrationsList:
    """Test listing user's integrations."""

    @patch('src.routers.integrations.get_channel_integrations_by_user')
    @patch('src.routers.integrations.get_current_user')
    def test_list_user_integrations(
        self,
        mock_user,
        mock_get_integrations,
        client: TestClient
    ):
        """Test GET /integrations/list returns user's integrations."""
        mock_user.return_value = {"id": "user_123"}

        # Mock integrations
        mock_integrations = [
            MagicMock(
                channel="instagram",
                page_id="page_123",
                page_name="My Business",
                connected_at="2025-12-01T00:00:00"
            ),
            MagicMock(
                channel="messenger",
                page_id="page_456",
                page_name="My Page",
                connected_at="2025-12-02T00:00:00"
            )
        ]
        mock_get_integrations.return_value = mock_integrations

        response = client.get("/integrations/list")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["channel"] == "instagram"
        assert data[1]["channel"] == "messenger"
