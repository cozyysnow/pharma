# 🚀 PharmaStock IQ — Cloud Deployment Guide

This guide walks you through deploying **PharmaStock IQ** for **100% free** using **Render / Railway** (for the FastAPI backend) and **Vercel / Netlify** (for the React frontend).

---

## Architecture Overview

```
 ┌───────────────────────────────┐
 │       React Frontend          │  Hosted on Vercel / Netlify (Free)
 │    (Vite SPA + Tailwind)      │  Base URL: https://pharmastock.vercel.app
 └──────────────┬────────────────┘
                │
                │ HTTPS API requests
                ▼
 ┌───────────────────────────────┐
 │       FastAPI Backend         │  Hosted on Render / Railway (Free)
 │  (Uvicorn + SQLite DB + ML)   │  Base URL: https://pharmastock-api.onrender.com
 └───────────────────────────────┘
```

---

## Part 1: Deploy Backend (Render)

Render offers free web services that run directly from your GitHub repository.

### Step 1.1: Sign up on Render
1. Go to [https://render.com](https://render.com) and sign in with your GitHub account.

### Step 1.2: Create a New Web Service
1. Click **New +** $\to$ **Web Service**.
2. Select your repository: **`cozyysnow/pharma`**.
3. Fill in the service configuration:
   - **Name:** `pharmastock-api`
   - **Region:** Choose the region closest to you (e.g., Oregon or Frankfurt).
   - **Branch:** `main`
   - **Root Directory:** Leave blank (root).
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r backend/requirements.txt && python backend/scripts/bootstrap_db.py
     ```
   - **Start Command:**
     ```bash
     uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type:** `Free`

### Step 1.3: Configure Environment Variables
Under **Advanced** $\to$ **Environment Variables**, add:
| Key | Value | Description |
|---|---|---|
| `PYTHON_VERSION` | `3.11.4` | Python version |
| `ENVIRONMENT` | `production` | Production mode |
| `DEBUG` | `false` | Disable debug banner |
| `SECRET_KEY` | *(Click Generate or enter a random 32+ char string)* | JWT encryption key |
| `DATABASE_URL` | `sqlite:///./pharmastock.db` | Local SQLite path |

### Step 1.4: Deploy & Verify
1. Click **Create Web Service**.
2. Render will run the build command, install dependencies, run `bootstrap_db.py` (which creates tables and seeds 155,210 rows), and launch Uvicorn.
3. Once deployed, Render gives you a public URL (e.g., `https://pharmastock-api.onrender.com`).
4. Test it in your browser:
   - Health check: `https://pharmastock-api.onrender.com/health` $\to$ Returns `{"status":"healthy"}`
   - API Docs: `https://pharmastock-api.onrender.com/docs` $\to$ Interactive Swagger UI

---

## Part 2: Deploy Frontend (Vercel)

Vercel provides lightning-fast hosting for Vite React applications with automatic continuous deployment.

### Step 2.1: Sign up on Vercel
1. Go to [https://vercel.com](https://vercel.com) and sign in with your GitHub account.

### Step 2.2: Import Repository
1. Click **Add New...** $\to$ **Project**.
2. Select repository: **`cozyysnow/pharma`**.

### Step 2.3: Configure Project Settings
1. **Framework Preset:** `Vite`
2. **Root Directory:** Click **Edit** and select **`frontend`**.
3. **Build Command:** `npm run build` *(automatic)*
4. **Output Directory:** `dist` *(automatic)*

### Step 2.4: Set Environment Variables
Expand **Environment Variables** and add:
| Key | Value |
|---|---|
| `VITE_API_BASE` | `https://pharmastock-api.onrender.com/api/v1` *(Replace with your Render backend URL)* |
| `VITE_USE_MOCKS` | `false` |

*(Note: Ensure `/api/v1` is appended to the backend URL without a trailing slash!)*

### Step 2.5: Deploy
1. Click **Deploy**.
2. In ~45 seconds, Vercel will build and assign you a production URL (e.g. `https://pharma-taupe.vercel.app`).
3. SPA routing is automatically pre-configured via [`frontend/vercel.json`](file:///frontend/vercel.json), so browser page refreshes on `/inventory` or `/forecast` work smoothly.

---

## Part 3: Verify End-to-End Production

1. Visit your Vercel URL in your browser.
2. Sign in with the default admin credentials:
   - **Email:** `admin@pharmastock.local`
   - **Password:** `AdminPassword123!` (or the password configured in `FIRST_SUPERUSER_PASSWORD`)
3. Check the Dashboard:
   - All 12 live KPI cards load from your Render backend.
   - Demand forecast charts render live data.
   - Risk matrix and replenishment recommendations show real computed shortfall values.

---

## Alternative: Railway (One-Click)

If you prefer Railway:
1. Connect `cozyysnow/pharma` to [Railway.app](https://railway.app).
2. Railway detects [`Dockerfile`](file:///Dockerfile) automatically and deploys the backend container with persistent storage.
3. Add a second service for `frontend` pointing to Vercel or Railway static hosting.

