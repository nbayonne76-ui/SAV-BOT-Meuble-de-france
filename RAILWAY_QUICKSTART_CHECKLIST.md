# Railway Deployment - Quick Start Checklist

## Step-by-Step Checklist for Deploying Your App

Use this checklist when deploying a new project to Railway.

---

## Phase 1: Railway Project Setup (5 min)

- [ ] Go to https://railway.app/
- [ ] Click "New Project" → "Empty Project"
- [ ] Name your project

---

## Phase 2: PostgreSQL Database (5 min)

- [ ] Click "+ New" → "Database" → "PostgreSQL"
- [ ] Wait for deployment
- [ ] Click on PostgreSQL service
- [ ] Go to "Variables" tab
- [ ] Copy and save the `DATABASE_URL`:

```
DATABASE_URL: _______________________________________________
```

- [ ] Go to "Settings" → "Networking"
- [ ] Enable "Public Networking" (for running migrations from local)
- [ ] Copy the public DATABASE_URL:

```
PUBLIC_DATABASE_URL: ________________________________________
```

---

## Phase 3: Backend Service (10 min)

### 3.1 Create Service
- [ ] Click "+ New" → "GitHub Repo"
- [ ] Select your backend repository
- [ ] Set Root Directory (if monorepo): `backend`

### 3.2 Configure Settings
- [ ] Go to "Settings" tab
- [ ] Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3.3 Add Environment Variables
Go to "Variables" tab and add:

| Variable | Value | Done |
|----------|-------|------|
| `DATABASE_URL` | (paste from PostgreSQL) | [ ] |
| `OPENAI_API_KEY` | `sk-proj-...` | [ ] |
| `PORT` | `8000` | [ ] |
| `NODE_ENV` | `production` | [ ] |
| `JWT_SECRET` | (generate strong secret) | [ ] |
| `SESSION_SECRET` | (generate strong secret) | [ ] |
| `LOG_LEVEL` | `info` | [ ] |
| `ALLOWED_ORIGINS` | (leave empty for now) | [ ] |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | [ ] |

### 3.4 Generate Domain
- [ ] Go to "Settings" → "Networking"
- [ ] Click "Generate Domain"
- [ ] Copy your backend URL:

```
BACKEND_URL: https://___________________________________.up.railway.app
```

### 3.5 Wait for Deployment
- [ ] Go to "Deployments" tab
- [ ] Wait for green checkmark
- [ ] Test: Open `https://your-backend.up.railway.app/docs`

---

## Phase 4: Frontend Service (10 min)

### 4.1 Create Service
- [ ] Click "+ New" → "GitHub Repo"
- [ ] Select your frontend repository
- [ ] Set Root Directory (if monorepo): `frontend`

### 4.2 Configure Settings
- [ ] Go to "Settings" tab
- [ ] Set Build Command: `npm install && npm run build`
- [ ] Set Start Command: `npm run preview` or `npx serve dist`

### 4.3 Add Environment Variables
Go to "Variables" tab and add:

| Variable | Value | Done |
|----------|-------|------|
| `VITE_API_URL` | (your backend URL) | [ ] |
| `VITE_WS_URL` | `wss://your-backend.up.railway.app` | [ ] |
| `NODE_ENV` | `production` | [ ] |

### 4.4 Generate Domain
- [ ] Go to "Settings" → "Networking"
- [ ] Click "Generate Domain"
- [ ] Copy your frontend URL:

```
FRONTEND_URL: https://___________________________________.up.railway.app
```

### 4.5 Wait for Deployment
- [ ] Go to "Deployments" tab
- [ ] Wait for green checkmark
- [ ] Test: Open your frontend URL in browser

---

## Phase 5: Connect Services (5 min)

### 5.1 Update Backend CORS
- [ ] Go to Backend service → "Variables"
- [ ] Update `ALLOWED_ORIGINS`:

```
ALLOWED_ORIGINS=https://your-frontend.up.railway.app
```

- [ ] Backend will automatically redeploy

### 5.2 Verify Connection
- [ ] Open frontend in browser
- [ ] Open browser Developer Tools (F12)
- [ ] Go to Console tab
- [ ] Check for CORS errors
- [ ] Test a feature that calls the backend API

---

## Phase 6: Database Migration (5 min)

If you need to run database migrations:

### Option A: From Local Machine

```bash
cd backend
python migrate_script.py "postgresql://postgres:PASSWORD@hopper.proxy.rlwy.net:PORT/railway"
```

### Option B: Via Railway CLI

```bash
railway login
railway link
railway run python migrate_script.py
```

---

## Phase 7: Final Verification

### Backend
- [ ] Service shows green status
- [ ] `/docs` endpoint works
- [ ] `/health` endpoint works (if exists)
- [ ] No errors in logs

### Frontend
- [ ] Service shows green status
- [ ] Website loads correctly
- [ ] No console errors
- [ ] Can communicate with backend

### Database
- [ ] Service shows green status
- [ ] Tables exist
- [ ] Data can be saved and retrieved

---

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Backend won't start | Check logs for error message |
| "Module not found" | Add package to requirements.txt |
| "DATABASE_URL required" | Add DATABASE_URL variable |
| CORS error | Add frontend URL to ALLOWED_ORIGINS |
| "Connection refused" | Use public DATABASE_URL |
| Frontend blank page | Check VITE_API_URL is correct |
| 404 on API calls | Check backend URL, no trailing slash |

---

## My Project Details

Fill in these details for your project:

```
Project Name: _______________________

PostgreSQL:
  - Internal URL: postgres.railway.internal:5432
  - Public URL: ________________________
  - Password: __________________________

Backend:
  - URL: https://______________________.up.railway.app
  - Port: 8000

Frontend:
  - URL: https://______________________.up.railway.app

Custom Domain (if any): _________________
```

---

## Time Estimate

| Phase | Time |
|-------|------|
| Project Setup | 5 min |
| PostgreSQL | 5 min |
| Backend | 10 min |
| Frontend | 10 min |
| Connect Services | 5 min |
| Database Migration | 5 min |
| **Total** | **~40 min** |

---

*Quick Start Checklist - Railway Deployment*
