# Testing the Backend API After Deployment

## Step 1: Wait for Deployment
1. Go to https://vercel.com
2. Click **MedSafeAI** project
3. Wait for deployment status to show **"Ready"** (green checkmark)
   - Currently: **Building** (should finish in 2-3 minutes)

## Step 2: Open Your App
Visit: https://med-safe-ai.vercel.app

## Step 3: Check Backend Connection
Open **Developer Tools** (F12) and go to **Console** tab

You should see:
```
[MedSafeAI] API Base URL: /api
```

## Step 4: Test Search
1. Type a drug name in the search box (e.g., **Aspirin**)
2. Look at **Network** tab in DevTools
3. You should see a request to `/api/search?q=aspirin` with:
   - Status: **200 OK**
   - Response: List of matching drugs

## Step 5: Test Risk Prediction
1. Select a drug from search results
2. Click "Check Risk"
3. In **Network** tab, you should see:
   - POST request to `/api/predict`
   - Status: **200 OK**
   - Response: Risk analysis with drugs, interactions, and explanations

## If Backend is Still Not Working

### Check 1: Console Errors
Look at **Console** tab for error messages like:
- `404 Not Found` → API endpoint issue
- `500 Server Error` → Backend crash
- `CORS error` → Cross-origin issue

### Check 2: Model Files
Go to Vercel project settings → Deployments tab → Click the latest deployment
- Look for "model/artifacts" in build output
- Should see "Built-in functions:" with `api/index.py`

### Check 3: Redeploy
1. Go to Vercel dashboard
2. Click MedSafeAI project
3. Click "..." (three dots) → **Redeploy**
4. Select "Redeploy without git changes"
5. Wait 2-3 minutes

### Check 4: Clear Vercel Cache
1. In Vercel dashboard
2. Click "Settings" → "Git"
3. Click "Clear Build Cache"
4. Go back and redeploy

## Expected Behavior When Working

✅ Frontend loads at med-safe-ai.vercel.app
✅ Can search for drugs
✅ Can select a drug and predict risk
✅ Shows:
   - Risk level (Low/Medium/High)
   - Risk score
   - Side effects
   - Drug interactions
   - SHAP-based explanation

## Endpoints Being Called

When everything works, these endpoints are called:

1. **Health Check** (automatic):
   ```
   GET /api/health
   ```

2. **Drug Search**:
   ```
   GET /api/search?q=aspirin
   Response: {"suggestions": ["aspirin", "aspirin-caffeine", ...]}
   ```

3. **Risk Prediction**:
   ```
   POST /api/predict
   Body: {"drugs": ["aspirin"]}
   Response: {
     "results": [...],
     "interactions": [...],
     "combined_risk": "Low"
   }
   ```

## Need Help?

If the backend still isn't working after following these steps:
1. Check the Vercel deployment logs for errors
2. Look at the API_FIX_SUMMARY.md in the repo
3. Verify model files are in git: `git ls-files | grep model/`
4. Check data files exist: `git ls-files | grep data/`
