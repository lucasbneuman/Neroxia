import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .routers import auth, conversations, bot, config, rag, followups, integrations, handoff

# Load environment variables
load_dotenv()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(
    title="WhatsApp Sales Bot API",
    description="Backend API for WhatsApp Sales Bot SaaS",
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
    "http://localhost:3000",  # Next.js frontend (dev)
    "http://localhost:8000",  # Self (dev)
]

# Add production origins from environment variable
if allowed_origins_env:
    origins.extend([origin.strip() for origin in allowed_origins_env.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit methods
    allow_headers=["Content-Type", "Authorization"],  # Explicit headers
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Include routers
app.include_router(auth.router)
app.include_router(config.router)
app.include_router(conversations.router)
app.include_router(bot.router)
app.include_router(rag.router)
app.include_router(followups.router)
app.include_router(integrations.router)
app.include_router(handoff.router)


@app.get("/")
async def root():
    return {"message": "WhatsApp Sales Bot API is running"}


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
