# Railway Detailed Deployment Guide

## Complete Step-by-Step Based on Real Deployment Experience

This guide documents **exactly** what we did to deploy the Meuble de France Chatbot to Railway, in the correct order, with all settings and configurations.

---

## Deployment Order

We deployed in this order:
1. **Backend First** (Python FastAPI)
2. **Frontend Second** (React/Vite)
3. **Database Last** (PostgreSQL) - Connected to Backend

---

# PART 1: BACKEND DEPLOYMENT

## Step 1.1: Create Railway Project

1. Go to https://railway.app/
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub (if first time)
5. Select your repository (e.g., `SAV-BOT-Meuble-de-france`)

## Step 1.2: Configure Root Directory

If your backend is in a subfolder:

1. Click on the newly created service
2. Go to **"Settings"** tab
3. Scroll down to **"Source"** section
4. Find **"Root Directory"**
5. Set it to: `backend`
6. Click **"Save"** or it auto-saves

```
Root Directory: backend
```

## Step 1.3: Configure Build Settings

Still in **"Settings"** tab:

1. Scroll to **"Build"** section
2. Railway usually auto-detects Python, but verify:
   - Builder: **Nixpacks** (default)
   - Build Command: (leave empty, Railway detects from requirements.txt)

3. Scroll to **"Deploy"** section
4. Set **Start Command**:

```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Step 1.4: Add Environment Variables

Go to **"Variables"** tab and click **"+ New Variable"** for each:

### Essential Variables (Add These First)

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `PORT` | `8000` | Backend port |
| `NODE_ENV` | `production` | Production mode |
| `LOG_LEVEL` | `info` | Logging level |

### API Keys

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `OPENAI_API_KEY` | `sk-proj-your-openai-api-key-here` | Your actual OpenAI key |

### Security Variables

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `JWT_SECRET` | `change-this-in-production-use-strong-secret` | Generate a strong random string |
| `SESSION_SECRET` | `change-this-in-production-use-strong-secret` | Generate a strong random string |

### CORS Variables (Important!)

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `ALLOWED_ORIGINS` | `https://your-railway-domain.up.railway.app` | Will update after frontend deployment |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173,http://localhost:8080` | For local development |

### Rate Limiting

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `RATE_LIMIT_MAX_REQUESTS` | `100` | Max requests per window |
| `RATE_LIMIT_WINDOW_MS` | `900000` | 15 minutes in milliseconds |

### Database Variables (Add Later After PostgreSQL Setup)

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `DATABASE_URL` | (will add after PostgreSQL) | Full connection string |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | (from PostgreSQL service) | Database password |
| `POSTGRES_DB` | `railway` | Database name |
| `POSTGRES_PORT` | `5432` | Database port |

## Step 1.5: Generate Backend Domain

1. Go to **"Settings"** tab
2. Scroll to **"Networking"** section
3. Under **"Public Networking"**:
   - Click **"Generate Domain"**
4. Copy your backend URL:

```
Example: https://sav-bot-meuble-de-france-production.up.railway.app
```

**Save this URL - you'll need it for frontend configuration!**

## Step 1.6: First Deployment

1. Railway will automatically start deploying
2. Go to **"Deployments"** tab
3. Click on the latest deployment to see logs
4. Watch for errors

### Common First Deployment Errors

#### Error: "ModuleNotFoundError"
**Solution:** Add missing package to `requirements.txt`

#### Error: "DATABASE_URL environment variable is required"
**Solution:** This is expected - we'll add database later. For now, you might need to set a dummy value or modify your code to handle missing database gracefully.

#### Error: SyntaxError with emojis (Python 3.13)
**Solution:** Remove emojis from the beginning of lines in Python multiline strings:

```python
# BAD - Causes SyntaxError on Python 3.13
text = """
🎯 IMPORTANT:
This is text
"""

# GOOD - Works on Python 3.13
text = """
IMPORTANT:
This is text
"""
```

## Step 1.7: Verify Backend is Running

Once deployment is green:

1. Open your backend URL in browser
2. Go to: `https://your-backend.up.railway.app/docs`
3. You should see the FastAPI Swagger documentation
4. If you see the docs, backend is working!

---

# PART 2: FRONTEND DEPLOYMENT

## Step 2.1: Add Frontend Service

1. In your Railway project dashboard
2. Click **"+ New"** button (top right)
3. Select **"GitHub Repo"**
4. Select the same repository (or different if frontend is separate)

## Step 2.2: Configure Root Directory

1. Click on the new service
2. Go to **"Settings"** tab
3. Set **"Root Directory"**: `frontend`

## Step 2.3: Configure Build Settings

In **"Settings"** tab:

1. **Build Command** (if not auto-detected):
```
npm install && npm run build
```

2. **Start Command**:
```
npm run preview
```

Or if using `serve`:
```
npx serve dist -l $PORT
```

## Step 2.4: Add Frontend Environment Variables

Go to **"Variables"** tab and add:

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `VITE_API_URL` | `https://your-backend.up.railway.app` | Your backend URL from Step 1.5 |
| `VITE_WS_URL` | `wss://your-backend.up.railway.app` | WebSocket URL (same as backend, but wss://) |
| `NODE_ENV` | `production` | Production mode |

**Important:** Replace `your-backend.up.railway.app` with your actual backend URL!

## Step 2.5: Generate Frontend Domain

1. Go to **"Settings"** tab
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"**
4. Copy your frontend URL:

```
Example: https://sav-bot-frontend-production.up.railway.app
```

## Step 2.6: Update Backend CORS Settings

**CRITICAL STEP!** Go back to your Backend service:

1. Click on **Backend** service
2. Go to **"Variables"** tab
3. Find `ALLOWED_ORIGINS`
4. Update it to include your frontend URL:

```
ALLOWED_ORIGINS=https://your-frontend.up.railway.app,https://innaturalstores.com
```

Multiple URLs separated by commas, no spaces!

5. Backend will automatically redeploy

## Step 2.7: Verify Frontend

1. Wait for frontend deployment to complete (green checkmark)
2. Open your frontend URL in browser
3. Open browser Developer Tools (F12)
4. Go to **Console** tab
5. Check for CORS errors

### If You See CORS Errors:

```
Access to fetch at 'https://backend...' from origin 'https://frontend...'
has been blocked by CORS policy
```

**Solution:**
1. Go to Backend → Variables
2. Make sure `ALLOWED_ORIGINS` includes your exact frontend URL
3. No trailing slashes
4. Must include `https://`
5. Wait for backend to redeploy

---

# PART 3: POSTGRESQL DATABASE

## Step 3.1: Add PostgreSQL Service

1. In your Railway project
2. Click **"+ New"**
3. Select **"Database"**
4. Choose **"PostgreSQL"**
5. Wait 1-2 minutes for provisioning

## Step 3.2: Get Database Credentials

1. Click on the **PostgreSQL** service
2. Go to **"Variables"** tab
3. You'll see these variables (Railway creates them automatically):

| Variable | Example Value |
|----------|---------------|
| `DATABASE_URL` | `postgresql://postgres:abc123@postgres.railway.internal:5432/railway` |
| `PGHOST` | `postgres.railway.internal` |
| `PGPORT` | `5432` |
| `PGUSER` | `postgres` |
| `PGPASSWORD` | `rhuTZdokjJXJMlqNCXltoNhazphIncbT` |
| `PGDATABASE` | `railway` |

## Step 3.3: Get PUBLIC Database URL (For Migrations)

The internal URL only works within Railway. For running migrations from your local machine:

1. Click on PostgreSQL service
2. Go to **"Settings"** tab
3. Scroll to **"Networking"** section
4. Find **"TCP Proxy"** or **"Public Networking"**
5. If not enabled, click **"Enable"**
6. Copy the public connection details:

```
Public Host: hopper.proxy.rlwy.net
Public Port: 12551 (different from internal 5432!)
```

**Public DATABASE_URL format:**
```
postgresql://postgres:PASSWORD@hopper.proxy.rlwy.net:12551/railway
```

## Step 3.4: Connect Backend to Database

1. Go to **Backend** service
2. Go to **"Variables"** tab
3. Add or update `DATABASE_URL`:

**Option A: Direct URL (Recommended)**
```
DATABASE_URL=postgresql://postgres:rhuTZdokjJXJMlqNCXltoNhazphIncbT@hopper.proxy.rlwy.net:12551/railway
```

**Option B: Reference Variable (If available)**
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

Note: Option B only works if Railway shows shared variables. If not, use Option A.

## Step 3.5: Run Database Migrations

From your local machine:

### Create Migration Script

Create `migrate_railway.py` in your backend folder:

```python
#!/usr/bin/env python
"""Run database migrations on Railway"""
import asyncio
import asyncpg
import sys

async def migrate(database_url: str):
    print("Connecting to database...")
    conn = await asyncpg.connect(database_url)

    try:
        # Example: Create tables
        print("Running migrations...")

        # Add your migration SQL here
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS your_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100)
            );
        """)

        print("Migration completed!")

    finally:
        await conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_railway.py <database_url>")
        sys.exit(1)
    asyncio.run(migrate(sys.argv[1]))
```

### Run Migration

```bash
cd backend
python migrate_railway.py "postgresql://postgres:PASSWORD@hopper.proxy.rlwy.net:PORT/railway"
```

Replace PASSWORD and PORT with your actual values!

## Step 3.6: Verify Database Connection

1. Go to Backend service → Deployments
2. Click on latest deployment
3. Check logs for:
   - `Database initialized successfully` ✅
   - No connection errors

If you see connection errors:
- Check DATABASE_URL is correct
- Check password has no extra spaces
- Make sure you're using the public URL (hopper.proxy.rlwy.net), not internal URL

---

# PART 4: TROUBLESHOOTING GUIDE

## Issue: Backend Crashes on Startup

### Check Deploy Logs
1. Go to Backend service
2. Click "Deployments" tab
3. Click on failed deployment
4. Read the error message

### Common Errors and Solutions

| Error Message | Solution |
|---------------|----------|
| `ModuleNotFoundError: No module named 'xxx'` | Add `xxx` to `requirements.txt` |
| `SyntaxError: invalid character '🎯'` | Remove emojis from start of lines in Python strings |
| `DATABASE_URL environment variable is required` | Add DATABASE_URL to Variables |
| `Connection refused` | Check database URL, use public URL |
| `database "railway\n" does not exist` | DATABASE_URL has whitespace, use `.strip()` in code |

## Issue: CORS Errors in Browser

### Symptoms
```
Access to fetch at 'https://...' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present
```

### Solution
1. Go to Backend → Variables
2. Check `ALLOWED_ORIGINS` includes your **exact** frontend URL
3. Format: `https://your-frontend.up.railway.app`
4. No trailing slash!
5. No spaces between multiple URLs (use commas)

### Example
```
ALLOWED_ORIGINS=https://sav-bot-frontend.up.railway.app,https://yourdomain.com
```

## Issue: Database Connection Failed

### Symptoms
- Backend logs show "Connection refused"
- "database does not exist"
- "password authentication failed"

### Solutions

1. **Check DATABASE_URL format:**
```
postgresql://USER:PASSWORD@HOST:PORT/DATABASE
```

2. **Use PUBLIC URL for backend:**
   - Internal: `postgres.railway.internal:5432` (won't work for backend service)
   - Public: `hopper.proxy.rlwy.net:12551` (use this!)

3. **Clean whitespace from URL in code:**
```python
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
```

4. **Check variable fallbacks in config.py:**
```python
# Support both Railway variable names
pguser = os.getenv("PGUSER") or os.getenv("POSTGRES_USER", "postgres")
pgpassword = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD")
```

## Issue: Frontend Shows Blank Page

### Solutions

1. **Check VITE_API_URL is set correctly:**
   - Must include `https://`
   - Must be the backend URL, not frontend URL
   - No trailing slash

2. **Check browser console for errors:**
   - Press F12 → Console tab
   - Look for red error messages

3. **Verify backend is running:**
   - Open backend URL directly
   - Should see JSON or API docs

## Issue: Python 3.13 Syntax Errors

Railway uses Python 3.13 which is stricter about Unicode characters in source code.

### Fix Emoji Issues

**Problem:** Emojis at the start of lines in multiline strings cause syntax errors.

**Before (Broken):**
```python
message = """
🎯 IMPORTANT:
Here is some text
📋 LIST:
- Item 1
"""
```

**After (Fixed):**
```python
message = """
IMPORTANT:
Here is some text
LIST:
- Item 1
"""
```

### Fix Accented Characters in Docstrings

**Problem:** French accented characters in docstrings can cause issues.

**Before:**
```python
def get_priority(self):
    """Retourne l'emoji de priorité"""
    pass
```

**After:**
```python
def get_priority(self):
    """Returns priority emoji"""
    pass
```

---

# PART 5: COMPLETE ENVIRONMENT VARIABLES REFERENCE

## Backend Service Variables

```env
# === SERVER ===
PORT=8000
NODE_ENV=production
LOG_LEVEL=info

# === DATABASE ===
DATABASE_URL=postgresql://postgres:PASSWORD@hopper.proxy.rlwy.net:PORT/railway
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=railway
POSTGRES_PORT=5432

# === API KEYS ===
OPENAI_API_KEY=sk-proj-xxx...

# === CORS (CRITICAL!) ===
ALLOWED_ORIGINS=https://your-frontend.up.railway.app,https://yourdomain.com
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080

# === SECURITY ===
JWT_SECRET=generate-a-strong-random-string-at-least-32-characters
SESSION_SECRET=generate-another-strong-random-string-at-least-32-characters

# === RATE LIMITING ===
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_MS=900000

# === OPTIONAL ===
REDIS_PORT=6379
DEBUG=false
```

## Frontend Service Variables

```env
# === API CONNECTION ===
VITE_API_URL=https://your-backend.up.railway.app
VITE_WS_URL=wss://your-backend.up.railway.app

# === ENVIRONMENT ===
NODE_ENV=production
```

---

# PART 6: POST-DEPLOYMENT CHECKLIST

## Backend Verification

- [ ] Service shows green status in Railway dashboard
- [ ] Open `https://your-backend.up.railway.app/docs` - shows Swagger docs
- [ ] Check deployment logs - no errors
- [ ] Database connection successful (check logs)

## Frontend Verification

- [ ] Service shows green status
- [ ] Website loads correctly
- [ ] No CORS errors in browser console (F12)
- [ ] Can login/use features
- [ ] API calls work (check Network tab in F12)

## Database Verification

- [ ] PostgreSQL service shows green status
- [ ] Tables were created (run migration if needed)
- [ ] Data persists after creating test entry
- [ ] Backend can read/write to database

## Security Checklist

- [ ] Changed `JWT_SECRET` from default value
- [ ] Changed `SESSION_SECRET` from default value
- [ ] `ALLOWED_ORIGINS` only contains known domains
- [ ] No API keys visible in frontend code
- [ ] HTTPS enabled on all services

---

# PART 7: QUICK COMMANDS REFERENCE

## Railway CLI

```bash
# Install
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Run command in Railway environment
railway run python manage.py migrate

# Open project dashboard
railway open
```

## Database Migration from Local

```bash
# Navigate to backend
cd backend

# Run migration with public DATABASE_URL
python migrate_script.py "postgresql://postgres:PASSWORD@hopper.proxy.rlwy.net:PORT/railway"
```

## Test Database Connection

```bash
# Quick connection test
python -c "
import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect('postgresql://postgres:PASSWORD@hopper.proxy.rlwy.net:PORT/railway')
    version = await conn.fetchval('SELECT version()')
    print(f'Connected: {version}')
    await conn.close()

asyncio.run(test())
"
```

---

# PART 8: MY DEPLOYMENT DETAILS

Fill in these details during deployment:

```
Project Name: _______________________________________

=== BACKEND ===
Railway URL: https://____________________________.up.railway.app
Root Directory: backend
Port: 8000

=== FRONTEND ===
Railway URL: https://____________________________.up.railway.app
Root Directory: frontend

=== DATABASE ===
Internal URL: postgres.railway.internal:5432
Public Host: hopper.proxy.rlwy.net
Public Port: ____________
Password: ______________________________________________
Database Name: railway

=== CUSTOM DOMAINS (if any) ===
Backend: _______________________________________________
Frontend: ______________________________________________
```

---

*Detailed Deployment Guide - Based on Meuble de France Chatbot Deployment*
*Created January 2025*
