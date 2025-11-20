from fastapi import APIRouter, UploadFile, File, HTTPException
from ultralytics import YOLO
import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any

router = APIRouter(prefix="/api", tags=["scan"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "models_yolo", "best (3).pt")

# Load model sekali di awal
model = None

def get_model():
    """Lazy load model untuk efisiensi"""
    global model
    if model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model tidak ditemukan di: {MODEL_PATH}")
        print(f"📦 Loading YOLOv8 model dari: {MODEL_PATH}")
        model = YOLO(MODEL_PATH)
        print(f"✅ Model loaded successfully! Classes: {len(model.names)}")
    return model

def detect_food(image_path: str, conf_threshold: float = 0.5):
    """Deteksi makanan menggunakan YOLOv8"""
    model = get_model()
    results = model.predict(source=image_path, conf=conf_threshold)
    return results

@router.post("/scan")
async def scan_food(
    file: UploadFile = File(...),
    confidence: float = 0.5
):
    """
    Endpoint untuk scan/deteksi makanan dari gambar
    
    Parameters:
    - file: File gambar yang akan di-scan
    - confidence: Threshold confidence (0.0 - 1.0), default 0.5
    
    Returns:
    - predictions: List deteksi makanan dengan label, confidence, dan bounding box
    """
    
    # Validasi file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar")
    
    # Validasi confidence
    if not 0.0 <= confidence <= 1.0:
        raise HTTPException(status_code=400, detail="Confidence harus antara 0.0 - 1.0")
    
    # Simpan file sementara
    temp_dir = tempfile.mkdtemp()
    temp_file_path = None
    
    try:
        # Buat path file sementara
        file_extension = Path(file.filename).suffix or ".jpg"
        temp_file_path = os.path.join(temp_dir, f"uploaded{file_extension}")
        
        # Simpan uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Deteksi menggunakan YOLO
        results = detect_food(temp_file_path, conf_threshold=confidence)
        
        # Debug logging
        print(f"\n=== YOLO Detection Debug ===")
        print(f"Confidence threshold: {confidence}")
        print(f"Results count: {len(results) if results else 0}")
        
        # Parse hasil deteksi
        predictions = []
        if results and len(results) > 0:
            result = results[0]  # Ambil hasil pertama
            
            print(f"Result boxes: {result.boxes}")
            print(f"Result boxes length: {len(result.boxes) if result.boxes is not None else 0}")
            
            # Cek apakah ada deteksi
            if result.boxes is not None and len(result.boxes) > 0:
                boxes = result.boxes
                names = result.names  # Dictionary class_id -> class_name
                
                print(f"Class names: {names}")
                
                for box in boxes:
                    # Ekstrak informasi box
                    class_id = int(box.cls[0])
                    confidence_score = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                    
                    # Dapatkan nama class
                    label = names.get(class_id, f"class_{class_id}")
                    
                    print(f"Detected: {label} with confidence {confidence_score}")
                    
                    predictions.append({
                        "label": label,
                        "confidence": round(confidence_score * 100, 2),  # Convert ke persen
                        "bounding_box": {
                            "x1": round(bbox[0], 2),
                            "y1": round(bbox[1], 2),
                            "x2": round(bbox[2], 2),
                            "y2": round(bbox[3], 2)
                        }
                    })
            else:
                print("No boxes detected!")
        
        print(f"Total predictions: {len(predictions)}")
        print(f"=== End Debug ===\n")
        
        # Jika tidak ada deteksi
        if not predictions:
            return {
                "success": True,
                "message": "Tidak ada makanan terdeteksi dalam gambar",
                "predictions": [],
                "count": 0
            }
        
        # Urutkan berdasarkan confidence tertinggi
        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Ekstrak ingredients yang terdeteksi untuk rekomendasi resep
        detected_ingredients = [pred["label"] for pred in predictions]
        
        # Dapatkan rekomendasi resep berdasarkan ingredients terdeteksi
        recommended_recipes = []
        if detected_ingredients:
            from app.services.recipe_service import recipe_service
            recommended_recipes = recipe_service.search_recipes(detected_ingredients, max_results=5)
        
        # Dapatkan informasi nutrisi untuk ingredients terdeteksi
        nutrition_info = None
        if detected_ingredients:
            from app.services.nutrition_service import get_nutrition_for_ingredients
            nutrition_info = get_nutrition_for_ingredients(detected_ingredients)
        
        return {
            "success": True,
            "message": f"Terdeteksi {len(predictions)} objek makanan",
            "predictions": predictions,
            "count": len(predictions),
            "detected_ingredients": detected_ingredients,
            "recommended_recipes": recommended_recipes,
            "nutrition_info": nutrition_info
        }
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Model tidak ditemukan: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saat memproses gambar: {str(e)}")
    finally:
        # Cleanup: hapus file sementara
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

@router.get("/scan/health")
async def health_check():
    """Health check untuk endpoint scan"""
    try:
        model = get_model()
        model_loaded = model is not None
        return {
            "status": "healthy",
            "model_loaded": model_loaded,
            "model_path": MODEL_PATH
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "model_loaded": False,
            "error": str(e)
        }
