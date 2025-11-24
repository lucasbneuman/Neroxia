# 🔧 Supabase Connection Fix Guide

## 🚨 Current Problem

The diagnostic script revealed: **Invalid Supabase API credentials**

```
Error: 401 Unauthorized - Invalid API key
```

This means your Supabase service key is invalid or the project doesn't exist.

## ✅ Solution Steps

### Step 1: Verify Supabase Project Exists

1. Go to: https://supabase.com/dashboard
2. Log in to your account
3. Check if you see a project with reference: `oveixhmndwrtymuymdxm`
4. If the project doesn't exist, you need to create a new one

### Step 2: Get Fresh Credentials

Once you're in your Supabase project dashboard:

#### A. Get API Keys

1. Go to: **Settings** → **API**
2. Copy the following values:
   - **Project URL**: Should look like `https://[PROJECT-REF].supabase.co`
   - **anon/public key**: Under "Project API keys"
   - **service_role key**: Under "Project API keys" (click "Reveal" to see it)

#### B. Get Database Connection String

1. Go to: **Settings** → **Database**
2. Scroll to **Connection string** section
3. Select the **URI** tab
4. **IMPORTANT**: Choose between:
   - **Direct connection** (Use this if unsure)
     - Mode: Direct connection
     - Copy the connection string
   - **Connection pooler** (For production with many connections)
     - Mode: Session
     - Copy the connection string

The connection string will look like one of these:

**Direct Connection:**
```
postgresql://postgres.oveixhmndwrtymuymdxm:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

**OR Pooler:**
```
postgresql://postgres:[YOUR-PASSWORD]@db.oveixhmndwrtymuymdxm.supabase.co:5432/postgres
```

### Step 3: Update .env File

Update your `.env` file with the correct values:

```env
# Supabase Configuration
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=[YOUR-ANON-KEY]
SUPABASE_SERVICE_KEY=[YOUR-SERVICE-ROLE-KEY]

# Database URL - ADD asyncpg+ at the beginning
# If using Direct Connection:
SUPABASE_DATABASE_URL=postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# OR if using Connection Pooler:
SUPABASE_DATABASE_URL=postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**IMPORTANT**:
- Replace `[YOUR-PASSWORD]` with your actual database password
- Add `postgresql+asyncpg://` (note the `+asyncpg`) instead of just `postgresql://`
- Make sure there are no spaces or line breaks in the connection string

### Step 4: Find Your Database Password

If you don't remember your database password:

1. Go to: **Settings** → **Database**
2. Look for **Database Password** section
3. Click **Reset Database Password** if needed
4. Copy the new password
5. Update it in the connection string

### Step 5: Verify the Connection

Run the verification script:

```bash
./venv/Scripts/python.exe scripts/test_supabase_simple.py
```

### Step 6: Restart the API

```bash
# Stop all running API processes
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"

# Start fresh
cd apps/api
../../venv/Scripts/python.exe -m uvicorn src.main:app --reload --port 8000
```

## 🔍 Common Issues

### Issue 1: "Invalid API key"
- Your service key is wrong or expired
- Solution: Get a fresh key from Settings → API

### Issue 2: "getaddrinfo failed"
- Your database hostname is wrong
- Solution: Get the correct connection string from Settings → Database

### Issue 3: "Password authentication failed"
- Your database password is wrong
- Solution: Reset the password in Settings → Database

### Issue 4: "Connection timeout"
- You might be using pooler when you should use direct connection (or vice versa)
- Solution: Try the other connection method

## 📞 Need Help?

If you're still having issues:

1. Check the Supabase project status at: https://status.supabase.com
2. Verify your project isn't paused (free tier projects pause after inactivity)
3. Make sure you're using the correct project (check the project reference ID)

## ✨ What This Will Fix

Once you update the credentials correctly:

- ✅ Login will continue to work
- ✅ Configuration page will load (`/config`)
- ✅ Test chat will work (`/test`)
- ✅ Database queries will succeed
- ✅ Bot processing will work

---

**Last Updated**: 2025-11-23
