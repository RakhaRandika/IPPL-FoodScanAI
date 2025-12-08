# ✅ Docker Migration Checklist

## Files Created/Modified

### Docker Configuration

- [x] `docker-compose.yml` - Orchestration (PostgreSQL, Backend, Frontend)
- [x] `backend/Dockerfile` - Backend container
- [x] `frontend/Dockerfile` - Frontend multi-stage build
- [x] `frontend/nginx.conf` - Reverse proxy config
- [x] `.dockerignore` - Exclude unnecessary files
- [x] `init.sql` - PostgreSQL schema initialization

### Migration & Deployment

- [x] `migrate_to_docker.py` - SQLite → PostgreSQL migration script
- [x] `deploy_docker.ps1` - Automated deployment script
- [x] `stop_docker.ps1` - Stop containers script

### Configuration

- [x] `backend/.env` - Docker PostgreSQL config
- [x] `backend/.env.local` - Local SQLite config
- [x] `backend/requirements.txt` - Added psycopg2-binary, sqlalchemy, python-dotenv

### Code Updates

- [x] `backend/app/main.py` - Added `/health` endpoint for Docker healthcheck

### Documentation

- [x] `README.md` - Main documentation with Docker section
- [x] `DOCKER_README.md` - Quick reference
- [x] `DOCKER_SETUP.md` - Comprehensive setup guide
- [x] `DOCKER_MIGRATION_CHECKLIST.md` - This file

---

## Deployment Steps

### 1. Prerequisites ✅

- [x] Docker Desktop installed and running
- [x] Docker Compose installed
- [x] SQLite database exists at `backend/foodscan.db` (25,768 recipes)
- [x] YOLO model exists at `backend/app/models/models_yolo/best (3).pt`

### 2. Build & Deploy 🚀

```powershell
.\deploy_docker.ps1
```

This script will:

- Check Docker availability
- Build all containers
- Start services
- Wait for PostgreSQL
- Migrate data from SQLite
- Verify deployment

### 3. Verify Services 🔍

- [ ] PostgreSQL running: `docker-compose ps`
- [ ] Backend healthy: http://localhost:8000/health
- [ ] Frontend accessible: http://localhost:3000
- [ ] Recipe count matches: 25,768 recipes

### 4. Test Functionality 🧪

- [ ] Upload image via frontend
- [ ] YOLO detection works
- [ ] Recipes returned (up to 1000)
- [ ] Nutrition data displayed
- [ ] Camera stream works (if available)

---

## Service Ports

| Service    | Port | URL                        |
| ---------- | ---- | -------------------------- |
| Frontend   | 3000 | http://localhost:3000      |
| Backend    | 8000 | http://localhost:8000/docs |
| PostgreSQL | 5432 | localhost:5432             |

---

## Docker Commands Reference

### View Status

```powershell
docker-compose ps
docker-compose logs -f
docker-compose logs -f backend
```

### Restart

```powershell
docker-compose restart
docker-compose restart backend
```

### Stop

```powershell
.\stop_docker.ps1
# OR
docker-compose down
```

### Clean Restart

```powershell
docker-compose down -v
.\deploy_docker.ps1
```

### Database Access

```powershell
# Connect to PostgreSQL
docker exec -it foodscan-postgres psql -U foodscan_user -d foodscan_db

# Inside psql:
\dt                           # List tables
\d recipes                    # Describe recipes table
SELECT COUNT(*) FROM recipes; # Count recipes
```

---

## Environment Switching

### Use Docker (PostgreSQL)

```powershell
cd backend
Copy-Item .env .env.backup
# .env already configured for Docker
```

### Use Local (SQLite)

```powershell
cd backend
Copy-Item .env.local .env
```

---

## Troubleshooting

### PostgreSQL not starting

```powershell
docker-compose logs postgres
docker-compose restart postgres
```

### Backend can't connect to database

```powershell
# Wait longer for PostgreSQL
Start-Sleep -Seconds 10
docker-compose restart backend
```

### Frontend showing errors

```powershell
# Check backend is accessible
curl http://localhost:8000/health

# Check nginx logs
docker-compose logs frontend
```

### Model not loading

```powershell
# Verify model file exists
Test-Path ".\backend\app\models\models_yolo\best (3).pt"

# Check backend logs
docker-compose logs backend | Select-String "model"
```

---

## Migration Verification

### Check Recipe Count

```powershell
# PostgreSQL
docker exec foodscan-postgres psql -U foodscan_user -d foodscan_db -t -c "SELECT COUNT(*) FROM recipes"

# SQLite (compare)
sqlite3 ".\backend\foodscan.db" "SELECT COUNT(*) FROM recipes"
```

### Sample Recipes

```powershell
docker exec foodscan-postgres psql -U foodscan_user -d foodscan_db -c "SELECT title, category FROM recipes LIMIT 10"
```

---

## Production Deployment (VPS)

### 1. Copy Files to VPS

```bash
scp -r . user@vps:/home/user/foodscan/
```

### 2. Install Docker on VPS

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose
```

### 3. Deploy

```bash
cd /home/user/foodscan
docker-compose up -d
python migrate_to_docker.py
```

### 4. Setup Nginx (VPS)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

---

## Success Indicators ✅

After successful deployment, you should see:

- ✅ 3 containers running (postgres, backend, frontend)
- ✅ PostgreSQL healthy with 25,768 recipes
- ✅ Backend `/health` returns 200 OK
- ✅ Frontend loads successfully
- ✅ Food detection works
- ✅ Recipe recommendations returned (up to 1000)
- ✅ Nutrition data displayed

---

## Next Steps 🎯

1. **Test dengan berbagai gambar makanan**
2. **Verify semua 25 kelas YOLO berfungsi**
3. **Test recipe search dengan berbagai kombinasi**
4. **Monitor performance dengan 1000 recipes**
5. **Backup PostgreSQL volume**: `docker run --rm -v foodscanai-copy_postgres_data:/data -v ${PWD}:/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .`

---

## Support 🆘

Jika ada masalah:

1. Check logs: `docker-compose logs -f`
2. Verify services: `docker-compose ps`
3. Restart: `docker-compose restart`
4. Clean restart: `docker-compose down && docker-compose up -d`
5. Check documentation: `DOCKER_SETUP.md`

---

**Migration Status**: ✅ COMPLETE
**Last Updated**: December 2025
**Migration Script**: `migrate_to_docker.py`
**Deployment Script**: `deploy_docker.ps1`
