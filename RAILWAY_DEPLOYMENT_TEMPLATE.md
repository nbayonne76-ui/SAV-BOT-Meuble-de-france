# Railway Deployment Template

## Complete Guide for Deploying Backend + Frontend + PostgreSQL

This template documents all steps required to deploy a full-stack application (Python FastAPI backend, React frontend, PostgreSQL database) to Railway.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Railway Project Setup](#2-railway-project-setup)
3. [PostgreSQL Database Setup](#3-postgresql-database-setup)
4. [Backend Service Setup](#4-backend-service-setup)
5. [Frontend Service Setup](#5-frontend-service-setup)
6. [Environment Variables Reference](#6-environment-variables-reference)
7. [Database Migrations](#7-database-migrations)
8. [CORS Configuration](#8-cors-configuration)
9. [Troubleshooting](#9-troubleshooting)
10. [Post-Deployment Checklist](#10-post-deployment-checklist)

---

## 1. Prerequisites

### Required Accounts
- [ ] Railway account: https://railway.app/
- [ ] GitHub account (for automatic deployments)

### Required Tools
- [ ] Git installed locally
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed (for frontend)

### Code Repository
- [ ] Backend code pushed to GitHub
- [ ] Frontend code pushed to GitHub (can be same repo or separate)

---

## 2. Railway Project Setup

### Step 2.1: Create New Project

1. Go to https://railway.app/
2. Click **"New Project"**
3. Choose **"Empty Project"**
4. Name your project (e.g., "my-chatbot-app")

### Step 2.2: Project Structure

You will create 3 services in this project:
```
Railway Project
├── PostgreSQL (Database)
├── Backend (Python FastAPI)
└── Frontend (React/Vite)
```

---

## 3. PostgreSQL Database Setup

### Step 3.1: Add PostgreSQL Service

1. In your Railway project, click **"+ New"**
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Wait for deployment (1-2 minutes)

### Step 3.2: Get Database Credentials

After PostgreSQL is deployed:

1. Click on the **PostgreSQL** service
2. Go to **"Variables"** tab
3. Note down these values (you'll need them later):

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Full connection string | `postgresql://postgres:abc123@host:5432/railway` |
| `PGHOST` | Database host | `postgres.railway.internal` |
| `PGPORT` | Database port | `5432` |
| `PGUSER` | Database user | `postgres` |
| `PGPASSWORD` | Database password | `abc123xyz` |
| `PGDATABASE` | Database name | `railway` |

### Step 3.3: Get Public Database URL

For external connections (migrations from local machine):

1. Click on PostgreSQL service
2. Go to **"Settings"** tab
3. Under **"Networking"**, find **"Public Networking"**
4. Enable it if not already enabled
5. Copy the **public DATABASE_URL** (uses different host/port)

Example public URL:
```
postgresql://postgres:password@hopper.proxy.rlwy.net:12551/railway
```

---

## 4. Backend Service Setup

### Step 4.1: Add Backend Service

1. In your Railway project, click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose your backend repository
4. If monorepo, set the **Root Directory** to `/backend`

### Step 4.2: Configure Build Settings

1. Click on the **Backend** service
2. Go to **"Settings"** tab
3. Configure:

| Setting | Value |
|---------|-------|
| Root Directory | `backend` (if monorepo) or `/` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### Step 4.3: Add Environment Variables

Go to **"Variables"** tab and add these variables:

#### Required Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql://postgres:PASSWORD@hopper.proxy.rlwy.net:PORT/railway` | From PostgreSQL service (public URL) |
| `OPENAI_API_KEY` | `sk-proj-xxx...` | Your OpenAI API key |
| `PORT` | `8000` | Backend port |
| `NODE_ENV` | `production` | Environment mode |

#### CORS Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `ALLOWED_ORIGINS` | `https://your-frontend.up.railway.app,https://yourdomain.com` | Frontend URLs |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173,http://localhost:8080` | For local dev |

#### Security Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `JWT_SECRET` | `your-strong-secret-key-here` | JWT signing key |
| `SESSION_SECRET` | `your-session-secret-here` | Session encryption |

#### Optional Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `LOG_LEVEL` | `info` | Logging level |
| `DEBUG` | `false` | Debug mode |
| `RATE_LIMIT_MAX_REQUESTS` | `100` | Rate limiting |
| `RATE_LIMIT_WINDOW_MS` | `900000` | Rate limit window (15 min) |

### Step 4.4: Configure Networking

1. Go to **"Settings"** tab
2. Under **"Networking"**:
   - Click **"Generate Domain"** to get a Railway URL
   - Or add a custom domain

Note your backend URL:
```
https://your-backend.up.railway.app
```

---

## 5. Frontend Service Setup

### Step 5.1: Add Frontend Service

1. In your Railway project, click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose your frontend repository
4. If monorepo, set the **Root Directory** to `/frontend`

### Step 5.2: Configure Build Settings

1. Click on the **Frontend** service
2. Go to **"Settings"** tab
3. Configure:

| Setting | Value |
|---------|-------|
| Root Directory | `frontend` (if monorepo) or `/` |
| Build Command | `npm install && npm run build` |
| Start Command | `npm run preview` or `npx serve dist` |

### Step 5.3: Add Environment Variables

Go to **"Variables"** tab and add:

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | `https://your-backend.up.railway.app` | Backend API URL |
| `VITE_WS_URL` | `wss://your-backend.up.railway.app` | WebSocket URL |
| `NODE_ENV` | `production` | Environment mode |

### Step 5.4: Configure Networking

1. Go to **"Settings"** tab
2. Under **"Networking"**:
   - Click **"Generate Domain"** to get a Railway URL
   - Or add a custom domain

Note your frontend URL:
```
https://your-frontend.up.railway.app
```

### Step 5.5: Update Backend CORS

After getting your frontend URL, go back to the **Backend** service and update:

```
ALLOWED_ORIGINS=https://your-frontend.up.railway.app
```

---

## 6. Environment Variables Reference

### Complete Backend Variables

```env
# === DATABASE ===
DATABASE_URL=postgresql://postgres:PASSWORD@hopper.proxy.rlwy.net:PORT/railway

# === API KEYS ===
OPENAI_API_KEY=sk-proj-xxx...
ANTHROPIC_API_KEY=sk-ant-xxx...  # Optional

# === SERVER ===
PORT=8000
NODE_ENV=production
LOG_LEVEL=info

# === CORS ===
ALLOWED_ORIGINS=https://your-frontend.up.railway.app,https://yourdomain.com
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# === SECURITY ===
JWT_SECRET=your-strong-jwt-secret-minimum-32-characters
SESSION_SECRET=your-strong-session-secret-minimum-32-characters

# === RATE LIMITING ===
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_MS=900000

# === OPTIONAL: Redis ===
REDIS_URL=redis://default:xxx@redis.railway.internal:6379

# === OPTIONAL: Cloudinary ===
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### Complete Frontend Variables

```env
# === API ===
VITE_API_URL=https://your-backend.up.railway.app
VITE_WS_URL=wss://your-backend.up.railway.app

# === ENVIRONMENT ===
NODE_ENV=production
```

---

## 7. Database Migrations

### Option A: Run Migration from Local Machine

1. Get the **public** DATABASE_URL from Railway PostgreSQL service

2. Create a migration script (example for adding columns):

```python
#!/usr/bin/env python
"""migrate_railway.py - Run database migrations on Railway"""
import asyncio
import asyncpg
import sys

async def migrate(database_url: str):
    print("Connecting to database...")
    conn = await asyncpg.connect(database_url)

    try:
        # Your migration SQL here
        await conn.execute("""
            ALTER TABLE your_table
            ADD COLUMN IF NOT EXISTS new_column VARCHAR(50);
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

3. Run the migration:

```bash
python migrate_railway.py "postgresql://postgres:PASSWORD@hopper.proxy.rlwy.net:PORT/railway"
```

### Option B: Run Migration via Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migration
railway run python migrate.py
```

### Option C: Auto-Migration on Startup

Add migration check in your FastAPI startup:

```python
# app/main.py
@app.on_event("startup")
async def startup_event():
    await run_migrations()
```

---

## 8. CORS Configuration

### Backend CORS Setup (FastAPI)

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Get allowed origins from environment
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
cors_origins = os.getenv("CORS_ORIGINS", "").split(",")

# Combine all origins
all_origins = [origin.strip() for origin in (allowed_origins + cors_origins) if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Important CORS Rules

1. **Always include your Railway frontend URL** in `ALLOWED_ORIGINS`
2. **Include localhost URLs** in `CORS_ORIGINS` for local development
3. **Don't use `*`** in production - list specific domains
4. **Update CORS** when you add custom domains

---

## 9. Troubleshooting

### Issue: Backend Won't Start

**Symptoms:** Backend deployment fails or crashes on startup

**Check Deploy Logs:**
1. Click on Backend service
2. Go to **"Deployments"** tab
3. Click on the latest deployment
4. Read the logs

**Common Causes:**

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | Add missing package to `requirements.txt` |
| `DATABASE_URL required` | Add `DATABASE_URL` to environment variables |
| `Connection refused` | Check database URL is correct |
| `SyntaxError` | Fix Python syntax (check for emoji in code) |

### Issue: Database Connection Failed

**Symptoms:** `Connection refused` or `database does not exist`

**Solutions:**

1. **Check DATABASE_URL format:**
   ```
   postgresql://USER:PASSWORD@HOST:PORT/DATABASE
   ```

2. **Use public URL for external access:**
   - Railway internal: `postgres.railway.internal:5432`
   - Railway public: `hopper.proxy.rlwy.net:12551`

3. **Clean whitespace from URL:**
   ```python
   DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
   ```

### Issue: CORS Error

**Symptoms:** Browser shows `No 'Access-Control-Allow-Origin' header`

**Solutions:**

1. Add your frontend URL to `ALLOWED_ORIGINS`
2. Make sure URL includes `https://`
3. No trailing slash in URLs
4. Redeploy backend after changing variables

### Issue: Frontend Can't Connect to Backend

**Symptoms:** API calls fail, 404 or connection errors

**Solutions:**

1. Check `VITE_API_URL` is set correctly in frontend
2. Verify backend URL is correct (no typos)
3. Make sure backend is actually running (check deployments)
4. Verify CORS includes frontend URL

### Issue: Python 3.13 Syntax Error with Emojis

**Symptoms:** `SyntaxError: invalid character` with emoji

**Solution:** Remove emojis from the beginning of lines in multiline strings:

```python
# BAD - Will fail on Python 3.13
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

---

## 10. Post-Deployment Checklist

### Backend Checks

- [ ] Backend service is running (green status)
- [ ] Health endpoint works: `https://your-backend.up.railway.app/health`
- [ ] API docs load: `https://your-backend.up.railway.app/docs`
- [ ] Database connection successful (check logs)
- [ ] No errors in deployment logs

### Frontend Checks

- [ ] Frontend service is running (green status)
- [ ] Website loads correctly
- [ ] Can connect to backend API
- [ ] No CORS errors in browser console
- [ ] All features work as expected

### Database Checks

- [ ] PostgreSQL service is running
- [ ] Tables created correctly
- [ ] Migrations completed
- [ ] Data persists after redeployment

### Security Checks

- [ ] `JWT_SECRET` is strong and unique
- [ ] `SESSION_SECRET` is strong and unique
- [ ] No sensitive data in logs
- [ ] CORS only allows known domains
- [ ] HTTPS enabled on all services

---

## Quick Reference: Railway CLI Commands

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link to existing project
railway link

# View logs
railway logs

# Run command in Railway environment
railway run <command>

# Open project in browser
railway open

# Check service status
railway status

# Deploy manually
railway up
```

---

## Quick Reference: Useful URLs

| Service | URL Pattern |
|---------|-------------|
| Railway Dashboard | https://railway.app/project/YOUR_PROJECT_ID |
| Backend API | https://your-backend.up.railway.app |
| Backend Docs | https://your-backend.up.railway.app/docs |
| Frontend | https://your-frontend.up.railway.app |
| Database (internal) | postgres.railway.internal:5432 |
| Database (public) | hopper.proxy.rlwy.net:PORT |

---

## Template Variables to Replace

When using this template for a new project, replace these placeholders:

| Placeholder | Replace With |
|-------------|--------------|
| `your-backend` | Your actual backend service name |
| `your-frontend` | Your actual frontend service name |
| `PASSWORD` | Your actual database password |
| `PORT` | Your actual database port |
| `sk-proj-xxx` | Your actual OpenAI API key |
| `yourdomain.com` | Your custom domain (if any) |

---

## Support

If you encounter issues:

1. Check Railway status: https://status.railway.app/
2. Railway documentation: https://docs.railway.app/
3. Railway Discord: https://discord.gg/railway

---

*Template created for Meuble de France Chatbot - January 2025*
