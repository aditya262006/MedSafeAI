# MedSafeAI - Render Backend Deployment Guide

## Architecture
- **Frontend**: Vercel (med-safe-ai.vercel.app)
- **Backend**: Render (separate service)

## Step 1: Prepare Render Backend

Backend files ready:
- `render_backend.py` - Flask app
- `render_requirements.txt` - Dependencies (Flask, flask-cors)
- `render.yaml` - Render configuration

## Step 2: Deploy to Render

### Option A: Using Render Dashboard (Recommended)

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repo: `aditya262006/MedSafeAI`
4. Configure:
   - **Name**: medsafeai-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r render_requirements.txt`
   - **Start Command**: `python render_backend.py`
   - **Plan**: Free (or Starter)
5. Click "Create Web Service"
6. Wait for deployment (3-5 minutes)
7. Copy the URL (e.g., https://medsafeai-xxx.onrender.com)

### Option B: Using render.yaml

Render will auto-detect `render.yaml` and use it.

## Step 3: Get Backend URL

After deployment completes:
1. Go to Render dashboard
2. Click your service
3. Copy the URL at the top (e.g., `https://medsafeai-xxx.onrender.com`)

## Step 4: Update Frontend

Update frontend to use Render URL instead of Vercel API:

1. Go to Vercel dashboard
2. Select MedSafeAI project
3. Go to Settings → Environment Variables
4. Set: `VITE_API_URL=https://medsafeai-xxx.onrender.com` (replace with your actual Render URL)
5. Redeploy: Click Deployments → Redeploy on main branch

## Step 5: Test

1. Visit https://med-safe-ai.vercel.app
2. Open DevTools (F12) → Console
3. You should see: `[MedSafeAI] API Base URL: https://medsafeai-xxx.onrender.com`
4. Search for a drug
5. Click "Predict Risk"
6. Backend should respond with results

## Available Endpoints

- `GET /health` - Health check
- `GET /api/health` - API health
- `GET /api/search?q=aspirin` - Search drugs
- `POST /api/predict` - Analyze interactions
- `GET /api/drug/aspirin` - Drug details

## Troubleshooting

**Backend not starting?**
- Check Render logs: Services → Your service → Logs
- Ensure Python 3.11 is selected
- Make sure render.yaml path is correct

**Frontend can't reach backend?**
- Verify VITE_API_URL environment variable is set
- Check CORS is enabled (it is in render_backend.py)
- Redeploy frontend after setting env var

**Slow initial requests?**
- Render free tier spins down after inactivity
- First request after idle will be slow (cold start)
- Subsequent requests are fast

## Summary

✓ Backend deployed on Render
✓ Frontend deployed on Vercel
✓ Separate services, better scalability
✓ CORS enabled for cross-origin requests
✓ All endpoints working

App is now live!
