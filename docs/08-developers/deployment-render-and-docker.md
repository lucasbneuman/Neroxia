# 🚀 Deployment Guide - Neroxia SaaS

**Version**: 1.0
**Last Updated**: 2025-11-23
**Target Platform**: Render.com (MVP)
**Local Development**: Docker Compose

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Variables](#environment-variables)
3. [Local Development (Docker Compose)](#local-development-docker-compose)
4. [Production Deployment (Render.com)](#production-deployment-rendercom)
5. [CI/CD Pipeline (GitHub Actions)](#cicd-pipeline-github-actions)
6. [Health Checks](#health-checks)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Procedures](#rollback-procedures)

---

## 🔧 Prerequisites

### For Local Development
- Docker Desktop 20.10+ ([Install](https://www.docker.com/products/docker-desktop))
- Docker Compose 2.0+ (included with Docker Desktop)
- Git
- Text editor (VS Code recommended)

### For Production Deployment
- GitHub account (for repository)
- Render.com account ([Sign up](https://render.com))
- Supabase account ([Sign up](https://supabase.com))
- OpenAI API key ([Get one](https://platform.openai.com))
- Twilio account (optional - for WhatsApp)
- HubSpot account (optional - for CRM)

---

## 🔐 Environment Variables

### Required Variables

#### Supabase (Database)
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhb...
SUPABASE_SERVICE_KEY=eyJhb...  # KEEP SECRET!
SUPABASE_DATABASE_URL=postgresql+asyncpg://postgres.xxx:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

**How to get these:**
1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Go to **Settings** → **API**
4. Copy `URL` and `anon/public key` and `service_role key`
5. For DATABASE_URL: **Settings** → **Database** → **Connection string** (Session Pooler)

#### OpenAI (AI/LLM)
```bash
OPENAI_API_KEY=sk-proj-...  # KEEP SECRET!
```

**How to get:**
1. Go to [OpenAI Platform](https://platform.openai.com)
2. Create API key under **API keys**

### Optional Variables

#### Twilio (WhatsApp Integration)
```bash
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...  # KEEP SECRET!
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

#### HubSpot (CRM Integration)
```bash
HUBSPOT_ACCESS_TOKEN=...  # KEEP SECRET!
HUBSPOT_CLIENT_SECRET=...  # KEEP SECRET!
```

#### Application Settings
```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
DEBUG=false  # true only for development
NODE_ENV=production  # development, production
```

### `.env.example`

Create a `.env` file from the template:
```bash
cp .env.example .env
# Edit .env with your actual values
```

**⚠️ NEVER commit `.env` to Git!** (already in `.gitignore`)

---

## 🐳 Local Development (Docker Compose)

### Initial Setup

1. **Clone the repository**
```bash
git clone https://github.com/lucasbneuman/neroxia.git
cd neroxia
```

2. **Create `.env` file**
```bash
cp .env.example .env
# Edit .env with your Supabase and OpenAI credentials
```

3. **Build and start services**
```bash
docker-compose up --build
```

This will start:
- **PostgreSQL** (local database) on `localhost:5432`
- **API** (FastAPI) on `http://localhost:8000`
- **Web** (Next.js) on `http://localhost:3000`
- **pgAdmin** (database UI) on `http://localhost:5050`

### Common Docker Commands

```bash
# Start services (after initial build)
docker-compose up

# Start in detached mode (background)
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v

# Rebuild specific service
docker-compose up --build api

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api

# Check service health
docker-compose ps

# Execute command in running container
docker-compose exec api bash
```

### Health Check Verification

After starting, verify all services are healthy:

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "services": {
#     "api": "healthy",
#     "database": "healthy",
#     "bot_engine": "healthy"
#   },
#   "version": "1.0.0"
# }

# Check Web (should return HTML)
curl http://localhost:3000/
```

### Accessing Services

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health
- **pgAdmin**: http://localhost:5050
  - Email: `admin@neroxia.local`
  - Password: `admin`

---

## ☁️ Production Deployment (Render.com)

### Step-by-Step Guide

#### 1. Prepare Repository

Ensure your code is pushed to GitHub:
```bash
git add .
git commit -m "Ready for deployment"
git push origin saas-migration
```

#### 2. Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repositories

#### 3. Deploy Using Blueprint (Recommended)

1. In Render Dashboard, click **"New +"** → **"Blueprint"**
2. Connect your GitHub repository: `lucasbneuman/neroxia`
3. Select branch: `saas-migration`
4. Render will detect `render.yaml` automatically
5. Click **"Apply"**

Render will create:
- **neroxia-api** (Web Service)
- **neroxia-web** (Web Service)

#### 4. Configure Environment Variables

For **neroxia-api**:

1. Go to service → **Environment** → **Environment Variables**
2. Add the following (click **"Add Environment Variable"** for each):

```
OPENAI_API_KEY = sk-proj-xxx (KEEP SECRET)
SUPABASE_URL = https://xxx.supabase.co
SUPABASE_ANON_KEY = eyJhb...
SUPABASE_SERVICE_KEY = eyJhb... (KEEP SECRET)
SUPABASE_DATABASE_URL = postgresql+asyncpg://postgres.xxx:... (KEEP SECRET)
TWILIO_ACCOUNT_SID = AC... (optional)
TWILIO_AUTH_TOKEN = ... (optional, KEEP SECRET)
TWILIO_WHATSAPP_NUMBER = whatsapp:+... (optional)
HUBSPOT_ACCESS_TOKEN = ... (optional, KEEP SECRET)
HUBSPOT_CLIENT_SECRET = ... (optional, KEEP SECRET)
LOG_LEVEL = INFO
DEBUG = false
```

For **neroxia-web**:

```
NEXT_PUBLIC_SUPABASE_URL = https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJhb...
```

**Note:** `NEXT_PUBLIC_API_URL` is automatically set from API service URL.

#### 5. Deploy

1. Click **"Manual Deploy"** → **"Deploy latest commit"**
2. Monitor build logs
3. Wait for **"Live"** status (typically 5-10 minutes)

#### 6. Verify Deployment

Once deployed, verify services:

```bash
# Get your Render URLs from dashboard
API_URL="https://neroxia-api.onrender.com"
WEB_URL="https://neroxia-web.onrender.com"

# Check API health
curl $API_URL/health

# Check Web (should return HTML)
curl $WEB_URL/
```

### Alternative: Manual Service Creation

If Blueprint doesn't work:

#### Create API Service

1. **New +** → **Web Service**
2. **Runtime**: Python
3. **Build Command**:
```bash
pip install --upgrade pip && pip install -e packages/shared && pip install -e packages/database && pip install -e apps/bot-engine && pip install -r apps/api/requirements.txt
```
4. **Start Command**:
```bash
cd apps/api && uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 1
```
5. **Health Check Path**: `/health`
6. Add environment variables (see above)

#### Create Web Service

1. **New +** → **Web Service**
2. **Runtime**: Node
3. **Build Command**:
```bash
cd apps/web && npm install && npm run build
```
4. **Start Command**:
```bash
cd apps/web && npm start
```
5. **Health Check Path**: `/`
6. Add environment variables (see above)
7. **Link API service**: In `NEXT_PUBLIC_API_URL`, select "From service" → neroxia-api

---

## 🔄 CI/CD Pipeline (GitHub Actions)

### Overview

The project includes a comprehensive CI/CD pipeline using GitHub Actions that automatically:
- ✅ Lints Python and TypeScript code
- ✅ Runs type checking (mypy, TypeScript)
- ✅ Tests Docker builds
- ✅ Runs unit tests (if available)
- 🔒 Optional: Auto-deploys to Render.com

### Workflow File

Location: `.github/workflows/ci.yml`

### Checks Performed

| Check | Description | Tools |
|-------|-------------|-------|
| **Python Linting** | Code style and syntax errors | flake8 |
| **Python Type Check** | Static type analysis | mypy |
| **TypeScript Linting** | Code style and best practices | ESLint |
| **TypeScript Type Check** | Type safety verification | tsc |
| **Docker Build** | Verify Dockerfiles build successfully | Docker Buildx |
| **Unit Tests** | Run pytest tests (if exist) | pytest |

### Triggering CI/CD

The pipeline runs automatically on:
- **Push** to `saas-migration` or `main` branches
- **Pull requests** to `saas-migration` or `main` branches

### Viewing Results

1. Go to your GitHub repository
2. Click **"Actions"** tab
3. Click on the latest workflow run
4. Expand each job to see detailed logs

### Configuration Files

#### `.flake8` - Python Linting
```ini
[flake8]
max-line-length = 127
max-complexity = 10
ignore = E203, E266, E501, W503, W504
```

#### `mypy.ini` - Python Type Checking
```ini
[mypy]
python_version = 3.11
ignore_missing_imports = True
strict_optional = False
```

### Running Checks Locally

#### Python Linting
```bash
# Install flake8
pip install flake8

# Lint API code
flake8 apps/api/src

# Lint bot-engine code
flake8 apps/bot-engine/src
```

#### Python Type Checking
```bash
# Install mypy
pip install mypy

# Check types
mypy apps/api/src --ignore-missing-imports
```

#### TypeScript Linting
```bash
# Navigate to web app
cd apps/web

# Run ESLint
npm run lint
```

#### TypeScript Type Checking
```bash
cd apps/web
npx tsc --noEmit
```

### Setting Up Auto-Deploy to Render

To enable automatic deployment on push to `main`:

1. **Get Render Deploy Hooks**:
   - Go to Render Dashboard
   - Select your API service → Settings → Deploy Hook
   - Copy the deploy hook URL
   - Repeat for Web service

2. **Add GitHub Secrets**:
   - Go to GitHub repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Add two secrets:
     - `RENDER_DEPLOY_HOOK_API`: Paste API deploy hook URL
     - `RENDER_DEPLOY_HOOK_WEB`: Paste Web deploy hook URL

3. **Enable Auto-Deploy**:
   - Edit `.github/workflows/ci.yml`
   - Uncomment the `deploy-render` job (lines ~180-195)
   - Commit and push

Now, every push to `main` will:
1. Run all CI checks
2. If all pass, trigger Render deployment automatically

### Branch Protection Rules (Recommended)

Protect your main branches by requiring CI to pass:

1. Go to GitHub repository → Settings → Branches
2. Click "Add branch protection rule"
3. Branch name pattern: `main` (or `saas-migration`)
4. Enable:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select checks: `All CI Checks Passed`
5. Save changes

This ensures no code is merged unless all checks pass.

### Troubleshooting CI/CD

#### Build fails on GitHub Actions
- Check the logs in Actions tab
- Verify all dependencies are in `requirements.txt` and `package.json`
- Ensure Docker builds work locally first

#### Type checking fails
- Run mypy/tsc locally to see errors
- Fix type issues or adjust configuration in `mypy.ini`

#### Auto-deploy not working
- Verify GitHub secrets are set correctly
- Check deploy hook URLs are valid
- Ensure `deploy-render` job is uncommented

---

## 🏥 Health Checks

### API Health Endpoint

**URL**: `/health`
**Method**: GET
**Response**:
```json
{
  "status": "healthy",
  "services": {
    "api": "healthy",
    "database": "healthy",
    "bot_engine": "healthy"
  },
  "version": "1.0.0"
}
```

**Status Codes**:
- `200 OK`: All services healthy
- `503 Service Unavailable`: One or more services degraded

### Health Check Configuration

#### Docker Compose
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

#### Render.com
```yaml
healthCheckPath: /health
```

Render automatically monitors this endpoint and restarts services if unhealthy.

---

## 🔍 Troubleshooting

### Docker Compose Issues

#### Services won't start
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

#### Port already in use
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Mac/Linux

# Kill the process or change port in docker-compose.yml
```

#### Database connection failed
```bash
# Verify postgres is healthy
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up postgres
```

### Render.com Issues

#### Build fails
1. Check build logs in Render dashboard
2. Verify `requirements.txt` and `package.json` are correct
3. Check Python version (should be 3.11+)
4. Check Node version (should be 18+)

#### Service crashes after deploy
1. Check **Logs** tab in Render dashboard
2. Verify environment variables are set correctly
3. Check health endpoint manually:
   ```bash
   curl https://your-api.onrender.com/health
   ```
4. Look for missing environment variables in logs

#### Database connection errors
1. Verify `SUPABASE_DATABASE_URL` is correct
2. Use **Session Pooler** URL (not Transaction pooler)
3. Check Supabase project is running
4. Verify IP allowlist (Supabase → Settings → Database → Connection pooling)

#### Frontend can't reach API
1. Verify `NEXT_PUBLIC_API_URL` is set correctly
2. Check CORS settings in `apps/api/src/main.py`
3. Ensure API service is deployed and healthy

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'X'` | Missing dependency | Add to requirements.txt, rebuild |
| `Connection refused` | Service not started | Check service status, verify ports |
| `Hydration error` | SSR/CSR mismatch | Check browser console, verify Supabase client setup |
| `401 Unauthorized` | Invalid credentials | Verify API keys and tokens |
| `503 Service Unavailable` | Health check failed | Check `/health` endpoint, verify database |

---

## ↩️ Rollback Procedures

### Render.com Rollback

#### Method 1: Redeploy Previous Version
1. Go to service → **Events**
2. Find last successful deployment
3. Click **"Redeploy"** on that commit

#### Method 2: Manual Deploy from Git
1. Identify working commit hash:
   ```bash
   git log --oneline
   ```
2. In Render: **Manual Deploy** → **Deploy commit** → Enter commit hash

#### Method 3: Environment Variable Rollback
If issue is config-related:
1. Go to **Environment** tab
2. Click **"View history"**
3. Revert to previous values
4. Click **"Save Changes"** (triggers redeploy)

### Docker Compose Rollback

```bash
# Pull previous version from Git
git log --oneline  # Find commit hash
git checkout <commit-hash>

# Rebuild and restart
docker-compose down
docker-compose up --build

# Return to latest
git checkout saas-migration
```

### Emergency Stop

If service is causing issues:

**Render.com**:
1. Service → **Settings** → **Suspend Service**

**Docker Compose**:
```bash
docker-compose down
```

---

## 📊 Monitoring & Logging

### Render.com Logs

- **Real-time**: Service → **Logs** tab
- **Download**: Click download icon for offline analysis
- **Search**: Use search box to filter logs

### Docker Compose Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100

# Since timestamp
docker-compose logs --since 2025-11-23T10:00:00
```

### Log Levels

Set via `LOG_LEVEL` environment variable:
- `DEBUG`: Verbose debugging info
- `INFO`: General information (default)
- `WARNING`: Warning messages only
- `ERROR`: Error messages only

---

## 🔒 Security Best Practices

1. **Never commit secrets**
   - Use `.env` for local development
   - Use Render environment variables for production
   - Never push `.env` to Git

2. **Use strong secrets**
   - `SUPABASE_SERVICE_KEY`: Keep private, never expose to frontend
   - `OPENAI_API_KEY`: Rotate regularly
   - `TWILIO_AUTH_TOKEN`: Store securely

3. **Enable CORS properly**
   - Update `apps/api/src/main.py` with production domains
   - Don't use `allow_origins=["*"]` in production

4. **Keep dependencies updated**
   ```bash
   pip list --outdated  # Python
   npm outdated  # Node.js
   ```

---

## 📚 Additional Resources

- [Render.com Docs](https://render.com/docs)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Supabase Docs](https://supabase.com/docs)

---

## 🆘 Support

If you encounter issues:

1. Check this guide's [Troubleshooting](#troubleshooting) section
2. Review service logs (Render or Docker)
3. Consult `.agents/BUG_TRACKER.md` for known issues
4. Create issue in `.agents/TASK_LOG.md`

---

**Last Updated**: 2025-11-23
**Maintained by**: DevOps Agent
**Version**: 1.0
