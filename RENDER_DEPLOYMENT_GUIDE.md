# Step-by-Step Deployment Guide for Render

This guide will help you deploy your Mutual Fund FAQ Chatbot to Render (backend) and GitHub Pages (frontend).

---

## Prerequisites

✅ Render account (you already have this)  
✅ GitHub account  
✅ Code pushed to GitHub repository  
✅ Gemini API key (from Google AI Studio)

---

## Part 1: Deploy Backend to Render

### Step 1: Create a New Web Service on Render

1. **Log in to Render**
   - Go to https://render.com
   - Sign in to your account

2. **Create New Web Service**
   - Click **"New +"** button (top right)
   - Select **"Web Service"**

3. **Connect Your GitHub Repository**
   - Click **"Connect account"** if not already connected
   - Authorize Render to access your GitHub
   - Select your repository: `Milestone1` (or your repo name)
   - Click **"Connect"**

### Step 2: Configure the Web Service

Fill in the following settings:

**Basic Settings:**
- **Name**: `mutual-fund-chatbot-backend` (or any name you prefer)
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main`
- **Root Directory**: Leave empty (or `.` if needed)

**Build & Deploy:**
- **Runtime**: Select **"Docker"** (recommended to avoid Python version issues)
  - OR use **"Python 3"** with Python 3.11 (see Alternative below)

**If using Docker:**
- **Dockerfile Path**: `Dockerfile.backend` (we'll create this)
- **Docker Context**: `.` (root directory)

**If using Python 3 (Alternative):**
- **Build Command**: 
  ```bash
  pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  uvicorn api.main:app --host 0.0.0.0 --port $PORT
  ```

**Advanced Settings:**
- **Instance Type**: `Free` (for testing)
- **Health Check Path**: `/api/health`
- **Auto-Deploy**: `Yes` (deploys on every push to main)

### Step 3: Create Dockerfile (if using Docker)

Create `Dockerfile.backend` in your project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render will set $PORT)
EXPOSE 8080

# Start the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Note**: If using Docker, Render will automatically map port 8080 to `$PORT`. Make sure your Dockerfile uses port 8080.

### Step 4: Set Environment Variables

In Render dashboard, go to your service → **"Environment"** tab:

Add these environment variables:

| Key | Value | Description |
|-----|-------|-------------|
| `GEMINI_API_KEY` | `your_api_key_here` | Your Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.0-flash-exp` | Gemini model name |
| `DATABASE_URL` | `sqlite:///./icici_funds.db` | Database URL (SQLite for free tier) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `RAG_ENABLED` | `false` | Set to `true` if you want RAG (requires more memory) |
| `BACKEND_CORS_ORIGINS` | `https://yourusername.github.io` | Frontend URL (we'll update this later) |

**Important**: 
- Get your Gemini API key from: https://makersuite.google.com/app/apikey
- Replace `your_api_key_here` with your actual key
- For `BACKEND_CORS_ORIGINS`, we'll update this after deploying the frontend

### Step 5: Deploy

1. Click **"Create Web Service"** (or **"Save Changes"** if editing)
2. Render will start building your service
3. Wait for the build to complete (5-10 minutes for first build)
4. Once deployed, you'll get a URL like: `https://mutual-fund-chatbot-backend.onrender.com`

### Step 6: Test Backend

1. Open your backend URL in a browser
2. You should see: `{"message":"ICICI Prudential Mutual Fund FAQ Assistant API","version":"1.0.0","docs":"/docs"}`
3. Test health endpoint: `https://your-backend-url.onrender.com/api/health`
4. Test API docs: `https://your-backend-url.onrender.com/docs`

**Copy your backend URL** - you'll need it for the frontend!

---

## Part 2: Deploy Frontend to GitHub Pages

### Step 1: Add GitHub Secret

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add:
   - **Name**: `BACKEND_PUBLIC_URL`
   - **Value**: `https://your-backend-url.onrender.com/api`
     - Example: `https://mutual-fund-chatbot-backend.onrender.com/api`
5. Click **"Add secret"**

### Step 2: Enable GitHub Pages

1. In your GitHub repository, go to **Settings** → **Pages**
2. Under **"Build and deployment"**:
   - **Source**: Select **"GitHub Actions"**
3. Save

### Step 3: Verify Workflow File

Check that `.github/workflows/frontend-pages.yml` exists and is correct. It should:
- Build the frontend
- Set `VITE_API_URL` from the secret
- Deploy to GitHub Pages

### Step 4: Trigger Deployment

1. Make a small change (or just push any commit)
2. Push to `main` branch:
   ```bash
   git add .
   git commit -m "trigger frontend deployment"
   git push origin main
   ```
3. Go to **Actions** tab in GitHub
4. Watch the workflow run
5. Once complete, your site will be at:
   `https://yourusername.github.io/Milestone1/`

---

## Part 3: Update CORS Settings

### Step 1: Get Your Frontend URL

Your frontend will be at:
`https://yourusername.github.io/Milestone1/`

### Step 2: Update Backend CORS

1. Go to Render dashboard → Your backend service
2. Go to **Environment** tab
3. Find `BACKEND_CORS_ORIGINS`
4. Update value to:
   ```
   https://yourusername.github.io
   ```
   (Replace `yourusername` with your GitHub username)
5. Click **"Save Changes"**
6. Render will automatically redeploy

---

## Part 4: Test Complete Deployment

### Test Frontend
1. Open: `https://yourusername.github.io/Milestone1/`
2. You should see the chatbot interface
3. Try asking a question like: "What is ICICI Prudential Large Cap Fund?"

### Test Backend Directly
1. Open: `https://your-backend-url.onrender.com/docs`
2. Test the `/api/chat` endpoint with:
   ```json
   {
     "query": "What is ICICI Prudential Large Cap Fund?"
   }
   ```

---

## Troubleshooting

### Backend Issues

**Problem: Build fails with Python version error**
- **Solution**: Use Docker option instead of Python 3 runtime

**Problem: "No open port detected"**
- **Solution**: 
  - Make sure start command uses `$PORT` (not hardcoded)
  - Check health check path is `/api/health`
  - Wait a few minutes for the service to start

**Problem: "Out of memory"**
- **Solution**: 
  - Set `RAG_ENABLED=false` (RAG uses a lot of memory)
  - Or upgrade to a paid plan

**Problem: CORS errors in browser**
- **Solution**: 
  - Check `BACKEND_CORS_ORIGINS` includes your frontend URL
  - Make sure there's no trailing slash in the URL
  - Redeploy backend after changing CORS settings

### Frontend Issues

**Problem: Frontend shows "Cannot connect to backend"**
- **Solution**: 
  - Check `BACKEND_PUBLIC_URL` secret is set correctly
  - Make sure it ends with `/api` (not just the base URL)
  - Verify backend is running and accessible

**Problem: GitHub Pages shows 404**
- **Solution**: 
  - Check GitHub Actions workflow ran successfully
  - Verify Pages is set to use GitHub Actions (not a branch)
  - Wait a few minutes for Pages to update

**Problem: Assets not loading (404 on CSS/JS)**
- **Solution**: 
  - Check workflow sets correct base path
  - Verify `vite.config.js` doesn't override base path

---

## Quick Reference

### Backend URL Format
```
https://your-service-name.onrender.com
```

### Frontend URL Format
```
https://yourusername.github.io/repository-name/
```

### Environment Variables Checklist
- [ ] `GEMINI_API_KEY` - Your Gemini API key
- [ ] `GEMINI_MODEL` - `gemini-2.0-flash-exp`
- [ ] `DATABASE_URL` - `sqlite:///./icici_funds.db`
- [ ] `BACKEND_CORS_ORIGINS` - Your frontend URL
- [ ] `LOG_LEVEL` - `INFO`
- [ ] `RAG_ENABLED` - `false` (or `true` if you have enough memory)

### GitHub Secret Checklist
- [ ] `BACKEND_PUBLIC_URL` - `https://your-backend-url.onrender.com/api`

---

## Next Steps After Deployment

1. ✅ Test all endpoints
2. ✅ Monitor Render logs for errors
3. ✅ Check GitHub Actions for frontend build status
4. ✅ Test chatbot with various queries
5. ✅ Share your deployed URL!

---

## Support

If you encounter issues:
1. Check Render logs: Service → **Logs** tab
2. Check GitHub Actions: Repository → **Actions** tab
3. Verify all environment variables are set correctly
4. Test backend health endpoint: `/api/health`

Good luck with your deployment! 🚀

