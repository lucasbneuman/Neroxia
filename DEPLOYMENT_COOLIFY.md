# Deployment Guide - Coolify

This guide covers deploying the WhatsApp Sales Bot to Coolify (self-hosted PaaS).

## Prerequisites

- Coolify instance running (v4.x+)
- Domain names configured:
  - `api.yourdomain.com` → API service
  - `app.yourdomain.com` → Frontend
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

In Coolify project settings, add all variables from `.env.prod.example`:

**Critical Variables:**
- `DATABASE_URL` - Auto-configured by Coolify PostgreSQL service
- `JWT_SECRET` - Generate with: `openssl rand -base64 32`
- `OPENAI_API_KEY` - From OpenAI platform
- `SUPABASE_*` - From Supabase project settings
- `FACEBOOK_*` - From Meta Developers Console

### 3. Configure Domains

**API Service:**
- Domain: `api.yourdomain.com`
- Port: 8000
- Health check: `/health`

**Web Service:**
- Domain: `app.yourdomain.com`
- Port: 3000
- Health check: `/api/health`

### 4. Database Setup

Coolify will auto-provision PostgreSQL. After first deployment:

```bash
# Access API container
coolify exec api bash

# Run migrations
cd packages/database/migrations
# Execute SQL files in order: 001, 002, 003, 004, 005, 006
```

Or use psql directly:
```bash
psql $DATABASE_URL -f packages/database/migrations/001_initial_schema.sql
psql $DATABASE_URL -f packages/database/migrations/002_add_crm_features.sql
psql $DATABASE_URL -f packages/database/migrations/003_add_subscription_models.sql
psql $DATABASE_URL -f packages/database/migrations/004_add_multi_tenant_support.sql
psql $DATABASE_URL -f packages/database/migrations/005_add_messaging_channels.sql
psql $DATABASE_URL -f packages/database/migrations/006_add_messaging_channels.sql
```

### 5. Configure Meta Webhooks

After deployment, configure Facebook webhooks:

1. Go to Meta Developers Console
2. Select your app
3. Configure webhooks:
   - **Instagram**: `https://api.yourdomain.com/webhook/instagram`
   - **Messenger**: `https://api.yourdomain.com/webhook/messenger`
4. Set verify token: Value from `FACEBOOK_VERIFY_TOKEN`
5. Subscribe to events:
   - `messages`
   - `messaging_postbacks`
   - `messaging_optins`

### 6. Test Deployment

**Health Checks:**
```bash
curl https://api.yourdomain.com/health
curl https://app.yourdomain.com/api/health
```

**API Documentation:**
- Swagger: `https://api.yourdomain.com/docs`
- ReDoc: `https://api.yourdomain.com/redoc`

**Frontend:**
- Open `https://app.yourdomain.com`
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

# Database logs
coolify logs postgres
```

**Health Endpoints:**
- API: `GET /health` → Returns 200 OK with status JSON
- Web: `GET /api/health` → Returns 200 OK

## Scaling

**Horizontal Scaling:**
```yaml
# In docker-compose.prod.yml
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
- Verify `DATABASE_URL` format
- Ensure PostgreSQL service is healthy
- Check network connectivity between services

**Meta Webhooks Not Working:**
- Verify webhook URLs are correct
- Check `FACEBOOK_VERIFY_TOKEN` matches Meta settings
- Ensure SSL certificate is valid
- Check API logs for webhook errors

## Backup Strategy

**Database Backups:**
```bash
# Automated daily backups (Coolify handles this)
# Manual backup:
coolify exec postgres pg_dump -U postgres whatsapp_bot > backup_$(date +%Y%m%d).sql
```

**Volume Backups:**
- `api_uploads` - RAG documents
- `api_chroma` - Vector embeddings
- `api_avatars` - User avatars

## Security Checklist

- [ ] All environment variables use strong secrets
- [ ] JWT_SECRET is randomly generated
- [ ] Database password is strong
- [ ] SSL/TLS enabled for all domains
- [ ] Meta webhook signatures verified
- [ ] Rate limiting enabled
- [ ] CORS configured correctly
- [ ] Supabase RLS policies active

## Support

For issues or questions:
- Check logs first: `coolify logs <service>`
- Review health checks
- Consult main documentation in `ARCHITECTURE.md`
