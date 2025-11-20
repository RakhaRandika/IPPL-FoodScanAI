"""
Test API endpoints dengan requests
"""
import requests
import json

API_BASE = "http://127.0.0.1:8000"

def test_health():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("TEST: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE}/api/scan/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_camera_status():
    """Test camera status endpoint"""
    print("\n" + "="*60)
    print("TEST: Camera Status")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE}/camera/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_camera_capture_scan():
    """Test camera capture and scan"""
    print("\n" + "="*60)
    print("TEST: Camera Capture & Scan")
    print("="*60)
    print("📷 Capturing frame from camera and running detection...")
    
    try:
        response = requests.post(f"{API_BASE}/camera/capture/scan")
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print(f"\n📊 Results:")
        print(f"   Success: {data.get('success')}")
        print(f"   Message: {data.get('message')}")
        print(f"   Detections: {data.get('count')}")
        
        if data.get('predictions'):
            print(f"\n🎯 Detected Objects:")
            for i, pred in enumerate(data['predictions'], 1):
                print(f"   {i}. {pred['label']} ({pred['confidence']}%)")
                print(f"      Box: ({pred['bounding_box']['x1']:.1f}, {pred['bounding_box']['y1']:.1f}) "
                      f"-> ({pred['bounding_box']['x2']:.1f}, {pred['bounding_box']['y2']:.1f})")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print("\n" + "="*60)
    print("TEST: Root Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"\n📋 API Info:")
        print(f"   Message: {data.get('message')}")
        print(f"   Version: {data.get('version')}")
        print(f"\n📍 Available Endpoints:")
        for key, value in data.get('endpoints', {}).items():
            print(f"   - {key}: {value}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all API tests"""
    print("\n" + "="*60)
    print("🧪 API Testing Suite")
    print("="*60)
    print(f"📡 Testing API at: {API_BASE}")
    
    tests = {
        "Root Endpoint": test_root,
        "Health Check": test_health,
        "Camera Status": test_camera_status,
        "Camera Capture & Scan": test_camera_capture_scan,
    }
    
    results = {}
    for name, test_func in tests.items():
        results[name] = test_func()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    for name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {name}: {status}")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    print(f"\n🎯 Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests PASSED!")
    else:
        print("⚠️  Some tests failed")

if __name__ == "__main__":
    main()
