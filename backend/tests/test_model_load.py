"""
Script untuk test loading model YOLOv8
Jalankan: python test_model_load.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.routes.scan import get_model, MODEL_PATH

def test_model_loading():
    """Test apakah model dapat dimuat dengan benar"""
    
    print("\n" + "="*60)
    print("🧪 Testing YOLOv8 Model Loading")
    print("="*60)
    
    # Check if model file exists
    print(f"\n1. Checking model file...")
    print(f"   Path: {MODEL_PATH}")
    
    if os.path.exists(MODEL_PATH):
        print(f"   ✅ Model file exists!")
        file_size = os.path.getsize(MODEL_PATH) / (1024 * 1024)  # Convert to MB
        print(f"   📦 Size: {file_size:.2f} MB")
    else:
        print(f"   ❌ Model file NOT found!")
        return False
    
    # Try to load model
    print(f"\n2. Loading model...")
    try:
        model = get_model()
        print(f"   ✅ Model loaded successfully!")
        
        # Display model info
        print(f"\n3. Model Information:")
        print(f"   🏷️  Number of classes: {len(model.names)}")
        print(f"   📋 Classes:")
        
        # Display classes in grid format
        classes = list(model.names.values())
        for i in range(0, len(classes), 4):
            row = classes[i:i+4]
            print("      " + " | ".join(f"{c:15}" for c in row))
        
        print("\n" + "="*60)
        print("✅ Model loading test PASSED!")
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print(f"   ❌ Error loading model: {e}")
        print("\n" + "="*60)
        print("❌ Model loading test FAILED!")
        print("="*60 + "\n")
        return False

if __name__ == "__main__":
    success = test_model_loading()
    sys.exit(0 if success else 1)
