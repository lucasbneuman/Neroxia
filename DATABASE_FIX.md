# Database Connection Issues - Quick Fix Guide

## Problem

The API is returning 500 errors because it cannot connect to the Supabase database.

**Error**: `socket.gaierror` - Cannot resolve `db.oveixhmndwrtymuymdxm.supabase.co`

## Quick Fix: Use SQLite for Local Development

### Step 1: Update `.env`

Comment out the Supabase database URL and use SQLite instead:

```env
# SUPABASE_DATABASE_URL=postgresql+asyncpg://postgres:5vNAztJpXzbt3@db.oveixhmndwrtymuymdxm.supabase.co:5432/postgres
DATABASE_URL=sqlite+aiosqlite:///./sales_bot.db
```

### Step 2: Initialize Database

Run the initialization script:

```bash
python scripts/init_database.py
```

### Step 3: Restart API Server

The server should automatically reload, or restart it manually:

```bash
cd apps/api
python -m uvicorn src.main:app --reload --port 8000
```

## Alternative: Use Local PostgreSQL

If you have Docker installed:

```bash
# Start PostgreSQL container
docker-compose up -d postgres

# Use this in .env:
DATABASE_URL=postgresql+asyncpg://salesbot:salesbot_dev_password@localhost:5432/sales_bot
```

## Verify Supabase Connection (If you want to use Supabase)

1. Check that your Supabase project is active at https://supabase.com
2. Verify credentials in `.env` match your Supabase project
3. Check if your IP is allowed in Supabase dashboard
4. Test connection manually:
   ```bash
   psql "postgresql://postgres:5vNAztJpXzbt3@db.oveixhmndwrtymuymdxm.supabase.co:5432/postgres"
   ```

## Recommendation

For local development, **use SQLite** (Option 1). It's simpler and doesn't require network connectivity.

For production deployment, use Supabase or a managed PostgreSQL service.
