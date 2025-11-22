# Gradio UI Features - Complete Documentation

This document lists all features from the Gradio UI (`app.py`, `live_chats_panel.py`, `config_panel_v2.py`) that need to be migrated to the Next.js frontend.

## Tab 1: 💬 Chats (Live Conversations)

### Conversation List
- **Auto-refresh**: Updates every 5 seconds automatically
- **Conversation items display**:
  - Mode indicator: 🟢 AUTO | 🔴 MANUAL | ⚠️ NEEDS_ATTENTION
  - Display name (user name or phone number)
  - Last message preview (truncated to 50 chars)
  - Timestamp of last message
  - Visual styling for unread messages (bold)
- **Manual refresh button**: 🔄 Actualizar
- **Conversation selection**: Click to view full conversation

### Chat Window
- **Message history display**: Shows all messages between user and bot
- **Message format**: User messages vs bot messages (different styling)
- **Scrollable chat area**: Height ~400px
- **Real-time updates**: When new messages arrive

### User Info Panel
- **User details**:
  - Name (or "Sin nombre")
  - Phone number
  - Email (or "No registrado")
  - Conversation mode: 🟢 Automatico | 🔴 Manual | ⚠️ Necesita Atencion
  - Total messages count
  - Last activity timestamp
- **Formatted display**: Card-style with background color

### Handoff Controls
- **Toggle mode button**: 🔄 Cambiar Modo (AUTO/MANUAL)
- **Mode status display**: Shows current mode and confirmation messages
- **Manual message input**: Text input for sending manual messages
- **Send button**: Enviar (primary variant)
- **Send status display**: Shows success/error messages after sending

### Functionality
- Load conversation history when selecting a user
- Send manual messages (only when in MANUAL mode)
- Toggle between AUTO and MANUAL modes
- Save messages to database
- Send messages via Twilio (if configured)

---

## Tab 2: ⚙️ Configuración (Configuration)

### Sub-tab 1: 🤖 Chatbot Configuration

#### Basic Settings
- **System Prompt**: Large textarea (4 lines)
  - Placeholder: "Eres un asistente de ventas profesional..."
  - Info: "Personalidad y comportamiento base del chatbot"
  
- **Welcome Message**: Textarea (2 lines)
  - Placeholder: "¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?"
  - Info: "Primer mensaje que verá el usuario al iniciar la conversación"
  
- **Payment Link**: Text input
  - Placeholder: "https://tu-sitio.com/pagar"
  - Info: "URL donde los clientes pueden realizar el pago"

#### Behavior Settings
- **Response Delay**: Number input (minutes)
  - Range: 0-10 minutes
  - Step: 0.1
  - Default: 0.5
  - Info: "Tiempo de espera antes de responder"

- **Max Words per Response**: Slider
  - Range: 5-500 words
  - Step: 5
  - Default: 100
  - Info: "Límite de palabras en cada mensaje"

- **Use Emojis**: Checkbox
  - Default: true
  - Info: "Incluir emojis en las respuestas"

- **Multi-part Messages**: Checkbox
  - Default: false
  - Info: "Dividir respuestas largas"

#### Audio/TTS Settings
- **Text/Audio Ratio**: Slider (%)
  - Range: 0-100%
  - Step: 10
  - Default: 0
  - Info: "0% = solo texto, 100% = solo audio"

- **TTS Voice**: Radio buttons
  - Options: alloy, echo, fable, onyx, nova, shimmer
  - Default: nova
  - Info: "Selecciona la voz para mensajes de audio"

- **Voice Preview**: Button + Audio player
  - Button: 🔊 Escuchar Voz
  - Generates sample audio with selected voice
  - Auto-plays preview

### Sub-tab 2: 📦 Producto/Servicio

- **Product Name**: Text input
  - Placeholder: "Ej: Curso de Marketing Digital"
  - Info: "¿Qué vendes?"

- **Description**: Textarea (4 lines)
  - Placeholder: "Curso completo de marketing digital con más de 50 horas de contenido..."
  - Info: "Descripción general de lo que ofreces"

- **Main Features**: Textarea (5 lines)
  - Placeholder: "- 50+ horas de video\n- Certificado al finalizar\n- Acceso de por vida\n- Soporte 24/7"
  - Info: "Lista las características clave (una por línea)"

- **Customer Benefits**: Textarea (5 lines)
  - Placeholder: "- Aprenderás a crear campañas efectivas\n- Aumentarás tus ventas online\n- Dominarás las redes sociales"
  - Info: "¿Qué gana el cliente? (una por línea)"

- **Price**: Text input
  - Placeholder: "Ej: $99 USD, Desde $50, Consultar"
  - Info: "Precio o rango de precio (opcional)"

- **Target Audience**: Text input
  - Placeholder: "Ej: Emprendedores, Pequeños negocios"
  - Info: "¿A quién está dirigido?"

### Sub-tab 3: 📚 Base de Conocimientos (RAG)

- **File Upload**: Multi-file upload
  - Supported formats: TXT, PDF, DOC, DOCX
  - Multiple files allowed
  - Upload button: 📤 Subir Archivos

- **RAG Stats Display**: Read-only textbox
  - Shows: "📊 Fragmentos en base de datos: {count}"
  - Updates after upload/clear

- **Upload Status**: Shows success/error messages
  - Format: "✅ {count} archivo(s) subido(s) correctamente ({chunks} fragmentos)"

- **Information Panel**: Markdown with:
  - What you can upload (catalogs, manuals, FAQs, etc.)
  - How it works (3 steps)

- **Clear Collection Button**: 🗑️ Limpiar Base de Conocimientos
  - Variant: "stop" (red/danger)
  - Confirmation message after clearing

### Save Configuration
- **Save Button**: 💾 Guardar Configuración
  - Variant: primary
  - Size: large
  - Saves all config values to database

- **Status Message**: Shows save result
  - Success: "✅ Configuración guardada exitosamente"
  - Error: "❌ Error: {message}"

---

## Tab 3: 🧪 Pruebas (Test Chat)

### Layout
- **Two-column layout**:
  - Left: Collected data panel (scale=1, narrower)
  - Right: Test chat (scale=2, wider)

### Collected Data Panel (Left)
Displays real-time data collected during the test conversation:

- **User ID**: 🆔 ID: {user_id}
  - Default: "USRPRUEBAS_00"
  - Auto-generated based on environment

- **Name**: 📝 Nombre: {name}
  - Default: "Aún no mencionó su nombre"
  - Detected from messages like "me llamo", "soy", "mi nombre es"

- **Email**: 📧 Email: {email}
  - Default: "No proporcionado"
  - Detected via regex pattern

- **Phone**: 📱 Teléfono: {phone}
  - Default: "+1234567890"
  - Editable input field
  - Can load history when changed

- **Last Contact**: 🕐 Último contacto: {timestamp}
  - Format: "DD/MM/YYYY HH:MM"
  - Default: "-"

- **Intent**: 🎯 Intención: {intent}
  - Values: Compra 🛒, Información ℹ️, Soporte 🆘, Saludo 👋, Conversación 💬
  - Auto-detected from keywords

- **Sentiment**: 😊 Sentimiento: {sentiment}
  - Values: Positivo 😊, Negativo 😞, Neutral 😐
  - Auto-detected from keywords

- **Stage**: 📊 Etapa: {stage}
  - Values: Bienvenida 👋, Calificación 🔍, Cierre 💰, Conversación 💬
  - Based on conversation progress

- **Needs**: 💡 Necesidades: {needs}
  - Detected from "necesito", "quiero", "busco", "me interesa"
  - 2 lines textarea

- **Requests Human**: 👨‍💼 Solicita Humano: {yes/no}
  - Detected from "humano", "persona", "supervisor", etc.
  - Values: Sí / No

- **Notes**: 📋 Notas: {notes}
  - Generated by LLM at key points (stage=Cierre, requests_human=Sí, or 10+ messages)
  - 3 lines textarea
  - Format: Intelligent summary of conversation

### Test Chat (Right)

- **Chat Display**: Chatbot component
  - Height: 500px
  - Type: "messages"
  - Shows conversation history

- **Message Input**: Text input
  - Placeholder: "Escribe tu mensaje..."
  - Scale: 4 (wider)

- **Send Button**: "Enviar"
  - Variant: primary
  - Scale: 1

- **Clear Chat Button**: "Limpiar Chat"
  - Size: small
  - Resets all data to defaults

### Functionality

- **Process messages**: Calls `process_chat_with_data()`
  - Saves to database
  - Updates all collected data fields
  - Detects name, email, phone, intent, sentiment, etc.
  - Generates notes with LLM at key points
  - Handles multi-part messages with [PAUSA] separator

- **Load history**: When phone number changes
  - Loads user from database
  - Loads all messages
  - Populates all data fields

- **Audio generation**: Based on text_audio_ratio
  - 0-49%: Text only
  - 50-99%: Probabilistic text + audio
  - 100%: Audio only (replaces text)

- **Real-time updates**: All data fields update after each message

---

## Global Features

### Styling
- **Theme**: Gradio Soft theme
- **Colors**: 
  - Primary: #25D366 (WhatsApp green)
  - Text: #666 (gray)
  - Background: #f5f5f5 (light gray)
  - Borders: #e0e0e0 (light gray)

### Header
- **Title**: "WhatsApp Sales Bot - Panel de Control"
- **Subtitle**: "Gestiona conversaciones, configura y prueba tu bot de ventas"
- **Styling**: Centered, with WhatsApp green color

### Footer
- **Text**: "WhatsApp Sales Bot | Powered by LangGraph + OpenAI + Gradio"
- **Styling**: Centered, gray color

### Database Integration
- **Async sessions**: All operations use AsyncSessionLocal
- **CRUD operations**: Via `database.crud` module
- **Models**: User, Message, Config

### Services Integration
- **LLM Service**: For generating responses and notes
- **TTS Service**: For generating audio messages
- **RAG Service**: For document upload and retrieval
- **Config Manager**: For loading/saving configuration
- **Twilio Service**: For sending WhatsApp messages

---

## Migration Priority

### High Priority (Core Features)
1. ✅ Tab 1: Chats - Live conversation management
2. ✅ Tab 2: Configuration - All settings
3. ✅ Tab 3: Test Chat - Testing interface

### Medium Priority (Enhanced UX)
4. Auto-refresh functionality
5. Real-time data updates
6. Voice preview
7. File upload with progress

### Low Priority (Nice to Have)
8. Audio message generation in test chat
9. Multi-part message handling
10. Advanced LLM note generation

---

## API Endpoints Needed

Based on the Gradio implementation, these endpoints are required:

### Configuration
- `GET /config` - Load all configuration
- `PUT /config` - Save all configuration
- `POST /config/rag/upload` - Upload RAG documents
- `DELETE /config/rag/clear` - Clear RAG collection
- `GET /config/rag/stats` - Get RAG statistics

### Conversations
- `GET /conversations` - List all active conversations
- `GET /conversations/{phone}/messages` - Get messages for a conversation
- `GET /conversations/{user_id}/info` - Get user info

### Handoff
- `POST /handoff/{phone}/take` - Take manual control
- `POST /handoff/{phone}/return` - Return to bot
- `POST /handoff/{phone}/send` - Send manual message

### Test Chat
- `POST /bot/process` - Process test message
- `GET /users/{phone}` - Get user by phone
- `POST /users/{phone}/clear` - Clear test conversation

### Audio
- `POST /tts/preview` - Generate voice preview
- `POST /tts/generate` - Generate audio for message
