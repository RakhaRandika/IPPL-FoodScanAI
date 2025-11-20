from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import cv2
import io
from pathlib import Path
from ultralytics import YOLO
import sys
import torch


# Fix for PyTorch 2.6+ weights_only=True issue - PATCH torch.load
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs.setdefault('weights_only', False)
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load
print("✅ PyTorch torch.load patched to use weights_only=False")

# Allow ultralytics classes to be loaded safely
try:
    from ultralytics.nn.tasks import DetectionModel
    torch.serialization.add_safe_globals([DetectionModel])
except Exception as e:
    print(f"⚠️  Warning: Could not add safe globals: {e}")

# Add parent directory to path untuk import
sys.path.insert(0, str(Path(__file__).parent.parent))

# Model Path
MODEL_PATH = Path(__file__).parent / "models" / "models_yolo" / "best (3).pt"

# Global model variable
_model = None

def get_model():
    """Load YOLOv8 model (singleton)"""
    global _model
    if _model is None:
        print(f"Loading YOLOv8 model from: {MODEL_PATH}")
        try:
            _model = YOLO(str(MODEL_PATH))
            print(f"✅ Model loaded successfully!")
            print(f"📋 Classes: {_model.names}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    return _model

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler untuk startup dan shutdown"""
    # Startup
    print("\n" + "="*60)
    print("🚀 FoodScanAI Backend Starting...")
    print("="*60)
    
    try:
        model = get_model()
        print(f"✅ Model YOLOv8 berhasil dimuat!")
        print(f"📁 Path: {MODEL_PATH}")
        print(f"🏷️  Jumlah kelas: {len(model.names)}")
        print(f"📋 Kelas yang dapat dideteksi:")
        
        # Tampilkan kelas dalam format grid
        classes = list(model.names.values())
        for i in range(0, len(classes), 4):
            row = classes[i:i+4]
            print("   " + " | ".join(f"{c:<15}" for c in row))
        
        # Load recipe dataset
        print("\n" + "-"*60)
        print("📚 Loading Recipe Dataset...")
        from app.services.recipe_service import recipe_service
        recipe_count = len(recipe_service.recipes_df) if recipe_service.recipes_df is not None else 0
        print(f"✅ {recipe_count:,} recipes loaded from Kaggle dataset")
        print("-"*60)
        
        print("="*60)
        print("✅ Backend siap digunakan!")
        print("📖 API Docs: http://127.0.0.1:8000/docs")
        print("📷 Camera Stream: http://127.0.0.1:8000/camera/stream")
        print("🍳 Recipe API: http://127.0.0.1:8000/api/recipes/")
        print("="*60 + "\n")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        raise
    
    yield
    
    # Shutdown
    print("\n🛑 Shutting down backend...")

app = FastAPI(
    title="FoodScanAI API",
    description="API untuk deteksi makanan menggunakan YOLOv8",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
try:
    from app.routes import scan, recipe, nutrition
    app.include_router(scan.router)
    app.include_router(recipe.router)
    app.include_router(nutrition.router)
except ImportError as e:
    print(f"Import error: {e}")
    # Jika dijalankan langsung dengan python app/main.py
    try:
        from routes import scan, recipe, nutrition
        app.include_router(scan.router)
        app.include_router(recipe.router)
        app.include_router(nutrition.router)
    except ImportError as e2:
        print(f"Second import error: {e2}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Selamat datang di FoodScanAI!",
        "version": "1.0.0",
        "endpoints": {
            "scan": "/api/scan",
            "health": "/api/scan/health",
            "camera_stream": "/camera/stream",
            "camera_capture": "/camera/capture",
            "camera_stream_detect": "/camera/stream/detect",
            "camera_capture_scan": "/camera/capture/scan",
            "camera_status": "/camera/status",
            "recipe_recommend": "/api/recipes/recommend",
            "recipe_search": "/api/recipes/search",
            "recipe_detail": "/api/recipes/{id}",
            "nutrition_batch": "/api/nutrition/batch",
            "nutrition_single": "/api/nutrition/{ingredient}",
            "nutrition_known": "/api/nutrition/known",
            "docs": "/docs"
        }
    }

# ============================================================
# CAMERA ENDPOINTS
# ============================================================

class CameraManager:
    """Manage camera access"""
    def __init__(self):
        self.camera = None
        self.is_streaming = False
    
    def get_camera(self):
        """Get or initialize camera"""
        if self.camera is None or not self.camera.isOpened():
            self.camera = cv2.VideoCapture(0)  # 0 = default camera
            if not self.camera.isOpened():
                raise Exception("Cannot access camera")
        return self.camera
    
    def release_camera(self):
        """Release camera resource"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            self.is_streaming = False

# Global camera manager
camera_manager = CameraManager()

@app.get("/camera/stream")
async def camera_stream():
    """Stream video dari kamera (MJPEG format)"""
    def generate_frames():
        camera = camera_manager.get_camera()
        camera_manager.is_streaming = True
        
        try:
            while camera_manager.is_streaming:
                success, frame = camera.read()
                if not success:
                    break
                
                # Encode frame ke JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                
                frame_bytes = buffer.tobytes()
                
                # Yield frame dalam format MJPEG
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        finally:
            camera_manager.release_camera()
    
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/camera/capture")
async def camera_capture():
    """Capture single frame dari kamera"""
    try:
        camera = camera_manager.get_camera()
        
        # Capture frame
        success, frame = camera.read()
        if not success:
            raise Exception("Failed to capture frame")
        
        # Encode ke JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            raise Exception("Failed to encode frame")
        
        # Release camera setelah capture
        camera_manager.release_camera()
        
        # Return image
        return StreamingResponse(
            io.BytesIO(buffer.tobytes()),
            media_type="image/jpeg"
        )
    except Exception as e:
        camera_manager.release_camera()
        return {"error": str(e)}

@app.post("/camera/stop")
async def camera_stop():
    """Stop camera streaming"""
    camera_manager.is_streaming = False
    camera_manager.release_camera()
    return {"message": "Camera stopped"}

@app.get("/camera/status")
async def camera_status():
    """Check camera status"""
    try:
        camera = cv2.VideoCapture(0)
        is_available = camera.isOpened()
        camera.release()
        return {
            "available": is_available,
            "streaming": camera_manager.is_streaming
        }
    except Exception as e:
        return {
            "available": False,
            "streaming": False,
            "error": str(e)
        }

# ============================================================
# CAMERA + YOLO DETECTION ENDPOINT
# ============================================================

@app.get("/camera/stream/detect")
async def camera_stream_with_detection():
    """Stream video dengan deteksi real-time"""
    def generate_frames():
        model = get_model()
        camera = camera_manager.get_camera()
        camera_manager.is_streaming = True
        
        try:
            while camera_manager.is_streaming:
                success, frame = camera.read()
                if not success:
                    break
                
                # Run YOLOv8 detection dengan confidence lebih rendah
                results = model(frame, conf=0.15)
                
                # Draw bounding boxes
                annotated_frame = results[0].plot()
                
                # Encode frame ke JPEG
                ret, buffer = cv2.imencode('.jpg', annotated_frame)
                if not ret:
                    continue
                
                frame_bytes = buffer.tobytes()
                
                # Yield frame dalam format MJPEG
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        finally:
            camera_manager.release_camera()
    
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.post("/camera/capture/scan")
async def camera_capture_and_scan(confidence: float = 0.15):
    """Capture frame dan scan dengan YOLOv8, lengkap dengan nutrisi dan rekomendasi resep"""
    try:
        model = get_model()
        camera = camera_manager.get_camera()
        
        # Capture frame
        success, frame = camera.read()
        if not success:
            raise Exception("Failed to capture frame")
        
        # Release camera
        camera_manager.release_camera()
        
        # Run detection dengan confidence threshold
        results = model(frame, conf=confidence)
        
        # Parse results
        predictions = []
        detected_labels = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0])
                    conf_score = float(box.conf[0])
                    label = model.names[class_id]
                    
                    # Bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    predictions.append({
                        "label": label,
                        "confidence": round(conf_score * 100, 2),
                        "bounding_box": {
                            "x1": round(x1, 2),
                            "y1": round(y1, 2),
                            "x2": round(x2, 2),
                            "y2": round(y2, 2)
                        }
                    })
                    detected_labels.append(label)
        
        if len(predictions) == 0:
            return {
                "success": False,
                "message": "Tidak ada makanan terdeteksi dalam gambar",
                "predictions": [],
                "count": 0,
                "detected_ingredients": [],
                "recommended_recipes": [],
                "nutrition_info": None
            }
        
        # Get unique detected ingredients
        unique_labels = list(set(detected_labels))
        print(f"🔍 DEBUG: Detected ingredients: {unique_labels}")
        
        # Get recipe recommendations
        recommended_recipes = []
        try:
            from app.services.recipe_service import recipe_service
            print(f"📚 DEBUG: Searching recipes for: {unique_labels}")
            recommended_recipes = recipe_service.search_recipes(unique_labels, max_results=5)
            print(f"✅ DEBUG: Found {len(recommended_recipes)} recipes")
            if len(recommended_recipes) > 0:
                print(f"   Top recipe: {recommended_recipes[0].get('name', 'N/A')}")
        except Exception as recipe_error:
            print(f"❌ Recipe recommendation error: {recipe_error}")
            import traceback
            traceback.print_exc()
        
        # Get nutrition information
        nutrition_info = None
        try:
            from app.services.nutrition_service import get_nutrition_for_ingredients
            print(f"🥗 DEBUG: Getting nutrition for: {unique_labels}")
            nutrition_info = get_nutrition_for_ingredients(unique_labels)
            print(f"✅ DEBUG: Got nutrition info: {nutrition_info is not None}")
            if nutrition_info:
                print(f"   Total calories: {nutrition_info.get('total', {}).get('calories', 'N/A')}")
        except Exception as nutrition_error:
            print(f"❌ Nutrition lookup error: {nutrition_error}")
            import traceback
            traceback.print_exc()
        
        result = {
            "success": True,
            "message": f"Terdeteksi {len(predictions)} objek makanan",
            "predictions": predictions,
            "count": len(predictions),
            "detected_ingredients": unique_labels,
            "recommended_recipes": recommended_recipes,
            "nutrition_info": nutrition_info
        }
        
        print(f"📦 DEBUG: Returning {len(recommended_recipes)} recipes and nutrition: {nutrition_info is not None}")
        return result
    
    except Exception as e:
        camera_manager.release_camera()
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "predictions": [],
            "count": 0,
            "detected_ingredients": [],
            "recommended_recipes": [],
            "nutrition_info": None
        }


# Run dengan uvicorn (recommended)
if __name__ == "__main__":
    import uvicorn
    print("\n⚡ Starting server with uvicorn...")
    print("💡 Tip: Gunakan 'uvicorn app.main:app --reload' untuk auto-reload\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)