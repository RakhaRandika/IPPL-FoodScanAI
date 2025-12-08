# Docker Deployment Script for FoodScanAI
# Run this to setup and deploy with Docker

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "    🐳 FoodScanAI Docker Deployment" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
docker --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker not found! Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

docker-compose --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker Compose not found! Please install Docker Compose." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker and Docker Compose are ready!" -ForegroundColor Green
Write-Host ""

# Check if foodscan.db exists
$sqlitePath = ".\backend\foodscan.db"
if (Test-Path $sqlitePath) {
    Write-Host "✅ Found SQLite database: $sqlitePath" -ForegroundColor Green
    $recipeCount = sqlite3 $sqlitePath "SELECT COUNT(*) FROM recipes" 2>$null
    if ($recipeCount) {
        Write-Host "   📊 Current recipes: $recipeCount" -ForegroundColor Cyan
    }
} else {
    Write-Host "⚠️  SQLite database not found. Will create empty PostgreSQL database." -ForegroundColor Yellow
}
Write-Host ""

# Build containers
Write-Host "Building Docker containers..." -ForegroundColor Yellow
docker-compose build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker build complete!" -ForegroundColor Green
Write-Host ""

# Start containers
Write-Host "Starting containers..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start containers!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Containers started!" -ForegroundColor Green
Write-Host ""

# Wait for PostgreSQL to be ready
Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

$maxRetries = 10
$retryCount = 0
while ($retryCount -lt $maxRetries) {
    $pgReady = docker exec foodscan-postgres pg_isready -U foodscan_user -d foodscan_db 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL is ready!" -ForegroundColor Green
        break
    }
    $retryCount++
    Write-Host "   Waiting... ($retryCount/$maxRetries)" -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}

if ($retryCount -eq $maxRetries) {
    Write-Host "❌ PostgreSQL failed to start!" -ForegroundColor Red
    docker-compose logs postgres
    exit 1
}
Write-Host ""

# Migrate data if SQLite exists
if (Test-Path $sqlitePath) {
    Write-Host "==============================================================" -ForegroundColor Cyan
    Write-Host "Migrate data dari SQLite ke PostgreSQL?" -ForegroundColor Yellow
    Write-Host "Ini akan memindahkan $recipeCount recipes ke Docker PostgreSQL" -ForegroundColor Yellow
    Write-Host "==============================================================" -ForegroundColor Cyan
    $migrate = Read-Host "Lanjutkan migrasi? (Y/n)"
    
    if ($migrate -ne "n" -and $migrate -ne "N") {
        Write-Host "Installing migration dependencies..." -ForegroundColor Yellow
        pip install psycopg2-binary pandas --quiet
        
        Write-Host "Running migration script..." -ForegroundColor Yellow
        python migrate_to_docker.py
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Migration complete!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Migration had issues. Check logs above." -ForegroundColor Yellow
        }
    }
}
Write-Host ""

# Show service status
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "📊 Service Status" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
docker-compose ps
Write-Host ""

# Check recipe count in PostgreSQL
Write-Host "Checking PostgreSQL data..." -ForegroundColor Yellow
$pgRecipeCount = docker exec foodscan-postgres psql -U foodscan_user -d foodscan_db -t -c "SELECT COUNT(*) FROM recipes" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostgreSQL recipes: $($pgRecipeCount.Trim())" -ForegroundColor Green
}
Write-Host ""

# Show URLs
Write-Host "==============================================================" -ForegroundColor Green
Write-Host "🎉 FoodScanAI is running!" -ForegroundColor Green
Write-Host "==============================================================" -ForegroundColor Green
Write-Host "Backend API:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Frontend:     http://localhost:3000" -ForegroundColor Cyan
Write-Host "PostgreSQL:   localhost:5432 (foodscan_db)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f              # View all logs" -ForegroundColor White
Write-Host "  docker-compose logs -f backend      # View backend logs" -ForegroundColor White
Write-Host "  docker-compose restart              # Restart all services" -ForegroundColor White
Write-Host "  docker-compose down                 # Stop all services" -ForegroundColor White
Write-Host "==============================================================" -ForegroundColor Green
