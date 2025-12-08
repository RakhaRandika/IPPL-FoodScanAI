# 🐳 Docker Migration - FoodScanAI

## Setup Cepat

### 1. Persiapan

Pastikan Docker Desktop sudah running.

### 2. Deploy ke Docker

```powershell
.\deploy_docker.ps1
```

Script ini akan:

- ✅ Build container (Backend, Frontend, PostgreSQL)
- ✅ Start semua services
- ✅ Migrate data dari SQLite → PostgreSQL
- ✅ Verify semua services running

### 3. Akses Aplikasi

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 4. Stop Docker

```powershell
.\stop_docker.ps1
```

---

## Struktur Docker

### Services:

1. **PostgreSQL** (port 5432)

   - Database: foodscan_db
   - User: foodscan_user
   - Password: foodscan_password
   - Volume: postgres_data (persistent)

2. **Backend FastAPI** (port 8000)

   - YOLOv8 model loaded
   - Auto-reload enabled
   - Connected to PostgreSQL

3. **Frontend React** (port 3000)
   - Nginx web server
   - Reverse proxy to backend
   - Production build

---

## Commands

### View Logs

```powershell
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Restart Services

```powershell
docker-compose restart
docker-compose restart backend
```

### Database Access

```powershell
docker exec -it foodscan-postgres psql -U foodscan_user -d foodscan_db
```

### Check Status

```powershell
docker-compose ps
```

---

## File Penting

- `docker-compose.yml` - Orchestration semua services
- `backend/Dockerfile` - Backend container config
- `frontend/Dockerfile` - Frontend container config
- `init.sql` - PostgreSQL schema
- `migrate_to_docker.py` - Data migration script
- `DOCKER_SETUP.md` - Dokumentasi lengkap

---

## Troubleshooting

### Backend tidak connect ke database

```powershell
docker-compose restart postgres
Start-Sleep -Seconds 10
docker-compose restart backend
```

### Check recipe count

```powershell
docker exec foodscan-postgres psql -U foodscan_user -d foodscan_db -c "SELECT COUNT(*) FROM recipes;"
```

### Clean install

```powershell
docker-compose down -v
.\deploy_docker.ps1
```

---

## Development vs Production

### Local Development (SQLite):

```powershell
# Use .env.local
cd backend
Copy-Item .env.local .env
uvicorn app.main:app --reload
```

### Docker Production (PostgreSQL):

```powershell
# Use default .env
.\deploy_docker.ps1
```

---

**Dokumentasi lengkap**: Lihat `DOCKER_SETUP.md`
