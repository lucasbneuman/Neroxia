"""
Integration tests for multi-channel HubSpot sync.

Tests HubSpot CRM integration with Instagram, Messenger, and WhatsApp:
- Contact sync without phone number (Instagram/Messenger)
- Lead source tracking (whatsapp/instagram/messenger)
- Channel user ID (PSID) storage
- Custom property creation
- Backwards compatibility with WhatsApp
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

pytestmark = pytest.mark.anyio


@pytest.fixture
def hubspot_contact_response():
    """Mock HubSpot API contact creation response."""
    return {
        "id": "hubspot_contact_123",
        "properties": {
            "email": "test@example.com",
            "firstname": "Test",
            "lastname": "User"
        }
    }


@pytest.mark.integration
class TestHubSpotInstagramSync:
    """Test HubSpot sync for Instagram users (no phone)."""

    @patch('httpx.AsyncClient')
    async def test_sync_instagram_user_without_phone(
        self,
        mock_client,
        hubspot_contact_response
    ):
        """Test HubSpot sync for Instagram user (no phone number)."""
        from src.services.hubspot_sync import sync_user_to_hubspot

        # Instagram state (no phone)
        state = {
            "channel": "instagram",
            "user_identifier": "INSTAGRAM_PSID_123",
            "user_phone": None,
            "user_email": "instagram_user@example.com",
            "stage": "qualifying",
            "intent_score": 0.65,
            "sentiment": "positive"
        }

        user_data = {
            "name": "Instagram User",
            "email": "instagram_user@example.com",
            "phone": None,
            "needs": "Looking for product information"
        }

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = hubspot_contact_response

        mock_http = MagicMock()
        mock_http.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_http

        # Sync should succeed without phone
        with patch('os.environ', {'HUBSPOT_ACCESS_TOKEN': 'test_token'}):
            result = await sync_user_to_hubspot(user_data, state, None)

        assert result is True
        mock_http.post.assert_called()

        # Verify properties sent
        call_args = mock_http.post.call_args
        properties = call_args[1]["json"]["properties"]

        # Email should be present
        assert "email" in properties
        assert properties["email"] == "instagram_user@example.com"

        # Phone should be absent or empty
        assert properties.get("phone") in [None, ""]

        # Lead source should be instagram
        assert properties["lead_source"] == "instagram"

        # Channel user ID should be PSID
        assert properties["channel_user_id"] == "INSTAGRAM_PSID_123"


    @patch('httpx.AsyncClient')
    async def test_sync_instagram_creates_custom_properties(
        self,
        mock_client,
        hubspot_contact_response
    ):
        """Test that Instagram sync creates HubSpot custom properties."""
        from src.services.hubspot_sync import sync_user_to_hubspot

        state = {
            "channel": "instagram",
            "user_identifier": "PSID_456",
            "user_email": "test@example.com",
            "stage": "nurturing",
            "intent_score": 0.80,
            "sentiment": "positive"
        }

        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "needs": "Product demo",
            "budget": "$500-1000"
        }

        # Mock responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = hubspot_contact_response

        mock_http = MagicMock()
        mock_http.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_http

        with patch('os.environ', {'HUBSPOT_ACCESS_TOKEN': 'test_token'}):
            await sync_user_to_hubspot(user_data, state, None)

        # Verify custom properties included
        call_args = mock_http.post.call_args
        properties = call_args[1]["json"]["properties"]

        assert properties["intent_score"] == 0.80
        assert properties["sentiment"] == "positive"
        assert properties["needs"] == "Product demo"
        assert properties["budget"] == "$500-1000"


@pytest.mark.integration
class TestHubSpotMessengerSync:
    """Test HubSpot sync for Messenger users."""

    @patch('httpx.AsyncClient')
    async def test_sync_messenger_user_with_email_only(
        self,
        mock_client,
        hubspot_contact_response
    ):
        """Test Messenger user sync with email but no phone."""
        from src.services.hubspot_sync import sync_user_to_hubspot

        state = {
            "channel": "messenger",
            "user_identifier": "MESSENGER_PSID_789",
            "user_email": "messenger@example.com",
            "user_phone": None,
            "stage": "closing"
        }

        user_data = {
            "name": "Messenger User",
            "email": "messenger@example.com",
            "phone": None
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = hubspot_contact_response

        mock_http = MagicMock()
        mock_http.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_http

        with patch('os.environ', {'HUBSPOT_ACCESS_TOKEN': 'test_token'}):
            result = await sync_user_to_hubspot(user_data, state, None)

        assert result is True

        # Verify lead source
        call_args = mock_http.post.call_args
        properties = call_args[1]["json"]["properties"]
        assert properties["lead_source"] == "messenger"
        assert properties["channel_user_id"] == "MESSENGER_PSID_789"


@pytest.mark.integration
class TestHubSpotWhatsAppBackwardsCompatibility:
    """Test WhatsApp integration still works (backwards compatibility)."""

    @patch('httpx.AsyncClient')
    async def test_whatsapp_sync_still_works(
        self,
        mock_client,
        hubspot_contact_response
    ):
        """Test WhatsApp users sync normally with phone."""
        from src.services.hubspot_sync import sync_user_to_hubspot

        # Traditional WhatsApp state
        state = {
            "channel": "whatsapp",
            "user_identifier": "+1234567890",
            "user_phone": "+1234567890",
            "user_email": "whatsapp@example.com",
            "stage": "qualifying"
        }

        user_data = {
            "name": "WhatsApp User",
            "email": "whatsapp@example.com",
            "phone": "+1234567890"
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = hubspot_contact_response

        mock_http = MagicMock()
        mock_http.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_http

        with patch('os.environ', {'HUBSPOT_ACCESS_TOKEN': 'test_token'}):
            result = await sync_user_to_hubspot(user_data, state, None)

        assert result is True

        # Verify phone is included
        call_args = mock_http.post.call_args
        properties = call_args[1]["json"]["properties"]
        assert properties["phone"] == "+1234567890"
        assert properties["lead_source"] == "whatsapp"


@pytest.mark.integration
class TestHubSpotLeadSourceTracking:
    """Test lead source field tracks origin channel."""

    @patch('httpx.AsyncClient')
    async def test_lead_source_maps_to_channel(
        self,
        mock_client,
        hubspot_contact_response
    ):
        """Test that lead_source property matches channel."""
        from src.services.hubspot_sync import sync_user_to_hubspot

        channels = ["instagram", "messenger", "whatsapp"]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = hubspot_contact_response

        mock_http = MagicMock()
        mock_http.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_http

        with patch('os.environ', {'HUBSPOT_ACCESS_TOKEN': 'test_token'}):
            for channel in channels:
                state = {
                    "channel": channel,
                    "user_identifier": f"{channel}_id_123",
                    "user_email": f"{channel}@example.com",
                    "stage": "qualifying"
                }

                user_data = {
                    "name": f"{channel} user",
                    "email": f"{channel}@example.com"
                }

                await sync_user_to_hubspot(user_data, state, None)

                # Verify lead source matches channel
                call_args = mock_http.post.call_args
                properties = call_args[1]["json"]["properties"]
                assert properties["lead_source"] == channel


@pytest.mark.integration
class TestHubSpotContactSearch:
    """Test searching contacts by PSID or email."""

    @patch('httpx.AsyncClient')
    async def test_search_by_email(
        self,
        mock_client
    ):
        """Test searching HubSpot contact by email."""
        from src.services.hubspot_sync import search_contact_by_email

        search_response = {
            "results": [{
                "id": "contact_123",
                "properties": {"email": "test@example.com"}
            }]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = search_response

        mock_http = MagicMock()
        mock_http.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_http

        with patch('os.environ', {'HUBSPOT_ACCESS_TOKEN': 'test_token'}):
            result = await search_contact_by_email("test@example.com")

        assert result is not None
        assert result["id"] == "contact_123"


    @patch('httpx.AsyncClient')
    async def test_search_by_psid(
        self,
        mock_client
    ):
        """Test searching HubSpot contact by channel_user_id (PSID)."""
        from src.services.hubspot_sync import search_contact_by_channel_id

        search_response = {
            "results": [{
                "id": "contact_456",
                "properties": {"channel_user_id": "PSID_123"}
            }]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = search_response

        mock_http = MagicMock()
        mock_http.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_http

        with patch('os.environ', {'HUBSPOT_ACCESS_TOKEN': 'test_token'}):
            result = await search_contact_by_channel_id("PSID_123")

        assert result is not None
        assert result["id"] == "contact_456"


@pytest.mark.integration
class TestHubSpotLifecycleStageMapping:
    """Test conversation stage maps to HubSpot lifecycle stage."""

    @patch('httpx.AsyncClient')
    async def test_stage_mapping(
        self,
        mock_client,
        hubspot_contact_response
    ):
        """Test bot stage maps to HubSpot lifecycle stage."""
        from src.services.hubspot_sync import sync_user_to_hubspot

        stage_mapping = {
            "welcome": "lead",
            "qualifying": "marketingqualifiedlead",
            "nurturing": "salesqualifiedlead",
            "closing": "opportunity",
            "sold": "customer"
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = hubspot_contact_response

        mock_http = MagicMock()
        mock_http.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_http

        with patch('os.environ', {'HUBSPOT_ACCESS_TOKEN': 'test_token'}):
            for bot_stage, hubspot_stage in stage_mapping.items():
                state = {
                    "channel": "instagram",
                    "user_identifier": "PSID",
                    "user_email": "test@example.com",
                    "stage": bot_stage
                }

                user_data = {
                    "name": "Test",
                    "email": "test@example.com"
                }

                await sync_user_to_hubspot(user_data, state, None)

                call_args = mock_http.post.call_args
                properties = call_args[1]["json"]["properties"]
                assert properties["lifecyclestage"] == hubspot_stage
