# 🏗️ Architecture Documentation

> **Purpose**: Central documentation for coordinating multiple agents working on the WhatsApp Sales Bot SaaS platform.

**Last Updated**: 2025-11-22  
**Architecture Version**: 2.0.0 - Microservices  
**Branch**: saas-migration

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Technical Stack](#technical-stack)
3. [Architecture Decisions](#architecture-decisions)
4. [Project Structure](#project-structure)
5. [Component Details](#component-details)
6. [Communication Patterns](#communication-patterns)
7. [What NOT to Change](#what-not-to-change)
8. [Code Conventions](#code-conventions)
9. [Development Workflow](#development-workflow)

---

## 📊 Project Overview

### What is this project?

A **multi-tenant SaaS platform** for conversational sales via WhatsApp, powered by AI. The system uses:
- **LangGraph** workflow with 11 specialized nodes for intelligent conversation management
- **FastAPI** backend for REST API endpoints
- **Next.js** frontend for modern web interface
- **Supabase** for PostgreSQL database and authentication
- **OpenAI GPT-4o/GPT-4o-mini** for AI conversations
- **ChromaDB** for RAG (Retrieval Augmented Generation)
- **HubSpot CRM** integration for automatic contact synchronization

### Key Features

- ✅ Intelligent conversation routing based on intent and sentiment
- ✅ Automatic data extraction and validation
- ✅ Text-to-Speech with configurable voice and audio/text ratio
- ✅ RAG-powered knowledge base from uploaded documents
- ✅ Real-time HubSpot CRM synchronization
- ✅ Multi-stage conversation flow (welcome → qualifying → nurturing → closing → sold)
- ✅ Human handoff capability for complex cases

---

## 🛠️ Technical Stack

### Backend & Bot Engine

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Primary language for backend and bot |
| **FastAPI** | 0.115.0 | REST API framework |
| **LangGraph** | 0.2.59 | Workflow orchestration (11 nodes) |
| **LangChain** | 0.3.13 | LLM framework |
| **Supabase** | Latest | PostgreSQL database + Auth |
| **SQLAlchemy** | 2.0.36 | ORM for database operations |
| **ChromaDB** | 0.5.23 | Vector database for RAG |
| **OpenAI** | Latest | GPT-4o, GPT-4o-mini, TTS |
| **Twilio** | 9.4.0 | WhatsApp Business API |
| **HubSpot** | 9.4.0 | CRM integration |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 14.x | React framework with App Router |
| **React** | 18.x | UI library |
| **TypeScript** | 5.x | Type safety |
| **Tailwind CSS** | 3.x | Styling framework |
| **Zustand** | Latest | State management |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Local development orchestration |
| **Render.com** | Production deployment |
| **PostgreSQL** | Production database (via Supabase) |
| **SQLite** | Legacy local development |

---

## 🎯 Architecture Decisions

### 1. **Microservices Architecture** ✅

**Decision**: Split monolithic Gradio app into 3 microservices  
**Rationale**: 
- Better separation of concerns
- Independent scaling
- Easier testing and deployment
- Team can work on different services simultaneously

**Services**:
1. **apps/web** - Next.js frontend
2. **apps/api** - FastAPI backend
3. **apps/bot-engine** - LangGraph workflow engine

### 2. **Supabase for Database + Auth** ✅

**Decision**: Migrate from SQLite to PostgreSQL via Supabase  
**Rationale**:
- Production-ready database
- Built-in authentication (replaces custom JWT)
- Real-time capabilities
- Hosted solution (no database management)
- Free tier for development

**Migration Status**: ✅ Completed
- Database schema migrated to PostgreSQL
- Supabase Auth integrated
- Environment variables updated

### 3. **Shared Packages** ✅

**Decision**: Create `packages/database` and `packages/shared` as local packages  
**Rationale**:
- Avoid code duplication
- Single source of truth for models
- Consistent database operations across services
- Shared utilities and logging

**Installation**:
```bash
pip install -e packages/database
pip install -e packages/shared
```

### 4. **LangGraph Workflow (11 Nodes)** ⚠️ DO NOT CHANGE

**Decision**: Keep existing LangGraph workflow intact  
**Rationale**: 
- Already working and tested
- Complex business logic embedded
- Critical for conversation quality

**Nodes**:
1. `welcome_node` - Initial greeting
2. `intent_classifier_node` - GPT-4o-mini for intent scoring (0-1)
3. `sentiment_analyzer_node` - GPT-4o-mini for sentiment (positive/neutral/negative)
4. `data_collector_node` - Extract and validate customer data
5. `router_node` - Conditional routing based on intent/sentiment
6. `conversation_node` - Main GPT-4o conversation with RAG
7. `closing_node` - High intent closing attempts
8. `payment_node` - Payment processing
9. `follow_up_node` - Schedule follow-ups
10. `handoff_node` - Human agent handoff
11. `summary_node` - Conversation summary generation

### 5. **FastAPI for REST API** ✅

**Decision**: Use FastAPI instead of Flask/Django  
**Rationale**:
- Async/await support (better performance)
- Automatic OpenAPI documentation
- Type hints and Pydantic validation
- Modern Python framework

**Routers**:
- `/auth` - Authentication (Supabase)
- `/users` - User profile management
- `/subscriptions` - Subscription & billing management
- `/conversations` - Conversation management
- `/bot` - Bot message processing
- `/config` - Configuration management
- `/rag` - RAG document management
- `/followups` - Follow-up scheduling

### 6. **Next.js App Router** ✅

**Decision**: Use Next.js 14 with App Router (not Pages Router)  
**Rationale**:
- Modern React patterns
- Server components for better performance
- Built-in API routes
- File-based routing

**Pages**:
- `/login` - Authentication
- `/dashboard` - Main dashboard
- `/chats` - Live chat interface
- `/config` - Configuration panel
- `/test` - Testing interface

### 7. **ChromaDB for RAG** ⚠️ DO NOT CHANGE

**Decision**: Keep ChromaDB for vector storage  
**Rationale**:
- Already integrated and working
- Lightweight and fast
- No need for external vector DB
- Persistent storage in `chroma_db/` directory

**Configuration**:
- Chunk size: 1000 characters
- Chunk overlap: 200 characters
- Embeddings: OpenAI `text-embedding-3-small`
- Top K: 3 documents

### 8. **Data Validation** ⚠️ DO NOT CHANGE

**Decision**: Strict validation before HubSpot sync  
**Rationale**:
- Prevent bad data in CRM
- Improve data quality
- Better user experience

**Validation Rules**:
- **Name**: No greetings, capitalized
- **Email**: Valid format with TLD
- **Phone**: Min 7 digits, formatted
- **Needs/Pain Points**: Min 5 characters
- **Budget**: Must mention money/numbers

---

## 📁 Project Structure

```
whatsapp_sales_bot/
├── apps/                           # Microservices
│   ├── api/                        # FastAPI Backend
│   │   ├── src/
│   │   │   ├── main.py            # FastAPI app entry point
│   │   │   ├── database.py        # DB session management
│   │   │   ├── core/              # Core utilities
│   │   │   │   └── supabase.py    # Supabase client
│   │   │   └── routers/           # API endpoints
│   │   │       ├── auth.py        # Authentication
│   │   │       ├── conversations.py
│   │   │       ├── bot.py         # Bot message processing
│   │   │       ├── config.py      # Configuration
│   │   │       ├── rag.py         # RAG documents
│   │   │       └── followups.py   # Follow-up scheduling
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── web/                        # Next.js Frontend
│   │   ├── src/
│   │   │   ├── app/               # App Router pages
│   │   │   │   ├── login/
│   │   │   │   ├── dashboard/
│   │   │   │   ├── chats/
│   │   │   │   ├── config/
│   │   │   │   └── test/
│   │   │   ├── components/        # React components
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   ├── ConversationList.tsx
│   │   │   │   ├── ConfigPanel.tsx
│   │   │   │   └── ...
│   │   │   ├── lib/               # Utilities
│   │   │   │   ├── api.ts         # API client
│   │   │   │   └── supabase.ts    # Supabase client
│   │   │   ├── stores/            # Zustand stores
│   │   │   └── types/             # TypeScript types
│   │   ├── package.json
│   │   ├── next.config.js
│   │   └── Dockerfile
│   │
│   └── bot-engine/                 # LangGraph Bot Engine
│       ├── src/
│       │   ├── graph/             # LangGraph workflow
│       │   │   ├── state.py       # Conversation state
│       │   │   ├── nodes.py       # 11 workflow nodes
│       │   │   └── workflow.py    # Graph compilation
│       │   ├── services/          # External services
│       │   │   ├── llm_service.py # OpenAI GPT
│       │   │   ├── rag_service.py # ChromaDB RAG
│       │   │   ├── tts_service.py # Text-to-Speech
│       │   │   ├── hubspot_sync.py # HubSpot CRM
│       │   │   ├── twilio_service.py # Twilio WhatsApp
│       │   │   ├── scheduler_service.py # Follow-ups
│       │   │   └── config_manager.py # Configuration
│       │   └── main.py
│       ├── requirements.txt
│       └── Dockerfile
│
├── packages/                       # Shared Packages
│   ├── database/                  # Database models & CRUD
│   │   ├── src/
│   │   │   └── whatsapp_bot_database/
│   │   │       ├── __init__.py
│   │   │       ├── models.py      # SQLAlchemy models
│   │   │       └── crud.py        # Database operations
│   │   └── setup.py
│   │
│   └── shared/                    # Shared utilities
│       ├── src/
│       │   └── whatsapp_bot_shared/
│       │       ├── __init__.py
│       │       ├── logging_config.py
│       │       └── helpers.py
│       └── setup.py
│
├── scripts/                        # Utility scripts
│   ├── start_dev.sh               # Dev startup (Linux/Mac)
│   ├── start_dev.ps1              # Dev startup (Windows)
│   ├── test_integration.py        # Integration tests
│   ├── reset_config.py            # Reset configuration
│   └── test_hubspot.py            # HubSpot testing
│
├── legacy/                         # Legacy Gradio UI (backup)
│   └── gradio/
│
├── infrastructure/                 # Infrastructure configs
│   └── docker/
│
├── chroma_db/                      # ChromaDB vector store ⚠️ DO NOT MOVE
├── data/                           # Data files
│   └── sales_bot.db               # SQLite (legacy) ⚠️ DO NOT MOVE
│
├── .env                            # Environment variables
├── .env.example                    # Environment template
├── docker-compose.yml              # Docker orchestration
├── render.yaml                     # Render.com deployment
├── README.md                       # Main documentation
├── MIGRATION_PLAN.md               # Migration guide
├── ARCHITECTURE.md                 # This file
└── WORK_LOG.md                     # Work coordination log
```

---

## 🔧 Component Details

### 1. **apps/api** - FastAPI Backend

**Purpose**: REST API for frontend and webhook handling

**Key Files**:
- `src/main.py` - FastAPI application, CORS, routers
- `src/database.py` - Database session management
- `src/core/supabase.py` - Supabase client initialization

**Routers**:
| Router | Endpoints | Purpose |
|--------|-----------|---------|
| `auth.py` | `/auth/login`, `/auth/signup`, `/auth/logout`, `/auth/refresh`, `/auth/me` | Supabase authentication |
| `conversations.py` | `/conversations/`, `/conversations/{phone}`, `/conversations/{phone}/messages`, `/conversations/{phone}/clear` | Conversation and message management |
| `bot.py` | `/bot/process`, `/bot/health` | Bot message processing |
| `config.py` | `/config/`, `/config/reset` | Configuration management |
| `rag.py` | `/rag/upload`, `/rag/files`, `/rag/files/{filename}`, `/rag/stats`, `/rag/clear` | RAG document management |
| `followups.py` | `/followups/`, `/followups/{id}`, `/followups/pending` | Follow-up scheduling |
| `handoff.py` | `/handoff/{phone}/take`, `/handoff/{phone}/return`, `/handoff/{phone}/send` | Human handoff controls |
| `integrations.py` | `/integrations/hubspot/*`, `/integrations/twilio/*` | External integrations |

**API Response Format**:
All endpoints return JSON with consistent structure:
```json
{
  "status": "success" | "error",
  "message": "Human readable message",
  "data": { ... },  // Optional, endpoint-specific data
  "configs": { ... } // For config endpoints
}
```

**Authentication**:
- All endpoints (except `/auth/login` and `/auth/signup`) require authentication
- Use `Authorization: Bearer {token}` header
- Token obtained from `/auth/login` endpoint

**Dependencies**:
- `packages/database` - For models and CRUD
- `packages/shared` - For logging and helpers
- `apps/bot-engine` - Imported for bot workflow

**Environment Variables**:
```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_KEY=xxx
SUPABASE_DATABASE_URL=postgresql+asyncpg://...
OPENAI_API_KEY=sk-...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=...
HUBSPOT_ACCESS_TOKEN=...
```

### 2. **apps/web** - Next.js Frontend

**Purpose**: Modern web interface for managing conversations

**Key Features**:
- Minimalist black and white design
- Real-time conversation updates
- Configuration panel
- Test interface for simulating conversations
- Human handoff controls

**Pages**:
| Route | Component | Purpose |
|-------|-----------|---------|
| `/login` | Login page | Supabase authentication |
| `/dashboard` | Dashboard | Overview and stats |
| `/chats` | Chat interface | Live conversation management |
| `/config` | Configuration | System prompts, TTS, RAG |
| `/test` | Test interface | Simulate conversations |

**State Management**:
- Zustand for global state
- React hooks for local state

**API Communication**:
- `lib/api.ts` - Axios client with interceptors
- `lib/supabase.ts` - Supabase client for auth

**Environment Variables**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
```

### 3. **apps/bot-engine** - LangGraph Workflow

**Purpose**: AI conversation engine with 11-node workflow

**Workflow Flow**:
```
User Message
    ↓
welcome_node (if first message)
    ↓
intent_classifier_node (GPT-4o-mini → intent_score: 0-1)
    ↓
sentiment_analyzer_node (GPT-4o-mini → sentiment: positive/neutral/negative)
    ↓
data_collector_node (Extract + Validate + HubSpot Sync)
    ↓
router_node (Conditional routing)
    ├── conversation_node (GPT-4o + RAG)
    ├── closing_node (intent_score > 0.7)
    ├── payment_node (ready to buy)
    ├── follow_up_node (leaving conversation)
    └── handoff_node (needs human)
```

**Services**:
| Service | Purpose | Model/Tech |
|---------|---------|------------|
| `llm_service.py` | LLM calls | GPT-4o, GPT-4o-mini |
| `rag_service.py` | Vector search | ChromaDB + OpenAI embeddings |
| `tts_service.py` | Audio generation | OpenAI TTS |
| `hubspot_sync.py` | CRM sync | HubSpot API |
| `twilio_service.py` | WhatsApp messaging | Twilio API |
| `scheduler_service.py` | Follow-up scheduling | APScheduler |
| `config_manager.py` | Configuration | Database |

**Key Models**:
- **Intent Classifier**: `gpt-4o-mini` (fast, cheap)
- **Sentiment Analyzer**: `gpt-4o-mini` (fast, cheap)
- **Data Extraction**: `gpt-4o-mini` (structured output)
- **Main Conversation**: `gpt-4o` (high quality)
- **Summary**: `gpt-4o` (high quality)

### 4. **packages/database** - Shared Database Package

**Purpose**: SQLAlchemy models and CRUD operations

**Models** (`models.py`):
```python
class User(Base):
    id: int
    auth_user_id: UUID  # Link to Supabase Auth
    phone: str
    ...

class UserProfile(Base):
    id: int
    auth_user_id: UUID
    company_name: str
    role: str
    preferences: JSON
    ...

class SubscriptionPlan(Base):
    id: int
    name: str
    price: float
    features: JSON
    ...

class UserSubscription(Base):
    id: int
    user_id: UUID
    plan_id: int
    status: str
    current_period_end: datetime
    ...

class Conversation(Base):
    id: UUID
    user_id: UUID
    phone_number: str
    stage: str  # welcome, qualifying, nurturing, closing, sold
    intent_score: float  # 0-1
    sentiment: str  # positive, neutral, negative
    customer_data: JSON  # name, email, needs, budget, etc.
    created_at: datetime
    updated_at: datetime

class Message(Base):
    id: UUID
    conversation_id: UUID
    role: str  # user, assistant, system
    content: str
    audio_url: str | None
    created_at: datetime

class Configuration(Base):
    id: UUID
    user_id: UUID
    system_prompt: str
    product_info: str
    tts_voice: str
    tts_ratio: int  # 0-100
    created_at: datetime
    updated_at: datetime

class RAGDocument(Base):
    id: UUID
    user_id: UUID
    filename: str
    content: str
    created_at: datetime
```

**CRUD Operations** (`crud.py`):
- `get_conversation()`, `create_conversation()`, `update_conversation()`
- `get_messages()`, `create_message()`
- `get_config()`, `update_config()`
- `get_rag_documents()`, `create_rag_document()`, `delete_rag_document()`

**Installation**:
```bash
pip install -e packages/database
```

**Import**:
```python
from whatsapp_bot_database.models import Conversation, Message
from whatsapp_bot_database.crud import get_conversation, create_message
```

### 5. **packages/shared** - Shared Utilities Package

**Purpose**: Common utilities and logging configuration

**Modules**:
- `logging_config.py` - Centralized logging setup
- `helpers.py` - Common functions (phone formatting, validation, etc.)

**Installation**:
```bash
pip install -e packages/shared
```

**Import**:
```python
from whatsapp_bot_shared.logging_config import setup_logging
from whatsapp_bot_shared.helpers import format_phone_number, validate_email
```

---

## 🔄 Communication Patterns

### Frontend → API

**Protocol**: HTTP REST  
**Format**: JSON  
**Authentication**: Supabase JWT token in `Authorization` header

**Example**:
```typescript
// Frontend (TypeScript)
const response = await fetch('http://localhost:8000/conversations', {
  headers: {
    'Authorization': `Bearer ${supabaseToken}`,
    'Content-Type': 'application/json'
  }
});
```

### API → Bot Engine

**Protocol**: Direct Python import  
**Pattern**: API imports bot-engine as a package

**Example**:
```python
# apps/api/src/routers/bot.py
from apps.bot_engine.src.graph.workflow import process_message

@router.post("/bot/message")
async def handle_message(message: MessageInput):
    result = await process_message(message.content, message.conversation_id)
    return result
```

### Bot Engine → External Services

**Services**:
- **OpenAI**: HTTP REST API (via `openai` SDK)
- **ChromaDB**: Local file-based storage
- **HubSpot**: HTTP REST API (via `hubspot-api-client`)
- **Twilio**: HTTP REST API (via `twilio` SDK)

### Database Access

**All services** access database via `packages/database`:
```python
from whatsapp_bot_database.models import Conversation
from whatsapp_bot_database.crud import get_conversation

# In any service
conversation = await get_conversation(db, conversation_id)
```

---

## ⚠️ What NOT to Change

### 1. **LangGraph Workflow Structure**

**DO NOT**:
- Change the 11-node workflow structure
- Modify node execution order
- Remove or rename nodes
- Change state schema

**Reason**: Complex business logic, already tested and working

### 2. **ChromaDB Storage Location**

**DO NOT**:
- Move `chroma_db/` directory
- Change ChromaDB collection names
- Modify embedding model

**Reason**: Existing vector data will be lost

### 3. **Database Models**

**DO NOT**:
- Remove existing fields from models
- Change field types without migration
- Rename tables

**Reason**: Breaking changes for existing data

**OK TO DO**:
- Add new fields (with defaults)
- Add new models
- Create database migrations

### 4. **Data Validation Rules**

**DO NOT**:
- Relax validation rules (e.g., allow invalid emails)
- Remove validation steps

**Reason**: Data quality is critical for CRM sync

**OK TO DO**:
- Add new validation rules
- Improve validation logic

### 5. **Environment Variable Names**

**DO NOT**:
- Rename existing environment variables
- Remove required variables

**Reason**: Breaking changes for deployment

**OK TO DO**:
- Add new optional variables
- Add defaults for optional variables

### 6. **Shared Package Names**

**DO NOT**:
- Rename `whatsapp_bot_database` or `whatsapp_bot_shared`
- Change package structure

**Reason**: All imports will break

---

## 📝 Code Conventions

### Python (Backend & Bot Engine)

**Style Guide**: PEP 8

**Naming**:
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore()`

**Type Hints**: Required for all functions
```python
def get_conversation(db: AsyncSession, conversation_id: str) -> Conversation | None:
    ...
```

**Async/Await**: Use for all I/O operations
```python
async def create_message(db: AsyncSession, message: MessageCreate) -> Message:
    ...
```

**Imports**:
```python
# Standard library
import os
from datetime import datetime

# Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Local
from whatsapp_bot_database.models import Conversation
from whatsapp_bot_shared.logging_config import setup_logging
```

**Logging**:
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Processing message")
logger.error("Failed to process", exc_info=True)
```

### TypeScript (Frontend)

**Style Guide**: Airbnb TypeScript

**Naming**:
- **Files**: `PascalCase.tsx` (components), `camelCase.ts` (utilities)
- **Components**: `PascalCase`
- **Functions**: `camelCase()`
- **Constants**: `UPPER_SNAKE_CASE`
- **Interfaces**: `PascalCase` (no `I` prefix)

**Type Safety**: Always use TypeScript, no `any`
```typescript
interface Conversation {
  id: string;
  phone_number: string;
  stage: string;
  intent_score: number;
}

const getConversation = async (id: string): Promise<Conversation> => {
  ...
};
```

**React Components**:
```typescript
// Functional components with TypeScript
interface ChatInterfaceProps {
  conversationId: string;
  onSendMessage: (message: string) => void;
}

export default function ChatInterface({ conversationId, onSendMessage }: ChatInterfaceProps) {
  ...
}
```

**API Calls**:
```typescript
// Use lib/api.ts for all API calls
import { api } from '@/lib/api';

const conversations = await api.get<Conversation[]>('/conversations');
```

### Database Migrations

**Tool**: Alembic (for SQLAlchemy)

**Process**:
1. Modify models in `packages/database/src/whatsapp_bot_database/models.py`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Review migration file
4. Apply migration: `alembic upgrade head`

### Git Workflow

**Branch Strategy**:
- `main` - Production-ready code
- `saas-migration` - Current migration work
- `feature/*` - New features
- `fix/*` - Bug fixes

**Commit Messages**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```
feat(api): add RAG document upload endpoint
fix(bot): correct intent score calculation
docs(architecture): update communication patterns
```

---

## 🚀 Development Workflow

### Setup

1. **Clone repository**:
   ```bash
   git clone https://github.com/lucasbneuman/whatsapp_sales_bot.git
   cd whatsapp_sales_bot
   ```

2. **Install shared packages**:
   ```bash
   pip install -e packages/shared
   pip install -e packages/database
   ```

3. **Install service dependencies**:
   ```bash
   # API
   cd apps/api && pip install -r requirements.txt && cd ../..
   
   # Bot Engine
   cd apps/bot-engine && pip install -r requirements.txt && cd ../..
   
   # Frontend
   cd apps/web && npm install && cd ../..
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run services**:
   ```bash
   # Option 1: Use startup script
   ./scripts/start_dev.sh  # Linux/Mac
   .\scripts\start_dev.ps1  # Windows
   
   # Option 2: Manual
   # Terminal 1: API
   cd apps/api && python -m uvicorn src.main:app --reload --port 8000
   
   # Terminal 2: Frontend
   cd apps/web && npm run dev
   ```

### Testing

**Integration Tests**:
```bash
python scripts/test_integration.py
```

**API Tests**:
```bash
cd apps/api
pytest tests/
```

**Frontend Tests**:
```bash
cd apps/web
npm test
```

### Deployment

**Render.com** (Production):
1. Push to `main` branch
2. Render auto-deploys from `render.yaml`
3. Set environment variables in Render dashboard

**Docker Compose** (Local/Staging):
```bash
docker-compose up --build
```

---

## 📚 Additional Resources

- **README.md** - Quick start guide
- **MIGRATION_PLAN.md** - Detailed migration steps
- **WORK_LOG.md** - Agent coordination log
- **HUBSPOT_SETUP.md** - HubSpot integration guide
- **API Docs** - http://localhost:8000/docs (when running)

---

## 🤝 Agent Coordination

**BEFORE STARTING ANY WORK**:

1. ✅ Read this ARCHITECTURE.md to understand decisions
2. ✅ Read WORK_LOG.md to see what others are doing
3. ✅ Update WORK_LOG.md with your task
4. ✅ When done, update WORK_LOG.md with completion status

**Questions?** Check this document first, then ask in WORK_LOG.md

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-11-22  
**Maintained By**: Documentation Agent
