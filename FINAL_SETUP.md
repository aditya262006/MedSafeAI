# MedSafeAI - Final Setup Instructions

## Problem Fixed ✅
Exit code 127 on Render was because it couldn't find `python` command.
**Solution**: Changed to `python3` which is available on Render.

---

## STEP 1: Re-Deploy on Render

### Option A: Use Render.yaml (Recommended)
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repo: `aditya262006/MedSafeAI` (main branch)
4. Render will auto-detect `render.yaml` and use it automatically
5. Click **"Deploy"** and wait 2-3 minutes

### Option B: Manual Deploy
If Render doesn't auto-detect render.yaml:

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub: `aditya262006/MedSafeAI`
4. Fill in:
   - **Name**: `medsafeai-backend`
   - **Build Command**: `pip install -r render_requirements.txt`
   - **Start Command**: `python3 render_backend.py`
   - **Plan**: Free
5. Click **"Deploy"**

### Watch for Success
- Status should go: `Queued` → `Building` → `Running` (green)
- If it shows red with "Exit code 127" again, check that start command is exactly: `python3 render_backend.py`

**Copy the Render URL** (looks like: `https://medsafeai-backend-xxxx.onrender.com`)

---

## STEP 2: Update Vercel Frontend

Once Render shows "Running" (green):

1. Go to https://vercel.com/dashboard
2. Click on **MedSafeAI** project
3. Go to **Settings** → **Environment Variables**
4. Find or create `VITE_API_URL` and set it to:
   ```
   https://your-render-url.onrender.com
   ```
   (Replace with actual Render URL)

5. Click **"Save"**
6. **Redeploy**: Click your project → **"Deployments"** → **"Redeploy"** on latest commit

---

## STEP 3: Test the App

1. Wait for Vercel to show "Ready" (green checkmark)
2. Visit: https://med-safe-ai.vercel.app
3. Search for a drug: type "aspirin"
4. Click "Predict Risk"
5. Should show: drug info, risk level, and any interactions

**If it works**: You're done! 🎉

**If frontend can't connect to backend**:
- Open DevTools (F12) → Console
- Look for CORS errors
- Double-check VITE_API_URL in Vercel is correct
- Verify Render backend is still running (check dashboard)

---

## Endpoints Available

Once deployed, test these:

```
GET  https://your-render-url.onrender.com/health
GET  https://your-render-url.onrender.com/api/search?q=aspirin
POST https://your-render-url.onrender.com/api/predict
     Body: {"drugs": ["aspirin", "warfarin"]}
GET  https://your-render-url.onrender.com/api/drug/aspirin
```

---

## Summary

- **Backend**: Render (render_backend.py)
- **Frontend**: Vercel (med-safe-ai.vercel.app)
- **Fixed**: python3 command, PORT binding
- **Ready**: No more exit 127 errors

Follow the 3 steps above and it will work!
