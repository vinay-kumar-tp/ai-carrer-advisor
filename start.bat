@echo off
echo ===================================================
echo     Launching AI Career Advisor Platform
echo ===================================================
echo.
echo Starting FastAPI Backend API on http://localhost:8000 ...
start "Backend API" cmd /k "cd backend && uvicorn app.main:app --port 8000 --reload"

echo Starting Vite React Frontend on http://localhost:5173 ...
start "Frontend UI" cmd /k "cd frontend && npm run dev"

echo.
echo Both backend and frontend services are starting up!
echo Access the application at: http://localhost:5173
pause
