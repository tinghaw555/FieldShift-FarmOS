@echo off
echo FieldShift FarmOS - Stop Development Servers
echo =============================================
echo.

echo Finding processes on ports 3000, 3001, 8000...
echo.

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo Stopping process on port 3000 (PID: %%a)
    taskkill /PID %%a /F > nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3001" ^| findstr "LISTENING"') do (
    echo Stopping process on port 3001 (PID: %%a)
    taskkill /PID %%a /F > nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Stopping process on port 8000 (PID: %%a)
    taskkill /PID %%a /F > nul 2>&1
)

echo.
echo All development servers stopped.
echo.
pause
