"""Unit tests for HubSpot multi-channel sync service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.hubspot_sync import HubSpotService

# Mark all async tests
pytestmark = pytest.mark.anyio


class TestHubSpotMultiChannelSync:
    """Test HubSpot sync with multi-channel support (Phase 5)."""

    @pytest.fixture
    def hubspot_service(self):
        """Create HubSpot service instance for testing."""
        with patch.dict('os.environ', {'HUBSPOT_ACCESS_TOKEN': 'test_token'}):
            service = HubSpotService(api_key='test_token')
            return service

    def test_prepare_properties_whatsapp_user(self, hubspot_service):
        """Test _prepare_properties with WhatsApp user (has phone)."""
        user_data = {
            "phone": "+1234567890",
            "name": "John Doe",
            "email": "john@example.com",
            "intent_score": 0.8,
            "sentiment": "positive",
            "stage": "qualifying",
        }

        state = {
            "channel": "whatsapp",
            "user_identifier": "+1234567890",
        }

        properties = hubspot_service._prepare_properties(user_data, state)

        assert properties["phone"] == "+1234567890"
        assert properties["email"] == "john@example.com"
        assert properties["firstname"] == "John"
        assert properties["lastname"] == "Doe"
        assert properties["lead_source"] == "whatsapp"
        assert properties["channel_user_id"] == "+1234567890"
        assert properties["intent_score"] == 0.8
        assert properties["sentiment"] == "positive"
        assert properties["lifecyclestage"] == "marketingqualifiedlead"

    def test_prepare_properties_instagram_user_no_phone(self, hubspot_service):
        """Test _prepare_properties with Instagram user (no phone, has PSID)."""
        user_data = {
            "phone": None,  # Instagram user may not have phone
            "name": "Jane Smith",
            "email": "jane@example.com",
            "intent_score": 0.6,
            "sentiment": "neutral",
            "stage": "nurturing",
        }

        state = {
            "channel": "instagram",
            "user_identifier": "instagram_psid_123456",
        }

        properties = hubspot_service._prepare_properties(user_data, state)

        # Phone should NOT be in properties (None was passed)
        assert "phone" not in properties
        assert properties["email"] == "jane@example.com"
        assert properties["firstname"] == "Jane"
        assert properties["lastname"] == "Smith"
        assert properties["lead_source"] == "instagram"
        assert properties["channel_user_id"] == "instagram_psid_123456"
        assert properties["intent_score"] == 0.6
        assert properties["lifecyclestage"] == "salesqualifiedlead"

    def test_prepare_properties_messenger_user_no_phone(self, hubspot_service):
        """Test _prepare_properties with Messenger user (no phone, has PSID)."""
        user_data = {
            "phone": None,
            "name": "Bob Johnson",
            "email": "bob@example.com",
            "stage": "closing",
        }

        state = {
            "channel": "messenger",
            "user_identifier": "messenger_psid_789012",
        }

        properties = hubspot_service._prepare_properties(user_data, state)

        assert "phone" not in properties
        assert properties["email"] == "bob@example.com"
        assert properties["lead_source"] == "messenger"
        assert properties["channel_user_id"] == "messenger_psid_789012"
        assert properties["lifecyclestage"] == "opportunity"

    def test_prepare_properties_backwards_compatible(self, hubspot_service):
        """Test _prepare_properties without state (backwards compatibility)."""
        user_data = {
            "phone": "+1234567890",
            "name": "Legacy User",
            "email": "legacy@example.com",
        }

        # No state passed (legacy behavior)
        properties = hubspot_service._prepare_properties(user_data, state=None)

        assert properties["phone"] == "+1234567890"
        assert properties["email"] == "legacy@example.com"
        assert properties["lead_source"] == "whatsapp"  # Default
        # channel_user_id should not be set without state
        assert "channel_user_id" not in properties

    async def test_sync_contact_requires_email_or_phone(self, hubspot_service):
        """Test sync_contact fails without email or phone."""
        user_data = {
            "name": "No Contact Info",
            # No phone, no email
        }

        result = await hubspot_service.sync_contact(user_data)

        assert result is None  # Should fail gracefully

    async def test_sync_contact_with_email_only(self, hubspot_service):
        """Test sync_contact works with email only (Instagram/Messenger case)."""
        user_data = {
            "email": "instagram@example.com",
            "name": "Instagram User",
        }

        state = {
            "channel": "instagram",
            "user_identifier": "instagram_psid_123",
        }

        # Mock the API calls
        with patch.object(hubspot_service, "_request", new_callable=AsyncMock) as mock_request:
            search_response = MagicMock()
            search_response.status_code = 200
            search_response.json.return_value = {"results": []}

            create_response = MagicMock()
            create_response.status_code = 201
            create_response.json.return_value = {
                "id": "12345",
                "properties": {"lifecyclestage": "lead"},
            }

            mock_request.side_effect = [search_response, search_response, create_response]

            result = await hubspot_service.sync_contact(user_data, state=state)

            assert result is not None
            assert result["contact_id"] == "12345"
            assert result["action"] == "created"

    async def test_search_contact_by_email_priority(self, hubspot_service):
        """Test _search_contact prioritizes email over phone."""
        with patch.object(hubspot_service, "_request", new_callable=AsyncMock) as mock_request:
            # Mock successful email search
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {
                "results": [{"id": "email_contact_123", "properties": {}}]
            }
            mock_request.return_value = response

            result = await hubspot_service._search_contact(
                email="test@example.com",
                phone="+1234567890",
                channel_user_id="psid_123"
            )

            assert result is not None
            assert result["id"] == "email_contact_123"
            # Should only call search once (email found)
            assert mock_request.call_count == 1
            _, path = mock_request.call_args.args[:2]
            assert path == "/crm/v3/objects/contacts/search"
            assert mock_request.call_args.kwargs["json"]["filterGroups"][0]["filters"][0]["propertyName"] == "email"

    async def test_search_contact_by_channel_user_id_fallback(self, hubspot_service):
        """Test _search_contact falls back to channel_user_id if email/phone not found."""
        with patch.object(hubspot_service, "_request", new_callable=AsyncMock) as mock_request:
            # Mock email and phone searches return empty, channel_user_id returns result
            def search_side_effect(*args, **kwargs):
                response = MagicMock()
                response.status_code = 200
                property_name = kwargs["json"]["filterGroups"][0]["filters"][0]["propertyName"]

                if property_name == "channel_user_id":
                    response.json.return_value = {
                        "results": [{"id": "psid_contact_456", "properties": {}}]
                    }
                else:
                    response.json.return_value = {"results": []}

                return response

            mock_request.side_effect = search_side_effect

            result = await hubspot_service._search_contact(
                email="notfound@example.com",
                phone="+9999999999",
                channel_user_id="instagram_psid_456"
            )

            assert result is not None
            assert result["id"] == "psid_contact_456"
            # Should have tried all three searches
            assert mock_request.call_count == 3

    async def test_search_contact_handles_missing_identifiers(self, hubspot_service):
        """Test _search_contact handles None values gracefully."""
        with patch.object(hubspot_service, "_request", new_callable=AsyncMock) as mock_request:
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {"results": []}
            mock_request.return_value = response

            # Only email provided
            result = await hubspot_service._search_contact(
                email="only@example.com",
                phone=None,
                channel_user_id=None
            )

            assert result is None
            # Should only call search once (email)
            assert mock_request.call_count == 1


class TestHubSpotBackwardsCompatibility:
    """Test that existing WhatsApp functionality still works."""

    @pytest.fixture
    def hubspot_service(self):
        """Create HubSpot service instance for testing."""
        with patch.dict('os.environ', {'HUBSPOT_ACCESS_TOKEN': 'test_token'}):
            service = HubSpotService(api_key='test_token')
            return service

    async def test_sync_contact_legacy_signature(self, hubspot_service):
        """Test sync_contact still works with old signature (no state param)."""
        user_data = {
            "phone": "+1234567890",
            "name": "Legacy User",
            "email": "legacy@example.com",
        }

        # Mock db_user
        db_user = MagicMock()
        db_user.hubspot_contact_id = None

        with patch.object(hubspot_service, "_request", new_callable=AsyncMock) as mock_request:
            search_response = MagicMock()
            search_response.status_code = 200
            search_response.json.return_value = {"results": []}

            create_response = MagicMock()
            create_response.status_code = 201
            create_response.json.return_value = {
                "id": "legacy_123",
                "properties": {"lifecyclestage": "lead"},
            }

            mock_request.side_effect = [search_response, search_response, create_response]

            # Call without state parameter (legacy)
            result = await hubspot_service.sync_contact(
                user_data,
                db_user=db_user
            )

            assert result is not None
            assert result["contact_id"] == "legacy_123"
            assert result["action"] == "created"
