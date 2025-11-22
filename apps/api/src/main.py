import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .routers import auth, conversations, bot, config, rag, followups, handoff

# Load environment variables
load_dotenv()

app = FastAPI(
    title="WhatsApp Sales Bot API",
    description="Backend API for WhatsApp Sales Bot SaaS",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Next.js frontend
    "http://localhost:8000",  # Self
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(config.router)
app.include_router(conversations.router)
app.include_router(bot.router)
app.include_router(rag.router)
app.include_router(followups.router)
app.include_router(handoff.router)


@app.get("/")
async def root():
    return {"message": "WhatsApp Sales Bot API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
