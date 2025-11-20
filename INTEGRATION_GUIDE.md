# 🚀 Panduan Lengkap Integrasi YOLOv8 dengan FastAPI

## ✅ Yang Sudah Dibuat

### 1. Backend API (`backend/app/routes/scan.py`)

- ✅ Endpoint POST `/api/scan` untuk deteksi makanan
- ✅ Endpoint GET `/api/scan/health` untuk health check
- ✅ Integrasi YOLOv8 dengan model `best.pt`
- ✅ Parse hasil deteksi (label, confidence, bounding box)
- ✅ Error handling lengkap
- ✅ Automatic cleanup file temporary

### 2. Dependencies (`backend/requirements.txt`)

- ✅ FastAPI, Uvicorn
- ✅ Ultralytics (YOLOv8)
- ✅ PyTorch, OpenCV, NumPy
- ✅ Python-multipart untuk upload file

### 3. Frontend Service (`src/services/api.js`)

- ✅ Service untuk komunikasi dengan backend
- ✅ Fungsi `scanFood()` untuk upload dan scan
- ✅ Fungsi `checkHealth()` untuk health check
- ✅ Error handling

### 4. Dokumentasi & Scripts

- ✅ README backend lengkap
- ✅ Script test API (`test_api.py`)
- ✅ Script run server (`run_server.ps1`)
- ✅ Contoh integrasi frontend

---

## 🎯 Cara Menjalankan

### Step 1: Install Backend Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### Step 2: Pastikan Model Ada

Model YOLOv8 harus ada di:

```
backend/app/models/models_yolo/best.pt
```

### Step 3: Jalankan Backend Server

**Opsi A: Dengan script**

```powershell
cd backend
.\run_server.ps1
```

**Opsi B: Manual**

```powershell
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di: **http://localhost:8000**

### Step 4: Test Backend API

**Test dengan browser:**

- Health check: http://localhost:8000/api/scan/health
- Docs: http://localhost:8000/docs

**Test dengan script Python:**

```powershell
cd backend
python test_api.py path/to/test_image.jpg 0.5
```

**Test dengan curl:**

```powershell
curl.exe -X POST "http://localhost:8000/api/scan" -F "file=@test_image.jpg"
```

### Step 5: Jalankan Frontend

Di terminal baru:

```powershell
cd d:\IPPL\FoodScanAI
npm start
```

Frontend akan berjalan di: **http://localhost:3000**

---

## 📡 API Endpoints

### 1. POST `/api/scan` - Deteksi Makanan

**Request:**

```javascript
POST /api/scan
Content-Type: multipart/form-data

Body:
- file: image file (required)
- confidence: float 0.0-1.0 (optional, default 0.5)
```

**Response Success:**

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

**Response No Detection:**

```json
{
  "success": true,
  "message": "Tidak ada makanan terdeteksi dalam gambar",
  "predictions": [],
  "count": 0
}
```

**Response Error:**

```json
{
  "detail": "File harus berupa gambar"
}
```

### 2. GET `/api/scan/health` - Health Check

**Response:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "path/to/best.pt"
}
```

---

## 🔗 Integrasi Frontend

### Import Service

```javascript
import { scanFood, checkHealth } from "./services/api";
```

### Contoh Penggunaan

```javascript
// Health check saat component mount
useEffect(() => {
  checkHealth()
    .then((res) => console.log("Backend ready:", res))
    .catch((err) => console.error("Backend error:", err));
}, []);

// Scan makanan dari file upload
const handleScan = async (file) => {
  try {
    setLoading(true);
    const result = await scanFood(file, 0.5);

    if (result.success && result.predictions.length > 0) {
      // Tampilkan hasil deteksi
      console.log("Detected foods:", result.predictions);
      setResults(result.predictions);
    } else {
      alert("Tidak ada makanan terdeteksi");
    }
  } catch (error) {
    alert("Error: " + error.message);
  } finally {
    setLoading(false);
  }
};
```

### Update UploadCard Component

Lihat contoh lengkap di: `src/examples/integration_example.js`

---

## 🐛 Troubleshooting

### Model tidak ditemukan

```
Error: Model tidak ditemukan di: backend/app/models/models_yolo/best.pt
```

**Solusi:** Pastikan file `best.pt` ada di path tersebut

### Import error ultralytics

```
ModuleNotFoundError: No module named 'ultralytics'
```

**Solusi:**

```powershell
pip install ultralytics
```

### CORS Error di Frontend

```
Access to fetch at 'http://localhost:8000/api/scan' from origin 'http://localhost:3000' has been blocked
```

**Solusi:** Sudah dikonfigurasi di `main.py`, pastikan frontend URL ada di array `origins`

### Port sudah digunakan

```
ERROR: Address already in use
```

**Solusi:** Ganti port atau kill process yang menggunakan port 8000:

```powershell
# Cari process
netstat -ano | findstr :8000

# Kill process (ganti PID)
taskkill /PID <PID> /F
```

---

## 📊 Struktur Response YOLOv8

Model YOLOv8 mendeteksi:

1. **Label** - Nama makanan yang terdeteksi
2. **Confidence** - Tingkat keyakinan (0-100%)
3. **Bounding Box** - Koordinat kotak deteksi (x1, y1, x2, y2)

Setiap gambar bisa menghasilkan multiple detections jika ada beberapa objek makanan.

---

## 🎨 Contoh Visualisasi

Untuk menampilkan bounding box di frontend, gunakan koordinat:

- `x1, y1` = titik kiri atas
- `x2, y2` = titik kanan bawah

```javascript
const drawBoundingBox = (ctx, bbox, label, confidence) => {
  ctx.strokeStyle = "#00ff00";
  ctx.lineWidth = 2;
  ctx.strokeRect(bbox.x1, bbox.y1, bbox.x2 - bbox.x1, bbox.y2 - bbox.y1);

  ctx.fillStyle = "#00ff00";
  ctx.font = "16px Arial";
  ctx.fillText(`${label} ${confidence}%`, bbox.x1, bbox.y1 - 5);
};
```

---

## 📝 Next Steps

1. ✅ Backend API sudah siap
2. ✅ Frontend service sudah dibuat
3. 🔄 Update `UploadCard.jsx` untuk menggunakan API
4. 🔄 Tampilkan hasil deteksi di `AnalysisResults.jsx`
5. 🔄 Optional: Tambah visualisasi bounding box
6. 🔄 Optional: Integrate dengan nutrition API

---

## 💡 Tips

1. **Development:** Gunakan `--reload` untuk auto-reload backend
2. **Testing:** Test backend dulu dengan curl sebelum integrasi frontend
3. **Debugging:** Cek log di terminal backend untuk error details
4. **Performance:** Model di-load sekali saat startup (lazy loading)
5. **Security:** Untuk production, tambahkan rate limiting & validation

---

## 📚 Referensi

- FastAPI Docs: https://fastapi.tiangolo.com/
- Ultralytics YOLOv8: https://docs.ultralytics.com/
- React Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

---

**Status:** ✅ Backend API ready to use!
**Next:** Integrasikan dengan frontend UploadCard component
