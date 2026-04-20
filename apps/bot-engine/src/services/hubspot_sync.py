"""HubSpot CRM synchronization service."""

import os
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

from whatsapp_bot_shared import get_logger

logger = get_logger(__name__)


class HubSpotService:
    """Service for syncing customer data to HubSpot CRM."""

    LIFECYCLE_STAGES = {
        "welcome": "lead",
        "qualifying": "marketingqualifiedlead",
        "nurturing": "salesqualifiedlead",
        "closing": "opportunity",
        "sold": "customer",
        "follow_up": "opportunity",
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("HUBSPOT_ACCESS_TOKEN")
        if not self.api_key:
            logger.warning("HubSpot API key not found, sync will be disabled")
            self.enabled = False
            return

        self.enabled = True
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        logger.info("HubSpot service initialized")

    async def sync_contact(
        self,
        user_data: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None,
        db_user: Optional[Any] = None,
    ) -> Optional[Dict[str, Any]]:
        """Sync contact to HubSpot (create or update)."""
        if not self.enabled:
            logger.warning("HubSpot sync skipped: API key not configured")
            return None

        phone = user_data.get("phone")
        email = user_data.get("email")
        if not phone and not email:
            logger.error("Cannot sync to HubSpot: at least email or phone is required")
            return None

        channel = state.get("channel", "whatsapp") if state else "whatsapp"
        user_identifier = state.get("user_identifier") if state else (phone or email)
        logger.info(
            f"HubSpot sync for {channel} user: {user_identifier} (phone={phone}, email={email})"
        )

        try:
            contact_id = None
            action = "skipped"
            lifecyclestage = None

            if db_user and getattr(db_user, "hubspot_contact_id", None):
                existing_contact = await self._get_contact_by_id(db_user.hubspot_contact_id)
                if existing_contact:
                    if await self._update_contact(
                        db_user.hubspot_contact_id, user_data, existing_contact, state
                    ):
                        contact_id = db_user.hubspot_contact_id
                        lifecyclestage = existing_contact.get("properties", {}).get("lifecyclestage")
                        action = "updated"
                else:
                    db_user.hubspot_contact_id = None

            if not contact_id:
                channel_user_id = state.get("user_identifier") if state else None
                existing_contact = await self._search_contact(email, phone, channel_user_id)
                if existing_contact:
                    contact_id = existing_contact["id"]
                    await self._update_contact(contact_id, user_data, existing_contact, state)
                    lifecyclestage = existing_contact.get("properties", {}).get("lifecyclestage")
                    action = "updated"
                else:
                    result = await self._create_contact(user_data, state)
                    if result:
                        contact_id = result["id"]
                        lifecyclestage = result.get("lifecyclestage")
                        action = "created"

            if not contact_id:
                logger.error("HubSpot sync failed: no contact_id returned")
                return None

            return {
                "contact_id": contact_id,
                "lifecyclestage": lifecyclestage,
                "action": action,
                "synced_at": datetime.utcnow(),
            }
        except Exception as e:
            logger.error(f"HubSpot sync error: {e}")
            return None

    async def _request(
        self, method: str, path: str, *, json: Optional[Dict[str, Any]] = None
    ) -> Optional[httpx.Response]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                request_method = getattr(client, method.lower())
                return await request_method(
                    f"{self.base_url}{path}",
                    headers=self.headers,
                    json=json,
                )
        except Exception as e:
            logger.error(f"HubSpot {method} {path} request failed: {e}")
            return None

    async def _get_contact_by_id(self, contact_id: str) -> Optional[Dict[str, Any]]:
        response = await self._request("GET", f"/crm/v3/objects/contacts/{contact_id}")
        if response is None:
            return None
        if response.status_code == 200:
            return response.json()
        if response.status_code != 404:
            logger.error(
                f"Error retrieving HubSpot contact: {response.status_code} - {response.text}"
            )
        return None

    async def _search_contact(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        channel_user_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        filters = []
        if email:
            filters.append(("email", email))
        if phone:
            filters.append(("phone", phone))
        if channel_user_id:
            filters.append(("channel_user_id", channel_user_id))

        for property_name, value in filters:
            payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": property_name,
                                "operator": "EQ",
                                "value": value,
                            }
                        ]
                    }
                ]
            }
            response = await self._request(
                "POST", "/crm/v3/objects/contacts/search", json=payload
            )
            if response and response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    return results[0]

        return None

    async def _create_contact(
        self,
        user_data: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        properties = self._prepare_properties(user_data, state)
        response = await self._request(
            "POST", "/crm/v3/objects/contacts", json={"properties": properties}
        )
        if response is None:
            return None
        if response.status_code in (200, 201):
            result = response.json()
            return {
                "id": result["id"],
                "lifecyclestage": result.get("properties", {}).get("lifecyclestage"),
            }
        if response.status_code == 400 and "PROPERTY_DOESNT_EXIST" in response.text:
            standard_properties = {
                key: value
                for key, value in properties.items()
                if key
                in {
                    "phone",
                    "firstname",
                    "lastname",
                    "email",
                    "lifecyclestage",
                    "intent_score",
                    "sentiment",
                    "needs",
                    "pain_points",
                    "budget",
                    "hs_content_membership_notes",
                    "hs_lead_status",
                }
            }
            retry_response = await self._request(
                "POST",
                "/crm/v3/objects/contacts",
                json={"properties": standard_properties},
            )
            if retry_response and retry_response.status_code in (200, 201):
                result = retry_response.json()
                return {
                    "id": result["id"],
                    "lifecyclestage": result.get("properties", {}).get("lifecyclestage"),
                }
        logger.error(f"Failed to create HubSpot contact: {response.status_code} - {response.text}")
        return None

    async def _update_contact(
        self,
        contact_id: str,
        user_data: Dict[str, Any],
        existing_contact: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None,
    ) -> bool:
        new_properties = self._prepare_properties(user_data, state)
        existing_properties = existing_contact.get("properties", {})
        update_properties = {}
        for key, value in new_properties.items():
            existing_value = existing_properties.get(key)
            if (
                not existing_value
                or str(existing_value).lower() in {"none", "null", ""}
                or existing_value != str(value)
            ):
                update_properties[key] = value

        if not update_properties:
            return True

        response = await self._request(
            "PATCH",
            f"/crm/v3/objects/contacts/{contact_id}",
            json={"properties": update_properties},
        )
        if response is None:
            return False
        if response.status_code == 200:
            return True
        if response.status_code == 400 and "PROPERTY_DOESNT_EXIST" in response.text:
            standard_properties = {
                key: value
                for key, value in update_properties.items()
                if key
                in {
                    "phone",
                    "firstname",
                    "lastname",
                    "email",
                    "lifecyclestage",
                    "intent_score",
                    "sentiment",
                    "needs",
                    "pain_points",
                    "budget",
                    "hs_content_membership_notes",
                    "hs_lead_status",
                }
            }
            if not standard_properties:
                return False
            retry_response = await self._request(
                "PATCH",
                f"/crm/v3/objects/contacts/{contact_id}",
                json={"properties": standard_properties},
            )
            return bool(retry_response and retry_response.status_code == 200)

        logger.error(f"Failed to update HubSpot contact: {response.status_code} - {response.text}")
        return False

    def _prepare_properties(
        self,
        user_data: Dict[str, Any],
        state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if user_data.get("phone"):
            properties["phone"] = user_data["phone"]
        if user_data.get("email"):
            properties["email"] = user_data["email"]

        name_to_use = user_data.get("whatsapp_profile_name") or user_data.get("name")
        if name_to_use:
            name_parts = name_to_use.strip().split(maxsplit=1)
            properties["firstname"] = name_parts[0]
            properties["lastname"] = name_parts[1] if len(name_parts) > 1 else ""

        channel = state.get("channel", "whatsapp") if state else "whatsapp"
        properties["lead_source"] = channel
        if state and state.get("user_identifier"):
            properties["channel_user_id"] = state["user_identifier"]

        internal_stage = user_data.get("stage") or (state.get("stage") if state else None)
        if internal_stage:
            properties["lifecyclestage"] = self.LIFECYCLE_STAGES.get(internal_stage, "lead")

        intent_score = user_data.get("intent_score")
        if intent_score is None and state:
            intent_score = state.get("intent_score")
        if intent_score is not None:
            properties["intent_score"] = round(intent_score, 2)

        sentiment = user_data.get("sentiment")
        if not sentiment and state:
            sentiment = state.get("sentiment")
        if sentiment:
            properties["sentiment"] = sentiment
        if user_data.get("needs"):
            properties["needs"] = user_data["needs"]
        if user_data.get("pain_points"):
            properties["pain_points"] = user_data["pain_points"]
        if user_data.get("budget"):
            properties["budget"] = user_data["budget"]
        if user_data.get("conversation_summary"):
            properties["hs_content_membership_notes"] = user_data["conversation_summary"]
        if user_data.get("whatsapp_profile_name"):
            properties["whatsapp_profile_name"] = user_data["whatsapp_profile_name"]
        if user_data.get("country_code"):
            properties["country_code"] = user_data["country_code"]

        properties["hs_lead_status"] = "NEW"
        return properties


hubspot_service: Optional[HubSpotService] = None


def get_hubspot_service() -> HubSpotService:
    """Get the global HubSpot service instance."""
    global hubspot_service
    if hubspot_service is None:
        hubspot_service = HubSpotService()
    return hubspot_service


async def sync_user_to_hubspot(
    user_data: Dict[str, Any],
    state: Optional[Dict[str, Any]] = None,
    db_user: Optional[Any] = None,
) -> bool:
    """Compatibility helper used by existing tests and workflow code."""
    result = await get_hubspot_service().sync_contact(user_data, state=state, db_user=db_user)
    return result is not None


async def search_contact_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Compatibility helper for direct contact lookup by email."""
    return await get_hubspot_service()._search_contact(email=email)


async def search_contact_by_channel_id(channel_user_id: str) -> Optional[Dict[str, Any]]:
    """Compatibility helper for direct contact lookup by channel identifier."""
    return await get_hubspot_service()._search_contact(channel_user_id=channel_user_id)


HubSpotSync = HubSpotService
