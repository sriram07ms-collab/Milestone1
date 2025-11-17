# Deployment Checklist

Use this checklist to track your deployment progress.

## Pre-Deployment

- [ ] Code is pushed to GitHub
- [ ] You have a Render account (✅ you mentioned you have this)
- [ ] You have a Gemini API key from https://makersuite.google.com/app/apikey
- [ ] You know your GitHub username

---

## Backend Deployment (Render)

### Step 1: Create Web Service
- [ ] Logged into Render
- [ ] Clicked "New +" → "Web Service"
- [ ] Connected GitHub repository
- [ ] Selected repository: `Milestone1`

### Step 2: Configure Service
- [ ] **Name**: `mutual-fund-chatbot-backend` (or your choice)
- [ ] **Region**: Selected (e.g., Oregon)
- [ ] **Branch**: `main`
- [ ] **Runtime**: `Docker` (recommended)
  - OR `Python 3` with Python 3.11
- [ ] **Dockerfile Path**: `Dockerfile.backend` (if using Docker)
- [ ] **Instance Type**: `Free`
- [ ] **Health Check Path**: `/api/health`
- [ ] **Auto-Deploy**: `Yes`

### Step 3: Environment Variables
Add these in Render → Environment tab:

- [ ] `GEMINI_API_KEY` = `your_actual_api_key`
- [ ] `GEMINI_MODEL` = `gemini-2.0-flash-exp`
- [ ] `DATABASE_URL` = `sqlite:///./icici_funds.db`
- [ ] `LOG_LEVEL` = `INFO`
- [ ] `RAG_ENABLED` = `false`
- [ ] `BACKEND_CORS_ORIGINS` = (leave empty for now, update after frontend)

### Step 4: Deploy
- [ ] Clicked "Create Web Service"
- [ ] Waited for build to complete (5-10 minutes)
- [ ] Backend URL received: `https://________________.onrender.com`
- [ ] Tested backend: `https://________________.onrender.com/api/health`
- [ ] Tested API docs: `https://________________.onrender.com/docs`

**Backend URL**: `________________________________________`

---

## Frontend Deployment (GitHub Pages)

### Step 1: GitHub Secret
- [ ] Went to GitHub repo → Settings → Secrets → Actions
- [ ] Created secret: `BACKEND_PUBLIC_URL`
- [ ] Value: `https://your-backend-url.onrender.com/api`
- [ ] Secret saved

### Step 2: Enable Pages
- [ ] Went to GitHub repo → Settings → Pages
- [ ] Set Source: `GitHub Actions`
- [ ] Saved

### Step 3: Trigger Deployment
- [ ] Pushed a commit to `main` branch
- [ ] Went to Actions tab
- [ ] Workflow completed successfully
- [ ] Frontend URL: `https://yourusername.github.io/Milestone1/`

**Frontend URL**: `________________________________________`

---

## Final Configuration

### Update CORS
- [ ] Went to Render → Backend service → Environment
- [ ] Updated `BACKEND_CORS_ORIGINS` = `https://yourusername.github.io`
- [ ] Saved (auto-redeploys)

---

## Testing

### Backend Tests
- [ ] Health check works: `/api/health`
- [ ] API docs accessible: `/docs`
- [ ] Chat endpoint works: `/api/chat` (test in Swagger UI)

### Frontend Tests
- [ ] Frontend loads correctly
- [ ] Can see chatbot interface
- [ ] Can send a message
- [ ] Receives response from backend
- [ ] No CORS errors in browser console

### Integration Test
- [ ] Asked: "What is ICICI Prudential Large Cap Fund?"
- [ ] Received proper answer
- [ ] Source URL displayed

---

## Troubleshooting

If something doesn't work:

### Backend Issues
- [ ] Checked Render logs (Service → Logs tab)
- [ ] Verified all environment variables are set
- [ ] Tested health endpoint directly
- [ ] Checked for Python version errors (use Docker if needed)

### Frontend Issues
- [ ] Checked GitHub Actions logs
- [ ] Verified `BACKEND_PUBLIC_URL` secret is correct
- [ ] Checked browser console for errors
- [ ] Verified CORS settings in backend

---

## Success! 🎉

Once all items are checked:
- ✅ Backend is live on Render
- ✅ Frontend is live on GitHub Pages
- ✅ Everything is connected and working

**Share your app**: `https://yourusername.github.io/Milestone1/`

---

## Quick Reference

**Backend URL**: `https://your-service-name.onrender.com`  
**Frontend URL**: `https://yourusername.github.io/Milestone1/`  
**API Docs**: `https://your-service-name.onrender.com/docs`  
**Health Check**: `https://your-service-name.onrender.com/api/health`

---

## Need Help?

Refer to: `RENDER_DEPLOYMENT_GUIDE.md` for detailed instructions.

