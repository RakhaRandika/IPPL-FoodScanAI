"""Simple local nutrition service.

This provides a small mapping of ingredient -> basic nutrition per 100g.
Used as a fast offline fallback. For production, replace or augment with
calls to Nutritionix/Spoonacular APIs.
"""
from typing import Optional, Dict

# Basic nutrition values per 100g (approximate)
_NUTRITION_DB = {
    # Protein sources
    "ayam": {"calories_kcal": 165, "protein_g": 31.0, "fat_g": 3.6, "carbs_g": 0.0},
    "daging_sapi": {"calories_kcal": 250, "protein_g": 26.0, "fat_g": 15.0, "carbs_g": 0.0},
    "daging_babi": {"calories_kcal": 242, "protein_g": 27.0, "fat_g": 14.0, "carbs_g": 0.0},
    "telur": {"calories_kcal": 155, "protein_g": 13.0, "fat_g": 11.0, "carbs_g": 1.1},
    "ikan": {"calories_kcal": 206, "protein_g": 22.0, "fat_g": 12.0, "carbs_g": 0.0},
    "ikan_galunggong": {"calories_kcal": 88, "protein_g": 18.0, "fat_g": 1.4, "carbs_g": 0.0},
    "ikan_bandeng": {"calories_kcal": 129, "protein_g": 20.0, "fat_g": 4.8, "carbs_g": 0.0},
    "ikan_nila": {"calories_kcal": 96, "protein_g": 20.1, "fat_g": 1.7, "carbs_g": 0.0},
    
    # Vegetables
    "tomat": {"calories_kcal": 18, "protein_g": 0.9, "fat_g": 0.2, "carbs_g": 3.9},
    "bawang": {"calories_kcal": 40, "protein_g": 1.1, "fat_g": 0.1, "carbs_g": 9.3},
    "bawang_bombai": {"calories_kcal": 40, "protein_g": 1.1, "fat_g": 0.1, "carbs_g": 9.3},
    "bawang_putih": {"calories_kcal": 149, "protein_g": 6.4, "fat_g": 0.5, "carbs_g": 33.0},
    "jahe": {"calories_kcal": 80, "protein_g": 1.8, "fat_g": 0.8, "carbs_g": 18.0},
    "kentang": {"calories_kcal": 77, "protein_g": 2.0, "fat_g": 0.1, "carbs_g": 17.0},
    "wortel": {"calories_kcal": 41, "protein_g": 0.9, "fat_g": 0.2, "carbs_g": 10.0},
    "kubis": {"calories_kcal": 25, "protein_g": 1.3, "fat_g": 0.1, "carbs_g": 5.8},
    "kol": {"calories_kcal": 25, "protein_g": 1.3, "fat_g": 0.1, "carbs_g": 5.8},
    "terong": {"calories_kcal": 25, "protein_g": 1.0, "fat_g": 0.2, "carbs_g": 5.9},
    "labu": {"calories_kcal": 26, "protein_g": 1.0, "fat_g": 0.1, "carbs_g": 6.5},
    "brokoli": {"calories_kcal": 34, "protein_g": 2.8, "fat_g": 0.4, "carbs_g": 7.0},
    "kembang_kol": {"calories_kcal": 25, "protein_g": 1.9, "fat_g": 0.3, "carbs_g": 5.0},
    "pare": {"calories_kcal": 17, "protein_g": 1.0, "fat_g": 0.2, "carbs_g": 3.7},
    "labu_siam": {"calories_kcal": 24, "protein_g": 0.8, "fat_g": 0.1, "carbs_g": 6.0},
    "pechay": {"calories_kcal": 13, "protein_g": 1.5, "fat_g": 0.2, "carbs_g": 2.2},
    "kangkung": {"calories_kcal": 19, "protein_g": 2.6, "fat_g": 0.2, "carbs_g": 3.1},
    "buncis": {"calories_kcal": 31, "protein_g": 1.8, "fat_g": 0.1, "carbs_g": 7.0},
    "sayote": {"calories_kcal": 19, "protein_g": 0.8, "fat_g": 0.1, "carbs_g": 4.5},
    
    # Fruits
    "pepaya": {"calories_kcal": 43, "protein_g": 0.5, "fat_g": 0.3, "carbs_g": 11.0},
    "pisang": {"calories_kcal": 89, "protein_g": 1.1, "fat_g": 0.3, "carbs_g": 23.0},
    
    # Others
    "cabai": {"calories_kcal": 40, "protein_g": 2.0, "fat_g": 0.4, "carbs_g": 8.8},
    "bayam": {"calories_kcal": 23, "protein_g": 2.9, "fat_g": 0.4, "carbs_g": 3.6},
    "daging": {"calories_kcal": 250, "protein_g": 26.0, "fat_g": 15.0, "carbs_g": 0.0},
    "beras": {"calories_kcal": 130, "protein_g": 2.4, "fat_g": 0.2, "carbs_g": 28.0},
    "tahu": {"calories_kcal": 76, "protein_g": 8.0, "fat_g": 4.8, "carbs_g": 1.9},
    "tempe": {"calories_kcal": 193, "protein_g": 20.3, "fat_g": 10.8, "carbs_g": 7.6},
    "susu": {"calories_kcal": 42, "protein_g": 3.4, "fat_g": 1.0, "carbs_g": 5.0},
    "keju": {"calories_kcal": 402, "protein_g": 25.0, "fat_g": 33.0, "carbs_g": 1.3},
    "minyak": {"calories_kcal": 884, "protein_g": 0.0, "fat_g": 100.0, "carbs_g": 0.0},
    "gula": {"calories_kcal": 387, "protein_g": 0.0, "fat_g": 0.0, "carbs_g": 100.0},
    "paprika": {"calories_kcal": 31, "protein_g": 1.0, "fat_g": 0.3, "carbs_g": 6.0},
    "jamur": {"calories_kcal": 22, "protein_g": 3.1, "fat_g": 0.3, "carbs_g": 3.3},
    "sawi": {"calories_kcal": 13, "protein_g": 1.5, "fat_g": 0.2, "carbs_g": 2.2},
    "labu_air": {"calories_kcal": 14, "protein_g": 0.6, "fat_g": 0.1, "carbs_g": 3.4},
    "kacang_panjang": {"calories_kcal": 31, "protein_g": 1.8, "fat_g": 0.1, "carbs_g": 7.0},
}

# Mapping from YOLO detection labels (English) to nutrition DB keys (Indonesian)
# Semua 25 kelas YOLO Model harus ada mapping-nya!
_YOLO_TO_NUTRITION_MAP = {
    # Protein (8 classes)
    "Beef": "daging_sapi",
    "Chicken": "ayam",
    "Pork": "daging_babi",
    "Egg": "telur",
    "Galunggong": "ikan_galunggong",
    "Milkfish": "ikan_bandeng",
    "Tilapia": "ikan_nila",
    
    # Vegetables (14 classes)
    "Tomato": "tomat",
    "Potato": "kentang",
    "Carrots": "wortel",
    "Cabbage": "kubis",
    "Eggplant": "terong",
    "Pumpkin": "labu",
    "Broccoli": "brokoli",
    "Cauliflower": "kembang_kol",
    "BitterGourd": "pare",
    "BottleGourd": "labu_siam",
    "Sayote": "labu_siam",
    "Pechay": "pechay",
    "WaterSpinach": "kangkung",
    "StringBeans": "buncis",
    
    # Spices (3 classes)
    "Onion": "bawang_bombai",
    "Garlic": "bawang_putih",
    "Ginger": "jahe",
    
    # Fruits (1 class)
    "Papaya": "pepaya",
    
    # Case-insensitive aliases (Indonesian labels)
    "ayam": "ayam",
    "daging sapi": "daging_sapi",
    "daging babi": "daging_babi",
    "telur": "telur",
    "ikan galunggong": "ikan_galunggong",
    "ikan bandeng": "ikan_bandeng",
    "ikan nila": "ikan_nila",
    "tomat": "tomat",
    "kentang": "kentang",
    "wortel": "wortel",
    "kubis": "kubis",
    "terong": "terong",
    "labu": "labu",
    "brokoli": "brokoli",
    "kembang kol": "kembang_kol",
    "pare": "pare",
    "labu siam": "labu_siam",
    "labu air": "labu_siam",
    "sawi": "pechay",
    "kangkung": "kangkung",
    "buncis": "buncis",
    "bawang merah": "bawang_bombai",
    "bawang bombai": "bawang_bombai",
    "bawang putih": "bawang_putih",
    "jahe": "jahe",
    "pepaya": "pepaya"
}


def get_nutrition(ingredient_name: str) -> Optional[Dict]:
    """Return nutrition info for an ingredient (per 100g) or None if unknown.

    Ingredient name is normalized to lowercase and stripped.
    """
    if not ingredient_name:
        return None
    key = ingredient_name.strip().lower()
    return _NUTRITION_DB.get(key)


def get_nutrition_from_yolo_label(yolo_label: str) -> Optional[Dict]:
    """Get nutrition info from YOLO detection label (English).
    
    Maps YOLO label (e.g., 'Chicken') to Indonesian nutrition DB key (e.g., 'ayam').
    Returns nutrition info per 100g or None if not found.
    """
    if not yolo_label:
        return None
    
    # Try exact match first (case-sensitive for English labels)
    nutrition_key = _YOLO_TO_NUTRITION_MAP.get(yolo_label)
    if nutrition_key:
        result = _NUTRITION_DB.get(nutrition_key)
        if result:
            return result
    
    # Try case-insensitive match (for Indonesian labels)
    label_lower = yolo_label.lower().strip()
    nutrition_key = _YOLO_TO_NUTRITION_MAP.get(label_lower)
    if nutrition_key:
        result = _NUTRITION_DB.get(nutrition_key)
        if result:
            return result
    
    # Fallback: direct lookup in nutrition DB
    return _NUTRITION_DB.get(label_lower)


def get_nutrition_for_ingredients(ingredients: list) -> Dict:
    """Get nutrition info for multiple ingredients (YOLO labels).
    
    Args:
        ingredients: List of YOLO detection labels (e.g., ['Chicken', 'Garlic', 'Tomato'])
    
    Returns:
        Dictionary with individual nutrition info and total summary
    """
    results = {
        "ingredients": [],
        "total": {
            "calories_kcal": 0.0,
            "protein_g": 0.0,
            "fat_g": 0.0,
            "carbs_g": 0.0
        },
        "found_count": 0,
        "not_found": []
    }
    
    for ingredient in ingredients:
        nutrition = get_nutrition_from_yolo_label(ingredient)
        
        if nutrition:
            results["ingredients"].append({
                "name": ingredient,
                "nutrition_per_100g": nutrition
            })
            results["found_count"] += 1
            
            # Add to totals (assuming 100g of each ingredient)
            results["total"]["calories_kcal"] += nutrition.get("calories_kcal", 0)
            results["total"]["protein_g"] += nutrition.get("protein_g", 0)
            results["total"]["fat_g"] += nutrition.get("fat_g", 0)
            results["total"]["carbs_g"] += nutrition.get("carbs_g", 0)
        else:
            results["not_found"].append(ingredient)
    
    return results


def list_known_ingredients():
    return list(_NUTRITION_DB.keys())
