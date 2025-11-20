# Start FoodScanAI Backend Server
# Pastikan running dari folder backend

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🚀 Starting FoodScanAI Backend Server" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Set Python path
$env:PYTHONPATH = "$PSScriptRoot"

# Check if port 8000 is in use
$portCheck = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portCheck) {
    Write-Host "⚠️  Port 8000 is already in use. Killing existing process..." -ForegroundColor Yellow
    $processId = $portCheck.OwningProcess
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host "📁 Current directory: $PSScriptRoot" -ForegroundColor Green
Write-Host "🐍 Python path: $env:PYTHONPATH" -ForegroundColor Green
Write-Host ""

# Start server
Write-Host "⚡ Starting uvicorn server..." -ForegroundColor Yellow
cd $PSScriptRoot
uvicorn app.main:app --host 127.0.0.1 --port 8000
