# Implementation Plan: Instagram & Facebook Messenger Integration

**Version:** 1.0
**Created:** 2025-12-04
**Project:** WhatsApp Sales Bot SaaS Platform
**Objective:** Enable bot conversations through Instagram Direct Messages and Facebook Messenger with full CRM synchronization and lead source tracking

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Meta APIs Research](#1-meta-apis-research--requirements)
3. [Database Schema Changes](#2-database-schema-changes)
4. [Webhook Architecture](#3-webhook-architecture)
5. [Bot Engine Modifications](#4-bot-engine-modifications)
6. [HubSpot CRM Sync Updates](#5-hubspot-crm-sync-updates)
7. [Instagram & Messenger Services](#6-instagram--messenger-service-implementation)
8. [Frontend Dashboard Updates](#7-frontend-dashboard-updates)
9. [CRUD Operations Updates](#8-crud-operations-updates)
10. [Authentication & App Registration](#9-authentication--app-registration)
11. [Security & Rate Limiting](#10-security--rate-limiting)
12. [Testing Strategy](#11-testing-strategy)
13. [Environment Variables](#12-environment-variables)
14. [Deployment (Coolify)](#13-deployment-coolify)
15. [Architectural Trade-offs](#14-architectural-trade-offs--challenges)
16. [Agent Coordination](#15-agent-coordination)

---

## Executive Summary

This plan outlines the integration of Instagram Direct Messages and Facebook Messenger into the WhatsApp Sales Bot SaaS platform. The architecture leverages Meta's Graph API for both channels, extends the existing multi-tenant structure, and maintains consistency with the current LangGraph workflow and HubSpot CRM synchronization.

**Key Features:**
- ✅ Multi-channel support: WhatsApp, Instagram, Messenger
- ✅ Unified LangGraph workflow (same 11 nodes)
- ✅ Lead source tracking in CRM
- ✅ Per-tenant channel configuration
- ✅ Backward compatible with existing WhatsApp functionality

---

## 1. Meta APIs Research & Requirements

### Meta Graph API - Unified Approach

Both Instagram and Facebook Messenger use the **Facebook Graph API** with platform-specific endpoints.

#### Instagram Messaging API Requirements

- Instagram Business Account or Creator Account
- Facebook Page connected to Instagram account
- Facebook App with Instagram permissions:
  - `instagram_basic`
  - `instagram_manage_messages`
  - `pages_manage_metadata`
- Webhook subscription to:
  - `messages`
  - `messaging_postbacks`
  - `messaging_optins`
- Send Endpoint: `https://graph.facebook.com/v18.0/me/messages`

#### Facebook Messenger API Requirements

- Facebook Page
- Facebook App with Messenger permissions:
  - `pages_messaging`
  - `pages_manage_metadata`
- Webhook subscription to:
  - `messages`
  - `messaging_postbacks`
  - `messaging_optins`
- Send Endpoint: `https://graph.facebook.com/v18.0/me/messages`

#### Authentication

Both channels use **Page Access Tokens** (long-lived tokens obtained via Facebook Login OAuth flow).

#### Message Format Differences

**Instagram:**
- Text messages
- Images
- Story mentions
- Story replies

**Messenger:**
- Text messages
- Images, videos, audio
- Quick replies
- Message templates

**Both:**
- Sender PSID (Page-Scoped ID) instead of phone numbers
- Webhook payload structure is identical

#### Webhook Payload Structure (Meta)

```json
{
  "object": "page",
  "entry": [
    {
      "id": "PAGE_ID",
      "time": 1234567890,
      "messaging": [
        {
          "sender": { "id": "USER_PSID" },
          "recipient": { "id": "PAGE_ID" },
          "timestamp": 1234567890,
          "message": {
            "mid": "MESSAGE_ID",
            "text": "Hello!"
          }
        }
      ]
    }
  ]
}
```

---

## 2. Database Schema Changes

**Strategy:** Extend existing models to support multiple messaging channels while maintaining backward compatibility.

### 2.1 Migration File

**File:** `packages/database/migrations/006_add_messaging_channels.sql`

```sql
-- ================================================
-- Migration 006: Multi-Channel Messaging Support
-- Date: 2025-12-04
-- Purpose: Add Instagram and Facebook Messenger support
-- ================================================

-- Add channel support to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS channel VARCHAR(20) DEFAULT 'whatsapp' NOT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS channel_user_id VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS channel_username VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS channel_profile_pic_url TEXT;

-- Modify phone to be nullable (Instagram/Messenger users may not have phone initially)
ALTER TABLE users ALTER COLUMN phone DROP NOT NULL;

-- Add composite unique constraint for channel + channel_user_id
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_channel_user_id
ON users(channel, channel_user_id)
WHERE channel_user_id IS NOT NULL;

-- Keep existing phone unique constraint (already allows NULL)
-- ALTER TABLE users ADD CONSTRAINT users_phone_key UNIQUE (phone);

-- Add index for efficient channel filtering
CREATE INDEX IF NOT EXISTS idx_users_channel ON users(channel);

-- Update deals table source to accommodate new channels
ALTER TABLE deals ALTER COLUMN source TYPE VARCHAR(50);
COMMENT ON COLUMN deals.source IS 'Lead source: whatsapp, instagram, messenger, test';

-- Add channel metadata to messages table
ALTER TABLE messages ADD COLUMN IF NOT EXISTS channel VARCHAR(20) DEFAULT 'whatsapp' NOT NULL;
ALTER TABLE messages ADD COLUMN IF NOT EXISTS channel_message_id VARCHAR(100);

-- Create index for message channel filtering
CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel);

-- ================================================
-- New Table: Channel Integrations (Multi-tenant)
-- ================================================

CREATE TABLE IF NOT EXISTS channel_integrations (
    id SERIAL PRIMARY KEY,
    auth_user_id UUID NOT NULL,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('instagram', 'messenger')),
    page_id VARCHAR(50),
    page_access_token TEXT NOT NULL,
    page_name VARCHAR(200),
    instagram_account_id VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    webhook_verify_token VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- One integration per tenant per channel per page
    UNIQUE(auth_user_id, channel, page_id)
);

CREATE INDEX IF NOT EXISTS idx_channel_integrations_user ON channel_integrations(auth_user_id);
CREATE INDEX IF NOT EXISTS idx_channel_integrations_channel ON channel_integrations(channel);
CREATE INDEX IF NOT EXISTS idx_channel_integrations_active ON channel_integrations(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE channel_integrations IS 'Stores per-tenant Meta (Instagram/Messenger) integration credentials';
COMMENT ON COLUMN channel_integrations.page_access_token IS 'Long-lived Page Access Token from Facebook OAuth';
COMMENT ON COLUMN channel_integrations.webhook_verify_token IS 'Custom token for webhook verification';

-- ================================================
-- Backfill existing data
-- ================================================

-- Ensure all existing users have channel set to 'whatsapp'
UPDATE users SET channel = 'whatsapp' WHERE channel IS NULL;

-- Ensure all existing messages have channel set to 'whatsapp'
UPDATE messages SET channel = 'whatsapp' WHERE channel IS NULL;

-- ================================================
-- Verification Queries
-- ================================================

-- Verify indexes
-- SELECT * FROM pg_indexes WHERE tablename IN ('users', 'messages', 'channel_integrations');

-- Verify constraints
-- SELECT conname, contype FROM pg_constraint WHERE conrelid = 'channel_integrations'::regclass;
```

### 2.2 Update User Model

**File:** `packages/database/whatsapp_bot_database/models.py`

Add new fields to `User` model:

```python
# Messaging channel identification
channel = Column(String(20), default="whatsapp", nullable=False, index=True)
channel_user_id = Column(String(100), nullable=True, index=True)  # PSID for IG/Messenger
channel_username = Column(String(100), nullable=True)  # @username for Instagram
channel_profile_pic_url = Column(Text, nullable=True)

# Make phone nullable for Instagram/Messenger users
phone = Column(String(20), unique=True, nullable=True, index=True)
```

**Add unique constraint in `__table_args__`:**

```python
__table_args__ = (
    Index('idx_users_channel_user_id', 'channel', 'channel_user_id',
          postgresql_where=text('channel_user_id IS NOT NULL'),
          unique=True),
)
```

### 2.3 New ChannelIntegration Model

**File:** `packages/database/whatsapp_bot_database/models.py`

```python
class ChannelIntegration(Base):
    """
    Stores per-tenant channel integration credentials for Instagram and Messenger.
    Each SaaS tenant can connect their own Facebook Pages.
    """
    __tablename__ = "channel_integrations"

    id = Column(Integer, primary_key=True, index=True)
    auth_user_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    channel = Column(String(20), nullable=False)  # 'instagram' or 'messenger'
    page_id = Column(String(50), nullable=True)
    page_access_token = Column(Text, nullable=False)  # Encrypted in production
    page_name = Column(String(200), nullable=True)
    instagram_account_id = Column(String(50), nullable=True)  # For Instagram only
    is_active = Column(Boolean, default=True)
    webhook_verify_token = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('auth_user_id', 'channel', 'page_id', name='uq_user_channel_page'),
    )
```

### 2.4 Update Message Model

**File:** `packages/database/whatsapp_bot_database/models.py`

Add to `Message` model:

```python
# Channel identification
channel = Column(String(20), default="whatsapp", nullable=False, index=True)
channel_message_id = Column(String(100), nullable=True)  # Meta message ID
```

---

## 3. Webhook Architecture

**Design Pattern:** Follow existing Twilio webhook pattern with channel-specific adapters.

### 3.1 New Router: Meta Webhooks

**File:** `apps/api/src/routers/meta_webhook.py`

```python
"""
Meta (Instagram + Facebook Messenger) webhook router.

This router handles incoming webhooks from Meta's Graph API for both
Instagram Direct Messages and Facebook Messenger.

Meta webhook verification docs:
https://developers.facebook.com/docs/graph-api/webhooks/getting-started
"""

from fastapi import APIRouter, Request, Query, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import hmac
import hashlib
from typing import Dict, Any

from ..database import get_db
from whatsapp_bot_database import crud
from whatsapp_bot_database.models import ChannelIntegration
from bot_engine.graph.workflow import run_workflow
from bot_engine.services.message_adapter import MessageAdapter
from bot_engine.services.instagram_service import InstagramService
from bot_engine.services.messenger_service import MessengerService

router = APIRouter(prefix="/webhook", tags=["webhooks"])


# ========================================
# Instagram Webhooks
# ========================================

@router.get("/instagram")
async def instagram_webhook_verify(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify Instagram webhook (required by Meta during setup).

    Meta sends a GET request with hub.mode, hub.challenge, and hub.verify_token.
    We must return hub.challenge if the verify_token matches our stored token.
    """
    if hub_mode != "subscribe":
        raise HTTPException(status_code=400, detail="Invalid hub.mode")

    # Validate verify_token against stored token in channel_integrations
    # For simplicity, using environment variable for initial setup
    # In production, validate against per-tenant tokens
    import os
    expected_token = os.getenv("FACEBOOK_VERIFY_TOKEN")

    if hub_verify_token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid verify token")

    return int(hub_challenge)


@router.post("/instagram")
async def instagram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Receive Instagram Direct Messages.

    Webhook payload structure:
    {
      "object": "page",
      "entry": [{
        "id": "PAGE_ID",
        "time": 1234567890,
        "messaging": [{
          "sender": {"id": "USER_PSID"},
          "recipient": {"id": "PAGE_ID"},
          "timestamp": 1234567890,
          "message": {"mid": "MESSAGE_ID", "text": "Hello!"}
        }]
      }]
    }
    """
    # Verify signature
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not _verify_webhook_signature(body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()

    # Process webhook events
    if payload.get("object") == "page":
        for entry in payload.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                await _process_instagram_message(messaging_event, db)

    return {"status": "ok"}


# ========================================
# Messenger Webhooks
# ========================================

@router.get("/messenger")
async def messenger_webhook_verify(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
):
    """Verify Messenger webhook (same pattern as Instagram)."""
    if hub_mode != "subscribe":
        raise HTTPException(status_code=400, detail="Invalid hub.mode")

    import os
    expected_token = os.getenv("FACEBOOK_VERIFY_TOKEN")

    if hub_verify_token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid verify token")

    return int(hub_challenge)


@router.post("/messenger")
async def messenger_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Receive Facebook Messenger messages."""
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not _verify_webhook_signature(body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()

    if payload.get("object") == "page":
        for entry in payload.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                await _process_messenger_message(messaging_event, db)

    return {"status": "ok"}


# ========================================
# Helper Functions
# ========================================

def _verify_webhook_signature(body: bytes, signature: str) -> bool:
    """
    Verify Meta webhook signature using app secret.

    Signature format: sha256=<hash>
    """
    import os
    app_secret = os.getenv("FACEBOOK_APP_SECRET")

    if not app_secret or not signature:
        return False

    # Remove 'sha256=' prefix
    expected_signature = signature.split("=")[1] if "=" in signature else signature

    # Compute HMAC
    mac = hmac.new(
        app_secret.encode(),
        msg=body,
        digestmod=hashlib.sha256
    )
    computed_signature = mac.hexdigest()

    return hmac.compare_digest(computed_signature, expected_signature)


async def _process_instagram_message(event: Dict[str, Any], db: AsyncSession):
    """Process incoming Instagram Direct Message."""
    sender_psid = event.get("sender", {}).get("id")
    recipient_page_id = event.get("recipient", {}).get("id")
    message = event.get("message", {})
    message_text = message.get("text", "")

    if not message_text:
        return  # Skip non-text messages for now

    # Normalize message
    normalized = MessageAdapter.normalize_message("instagram", event)

    # Get or create user
    user = await crud.get_user_by_identifier(
        db, identifier=sender_psid, channel="instagram"
    )

    if not user:
        # Fetch user profile from Instagram API
        integration = await _get_integration(db, recipient_page_id, "instagram")
        if not integration:
            return

        instagram_service = InstagramService()
        profile = await instagram_service.get_user_profile(
            sender_psid, integration.page_access_token
        )

        user = await crud.create_user(
            db,
            phone=None,  # Instagram users don't have phone initially
            name=profile.get("name"),
            channel="instagram",
            channel_user_id=sender_psid,
            channel_username=profile.get("username"),
            channel_profile_pic_url=profile.get("profile_pic"),
            auth_user_id=integration.auth_user_id
        )

    # Save incoming message
    await crud.create_message(
        db,
        user_id=user.id,
        message=message_text,
        is_user=True,
        channel="instagram",
        channel_message_id=message.get("mid")
    )

    # Process through bot workflow
    response = await run_workflow(
        user_phone=None,
        user_message=message_text,
        db_session=db,
        channel="instagram",
        channel_user_id=sender_psid,
        auth_user_id=user.auth_user_id
    )

    # Send response via Instagram
    instagram_service = InstagramService()
    await instagram_service.send_message(
        sender_psid,
        response.get("current_response", ""),
        db
    )

    # Save bot response
    await crud.create_message(
        db,
        user_id=user.id,
        message=response.get("current_response", ""),
        is_user=False,
        channel="instagram"
    )


async def _process_messenger_message(event: Dict[str, Any], db: AsyncSession):
    """Process incoming Facebook Messenger message (similar structure to Instagram)."""
    # Implementation similar to Instagram
    pass


async def _get_integration(
    db: AsyncSession,
    page_id: str,
    channel: str
) -> ChannelIntegration:
    """Get active channel integration by page ID."""
    return await crud.get_channel_integration_by_page(db, page_id, channel)
```

### 3.2 Message Adapter Service

**File:** `apps/bot-engine/src/services/message_adapter.py`

```python
"""
Message adapter to normalize messages from different channels.

Converts channel-specific message formats to a unified internal format
that the LangGraph workflow can process.
"""

from typing import Dict, Any
from datetime import datetime


class MessageAdapter:
    """Adapter pattern for normalizing multi-channel messages."""

    @staticmethod
    def normalize_message(channel: str, raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize incoming message to unified format.

        Args:
            channel: "whatsapp", "instagram", or "messenger"
            raw_payload: Raw webhook payload from channel

        Returns:
            {
                "channel": str,
                "user_id": str,  # phone or PSID
                "message_text": str,
                "timestamp": datetime,
                "metadata": dict  # channel-specific data
            }
        """
        if channel == "whatsapp":
            return MessageAdapter._normalize_twilio(raw_payload)
        elif channel == "instagram":
            return MessageAdapter._normalize_instagram(raw_payload)
        elif channel == "messenger":
            return MessageAdapter._normalize_messenger(raw_payload)
        else:
            raise ValueError(f"Unsupported channel: {channel}")

    @staticmethod
    def _normalize_twilio(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Twilio WhatsApp webhook."""
        return {
            "channel": "whatsapp",
            "user_id": payload.get("From", "").replace("whatsapp:", ""),
            "message_text": payload.get("Body", ""),
            "timestamp": datetime.utcnow(),
            "metadata": {
                "message_sid": payload.get("MessageSid"),
                "profile_name": payload.get("ProfileName"),
                "num_media": payload.get("NumMedia", 0)
            }
        }

    @staticmethod
    def _normalize_instagram(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Instagram webhook."""
        sender = payload.get("sender", {})
        message = payload.get("message", {})

        return {
            "channel": "instagram",
            "user_id": sender.get("id"),
            "message_text": message.get("text", ""),
            "timestamp": datetime.fromtimestamp(payload.get("timestamp", 0) / 1000),
            "metadata": {
                "message_id": message.get("mid"),
                "page_id": payload.get("recipient", {}).get("id"),
                "has_attachments": "attachments" in message
            }
        }

    @staticmethod
    def _normalize_messenger(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Messenger webhook (similar structure to Instagram)."""
        sender = payload.get("sender", {})
        message = payload.get("message", {})

        return {
            "channel": "messenger",
            "user_id": sender.get("id"),
            "message_text": message.get("text", ""),
            "timestamp": datetime.fromtimestamp(payload.get("timestamp", 0) / 1000),
            "metadata": {
                "message_id": message.get("mid"),
                "page_id": payload.get("recipient", {}).get("id"),
                "has_attachments": "attachments" in message
            }
        }
```

---

## 4. Bot Engine Modifications

**Strategy:** LangGraph workflow remains unchanged. Add channel awareness at state level.

### 4.1 Update ConversationState

**File:** `apps/bot-engine/src/graph/state.py`

```python
class ConversationState(TypedDict):
    """State shared across all LangGraph nodes."""

    # Message history
    messages: List[BaseMessage]

    # User identification (UPDATED FOR MULTI-CHANNEL)
    user_phone: Optional[str]  # WhatsApp only
    user_name: Optional[str]
    user_email: Optional[str]

    # NEW: Channel identification
    channel: str  # "whatsapp", "instagram", "messenger"
    channel_user_id: Optional[str]  # PSID for IG/Messenger, phone for WhatsApp
    channel_username: Optional[str]  # @username for Instagram

    # Conversation analysis
    intent_score: float
    sentiment: str
    stage: str
    conversation_mode: str

    # Collected data
    collected_data: Dict[str, Any]

    # Transaction tracking
    payment_link_sent: bool
    follow_up_scheduled: Optional[datetime]
    follow_up_count: int

    # Summary & response
    conversation_summary: Optional[str]
    current_response: Optional[str]

    # Configuration & database
    config: Dict[str, Any]
    db_session: Optional[Any]
    db_user: Optional[Any]

    # NEW: Tenant identification
    auth_user_id: Optional[str]
```

### 4.2 Update Workflow Entry Point

**File:** `apps/bot-engine/src/graph/workflow.py`

Update `run_workflow` function signature:

```python
async def run_workflow(
    user_phone: Optional[str],
    user_message: str,
    db_session: AsyncSession,
    channel: str = "whatsapp",
    channel_user_id: Optional[str] = None,
    channel_username: Optional[str] = None,
    auth_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the LangGraph workflow for a user message.

    Args:
        user_phone: Phone number (WhatsApp only)
        user_message: Message text
        db_session: Database session
        channel: "whatsapp", "instagram", or "messenger"
        channel_user_id: PSID for Instagram/Messenger
        channel_username: @username for Instagram
        auth_user_id: Tenant ID for multi-tenant isolation
    """
    # Initialize state with channel information
    initial_state = ConversationState(
        messages=[HumanMessage(content=user_message)],
        user_phone=user_phone,
        channel=channel,
        channel_user_id=channel_user_id or user_phone,
        channel_username=channel_username,
        auth_user_id=auth_user_id,
        # ... rest of state initialization
    )

    # Run workflow
    final_state = await graph.ainvoke(initial_state)
    return final_state
```

### 4.3 Update Data Collector Node

**File:** `apps/bot-engine/src/graph/nodes.py`

```python
async def data_collector_node(state: ConversationState) -> ConversationState:
    """
    Extract and validate customer data from conversation.

    For Instagram/Messenger users:
    - Collect phone if needed for CRM
    - Use channel_user_id as primary identifier
    """
    # ... existing extraction logic ...

    # NEW: Handle phone collection for Instagram/Messenger
    if state["channel"] in ["instagram", "messenger"]:
        # If phone not yet collected, prompt user
        if not state.get("user_phone") and not collected_data.get("phone"):
            if _should_collect_phone(state):  # Business logic
                state["current_response"] = (
                    "Para ofrecerte un mejor servicio, ¿podrías compartir "
                    "tu número de teléfono?"
                )
                return state

        # Validate and store phone if provided
        if collected_data.get("phone"):
            validated_phone = _validate_phone(collected_data["phone"])
            if validated_phone:
                # Update user in database
                await crud.update_user(
                    state["db_session"],
                    user_id=state["db_user"].id,
                    phone=validated_phone
                )
                state["user_phone"] = validated_phone

    # ... rest of data collection logic ...

    return state
```

### 4.4 Response Routing Service

**File:** `apps/bot-engine/src/services/message_sender.py`

```python
"""Service to send messages through appropriate channel."""

from sqlalchemy.ext.asyncio import AsyncSession
from .instagram_service import InstagramService
from .messenger_service import MessengerService
from .twilio_service import TwilioService


class MessageSender:
    """Route messages to appropriate channel API."""

    @staticmethod
    async def send_message(
        channel: str,
        recipient_id: str,
        message_text: str,
        db_session: AsyncSession,
        auth_user_id: Optional[str] = None
    ):
        """
        Send message through appropriate channel.

        Args:
            channel: "whatsapp", "instagram", or "messenger"
            recipient_id: Phone (WhatsApp) or PSID (IG/Messenger)
            message_text: Text to send
            db_session: Database session for credential lookup
            auth_user_id: Tenant ID
        """
        if channel == "whatsapp":
            twilio_service = TwilioService()
            return await twilio_service.send_whatsapp(recipient_id, message_text)

        elif channel == "instagram":
            instagram_service = InstagramService()
            return await instagram_service.send_message(
                recipient_id, message_text, db_session, auth_user_id
            )

        elif channel == "messenger":
            messenger_service = MessengerService()
            return await messenger_service.send_message(
                recipient_id, message_text, db_session, auth_user_id
            )

        else:
            raise ValueError(f"Unsupported channel: {channel}")
```

---

## 5. HubSpot CRM Sync Updates

**File:** `apps/bot-engine/src/services/hubspot_sync.py`

### 5.1 Add Lead Source Field

```python
def _prepare_properties(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare HubSpot properties from user data.

    Updated to include lead source (channel) tracking.
    """
    properties = {}

    # ... existing fields (name, email, phone) ...

    # NEW: Lead Source (channel)
    if user_data.get("channel"):
        # Use HubSpot standard field
        properties["hs_analytics_source"] = user_data["channel"]

        # Also create custom field for explicit tracking
        properties["lead_source_channel"] = user_data["channel"]

    # NEW: Channel username (for Instagram)
    if user_data.get("channel_username"):
        properties["instagram_username"] = user_data["channel_username"]

    # NEW: Use channel_user_id if no phone
    if not user_data.get("phone") and user_data.get("channel_user_id"):
        properties["channel_user_id"] = user_data["channel_user_id"]

    # ... rest of properties ...

    return properties
```

### 5.2 Update Contact Search Logic

```python
async def _search_contact(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Search for existing contact by phone, email, or channel_user_id.

    Updated to support multi-channel user identification.
    """

    # Try phone first (if available)
    if user_data.get("phone"):
        contact = await self._search_by_phone(user_data["phone"])
        if contact:
            return contact

    # Try email
    if user_data.get("email"):
        contact = await self._search_by_email(user_data["email"])
        if contact:
            return contact

    # NEW: Try channel_user_id (for Instagram/Messenger without phone)
    if user_data.get("channel_user_id"):
        search_payload = {
            "filterGroups": [{
                "filters": [{
                    "propertyName": "channel_user_id",
                    "operator": "EQ",
                    "value": user_data["channel_user_id"]
                }]
            }]
        }

        response = requests.post(
            f"{self.base_url}/crm/v3/objects/contacts/search",
            headers=self.headers,
            json=search_payload
        )

        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                return results[0]

    return None
```

### 5.3 Ensure Custom Properties Exist

```python
async def _ensure_custom_properties(self):
    """
    Create custom HubSpot properties if they don't exist.

    Added: lead_source_channel, instagram_username, channel_user_id
    """
    custom_properties = [
        # Existing properties
        {"name": "intent_score", "label": "Intent Score", "type": "number"},
        {"name": "sentiment", "label": "Sentiment", "type": "string"},
        {"name": "needs", "label": "Customer Needs", "type": "string"},
        {"name": "pain_points", "label": "Pain Points", "type": "string"},
        {"name": "budget", "label": "Budget", "type": "string"},

        # NEW: Multi-channel properties
        {"name": "lead_source_channel", "label": "Lead Source Channel", "type": "enumeration",
         "options": ["whatsapp", "instagram", "messenger"]},
        {"name": "instagram_username", "label": "Instagram Username", "type": "string"},
        {"name": "channel_user_id", "label": "Channel User ID", "type": "string"},
    ]

    for prop in custom_properties:
        await self._create_property_if_not_exists("contacts", prop)
```

---

## 6. Instagram & Messenger Service Implementation

### 6.1 Instagram Service

**File:** `apps/bot-engine/src/services/instagram_service.py`

**Note for Developers:** Before implementing, use Context7 MCP to research the latest Instagram Messaging API documentation:

```python
# Use Context7 MCP:
# - Library: "Facebook Graph API"
# - Topic: "Instagram messaging API send messages"
# - Mode: "code" for API examples
```

```python
"""
Instagram Messaging API service.

Handles sending messages and fetching user profiles via Meta Graph API.
"""

import os
import requests
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from whatsapp_bot_database import crud


class InstagramService:
    """Service for Instagram Direct Message API."""

    def __init__(self):
        self.graph_api_url = os.getenv("GRAPH_API_URL", "https://graph.facebook.com/v18.0")

    async def send_message(
        self,
        recipient_psid: str,
        message_text: str,
        db_session: AsyncSession,
        auth_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send message via Instagram Messaging API.

        Args:
            recipient_psid: Instagram user's Page-Scoped ID
            message_text: Message to send
            db_session: Database session for credential lookup
            auth_user_id: Tenant ID

        Returns:
            API response dict

        Raises:
            Exception: If integration not configured or API call fails
        """
        # Get page access token from channel_integrations
        integration = await self._get_integration(db_session, "instagram", auth_user_id)

        if not integration or not integration.is_active:
            raise Exception("Instagram integration not configured for this tenant")

        # Prepare payload
        payload = {
            "recipient": {"id": recipient_psid},
            "message": {"text": message_text}
        }

        # Send via Graph API
        response = requests.post(
            f"{self.graph_api_url}/me/messages",
            params={"access_token": integration.page_access_token},
            json=payload,
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"Instagram API error: {response.text}")

        return response.json()

    async def get_user_profile(
        self,
        psid: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Get Instagram user profile information.

        Args:
            psid: Page-Scoped ID
            access_token: Page Access Token

        Returns:
            {
                "id": "PSID",
                "name": "User Name",
                "username": "@username",
                "profile_pic": "https://..."
            }
        """
        response = requests.get(
            f"{self.graph_api_url}/{psid}",
            params={
                "fields": "name,profile_pic,username",
                "access_token": access_token
            },
            timeout=10
        )

        if response.status_code != 200:
            # Fallback to minimal info
            return {"id": psid, "name": "Instagram User"}

        return response.json()

    async def _get_integration(
        self,
        db_session: AsyncSession,
        channel: str,
        auth_user_id: Optional[str]
    ):
        """Get active channel integration for tenant."""
        if auth_user_id:
            return await crud.get_channel_integration(db_session, auth_user_id, channel)
        return None
```

### 6.2 Messenger Service

**File:** `apps/bot-engine/src/services/messenger_service.py`

**Note for Developers:** Use Context7 MCP to research Messenger API:

```python
# Use Context7 MCP:
# - Library: "Facebook Graph API"
# - Topic: "Messenger send API messages"
# - Mode: "code"
```

```python
"""
Facebook Messenger API service.

Similar to Instagram service but for Messenger platform.
"""

import os
import requests
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from whatsapp_bot_database import crud


class MessengerService:
    """Service for Facebook Messenger API."""

    def __init__(self):
        self.graph_api_url = os.getenv("GRAPH_API_URL", "https://graph.facebook.com/v18.0")

    async def send_message(
        self,
        recipient_psid: str,
        message_text: str,
        db_session: AsyncSession,
        auth_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send message via Messenger API.

        Implementation identical to Instagram service but uses Messenger integration.
        """
        integration = await self._get_integration(db_session, "messenger", auth_user_id)

        if not integration or not integration.is_active:
            raise Exception("Messenger integration not configured for this tenant")

        payload = {
            "recipient": {"id": recipient_psid},
            "message": {"text": message_text}
        }

        response = requests.post(
            f"{self.graph_api_url}/me/messages",
            params={"access_token": integration.page_access_token},
            json=payload,
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"Messenger API error: {response.text}")

        return response.json()

    async def get_user_profile(self, psid: str, access_token: str) -> Dict[str, Any]:
        """Get Messenger user profile."""
        response = requests.get(
            f"{self.graph_api_url}/{psid}",
            params={
                "fields": "name,profile_pic",
                "access_token": access_token
            },
            timeout=10
        )

        if response.status_code != 200:
            return {"id": psid, "name": "Messenger User"}

        return response.json()

    async def _get_integration(
        self,
        db_session: AsyncSession,
        channel: str,
        auth_user_id: Optional[str]
    ):
        """Get active channel integration for tenant."""
        if auth_user_id:
            return await crud.get_channel_integration(db_session, auth_user_id, channel)
        return None
```

---

## 7. Frontend Dashboard Updates

### 7.1 Update Conversations API Response

**File:** `apps/api/src/routers/conversations.py`

```python
@router.get("/", response_model=List[dict])
async def get_conversations(
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    channel: Optional[str] = Query(None),  # NEW: Filter by channel
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all active conversations.

    NEW: Support channel filtering and return channel info.
    """
    users = await crud.get_all_active_users(
        db,
        limit=limit,
        offset=offset,
        auth_user_id=current_user["id"],
        channel=channel  # NEW parameter
    )

    result = []
    for user in users:
        result.append({
            # ... existing fields ...
            "channel": user.channel,  # NEW
            "channel_username": user.channel_username,  # NEW
            "identifier": user.phone or user.channel_user_id,  # NEW: Universal ID
            "profile_pic": user.channel_profile_pic_url or user.whatsapp_profile_name,  # NEW
        })

    return result
```

### 7.2 CRM Contacts Page - Add Channel Badges

**File:** `apps/web/src/app/dashboard/crm/contacts/page.tsx`

Add channel badge/icon rendering:

```tsx
import { MessageCircle, Instagram, Facebook } from 'lucide-react';

// In contact list item
const ChannelBadge = ({ channel }: { channel: string }) => {
  const icons = {
    whatsapp: <MessageCircle className="w-4 h-4 text-green-500" />,
    instagram: <Instagram className="w-4 h-4 text-pink-500" />,
    messenger: <Facebook className="w-4 h-4 text-blue-500" />,
  };

  return (
    <span className="inline-flex items-center gap-1">
      {icons[channel]}
      <span className="text-xs text-muted-foreground capitalize">{channel}</span>
    </span>
  );
};

// Update contact table columns
const columns = [
  {
    accessorKey: "channel",
    header: "Canal",
    cell: ({ row }) => <ChannelBadge channel={row.getValue("channel")} />,
  },
  // ... other columns
];
```

### 7.3 New Integration Settings Page

**File:** `apps/web/src/app/dashboard/integrations/page.tsx`

Create new page for managing channel integrations:

```tsx
"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Instagram, Facebook, CheckCircle, XCircle } from 'lucide-react';

export default function IntegrationsPage() {
  const [instagramConnected, setInstagramConnected] = useState(false);
  const [messengerConnected, setMessengerConnected] = useState(false);

  const handleFacebookOAuth = () => {
    // Redirect to Facebook OAuth flow
    window.location.href = '/api/integrations/facebook/connect';
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Integraciones</h1>
        <p className="text-muted-foreground">
          Conecta tus canales de mensajería para recibir leads desde múltiples plataformas.
        </p>
      </div>

      {/* Instagram Integration Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Instagram className="w-8 h-8 text-pink-500" />
              <div>
                <CardTitle>Instagram Direct Messages</CardTitle>
                <CardDescription>
                  Recibe mensajes directos de Instagram en tu dashboard
                </CardDescription>
              </div>
            </div>
            {instagramConnected ? (
              <CheckCircle className="w-6 h-6 text-green-500" />
            ) : (
              <XCircle className="w-6 h-6 text-gray-300" />
            )}
          </div>
        </CardHeader>
        <CardContent>
          {!instagramConnected ? (
            <>
              <p className="text-sm text-muted-foreground mb-4">
                Conecta tu cuenta de Instagram Business para recibir y responder mensajes.
              </p>
              <Button onClick={handleFacebookOAuth}>
                Conectar Instagram
              </Button>
            </>
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-green-600">✓ Instagram conectado correctamente</p>
              <p className="text-xs text-muted-foreground">
                Webhook URL: https://yourdomain.com/webhook/instagram
              </p>
              <Button variant="outline" size="sm">
                Desconectar
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Messenger Integration Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Facebook className="w-8 h-8 text-blue-500" />
              <div>
                <CardTitle>Facebook Messenger</CardTitle>
                <CardDescription>
                  Recibe mensajes de Facebook Messenger en tu dashboard
                </CardDescription>
              </div>
            </div>
            {messengerConnected ? (
              <CheckCircle className="w-6 h-6 text-green-500" />
            ) : (
              <XCircle className="w-6 h-6 text-gray-300" />
            )}
          </div>
        </CardHeader>
        <CardContent>
          {!messengerConnected ? (
            <>
              <p className="text-sm text-muted-foreground mb-4">
                Conecta tu página de Facebook para recibir y responder mensajes de Messenger.
              </p>
              <Button onClick={handleFacebookOAuth}>
                Conectar Messenger
              </Button>
            </>
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-green-600">✓ Messenger conectado correctamente</p>
              <p className="text-xs text-muted-foreground">
                Webhook URL: https://yourdomain.com/webhook/messenger
              </p>
              <Button variant="outline" size="sm">
                Desconectar
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## 8. CRUD Operations Updates

**File:** `packages/database/whatsapp_bot_database/crud.py`

### 8.1 Update User Lookup Functions

```python
async def get_user_by_identifier(
    db: AsyncSession,
    identifier: str,
    channel: str,
    auth_user_id: Optional[str] = None
) -> Optional[User]:
    """
    Get user by phone (WhatsApp) or channel_user_id (Instagram/Messenger).

    Args:
        identifier: Phone number or PSID
        channel: 'whatsapp', 'instagram', or 'messenger'
        auth_user_id: Tenant ID for multi-tenant filtering

    Returns:
        User object or None
    """
    if channel == "whatsapp":
        # Use existing phone lookup
        return await get_user_by_phone(db, identifier, auth_user_id)
    else:
        # Lookup by channel_user_id
        query = select(User).where(
            User.channel == channel,
            User.channel_user_id == identifier
        )

        if auth_user_id:
            query = query.where(User.auth_user_id == auth_user_id)

        result = await db.execute(query)
        return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    phone: Optional[str],
    name: Optional[str] = None,
    channel: str = "whatsapp",
    channel_user_id: Optional[str] = None,
    channel_username: Optional[str] = None,
    channel_profile_pic_url: Optional[str] = None,
    auth_user_id: Optional[str] = None,
    **kwargs
) -> User:
    """
    Create new user with multi-channel support.

    Args:
        phone: Phone number (nullable for Instagram/Messenger)
        name: User's name
        channel: 'whatsapp', 'instagram', or 'messenger'
        channel_user_id: PSID for Instagram/Messenger
        channel_username: @username for Instagram
        channel_profile_pic_url: Profile picture URL
        auth_user_id: Tenant ID
    """
    user = User(
        phone=phone,
        name=name or "Unknown User",
        channel=channel,
        channel_user_id=channel_user_id,
        channel_username=channel_username,
        channel_profile_pic_url=channel_profile_pic_url,
        auth_user_id=auth_user_id,
        **kwargs
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

### 8.2 Add Channel Integration CRUD

```python
async def create_channel_integration(
    db: AsyncSession,
    auth_user_id: str,
    channel: str,
    page_id: str,
    page_access_token: str,
    page_name: Optional[str] = None,
    instagram_account_id: Optional[str] = None,
    webhook_verify_token: Optional[str] = None
) -> ChannelIntegration:
    """
    Create new channel integration for a tenant.

    Args:
        auth_user_id: Tenant ID
        channel: 'instagram' or 'messenger'
        page_id: Facebook Page ID
        page_access_token: Long-lived Page Access Token
        page_name: Facebook Page name
        instagram_account_id: Instagram Business Account ID (for Instagram only)
        webhook_verify_token: Custom webhook verification token
    """
    integration = ChannelIntegration(
        auth_user_id=auth_user_id,
        channel=channel,
        page_id=page_id,
        page_access_token=page_access_token,
        page_name=page_name,
        instagram_account_id=instagram_account_id,
        webhook_verify_token=webhook_verify_token,
        is_active=True
    )

    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return integration


async def get_channel_integration(
    db: AsyncSession,
    auth_user_id: str,
    channel: str
) -> Optional[ChannelIntegration]:
    """
    Get active channel integration for a tenant.

    Returns the first active integration found.
    """
    query = select(ChannelIntegration).where(
        ChannelIntegration.auth_user_id == auth_user_id,
        ChannelIntegration.channel == channel,
        ChannelIntegration.is_active == True
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_channel_integration_by_page(
    db: AsyncSession,
    page_id: str,
    channel: str
) -> Optional[ChannelIntegration]:
    """
    Get integration by Facebook Page ID.

    Used in webhooks to identify which tenant the message belongs to.
    """
    query = select(ChannelIntegration).where(
        ChannelIntegration.page_id == page_id,
        ChannelIntegration.channel == channel,
        ChannelIntegration.is_active == True
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_channel_integration(
    db: AsyncSession,
    integration_id: int,
    **kwargs
) -> ChannelIntegration:
    """Update existing channel integration."""
    query = select(ChannelIntegration).where(ChannelIntegration.id == integration_id)
    result = await db.execute(query)
    integration = result.scalar_one_or_none()

    if not integration:
        raise ValueError(f"Integration {integration_id} not found")

    for key, value in kwargs.items():
        setattr(integration, key, value)

    integration.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(integration)
    return integration


async def deactivate_channel_integration(
    db: AsyncSession,
    integration_id: int
) -> ChannelIntegration:
    """Deactivate (soft delete) a channel integration."""
    return await update_channel_integration(db, integration_id, is_active=False)
```

### 8.3 Update Deal Creation

```python
async def create_deal(
    db: AsyncSession,
    user_id: int,
    title: str,
    source: str = "whatsapp",  # Updated to accept multi-channel sources
    stage: str = "new_lead",
    **kwargs
) -> Deal:
    """
    Create deal with channel source tracking.

    Args:
        source: 'whatsapp', 'instagram', 'messenger', or 'test'
    """
    # Validate source
    valid_sources = ["whatsapp", "instagram", "messenger", "test"]
    if source not in valid_sources:
        raise ValueError(f"Invalid source. Must be one of: {valid_sources}")

    deal = Deal(
        user_id=user_id,
        title=title,
        source=source,
        stage=stage,
        **kwargs
    )

    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal
```

### 8.4 Update Active Users Query

```python
async def get_all_active_users(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    auth_user_id: Optional[str] = None,
    channel: Optional[str] = None  # NEW: Filter by channel
) -> List[User]:
    """
    Get all active users with optional channel filtering.

    Args:
        limit: Maximum users to return
        offset: Pagination offset
        auth_user_id: Filter by tenant
        channel: Filter by channel ('whatsapp', 'instagram', 'messenger')
    """
    query = select(User).where(User.total_messages > 0)

    if auth_user_id:
        query = query.where(User.auth_user_id == auth_user_id)

    if channel:
        query = query.where(User.channel == channel)

    query = query.order_by(User.last_message_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    return result.scalars().all()
```

---

## 9. Authentication & App Registration

### 9.1 Facebook App Setup (One-time per Deployment)

**Manual steps** (performed by admin):

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create new Facebook App (type: Business)
3. Add **Instagram** and **Messenger** products
4. Configure OAuth Redirect URIs:
   - `https://yourdomain.com/api/integrations/facebook/callback`
5. Generate App Secret
6. Set up webhook endpoints:
   - Instagram: `https://yourdomain.com/webhook/instagram`
   - Messenger: `https://yourdomain.com/webhook/messenger`
7. Request permissions review from Meta:
   - `pages_manage_metadata`
   - `pages_messaging`
   - `instagram_basic`
   - `instagram_manage_messages`

### 9.2 Per-Tenant OAuth Flow

**File:** `apps/api/src/routers/integrations.py`

```python
"""
Facebook/Instagram OAuth flow for per-tenant integration.
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import RedirectResponse
import requests
import os
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..routers.auth import get_current_user
from whatsapp_bot_database import crud

router = APIRouter(prefix="/integrations", tags=["integrations"])

FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_REDIRECT_URI = os.getenv("FACEBOOK_REDIRECT_URI")


@router.get("/facebook/connect")
async def facebook_oauth_start(current_user: dict = Depends(get_current_user)):
    """
    Initiate Facebook OAuth flow.

    Redirects user to Facebook login to authorize app.
    """
    # Generate state token for CSRF protection
    import secrets
    state = secrets.token_urlsafe(32)

    # Store state in session or database (for validation in callback)
    # For simplicity, using user ID as state (in production, use secure session)

    # Required scopes
    scopes = [
        "pages_manage_metadata",
        "pages_messaging",
        "instagram_basic",
        "instagram_manage_messages"
    ]

    oauth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={FACEBOOK_APP_ID}&"
        f"redirect_uri={FACEBOOK_REDIRECT_URI}&"
        f"state={state}&"
        f"scope={','.join(scopes)}"
    )

    return RedirectResponse(url=oauth_url)


@router.get("/facebook/callback")
async def facebook_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Handle Facebook OAuth callback.

    Exchange authorization code for access token, retrieve user's pages,
    and store page access tokens in database.
    """
    # Validate state (CSRF protection)
    # In production, validate against stored session state

    # Exchange code for user access token
    token_response = requests.get(
        "https://graph.facebook.com/v18.0/oauth/access_token",
        params={
            "client_id": FACEBOOK_APP_ID,
            "client_secret": FACEBOOK_APP_SECRET,
            "redirect_uri": FACEBOOK_REDIRECT_URI,
            "code": code
        }
    )

    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get access token")

    user_access_token = token_response.json().get("access_token")

    # Get user's Facebook Pages
    pages_response = requests.get(
        "https://graph.facebook.com/v18.0/me/accounts",
        params={"access_token": user_access_token}
    )

    if pages_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get pages")

    pages = pages_response.json().get("data", [])

    if not pages:
        raise HTTPException(status_code=400, detail="No Facebook Pages found")

    # Store each page as a potential integration
    integrations_created = []

    for page in pages:
        page_id = page.get("id")
        page_access_token = page.get("access_token")
        page_name = page.get("name")

        # Get Instagram account connected to page (if any)
        instagram_response = requests.get(
            f"https://graph.facebook.com/v18.0/{page_id}",
            params={
                "fields": "instagram_business_account",
                "access_token": page_access_token
            }
        )

        instagram_account_id = None
        if instagram_response.status_code == 200:
            instagram_data = instagram_response.json()
            instagram_account_id = instagram_data.get("instagram_business_account", {}).get("id")

        # Create Messenger integration
        messenger_integration = await crud.create_channel_integration(
            db,
            auth_user_id=current_user["id"],
            channel="messenger",
            page_id=page_id,
            page_access_token=page_access_token,
            page_name=page_name
        )
        integrations_created.append(("messenger", page_name))

        # Create Instagram integration if account exists
        if instagram_account_id:
            instagram_integration = await crud.create_channel_integration(
                db,
                auth_user_id=current_user["id"],
                channel="instagram",
                page_id=page_id,
                page_access_token=page_access_token,
                page_name=page_name,
                instagram_account_id=instagram_account_id
            )
            integrations_created.append(("instagram", page_name))

        # Subscribe webhook for this page
        await _subscribe_webhook(page_id, page_access_token)

    # Redirect to integrations page with success message
    return RedirectResponse(
        url=f"/dashboard/integrations?success=true&count={len(integrations_created)}"
    )


async def _subscribe_webhook(page_id: str, page_access_token: str):
    """
    Subscribe webhook for a Facebook Page.

    Subscribes to 'messages', 'messaging_postbacks', 'messaging_optins'.
    """
    response = requests.post(
        f"https://graph.facebook.com/v18.0/{page_id}/subscribed_apps",
        params={
            "subscribed_fields": "messages,messaging_postbacks,messaging_optins",
            "access_token": page_access_token
        }
    )

    if response.status_code != 200:
        # Log error but don't fail the OAuth flow
        print(f"Failed to subscribe webhook for page {page_id}: {response.text}")
```

---

## 10. Security & Rate Limiting

### 10.1 Webhook Verification

**File:** `apps/api/src/routers/meta_webhook.py` (already included above)

- Validate Meta signature on all incoming webhooks using HMAC-SHA256
- Store and check webhook verify tokens per tenant in `channel_integrations.webhook_verify_token`
- Rate limit webhook endpoints (Meta can send bursts during active conversations)

### 10.2 Token Security

**Best Practices:**

1. **Encrypt tokens at rest:**
   - Use cryptography library to encrypt `page_access_token` before storing
   - Decrypt only when making API calls

2. **Token refresh:**
   - Long-lived tokens expire after 60 days
   - Implement background job to refresh tokens before expiration
   - Alert tenant if refresh fails

3. **Environment variables:**
   - Store `FACEBOOK_APP_SECRET` securely
   - Never expose in logs or error messages

**File:** `apps/api/src/utils/encryption.py` (NEW)

```python
"""
Utility for encrypting sensitive data like access tokens.
"""

from cryptography.fernet import Fernet
import os

# Load encryption key from environment (generate with Fernet.generate_key())
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "").encode()
cipher = Fernet(ENCRYPTION_KEY) if ENCRYPTION_KEY else None


def encrypt_token(token: str) -> str:
    """Encrypt access token."""
    if not cipher:
        return token  # Skip encryption in dev if key not set
    return cipher.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt access token."""
    if not cipher:
        return encrypted_token
    return cipher.decrypt(encrypted_token.encode()).decode()
```

### 10.3 Rate Limiting

**Update:** `apps/api/src/main.py`

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply higher rate limit to webhooks (Meta can burst)
@app.middleware("http")
async def webhook_rate_limit(request: Request, call_next):
    if request.url.path.startswith("/webhook/"):
        # Allow 500 requests per minute for webhooks
        # (higher than default 200/min for regular API)
        pass
    response = await call_next(request)
    return response
```

**Meta API Rate Limits:**

- **Platform limit:** 200 calls per user per hour
- **Instagram messaging:** 200 messages per 24h to users who haven't messaged first (24-hour window)
- **Messenger:** No strict outbound limits, but subject to spam detection

**Implementation strategy:**

- Queue outbound messages if rate limit approaching
- Implement exponential backoff for failed API calls
- Monitor rate limit headers in Meta API responses

---

## 11. Testing Strategy

### 11.1 Unit Tests

**Files to create:**

1. `apps/api/tests/unit/test_meta_webhook.py`
```python
"""Test webhook parsing and signature verification."""
import pytest
from apps.api.src.routers.meta_webhook import _verify_webhook_signature

def test_verify_valid_signature():
    body = b'{"test": "data"}'
    # Generate valid signature
    # Assert verification passes

def test_verify_invalid_signature():
    # Assert verification fails

def test_normalize_instagram_message():
    # Test MessageAdapter for Instagram
```

2. `apps/bot-engine/tests/unit/test_message_adapter.py`
```python
"""Test message normalization across channels."""
import pytest
from bot_engine.services.message_adapter import MessageAdapter

def test_normalize_instagram_message():
    raw_payload = {
        "sender": {"id": "12345"},
        "message": {"text": "Hello", "mid": "m_123"},
        "timestamp": 1234567890000
    }

    normalized = MessageAdapter.normalize_message("instagram", raw_payload)

    assert normalized["channel"] == "instagram"
    assert normalized["user_id"] == "12345"
    assert normalized["message_text"] == "Hello"

def test_normalize_messenger_message():
    # Similar test for Messenger
```

3. `apps/bot-engine/tests/unit/test_instagram_service.py`
```python
"""Test Instagram API service with mocking."""
import pytest
from unittest.mock import patch, AsyncMock
from bot_engine.services.instagram_service import InstagramService

@pytest.mark.asyncio
@patch('requests.post')
async def test_send_message_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"message_id": "m_123"}

    service = InstagramService()
    # Mock db session
    result = await service.send_message("psid", "Hello", mock_db, "user_id")

    assert result["message_id"] == "m_123"
```

4. `apps/bot-engine/tests/unit/test_messenger_service.py`
```python
"""Test Messenger API service."""
# Similar structure to Instagram tests
```

### 11.2 Integration Tests

**Files to create:**

1. `apps/api/tests/integration/test_instagram_flow.py`
```python
"""Test full Instagram message flow end-to-end."""
import pytest
from httpx import AsyncClient
from apps.api.src.main import app

@pytest.mark.asyncio
async def test_instagram_webhook_verify():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/webhook/instagram",
            params={
                "hub.mode": "subscribe",
                "hub.challenge": "123456",
                "hub.verify_token": "correct_token"
            }
        )
        assert response.status_code == 200
        assert response.text == "123456"

@pytest.mark.asyncio
async def test_instagram_message_processing(db_session):
    # Mock Instagram webhook payload
    payload = {
        "object": "page",
        "entry": [{
            "messaging": [{
                "sender": {"id": "test_psid"},
                "message": {"text": "Hello bot"}
            }]
        }]
    }

    # Send webhook
    # Assert user created
    # Assert message saved
    # Assert bot response sent
```

2. `apps/api/tests/integration/test_messenger_flow.py`
```python
"""Test full Messenger message flow."""
# Similar to Instagram tests
```

3. `apps/api/tests/integration/test_multi_channel_crm.py`
```python
"""Test CRM sync across multiple channels."""
import pytest

@pytest.mark.asyncio
async def test_lead_source_tracked_in_hubspot():
    # Create users from different channels
    # Trigger HubSpot sync
    # Assert lead_source_channel is set correctly

@pytest.mark.asyncio
async def test_deals_created_with_correct_source():
    # Create deals from different channels
    # Assert source field matches channel
```

### 11.3 Manual Testing Checklist

**Instagram:**
- [ ] Instagram DM received and webhook triggered
- [ ] User created with correct channel and channel_user_id
- [ ] Bot response sent successfully
- [ ] Message appears in dashboard with Instagram badge
- [ ] HubSpot contact created with lead_source_channel = "instagram"
- [ ] Deal created with source = "instagram"

**Messenger:**
- [ ] Messenger message received and webhook triggered
- [ ] User created with correct channel
- [ ] Bot response sent successfully
- [ ] Message appears in dashboard with Messenger badge
- [ ] HubSpot contact synced with correct source
- [ ] Deal created with correct source

**Multi-Channel:**
- [ ] Same user can message from WhatsApp and Instagram (separate User records)
- [ ] Dashboard filtering by channel works
- [ ] Phone collection prompt works for Instagram/Messenger users
- [ ] Webhook verification succeeds for both channels
- [ ] OAuth flow completes and stores tokens
- [ ] Token encryption/decryption works

---

## 12. Environment Variables

**Update:** `.env.example`

```env
# ================================================
# Existing Variables
# ================================================

OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
JWT_SECRET=your-secret-key-change-in-production

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+...

# HubSpot
HUBSPOT_ACCESS_TOKEN=pat-na1-...

# Supabase
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...

LOG_LEVEL=INFO

# ================================================
# NEW: Facebook/Instagram Integration
# ================================================

# Facebook App Credentials (from developers.facebook.com)
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret

# Webhook Verification Token (custom string for webhook verification)
FACEBOOK_VERIFY_TOKEN=your-custom-verify-token-min-20-chars

# OAuth Redirect URI (must match Facebook App settings)
FACEBOOK_REDIRECT_URI=https://yourdomain.com/api/integrations/facebook/callback

# Graph API Version
GRAPH_API_VERSION=v18.0
GRAPH_API_URL=https://graph.facebook.com/v18.0

# Token Encryption Key (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=your-fernet-encryption-key-here
```

**Security Notes:**

- `FACEBOOK_APP_SECRET`: Keep secret, never expose in client
- `FACEBOOK_VERIFY_TOKEN`: Custom string (min 20 characters) for webhook verification
- `ENCRYPTION_KEY`: Used to encrypt Page Access Tokens at rest in database
- All tokens should be rotated periodically

---

## 13. Deployment (Coolify)

**Strategy:** Deploy multi-service application to self-hosted Coolify instance with proper health checks and monitoring.

### 13.1 Coolify Architecture

Coolify is a self-hosted alternative to Heroku/Render that supports:
- Docker Compose deployments
- Automatic HTTPS via Let's Encrypt
- Built-in reverse proxy (Traefik)
- PostgreSQL managed databases
- Environment variable management

### 13.2 Update Docker Compose for Production

**File:** `docker-compose.prod.yml` (NEW)

```yaml
version: '3.8'

services:
  # ========================================
  # API Service (FastAPI)
  # ========================================
  api:
    build:
      context: ./apps/api
      dockerfile: Dockerfile
      target: production
    container_name: whatsapp-bot-api
    restart: unless-stopped
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - HUBSPOT_ACCESS_TOKEN=${HUBSPOT_ACCESS_TOKEN}
      - FACEBOOK_APP_ID=${FACEBOOK_APP_ID}
      - FACEBOOK_APP_SECRET=${FACEBOOK_APP_SECRET}
      - FACEBOOK_VERIFY_TOKEN=${FACEBOOK_VERIFY_TOKEN}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - LOG_LEVEL=INFO
    ports:
      - "8000:8000"
    volumes:
      - api-uploads:/app/rag_uploads
      - chroma-data:/app/chroma_db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - app-network
    depends_on:
      db:
        condition: service_healthy

  # ========================================
  # Web Service (Next.js)
  # ========================================
  web:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
      target: production
    container_name: whatsapp-bot-web
    restart: unless-stopped
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    ports:
      - "3000:3000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - app-network
    depends_on:
      - api

  # ========================================
  # PostgreSQL Database
  # ========================================
  db:
    image: postgres:15-alpine
    container_name: whatsapp-bot-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

volumes:
  postgres-data:
    driver: local
  api-uploads:
    driver: local
  chroma-data:
    driver: local

networks:
  app-network:
    driver: bridge
```

### 13.3 Coolify Configuration

**File:** `.coolify/config.json` (NEW)

```json
{
  "name": "whatsapp-sales-bot",
  "type": "docker-compose",
  "description": "Multi-tenant WhatsApp Sales Bot with Instagram & Messenger integration",
  "compose_file": "docker-compose.prod.yml",
  "domains": [
    {
      "service": "web",
      "domain": "yourdomain.com",
      "port": 3000
    },
    {
      "service": "api",
      "domain": "api.yourdomain.com",
      "port": 8000
    }
  ],
  "health_checks": [
    {
      "service": "api",
      "path": "/health",
      "port": 8000,
      "interval": 30
    },
    {
      "service": "web",
      "path": "/api/health",
      "port": 3000,
      "interval": 30
    }
  ],
  "environment_variables": [
    "DATABASE_URL",
    "OPENAI_API_KEY",
    "JWT_SECRET",
    "FACEBOOK_APP_ID",
    "FACEBOOK_APP_SECRET",
    "FACEBOOK_VERIFY_TOKEN",
    "ENCRYPTION_KEY"
  ]
}
```

### 13.4 Deployment Steps for Coolify

**Documentation:** `DEPLOYMENT_COOLIFY.md` (NEW)

```markdown
# Deployment Guide: Coolify

## Prerequisites

1. Coolify instance running (self-hosted)
2. Domain name pointing to Coolify server
3. GitHub repository access
4. Environment variables prepared

## Step 1: Create New Project in Coolify

1. Login to Coolify dashboard
2. Click "New Resource" → "Docker Compose"
3. Select repository: `lucasbneuman/whatsapp_sales_bot`
4. Branch: `saas-migration`
5. Compose file: `docker-compose.prod.yml`

## Step 2: Configure Domains

**Web Service:**
- Domain: `yourdomain.com`
- Port: `3000`
- HTTPS: ✅ (automatic Let's Encrypt)

**API Service:**
- Domain: `api.yourdomain.com`
- Port: `8000`
- HTTPS: ✅

## Step 3: Set Environment Variables

Go to "Environment Variables" tab and add:

### Database
```
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/whatsapp_bot
POSTGRES_DB=whatsapp_bot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<generate-strong-password>
```

### OpenAI
```
OPENAI_API_KEY=sk-...
```

### Auth
```
JWT_SECRET=<generate-with-openssl-rand-hex-32>
```

### Twilio (WhatsApp)
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
```

### HubSpot
```
HUBSPOT_ACCESS_TOKEN=pat-na1-xxxxxxxxx
```

### Facebook/Instagram (NEW)
```
FACEBOOK_APP_ID=1234567890
FACEBOOK_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
FACEBOOK_VERIFY_TOKEN=<custom-string-min-20-chars>
FACEBOOK_REDIRECT_URI=https://yourdomain.com/api/integrations/facebook/callback
ENCRYPTION_KEY=<generate-with-cryptography.fernet>
```

### Supabase
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...
```

### Frontend
```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
```

## Step 4: Configure Webhooks

After deployment, configure webhooks in external services:

### Meta (Facebook/Instagram)

1. Go to developers.facebook.com → Your App → Webhooks
2. Add Callback URLs:
   - Instagram: `https://api.yourdomain.com/webhook/instagram`
   - Messenger: `https://api.yourdomain.com/webhook/messenger`
3. Verify Token: Use value from `FACEBOOK_VERIFY_TOKEN` env var
4. Subscribe to fields: `messages`, `messaging_postbacks`, `messaging_optins`

### Twilio (WhatsApp)

1. Go to Twilio Console → WhatsApp Sandbox
2. Update webhook URL: `https://api.yourdomain.com/webhook/whatsapp`

## Step 5: Database Migrations

After first deployment:

```bash
# SSH into Coolify server
ssh user@coolify-server

# Access API container
docker exec -it whatsapp-bot-api bash

# Apply migrations
psql $DATABASE_URL < /app/packages/database/migrations/006_add_messaging_channels.sql

# Initialize subscription plans
python /app/scripts/init_subscription_plans.py
```

## Step 6: Health Checks

Verify all services are healthy:

- API: `https://api.yourdomain.com/health`
- Web: `https://yourdomain.com`
- Database: Check Coolify logs

## Step 7: Monitor Logs

Coolify provides real-time logs for each service:

1. Go to project in Coolify
2. Click "Logs" tab
3. Select service (api, web, db)
4. Monitor for errors

## Rollback Procedure

If deployment fails:

1. Go to Coolify → Deployments
2. Select previous successful deployment
3. Click "Redeploy"

## Scaling

To scale services:

1. Update `docker-compose.prod.yml`
2. Add `deploy.replicas` to service:
   ```yaml
   services:
     api:
       deploy:
         replicas: 3
   ```
3. Push changes and redeploy

## Backup Strategy

**Database Backups:**
- Coolify automatically backs up PostgreSQL daily
- Manual backup: `docker exec whatsapp-bot-db pg_dump -U postgres whatsapp_bot > backup.sql`

**Volume Backups:**
- `api-uploads`: RAG documents
- `chroma-data`: Vector embeddings
- Schedule weekly backups via Coolify

## Troubleshooting

### Webhook Verification Fails
- Check `FACEBOOK_VERIFY_TOKEN` matches in env vars and Meta dashboard
- Check webhook URL is accessible: `curl https://api.yourdomain.com/webhook/instagram`

### Messages Not Received
- Check Meta webhook logs in developers.facebook.com
- Verify Page Access Tokens in `channel_integrations` table
- Check API logs for errors

### Database Connection Fails
- Verify `DATABASE_URL` format: `postgresql+asyncpg://...`
- Check database container is healthy: `docker ps`
- Check network connectivity: `docker network inspect app-network`
```

### 13.5 Health Check Endpoints

**File:** `apps/api/src/routers/health.py` (UPDATE)

```python
"""Health check endpoints for monitoring."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
import os

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "whatsapp-sales-bot-api",
        "version": "2.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check including:
    - Database connectivity
    - Environment variables
    - External API availability
    """
    checks = {
        "status": "healthy",
        "checks": {}
    }

    # Database check
    try:
        await db.execute("SELECT 1")
        checks["checks"]["database"] = "healthy"
    except Exception as e:
        checks["status"] = "unhealthy"
        checks["checks"]["database"] = f"unhealthy: {str(e)}"

    # Environment variables check
    required_vars = ["OPENAI_API_KEY", "JWT_SECRET", "FACEBOOK_APP_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        checks["status"] = "unhealthy"
        checks["checks"]["environment"] = f"missing: {missing_vars}"
    else:
        checks["checks"]["environment"] = "healthy"

    return checks
```

### 13.6 Monitoring & Alerting

**Coolify Built-in Monitoring:**

- CPU/Memory usage per container
- Request rate and response times
- Error logs aggregation
- Uptime percentage

**External Monitoring (Optional):**

- **Sentry:** Error tracking for API and bot-engine
- **UptimeRobot:** External uptime monitoring for webhooks
- **Prometheus + Grafana:** Advanced metrics (if Coolify supports)

---

## 14. Architectural Trade-offs & Challenges

### 14.1 Key Decisions

#### Decision 1: Unified vs. Separate Webhooks

**Chosen:** Separate webhook endpoints per channel (`/webhook/instagram`, `/webhook/messenger`)

**Rationale:**
- Easier debugging (logs separated by channel)
- Channel-specific rate limiting
- Clearer code organization

**Trade-off:** Slightly more code duplication

#### Decision 2: Phone Requirement

**Chosen:** Make `phone` nullable, use `channel_user_id` as primary identifier

**Rationale:**
- Instagram/Messenger users may never provide phone number
- CRM systems can use alternative identifiers
- Bot can prompt for phone if needed for business logic

**Trade-off:** Existing code assumes phone exists (requires careful updates)

#### Decision 3: Token Storage

**Chosen:** Per-tenant tokens in database (`channel_integrations` table)

**Rationale:**
- Multi-tenant SaaS requires per-tenant credentials
- Each tenant manages their own Facebook/Instagram pages
- Scalable for enterprise plans

**Trade-off:** More complex than single shared token, requires encryption

#### Decision 4: Same LangGraph Workflow

**Chosen:** Reuse existing 11-node workflow for all channels

**Rationale:**
- Code reuse and consistency
- Easier maintenance
- Same conversation quality across channels

**Trade-off:** Less channel-specific customization (can be added later via config)

### 14.2 Key Challenges

#### Challenge 1: User Identification

**Problem:** WhatsApp uses phone numbers, Instagram/Messenger use PSIDs (Page-Scoped IDs)

**Solution:**
- Add `channel` and `channel_user_id` fields to User model
- Make `phone` nullable
- Update lookup functions to handle both identifiers
- Create composite unique index on `(channel, channel_user_id)`

#### Challenge 2: Phone Collection for CRM

**Problem:** CRM workflows may require phone numbers, but Instagram/Messenger don't provide them

**Solution:**
- Bot prompts user for phone if needed (business logic decision)
- Store phone in `user.phone` once collected
- HubSpot can use `channel_user_id` as fallback identifier

#### Challenge 3: Message Format Differences

**Problem:** Each channel supports different media types and message structures

**Solution:**
- Create `MessageAdapter` to normalize formats
- Store raw payload in `metadata` field for channel-specific features
- Start with text-only support, expand to media later

#### Challenge 4: Token Management

**Problem:** Page Access Tokens expire after 60 days

**Solution:**
- Store long-lived tokens (exchanged during OAuth)
- Implement background job to refresh tokens (check expiration weekly)
- Alert tenant if token refresh fails or is about to expire
- Provide re-authentication flow in UI

#### Challenge 5: Webhook Reliability

**Problem:** Meta may retry failed webhooks multiple times, causing duplicate processing

**Solution:**
- Implement idempotency using `message_id` (deduplicate in database)
- Store `channel_message_id` in Message model
- Check for existing message before processing webhook

#### Challenge 6: Rate Limits

**Problem:** Instagram has strict limits for outbound messages (200/24h to users who didn't initiate)

**Solution:**
- Track 24-hour message window per user
- Queue messages if limit approaching
- Respect "message tags" for different message types
- Handle rate limit errors gracefully (retry with backoff)

### 14.3 Future Enhancements

**Phase 2 (Post-MVP):**

1. **Media Support:**
   - Images, videos, audio in Instagram/Messenger
   - Stickers and GIFs

2. **Advanced Features:**
   - Instagram Story mentions/replies
   - Messenger quick replies and templates
   - Read receipts and typing indicators

3. **Analytics:**
   - Channel performance comparison
   - Conversion rates by source
   - Response time by channel

4. **Automation:**
   - Automated token refresh
   - Channel health monitoring dashboard
   - Automatic webhook re-subscription

---

## 15. Agent Coordination

### 15.1 Implementation Phases

This section outlines which agent handles which phase of implementation, ensuring clear responsibility boundaries and efficient parallel work where possible.

#### Phase 1: Database Foundation (Week 1)

**Agent:** `lead-developer`

**Tasks:**
- Create migration `006_add_messaging_channels.sql`
- Update User model with channel fields
- Create ChannelIntegration model
- Update Message model
- Apply migration to development database
- Reinstall database package: `pip install -e packages/database`
- Run validation queries

**Dependencies:** None (can start immediately)

**Deliverables:**
- Migration file applied
- Models updated and tested
- TASK.md entry created
- Commit: "feat: Add multi-channel database support"

---

#### Phase 2: CRUD Operations (Week 1)

**Agent:** `lead-developer`

**Tasks:**
- Implement `get_user_by_identifier()` for multi-channel lookup
- Implement channel integration CRUD operations
- Update `create_user()` to support channel fields
- Update `create_deal()` to validate source
- Update `get_all_active_users()` with channel filter
- Write unit tests for new CRUD functions

**Dependencies:** Phase 1 (database models)

**Deliverables:**
- CRUD operations implemented in `crud.py`
- Unit tests passing
- TASK.md entry
- Commit: "feat: Add multi-channel CRUD operations"

---

#### Phase 3: Webhook Infrastructure (Week 1-2)

**Agent:** `lead-developer`

**Tasks:**
- Create `meta_webhook.py` router
- Implement Instagram webhook verify endpoint
- Implement Instagram webhook POST handler
- Implement Messenger webhook endpoints
- Add webhook signature verification
- Create `MessageAdapter` service
- Add error handling and logging

**Dependencies:** Phase 2 (CRUD operations)

**Deliverables:**
- Webhook endpoints functional
- Signature verification working
- TASK.md entry
- API_DOCUMENTATION.md updated
- Commit: "feat: Add Instagram and Messenger webhook handlers"

---

#### Phase 4: Bot Engine Updates (Week 2)

**Agent:** `lead-developer`

**Tasks:**
- Update `ConversationState` with channel fields
- Update `run_workflow()` function signature
- Modify `data_collector_node` for phone collection
- Create `InstagramService` (use Context7 MCP for API docs)
- Create `MessengerService` (use Context7 MCP for API docs)
- Create `MessageSender` routing service
- Test workflow with mock channel data

**Dependencies:** Phase 3 (webhooks)

**Note:** Use Context7 MCP to research Facebook Graph API before implementing services:
```
- Library: "Facebook Graph API"
- Topic: "Instagram messaging API" / "Messenger send API"
- Mode: "code"
```

**Deliverables:**
- LangGraph state updated
- Channel services implemented
- Bot engine tests passing
- TASK.md entry
- Commit: "feat: Update bot engine for multi-channel support"

---

#### Phase 5: HubSpot Sync (Week 2)

**Agent:** `lead-developer`

**Tasks:**
- Update `_prepare_properties()` with lead source field
- Update `_search_contact()` to search by channel_user_id
- Add `_ensure_custom_properties()` for new fields
- Test HubSpot sync with Instagram/Messenger users
- Handle cases where phone is missing

**Dependencies:** Phase 4 (bot engine)

**Deliverables:**
- HubSpot sync updated
- Custom properties created in HubSpot
- TASK.md entry
- Commit: "feat: Add lead source tracking to HubSpot sync"

---

#### Phase 6: OAuth & Integrations API (Week 3)

**Agent:** `lead-developer`

**Tasks:**
- Create `integrations.py` router
- Implement `/integrations/facebook/connect` endpoint
- Implement `/integrations/facebook/callback` endpoint
- Add webhook subscription logic
- Implement token encryption utilities
- Add integration status endpoints
- Test OAuth flow end-to-end

**Dependencies:** Phase 2 (channel integration CRUD)

**Deliverables:**
- OAuth flow functional
- Tokens stored securely
- API_DOCUMENTATION.md updated
- TASK.md entry
- Commit: "feat: Add Facebook OAuth integration flow"

---

#### Phase 7: Frontend Dashboard (Week 3)

**Agent:** `lead-developer` (or dedicated frontend developer if available)

**Tasks:**
- Update conversations API response with channel info
- Create channel badge component
- Update CRM contacts page with channel badges
- Create `/dashboard/integrations` page
- Implement OAuth initiation from frontend
- Add channel filtering in conversations
- Test UI with mock multi-channel data

**Dependencies:** Phase 6 (OAuth API)

**Deliverables:**
- Frontend displays channel info
- Integrations page functional
- TASK.md entry
- Commit: "feat: Add multi-channel UI to dashboard"

---

#### Phase 8: Deployment Configuration (Week 3-4)

**Agent:** `devops-deployment-specialist`

**Tasks:**
- Create `docker-compose.prod.yml` for production
- Update Dockerfiles with health checks
- Create `.coolify/config.json`
- Write `DEPLOYMENT_COOLIFY.md` documentation
- Configure domain mappings
- Set up environment variable templates
- Test deployment to Coolify staging

**Dependencies:** Phases 1-7 (full backend + frontend)

**Note:** Focus on Coolify instead of Render.com

**Deliverables:**
- Production Docker Compose ready
- Coolify configuration complete
- Deployment documentation written
- Health checks implemented
- TASK.md entry
- Commit: "chore: Add Coolify deployment configuration"

---

#### Phase 9: Testing (Week 4)

**Agent:** `qa-tester-validator`

**Tasks:**
- Write unit tests for message adapter
- Write unit tests for Instagram/Messenger services
- Write integration tests for Instagram flow
- Write integration tests for Messenger flow
- Write integration tests for multi-channel CRM
- Execute manual testing checklist
- Document test results
- Update BUG_TRACKER.md if issues found

**Dependencies:** Phases 1-7 (all code complete)

**Deliverables:**
- Test suite coverage >80%
- All tests passing
- Manual test checklist completed
- QA report in `.claude/QA_REPORT_INSTAGRAM_FACEBOOK.md`
- TASK.md entry
- Commit: "test: Add comprehensive tests for multi-channel support"

---

#### Phase 10: Database Validation (Week 4)

**Agent:** `supabase-database-validator`

**Tasks:**
- Validate migration 006 applied correctly
- Verify indexes created on channel fields
- Check foreign key constraints
- Validate composite unique constraints
- Test multi-channel queries performance
- Ensure RLS policies updated (if using Supabase)
- Run integrity checks on channel_integrations table

**Dependencies:** Phase 1 (database models) + Phase 9 (test data)

**Deliverables:**
- Database validation report
- Performance recommendations
- TASK.md entry
- Commit: "chore: Validate multi-channel database schema"

---

#### Phase 11: Documentation (Week 4)

**Agent:** `documentation-architect`

**Tasks:**
- Update `API_DOCUMENTATION.md` with new endpoints:
  - `/webhook/instagram` (GET, POST)
  - `/webhook/messenger` (GET, POST)
  - `/integrations/facebook/connect`
  - `/integrations/facebook/callback`
- Update `ARCHITECTURE.md` with multi-channel architecture diagram
- Create user guide for setting up Instagram/Messenger integrations
- Document environment variables
- Update `CLAUDE.md` with multi-channel patterns
- Consolidate agent task logs

**Dependencies:** All phases (complete implementation)

**Deliverables:**
- API documentation complete
- Architecture documentation updated
- User guide created
- TASK.md entry
- Commit: "docs: Document Instagram and Messenger integration"

---

#### Phase 12: Executive Summary (Week 4)

**Agent:** `executive-summary-notifier`

**Tasks:**
- Create executive summary in Notion
- Highlight business value of multi-channel support
- Document lead source tracking benefits
- Summarize implementation timeline
- List next steps and future enhancements

**Dependencies:** Phase 11 (documentation complete)

**Deliverables:**
- Notion page created with executive summary
- Stakeholders notified
- TASK.md entry

---

### 15.2 Parallel Work Opportunities

To maximize efficiency, the following phases can be executed in parallel:

**Parallel Group 1 (Week 1):**
- Phase 1: Database Foundation (lead-developer)
- Phase 8 (prep): DevOps audit current infrastructure (devops-deployment-specialist)

**Parallel Group 2 (Week 2):**
- Phase 4: Bot Engine Updates (lead-developer)
- Phase 8 (continued): Docker Compose preparation (devops-deployment-specialist)

**Parallel Group 3 (Week 3):**
- Phase 6: OAuth API (lead-developer)
- Phase 7: Frontend Dashboard (frontend developer, if separate)

**Parallel Group 4 (Week 4):**
- Phase 9: Testing (qa-tester-validator)
- Phase 10: Database Validation (supabase-database-validator)
- Phase 11: Documentation (documentation-architect)

---

### 15.3 Agent Coordination Protocol

**Before Starting Work:**

1. Each agent MUST read `.claude/TASK.md` to see recent work
2. Check `.claude/BUG_TRACKER.md` for known issues
3. Verify dependencies are complete (check TASK.md entries)

**During Work:**

1. Update TASK.md every time you complete a subtask
2. Commit after every logical code chunk
3. Use Context7 MCP for researching new dependencies/APIs
4. Follow AGENT_PROTOCOL.md strictly

**After Completing Phase:**

1. Update TASK.md with final entry
2. Update API_DOCUMENTATION.md or ARCHITECTURE.md if applicable
3. Create final commit with descriptive message
4. Clean workspace (delete temp scripts)
5. Notify next agent in sequence (via TASK.md entry)

**Example TASK.md Entry:**

```markdown
### [2025-12-04 14:30] - lead-developer
**Task:** Phase 1 - Multi-channel database foundation
**Changes:** `migrations/006_add_messaging_channels.sql`, `models.py`
**Status:** ✅ Complete - Ready for Phase 2 (CRUD operations)
```

---

### 15.4 Critical Handoff Points

**Handoff 1: Phase 1 → Phase 2**
- `lead-developer` completes migration
- `lead-developer` continues with CRUD (same agent)
- Verify: Database models can be imported without errors

**Handoff 2: Phase 7 → Phase 8**
- `lead-developer` completes frontend
- `devops-deployment-specialist` takes over
- Verify: All services run locally with `docker-compose up`

**Handoff 3: Phase 8 → Phase 9**
- `devops-deployment-specialist` completes deployment config
- `qa-tester-validator` begins testing
- Verify: Deployment to Coolify staging succeeds

**Handoff 4: Phase 9 → Phase 11**
- `qa-tester-validator` completes tests
- `documentation-architect` consolidates docs
- Verify: All tests pass, no blocking bugs

---

## Critical Files Summary

The following files are essential for the multi-channel implementation:

### Database & Models
1. `packages/database/migrations/006_add_messaging_channels.sql` - Core schema changes
2. `packages/database/whatsapp_bot_database/models.py` - User, ChannelIntegration, Message models
3. `packages/database/whatsapp_bot_database/crud.py` - Multi-channel CRUD operations

### API Layer
4. `apps/api/src/routers/meta_webhook.py` - **NEW** - Instagram/Messenger webhooks
5. `apps/api/src/routers/integrations.py` - **NEW** - Facebook OAuth flow
6. `apps/api/src/routers/conversations.py` - **UPDATE** - Channel filtering

### Bot Engine
7. `apps/bot-engine/src/graph/state.py` - **UPDATE** - ConversationState with channels
8. `apps/bot-engine/src/graph/workflow.py` - **UPDATE** - run_workflow signature
9. `apps/bot-engine/src/graph/nodes.py` - **UPDATE** - data_collector_node
10. `apps/bot-engine/src/services/message_adapter.py` - **NEW** - Message normalization
11. `apps/bot-engine/src/services/instagram_service.py` - **NEW** - Instagram API
12. `apps/bot-engine/src/services/messenger_service.py` - **NEW** - Messenger API
13. `apps/bot-engine/src/services/message_sender.py` - **NEW** - Channel routing
14. `apps/bot-engine/src/services/hubspot_sync.py` - **UPDATE** - Lead source tracking

### Frontend
15. `apps/web/src/app/dashboard/crm/contacts/page.tsx` - **UPDATE** - Channel badges
16. `apps/web/src/app/dashboard/integrations/page.tsx` - **NEW** - Integration settings

### Deployment
17. `docker-compose.prod.yml` - **NEW** - Production Docker Compose for Coolify
18. `.coolify/config.json` - **NEW** - Coolify configuration
19. `DEPLOYMENT_COOLIFY.md` - **NEW** - Deployment documentation

### Documentation
20. `API_DOCUMENTATION.md` - **UPDATE** - New endpoints
21. `ARCHITECTURE.md` - **UPDATE** - Multi-channel architecture
22. `.claude/TASK.md` - **UPDATE** - Agent coordination log

---

## Completion Criteria

This implementation is complete when:

- [ ] All 12 phases executed successfully
- [ ] Migration 006 applied to production database
- [ ] Instagram webhook receives and processes DMs
- [ ] Messenger webhook receives and processes messages
- [ ] Users created with correct channel attribution
- [ ] HubSpot contacts synced with lead_source_channel field
- [ ] Deals created with correct source (whatsapp/instagram/messenger)
- [ ] Frontend displays channel badges
- [ ] OAuth flow connects Facebook/Instagram pages
- [ ] Deployment to Coolify successful
- [ ] All tests passing (>80% coverage)
- [ ] Documentation complete and up-to-date
- [ ] Executive summary delivered to stakeholders

---

**Last Updated:** 2025-12-04
**Plan Version:** 1.0
**Estimated Timeline:** 4 weeks with parallel agent work
