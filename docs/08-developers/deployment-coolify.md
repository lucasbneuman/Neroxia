# Deployment Guide - Coolify

This guide covers deploying the Neroxia to Coolify (self-hosted PaaS).

## Prerequisites

- Coolify instance running (v4.x+)
- Domain names configured:
  - `api.neroxia.tech` → API service
  - `neroxia.tech` → Public marketing site
  - `app.neroxia.tech` → SaaS application frontend
- Git repository accessible to Coolify
- Required API keys (OpenAI, Twilio, HubSpot, Facebook)

## Deployment Steps

### 1. Create New Project in Coolify

1. Log in to Coolify dashboard
2. Click "New Project"
3. Select "Docker Compose"
4. Connect Git repository
5. Set branch to `main` (or your production branch)

### 2. Configure Environment Variables

In Coolify project settings, add all variables from `.env.example`:

**Critical Variables:**
- `SUPABASE_DATABASE_URL` - Supabase PostgreSQL connection string
- `OPENAI_API_KEY` - From OpenAI platform
- `SUPABASE_*` - From Supabase project settings
- `FACEBOOK_*` - From Meta Developers Console

### 3. Configure Domains

**API Service:**
- Domain: `api.neroxia.tech`
- Internal port: 8000
- Health check: `/health`

**Web Service:**
- Domains: `https://neroxia.tech:3000,https://app.neroxia.tech:3000`
- Internal port: 3000
- Health check: `/api/health`

Do not publish service ports to the host in Coolify. The Docker Compose file uses
`expose` for `api` and `web` so Coolify's proxy can route to the containers
without conflicting with other applications on the server.
The web service forces `PORT=3000` in Compose because global Coolify variables
such as `PORT=7860` would otherwise make Next.js listen on the wrong internal
port.

Final public routing:
- `https://neroxia.tech` serves marketing pages (`/`, `/platform`, `/pricing`)
- `https://app.neroxia.tech` serves the SaaS app (`/login`, `/signup`, `/dashboard`)
- `https://api.neroxia.tech` serves the backend API

Recommended production URL variables:
```env
NEXT_PUBLIC_API_URL=https://api.neroxia.tech
FRONTEND_URL=https://app.neroxia.tech
ALLOWED_ORIGINS=https://neroxia.tech,https://app.neroxia.tech
FACEBOOK_OAUTH_REDIRECT_URI=https://api.neroxia.tech/integrations/facebook/callback
```

### 4. Database Setup

The database is the existing Supabase PostgreSQL project. After first deployment:

```bash
# Access API container
coolify exec api bash

# Run migrations
cd packages/database/migrations
# Execute SQL files in order: 001, 002, 003, 004, 005, 006
```

Or use psql directly:
```bash
psql $SUPABASE_DATABASE_URL -f packages/database/migrations/001_initial_schema.sql
psql $SUPABASE_DATABASE_URL -f packages/database/migrations/002_add_crm_features.sql
psql $SUPABASE_DATABASE_URL -f packages/database/migrations/003_add_subscription_models.sql
psql $SUPABASE_DATABASE_URL -f packages/database/migrations/004_add_multi_tenant_support.sql
psql $SUPABASE_DATABASE_URL -f packages/database/migrations/005_add_messaging_channels.sql
psql $SUPABASE_DATABASE_URL -f packages/database/migrations/006_add_messaging_channels.sql
```

### 5. Configure Meta Webhooks

After deployment, configure Facebook webhooks:

1. Go to Meta Developers Console
2. Select your app
3. Configure webhooks:
   - **Instagram**: `https://api.neroxia.tech/webhook/instagram`
   - **Messenger**: `https://api.neroxia.tech/webhook/messenger`
4. Set verify token: Value from `FACEBOOK_VERIFY_TOKEN`
5. Subscribe to events:
   - `messages`
   - `messaging_postbacks`
   - `messaging_optins`

### 6. Test Deployment

**Health Checks:**
```bash
curl https://api.neroxia.tech/health
curl https://app.neroxia.tech/api/health
curl https://neroxia.tech
```

**API Documentation:**
- Swagger: `https://api.neroxia.tech/docs`
- ReDoc: `https://api.neroxia.tech/redoc`

**Frontend:**
- Open `https://neroxia.tech` for public pages
- Open `https://app.neroxia.tech/login` for the SaaS app
- Sign up / Log in
- Navigate to Integrations
- Connect Facebook/Instagram

## Monitoring

**Logs:**
```bash
# API logs
coolify logs api

# Frontend logs
coolify logs web

```

**Health Endpoints:**
- API: `GET /health` → Returns 200 OK with status JSON
- API diagnostics: `GET /health/details` → Checks database and bot engine
- Web: `GET /api/health` → Returns 200 OK

## Scaling

**Horizontal Scaling:**
```yaml
# In docker-compose.yml
services:
  api:
    deploy:
      replicas: 3  # Run 3 API instances
```

**Resource Limits:**
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Troubleshooting

**503 Service Unavailable:**
- Check health checks are passing
- Verify environment variables set correctly
- Check logs for startup errors

**Database Connection Errors:**
- Verify `SUPABASE_DATABASE_URL` format
- Ensure the Supabase project is active
- Check network connectivity between services

**Meta Webhooks Not Working:**
- Verify webhook URLs are correct
- Check `FACEBOOK_VERIFY_TOKEN` matches Meta settings
- Ensure SSL certificate is valid
- Check API logs for webhook errors

## Backup Strategy

**Database Backups:**
- Use Supabase project backups from the Supabase dashboard.
- For manual exports, run `pg_dump` against `SUPABASE_DATABASE_URL` from a secure machine.

**Volume Backups:**
- `api_uploads` - RAG documents
- `api_chroma` - Vector embeddings
- `api_avatars` - User avatars

## Security Checklist

- [ ] All environment variables use strong secrets
- [ ] Supabase database password is strong
- [ ] SSL/TLS enabled for all domains
- [ ] Meta webhook signatures verified
- [ ] Rate limiting enabled
- [ ] CORS configured correctly
- [ ] Supabase RLS policies active

## Support

For issues or questions:
- Check logs first: `coolify logs <service>`
- Review health checks
- Consult canonical architecture docs in `../01-architecture/sad.md` and `../01-architecture/sdd.md`
