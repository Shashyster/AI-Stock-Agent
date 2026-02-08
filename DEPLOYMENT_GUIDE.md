# 🚀 Deployment Guide: Publishing Your Stock Information Website

This guide will help you publish your Flask stock information web app to the internet so anyone can access it!

## 📋 Table of Contents
1. [Quick Deploy Options](#quick-deploy-options)
2. [Option 1: Render (Recommended - Free)](#option-1-render-recommended---free)
3. [Option 2: Railway](#option-2-railway)
4. [Option 3: Fly.io](#option-3-flyio)
5. [Option 4: PythonAnywhere](#option-4-pythonanywhere)
6. [Option 5: AWS/Cloud Platforms](#option-5-awscloud-platforms)
7. [Pre-Deployment Checklist](#pre-deployment-checklist)

---

## Quick Deploy Options

### 🎯 Best for Beginners (Free):
- **Render** - Easiest, free tier available
- **Railway** - Simple, $5/month credit
- **PythonAnywhere** - Free tier for beginners

### 🎯 Best for Production:
- **Fly.io** - Great performance, free tier
- **AWS App Runner** - Scalable, pay-as-you-go
- **DigitalOcean App Platform** - Simple, $5/month

---

## Option 1: Render (Recommended - Free)

### Why Render?
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Easy deployment from GitHub
- ✅ Auto-deploys on git push
- ✅ No credit card required for free tier

### Steps:

1. **Prepare your code:**
   - Make sure your code is in a Git repository (GitHub, GitLab, or Bitbucket)
   - If not, create one:
     ```bash
     git init
     git add .
     git commit -m "Initial commit"
     git remote add origin YOUR_GITHUB_REPO_URL
     git push -u origin main
     ```

2. **Create a `render.yaml` file** (already created for you):
   - This file configures your deployment

3. **Sign up for Render:**
   - Go to https://render.com
   - Sign up with GitHub (easiest)

4. **Create a new Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect it's a Python app

5. **Configure:**
   - **Name**: stock-info-app (or any name)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free (or paid if you want)

6. **Deploy:**
   - Click "Create Web Service"
   - Wait 5-10 minutes for first deployment
   - Your site will be live at: `https://your-app-name.onrender.com`

### Environment Variables (if needed):
- Add in Render dashboard → Environment
- `PORT` is automatically set by Render

---

## Option 2: Railway

### Why Railway?
- ✅ Simple deployment
- ✅ $5/month free credit
- ✅ Great developer experience

### Steps:

1. **Sign up:**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure:**
   - Railway auto-detects Python
   - It will use `requirements.txt` automatically
   - Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`

4. **Deploy:**
   - Railway automatically deploys
   - Get your URL: `https://your-app-name.up.railway.app`

---

## Option 3: Fly.io

### Why Fly.io?
- ✅ Free tier with good limits
- ✅ Global edge network
- ✅ Great performance

### Steps:

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Sign up:**
   ```bash
   fly auth signup
   ```

3. **Launch your app:**
   ```bash
   fly launch
   ```
   - Follow the prompts
   - Say yes to creating a `fly.toml` file

4. **Deploy:**
   ```bash
   fly deploy
   ```

5. **Your app is live:**
   - URL: `https://your-app-name.fly.dev`

---

## Option 4: PythonAnywhere

### Why PythonAnywhere?
- ✅ Free tier available
- ✅ Beginner-friendly
- ✅ No command line needed

### Steps:

1. **Sign up:**
   - Go to https://www.pythonanywhere.com
   - Create a free "Beginner" account

2. **Upload your files:**
   - Go to Files tab
   - Upload all your project files
   - Or use Git: `git clone YOUR_REPO_URL`

3. **Create a Web App:**
   - Go to Web tab
   - Click "Add a new web app"
   - Choose Flask
   - Select Python 3.10 (or latest)

4. **Configure:**
   - Set source code path: `/home/YOUR_USERNAME/your-project-folder`
   - Set WSGI file: `/var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py`
   - Edit WSGI file to point to your app:
     ```python
     import sys
     path = '/home/YOUR_USERNAME/your-project-folder'
     if path not in sys.path:
         sys.path.append(path)
     
     from app import app as application
     ```

5. **Install dependencies:**
   - Go to Bash tab
   - Run: `pip3.10 install --user -r requirements.txt`

6. **Reload:**
   - Go back to Web tab
   - Click "Reload"
   - Your site: `https://YOUR_USERNAME.pythonanywhere.com`

---

## Option 5: AWS/Cloud Platforms

### AWS App Runner (Easiest AWS option)

1. **Prerequisites:**
   - AWS account
   - Code in GitHub/GitLab

2. **Create App Runner Service:**
   - Go to AWS Console → App Runner
   - Create service from source code
   - Connect GitHub
   - Configure:
     - Build: `pip install -r requirements.txt`
     - Start: `gunicorn app:app --bind 0.0.0.0:8000`
   - Deploy

### DigitalOcean App Platform

1. **Sign up:** https://www.digitalocean.com
2. **Create App:**
   - Connect GitHub repo
   - Auto-detects Python
   - Configure start command: `gunicorn app:app`
3. **Deploy:** Starts at $5/month

---

## Pre-Deployment Checklist

### ✅ Before deploying, make sure:

1. **Production-ready code:**
   - ✅ Debug mode is OFF (see `app.py` - already configured)
   - ✅ Port uses environment variable (see `app.py`)
   - ✅ Error handling is in place

2. **Dependencies:**
   - ✅ `requirements.txt` is up to date
   - ✅ All packages are listed

3. **Security:**
   - ✅ No hardcoded secrets
   - ✅ CORS is configured (already done)

4. **Files needed:**
   - ✅ `requirements.txt` ✓
   - ✅ `app.py` ✓
   - ✅ `templates/` folder ✓
   - ✅ `static/` folder ✓
   - ✅ `Procfile` or `render.yaml` (for some platforms)

5. **Git repository:**
   - ✅ Code is in GitHub/GitLab/Bitbucket
   - ✅ `.gitignore` excludes `venv/`, `__pycache__/`, etc.

---

## 🎯 Recommended: Render (Easiest)

For most users, **Render** is the best choice:
- Free tier available
- Easy GitHub integration
- Automatic HTTPS
- No credit card needed

**Quick Start:**
1. Push code to GitHub
2. Sign up at render.com
3. Connect GitHub repo
4. Deploy!
5. Done! 🎉

---

## 📝 Notes

- **Free tiers** usually have limitations (sleep after inactivity, slower cold starts)
- **Paid tiers** offer better performance and no sleep
- **Custom domains** can be added on most platforms
- **Environment variables** can be set in platform dashboards

---

## 🆘 Troubleshooting

### App won't start:
- Check logs in platform dashboard
- Ensure `requirements.txt` has all dependencies
- Verify start command is correct

### Port errors:
- Make sure app uses `$PORT` environment variable (already configured)

### Module not found:
- Check `requirements.txt` includes all packages
- Rebuild/redeploy

### 404 errors:
- Check static file paths use `url_for()`
- Verify folder structure matches

---

## 🎉 You're Ready!

Choose a platform above and follow the steps. Your stock information website will be live on the internet in minutes!

**Need help?** Check the platform's documentation or support forums.
