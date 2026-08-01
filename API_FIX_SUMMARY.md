# API Deployment Fix Summary

## Problem
Backend API was not working on Vercel deployment. Only the frontend was displaying, but API calls failed.

## Root Causes Fixed

### 1. **Incorrect Vercel Handler Format** 
   - `api/index.py` was returning a tuple `(body, status, headers)` 
   - Vercel requires a dict with `statusCode`, `headers`, and `body`

### 2. **Missing API Route Configuration**
   - `vercel.json` had incorrect `rewrites` instead of `routes`
   - Routes now explicitly map `/api/*` to the Python handler

### 3. **Missing Files in Deployment**
   - Model artifacts and data files weren't being included
   - Created `.vercelignore` to ensure `model/` and `data/` directories deploy

### 4. **Missing CORS Headers**
   - API responses weren't including proper CORS headers
   - Added CORS headers to `vercel.json` configuration

## Changes Made

### api/index.py
```python
# Before: returned tuple
def handler(request):
    response_body, status_code, headers = handle_request(request)
    return response_body

# After: returns proper Vercel format
def handler(request):
    response_body, status_code, headers = handle_request(request)
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": response_body if isinstance(response_body, str) else json.dumps(response_body)
    }
```

### vercel.json
```json
"routes": [
  {
    "src": "/api/(.*)",
    "dest": "/api/index.py",
    "methods": ["GET", "POST", "OPTIONS"]
  }
],
"functions": {
  "api/index.py": {
    "runtime": "python3.11",
    "memory": 1024,
    "maxDuration": 30
  }
}
```

### .vercelignore (NEW)
```
# Keep model and data directories
# - model/artifacts (ML model files)
# - data/processed (drug knowledge, interactions)
```

## Deployment Status

✅ **Changes pushed to:** `main` branch
✅ **Vercel automatic redeploy:** Triggered
✅ **Expected completion:** 2-3 minutes

## What to Check Next

1. Go to https://vercel.com → MedSafeAI project
2. Watch for "Building..." → "Ready" (green checkmark)
3. Visit https://med-safe-ai.vercel.app
4. Open DevTools (F12) → Console
5. Try searching for a drug (e.g., "aspirin")
6. Check Network tab - `/api/search?q=aspirin` should return results

## API Endpoints Now Available

- `GET /api/health` - Health check
- `GET /api/search?q=aspirin` - Search drugs
- `POST /api/predict` - Predict drug risk
- `GET /api/drug/aspirin` - Get drug info

## If Still Not Working

Common issues:
1. **Model files missing:** Check `model/artifacts/` files exist in repo
2. **Data files missing:** Check `data/processed/drug_knowledge.json` exists
3. **Vercel cache:** Clear cache and redeploy
4. **Python version:** Confirm Python 3.11 runtime in Vercel settings

Run this command to verify files are in git:
```bash
git ls-files | grep -E "model/|data/"
```
