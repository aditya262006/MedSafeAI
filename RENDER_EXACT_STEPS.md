# EXACT RENDER DEPLOYMENT STEPS - GUARANTEED TO WORK

## STOP - Delete Old Deployment First

1. Go to https://dashboard.render.com
2. Click on your old **medsafeai-backend** service
3. Click **"Settings"** (bottom right)
4. Scroll down → Click **"Delete Web Service"**
5. Type the name to confirm
6. Wait 30 seconds

---

## DEPLOY NEW VERSION - STEP BY STEP

### Step 1: Create New Service
1. Go to https://dashboard.render.com
2. Click **"New +"** button
3. Select **"Web Service"**

### Step 2: Connect GitHub
1. Click **"Connect a repository"**
2. Search for: `aditya262006/MedSafeAI`
3. Click the repo
4. Click **"Connect"**

### Step 3: Configure Service
Copy EXACTLY these settings:

```
Name: medsafeai-backend
Environment: Python 3
Region: Oregon (or closest to you)
Branch: main
Root Directory: (leave empty)
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
Plan: Free
```

**IMPORTANT: Use `gunicorn app:app` as Start Command, NOT `python app.py`**

### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait 3-5 minutes
3. Watch the logs - should say "Running"
4. Copy the URL (looks like: `https://medsafeai-backend-xxxx.onrender.com`)

### Step 5: Test Backend (Optional)
Visit: `https://your-render-url/health`
Should show: `{"status": "healthy", "drugs": 10}`

---

## UPDATE VERCEL FRONTEND

### Step 1: Go to Vercel
1. Visit https://vercel.com/dashboard
2. Click **MedSafeAI** project

### Step 2: Set Environment Variable
1. Click **"Settings"** (top menu)
2. Click **"Environment Variables"** (left sidebar)
3. Look for **`VITE_API_URL`**
4. Click to edit it
5. Change value to: `https://your-render-url` (the URL from Step 4 above)
6. Click **"Save"**

### Step 3: Redeploy Frontend
1. Click **"Deployments"** (top menu)
2. Click the first/top deployment
3. Click **"Redeploy"** button (bottom right)
4. Wait 1-2 minutes for "Ready" status

---

## TEST EVERYTHING

1. Visit: https://med-safe-ai.vercel.app
2. Search for "aspirin"
3. Click "Predict Risk"
4. Should show results from backend

---

## If Still Getting Errors

Check Render logs:
1. Go to https://dashboard.render.com
2. Click **medsafeai-backend**
3. Click **"Logs"** tab
4. Look for errors

If you see:
- "Exit Code 127" = Wrong start command
- "ModuleNotFoundError" = Missing package in requirements.txt
- "Connection refused" = Frontend URL is wrong

Let me know what error you see!
