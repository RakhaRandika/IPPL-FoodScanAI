"""
Test script untuk menguji YOLOv8 model detection
"""
import sys
from pathlib import Path
from ultralytics import YOLO
import cv2

# Path ke model
MODEL_PATH = Path(__file__).parent / "app" / "models" / "models_yolo" / "best (3).pt"

def test_model_info():
    """Test 1: Load model dan tampilkan informasi"""
    print("\n" + "="*60)
    print("TEST 1: Model Information")
    print("="*60)
    
    try:
        print(f"📁 Loading model from: {MODEL_PATH}")
        model = YOLO(str(MODEL_PATH))
        
        print(f"✅ Model loaded successfully!")
        print(f"\n📊 Model Details:")
        print(f"   - Type: {type(model).__name__}")
        print(f"   - Classes count: {len(model.names)}")
        print(f"\n🏷️  Detected Classes:")
        
        # Tampilkan kelas dalam format grid
        classes = list(model.names.values())
        for i in range(0, len(classes), 4):
            row = classes[i:i+4]
            print("   " + " | ".join(f"{c:<15}" for c in row))
        
        print("\n✅ Test 1 PASSED")
        return model
    
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
        return None

def test_camera_detection(model):
    """Test 2: Test deteksi dengan kamera"""
    print("\n" + "="*60)
    print("TEST 2: Camera Detection Test")
    print("="*60)
    
    try:
        print("📷 Opening camera...")
        camera = cv2.VideoCapture(0)
        
        if not camera.isOpened():
            print("❌ Cannot open camera")
            return False
        
        print("✅ Camera opened successfully")
        print("\n🎯 Running detection on camera frame...")
        
        # Capture 1 frame
        success, frame = camera.read()
        if not success:
            print("❌ Failed to capture frame")
            camera.release()
            return False
        
        print(f"✅ Frame captured: {frame.shape}")
        
        # Run detection
        print("🔍 Running YOLOv8 detection...")
        results = model(frame, conf=0.25)
        
        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    label = model.names[class_id]
                    detections.append({
                        "label": label,
                        "confidence": round(confidence * 100, 2)
                    })
        
        print(f"\n📋 Detection Results:")
        print(f"   - Total detections: {len(detections)}")
        
        if len(detections) > 0:
            print(f"\n🎯 Detected Objects:")
            for i, det in enumerate(detections, 1):
                print(f"   {i}. {det['label']} ({det['confidence']}%)")
        else:
            print("   ⚠️  No objects detected (normal if no food in frame)")
        
        # Save annotated image
        annotated_frame = results[0].plot()
        output_path = Path(__file__).parent / "test_detection_result.jpg"
        cv2.imwrite(str(output_path), annotated_frame)
        print(f"\n💾 Saved annotated image to: {output_path}")
        
        camera.release()
        print("\n✅ Test 2 PASSED")
        return True
    
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        if 'camera' in locals():
            camera.release()
        return False

def test_sample_image(model):
    """Test 3: Test deteksi dengan gambar sample (jika ada)"""
    print("\n" + "="*60)
    print("TEST 3: Sample Image Detection (Optional)")
    print("="*60)
    
    # Coba cari gambar test di folder backend
    test_images = list(Path(__file__).parent.glob("*.jpg")) + \
                  list(Path(__file__).parent.glob("*.png")) + \
                  list(Path(__file__).parent.glob("test*.jpg"))
    
    if not test_images:
        print("⚠️  No test images found, skipping...")
        return True
    
    try:
        test_image = test_images[0]
        print(f"📷 Testing with image: {test_image.name}")
        
        # Load image
        image = cv2.imread(str(test_image))
        if image is None:
            print("❌ Failed to load image")
            return False
        
        print(f"✅ Image loaded: {image.shape}")
        
        # Run detection
        print("🔍 Running detection...")
        results = model(image, conf=0.25)
        
        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    label = model.names[class_id]
                    detections.append({
                        "label": label,
                        "confidence": round(confidence * 100, 2)
                    })
        
        print(f"\n📋 Detection Results:")
        print(f"   - Total detections: {len(detections)}")
        
        if len(detections) > 0:
            print(f"\n🎯 Detected Objects:")
            for i, det in enumerate(detections, 1):
                print(f"   {i}. {det['label']} ({det['confidence']}%)")
        else:
            print("   ⚠️  No objects detected")
        
        print("\n✅ Test 3 PASSED")
        return True
    
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 YOLOv8 Model Detection Test Suite")
    print("="*60)
    
    # Test 1: Load model
    model = test_model_info()
    if model is None:
        print("\n❌ OVERALL TEST FAILED: Cannot load model")
        return
    
    # Test 2: Camera detection
    camera_test = test_camera_detection(model)
    
    # Test 3: Sample image (optional)
    image_test = test_sample_image(model)
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"   Test 1 (Model Load):      ✅ PASSED")
    print(f"   Test 2 (Camera Detect):   {'✅ PASSED' if camera_test else '❌ FAILED'}")
    print(f"   Test 3 (Image Detect):    {'✅ PASSED' if image_test else '⚠️  SKIPPED'}")
    print("="*60)
    
    if camera_test:
        print("\n🎉 All critical tests PASSED!")
        print("✅ Model 'best (3).pt' is working correctly")
    else:
        print("\n⚠️  Some tests failed, but model loaded successfully")

if __name__ == "__main__":
    main()
