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

### HubSpot Integration
- `/integrations/hubspot/sync` - Sync contact to HubSpot
- `/integrations/hubspot/status` - Check HubSpot connection status

### Twilio Integration
- `/integrations/twilio/send` - Send WhatsApp message via Twilio
- `/integrations/twilio/status` - Check Twilio connection status

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
