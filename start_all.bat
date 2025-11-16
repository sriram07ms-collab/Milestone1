@echo off
echo ========================================
echo Starting Backend and Frontend Servers
echo ========================================
echo.

echo Starting Backend Server (Port 8000)...
start "Backend Server" cmd /k "cd /d %~dp0 && python run_server.py"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server (Port 3000)...
start "Frontend Server" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit (servers will continue running)...
pause >nul


