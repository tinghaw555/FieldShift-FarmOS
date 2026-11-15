@echo off
echo ========================================
echo FieldShift FarmOS - Starting Frontend
echo ========================================
echo.

cd frontend

echo Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

echo.
echo Installing dependencies (first time only)...
if not exist node_modules (
    npm install
) else (
    echo Dependencies already installed, skipping...
)

echo.
echo Starting Next.js development server...
echo Frontend will be available at http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev
