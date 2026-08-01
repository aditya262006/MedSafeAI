# How to Merge and Deploy

## Step 1: Merge the Branch to Main (Using Git Commands)

Run these exact commands in your terminal:

```bash
cd /vercel/share/v0-project

# Step 1a: Make sure you're on the development branch
git checkout v0/backend-deployment-update-7b2e09d0

# Step 1b: Pull latest changes from this branch
git pull origin v0/backend-deployment-update-7b2e09d0

# Step 1c: Switch to main branch
git checkout main

# Step 1d: Pull latest changes from main
git pull origin main

# Step 1e: Merge the development branch into main
git merge v0/backend-deployment-update-7b2e09d0

# Step 1f: Push the merged changes back to GitHub
git push origin main
```

## Step 2: What Happens After You Push to Main

Once you run `git push origin main`:

1. **GitHub receives the push** - Your code is updated on GitHub
2. **Vercel detects the change** - Vercel automatically watches the main branch
3. **Vercel starts deploying** - It will:
   - Install dependencies
   - Build the frontend (React/Vite)
   - Prepare the API routes (Python)
   - Deploy everything to your domain

## Step 3: Check Deployment Status

### Option A: Check Vercel Dashboard
1. Go to https://vercel.com
2. Click on your project "medsafeai" (or whatever it's called)
3. You'll see the deployment happening in real-time
4. Wait for status to show "Ready" (green checkmark)

### Option B: Check Email
- Vercel will send you an email when deployment succeeds or fails

## Step 4: After Deployment Completes

Once Vercel shows "Ready":

1. Visit your app: https://med-safe-ai.vercel.app
2. Try searching for a drug
3. The app should:
   - Load the frontend (React UI)
   - Call the backend API via `/api` (NOT Render anymore)
   - Return drug data and predictions

## Troubleshooting

If it's still not working after deployment:

### Check 1: Open DevTools
- Press `F12` or right-click → "Inspect"
- Go to "Console" tab
- Look for errors

### Check 2: Check Network Calls
- In DevTools, go to "Network" tab
- Try searching for a drug
- Look for `/api/search?q=...` request
- It should show status `200` (success)

### Check 3: Check Deployment Logs
- Go to Vercel dashboard
- Click on your project
- Click "Deployments" tab
- Click the latest deployment
- Click "Logs" to see what happened

## If Something Goes Wrong

If you get errors during deployment, the most common reasons are:

1. **Python version mismatch** - Vercel uses Python 3.11
2. **Missing dependencies** - Check `api/requirements.txt`
3. **Import errors** - Check `api/index.py` syntax

Just reply with the error message and I'll fix it!

## Quick Summary of the 6 Git Commands:

```bash
cd /vercel/share/v0-project
git checkout v0/backend-deployment-update-7b2e09d0
git pull origin v0/backend-deployment-update-7b2e09d0
git checkout main
git pull origin main
git merge v0/backend-deployment-update-7b2e09d0
git push origin main
```

That's it! After step 6 (`git push origin main`), Vercel will automatically deploy everything.
