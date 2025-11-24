# Dockerfile for Bot Engine (LangGraph Workflow)
# NOTE: Currently bot-engine is embedded in API service
# This Dockerfile is for future use if bot-engine needs to run as separate worker

# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.11-slim as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package definitions
COPY packages/shared/setup.py packages/shared/
COPY packages/database/setup.py packages/database/
COPY apps/bot-engine/setup.py apps/bot-engine/
COPY apps/bot-engine/requirements.txt apps/bot-engine/

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install packages
COPY packages/shared/ packages/shared/
COPY packages/database/ packages/database/
COPY apps/bot-engine/ apps/bot-engine/

RUN pip install --upgrade pip && \
    pip install -e packages/shared && \
    pip install -e packages/database && \
    pip install -e apps/bot-engine && \
    pip install --no-cache-dir -r apps/bot-engine/requirements.txt

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 botuser && \
    mkdir -p /app/chroma_db && \
    chown -R botuser:botuser /app

WORKDIR /app

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=botuser:botuser apps/bot-engine/ apps/bot-engine/
COPY --chown=botuser:botuser packages/ packages/

USER botuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO

# This is a placeholder - bot-engine currently runs embedded in API
# If you need to run it as a separate worker, add appropriate CMD here
CMD ["python", "-m", "graph.workflow"]
