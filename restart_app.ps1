# Script untuk restart aplikasi dengan bersih
# File: restart_app.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   FoodScanAI - Clean Restart Script   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Kill semua process Node.js
Write-Host "1. Membersihkan process Node.js lama..." -ForegroundColor Yellow
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    $nodeProcesses | Stop-Process -Force
    Write-Host "   ✓ Node.js processes dihentikan" -ForegroundColor Green
} else {
    Write-Host "   ℹ Tidak ada Node.js process yang running" -ForegroundColor Gray
}

# 2. Kill semua process Python (uvicorn)
Write-Host "2. Membersihkan process Python lama..." -ForegroundColor Yellow
$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*FoodScanAI*"}
if ($pythonProcesses) {
    $pythonProcesses | Stop-Process -Force
    Write-Host "   ✓ Python processes dihentikan" -ForegroundColor Green
} else {
    Write-Host "   ℹ Tidak ada Python process yang running" -ForegroundColor Gray
}

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "3. Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
Write-Host "   ✓ Backend starting di http://127.0.0.1:8000" -ForegroundColor Green

Start-Sleep -Seconds 5

Write-Host ""
Write-Host "4. Starting Frontend Server..." -ForegroundColor Yellow  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"
Write-Host "   ✓ Frontend akan start di http://localhost:3000" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ✅ Aplikasi sedang starting...       " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tunggu beberapa saat, lalu buka browser:" -ForegroundColor White
Write-Host ""
Write-Host "  Backend:  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tekan Ctrl+C untuk keluar dari script ini" -ForegroundColor Gray
Write-Host ""

# Keep script running
while ($true) {
    Start-Sleep -Seconds 1
}
