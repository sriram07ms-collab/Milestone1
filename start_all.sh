#!/bin/bash

echo "========================================"
echo "Starting Backend and Frontend Servers"
echo "========================================"
echo ""

# Start backend in background
echo "Starting Backend Server (Port 8000)..."
python run_server.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting Frontend Server (Port 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "Both servers are running!"
echo "========================================"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM
wait


