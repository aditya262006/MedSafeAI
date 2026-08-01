# MedSafeAI Deployment Guide

This guide covers deploying MedSafeAI backend to Render and frontend to Vercel.

## Backend Deployment (Render)

### Prerequisites
- Render account (https://render.com)
- GitHub repository connected

### Deployment Steps

1. **Connect GitHub Repository to Render**
   - Go to https://dashboard.render.com
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository

2. **Configure Render Service**
   - **Name**: `medsafeai-backend`
   - **Environment**: Python 3.11
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
   - **Publish Port**: 8000

3. **Environment Variables** (if needed)
   - No additional environment variables required for basic setup

4. **Deploy**
   - Render will automatically deploy when you push to your repository
   - Your backend will be available at: `https://medsafeai-iep6.onrender.com`

### Backend Health Check
```bash
curl https://medsafeai-iep6.onrender.com/health
```

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account (https://vercel.com)
- GitHub repository connected
- Backend URL (from Render deployment above)

### Deployment Steps

1. **Set Environment Variables in Vercel**
   - Go to your Vercel project settings: https://vercel.com/dashboard
   - Navigate to "Settings" → "Environment Variables"
   - Add the following:
     ```
     VITE_API_URL=https://medsafeai-iep6.onrender.com
     ```

2. **Build Configuration**
   - Root Directory: `.` (project root)
   - Build Command: `cd frontend && npm run build`
   - Output Directory: `frontend/dist`
   - Install Command: `npm install` (auto-configured)

3. **Redeploy**
   - Go to "Deployments" tab
   - Click the three dots (⋯) on the latest deployment
   - Select "Redeploy"

### Frontend Access
- Your app will be available at: `https://itmed-safe-1fq77dxp8-adityaag5492045-6100s-projects.vercel.app`

## Troubleshooting

### Backend Connection Issues

**Problem**: Frontend shows "Failed to connect to backend"

**Solution**:
1. Verify backend is running: `curl https://medsafeai-iep6.onrender.com/health`
2. Check browser console for CORS errors
3. Ensure `VITE_API_URL` environment variable is set correctly in Vercel
4. Verify Render service status in dashboard

### CORS Errors

The backend CORS is configured to accept requests from:
- `http://localhost:5173` (local Vite dev)
- `http://localhost:3000` (local Next.js dev)
- `https://*.vercel.app` (all Vercel deployments)
- `https://medsafeai-iep6.onrender.com` (Render backend itself)

If you're getting CORS errors:
1. Check that your frontend domain matches one of the allowed origins
2. Verify the `VITE_API_URL` matches the backend URL exactly

### Build Issues

**Check build logs**:
1. Vercel: Go to Deployments → Click failed build → View logs
2. Render: Go to your service → Logs tab

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Then visit: http://localhost:5173

## Production Checklist

- [ ] Backend deployed to Render
- [ ] Backend health check passing
- [ ] Frontend `VITE_API_URL` environment variable set in Vercel
- [ ] Frontend redeployed after env var change
- [ ] CORS errors resolved
- [ ] Test full drug safety prediction flow
