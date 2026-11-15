@echo off
echo ========================================
echo FieldShift FarmOS - Starting Backend
echo ========================================
echo.

cd backend

echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting FastAPI server...
echo API will be available at http://localhost:8000
echo API docs at http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn main:app --reload --port 8000
