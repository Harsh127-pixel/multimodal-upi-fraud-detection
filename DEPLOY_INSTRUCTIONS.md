# 🚀 FraudGuard Deployment Guide

Follow these steps to get your full-stack application live.

---

## 🏗️ PART 1: Deploy Backend (Render)
*Render will host your FastAPI code, PostgreSQL database, and Redis cache.*

1.  **Login to [Render.com](https://render.com)** using your GitHub account.
2.  **Create New Blueprint Instance**:
    *   Click `New` → `Blueprint`.
    *   Connect your `multimodal-upi-fraud-detection` repository.
    *   Render will detect the `render.yaml` file.
3.  **Configure Service**:
    *   Give it a name (e.g., `fraudguard`).
    *   Click **Approve**.
    *   *Note: Render Redis requires a paid plan (starts at $7/mo). If you want a free Redis, you can use [Upstash](https://upstash.com) and manually set the `REDIS_URL` in Render's dashboard.*
4.  **Database Migration**:
    *   Render will automatically run `alembic upgrade head` as part of the Docker build (see `Dockerfile`).
5.  **Get your API URL**:
    *   Once the `backend` service is live, copy its URL (e.g., `https://fraudguard-backend.onrender.com`). **This is your `API_URL`.**

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
        *   **Value:** `https://your-render-url.onrender.com/api` (Make sure to add **`/api`** at the end).
5.  **Deploy**:
    *   Click **Deploy**. In ~2 minutes, your frontend will be live at a `.vercel.app` URL!

---

## ✅ Post-Deployment Checklist

1.  **Frontend Check**: Open your Vercel URL. You should see the login page.
2.  **API Check**: Open `https://your-render-url.onrender.com/docs`. You should see the FastAPI Swagger UI.
3.  **Database Migration**:
    *   If the app crashes on the first login, Render might need you to run migrations manually if the automatic one failed. In the Render dashboard, go to your backend service → **Shell** and run: `alembic upgrade head`.

---

## 📱 Pro-Tip: Sharing the App
Since your portfolio is at `harshbhojwani.in`, you can add a link to your portfolio that says:
> **"Check out FraudGuard (Live Demo)"** → Link to your Vercel URL.

This keeps your professional presence while showing the project!
