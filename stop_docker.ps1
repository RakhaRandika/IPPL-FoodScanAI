# Stop Docker containers
Write-Host "Stopping FoodScanAI containers..." -ForegroundColor Yellow
docker-compose down

Write-Host "✅ Containers stopped!" -ForegroundColor Green
Write-Host ""
Write-Host "Note: Data tetap aman di volume 'postgres_data'" -ForegroundColor Cyan
Write-Host "Untuk menghapus semua data: docker-compose down -v" -ForegroundColor Yellow
