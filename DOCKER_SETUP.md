# 🐳 Docker Setup Guide - FoodScanAI

## Prerequisites

- Docker Desktop installed
- Docker Compose installed
- SQLite database dengan recipes sudah terisi

---

## 🚀 Quick Start

### 1. Build dan Start Containers

```powershell
# Build semua services
docker-compose build

# Start all containers
docker-compose up -d

# Check status
docker-compose ps
```

### 2. Migrate Data dari SQLite ke PostgreSQL

```powershell
# Install psycopg2 jika belum ada
pip install psycopg2-binary

# Run migration script
python migrate_to_docker.py
```

### 3. Verify Services

- **Backend API**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5432

---

## 📦 Services

### PostgreSQL Database

- **Port**: 5432
- **Database**: foodscan_db
- **User**: foodscan_user
- **Password**: foodscan_password
- **Volume**: `postgres_data` (persistent)

### Backend (FastAPI)

- **Port**: 8000
- **Auto-reload**: Enabled
- **Volume**: Mounted untuk development
- **Model**: YOLO models di `/app/app/models/models_yolo`

### Frontend (React + Nginx)

- **Port**: 3000 (mapped to 80 in container)
- **Nginx**: Reverse proxy ke backend
- **API Proxy**: `/api` → `http://backend:8000`

---

## 🛠️ Common Commands

### View Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f frontend
```

### Restart Services

```powershell
# Restart backend
docker-compose restart backend

# Restart all
docker-compose restart
```

### Stop & Remove

```powershell
# Stop containers
docker-compose stop

# Remove containers (data tetap aman di volume)
docker-compose down

# Remove containers + volumes (HATI-HATI: data hilang!)
docker-compose down -v
```

### Access Database

```powershell
# Connect to PostgreSQL container
docker exec -it foodscan-postgres psql -U foodscan_user -d foodscan_db

# Inside psql:
\dt              # List tables
\d recipes       # Describe recipes table
SELECT COUNT(*) FROM recipes;
```

### Shell Access

```powershell
# Backend container
docker exec -it foodscan-backend bash

# PostgreSQL container
docker exec -it foodscan-postgres sh
```

---

## 🔧 Development Workflow

### Backend Development

Files di `./backend` otomatis sync ke container (volume mount).
Uvicorn auto-reload aktif, jadi perubahan langsung terdeteksi.

### Frontend Development

Untuk development, lebih baik run di local:

```powershell
cd frontend
npm start
```

Untuk production build:

```powershell
docker-compose up --build frontend
```

---

## 📊 Database Management

### Backup Database

```powershell
# Backup PostgreSQL
docker exec foodscan-postgres pg_dump -U foodscan_user foodscan_db > backup.sql

# Restore
docker exec -i foodscan-postgres psql -U foodscan_user -d foodscan_db < backup.sql
```

### Check Recipe Count

```powershell
docker exec foodscan-postgres psql -U foodscan_user -d foodscan_db -c "SELECT COUNT(*) FROM recipes;"
```

---

## 🐛 Troubleshooting

### Backend tidak bisa connect ke PostgreSQL

```powershell
# Check if postgres is healthy
docker-compose ps

# Check postgres logs
docker-compose logs postgres

# Restart with fresh start
docker-compose down
docker-compose up -d postgres
# Wait 10 seconds
docker-compose up -d backend
```

### Frontend tidak bisa akses backend API

Check `nginx.conf` - pastikan proxy_pass ke `http://backend:8000`

### YOLO Model tidak ditemukan

Pastikan folder `backend/app/models/models_yolo` ada dan berisi `best (3).pt`

---

## 🌐 Environment Variables

Buat file `.env` di root folder:

```env
# Database
POSTGRES_USER=foodscan_user
POSTGRES_PASSWORD=foodscan_password
POSTGRES_DB=foodscan_db
DATABASE_URL=postgresql://foodscan_user:foodscan_password@postgres:5432/foodscan_db

# Backend
PYTHONUNBUFFERED=1
```

---

## 📝 Production Deployment

Untuk deploy ke VPS:

1. **Copy files ke VPS**

```bash
scp -r . user@vps-ip:/home/user/foodscan/
```

2. **Install Docker di VPS**

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose
```

3. **Start services**

```bash
cd /home/user/foodscan
docker-compose up -d
```

4. **Migrate data**

```bash
python migrate_to_docker.py
```

---

## ✅ Checklist

- [ ] Docker Desktop running
- [ ] `docker-compose.yml` di root folder
- [ ] `backend/Dockerfile` exists
- [ ] `frontend/Dockerfile` exists
- [ ] `frontend/nginx.conf` exists
- [ ] `init.sql` di root folder
- [ ] SQLite database `backend/foodscan.db` exists
- [ ] YOLO model `backend/app/models/models_yolo/best (3).pt` exists
- [ ] Run `docker-compose build`
- [ ] Run `docker-compose up -d`
- [ ] Run `python migrate_to_docker.py`
- [ ] Test: http://localhost:8000/docs
- [ ] Test: http://localhost:3000

---

## 🎉 Success!

Jika semua berjalan lancar:

- ✅ PostgreSQL running dengan 25,768+ recipes
- ✅ Backend API accessible di port 8000
- ✅ Frontend accessible di port 3000
- ✅ YOLO model loaded
- ✅ Database persistent (data tidak hilang saat restart)

**Selamat! FoodScanAI sudah berjalan di Docker! 🚀**
