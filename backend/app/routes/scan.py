from fastapi import APIRouter, UploadFile, File, HTTPException, Query
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

def translate_food_label(english_label: str) -> str:
    """Translate English food labels to Indonesian"""
    translations = {
        'potato': 'Kentang',
        'beef': 'Daging Sapi',
        'chicken': 'Ayam',
        'pork': 'Daging Babi',
        'egg': 'Telur',
        'eggplant': 'Terong',
        'galunggong': 'Ikan Galunggong',
        'milkfish': 'Ikan Bandeng',
        'tilapia': 'Ikan Nila',
        'tomato': 'Tomat',
        'carrots': 'Wortel',
        'cabbage': 'Kubis',
        'broccoli': 'Brokoli',
        'cauliflower': 'Kembang Kol',
        'pumpkin': 'Labu',
        'bittergourd': 'Pare',
        'bottlegourd': 'Labu Air',
        'sayote': 'Labu Siam',
        'pechay': 'Sawi',
        'waterspinach': 'Kangkung',
        'stringbeans': 'Buncis',
        'papaya': 'Pepaya',
        'onion': 'Bawang Merah',
        'garlic': 'Bawang Putih',
        'ginger': 'Jahe',
        'chili': 'Cabai'
    }
    return translations.get(english_label.lower(), english_label.title())

def detect_food(image_path: str, conf_threshold: float = 0.5):
    """Deteksi makanan menggunakan YOLOv8 dengan parameter multi-objek yang lebih baik"""
    model = get_model()
    

    results = model.predict(
        source=image_path,
        conf=conf_threshold,  
        iou=0.5,              
        agnostic_nms=False,   
        max_det=100,          
        verbose=False
    )
    return results

@router.post("/scan")
async def scan_food(
    file: UploadFile = File(...),
    confidence: float = Query(default=0.5, ge=0.0, le=1.0, description="YOLO confidence threshold (0.0-1.0)"),
    min_match: int = Query(default=1, ge=1, le=10, description="Minimal bahan yang harus match (1-10)"),
    max_results: int = Query(default=200, ge=5, le=500, description="Maksimal jumlah resep (default 200, fokus pada kualitas)")
):
    """
    Endpoint untuk scan/deteksi makanan dari gambar
    
    Parameters:
    - file: File gambar yang akan di-scan
    - confidence: YOLO confidence threshold (0.0-1.0), default 0.5
    - min_match: Minimal bahan yang harus match untuk resep (1-10), default 1
    - max_results: Maksimal resep yang dikembalikan (default 200, max 500)
    
    Returns:
    - predictions: List deteksi makanan dengan label, confidence, dan bounding box
    - recommended_recipes: List rekomendasi resep
    - nutrition_info: Informasi nutrisi
    """
    
    # Validasi file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar")
    
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
        print(f"YOLO Confidence threshold: {confidence}")
        print(f"Recipe min_match: {min_match}")
        print(f"Recipe max_results: {max_results}")
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
                    
                    print(f"✅ Detected: {label} with confidence {confidence_score*100:.2f}%")
                    
                    predictions.append({
                        "label": translate_food_label(label),
                        "confidence": round(confidence_score * 100, 2),  # Convert ke persen
                        "bounding_box": {
                            "x1": round(bbox[0], 2),
                            "y1": round(bbox[1], 2),
                            "x2": round(bbox[2], 2),
                            "y2": round(bbox[3], 2)
                        }
                    })
            else:
                print("⚠️ No boxes detected!")
        
        print(f"Total predictions: {len(predictions)}")
        print(f"=== End Debug ===\n")
        
        # Jika tidak ada deteksi
        if not predictions:
            return {
                "success": False,
                "message": "Tidak ada makanan terdeteksi dalam gambar. Coba gambar yang lebih jelas atau adjust confidence threshold.",
                "predictions": [],
                "count": 0,
                "detected_ingredients": [],
                "recommended_recipes": [],
                "nutrition_info": None,
                "settings": {
                    "yolo_confidence": confidence,
                    "min_match": min_match,
                    "max_results": max_results
                }
            }
        
        # Urutkan berdasarkan confidence tertinggi
        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Ekstrak ingredients yang terdeteksi untuk rekomendasi resep
        detected_ingredients = list(set([pred.get("label_en", pred["label"]) for pred in predictions]))
        
        print(f"\n🔍 Detected unique ingredients: {detected_ingredients}")
        
        # Dapatkan rekomendasi resep berdasarkan ingredients terdeteksi
        recommended_recipes = []
        if detected_ingredients:
            try:
                from app.services.recipe_service import recipe_service
                print(f"📚 Searching recipes with min_match={min_match}, max_results={max_results}")
                
                recommended_recipes = recipe_service.search_recipes(
                    ingredients=detected_ingredients,
                    min_match=min_match,     
                    max_results=max_results 
                )
                
                print(f"✅ Found {len(recommended_recipes)} recipes")
                
                if len(recommended_recipes) > 0:
                    print(f"   Top 3 recipes:")
                    for i, recipe in enumerate(recommended_recipes[:3], 1):
                        print(f"   {i}. {recipe.get('name', 'N/A')} - Match: {recipe.get('match_percentage', 0)}%")
            except Exception as recipe_error:
                print(f"❌ Recipe search error: {recipe_error}")
                import traceback
                traceback.print_exc()
        
        # Dapatkan informasi nutrisi untuk ingredients terdeteksi
        nutrition_info = None
        if detected_ingredients:
            try:
                from app.services.nutrition_service import get_nutrition_for_ingredients
                print(f"🥗 Getting nutrition info for: {detected_ingredients}")
                nutrition_info = get_nutrition_for_ingredients(detected_ingredients)
                print(f"✅ Nutrition info retrieved: {nutrition_info is not None}")
            except Exception as nutrition_error:
                print(f"❌ Nutrition error: {nutrition_error}")
                import traceback
                traceback.print_exc()
        
        return {
            "success": True,
            "message": f"Terdeteksi {len(predictions)} objek makanan, ditemukan {len(recommended_recipes)} resep yang cocok",
            "predictions": predictions,
            "count": len(predictions),
            "detected_ingredients": detected_ingredients,
            "recommended_recipes": recommended_recipes,
            "nutrition_info": nutrition_info,
            "total_recipes_found": len(recommended_recipes),
            "settings": {
                "yolo_confidence": confidence,
                "min_match": min_match,
                "max_results": max_results
            }
        }
        
    except FileNotFoundError as e:
        print(f"❌ FileNotFoundError: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model tidak ditemukan: {str(e)}")
    except Exception as e:
        print(f"❌ Error in scan_food: {str(e)}")
        import traceback
        traceback.print_exc()
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
            "model_path": MODEL_PATH,
            "model_classes": len(model.names) if model else 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "model_loaded": False,
            "error": str(e)
        }
