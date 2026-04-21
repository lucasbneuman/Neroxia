# Deployment Guide: Render + Supabase

This guide walks you through deploying the WhatsApp Sales SaaS application to Render.com with Supabase as the database.

## Prerequisites

- GitHub account with your repository
- Supabase account (free tier available at [supabase.com](https://supabase.com))
- Render account (free tier available at [render.com](https://render.com))
- All API keys ready (OpenAI, Twilio, HubSpot)

---

## Step 1: Create Supabase Project

1. **Sign up/Login to Supabase**
   - Go to [supabase.com](https://supabase.com)
   - Create a new account or sign in

2. **Create New Project**
   - Click "New Project"
   - Choose your organization
   - Enter project details:
     - **Name**: `neroxia-bot` (or your preferred name)
     - **Database Password**: Generate a strong password (save it!)
     - **Region**: Choose closest to your users
   - Click "Create new project"
   - Wait 2-3 minutes for provisioning

3. **Save Project Credentials**
   - Go to **Settings** → **API**
   - Copy and save these values:
     - `Project URL` → This is your `SUPABASE_URL`
     - `anon public` key → This is your `SUPABASE_ANON_KEY`
   - Go to **Settings** → **API** → **Service Role**
     - Copy `service_role` key → This is your `SUPABASE_SERVICE_KEY`
   - Go to **Settings** → **Database**
     - Copy the connection string → This is your `SUPABASE_DATABASE_URL`
     - Format: `postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/postgres`
     - Convert to asyncpg format: `postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:[PORT]/postgres`

---

## Step 2: Execute Database Schema

1. **Open SQL Editor**
   - In Supabase dashboard, go to **SQL Editor**
   - Click "New query"

2. **Copy Schema SQL**
   - Open `scripts/supabase_schema.sql` from your project
   - Copy the entire contents

3. **Execute Schema**
   - Paste the SQL into the Supabase SQL Editor
   - Click "Run" or press `Ctrl+Enter`
   - Verify success (should see "Success. No rows returned")

4. **Verify Tables Created**
   - Go to **Table Editor** in Supabase
   - You should see these tables:
     - `users`
     - `messages`
     - `configs`
     - `follow_ups`

---

## Step 3: Update Local Environment

1. **Update `.env` File**
   
   Add these Supabase variables to your `.env`:
   
   ```env
   # Supabase Configuration
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   SUPABASE_SERVICE_KEY=your-service-key-here
   SUPABASE_DATABASE_URL=postgresql+asyncpg://postgres:your-password@db.your-project.supabase.co:5432/postgres
   
   # Keep existing variables
   OPENAI_API_KEY=your-openai-key
   TWILIO_ACCOUNT_SID=your-twilio-sid
   TWILIO_AUTH_TOKEN=your-twilio-token
   TWILIO_WHATSAPP_NUMBER=your-whatsapp-number
   HUBSPOT_ACCESS_TOKEN=your-hubspot-token
   HUBSPOT_CLIENT_SECRET=your-hubspot-secret
   ```

2. **Test Local Connection** (Optional)
   
   ```bash
   cd apps/api
   pip install -r requirements.txt
   python -c "from src.core.supabase import supabase; print('✓ Supabase connected')"
   ```

---

## Step 4: Connect Repository to Render

1. **Sign up/Login to Render**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub (recommended)

2. **Connect GitHub Repository**
   - In Render dashboard, click "New +"
   - Select "Blueprint"
   - Click "Connect a repository"
   - Authorize Render to access your GitHub
   - Select your `neroxia` repository

3. **Select Branch**
   - Choose `saas-migration` branch
   - Render will detect `render.yaml` automatically

---

## Step 5: Configure Environment Variables

Render will create two services from `render.yaml`:
- `neroxia-api` (Backend)
- `neroxia-web` (Frontend)

### Configure API Service Environment Variables

1. Go to **neroxia-api** service
2. Click **Environment** tab
3. Add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `SUPABASE_URL` | `https://your-project.supabase.co` | From Step 1 |
| `SUPABASE_ANON_KEY` | `your-anon-key` | From Step 1 |
| `SUPABASE_SERVICE_KEY` | `your-service-key` | From Step 1 |
| `SUPABASE_DATABASE_URL` | `postgresql+asyncpg://...` | From Step 1 |
| `OPENAI_API_KEY` | `sk-...` | Your OpenAI API key |
| `TWILIO_ACCOUNT_SID` | `AC...` | Your Twilio SID |
| `TWILIO_AUTH_TOKEN` | `...` | Your Twilio auth token |
| `TWILIO_WHATSAPP_NUMBER` | `+1...` | Your Twilio WhatsApp number |
| `HUBSPOT_ACCESS_TOKEN` | `pat-...` | Your HubSpot access token |
| `HUBSPOT_CLIENT_SECRET` | `...` | Your HubSpot client secret |

### Configure Web Service Environment Variables

1. Go to **neroxia-web** service
2. Click **Environment** tab
3. Add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `NEXT_PUBLIC_SUPABASE_URL` | `https://your-project.supabase.co` | From Step 1 |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `your-anon-key` | From Step 1 |

**Note**: `NEXT_PUBLIC_API_URL` is automatically set from the API service URL.

---

## Step 6: Deploy Services

1. **Apply Blueprint**
   - Click "Apply" to create services from `render.yaml`
   - Render will start building both services

2. **Monitor Build Progress**
   - Watch the build logs for both services
   - API build takes ~5-10 minutes
   - Web build takes ~3-5 minutes

3. **Wait for Deployment**
   - Services will automatically deploy after successful build
   - You'll see "Live" status when ready

---

## Step 7: Verify Deployment

### Test API Service

1. **Get API URL**
   - Go to **neroxia-api** service
   - Copy the service URL (e.g., `https://neroxia-api.onrender.com`)

2. **Test Health Endpoint**
   ```bash
   curl https://neroxia-api.onrender.com/health
   ```
   Expected response: `{"status":"healthy"}`

3. **Test Auth Endpoint**
   ```bash
   curl -X POST https://neroxia-api.onrender.com/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"testpass123"}'
   ```
   Expected: User created with tokens

### Test Web Service

1. **Get Web URL**
   - Go to **neroxia-web** service
   - Copy the service URL (e.g., `https://neroxia-web.onrender.com`)

2. **Open in Browser**
   - Visit the web URL
   - You should see the Next.js application
   - Try logging in with the test user created above

### Test Database Connection

1. **Check Supabase Dashboard**
   - Go to Supabase **Table Editor**
   - Check `users` table
   - You should see the test user created

---

## Step 8: Configure Twilio Webhook (Production)

1. **Update Twilio Webhook URL**
   - Go to Twilio Console
   - Navigate to your WhatsApp Sandbox or Phone Number
   - Set webhook URL to: `https://neroxia-api.onrender.com/bot/webhook`
   - Save changes

2. **Test WhatsApp Integration**
   - Send a message to your WhatsApp number
   - Check Render logs to see webhook received
   - Verify response in WhatsApp

---

## Troubleshooting

### Build Failures

**Issue**: API build fails with "Module not found"
- **Solution**: Check that all packages are listed in `requirements.txt`
- Verify `packages/database` and `packages/shared` are installed with `-e` flag

**Issue**: Web build fails with npm errors
- **Solution**: Clear build cache in Render
- Check `package.json` for correct dependencies

### Database Connection Issues

**Issue**: "Could not connect to database"
- **Solution**: Verify `SUPABASE_DATABASE_URL` format is correct
- Ensure it uses `postgresql+asyncpg://` prefix
- Check Supabase project is not paused (free tier pauses after inactivity)

**Issue**: "Row Level Security" errors
- **Solution**: Verify RLS policies were created in Step 2
- Re-run `supabase_schema.sql` if needed

### Authentication Issues

**Issue**: "Invalid Supabase credentials"
- **Solution**: Double-check all three Supabase keys are correct
- Verify keys are from the same project
- Check for extra spaces in environment variables

---

## Monitoring and Maintenance

### View Logs

**API Logs**:
- Go to **neroxia-api** → **Logs** tab
- Monitor for errors and requests

**Web Logs**:
- Go to **neroxia-web** → **Logs** tab
- Check for build and runtime errors

### Database Monitoring

- Go to Supabase **Database** → **Logs**
- Monitor query performance
- Check for slow queries

### Auto-Deploy

- Render automatically deploys on git push to `saas-migration` branch
- Monitor deployments in Render dashboard

---

## Cost Considerations

### Render Free Tier
- 750 hours/month per service (enough for 1 service 24/7)
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds

### Supabase Free Tier
- 500MB database storage
- 2GB bandwidth/month
- Projects pause after 1 week of inactivity

### Upgrading
- Render Starter: $7/month per service (no spin-down)
- Supabase Pro: $25/month (no pause, more resources)

---

## Next Steps

1. **Set up custom domain** (optional)
   - Configure in Render dashboard
   - Update CORS settings in API

2. **Enable monitoring**
   - Set up error tracking (Sentry, etc.)
   - Configure uptime monitoring

3. **Backup strategy**
   - Supabase provides automatic backups (Pro plan)
   - Export data regularly for free tier

4. **Security hardening**
   - Review RLS policies
   - Enable MFA for Supabase/Render accounts
   - Rotate API keys regularly

---

## Support

- **Render Docs**: https://render.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **Project Issues**: Create issue in GitHub repository
