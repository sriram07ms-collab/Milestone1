## Simple GitHub-based deployment (no server, no domain)

This setup deploys:
- Frontend (Vite React) → GitHub Pages (free URL)
- Backend (FastAPI) → Railway or Render (free URL)

You only need a GitHub account. No Ubuntu server or custom domain required.

---

### 1) Push your code to GitHub
Create a new repository and push this project to `main`.

### 2) Deploy backend (Railway or Render)
Pick one (both are OK for demos):

- Railway
  - New Project → Deploy from GitHub → select this repo.
  - Build command: `pip install -r requirements.txt`
  - Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
  - Env Vars: `GEMINI_API_KEY=your_key`, `GEMINI_MODEL=gemini-2.0-flash-exp`
  - (Optional) If you want embeddings on each boot (ephemeral storage):  
    `python scripts/generate_embeddings.py && uvicorn api.main:app --host 0.0.0.0 --port $PORT`

- Render
  - New → Web Service → connect GitHub repo.
  - Option A (Buildpacks, Python 3.11):
    - Runtime: Python 3.11
    - Build: `pip install --upgrade pip setuptools wheel && pip install -r requirements.txt`
    - Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
  - Option B (Docker — avoids Python 3.13 wheel issues):
    - Select “Use Docker” and point to `Dockerfile.backend` (Python 3.11).
    - Internal port: 8080 (Render maps to `$PORT` automatically).
  - Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
  - Env Vars: `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-2.0-flash-exp`
  - (Optional) Set `PIP_ONLY_BINARY=:all:` to avoid building from source (buildpacks only)

Copy your backend public URL, e.g. `https://yourapp.up.railway.app` or `https://yourapp.onrender.com`.

### 3) Add a GitHub secret for the frontend
In GitHub → Repo → Settings → Secrets and variables → Actions → “New repository secret”
- Name: `BACKEND_PUBLIC_URL`
- Value: `https://<your-backend-host>/api`

Example: `https://yourapp.up.railway.app/api`

### 4) Frontend auto-deploy to GitHub Pages
This repo includes a workflow at `.github/workflows/frontend-pages.yml`.
On each push to `main`:
- It builds `frontend/` with `VITE_API_URL` set from `BACKEND_PUBLIC_URL`
- It auto-sets Vite base path to `/<repo-name>/` so assets work on GitHub Pages
- Publishes the static site to GitHub Pages

Enable Pages:
- GitHub → Repo → Settings → Pages → Build & deployment = GitHub Actions

After the first run, your site will be available at:
`https://<your-github-username>.github.io/<repo-name>/`

### 5) Test
- Open the GitHub Pages URL and send a message.
- The frontend calls the backend at `BACKEND_PUBLIC_URL`.

### Notes
- Free tiers may sleep; first request after idle can be slower.
- Railway/Render free storage is ephemeral; embeddings reset on deploy. For persistence, add a paid volume or switch to a managed vector DB later.
- CORS: set `BACKEND_CORS_ORIGINS` in your backend (comma-separated) to include your Pages URL, e.g. `https://<username>.github.io/<repo-name>`.

That’s it—no server and no domain needed. Push to `main` to redeploy automatically. 


