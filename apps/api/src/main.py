"""Main application entry point."""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .routers import (
    auth,
    bot,
    config,
    conversations,
    crm,
    followups,
    handoff,
    integrations,
    meta_webhook,
    rag,
    subscriptions,
    twilio_webhook,
    users,
)



# Load environment variables
load_dotenv()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(
    title="Neroxia API",
    description="Backend API for Neroxia SaaS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add rate limiter to app state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add GZip compression middleware (compress responses > 1000 bytes)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configure CORS
# Allow configuring allowed origins via environment variable for production
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

# Add production origins from environment variable
if allowed_origins_env:
    origins.extend([origin.strip() for origin in allowed_origins_env.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)  # User management
app.include_router(subscriptions.router)  # Subscription management
app.include_router(config.router)
app.include_router(conversations.router)
app.include_router(bot.router)
app.include_router(rag.router)
app.include_router(followups.router)
app.include_router(integrations.router)
app.include_router(handoff.router)
app.include_router(twilio_webhook.router)  # Twilio webhook for incoming messages
app.include_router(meta_webhook.router)  # Instagram + Messenger webhooks
app.include_router(crm.router)  # CRM module endpoints

# Mount static files for avatars
avatars_dir = Path("avatars")
avatars_dir.mkdir(exist_ok=True)  # Create directory if it doesn't exist
app.mount("/avatars", StaticFiles(directory=str(avatars_dir)), name="avatars")


@app.get("/")
async def root():
    return {"message": "Neroxia API is running"}


@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.
    Returns overall status and individual service health.
    """
    from .database import get_db
    from sqlalchemy import text

    health_status = {
        "status": "healthy",
        "services": {
            "api": "healthy",
            "database": "unknown",
            "bot_engine": "unknown"
        },
        "version": "1.0.0"
    }

    # Check database connection
    try:
        async for db in get_db():
            await db.execute(text("SELECT 1"))
            health_status["services"]["database"] = "healthy"
            break
    except Exception as e:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"

    # Check bot-engine availability
    try:
        from graph.workflow import get_sales_graph
        graph = get_sales_graph()
        health_status["services"]["bot_engine"] = "healthy"
    except Exception as e:
        health_status["services"]["bot_engine"] = "unhealthy"
        health_status["status"] = "degraded"

    return health_status
