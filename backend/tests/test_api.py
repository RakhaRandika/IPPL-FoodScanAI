# Test script untuk FoodScanAI Backend API
# Pastikan server sudah running: uvicorn app.main:app --reload

import requests
import sys
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/api/scan/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_scan(image_path: str, confidence: float = 0.5):
    """Test scan endpoint dengan gambar"""
    print(f"\n=== Testing Scan Endpoint ===")
    print(f"Image: {image_path}")
    print(f"Confidence: {confidence}")
    
    if not os.path.exists(image_path):
        print(f"Error: File tidak ditemukan: {image_path}")
        return False
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            data = {"confidence": confidence}
            response = requests.post(f"{BASE_URL}/api/scan", files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            print(f"Count: {result.get('count')}")
            print("\nPredictions:")
            for i, pred in enumerate(result.get('predictions', []), 1):
                print(f"  {i}. {pred['label']} - {pred['confidence']}%")
                bbox = pred['bounding_box']
                print(f"     Box: ({bbox['x1']}, {bbox['y1']}) -> ({bbox['x2']}, {bbox['y2']})")
            return True
        else:
            print(f"Error: {result}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("=" * 60)
    print("FoodScanAI Backend API Test")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print("Pastikan server sudah running!")
    print("=" * 60)
    
    # Test root endpoint
    if not test_root():
        print("\n⚠️ Root endpoint tidak bisa diakses. Pastikan server running!")
        return
    
    # Test health check
    if not test_health_check():
        print("\n⚠️ Health check gagal. Cek model path!")
        return
    
    # Test scan dengan gambar
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        confidence = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
        test_scan(image_path, confidence)
    else:
        print("\n💡 Tip: Jalankan dengan gambar untuk test scan:")
        print("   python test_api.py path/to/image.jpg 0.5")
    
    print("\n" + "=" * 60)
    print("✅ Test selesai!")
    print("=" * 60)

if __name__ == "__main__":
    main()
