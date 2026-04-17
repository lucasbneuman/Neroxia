# WhatsApp Sales Bot API - Endpoints Documentation

Complete API reference for the WhatsApp Sales Bot backend.

**Base URL**: `http://localhost:8000`

**Authentication**: Most endpoints require JWT authentication via Bearer token.

---

## Authentication

### POST /auth/login

Login and obtain JWT access token.

**Request**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## Configuration Management

### GET /config

Get all configuration settings.

**Auth**: Required

**Request**:
```bash
curl -X GET http://localhost:8000/config \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
{
  "configs": {
    "system_prompt": "You are a helpful sales assistant...",
    "welcome_message": "Hello! How can I help you today?",
    "product_name": "Premium Software",
    "product_price": "$99/month",
    "use_emojis": true,
    "text_audio_ratio": 0,
    ...
  }
}
```

### PUT /config

Update configuration settings.

**Auth**: Required

**Request**:
```bash
curl -X PUT http://localhost:8000/config \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "configs": {
      "system_prompt": "New system prompt",
      "welcome_message": "Welcome!",
      "use_emojis": false
    }
  }'
```

**Response**:
```json
{
  "status": "success",
  "message": "Updated 3 settings",
  "configs": { ... }
}
```

### POST /config/reset

Reset configuration to defaults.

**Auth**: Required

**Request**:
```bash
curl -X POST http://localhost:8000/config/reset \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
{
  "status": "success",
  "message": "Configuration reset to defaults",
  "configs": { ... }
}
```

---

## RAG Document Management

### POST /rag/upload

Upload a document for RAG processing.

**Auth**: Required

**Supported Formats**: PDF, TXT, DOC, DOCX

**Request**:
```bash
curl -X POST http://localhost:8000/rag/upload \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@document.pdf"
```

**Response**:
```json
{
  "status": "success",
  "filename": "document.pdf",
  "chunks_created": 15,
  "message": "Document uploaded and processed successfully"
}
```

### GET /rag/files

List all uploaded RAG documents.

**Auth**: Required

**Request**:
```bash
curl -X GET http://localhost:8000/rag/files \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
[
  {
    "filename": "document.pdf",
    "size": 245678,
    "uploaded_at": "1700000000.0"
  },
  {
    "filename": "guide.txt",
    "size": 12345,
    "uploaded_at": "1700000100.0"
  }
]
```

### DELETE /rag/files/{filename}

Delete an uploaded RAG document.

**Auth**: Required

**Request**:
```bash
curl -X DELETE http://localhost:8000/rag/files/document.pdf \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
{
  "status": "success",
  "message": "File document.pdf deleted successfully"
}
```

### GET /rag/stats

Get RAG collection statistics.

**Auth**: Required

**Request**:
```bash
curl -X GET http://localhost:8000/rag/stats \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
{
  "enabled": true,
  "total_chunks": 45,
  "collection_name": "sales_documents"
}
```

### POST /rag/clear

Clear all documents from RAG collection.

**Auth**: Required

**Warning**: This removes all document chunks from the vector database.

**Request**:
```bash
curl -X POST http://localhost:8000/rag/clear \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
{
  "status": "success",
  "message": "RAG collection cleared successfully"
}
```

---

## Conversations

### GET /conversations

Get all active conversations.

**Auth**: Required

**Query Parameters**:
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100)

**Request**:
```bash
curl -X GET "http://localhost:8000/conversations?limit=50" \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
[
  {
    "phone": "+1234567890",
    "name": "John Doe",
    "lastMessage": "I'm interested in your product",
    "timestamp": "2025-11-22T14:30:00",
    "unread": 0,
    "isHandedOff": false,
    "stage": "qualification",
    "sentiment": "positive"
  }
]
```

### GET /conversations/pending

Get conversations that need attention (NEEDS_ATTENTION or MANUAL mode).

**Auth**: Required

**Request**:
```bash
curl -X GET http://localhost:8000/conversations/pending \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
[
  {
    "phone": "+1234567890",
    "name": "Jane Smith",
    "lastMessage": "I need to speak with a human",
    "timestamp": "2025-11-22T14:35:00",
    "mode": "NEEDS_ATTENTION",
    "stage": "qualification",
    "sentiment": "neutral"
  }
]
```

### GET /conversations/{phone}

Get detailed user information.

**Auth**: Required

**Request**:
```bash
curl -X GET http://localhost:8000/conversations/+1234567890 \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
{
  "id": 1,
  "phone": "+1234567890",
  "name": "John Doe",
  "email": "john@example.com",
  "stage": "qualification",
  "sentiment": "positive",
  "intent_score": 0.85,
  "conversation_mode": "AUTO",
  "conversation_summary": "Interested in premium plan, asked about pricing",
  "last_message_at": "2025-11-22T14:30:00",
  "created_at": "2025-11-20T10:00:00",
  "updated_at": "2025-11-22T14:30:00"
}
```

### GET /conversations/{phone}/messages

Get message history for a conversation.

**Auth**: Required

**Query Parameters**:
- `limit` (int, optional): Maximum messages to return (default: 50)

**Request**:
```bash
curl -X GET "http://localhost:8000/conversations/+1234567890/messages?limit=20" \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
[
  {
    "id": 1,
    "text": "Hello, I'm interested in your product",
    "sender": "customer",
    "timestamp": "2025-11-22T14:25:00",
    "metadata": {}
  },
  {
    "id": 2,
    "text": "Great! I'd be happy to help. What would you like to know?",
    "sender": "bot",
    "timestamp": "2025-11-22T14:25:05",
    "metadata": {"stage": "welcome"}
  }
]
```

### POST /conversations/{phone}/take-control

Take manual control of a conversation.

**Auth**: Required

**Request**:
```bash
curl -X POST http://localhost:8000/conversations/+1234567890/take-control \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
{
  "status": "success",
  "mode": "MANUAL"
}
```

### POST /conversations/{phone}/return-to-bot

Return conversation control to the bot.

**Auth**: Required

**Request**:
```bash
curl -X POST http://localhost:8000/conversations/+1234567890/return-to-bot \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
{
  "status": "success",
  "mode": "AUTO"
}
```

### POST /conversations/{phone}/send

Send a manual message to the user.

**Auth**: Required

**Request**:
```bash
curl -X POST http://localhost:8000/conversations/+1234567890/send \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how can I help you?"}'
```

**Response**:
```json
{
  "status": "success",
  "message_id": 123
}
```

---

## Bot Message Processing

### POST /bot/process

Process a message through the bot workflow.

**Auth**: Not required (used by WhatsApp webhook)

**Request**:
```bash
curl -X POST http://localhost:8000/bot/process \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "message": "I want to buy your product",
    "config": {}
  }'
```

**Response**:
```json
{
  "response": "Great! I'd love to help you with that. Let me get some details...",
  "user_phone": "+1234567890",
  "user_name": "John Doe",
  "intent_score": 0.92,
  "sentiment": "positive",
  "stage": "closing",
  "conversation_mode": "AUTO"
}
```

### GET /bot/health

Check bot engine availability.

**Auth**: Not required

**Request**:
```bash
curl -X GET http://localhost:8000/bot/health
```

**Response**:
```json
{
  "status": "healthy",
  "bot_engine": "available",
  "graph": "compiled"
}
```

---

## Follow-ups

### GET /followups

List all scheduled follow-ups.

**Auth**: Required

**Request**:
```bash
curl -X GET http://localhost:8000/followups \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
[
  {
    "id": "followup_+1234567890_1700000000",
    "next_run_time": "2025-11-23T10:00:00",
    "trigger": "date[2025-11-23 10:00:00]"
  }
]
```

### POST /followups/{phone}/schedule

Schedule a follow-up message.

**Auth**: Required

**Request**:
```bash
curl -X POST http://localhost:8000/followups/+1234567890/schedule \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Following up on our conversation...",
    "scheduled_time": "2025-11-23T10:00:00"
  }'
```

**Response**:
```json
{
  "status": "success",
  "job_id": "followup_+1234567890_1700000000",
  "phone": "+1234567890",
  "message": "Following up on our conversation...",
  "scheduled_time": "2025-11-23T10:00:00"
}
```

### GET /followups/{job_id}

Get information about a specific follow-up.

**Auth**: Required

**Request**:
```bash
curl -X GET http://localhost:8000/followups/followup_+1234567890_1700000000 \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
{
  "id": "followup_+1234567890_1700000000",
  "next_run_time": "2025-11-23T10:00:00",
  "trigger": "date[2025-11-23 10:00:00]"
}
```

### DELETE /followups/{job_id}

Cancel a scheduled follow-up.

**Auth**: Required

**Request**:
```bash
curl -X DELETE http://localhost:8000/followups/followup_+1234567890_1700000000 \
  -H "Authorization: Bearer <TOKEN>"
```

**Response**:
```json
{
  "status": "success",
  "message": "Follow-up followup_+1234567890_1700000000 cancelled successfully"
}
```

---

## Health & Status

### GET /

Root endpoint.

**Request**:
```bash
curl -X GET http://localhost:8000/
```

**Response**:
```json
{
  "message": "WhatsApp Sales Bot API is running"
}
```

### GET /health

Health check endpoint.

**Request**:
```bash
curl -X GET http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy"
}
```

---

## Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to test all endpoints directly from your browser.

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Notes

1. **Authentication**: Store the JWT token from `/auth/login` and include it in the `Authorization` header as `Bearer <TOKEN>` for all protected endpoints.

2. **Phone Number Format**: Phone numbers should include country code (e.g., `+1234567890`). The API will attempt to format them automatically.

3. **RAG Service**: RAG endpoints require ChromaDB to be installed. If not available, endpoints will return appropriate error messages.

4. **Follow-ups**: Scheduled follow-ups are persisted in the database and will survive server restarts.

5. **CORS**: The API is configured to accept requests from `http://localhost:3000` (Next.js frontend) and `http://localhost:8000` (self).
