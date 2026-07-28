# MedSafeAI Setup Checklist

Follow these steps to complete the Render backend and Vercel frontend setup.

## Step 1: Prepare Your Repository ✅ (Complete)

- [x] Backend CORS updated to accept Vercel domains
- [x] render.yaml created for automated deployment
- [x] vercel.json created for build configuration
- [x] API client improved with error handling
- [x] Deployment guides created

## Step 2: Deploy Backend to Render

**Time Required**: ~5-10 minutes

### 2.1 Create Render Service
- [ ] Go to https://dashboard.render.com
- [ ] Click "New +" → "Web Service"
- [ ] Connect your GitHub repository: `aditya262006/MedSafeAI`
- [ ] Authorize GitHub connection if prompted

### 2.2 Verify Auto-Configuration
Render should auto-detect `render.yaml` with these settings:
- [ ] Service name: `medsafeai-backend`
- [ ] Environment: Python 3.11
- [ ] Build Command: `pip install -r backend/requirements.txt`
- [ ] Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
- [ ] Region: Oregon (or your preference)

### 2.3 Deploy
- [ ] Click "Create Web Service"
- [ ] Wait for build to complete (~2-3 minutes)
- [ ] Look for green checkmark indicating successful deploy
- [ ] Note your backend URL (should be https://medsafeai-iep6.onrender.com)

### 2.4 Test Backend
```bash
curl https://medsafeai-iep6.onrender.com/health
```
- [ ] Should return: `{"status": "healthy", "model_loaded": ..., ...}`

## Step 3: Configure Vercel Frontend

**Time Required**: ~5 minutes

### 3.1 Set Environment Variables
- [ ] Go to your Vercel project: https://vercel.com/dashboard
- [ ] Click on the project "itmed-safe-1fq77dxp8-adityaag5492045-6100s-projects"
- [ ] Go to "Settings" → "Environment Variables"
- [ ] Add new variable:
  - **Name**: `VITE_API_URL`
  - **Value**: `https://medsafeai-iep6.onrender.com`
- [ ] Save environment variable
- [ ] Select "Production" environment (at minimum)

### 3.2 Redeploy Frontend
- [ ] Go to "Deployments" tab
- [ ] Find your latest deployment
- [ ] Click the three dots (⋯)
- [ ] Select "Redeploy"
- [ ] Wait for build to complete

### 3.3 Verify Deployment
- [ ] Visit: https://itmed-safe-1fq77dxp8-adityaag5492045-6100s-projects.vercel.app
- [ ] Open browser DevTools (F12)
- [ ] Check console for any errors
- [ ] Look for `[MedSafeAI] API Base URL: https://medsafeai-iep6.onrender.com`

## Step 4: Test Full Integration

**Time Required**: ~5 minutes

### 4.1 Test Drug Search
- [ ] Go to your Vercel app
- [ ] Try searching for a drug (e.g., "aspirin")
- [ ] Should see search suggestions appearing

### 4.2 Test Risk Prediction
- [ ] Select a drug or add it manually
- [ ] Click "Check Safety"
- [ ] Should see risk analysis with SHAP explanations
- [ ] No CORS errors in console

### 4.3 Check Console Logs
- [ ] Open DevTools Console (F12)
- [ ] Should NOT see any errors about:
  - "CORS"
  - "Failed to fetch"
  - "Cannot connect to"
- [ ] Should see: `[MedSafeAI] API Base URL: https://medsafeai-iep6.onrender.com`

## Troubleshooting Guide

### Issue: "Failed to connect to backend"

**Check 1**: Is the backend running?
```bash
curl https://medsafeai-iep6.onrender.com/health
```
- If this fails, check Render service status
- Go to Render dashboard → Logs tab
- Look for deployment errors

**Check 2**: Is VITE_API_URL set correctly?
- Vercel Dashboard → Settings → Environment Variables
- Should be exactly: `https://medsafeai-iep6.onrender.com`
- After changing, redeploy frontend

**Check 3**: Browser Console Errors?
- Open DevTools (F12)
- Check Console tab for specific error messages
- Common issues:
  - ❌ Mixed Content (https frontend → http backend) - Update VITE_API_URL
  - ❌ CORS errors - Check backend CORS configuration
  - ❌ 404 errors - Check endpoint paths match

### Issue: CORS Errors in Console

**Solution**:
1. Backend should already accept your Vercel domain
2. Verify `VITE_API_URL` matches exactly
3. Check for typos in domain name
4. If custom domain used, add to backend CORS in `backend/main.py`

### Issue: 502 or Service Unavailable

**Render Backend Issue**:
- Go to Render Dashboard
- Check service status (should be "Running")
- Check Logs tab for errors
- Service may be starting up (first request can take 30s)

## Verifying Everything Works

Open browser console and run:

```javascript
// Check API URL
console.log('API URL:', import.meta.env.VITE_API_URL);

// Test backend connection
fetch('https://medsafeai-iep6.onrender.com/health')
  .then(r => r.json())
  .then(data => console.log('✅ Backend Connected:', data))
  .catch(err => console.error('❌ Connection Failed:', err.message));
```

## Success Indicators ✅

You'll know everything is working when:
1. ✅ No CORS errors in console
2. ✅ Drug search returns suggestions
3. ✅ Risk predictions return full analysis
4. ✅ SHAP explanations display correctly
5. ✅ All requests complete in <5 seconds

## Next Steps

- [ ] Share the app URL with others: https://itmed-safe-1fq77dxp8-adityaag5492045-6100s-projects.vercel.app
- [ ] Monitor Render service health
- [ ] Consider upgrading to paid plan for production

## Support

If you encounter issues:
1. Check this checklist first
2. Review DEPLOYMENT.md for detailed guides
3. Check Render service logs
4. Check Vercel deployment logs
5. Open browser DevTools (F12) for error messages

---

**Last Updated**: July 28, 2026
**Status**: Ready for deployment
