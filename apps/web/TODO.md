# TODO: Missing API Endpoints

This document lists API endpoints that are referenced in the frontend but may not exist yet in the backend.

## Configuration Endpoints

- `GET /config` - Load all configuration settings
- `PUT /config` - Save all configuration settings
- `POST /config/rag/upload` - Upload RAG documents (multipart/form-data)
- `DELETE /config/rag/clear` - Clear all RAG documents
- `GET /config/rag/stats` - Get RAG collection statistics
- `POST /tts/preview` - Generate voice preview audio

## Conversation Endpoints

- `GET /conversations` - List all active conversations
  - Should return array of conversations with user data and last message
- `GET /conversations/{phone}/messages` - Get messages for a specific conversation
- `GET /users/{userId}` - Get user by ID
- `GET /users/phone/{phone}` - Get user by phone number

## Handoff Endpoints

- `POST /handoff/{phone}/take` - Take manual control of conversation
- `POST /handoff/{phone}/return` - Return conversation to bot
- `POST /handoff/{phone}/send` - Send manual message
  - Body: `{ "message": "text" }`

## Test Chat Endpoints

- `POST /bot/process` - Process test message and return response with collected data
  - Body: `{ "phone": "+123...", "message": "text", "history": [...] }`
  - Response: `{ "success": true, "data": { "response": "...", "collected_data": {...} } }`
- `DELETE /conversations/{phone}/clear` - Clear test conversation

## Notes

- All endpoints should follow the API response format: `{ "success": boolean, "data"?: any, "error"?: string }`
- Authentication via Bearer token in Authorization header
- CORS should be configured to allow requests from the frontend

## Priority

**High Priority:**
1. `/conversations` - Required for Chats tab to function
2. `/conversations/{phone}/messages` - Required for viewing chat history
3. `/config` (GET/PUT) - Required for Configuration tab
4. `/bot/process` - Required for Test tab

**Medium Priority:**
5. `/handoff/*` - Required for manual conversation control
6. `/config/rag/*` - Required for RAG document management
7. `/tts/preview` - Nice to have for voice preview

**Low Priority:**
8. Advanced features and optimizations
