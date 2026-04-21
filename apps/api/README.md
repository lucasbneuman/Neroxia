# Neroxia - API Backend

FastAPI backend for the Neroxia SaaS platform.

## Tech Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: SQLAlchemy (Async) + SQLite (shared with bot-engine)
- **Auth**: JWT (Python-Jose)
- **Validation**: Pydantic

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   Note: This requires `packages/database` and `packages/shared` to be installed in editable mode first.

2. **Run Server**
   ```bash
   python -m uvicorn src.main:app --reload --port 8000
   ```

## Endpoints

### Auth
- `POST /auth/login` - Login with username/password (returns JWT)

### Conversations
- `GET /conversations` - List active conversations
- `GET /conversations/{phone}/messages` - Get message history
- `POST /conversations/{phone}/take-control` - Switch to MANUAL mode
- `POST /conversations/{phone}/return-to-bot` - Switch to AUTO mode
- `POST /conversations/{phone}/send` - Send manual message

## Database
Connects to the root `neroxia.db` SQLite database using models from `packages/database`.
