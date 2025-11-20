# FoodScan AI - PowerShell Launcher
Write-Host "================================================" -ForegroundColor Green
Write-Host "      FoodScan AI - Application Launcher" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Check if backend venv exists
Write-Host "[1/3] Checking Python environment..." -ForegroundColor Cyan
if (-Not (Test-Path ".\backend\venv")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv backend\venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Start Backend Server
Write-Host "[2/3] Starting Backend Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; Write-Host 'Backend Server Starting...' -ForegroundColor Green; uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

# Wait for backend to initialize
Write-Host "[3/3] Waiting for backend to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Start Frontend Server
Write-Host "[3/3] Starting Frontend Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Frontend Server Starting...' -ForegroundColor Green; npm start"

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  Both servers are starting up!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "The application will open in your browser shortly." -ForegroundColor White
Write-Host ""
Write-Host "Press Enter to exit this launcher window..." -ForegroundColor Gray
Write-Host "(The servers will continue running)" -ForegroundColor Gray
Read-Host
