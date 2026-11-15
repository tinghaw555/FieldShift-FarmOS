@echo off
echo FieldShift FarmOS - Development Startup Script
echo ================================================
echo.

echo Checking for existing processes on ports 3000, 3001, 8000...
netstat -ano | findstr ":3000 :3001 :8000" > nul
if %errorlevel% == 0 (
    echo WARNING: Ports may already be in use.
    echo Run stop-dev.bat first to clean up old processes.
    pause
)

echo.
echo Starting Backend (FastAPI on port 8000)...
start "FieldShift Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --port 8000"

echo Waiting 3 seconds for backend to initialize...
timeout /t 3 /nobreak > nul

echo.
echo Starting Frontend (Next.js on port 3000)...
start "FieldShift Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ================================================
echo FieldShift FarmOS is starting up!
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to return to prompt...
echo (Development servers will continue running in separate windows)
pause > nul
