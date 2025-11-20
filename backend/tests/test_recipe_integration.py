"""
Test script untuk recipe recommendation integration
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_recipe_recommend():
    """Test direct recipe recommendation endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Direct Recipe Recommendation")
    print("="*60)
    
    url = f"{BASE_URL}/api/recipes/recommend"
    data = {
        "ingredients": ["Chicken", "Garlic", "Tomato", "Onion"]
    }
    
    print(f"📤 Request: POST {url}")
    print(f"📦 Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, json=data)
    
    print(f"\n✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"📊 Found {len(result['recipes'])} recipes")
        
        if result['recipes']:
            print(f"\n🏆 Top 3 Recipes:")
            for i, recipe in enumerate(result['recipes'][:3], 1):
                print(f"   {i}. {recipe['name']}")
                print(f"      - Category: {recipe['category']}")
                print(f"      - Match: {recipe['match_percentage']:.1f}%")
                print(f"      - Matched Ingredients: {', '.join(recipe['matched_ingredients'])}")
                print(f"      - Loves: {recipe['loves']:,}")
                print()
    else:
        print(f"❌ Error: {response.text}")


def test_recipe_search():
    """Test recipe search by name"""
    print("\n" + "="*60)
    print("TEST 2: Recipe Search by Name")
    print("="*60)
    
    url = f"{BASE_URL}/api/recipes/search"
    params = {"query": "ayam"}
    
    print(f"📤 Request: GET {url}")
    print(f"🔍 Query: {params['query']}")
    
    response = requests.get(url, params=params)
    
    print(f"\n✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"📊 Found {len(result['recipes'])} recipes")
        
        if result['recipes']:
            print(f"\n🏆 Top 5 Recipes:")
            for i, recipe in enumerate(result['recipes'][:5], 1):
                print(f"   {i}. {recipe['name']} ({recipe['category']}) - ❤️ {recipe['loves']:,}")
    else:
        print(f"❌ Error: {response.text}")


def test_scan_with_ingredients():
    """Test scan endpoint to verify recipe recommendations are included"""
    print("\n" + "="*60)
    print("TEST 3: Scan Integration Check (Mock Detection)")
    print("="*60)
    
    # Note: This would normally use an actual image file
    # For now, we're just checking if the endpoint structure is correct
    print("⚠️  This test requires an actual image file to scan")
    print("   The scan endpoint will detect ingredients and automatically")
    print("   recommend recipes based on detected items.")
    print("\n📝 Example flow:")
    print("   1. Upload image → POST /api/scan")
    print("   2. YOLO detects: ['Chicken', 'Garlic', 'Tomato']")
    print("   3. Response includes:")
    print("      - predictions: [...detected objects...]")
    print("      - detected_ingredients: ['Chicken', 'Garlic', 'Tomato']")
    print("      - recommended_recipes: [...matching recipes...]")


if __name__ == "__main__":
    print("\n🧪 Testing Recipe Recommendation Integration")
    print("=" * 60)
    
    try:
        # Test 1: Direct recipe recommendation
        test_recipe_recommend()
        
        # Test 2: Recipe search
        test_recipe_search()
        
        # Test 3: Scan integration info
        test_scan_with_ingredients()
        
        print("\n" + "="*60)
        print("✅ All Tests Completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print("   Make sure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
