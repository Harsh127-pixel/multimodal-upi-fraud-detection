# 🚀 FraudGuard Deployment Guide

Follow these steps to get your full-stack application live.

---

## 🏗️ PART 1: Deploy Backend (Railway)
*Railway will host your FastAPI code, PostgreSQL database, and Redis cache.*

1.  **Login to [Railway.app](https://railway.app)** using your GitHub account.
2.  **Create New Project**:
    *   Click `+ New Project`.
    *   Select `Deploy from GitHub repo`.
    *   Choose your `multimodal-upi-fraud-detection` repository.
3.  **Configure Service**:
    *   Railway will ask for the root folder. Select **`fraudguard-backend`**.
    *   Go to the **Variables** tab and click `+ New Variable`.
    *   Add `PORT` = `8000`.
4.  **Add Databases**:
    *   In the project canvas, click `+` → **Database** → **PostgreSQL**.
    *   Click `+` → **Database** → **Redis**.
5.  **Link Everything**:
    *   Railway automatically injects `DATABASE_URL` and `REDIS_URL` into your backend service if they are in the same project. Double-check the **Variables** tab of your `backend` service to ensure they are there.
6.  **Get your API URL**:
    *   Go to **Settings** → **Public Networking**.
    *   Click **Generate Domain**.
    *   Copy the URL (e.g., `https://fraudguard-production.up.railway.app`). **This is your `API_URL`.**

---

## 🎨 PART 2: Deploy Frontend (Vercel)
*Vercel will host your Quasar/Vue 3 web application.*

1.  **Login to [Vercel.com](https://vercel.com)** using your GitHub account.
2.  **Import Project**:
    *   Click `Add New` → `Project`.
    *   Import your `multimodal-upi-fraud-detection` repository.
3.  **Project Settings**:
    *   **Root Directory**: Click `Edit` and select **`fraudguard-frontend`**.
    *   **Framework Preset**: Select `Other` or `Vite` (Vercel should detect this automatically).
    *   **Build & Output Settings**:
        *   Build Command: `npx quasar build`
        *   Output Directory: `dist/spa`
4.  **Environment Variables**:
    *   Add a new variable:
        *   **Name:** `API_URL`
        *   **Value:** `https://your-railway-url.up.railway.app/api` (Make sure to add **`/api`** at the end).
5.  **Deploy**:
    *   Click **Deploy**. In ~2 minutes, your frontend will be live at a `.vercel.app` URL!

---

## ✅ Post-Deployment Checklist

1.  **Frontend Check**: Open your Vercel URL. You should see the login page.
2.  **API Check**: Open `https://your-railway-url.up.railway.app/docs`. You should see the FastAPI Swagger UI.
3.  **Database Migration**:
    *   If the app crashes on the first login, Railway might need you to run migrations. In the Railway dashboard, go to your backend service → **Deployments** → **Details** → **CMD**. You can trigger a one-time command: `alembic upgrade head`.

---

## 📱 Pro-Tip: Sharing the App
Since your portfolio is at `harshbhojwani.in`, you can add a link to your portfolio that says:
> **"Check out FraudGuard (Live Demo)"** → Link to your Vercel URL.

This keeps your professional presence while showing the project!
