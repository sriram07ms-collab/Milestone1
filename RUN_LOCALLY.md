# Run Frontend and Backend Locally

## ✅ Integration Complete

The frontend and backend are properly integrated and ready to run locally.

---

## 🚀 Quick Start

### Method 1: Use Batch Script (Windows)

Double-click `start_all.bat` or run:
```bash
start_all.bat
```

This opens two windows:
- Backend server (port 8000)
- Frontend server (port 3000)

### Method 2: Manual Start (Recommended)

**Step 1: Start Backend**

Open Terminal 1:
```bash
cd C:\Users\SM095616\Milestone1
python run_server.py
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

**Step 2: Start Frontend**

Open Terminal 2:
```bash
cd C:\Users\SM095616\Milestone1\frontend
npm run dev
```

Wait for: `Local: http://localhost:3000`

**Step 3: Open Browser**

Navigate to: **http://localhost:3000**

---

## 📍 Server URLs

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

## ✅ Verify Everything is Working

### Check Server Status

```bash
python check_status.py
```

This will show:
- Backend status
- Frontend status
- Integration test

### Test in Browser

1. Open http://localhost:3000
2. You should see:
   - Green header with "Fact Only" badge
   - Blue disclaimer banner
   - Chat interface
   - Suggested questions

3. Try asking:
   - "What is the expense ratio of ICICI Prudential Large Cap Fund?"
   - "What is the minimum SIP amount?"
   - "Tell me about exit load"

---

## 🔧 Configuration

### Backend
- **Port**: 8000
- **CORS**: Enabled for all origins
- **API Prefix**: `/api`

### Frontend
- **Port**: 3000
- **API Proxy**: Configured to backend
- **Environment**: Development mode

---

## 🐛 Troubleshooting

### Backend Won't Start

1. **Check port 8000 is free:**
   ```bash
   netstat -ano | findstr :8000
   ```

2. **Check dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check database:**
   ```bash
   python verify_database.py
   ```

### Frontend Won't Start

1. **Check Node.js (18+):**
   ```bash
   node --version
   ```

2. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

3. **Check port 3000 is free**

### Connection Errors

1. **Verify backend is running:**
   - Visit: http://localhost:8000/api/health
   - Should return JSON with status

2. **Check browser console:**
   - Open DevTools (F12)
   - Look for errors in Console tab

3. **Verify CORS:**
   - Backend CORS is configured
   - Should work automatically

---

## 📝 Development Workflow

1. **Start Backend** (Terminal 1)
   ```bash
   python run_server.py
   ```

2. **Start Frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Browser**
   - http://localhost:3000

4. **Monitor Logs**
   - Backend: Terminal 1
   - Frontend: Terminal 2
   - Browser: DevTools Console

---

## ✅ Success Indicators

When everything is working:

- ✅ Backend shows: `Uvicorn running on http://0.0.0.0:8000`
- ✅ Frontend shows: `Local: http://localhost:3000`
- ✅ Browser shows: Chat interface with green theme
- ✅ Health check: http://localhost:8000/api/health returns 200
- ✅ Chat works: Questions get answered with source URLs

---

## 🎯 Next Steps

1. ✅ Integration complete
2. ✅ Both servers can run locally
3. ⏳ Test with sample queries
4. ⏳ Verify all features
5. ⏳ Customize (optional)

---

## 📚 Additional Resources

- **Integration Guide**: `INTEGRATION_GUIDE.md`
- **Frontend Setup**: `FRONTEND_SETUP.md`
- **Backend API Docs**: http://localhost:8000/docs
- **Status Check**: `python check_status.py`

---

**Status**: ✅ **Ready to Run Locally**

Start both servers and access the application at http://localhost:3000!


