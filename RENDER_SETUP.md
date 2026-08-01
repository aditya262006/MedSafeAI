# Render Backend Setup Guide

This guide walks you through setting up the MedSafeAI backend on Render.

## Quick Start

### Option 1: Using render.yaml (Recommended)

The project includes a `render.yaml` file with pre-configured settings.

1. Push your code to GitHub:
   ```bash
   git push origin main
   ```

2. Go to https://dashboard.render.com

3. Click **"New +"** → **"Web Service"**

4. **Connect GitHub**: 
   - Select your GitHub repository (aditya262006/MedSafeAI)
   - Authorize if prompted

5. **Verify Configuration**:
   - Service name will auto-populate from `render.yaml`
   - Build and start commands are pre-configured
   - Click **"Create Web Service"**

6. **Wait for Deployment**:
   - Render will build and deploy automatically
   - Watch the deploy logs for any errors
   - You'll see a green checkmark when done

7. **Test Your Backend**:
   ```bash
   curl https://medsafeai-iep6.onrender.com/health
   ```

### Option 2: Manual Configuration

If `render.yaml` isn't picked up:

1. Create new Web Service on Render
2. Configure these settings:

   | Setting | Value |
   |---------|-------|
   | **Name** | medsafeai-backend |
   | **Environment** | Python 3 |
   | **Region** | Oregon (or closest to you) |
   | **Branch** | main |
   | **Build Command** | `pip install -r backend/requirements.txt` |
   | **Start Command** | `uvicorn backend.main:app --host 0.0.0.0 --port 8000` |
   | **Plan** | Free (or Starter) |

3. Click **"Create Web Service"**

## Backend Structure

```
backend/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
└── [data/model/]       # Model artifacts loaded at startup
```

## Available Endpoints

- **GET `/health`** - Health check
- **GET `/search?q=...`** - Drug search autocomplete
- **POST `/predict`** - Predict drug safety risk
- **GET `/drug/{name}`** - Get drug information

## Troubleshooting

### Build Fails: "No such file or directory"

**Cause**: Render can't find `requirements.txt`

**Fix**: 
- Ensure path is correct: `pip install -r backend/requirements.txt`
- Check your repository structure has `backend/requirements.txt` at root level

### Service Crashes After Deploy

**Check logs**: Go to your service → Logs tab

**Common issues**:
1. Missing model artifacts in `model/artifacts/`
2. Python version incompatibility
3. Missing environment variables

### Connection Timeout

**If frontend can't reach backend**:
1. Verify service is running (green status indicator)
2. Check health endpoint: `curl https://[service-url]/health`
3. Ensure `VITE_API_URL` in Vercel matches exactly

## Environment Variables

No additional environment variables are required for the basic setup.

If you need to configure logging or other options, add them via Render dashboard:
- Go to service settings
- Add environment variable
- Redeploy

## Monitoring

- **Logs**: Check Build & Deploy logs for errors
- **Status**: Green indicator means healthy
- **Metrics**: View CPU, memory, and request counts

## Cost

- **Free Tier**: Limited availability (service spins down after inactivity)
- **Starter Plan**: $7/month for always-on service

For production, consider Starter or higher plan.

## Next Steps

1. ✅ Backend deployed to Render
2. ⏭️ Set `VITE_API_URL` in Vercel environment variables
3. ⏭️ Redeploy frontend on Vercel
4. ⏭️ Test connection in browser console

See [DEPLOYMENT.md](./DEPLOYMENT.md) for frontend setup.
