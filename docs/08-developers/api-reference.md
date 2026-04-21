# API Endpoints Documentation

## Authentication Endpoints

### POST `/auth/login`
Login with email and password.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "user_metadata": {},
    "created_at": "2025-11-25T00:00:00Z"
  }
}
```

### POST `/auth/signup`
Create a new user account.

**Request**:
```json
{
  "email": "newuser@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

### POST `/auth/logout`
Logout current user (requires authentication).

### POST `/auth/refresh`
Refresh access token using refresh token.

**Request**:
```json
{
  "refresh_token": "eyJ..."
}
```

### GET `/auth/me`
Get current authenticated user profile.

---

## Conversation Endpoints

### GET `/conversations/`
Get all active conversations.

**Query Parameters**:
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records (default: 100)

**Response**:
```json
[
  {
    "id": 1,
    "phone": "+1234567890",
    "name": "John Doe",
    "email": "john@example.com",
    "lastMessage": "Hello, I'm interested in your product",
    "timestamp": "2025-11-25T10:30:00Z",
    "unread": 0,
    "isHandedOff": false,
    "mode": "AUTO",
    "stage": "qualifying",
    "sentiment": "positive",
    "conversation_summary": "Customer interested in product features",
    "total_messages": 5
  }
]
```

### GET `/conversations/{phone}`
Get detailed user information for a specific phone number.

**Response**:
```json
{
  "id": 1,
  "phone": "+1234567890",
  "name": "John Doe",
  "email": "john@example.com",
  "stage": "qualifying",
  "sentiment": "positive",
  "intent_score": 0.75,
  "conversation_mode": "AUTO",
  "conversation_summary": "Customer interested in product features",
  "last_message_at": "2025-11-25T10:30:00Z",
  "created_at": "2025-11-25T09:00:00Z",
  "updated_at": "2025-11-25T10:30:00Z"
}
```

### GET `/conversations/{phone}/messages`
Get all messages for a specific conversation.

**Query Parameters**:
- `limit` (int, optional): Maximum number of messages (default: 50)

**Response**:
```json
[
  {
    "id": 1,
    "text": "Hello! How can I help you?",
    "sender": "bot",
    "timestamp": "2025-11-25T10:00:00Z",
    "metadata": {}
  },
  {
    "id": 2,
    "text": "I'm interested in your product",
    "sender": "customer",
    "timestamp": "2025-11-25T10:01:00Z",
    "metadata": {}
  }
]
```

### DELETE `/conversations/{phone}/clear`
Clear message history for a conversation while preserving user data.

**Response**:
```json
{
  "status": "success",
  "message": "Cleared message history for John Doe",
  "user_preserved": true
}
```

---

## Bot Processing Endpoints

### POST `/bot/process`
Process a message through the bot workflow.

**Request**:
```json
{
  "phone": "+1234567890",
  "message": "I want to know more about your product",
  "history": [
    {
      "text": "Hello!",
      "sender": "user"
    }
  ]
}
```

**Response**:
```json
{
  "response": "I'd be happy to tell you about our product...",
  "user_phone": "+1234567890",
  "user_name": "John Doe",
  "intent_score": 0.75,
  "sentiment": "positive",
  "stage": "qualifying",
  "conversation_mode": "AUTO"
}
```

### GET `/bot/health`
Check bot engine health status.

---

## Configuration Endpoints

### GET `/config/`
Get all configuration settings.

**Response**:
```json
{
  "configs": {
    "system_prompt": "You are a helpful sales assistant...",
    "welcome_message": "Hello! How can I help you today?",
    "payment_link": "https://example.com/pay",
    "response_delay_minutes": 0,
    "text_audio_ratio": 50,
    "use_emojis": true,
    "tts_voice": "alloy",
    "multi_part_messages": false,
    "max_words_per_response": 100,
    "product_name": "My Product",
    "product_description": "A great product...",
    "product_features": "Feature 1, Feature 2",
    "product_benefits": "Benefit 1, Benefit 2",
    "product_price": "$99",
    "product_target_audience": "Small businesses"
  }
}
```

### PUT `/config/`
Update configuration settings.

**Request**:
```json
{
  "configs": {
    "system_prompt": "Updated prompt...",
    "product_name": "New Product Name"
  }
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Updated 2 settings",
  "configs": {
    // ... all configs including updated ones
  }
}
```

### POST `/config/reset`
Reset configuration to defaults.

---

## RAG Document Endpoints

### POST `/rag/upload`
Upload documents for RAG processing.

**Request**: `multipart/form-data`
- Field name: `files`
- Supported formats: PDF, TXT, DOC, DOCX

**Response**:
```json
{
  "status": "success",
  "uploaded": 2,
  "files": ["document1.pdf", "document2.pdf"],
  "total_chunks": 150,
  "message": "Successfully uploaded 2 file(s) with 150 total chunks"
}
```

### GET `/rag/files`
List all uploaded RAG documents.

**Response**:
```json
[
  {
    "filename": "product_guide.pdf",
    "size": 1024000,
    "uploaded_at": "1732531200.0"
  }
]
```

### DELETE `/rag/files/{filename}`
Delete a specific RAG document.

**Response**:
```json
{
  "status": "success",
  "message": "File product_guide.pdf deleted successfully"
}
```

### GET `/rag/stats`
Get RAG collection statistics.

**Response**:
```json
{
  "enabled": true,
  "total_chunks": 150,
  "collection_name": "sales_documents",
  "backend": "chromadb"
}
```

### DELETE `/rag/clear`
Clear all documents from RAG collection.

**Response**:
```json
{
  "status": "success",
  "message": "RAG collection cleared successfully"
}
```

---

## Handoff Endpoints

### POST `/handoff/{phone}/take`
Take manual control of a conversation.

**Response**:
```json
{
  "status": "success",
  "mode": "MANUAL"
}
```

### POST `/handoff/{phone}/return`
Return conversation control to the bot.

**Response**:
```json
{
  "status": "success",
  "mode": "AUTO"
}
```

### POST `/handoff/{phone}/send`
Send a manual message to a user.

**Request**:
```json
{
  "message": "Hello, this is a human agent. How can I help you?"
}
```

**Response**:
```json
{
  "status": "success",
  "message_id": 123
}
```

---

## Follow-up Endpoints

### GET `/followups/`
Get all scheduled follow-ups.

### GET `/followups/pending`
Get pending follow-ups that need to be sent.

### POST `/followups/`
Schedule a new follow-up.

### DELETE `/followups/{id}`
Cancel a scheduled follow-up.

---

## Integration Endpoints

### GET `/integrations/`
Get all integration configurations (masked).

**Response**:
```json
{
  "twilio": {
    "account_sid": "ACxxxxxxxx...",
    "whatsapp_number": "whatsapp:+14155238886",
    "configured": true
  },
  "hubspot": {
    "enabled": true,
    "configured": true
  }
}
```

### GET `/integrations/hubspot/status`
Get HubSpot integration status.

**Response**:
```json
{
  "configured": true,
  "enabled": true,
  "status": "active"
}
```

**Status values**:
- `active`: Configured and enabled
- `configured`: Configured but disabled
- `not_configured`: No credentials set

### GET `/integrations/twilio/status`
Get Twilio integration status.

**Response**:
```json
{
  "configured": true,
  "whatsapp_number": "whatsapp:+14155238886",
  "status": "active"
}
```

**Status values**:
- `active`: Fully configured
- `not_configured`: Missing credentials

### PUT `/integrations/hubspot`
Update HubSpot configuration.

**Request**:
```json
{
  "access_token": "pat-na1-...",
  "enabled": true
}
```

### PUT `/integrations/twilio`
Update Twilio configuration.

**Request**:
```json
{
  "account_sid": "ACxxxxxxxxxx",
  "auth_token": "your_auth_token",
  "whatsapp_number": "whatsapp:+14155238886"
}
```

### DELETE `/integrations/hubspot`
Remove HubSpot configuration.

### DELETE `/integrations/twilio`
Remove Twilio configuration.

### POST `/integrations/hubspot/test`
Test HubSpot connection with current credentials.

### POST `/integrations/twilio/test`
Test Twilio connection with current credentials.

---

## CRM Endpoints

### Dashboard

#### GET `/crm/dashboard/metrics`
Get CRM dashboard metrics and analytics.

**Response**:
```json
{
  "total_active_deals": 15,
  "total_won_deals": 8,
  "total_revenue": 45000.00,
  "conversion_rate": 34.78
}
```

### Deals

#### GET `/crm/deals`
Get all deals with optional filtering.

**Query Parameters**:
- `stage` (optional): Filter by stage (`new_lead`, `qualified`, `in_conversation`, `proposal_sent`, `won`, `lost`)
- `limit` (optional, default: 100): Maximum number of results
- `offset` (optional, default: 0): Pagination offset

**Response**:
```json
[
  {
    "id": 1,
    "user_id": 123,
    "title": "Lead: +1234567890",
    "value": 1500.00,
    "currency": "USD",
    "stage": "qualified",
    "probability": 25,
    "source": "whatsapp",
    "manually_qualified": false,
    "expected_close_date": null,
    "won_date": null,
    "lost_date": null,
    "lost_reason": null,
    "created_at": "2025-11-27T10:00:00",
    "updated_at": "2025-11-27T12:00:00",
    "user": {
      "id": 123,
      "phone": "+1234567890",
      "name": "John Doe",
      "email": "john@example.com",
      "stage": "qualifying"
    }
  }
]
```

#### POST `/crm/deals`
Create a new deal.

**Request**:
```json
{
  "user_id": 123,
  "title": "Custom Deal Title",
  "value": 2500.00,
  "stage": "new_lead",
  "source": "whatsapp",
  "probability": 10,
  "expected_close_date": "2025-12-31"
}
```

**Response**: Returns created deal object (same structure as GET)

#### GET `/crm/deals/{deal_id}`
Get a specific deal by ID.

**Response**: Returns deal object with user relationship loaded

#### PATCH `/crm/deals/{deal_id}`
Update a deal (partial update). **Note**: Updating the `stage` field will automatically set `manually_qualified=true`.

**Request**:
```json
{
  "stage": "in_conversation",
  "value": 3000.00,
  "probability": 60
}
```

**Response**: Returns updated deal object

#### PATCH `/crm/deals/{deal_id}/stage`
Update only the stage of a deal. This is a convenience endpoint for drag-and-drop operations.

**Request**:
```json
{
  "stage": "proposal_sent"
}
```

**Response**: Returns updated deal object with new stage

#### POST `/crm/deals/{deal_id}/won`
Mark a deal as won.

**Request** (optional):
```json
{
  "won_date": "2025-11-27T15:00:00"
}
```

**Response**: Returns updated deal with `stage="won"` and `probability=100`

#### POST `/crm/deals/{deal_id}/lost`
Mark a deal as lost.

**Request**:
```json
{
  "reason": "Budget constraints"
}
```

**Response**: Returns updated deal with `stage="lost"` and `probability=0`

#### DELETE `/crm/deals/{deal_id}`
Delete a deal.

**Response**:
```json
{
  "success": true,
  "message": "Deal deleted successfully"
}
```

### Notes

#### GET `/crm/users/{user_id}/notes`
Get all notes for a specific user.

**Response**:
```json
[
  {
    "id": 1,
    "user_id": 123,
    "deal_id": 5,
    "content": "Called customer, very interested in product",
    "note_type": "call",
    "created_by": "admin-uuid",
    "created_at": "2025-11-27T14:00:00"
  }
]
```

#### POST `/crm/users/{user_id}/notes`
Create a note for a user.

**Request**:
```json
{
  "content": "Follow-up scheduled for next week",
  "note_type": "note",
  "deal_id": 5
}
```

**Note types**: `note`, `call`, `email`, `meeting`, `task`

**Response**: Returns created note object

#### DELETE `/crm/notes/{note_id}`
Delete a note.

**Response**:
```json
{
  "success": true,
  "message": "Note deleted successfully"
}
```

### Tags

#### GET `/crm/tags`
Get all available tags.

**Response**:
```json
[
  {
    "id": 1,
    "name": "Hot Lead",
    "color": "#EF4444",
    "created_at": "2025-11-27T10:00:00"
  },
  {
    "id": 2,
    "name": "VIP",
    "color": "#8B5CF6",
    "created_at": "2025-11-27T10:00:00"
  }
]
```

#### POST `/crm/tags`
Create a new tag.

**Request**:
```json
{
  "name": "Enterprise",
  "color": "#3B82F6"
}
```

**Response**: Returns created tag object

#### GET `/crm/users/{user_id}/tags`
Get all tags assigned to a user.

**Response**: Returns array of tag objects

#### POST `/crm/users/{user_id}/tags/{tag_id}`
Assign a tag to a user.

**Response**: Returns created user-tag relationship

#### DELETE `/crm/users/{user_id}/tags/{tag_id}`
Remove a tag from a user.

**Response**:
```json
{
  "success": true,
  "message": "Tag removed from user"
}
```

### Stage Synchronization

The CRM includes automatic stage synchronization between the bot conversation (`User.stage`) and CRM deals (`Deal.stage`):

**Automatic Sync (Bot → CRM)**:
- When bot updates `User.stage`, the associated deal's stage updates automatically
- Only applies if `manually_qualified=false`
- Stage mapping:
  - `welcome` → `new_lead`
  - `qualifying` → `qualified`
  - `closing` → `in_conversation`
  - `sold` → `proposal_sent`

**Manual Override Protection**:
- When a deal's stage is updated via API (PUT `/crm/deals/{id}`), `manually_qualified` is set to `true`
- Once `manually_qualified=true`, the bot can no longer auto-update that deal's stage
- This prevents conflicts between manual CRM decisions and bot automation

---

---

## User Management Endpoints

### GET `/users/profile`
Get current authenticated user profile.

**Response**:
```json
{
  "id": 1,
  "auth_user_id": "uuid",
  "company_name": "Acme Corp",
  "phone": "+1234567890",
  "timezone": "UTC",
  "language": "en",
  "avatar_url": "https://...",
  "role": "owner",
  "onboarding_completed": true,
  "preferences": {
    "theme": "dark",
    "notifications": true
  }
}
```

### PUT `/users/profile`
Update user profile information.

**Request**:
```json
{
  "company_name": "New Name",
  "phone": "+9876543210",
  "timezone": "America/New_York",
  "language": "es"
}
```

### POST `/users/avatar`
Upload user avatar image.

**Request**: `multipart/form-data`
- Field name: `file`

### GET `/users/settings`
Get user settings and preferences.

**Response**:
```json
{
  "preferences": {
    "theme": "dark",
    "notifications": true
  },
  "timezone": "UTC",
  "language": "en"
}
```

### PUT `/users/settings`
Update user preferences.

**Request**:
```json
{
  "preferences": {
    "theme": "light",
    "notifications": false
  }
}
```

### PUT `/users/password`
Change user password. Requires current password for verification.

**Request**:
```json
{
  "current_password": "old_password123",
  "new_password": "new_secure_password456"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Password updated successfully"
}
```

### DELETE `/users/account`
Delete user account permanently.

**⚠️ WARNING**: This action is irreversible and deletes all user data.

**Response**:
```json
{
  "status": "success",
  "message": "Account deleted successfully"
}
```

### POST `/users/onboarding/complete`
Mark onboarding wizard as completed.

**Response**:
```json
{
  "status": "success",
  "message": "Onboarding completed"
}
```

### PUT `/users/onboarding/step`
Update current onboarding step.

**Query Parameters**:
- `step` (integer): Current step number

**Response**:
```json
{
  "status": "success",
  "current_step": 3
}
```

---

## Subscription Endpoints

### GET `/subscriptions/plans`
Get all available subscription plans.

**Response**:
```json
[
  {
    "id": 1,
    "name": "professional",
    "display_name": "Professional",
    "price": 49.0,
    "features": {
      "messages_per_month": 5000,
      "bots_limit": 3
    }
  }
]
```

### GET `/subscriptions/current`
Get current user's subscription details.

**Response**:
```json
{
  "id": 1,
  "status": "active",
  "plan": {
    "name": "professional",
    "display_name": "Professional"
  },
  "current_period_end": "2025-12-31T23:59:59",
  "cancel_at_period_end": false
}
```

### GET `/subscriptions/usage`
Get current usage metrics vs plan limits.

**Response**:
```json
{
  "messages_sent": 1500,
  "messages_limit": 5000,
  "bots_created": 2,
  "bots_limit": 3,
  "rag_storage_mb": 120.5,
  "rag_storage_limit_mb": 500
}
```

### GET `/subscriptions/billing-history`
Get payment history.

**Response**:
```json
[
  {
    "id": 1,
    "amount": 49.0,
    "status": "paid",
    "billing_date": "2025-11-01T10:00:00",
    "invoice_url": "https://stripe.com/..."
  }
]
```

### POST `/subscriptions/cancel`
Cancel subscription.

**Request**:
```json
{
  "cancel_at_period_end": true
}
```

---

## Webhook Endpoints

### POST `/webhook/twilio`
Receive incoming WhatsApp messages from Twilio.

**⚠️ NOTE**: This endpoint is called by Twilio, not by your frontend.

**Content-Type**: `application/x-www-form-urlencoded`

**Form Parameters** (sent by Twilio):
- `From` (string, required): User's phone number (format: `whatsapp:+1234567890`)
- `To` (string, required): Your WhatsApp Business number
- `Body` (string, required): Message text content
- `MessageSid` (string, required): Unique message identifier
- `ProfileName` (string, optional): WhatsApp profile name
- `NumMedia` (string, optional): Number of media files attached (default: "0")
- `MediaUrl0` (string, optional): URL to first media file
- `MediaContentType0` (string, optional): MIME type of first media file
- `Latitude` (string, optional): Location latitude if user shared location
- `Longitude` (string, optional): Location longitude if user shared location
- `Address` (string, optional): Location address if user shared location

**Process Flow**:
1. Extracts and cleans Twilio data
2. Creates or updates user with Twilio metadata (profile name, country code, etc.)
3. Processes message through LangGraph bot workflow
4. Returns TwiML response for Twilio to send back to user

**Response**: TwiML XML format
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Bot response message here</Message>
</Response>
```

**Error Response**: TwiML error message
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Lo siento, hubo un error procesando tu mensaje. Por favor intenta de nuevo.</Message>
</Response>
```

### GET `/webhook/twilio/status`
Check if Twilio webhook endpoint is active and configured correctly.

**Response**:
```json
{
  "status": "active",
  "endpoint": "/webhook/twilio",
  "method": "POST",
  "description": "Twilio WhatsApp webhook endpoint",
  "data_collected": [
    "phone_number",
    "whatsapp_profile_name",
    "country_code",
    "media_files",
    "location"
  ]
}
```

**Use Case**: Verify webhook configuration before connecting to Twilio.

---

## Meta Webhooks (Instagram + Messenger)

The Meta webhooks enable multi-channel messaging support for Instagram Direct Messages and Facebook Messenger. These endpoints handle webhook verification during Meta app setup and process incoming messages from both platforms.

**Multi-Tenant Isolation**: Messages are linked to tenants via `page_id` → `ChannelIntegration` lookup. Each tenant can connect their own Instagram/Messenger pages.

**Phase Status**: Phase 3 complete (webhook foundation). Phase 4 will add bot workflow integration for automated responses.

### GET `/webhook/instagram`

Verify Instagram webhook during Meta Developer Console setup.

**Purpose**: Meta calls this endpoint during webhook subscription to verify your server owns the URL.

**Authentication**: Query parameter verification token (not JWT)

**Query Parameters** (sent by Meta):
- `hub.mode` (string, required): Must be "subscribe"
- `hub.challenge` (string, required): Random string to echo back
- `hub.verify_token` (string, required): Must match `FACEBOOK_VERIFY_TOKEN` env var

**Response**: `200 OK`
```json
1234567890
```
Returns the `hub.challenge` value as an integer.

**Error Responses**:
- `400 Bad Request`: Invalid `hub.mode` (not "subscribe")
- `403 Forbidden`: Invalid verify token (doesn't match `FACEBOOK_VERIFY_TOKEN`)
- `500 Internal Server Error`: `FACEBOOK_VERIFY_TOKEN` not configured

**Environment Variables Required**:
- `FACEBOOK_VERIFY_TOKEN`: Custom token you create and configure in Meta Developer Console

**Setup Instructions**:
1. Set `FACEBOOK_VERIFY_TOKEN` in your environment (e.g., "my_secure_random_token_123")
2. In Meta Developer Console, add webhook with URL: `https://yourdomain.com/webhook/instagram`
3. Enter same verify token
4. Meta will call this GET endpoint to verify

---

### POST `/webhook/instagram`

Receive incoming Instagram Direct Messages.

**Purpose**: Meta calls this endpoint when users send messages to your Instagram business account.

**Authentication**: HMAC-SHA256 signature verification via `X-Hub-Signature-256` header

**Headers** (sent by Meta):
- `X-Hub-Signature-256` (string, required): HMAC signature in format `sha256=<hash>`
- `Content-Type`: `application/json`

**Request Body** (Meta webhook payload):
```json
{
  "object": "page",
  "entry": [{
    "id": "PAGE_ID",
    "time": 1234567890,
    "messaging": [{
      "sender": {"id": "USER_PSID"},
      "recipient": {"id": "PAGE_ID"},
      "timestamp": 1234567890,
      "message": {
        "mid": "MESSAGE_ID",
        "text": "Hello, I'm interested in your product!"
      }
    }]
  }]
}
```

**Process Flow**:
1. Verifies HMAC-SHA256 signature using `FACEBOOK_APP_SECRET`
2. Extracts sender PSID (Page-Scoped User ID) and message text
3. Looks up tenant via `page_id` in `ChannelIntegration` table
4. Gets or creates `User` record with `channel="instagram"`, `channel_user_id=PSID`
5. Saves message to `Message` table with `channel="instagram"`
6. Links user to tenant via `auth_user_id` from integration

**Response**: `200 OK`
```json
{
  "status": "ok"
}
```

**Error Responses**:
- `403 Forbidden`: Invalid signature (HMAC verification failed)

**Environment Variables Required**:
- `FACEBOOK_APP_SECRET`: Your Meta app secret (for signature verification)

**Notes**:
- Non-text messages (images, audio, etc.) are skipped in Phase 3
- If no `ChannelIntegration` found for `page_id`, message is logged but not processed
- Users are created with PSID as placeholder name (will be enriched later)
- Phase 4 will add bot workflow processing for automated responses

**Security**:
- All requests must have valid HMAC-SHA256 signature
- Signature computed using app secret and raw request body
- Uses constant-time comparison to prevent timing attacks

---

### GET `/webhook/messenger`

Verify Facebook Messenger webhook during Meta Developer Console setup.

**Purpose**: Identical to Instagram verification but for Messenger channel.

**Authentication**: Query parameter verification token (not JWT)

**Query Parameters** (sent by Meta):
- `hub.mode` (string, required): Must be "subscribe"
- `hub.challenge` (string, required): Random string to echo back
- `hub.verify_token` (string, required): Must match `FACEBOOK_VERIFY_TOKEN` env var

**Response**: `200 OK`
```json
1234567890
```
Returns the `hub.challenge` value as an integer.

**Error Responses**:
- `400 Bad Request`: Invalid `hub.mode` (not "subscribe")
- `403 Forbidden`: Invalid verify token (doesn't match `FACEBOOK_VERIFY_TOKEN`)
- `500 Internal Server Error`: `FACEBOOK_VERIFY_TOKEN` not configured

**Environment Variables Required**:
- `FACEBOOK_VERIFY_TOKEN`: Same token used for Instagram verification

**Setup Instructions**: Same as Instagram webhook setup, but use URL `https://yourdomain.com/webhook/messenger`

---

### POST `/webhook/messenger`

Receive incoming Facebook Messenger messages.

**Purpose**: Meta calls this endpoint when users send messages via Facebook Messenger.

**Authentication**: HMAC-SHA256 signature verification via `X-Hub-Signature-256` header

**Headers** (sent by Meta):
- `X-Hub-Signature-256` (string, required): HMAC signature in format `sha256=<hash>`
- `Content-Type`: `application/json`

**Request Body** (Meta webhook payload):
```json
{
  "object": "page",
  "entry": [{
    "id": "PAGE_ID",
    "time": 1234567890,
    "messaging": [{
      "sender": {"id": "USER_PSID"},
      "recipient": {"id": "PAGE_ID"},
      "timestamp": 1234567890,
      "message": {
        "mid": "MESSAGE_ID",
        "text": "Can you help me with an order?"
      }
    }]
  }]
}
```

**Process Flow**: Identical to Instagram POST webhook:
1. Verifies HMAC-SHA256 signature
2. Extracts sender PSID and message text
3. Looks up tenant via `page_id` in `ChannelIntegration` table
4. Gets or creates `User` with `channel="messenger"`
5. Saves message to database
6. Links to tenant via `auth_user_id`

**Response**: `200 OK`
```json
{
  "status": "ok"
}
```

**Error Responses**:
- `403 Forbidden`: Invalid signature (HMAC verification failed)

**Environment Variables Required**:
- `FACEBOOK_APP_SECRET`: Your Meta app secret (for signature verification)

**Notes**:
- Same behavior as Instagram webhook (user creation, message storage, multi-tenant isolation)
- Non-text messages skipped in Phase 3
- Phase 4 will integrate with bot workflow

---

### Meta Webhook Common Concepts

**PSID (Page-Scoped User ID)**:
- Unique identifier for a user in context of a specific page
- Different pages see different PSIDs for the same Facebook user
- Used as `channel_user_id` in the `User` table

**Multi-Tenant Isolation**:
- Each tenant connects their own Instagram/Messenger pages via `ChannelIntegration`
- Incoming messages are routed to correct tenant using `page_id` lookup
- Users are linked to tenants via `integration.auth_user_id`

**Signature Verification**:
- Meta sends `X-Hub-Signature-256: sha256=<hmac_hash>` header
- Server computes HMAC-SHA256 of raw request body using `FACEBOOK_APP_SECRET`
- Signatures are compared using constant-time comparison (`hmac.compare_digest`)

**Environment Variables Summary**:
```env
# Required for both Instagram and Messenger
FACEBOOK_VERIFY_TOKEN=your_custom_token_here
FACEBOOK_APP_SECRET=your_meta_app_secret
```

**Testing**:
- Unit tests: `apps/api/tests/integration/test_meta_webhooks.py`
- 20 comprehensive tests covering verification, signature validation, multi-tenant routing
- Known Issue: BUG-008 - Signature validation accepts signatures without `sha256=` prefix (security hardening needed)

---

## Error Responses

All endpoints may return error responses in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200` - Success
- `401` - Unauthorized (missing or invalid token)
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error
- `503` - Service Unavailable (e.g., RAG service not available)
