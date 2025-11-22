# 🤖 WhatsApp Sales Bot SaaS Platform

Plataforma SaaS multi-tenant de ventas conversacionales para WhatsApp con IA, construida con arquitectura de microservicios, LangGraph, FastAPI y Next.js.

## ✨ Características

### 🎯 Core Features
- **Conversaciones Inteligentes**: Workflow LangGraph con 11 nodos especializados
- **IA Multimodal**: Integración con GPT-4o y GPT-4o-mini
- **Text-to-Speech**: Voces configurables con OpenAI TTS (ratio 0-100%)
- **RAG (Retrieval Augmented Generation)**: ChromaDB para conocimiento empresarial
- **Recolección Inteligente de Datos**: Extracción y validación automática de información del cliente
- **Configuración Dinámica**: Panel completo de configuración en tiempo real
- **Persistencia**: Base de datos SQLite con historial completo por usuario

### 📊 Panel de Control Gradio
- **Chats en Vivo**: Monitoreo de conversaciones activas con datos recolectados
- **Configuración Avanzada**: System prompts, voces TTS, ratio audio/texto
- **Panel de Pruebas**: Simulación de conversaciones con datos en tiempo real
- **Gestión de Documentos**: Upload y gestión de base de conocimiento RAG

### 🔗 Integraciones
- **WhatsApp Business API** (Twilio)
- **HubSpot CRM** - Sincronización automática en tiempo real:
  - Campos estándar: name, email, phone, lifecyclestage
  - Campos personalizados: needs, pain_points, budget, intent_score, sentiment
  - Notas automáticas de conversación
  - Validación de datos antes de sincronizar
- **OpenAI** (GPT-4o, GPT-4o-mini, TTS)
- **ChromaDB** (Vector Store)

---

## 🚀 Quick Start

### 1. Requisitos Previos
- **Python 3.11+** (Backend & Bot-Engine)
- **Node.js 18+** (Frontend)
- **Cuenta OpenAI** con API key
- (Opcional) Cuenta Twilio para WhatsApp
- (Opcional) Cuenta HubSpot para CRM

### 2. Instalación

```bash
# Clonar repositorio
git clone https://github.com/lucasbneuman/whatsapp_sales_bot.git
cd whatsapp_sales_bot

# Instalar shared packages
cd packages/shared
pip install -e .
cd ../database
pip install -e .
cd ../..

# Instalar API dependencies
cd apps/api
pip install -r requirements.txt
cd ../..

# Instalar Bot-Engine dependencies
cd apps/bot-engine
pip install -r requirements.txt
cd ../..

# Instalar Frontend dependencies
cd apps/web
npm install
cd ../..
```

### 3. Configuración

Crear archivo `.env` en la raíz del proyecto:

```env
# OpenAI (REQUERIDO)
OPENAI_API_KEY=sk-...

# Base de Datos
DATABASE_URL=sqlite+aiosqlite:///./data/sales_bot.db

# JWT Authentication
JWT_SECRET=your-secret-key-change-in-production

# Twilio WhatsApp (Opcional)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# HubSpot CRM (Opcional)
HUBSPOT_ACCESS_TOKEN=pat-na1-...

# Logging
LOG_LEVEL=INFO
```

**⚠️ IMPORTANTE - Seguridad:**
- Cambia `JWT_SECRET` antes de deployar a producción
- Usa un secreto fuerte (mínimo 32 caracteres aleatorios)
- No subas el .env a Git

### 4. Ejecución

#### Opción 1: Script de Desarrollo Rápido ⭐ (Recomendado)

**Windows (PowerShell):**
```powershell
.\scripts\start_dev.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/start_dev.sh
./scripts/start_dev.sh
```

Esto iniciará automáticamente:
- **API Backend**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`
- **Frontend**: `http://localhost:3000`

#### Opción 2: Iniciar Servicios Manualmente

**Terminal 1 - Backend API:**
```bash
cd apps/api
python -m uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd apps/web
npm run dev
```

#### Opción 3: Docker Compose (Producción)

```bash
docker-compose up --build
```

### 5. Testing de Integración

```bash
# Ejecutar test de integración
python scripts/test_integration.py
```

Esto verificará:
- ✅ Shared packages funcionando
- ✅ Database operations
- ✅ Bot-engine workflow
- ✅ Message processing end-to-end

---

## 📖 Uso

### Configuración Inicial

1. **System Prompt**: Define la personalidad y objetivo del bot
2. **Información del Producto/Servicio**: Contexto automático para RAG
3. **Voces TTS**: Selecciona voz y ratio audio/texto (0-100%)
4. **Documentos**: Sube PDFs/TXT para conocimiento adicional

### Panel de Pruebas

Simula conversaciones completas y visualiza:
- Datos recolectados (nombre, email, teléfono, necesidades, presupuesto, pain points)
- Intent Score (0-1): Probabilidad de compra
- Sentiment: positive/neutral/negative
- Stage: welcome → qualifying → nurturing → closing → sold
- Notas LLM: Observaciones del asistente
- Historial de mensajes completo

### Integración HubSpot CRM

#### Setup Automático

Los campos personalizados se crean automáticamente en la primera sincronización:
- `intent_score` (Number)
- `sentiment` (Dropdown: positive/neutral/negative)
- `needs` (Textarea)
- `pain_points` (Textarea)
- `budget` (Text)

#### Sincronización en Tiempo Real

El bot sincroniza automáticamente:
1. Extrae datos del cliente (con validación estricta)
2. Valida formato de email, teléfono, etc.
3. Sincroniza a HubSpot (create o update automático)
4. Actualiza notas con resumen de conversación
5. Mapea lifecycle stages:
   - `welcome/qualifying` → lead
   - `nurturing` → marketingqualifiedlead
   - `closing` → salesqualifiedlead
   - `sold` → customer

#### Testing HubSpot

```bash
python test_hubspot.py
```

Ver `HUBSPOT_SETUP.md` para instrucciones detalladas.

---

## 🏗️ Arquitectura

### LangGraph Workflow (11 Nodos)

```
welcome_node
    ↓
intent_classifier_node (GPT-4o-mini: 0-1 score)
    ↓
sentiment_analyzer_node (GPT-4o-mini: positive/neutral/negative)
    ↓
data_collector_node (Extracción + Validación + HubSpot Sync)
    ↓
router_node (Conditional routing)
    ├── conversation_node (GPT-4o + RAG)
    ├── closing_node (High intent)
    ├── payment_node (Ready to buy)
    ├── follow_up_node (Leaving)
    └── handoff_node (Needs attention)
```

### Validación de Datos

**Nombre:**
- ❌ Rechaza saludos: "hola", "buenos días"
- ✅ Capitaliza: "lucas" → "Lucas"

**Email:**
- ✅ Formato válido: `usuario@dominio.com`
- ❌ Rechaza: `usuario@dominio` (sin TLD)

**Teléfono:**
- ✅ Números con formato: `+54 911 1234-5678`
- ✅ Mínimo 7 dígitos
- ❌ Rechaza texto no numérico

**Needs/Pain Points:**
- ✅ Mínimo 5 caracteres
- ✅ Descripciones concretas
- ❌ Rechaza frases vacías

**Budget:**
- ✅ Debe mencionar números o keywords monetarios
- ❌ Rechaza texto sin referencia a dinero

---

## 📁 Estructura del Proyecto (Microservicios)

```
whatsapp_sales_bot/
├── apps/
│   ├── api/                          # Backend API (FastAPI)
│   │   ├── src/
│   │   │   ├── main.py              # FastAPI application
│   │   │   ├── database.py          # DB session management
│   │   │   └── routers/
│   │   │       ├── auth.py          # Authentication endpoints
│   │   │       ├── conversations.py # Conversations management
│   │   │       └── bot.py           # Bot message processing
│   │   └── requirements.txt
│   │
│   ├── web/                          # Frontend (Next.js)
│   │   ├── src/
│   │   │   ├── app/                 # Next.js app router
│   │   │   ├── components/          # React components
│   │   │   └── lib/                 # API client & utilities
│   │   ├── package.json
│   │   └── next.config.js
│   │
│   └── bot-engine/                   # Bot Engine (LangGraph)
│       ├── src/
│       │   ├── graph/               # LangGraph workflow
│       │   │   ├── state.py         # Conversation state
│       │   │   ├── nodes.py         # 11 workflow nodes
│       │   │   └── workflow.py      # Graph compilation
│       │   ├── services/            # Bot services
│       │   │   ├── llm_service.py   # OpenAI GPT
│       │   │   ├── rag_service.py   # ChromaDB RAG
│       │   │   ├── tts_service.py   # Text-to-Speech
│       │   │   └── hubspot_sync.py  # HubSpot CRM
│       │   └── main.py
│       └── requirements.txt
│
├── packages/                         # Shared packages
│   ├── database/                    # Database models & CRUD
│   │   └── src/
│   │       └── whatsapp_bot_database/
│   │           ├── models.py        # SQLAlchemy models
│   │           └── crud.py          # Database operations
│   │
│   └── shared/                      # Shared utilities
│       └── src/
│           └── whatsapp_bot_shared/
│               ├── logging_config.py # Logging setup
│               └── helpers.py        # Common functions
│
├── scripts/
│   ├── test_integration.py          # Integration tests
│   ├── start_dev.sh                 # Dev startup (Linux/Mac)
│   └── start_dev.ps1                # Dev startup (Windows)
│
├── docker-compose.yml               # Docker orchestration
├── .env                             # Environment variables
└── README.md
```

### 🏗️ Arquitectura de Microservicios

**Frontend (Next.js)** ← HTTP → **API (FastAPI)** ← Import → **Bot-Engine (LangGraph)**
                                        ↓
                                  **Shared Packages**
                                  - Database Models
                                  - Utilities & Logging

---

## 🧪 Testing

### Test de Integración Completa

```bash
python scripts/test_integration.py
```

Verifica:
- ✅ Shared packages (logging, helpers)
- ✅ Database package (models, CRUD)
- ✅ Bot-engine workflow (LangGraph)
- ✅ Message processing end-to-end

### Test API Endpoints

```bash
# Inicia el API
cd apps/api
python -m uvicorn src.main:app --reload --port 8000

# En otra terminal, verifica endpoints
curl http://localhost:8000/health
curl http://localhost:8000/bot/health
```

Visita la documentación interactiva:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Test Frontend

```bash
cd apps/web
npm run dev
```

Abre `http://localhost:3000` y verifica:
- ✅ Login page
- ✅ Dashboard con conversaciones
- ✅ Chat interface
- ✅ Handoff controls

---

## 🔧 Configuración Avanzada

### Modelos OpenAI

- **Intent Classifier**: `gpt-4o-mini` (rápido, económico)
- **Sentiment Analyzer**: `gpt-4o-mini` (rápido, económico)
- **Data Extraction**: `gpt-4o-mini` (structured output)
- **Conversation**: `gpt-4o` (conversación principal)
- **Summary**: `gpt-4o` (resúmenes finales)

### Text-to-Speech

**Voces disponibles:**
- `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`

**Ratio Audio/Texto:**
- `0-49%`: Solo texto
- `50%`: 50% probabilidad de audio + texto
- `51-99%`: Probabilidad proporcional
- `100%`: Solo audio (sin texto)

### RAG (ChromaDB)

- **Chunk Size**: 1000 caracteres
- **Chunk Overlap**: 200 caracteres
- **Embeddings**: OpenAI `text-embedding-3-small`
- **Top K Results**: 3 documentos más relevantes

---

## 📝 Roadmap

- [ ] Multi-tenancy (múltiples empresas)
- [ ] Dashboard de analytics
- [ ] A/B testing de prompts
- [ ] Integración con más CRMs (Salesforce, Pipedrive)
- [ ] Soporte para más idiomas
- [ ] Voice input (Speech-to-Text)
- [ ] Integración con calendarios (scheduling)

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

- [LangGraph](https://github.com/langchain-ai/langgraph) - Workflow orchestration
- [OpenAI](https://openai.com/) - GPT-4o, GPT-4o-mini, TTS
- [Gradio](https://gradio.app/) - UI framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [HubSpot](https://www.hubspot.com/) - CRM integration

---

**Version**: 2.0.0 - Microservices Architecture
**Last Updated**: 2025-11-22
**Author**: Lucas Neuman

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---

## 🔄 Changelog

### v2.0.0 - Microservices Architecture (2025-11-22)
- ✨ Complete migration to microservices architecture
- 🏗️ Separated Frontend (Next.js), API (FastAPI), and Bot-Engine (LangGraph)
- 📦 Created shared packages for database and utilities
- 🐳 Added Docker Compose for production deployment
- 🚀 Added development startup scripts for Windows & Linux/Mac
- ✅ Added comprehensive integration tests
- 📚 Updated documentation for new architecture

### v1.1.0 - HubSpot CRM Integration (2025-11-21)
- 🔗 HubSpot CRM integration with auto-sync
- ✅ Data validation before sync
- 📊 Custom fields and lifecycle stages mapping
