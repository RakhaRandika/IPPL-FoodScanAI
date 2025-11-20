# Script untuk menjalankan FoodScanAI Backend Server
# PowerShell script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   FoodScanAI Backend Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cek apakah di folder backend
$currentPath = Get-Location
if ($currentPath.Path -notlike "*backend*") {
    Write-Host "Berpindah ke folder backend..." -ForegroundColor Yellow
    Set-Location -Path (Join-Path $PSScriptRoot ".")
}

# Cek apakah model ada
$modelPath = "app\models\models_yolo\best.pt"
if (Test-Path $modelPath) {
    Write-Host "✓ Model ditemukan: $modelPath" -ForegroundColor Green
} else {
    Write-Host "⚠ Warning: Model tidak ditemukan di $modelPath" -ForegroundColor Yellow
    Write-Host "  Pastikan file best.pt ada di lokasi tersebut!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Memulai server..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Server akan berjalan di:" -ForegroundColor Green
Write-Host "  → http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "Dokumentasi API:" -ForegroundColor Green
Write-Host "  → Swagger UI: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  → ReDoc: http://localhost:8000/redoc" -ForegroundColor White
Write-Host ""
Write-Host "Tekan Ctrl+C untuk menghentikan server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Jalankan uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
