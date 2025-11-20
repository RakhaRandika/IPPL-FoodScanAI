@echo off
title FoodScan AI - Launcher
color 0A

echo ================================================
echo       FoodScan AI - Application Launcher
echo ================================================
echo.

echo [1/3] Checking Python environment...
cd backend
if not exist "venv\" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

echo [2/3] Starting Backend Server...
start "FoodScan Backend" cmd /k "cd /d %CD% && .\venv\Scripts\activate && echo Backend Server Starting... && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
cd ..

echo [3/3] Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo [3/3] Starting Frontend Server...
start "FoodScan Frontend" cmd /k "npm start"

echo.
echo ================================================
echo   Both servers are starting up!
echo ================================================
echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:3000
echo.
echo The application will open in your browser shortly.
echo.
echo Press any key to exit this launcher window...
echo (The servers will continue running)
pause > nul
