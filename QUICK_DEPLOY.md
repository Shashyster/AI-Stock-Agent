# 🚀 Quick Deploy Guide - Get Your Site Live in 5 Minutes!

## Step 1: Push to GitHub (if not already done)

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Render (Easiest - Free!)

1. **Go to https://render.com** and sign up (use GitHub login)

2. **Click "New +" → "Web Service"**

3. **Connect your GitHub repository**

4. **Configure:**
   - **Name**: `stock-info-app` (or any name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: `Free`

5. **Click "Create Web Service"**

6. **Wait 5-10 minutes** for deployment

7. **Done!** Your site is live at: `https://your-app-name.onrender.com`

---

## Alternative: Deploy to Railway

1. **Go to https://railway.app** and sign up

2. **Click "New Project" → "Deploy from GitHub repo"**

3. **Select your repository**

4. **Railway auto-detects everything!** Just wait for deployment.

5. **Your site**: `https://your-app-name.up.railway.app`

---

## ✅ That's It!

Your stock information website is now live on the internet! Share the URL with anyone.

### Notes:
- Free tiers may sleep after inactivity (takes a few seconds to wake up)
- First deployment takes 5-10 minutes
- Subsequent updates deploy automatically when you push to GitHub

### Need Help?
Check `DEPLOYMENT_GUIDE.md` for detailed instructions and troubleshooting.
