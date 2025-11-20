"""
Test script untuk nutrition integration dengan YOLO detection
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_nutrition_batch():
    """Test batch nutrition endpoint dengan YOLO labels"""
    print("\n" + "="*60)
    print("TEST 1: Batch Nutrition dari YOLO Labels")
    print("="*60)
    
    url = f"{BASE_URL}/api/nutrition/batch"
    data = {
        "ingredients": ["Chicken", "Garlic", "Tomato", "Onion", "Carrots"]
    }
    
    print(f"📤 Request: POST {url}")
    print(f"📦 Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, json=data)
    
    print(f"\n✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        if result["success"]:
            data = result["data"]
            print(f"\n📊 Found nutrition for {data['found_count']} ingredients")
            
            print(f"\n🥗 Individual Nutrition (per 100g):")
            for item in data["ingredients"]:
                nutrition = item["nutrition_per_100g"]
                print(f"\n   {item['name']}:")
                print(f"      Calories: {nutrition['calories_kcal']} kcal")
                print(f"      Protein:  {nutrition['protein_g']} g")
                print(f"      Fat:      {nutrition['fat_g']} g")
                print(f"      Carbs:    {nutrition['carbs_g']} g")
            
            print(f"\n📈 TOTAL (100g each ingredient):")
            total = data["total"]
            print(f"   Calories: {total['calories_kcal']:.1f} kcal")
            print(f"   Protein:  {total['protein_g']:.1f} g")
            print(f"   Fat:      {total['fat_g']:.1f} g")
            print(f"   Carbs:    {total['carbs_g']:.1f} g")
            
            if data["not_found"]:
                print(f"\n⚠️  Not found: {', '.join(data['not_found'])}")
    else:
        print(f"❌ Error: {response.text}")


def test_nutrition_single():
    """Test single ingredient nutrition"""
    print("\n" + "="*60)
    print("TEST 2: Single Ingredient Nutrition (Indonesian)")
    print("="*60)
    
    ingredient = "ayam"
    url = f"{BASE_URL}/api/nutrition/{ingredient}"
    
    print(f"📤 Request: GET {url}")
    
    response = requests.get(url)
    
    print(f"\n✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        nutrition = result["nutrition_per_100g"]
        
        print(f"\n🍗 {result['ingredient'].upper()} (per 100g):")
        print(f"   Calories: {nutrition['calories_kcal']} kcal")
        print(f"   Protein:  {nutrition['protein_g']} g")
        print(f"   Fat:      {nutrition['fat_g']} g")
        print(f"   Carbs:    {nutrition['carbs_g']} g")
    else:
        print(f"❌ Error: {response.text}")


def test_known_ingredients():
    """Test list of known ingredients"""
    print("\n" + "="*60)
    print("TEST 3: List of Known Ingredients")
    print("="*60)
    
    url = f"{BASE_URL}/api/nutrition/known"
    
    print(f"📤 Request: GET {url}")
    
    response = requests.get(url)
    
    print(f"\n✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        ingredients = result["known"]
        
        print(f"\n📋 Total: {len(ingredients)} ingredients in database")
        print(f"\n🥦 Sample ingredients:")
        for i, ing in enumerate(ingredients[:15], 1):
            print(f"   {i:2d}. {ing}")
        
        if len(ingredients) > 15:
            print(f"   ... and {len(ingredients) - 15} more")
    else:
        print(f"❌ Error: {response.text}")


def test_scan_integration_info():
    """Info about scan endpoint with nutrition"""
    print("\n" + "="*60)
    print("TEST 4: Scan Integration (Info)")
    print("="*60)
    
    print("⚠️  Scan endpoint sekarang otomatis mengembalikan:")
    print("\n📝 Response structure:")
    print("""
    {
        "success": true,
        "predictions": [...detected objects...],
        "detected_ingredients": ["Chicken", "Garlic"],
        "recommended_recipes": [...recipes...],
        "nutrition_info": {
            "ingredients": [
                {
                    "name": "Chicken",
                    "nutrition_per_100g": {
                        "calories_kcal": 165,
                        "protein_g": 31.0,
                        "fat_g": 3.6,
                        "carbs_g": 0.0
                    }
                },
                ...
            ],
            "total": {
                "calories_kcal": 314,
                "protein_g": 38.4,
                "fat_g": 4.1,
                "carbs_g": 42.2
            },
            "found_count": 2,
            "not_found": []
        }
    }
    """)
    
    print("\n✨ Features:")
    print("   1. ✅ Deteksi makanan dengan YOLO")
    print("   2. ✅ Rekomendasi resep otomatis")
    print("   3. ✅ Informasi nutrisi otomatis")
    print("   4. ✅ Total nutrisi dari semua bahan")


if __name__ == "__main__":
    print("\n🧪 Testing Nutrition Integration")
    print("=" * 60)
    
    try:
        # Test 1: Batch nutrition
        test_nutrition_batch()
        
        # Test 2: Single ingredient
        test_nutrition_single()
        
        # Test 3: Known ingredients
        test_known_ingredients()
        
        # Test 4: Integration info
        test_scan_integration_info()
        
        print("\n" + "="*60)
        print("✅ All Tests Completed!")
        print("="*60)
        print("\n💡 Tip: Upload gambar ke /api/scan untuk mendapatkan:")
        print("   - Deteksi bahan makanan")
        print("   - Rekomendasi resep")
        print("   - Informasi nutrisi lengkap")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print("   Make sure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
