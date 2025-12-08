# 🍽️ FoodScanAI - Smart Food Detection System

Sistem deteksi makanan berbasis YOLOv8 dengan rekomendasi resep dan informasi nutrisi.

## 📋 Features

- ✅ **25 Kelas Makanan** (Daging Sapi, Ayam, Ikan, Sayuran, dll)
- ✅ **25,768+ Resep** dari 5 dataset tergabung
- ✅ **Informasi Nutrisi** lengkap untuk semua bahan
- ✅ **Rekomendasi Resep** dengan weighted scoring
- ✅ **Deteksi Real-time** via camera atau upload
- ✅ **Dual Language** (English + Indonesian)

---

## 🚀 Quick Start

### Option 1: Docker (Recommended) 🐳

```powershell
# Deploy dengan PostgreSQL
.\deploy_docker.ps1

# Akses aplikasi
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

**[Lihat dokumentasi Docker lengkap →](DOCKER_README.md)**

### Option 2: Local Development

#### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend

```powershell
cd frontend
npm install
npm start
```

---

## 📊 Database

### SQLite (Local Development)

- Location: `backend/foodscan.db`
- Recipes: 25,768
- Auto-generated dari CSV files

### PostgreSQL (Docker Production)

- Host: localhost:5432
- Database: foodscan_db
- User: foodscan_user
- Migrated from SQLite

---

## 🎯 YOLOv8 Model

**Model**: `backend/app/models/models_yolo/best (3).pt`

**25 Classes**:

- **Protein**: Beef, Chicken, Pork, Egg, Galunggong, Milkfish, Tilapia
- **Vegetables**: Cabbage, Carrot, Cauliflower, Chayote, Corn, Eggplant, Green Beans, Kangkong, Long Beans, Mushroom, Potato, Radish, Tomato, Zucchini
- **Spices**: Garlic, Ginger, Onion
- **Fruit**: Papaya

**Settings**:

- Confidence: 60%
- IoU: 0.45
- Max Detections: 50

---

## 📁 Project Structure

```
FoodScanAI/
├── backend/
│   ├── app/
│   │   ├── routes/       # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── database/     # SQLAlchemy models
│   │   ├── models/       # YOLO model files
│   │   └── data/         # CSV datasets
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API calls
│   │   └── views/        # Pages
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── migrate_to_docker.py
└── deploy_docker.ps1
```

---

## 🔧 Configuration

### Backend Environment Variables

**Docker** (`backend/.env`):

```env
DATABASE_URL=postgresql://foodscan_user:foodscan_password@postgres:5432/foodscan_db
MODEL_PATH=./app/models/models_yolo/best (3).pt
```

**Local** (`backend/.env.local`):

```env
DATABASE_URL=sqlite:///./foodscan.db
MODEL_PATH=./app/models/models_yolo/best (3).pt
```

---

## 📖 API Endpoints

### Scan Food

```http
POST /api/scan
Content-Type: multipart/form-data

file: <image_file>
confidence: 0.6 (optional)
max_results: 1000 (optional, max 10000)
```

### Search Recipes

```http
POST /api/recipe/search
Content-Type: application/json

{
  "ingredients": ["daging sapi", "bawang merah"],
  "max_results": 100
}
```

### Get Nutrition

```http
POST /api/nutrition/analyze
Content-Type: application/json

{
  "ingredients": ["ayam", "wortel"],
  "portion_grams": 100
}
```

---

## 🧪 Testing

```powershell
cd backend
pytest tests/ -v
```

Test Coverage:

- ✅ Model loading
- ✅ Detection accuracy
- ✅ Recipe search
- ✅ Nutrition mapping
- ✅ API endpoints

---

## 📚 Documentation

- **[Docker Setup Guide](DOCKER_SETUP.md)** - Deployment lengkap
- **[Docker README](DOCKER_README.md)** - Quick reference
- **[Integration Guide](INTEGRATION_GUIDE.md)** - API integration
- **[Deployment VPS](DEPLOYMENT_VPS.md)** - Production deployment

---

## 🛠️ Tech Stack

### Backend

- FastAPI (Python 3.11+)
- YOLOv8 (Ultralytics)
- PostgreSQL / SQLite
- SQLAlchemy 2.0
- OpenCV
- PyTorch

### Frontend

- React 18
- TailwindCSS
- Nginx (production)

### DevOps

- Docker & Docker Compose
- Multi-stage builds
- Health checks
- Volume persistence

---

## 📊 Database Stats

- **Total Recipes**: 25,768
- **Dataset Sources**: 5 CSV files
  - resep_dataset.csv (14,945)
  - resep_dataset2.csv (13,501)
  - dataset-sapi.csv (1,958)
  - dataset-ikan.csv (1,932)
  - dataset-ayam.csv (1,916)
- **De-duplicated**: 34,252 → 25,768

---

## 🎯 Recipe Matching Logic

### Weighted Scoring:

- **Protein**: +20 points
- **Vegetables**: +10 points
- **Spices**: +5 points
- **Title Match**: +30 points

### Features:

- Species-specific detection (Bandeng, Galunggong, Nila)
- Dual-language keywords (English + Indonesian)
- Processed dish filtering (exclude "mie ayam", etc.)
- Strict matching (ALL ingredients required)

---

## 🚀 Deployment

### Docker (Recommended)

```powershell
.\deploy_docker.ps1
```

### Manual

```powershell
# Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
npx serve -s build -l 3000
```

---

## 📝 License

MIT License - Feel free to use for educational purposes.

---

## 👥 Contributors

- **Rakha Randika** - Initial work & Docker migration

---

## 🙏 Acknowledgments

- Ultralytics YOLOv8
- FastAPI Framework
- React Community
- Dataset contributors (5 recipe datasets)

---

**Last Updated**: December 2025
**Version**: 2.0.0 (Docker Ready)
