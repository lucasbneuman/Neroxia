# Multi-stage build for WhatsApp Sales Bot API (FastAPI)
# Production-optimized with security and performance in mind

# ============================================
# Stage 1: Builder - Install dependencies
# ============================================
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package definitions for dependency resolution
COPY packages/shared/setup.py packages/shared/
COPY packages/database/setup.py packages/database/
COPY apps/bot-engine/setup.py apps/bot-engine/
COPY apps/api/requirements.txt apps/api/

# Install Python dependencies to a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install shared packages first (editable mode)
COPY packages/shared/ packages/shared/
COPY packages/database/ packages/database/
COPY apps/bot-engine/ apps/bot-engine/

RUN pip install --upgrade pip && \
    pip install -e packages/shared && \
    pip install -e packages/database && \
    pip install -e apps/bot-engine && \
    pip install --no-cache-dir -r apps/api/requirements.txt

# ============================================
# Stage 2: Runtime - Minimal production image
# ============================================
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 apiuser && \
    mkdir -p /app/chroma_db /app/rag_uploads /app/apps/api && \
    chown -R apiuser:apiuser /app

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code with proper ownership
COPY --chown=apiuser:apiuser apps/api/ apps/api/
COPY --chown=apiuser:apiuser packages/ packages/
COPY --chown=apiuser:apiuser apps/bot-engine/ apps/bot-engine/

# Switch to non-root user
USER apiuser

# Expose API port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set Python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO

# Start the FastAPI application
CMD ["uvicorn", "apps.api.src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
