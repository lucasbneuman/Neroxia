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
