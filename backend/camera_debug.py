"""
Diagnostic tool untuk troubleshoot camera detection
Menguji berbagai confidence threshold dan visualisasi hasil
"""
import cv2
from pathlib import Path
from ultralytics import YOLO
import time

# Path ke model
MODEL_PATH = Path(__file__).parent / "app" / "models" / "models_yolo" / "best (3).pt"

def test_camera_detection_debug():
    """Test deteksi dengan berbagai confidence level"""
    print("\n" + "="*60)
    print("🔍 Camera Detection Diagnostic Tool")
    print("="*60)
    
    # Load model
    print(f"\n📁 Loading model: {MODEL_PATH}")
    model = YOLO(str(MODEL_PATH))
    print(f"✅ Model loaded: {len(model.names)} classes")
    
    # Open camera
    print("\n📷 Opening camera...")
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("❌ Cannot open camera!")
        return
    
    print("✅ Camera opened successfully")
    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("="*60)
    print("  - Place food items in front of camera")
    print("  - Press 'q' to quit")
    print("  - Press 's' to save current frame")
    print("  - Press '1-5' to change confidence threshold:")
    print("    1 = 0.10 (very sensitive)")
    print("    2 = 0.15 (sensitive)")
    print("    3 = 0.25 (balanced)")
    print("    4 = 0.35 (strict)")
    print("    5 = 0.50 (very strict)")
    print("="*60 + "\n")
    
    # Confidence levels
    conf_levels = {
        ord('1'): 0.10,
        ord('2'): 0.15,
        ord('3'): 0.25,
        ord('4'): 0.35,
        ord('5'): 0.50,
    }
    
    current_conf = 0.15
    frame_count = 0
    detection_count = 0
    
    try:
        while True:
            success, frame = camera.read()
            if not success:
                print("❌ Failed to read frame")
                break
            
            frame_count += 1
            
            # Run detection
            start_time = time.time()
            results = model(frame, conf=current_conf, verbose=False)
            inference_time = (time.time() - start_time) * 1000
            
            # Parse detections
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
                            "confidence": confidence
                        })
            
            if len(detections) > 0:
                detection_count += 1
            
            # Draw annotated frame
            annotated_frame = results[0].plot()
            
            # Add info overlay
            h, w = annotated_frame.shape[:2]
            
            # Status bar background
            cv2.rectangle(annotated_frame, (0, 0), (w, 120), (0, 0, 0), -1)
            
            # Display info
            info_lines = [
                f"Confidence Threshold: {current_conf:.2f}",
                f"FPS: {1000/inference_time:.1f} | Inference: {inference_time:.1f}ms",
                f"Frame: {frame_count} | Detections: {len(detections)}",
                f"Detection Rate: {(detection_count/frame_count*100):.1f}%"
            ]
            
            y_offset = 25
            for line in info_lines:
                cv2.putText(annotated_frame, line, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y_offset += 25
            
            # Show detected objects
            if len(detections) > 0:
                y_text = h - 60
                cv2.rectangle(annotated_frame, (0, h - 80), (w, h), (0, 100, 0), -1)
                cv2.putText(annotated_frame, f"DETECTED: {len(detections)} objects", 
                           (10, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # List detected items
                y_text += 25
                det_text = ", ".join([f"{d['label']} ({d['confidence']*100:.0f}%)" 
                                     for d in detections[:3]])
                if len(det_text) > 80:
                    det_text = det_text[:80] + "..."
                cv2.putText(annotated_frame, det_text, (10, y_text), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display frame
            cv2.imshow('FoodScanAI - Camera Detection Debug', annotated_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n👋 Quitting...")
                break
            elif key == ord('s'):
                # Save frame
                filename = f"debug_frame_{frame_count}.jpg"
                cv2.imwrite(filename, annotated_frame)
                print(f"\n💾 Saved frame to: {filename}")
                print(f"   Detections in frame: {len(detections)}")
                for i, det in enumerate(detections, 1):
                    print(f"   {i}. {det['label']} ({det['confidence']*100:.1f}%)")
            elif key in conf_levels:
                current_conf = conf_levels[key]
                print(f"\n🎯 Changed confidence threshold to: {current_conf}")
                detection_count = 0
                frame_count = 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    finally:
        # Cleanup
        camera.release()
        cv2.destroyAllWindows()
        
        # Summary
        print("\n" + "="*60)
        print("📊 Session Summary")
        print("="*60)
        print(f"  Total Frames: {frame_count}")
        print(f"  Frames with Detections: {detection_count}")
        print(f"  Detection Rate: {(detection_count/frame_count*100) if frame_count > 0 else 0:.1f}%")
        print(f"  Final Confidence: {current_conf}")
        print("="*60)

def test_single_frame_multiple_conf():
    """Test satu frame dengan berbagai confidence level"""
    print("\n" + "="*60)
    print("🧪 Single Frame Multi-Confidence Test")
    print("="*60)
    
    # Load model
    print(f"\n📁 Loading model: {MODEL_PATH}")
    model = YOLO(str(MODEL_PATH))
    
    # Capture frame
    print("\n📷 Capturing frame from camera...")
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("❌ Cannot open camera!")
        return
    
    success, frame = camera.read()
    camera.release()
    
    if not success:
        print("❌ Failed to capture frame")
        return
    
    print(f"✅ Frame captured: {frame.shape}")
    
    # Test multiple confidence levels
    conf_levels = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
    
    print("\n" + "="*60)
    print("Testing different confidence thresholds:")
    print("="*60)
    
    best_conf = None
    max_detections = 0
    
    for conf in conf_levels:
        results = model(frame, conf=conf, verbose=False)
        
        detection_count = 0
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                detection_count = len(boxes)
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    label = model.names[class_id]
                    detections.append(f"{label} ({confidence*100:.1f}%)")
        
        status = "✅" if detection_count > 0 else "❌"
        print(f"\n{status} Confidence {conf:.2f}: {detection_count} detections")
        
        if detection_count > 0:
            for det in detections:
                print(f"     - {det}")
            
            if detection_count > max_detections:
                max_detections = detection_count
                best_conf = conf
    
    print("\n" + "="*60)
    print("📊 Recommendation")
    print("="*60)
    
    if best_conf is not None:
        print(f"✅ Recommended confidence threshold: {best_conf:.2f}")
        print(f"   (Found {max_detections} objects at this level)")
    else:
        print("⚠️  No objects detected at any confidence level")
        print("   Possible reasons:")
        print("   1. No food items in frame")
        print("   2. Poor lighting conditions")
        print("   3. Objects too far or too close")
        print("   4. Objects not in training dataset")
    
    print("="*60)

def main():
    """Run diagnostic tools"""
    print("\n" + "="*60)
    print("🔧 FoodScanAI Camera Detection Diagnostic")
    print("="*60)
    print("\nChoose test mode:")
    print("  1. Live camera debug (interactive)")
    print("  2. Single frame multi-confidence test")
    print("  3. Both tests")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        test_camera_detection_debug()
    elif choice == "2":
        test_single_frame_multiple_conf()
    elif choice == "3":
        test_single_frame_multiple_conf()
        print("\n\nStarting live camera debug in 3 seconds...")
        time.sleep(3)
        test_camera_detection_debug()
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
