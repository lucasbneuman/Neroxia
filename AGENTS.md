# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## 🚨 CRITICAL: Agent Protocol System

**ALL agents** in `.Codex/agents/` MUST follow the mandatory protocol defined in `.Codex/AGENT_PROTOCOL.md`.

### Key Protocol Rules (for all agents):

1. **Before starting ANY task**: Read `AGENT_PROTOCOL.md`, `TASK.md`, and `BUG_TRACKER.md`
2. **Workspace cleanliness**: Delete all temporary/diagnostic scripts after use
3. **Script organization**: One-time-use scripts → `.Codex/scripts/` (then delete after completion)
4. **Task logging**: Update `.Codex/TASK.md` after EVERY task (3 lines max)
5. **Bug tracking**: Update `.Codex/BUG_TRACKER.md` when bugs are found/fixed
6. **Commits**: Create commit after EVERY completed subtask
7. **Documentation**: Update `ARCHITECTURE.md`, `API_DOCUMENTATION.md`, or `AGENTS.md` when modifying architecture/APIs
8. **Response length**: Be concise (<100 words unless details explicitly requested)

**Non-compliance will result in agent prompt rewriting.**

See `.Codex/AGENT_PROTOCOL.md` for complete rules and compliance checklist.

---

## Project Overview

WhatsApp Sales Bot is a multi-tenant SaaS platform for conversational sales via WhatsApp, built with a microservices architecture. The system uses LangGraph for AI conversation orchestration, FastAPI for the backend API, and Next.js for the frontend dashboard.

## Architecture

### Microservices Structure

```
apps/
├── api/           # FastAPI backend - REST API, authentication, webhooks
├── bot-engine/    # LangGraph workflow - AI conversation engine
└── web/           # Next.js frontend - React dashboard

packages/
├── database/      # Shared SQLAlchemy models and CRUD operations
└── shared/        # Shared utilities (logging, helpers)
```

**Key Principle**: The API imports and uses bot-engine as a library. Both depend on shared packages (database, shared).

### Database

- **Development**: SQLite (file-based at `apps/api/sales_bot.db`)
- **Production**: PostgreSQL via Supabase
- **ORM**: SQLAlchemy with async support (asyncpg for Postgres, aiosqlite for SQLite)
- **Models**: Defined in `packages/database/whatsapp_bot_database/models.py`
  - `User`: WhatsApp contacts with conversation tracking and integration fields
    - **Core fields**: phone (unique), name, email, auth_user_id (multi-tenant link)
    - **Conversation state**: intent_score, sentiment, stage, conversation_mode
    - **HubSpot sync**: hubspot_contact_id, hubspot_lifecyclestage, hubspot_synced_at
    - **Twilio auto-populated**: whatsapp_profile_name, country_code, phone_formatted, first_contact_timestamp, media_count, location_shared, last_twilio_message_sid
    - **Activity**: total_messages, last_message_at
  - `Message`: Conversation history
  - `Deal`: CRM pipeline management with stage synchronization
  - `Note`: CRM notes attached to users/deals
  - `Tag`: User categorization
  - `FollowUp`: Scheduled messages
  - Subscription models: `SubscriptionPlan`, `Subscription`, `UsageTracking`

### LangGraph Workflow (Bot Engine)

The bot uses an 11-node LangGraph workflow in `apps/bot-engine/src/graph/`:

1. **welcome_node** - Initial greeting
2. **intent_classifier_node** - Scores purchase intent (0-1) using GPT-4o-mini
3. **sentiment_analyzer_node** - Analyzes sentiment (positive/neutral/negative) using GPT-4o-mini
4. **data_collector_node** - Extracts and validates user data, syncs to HubSpot
5. **router_node** - Conditional routing based on intent/stage
6. **conversation_node** - Main conversation with RAG using GPT-4o
7. **closing_node** - High-intent sales closing
8. **payment_node** - Payment link handling
9. **follow_up_node** - Schedules follow-ups
10. **handoff_node** - Escalates to human agent
11. **summary_node** - Generates conversation summaries

**State Management**: All nodes share `ConversationState` (TypedDict) defined in `apps/bot-engine/src/graph/state.py`:

```python
class ConversationState(TypedDict):
    # Message history
    messages: List[BaseMessage]  # LangChain message objects

    # User identification
    user_phone: str
    user_name: Optional[str]
    user_email: Optional[str]

    # Conversation analysis (updated by nodes)
    intent_score: float  # 0.0-1.0, purchase likelihood
    sentiment: str  # "positive", "neutral", "negative"
    stage: str  # "welcome", "qualifying", "nurturing", "closing", "sold", "follow_up"

    # Conversation control
    conversation_mode: str  # "AUTO", "MANUAL", "NEEDS_ATTENTION"

    # Collected data
    collected_data: Dict[str, Any]  # Structured: name, email, needs, budget, etc.

    # Transaction tracking
    payment_link_sent: bool
    follow_up_scheduled: Optional[datetime]
    follow_up_count: int

    # Summary & response
    conversation_summary: Optional[str]  # AI-generated summary
    current_response: Optional[str]  # Latest bot response

    # Configuration & database
    config: Dict[str, Any]  # System prompts, TTS settings, etc.
    db_session: Optional[Any]  # Async DB session
    db_user: Optional[Any]  # SQLAlchemy User object
```

Each node receives state as input, performs its function, and returns updated state (immutable pattern).

**RAG System**: ChromaDB vector store with OpenAI embeddings for product knowledge retrieval.

**Data Validation**: Strict validation in `data_collector_node`:
- Name: Rejects greetings, capitalizes properly
- Email: Must match valid format with TLD
- Phone: Minimum 7 digits, formatted
- Needs/Pain Points: Minimum 5 characters, concrete descriptions
- Budget: Must mention numbers or monetary keywords

### Conversation Stages & CRM Synchronization

**User Stages** (Bot workflow):
- `welcome` → `qualifying` → `nurturing` → `closing` → `sold` → `follow_up`

**Deal Stages** (CRM pipeline):
- `new_lead` → `qualified` → `in_conversation` → `proposal_sent` → `won` / `lost`

**Auto-sync Logic** (in `data_collector_node`):
- When bot updates `User.stage`, associated `Deal.stage` updates automatically
- Only applies if `Deal.manually_qualified=false`
- Mapping: welcome→new_lead, qualifying→qualified, closing→in_conversation, sold→proposal_sent
- Once a deal stage is manually updated via API, `manually_qualified=true` prevents further auto-sync

### HubSpot Integration

**Auto-sync on data collection** (`apps/bot-engine/src/services/hubspot_sync.py`):
- Creates/updates contacts with standard fields (name, email, phone, lifecyclestage)
- Creates custom properties if they don't exist: intent_score, sentiment, needs, pain_points, budget
- Maps conversation stages to HubSpot lifecycle stages
- Adds conversation notes automatically

**Configuration**: Requires `HUBSPOT_ACCESS_TOKEN` in environment.

## Development Commands

### Setup

```bash
# Install shared packages first (editable mode required)
cd packages/shared && pip install -e .
cd ../database && pip install -e .

# Install API dependencies
cd ../../apps/api && pip install -r requirements.txt

# Install bot-engine dependencies
cd ../bot-engine && pip install -r requirements.txt

# Install frontend dependencies
cd ../web && npm install
```

### Running Services

**Development (Recommended)**: Use startup scripts that run all services:
```bash
# Windows
.\scripts\start_dev.ps1

# Linux/Mac
chmod +x scripts/start_dev.sh
./scripts/start_dev.sh
```

**Manual start**:
```bash
# API (from apps/api/)
python -m uvicorn src.main:app --reload --port 8000

# Frontend (from apps/web/)
npm run dev
```

**Docker Compose (Production)**:
```bash
docker-compose up --build
```

### Testing

**API Tests** (from `apps/api/`):
```bash
# Run all tests
pytest

# Run specific test categories (defined in pytest.ini)
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m rag           # RAG endpoint tests
pytest -m auth          # Auth tests
pytest -m config        # Configuration tests
pytest -m bot           # Bot processing tests
pytest -m conversations # Conversation tests

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_config_api.py

# Run single test function
pytest tests/unit/test_config_api.py::test_get_config
```

**Bot-Engine Tests** (from `apps/bot-engine/`):
```bash
pytest -m unit          # Unit tests
pytest -m integration   # Integration tests
pytest -m llm          # LLM service tests
pytest -m nodes        # Graph node tests
```

**Frontend**:
```bash
# From apps/web/
npm run build    # Test build
npm run lint     # Lint check
```

**Integration Test** (end-to-end):
```bash
# From project root
python scripts/test_integration.py
```

### Database Operations

**Migrations**: Located in `packages/database/migrations/`
```bash
# Apply migrations (manual SQL execution for now)
# Check migration files in packages/database/migrations/
```

**Initialize subscription plans**:
```bash
python scripts/init_subscription_plans.py
```

**Database inspection**:
```bash
# SQLite (dev)
sqlite3 apps/api/sales_bot.db

# PostgreSQL (via Docker Compose)
# pgAdmin available at http://localhost:5050
```

### API Documentation

When server is running:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Full endpoint reference: `API_DOCUMENTATION.md`

## Key Implementation Patterns

### Adding a New Endpoint

1. Create router in `apps/api/src/routers/`
2. Import database models from `whatsapp_bot_database`
3. Use async database session from `apps/api/src/database.py`
4. Add router to `apps/api/src/main.py`
5. Document in `API_DOCUMENTATION.md`

Example:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from whatsapp_bot_database.models import User

router = APIRouter(prefix="/myroute", tags=["myroute"])

@router.get("/")
async def get_items(db: AsyncSession = Depends(get_db)):
    # Use db session for queries
    pass
```

### Adding a New Graph Node

1. Define node function in `apps/bot-engine/src/graph/nodes.py`
2. Node signature: `async def my_node(state: ConversationState) -> ConversationState`
3. Update state and return it (immutable pattern)
4. Add node to graph in `apps/bot-engine/src/graph/workflow.py`
5. Connect edges appropriately
6. Test in isolation with unit tests

### Modifying Database Models

1. Edit models in `packages/database/whatsapp_bot_database/models.py`
2. Create migration SQL in `packages/database/migrations/`
3. Update CRUD operations in `packages/database/whatsapp_bot_database/crud.py`
4. Reinstall package: `pip install -e packages/database`
5. Apply migrations to database
6. Update API endpoints and bot nodes that use the model

### Adding RAG Documents

Documents are uploaded via `/rag/upload` endpoint and stored in:
- Files: `apps/api/rag_uploads/`
- Vector embeddings: `apps/api/chroma_db/` (ChromaDB collection)

Supported formats: PDF, TXT, DOC, DOCX

Processing happens in `apps/bot-engine/src/services/rag_service.py`:
- Chunking: 1000 chars with 200 overlap
- Embeddings: OpenAI `text-embedding-3-small`
- Retrieval: Top 3 most relevant chunks

## Environment Variables

Required `.env` at project root:
```env
# Required
OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite+aiosqlite:///./apps/api/sales_bot.db  # Dev
JWT_SECRET=your-secret-key-change-in-production

# Optional integrations
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+...
HUBSPOT_ACCESS_TOKEN=pat-na1-...

# Facebook/Instagram/Messenger (Phase 6)
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
FACEBOOK_VERIFY_TOKEN=...  # Custom token for webhook verification
FACEBOOK_OAUTH_REDIRECT_URI=https://yourdomain.com/integrations/facebook/callback
FRONTEND_URL=http://localhost:7860  # For OAuth redirects

# Production (Supabase)
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...
SUPABASE_DATABASE_URL=postgresql+asyncpg://...

LOG_LEVEL=INFO
```

## Tech Stack Summary

**Backend**: FastAPI, Python 3.11+, SQLAlchemy (async), Pydantic
**Bot Engine**: LangGraph, LangChain, OpenAI GPT-4o/GPT-4o-mini, ChromaDB
**Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS, Zustand
**Database**: SQLite (dev), PostgreSQL (prod via Supabase)
**Integrations**: Twilio (WhatsApp), HubSpot (CRM), OpenAI (LLM + TTS + Embeddings)
**Auth**: Supabase Auth with JWT
**Deployment**: Docker Compose, Render.com compatible

## Common Gotchas

1. **Import paths**: Shared packages must be installed in editable mode (`pip install -e`) for imports to work
2. **Database sessions**: Always use async sessions (`AsyncSession`) and proper async/await patterns
3. **LangGraph state**: State is immutable - always return a new/updated state dict from nodes
4. **CORS**: Frontend and API must have matching CORS config in `apps/api/src/main.py`
5. **Environment variables**: Bot-engine needs access to same `.env` as API when imported
6. **Manual stage updates**: Setting `Deal.stage` via API sets `manually_qualified=true`, preventing bot auto-sync
7. **ChromaDB persistence**: Collection stored in `apps/api/chroma_db/` - don't delete in production
8. **Rate limiting**: API has rate limits (200/min default) via SlowAPI middleware

## Testing Strategy

- **Unit tests**: Test individual functions/services in isolation
- **Integration tests**: Test full request/response cycles through API
- **Markers**: Use pytest markers (`-m unit`, `-m integration`) to run specific test suites
- **Fixtures**: Common fixtures in `conftest.py` (db sessions, mock data)
- **Coverage**: Target >80% coverage for critical paths (auth, bot processing, CRM)

## Deployment

**Render.com** (documented in Docker Compose):
- API service: Uses `apps/api/Dockerfile`
- Web service: Uses `apps/web/Dockerfile`
- PostgreSQL: Uses Render's managed Postgres
- Environment variables: Set in Render dashboard (see `.env` template)

**Health checks**:
- API: `GET /health`
- Bot: `GET /bot/health`
