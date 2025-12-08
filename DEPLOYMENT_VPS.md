# 🚀 Deployment Guide - FoodScanAI ke VPS

## 📋 Prerequisites

- VPS Ubuntu 22.04/24.04 (DigitalOcean, Vultr, Linode, dll)
- Domain (opsional, bisa pakai IP)
- SSH access ke VPS

## 🎯 Architecture di VPS

```
Internet
    ↓
Nginx (Port 80/443) → Reverse Proxy
    ↓
Backend API (Port 8000) → FastAPI + Uvicorn
    ↓
PostgreSQL (Port 5432) → Database Lokal VPS
    ↓
Frontend (Static Files) → Served by Nginx
```

---

## 📦 Step 1: Setup VPS & Dependencies

### 1.1 Connect ke VPS

```bash
ssh root@your-vps-ip
```

### 1.2 Update System

```bash
apt update && apt upgrade -y
```

### 1.3 Install Dependencies

```bash
# Python & PostgreSQL
apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx git

# System libraries untuk OpenCV & YOLO
apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev
```

---

## 🗄️ Step 2: Setup PostgreSQL

### 2.1 Create Database & User

```bash
# Switch ke user postgres
sudo -u postgres psql

# Di psql prompt:
CREATE DATABASE foodscan;
CREATE USER dbuser WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE foodscan TO dbuser;
ALTER DATABASE foodscan OWNER TO dbuser;
\q
```

### 2.2 Configure PostgreSQL untuk Local Access

```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Tambahkan line ini:
# local   all             dbuser                                  md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 2.3 Test Connection

```bash
psql -U dbuser -d foodscan -h localhost
# Masukkan password, ketik \q untuk exit
```

---

## 📂 Step 3: Deploy Application

### 3.1 Clone Repository

```bash
cd /opt
git clone https://github.com/RakhaRandika/IPPL-FoodScanAI.git
cd IPPL-FoodScanAI
```

### 3.2 Setup Backend

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql+psycopg2://dbuser:your_secure_password_here@localhost:5432/foodscan
MODEL_PATH=./app/models/models_yolo/best (3).pt
SECRET_KEY=$(openssl rand -hex 32)
EOF

# Set permissions
chmod 600 .env
```

### 3.3 Populate Database

```bash
# Pastikan CSV ada di app/data/resep_dataset.csv
python -m app.database.populate_db

# Verify
python -c "from app.database import SessionLocal, Recipe; s = SessionLocal(); print(f'Total recipes: {s.query(Recipe).count()}'); s.close()"
```

### 3.4 Build Frontend

```bash
cd ../frontend

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install dependencies & build
npm install
npm run build

# Build output akan ada di: frontend/build/
```

---

## 🔧 Step 4: Setup Systemd Service (Auto-start Backend)

### 4.1 Create Service File

```bash
sudo nano /etc/systemd/system/foodscan-backend.service
```

### 4.2 Paste Configuration

```ini
[Unit]
Description=FoodScanAI Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/IPPL-FoodScanAI/backend
Environment="PATH=/opt/IPPL-FoodScanAI/backend/venv/bin"
ExecStart=/opt/IPPL-FoodScanAI/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4.3 Enable & Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable foodscan-backend
sudo systemctl start foodscan-backend

# Check status
sudo systemctl status foodscan-backend

# View logs
sudo journalctl -u foodscan-backend -f
```

---

## 🌐 Step 5: Setup Nginx Reverse Proxy

### 5.1 Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/foodscan
```

### 5.2 Paste Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Ganti dengan domain/IP Anda

    # Frontend (Static Files)
    location / {
        root /opt/IPPL-FoodScanAI/frontend/build;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "public, max-age=3600";
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Upload size limit untuk gambar
        client_max_body_size 10M;
    }

    # Static files dari backend (jika ada)
    location /static/ {
        alias /opt/IPPL-FoodScanAI/backend/static/;
    }
}
```

### 5.3 Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/foodscan /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

---

## 🔒 Step 6: Setup SSL (HTTPS) - Optional tapi Recommended

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL Certificate (ganti your-domain.com)
sudo certbot --nginx -d your-domain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

---

## ✅ Step 7: Verification

### 7.1 Test Backend API

```bash
curl http://localhost:8000/docs
# Harus return Swagger UI HTML
```

### 7.2 Test Full Stack

```bash
# Dari browser:
http://your-domain.com       # Frontend
http://your-domain.com/api/docs  # API Documentation
```

### 7.3 Test Upload Gambar

Upload gambar via frontend, cek apakah:

- ✅ YOLO deteksi berjalan
- ✅ Recipes muncul
- ✅ Database query cepat

---

## 🔄 Update Application (Deploy Update)

```bash
cd /opt/IPPL-FoodScanAI

# Pull latest code
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart foodscan-backend

# Update frontend
cd ../frontend
npm install
npm run build
sudo systemctl reload nginx
```

---

## 📊 Monitoring & Maintenance

### Backend Logs

```bash
# Real-time logs
sudo journalctl -u foodscan-backend -f

# Last 100 lines
sudo journalctl -u foodscan-backend -n 100

# Today's logs
sudo journalctl -u foodscan-backend --since today
```

### Database Maintenance

```bash
# Backup database
pg_dump -U dbuser foodscan > foodscan_backup_$(date +%Y%m%d).sql

# Restore database
psql -U dbuser foodscan < foodscan_backup_20241206.sql

# Check database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('foodscan'));"
```

### System Resources

```bash
# Disk usage
df -h

# Memory usage
free -h

# CPU usage
htop
```

---

## 🚨 Troubleshooting

### Backend tidak start

```bash
# Check error logs
sudo journalctl -u foodscan-backend -n 50

# Common issues:
# 1. Database connection failed → Check PostgreSQL running
sudo systemctl status postgresql

# 2. Permission denied → Check file ownership
sudo chown -R root:root /opt/IPPL-FoodScanAI

# 3. Port already in use → Check what's using port 8000
sudo lsof -i :8000
```

### Frontend tidak muncul

```bash
# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Test Nginx config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Database slow

```bash
# Create indexes (jika belum ada)
psql -U dbuser foodscan

# Di psql:
CREATE INDEX idx_recipe_ingredients ON recipes USING gin(to_tsvector('indonesian', ingredients));
CREATE INDEX idx_recipe_title ON recipes(title);
\q
```

---

## 💰 Estimasi Biaya VPS

| Provider         | Specs                      | Price/Month   |
| ---------------- | -------------------------- | ------------- |
| **DigitalOcean** | 2 vCPU, 4GB RAM, 80GB SSD  | $24           |
| **Vultr**        | 2 vCPU, 4GB RAM, 80GB SSD  | $18           |
| **Linode**       | 2 vCPU, 4GB RAM, 80GB SSD  | $18           |
| **Contabo**      | 4 vCPU, 8GB RAM, 200GB SSD | €6.99 (~$7.5) |

**Rekomendasi:** Minimal 2GB RAM untuk YOLO model + PostgreSQL

---

## 📝 Checklist Deployment

- [ ] VPS Ubuntu 22.04+ ready
- [ ] PostgreSQL installed & database created
- [ ] Backend deployed & service running
- [ ] Frontend built & served by Nginx
- [ ] Nginx reverse proxy configured
- [ ] SSL certificate installed (optional)
- [ ] Database populated dengan 14,945 recipes
- [ ] Test upload gambar → recipes muncul
- [ ] Auto-start services enabled
- [ ] Backup script setup (optional)

---

## 🎓 Untuk Penjelasan ke Dosen

**Arsitektur Deployment:**

1. **Database Layer**: PostgreSQL di VPS untuk data persistence & concurrent access
2. **Backend Layer**: FastAPI dengan Uvicorn workers untuk handle multiple requests
3. **Frontend Layer**: React build di-serve sebagai static files via Nginx
4. **Reverse Proxy**: Nginx routing `/api/*` ke backend, `/` ke frontend
5. **Process Manager**: Systemd untuk auto-restart & monitoring backend service

**Keuntungan Arsitektur Ini:**

- ✅ Scalable: Bisa tambah workers/server
- ✅ Reliable: Auto-restart jika crash
- ✅ Secure: SSL/HTTPS support
- ✅ Production-ready: Logging, monitoring, backup
- ✅ Cost-effective: Single VPS bisa handle 100+ concurrent users

---

## 📞 Support

Jika ada masalah saat deployment, check:

1. Backend logs: `sudo journalctl -u foodscan-backend -f`
2. Nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. PostgreSQL logs: `sudo tail -f /var/log/postgresql/postgresql-*.log`
