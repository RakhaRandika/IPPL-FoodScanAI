# FoodScanAI Backend

Backend FastAPI untuk deteksi makanan menggunakan YOLOv8.

## Setup

### 1. Install Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 2. Pastikan Model Ada

Model YOLOv8 harus tersedia di:

```
backend/app/models/models_yolo/best.pt
```

### 3. Jalankan Server

```powershell
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di: `http://localhost:8000`

## API Endpoints

### 1. Scan Makanan

**POST** `/api/scan`

Upload gambar untuk deteksi makanan.

**Request:**

- Method: POST
- Content-Type: multipart/form-data
- Body:
  - `file`: File gambar (JPG, PNG, dll)
  - `confidence`: (optional) Threshold confidence 0.0-1.0, default 0.5

**Response:**

```json
{
  "success": true,
  "message": "Terdeteksi 2 objek makanan",
  "predictions": [
    {
      "label": "ayam",
      "confidence": 95.5,
      "bounding_box": {
        "x1": 100.5,
        "y1": 150.2,
        "x2": 300.8,
        "y2": 400.5
      }
    }
  ],
  "count": 2
}
```

**Contoh dengan curl:**

```powershell
curl.exe -X POST "http://localhost:8000/api/scan" -F "file=@path/to/image.jpg" -F "confidence=0.6"
```

### 2. Health Check

**GET** `/api/scan/health`

Cek status model dan API.

**Response:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "path/to/best.pt"
}
```

### 3. Root Endpoint

**GET** `/`

**Response:**

```json
{
  "message": "Selamat datang di FoodScanAI!"
}
```

## Testing

### Test dengan curl (PowerShell)

```powershell
# Test health check
curl.exe http://localhost:8000/api/scan/health

# Test upload gambar
curl.exe -X POST "http://localhost:8000/api/scan" -F "file=@test_image.jpg"
```

### Test dengan Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/scan/health")
print(response.json())

# Upload gambar
with open("test_image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/api/scan", files=files)
    print(response.json())
```

## Struktur Folder

```
backend/
├── app/
│   ├── main.py              # Entry point FastAPI
│   ├── config.py            # Konfigurasi
│   ├── models/
│   │   ├── models_yolo/
│   │   │   └── best.pt      # Model YOLOv8
│   │   └── recipe.py
│   ├── routes/
│   │   ├── scan.py          # Endpoint scan/deteksi
│   │   ├── nutrition.py     # Endpoint nutrisi
│   │   └── recipe.py        # Endpoint resep
│   └── services/
│       ├── ai_service.py
│       ├── nutrition_api.py
│       ├── nutrition_service.py
│       └── recipe_service.py
├── tests/
├── requirements.txt
└── README.md
```

## Troubleshooting

### Model tidak ditemukan

Pastikan file `best.pt` ada di `backend/app/models/models_yolo/best.pt`

### Error import ultralytics

```powershell
pip install ultralytics
```

### Error CORS

Pastikan frontend URL sudah ditambahkan di `main.py` di array `origins`

## Development

Server akan auto-reload saat ada perubahan code (mode `--reload`).

Dokumentasi API interaktif tersedia di:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
