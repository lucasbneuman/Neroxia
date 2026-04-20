# Deployment Guide - Coolify

Esta app debe desplegarse en Coolify como proyecto `Docker Compose`, usando:

- `.coolify/config.json`
- `docker-compose.prod.yml`

## Resumen

- Tipo de proyecto en Coolify: `Docker Compose`
- Archivo de despliegue: `docker-compose.prod.yml`
- Healthcheck API: `/health`
- Healthcheck Web: `/api/health`
- Servicios esperados:
  - `postgres`
  - `api`
  - `web`

## Variables mínimas de producción

### Base de datos

Usa una de estas estrategias:

1. `DATABASE_URL`
   Valor recomendado si el API usará la base incluida en `docker-compose.prod.yml`.
   Debe ser async-compatible para SQLAlchemy:
   `postgresql+asyncpg://USER:PASSWORD@HOST:5432/DBNAME`

2. `SUPABASE_DATABASE_URL`
   Úsala si prefieres una base externa de Supabase.
   Si viene en formato `postgresql://` o `postgres://`, el backend ahora la normaliza a `postgresql+asyncpg://`.

### Backend/API

- `JWT_SECRET`
- `ALLOWED_ORIGINS`
- `FRONTEND_URL`
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_KEY`

### Frontend/Web

- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### Meta / Instagram / Messenger

- `FACEBOOK_APP_ID`
- `FACEBOOK_APP_SECRET`
- `FACEBOOK_VERIFY_TOKEN`
- `FACEBOOK_OAUTH_REDIRECT_URI`

### Integraciones opcionales

Define estas sólo si vas a activarlas en el primer deploy:

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_NUMBER`
- `HUBSPOT_ACCESS_TOKEN`

## Configuración recomendada en Coolify

### 1. Crear el proyecto

1. En Coolify, crea un proyecto nuevo.
2. Elige `Docker Compose`.
3. Conecta este repositorio.
4. Usa `docker-compose.prod.yml` como archivo de despliegue.

### 2. Dominios

Los dominios deben coincidir con `.coolify/config.json`:

- API: `api.yourdomain.com`
- Web: `app.yourdomain.com`

Ejemplo de valores:

- `FRONTEND_URL=https://app.yourdomain.com`
- `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`
- `ALLOWED_ORIGINS=https://app.yourdomain.com,https://www.app.yourdomain.com`
- `FACEBOOK_OAUTH_REDIRECT_URI=https://api.yourdomain.com/integrations/facebook/callback`

### 3. PostgreSQL

Puedes usar:

- la base `postgres` del mismo `docker-compose.prod.yml`, o
- una base externa tipo Supabase

Si usas la base interna del compose, define:

- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

Y el servicio `api` construirá:

- `DATABASE_URL=postgresql+asyncpg://DB_USER:DB_PASSWORD@postgres:5432/DB_NAME`

Si usas Supabase externa, deja igualmente definidos `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY` y agrega `SUPABASE_DATABASE_URL`.

## Migraciones reales del repo

Las migraciones actuales en `packages/database/migrations` son:

- `002_create_crm_tables.sql`
- `003_add_deal_manual_flag.sql`
- `004_add_subscription_tables.sql`
- `005_enable_row_level_security.sql`
- `006_add_messaging_channels.sql`

No hay que usar nombres anteriores o inexistentes.

Ejemplo con `psql`:

```bash
psql "$DATABASE_URL" -f packages/database/migrations/002_create_crm_tables.sql
psql "$DATABASE_URL" -f packages/database/migrations/003_add_deal_manual_flag.sql
psql "$DATABASE_URL" -f packages/database/migrations/004_add_subscription_tables.sql
psql "$DATABASE_URL" -f packages/database/migrations/005_enable_row_level_security.sql
psql "$DATABASE_URL" -f packages/database/migrations/006_add_messaging_channels.sql
```

Si `DATABASE_URL` usa `postgresql+asyncpg://`, para `psql` conviene convertirla a un DSN postgres estándar o usar los parámetros separados de conexión.

## Comandos oficiales de terminal

### Backend local

```powershell
cd C:\Users\AVALITH\Desktop\Proyectos\whatsapp_sales_bot\apps\api
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend local

```powershell
cd C:\Users\AVALITH\Desktop\Proyectos\whatsapp_sales_bot\apps\web
npm run dev
```

### Tests backend API

```powershell
cd C:\Users\AVALITH\Desktop\Proyectos\whatsapp_sales_bot\apps\api
pytest
```

### Tests bot-engine

```powershell
cd C:\Users\AVALITH\Desktop\Proyectos\whatsapp_sales_bot\apps\bot-engine
pytest
```

### Checks frontend

```powershell
cd C:\Users\AVALITH\Desktop\Proyectos\whatsapp_sales_bot\apps\web
npm run lint
npm run build
```

### Validación de deploy local

```powershell
cd C:\Users\AVALITH\Desktop\Proyectos\whatsapp_sales_bot
docker compose -f docker-compose.prod.yml config
docker compose -f docker-compose.prod.yml build
```

## Validación previa a subir

Checklist mínima:

- `apps/api/tests` en verde
- `apps/bot-engine` en verde
- `apps/web` lint en verde
- `apps/web` build en verde
- `docker compose -f docker-compose.prod.yml config` válido
- variables de Coolify completas
- dominios de API/Web correctos

## Webhooks de Meta

Después del deploy:

- Instagram: `https://api.yourdomain.com/webhook/instagram`
- Messenger: `https://api.yourdomain.com/webhook/messenger`

Usa `FACEBOOK_VERIFY_TOKEN` como verify token y confirma que `FACEBOOK_APP_SECRET` quede cargado para la verificación de firma.

## Troubleshooting rápido

### API no levanta

- revisa `DATABASE_URL` o `SUPABASE_DATABASE_URL`
- revisa `JWT_SECRET`
- revisa `SUPABASE_*`

### Frontend no conecta con el backend

- revisa `NEXT_PUBLIC_API_URL`
- revisa `ALLOWED_ORIGINS`
- revisa `FRONTEND_URL`

### OAuth de Meta falla

- revisa `FACEBOOK_APP_ID`
- revisa `FACEBOOK_APP_SECRET`
- revisa `FACEBOOK_OAUTH_REDIRECT_URI`
- revisa que el redirect URI en Meta coincida exactamente con el configurado
