# MedSafeAI - Vercel Deployment Guide

## Overview

MedSafeAI is now deployed as an **integrated full-stack application on Vercel** with:
- **Frontend**: React/Vite app at `/` 
- **Backend**: Serverless Python functions at `/api`
- **Same domain**: No CORS issues, seamless integration

## What Changed

### ✅ Removed
- ❌ External Render backend dependency
- ❌ CORS configuration complexity
- ❌ Pydantic/compilation issues

### ✅ Added
- ✅ Backend deployed as Vercel serverless functions (`/api`)
- ✅ Frontend uses relative `/api` path (same domain)
- ✅ Lightweight dependencies (numpy, scikit-learn)
- ✅ Python 3.11 runtime configured in `vercel.json`

## Deployment Steps

### Step 1: Merge to Main Branch
```bash
# Go to GitHub PR and merge your branch to main
# Or locally:
git checkout main
git pull origin main
git merge v0/backend-deployment-update-7b2e09d0
git push origin main
```

### Step 2: Vercel Auto-Deploy
- Vercel will automatically detect the changes
- It will:
  1. Build the frontend (`npm run build` in `/frontend`)
  2. Deploy the backend functions (`/api/index.py`)
  3. Serve both from the same domain

### Step 3: Verify Deployment
Once deployed, visit: `https://itmed-safe-1fq77dxp8-adityaag5492045-6100s-projects.vercel.app`

Check the browser console for:
```
[MedSafeAI] API Base URL: /api
```

## Architecture

### File Structure
```
/
├── frontend/
│   ├── src/
│   │   ├── api.ts          # ✅ Uses `/api` as base URL
│   │   ├── App.tsx
│   │   └── ...
│   ├── vite.config.ts      # ✅ Updated for `/api`
│   └── package.json
│
├── api/
│   ├── index.py            # ✅ Vercel serverless function
│   └── requirements.txt     # ✅ Minimal dependencies
│
├── model/
│   └── artifacts/          # ML models loaded by API
│
├── data/
│   └── processed/          # Drug knowledge & interactions
│
└── vercel.json             # ✅ Configuration
```

### Request Flow
```
User Browser
    ↓
Vercel Frontend (React app)
    ↓
/api/predict    ← Same domain, no CORS
    ↓
Vercel Backend (Python function)
    ↓
ML Model + Drug DB
    ↓
Response → Frontend
```

## API Endpoints

All endpoints are served at `/api`:

- **GET `/api/health`** - Health check
- **GET `/api/search?q=drug_name`** - Search drug database
- **POST `/api/predict`** - Run ML risk prediction
  ```json
  {
    "drugs": ["aspirin", "ibuprofen"]
  }
  ```

## Environment Variables

No environment variables needed! The backend runs on the same Vercel project.

## Troubleshooting

### Frontend shows "Backend not responding"
1. Check browser DevTools → Network tab
2. Verify API calls go to `/api` (not external URL)
3. Restart Vercel deployment: Go to Vercel dashboard → Redeploy

### API returns 500 error
1. Check that model artifacts exist in `/model/artifacts/`
2. Verify `/data/processed/drug_knowledge.json` exists
3. Check Vercel function logs in dashboard

### "Model not loaded"
This is normal! The ML model loads on first request. Hit `/api/health` a few times.

## Performance Notes

- ✅ **Faster**: No cross-domain requests, same Vercel infrastructure
- ✅ **More Reliable**: No external dependencies or CORS issues
- ✅ **Scalable**: Vercel auto-scales serverless functions
- ✅ **Cold Start**: First request may take 3-5s (model loading), subsequent requests are fast

## Monitoring

Go to Vercel Dashboard:
1. **Functions** tab → See API usage and cold starts
2. **Logs** tab → View Python error messages
3. **Deployments** tab → Check build/deployment status

## Rolling Back

If something breaks:
```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Vercel will auto-deploy the revert
```

## Questions?

Check the AI-generated documentation in:
- `DEPLOYMENT.md` - General deployment guide
- `SETUP_CHECKLIST.md` - Step-by-step setup verification
- `vercel.json` - Vercel configuration reference

---

**Status**: ✅ Ready for Production

MedSafeAI is now a cohesive, single-domain application running on Vercel's infrastructure.
