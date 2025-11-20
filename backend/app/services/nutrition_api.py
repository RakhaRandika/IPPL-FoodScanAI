"""Optional external nutrition API client.

This module provides a tiny example client for Spoonacular. To enable it,
set the environment variables:
  NUTRITION_PROVIDER=spoonacular
  NUTRITION_API_KEY=<your_spoonacular_api_key>

If not configured or the request fails, callers should fallback to local mapping.
"""
import os
import requests
from typing import Optional, Dict

API_PROVIDER = os.getenv("NUTRITION_PROVIDER", "").lower()
API_KEY = os.getenv("NUTRITION_API_KEY", "")


def get_spoonacular_nutrition(ingredient: str) -> Optional[Dict]:
    """Query Spoonacular to fetch nutrition for ~100g of an ingredient.

    This does a a search then information lookup for 100 grams. Requires API key.
    Returns dict similar to local nutrition mapping or None on failure.
    """
    if not API_KEY:
        return None
    try:
        search_url = "https://api.spoonacular.com/food/ingredients/search"
        params = {"query": ingredient, "apiKey": API_KEY, "number": 1}
        r = requests.get(search_url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data.get("results"):
            return None
        ing_id = data["results"][0]["id"]

        info_url = f"https://api.spoonacular.com/food/ingredients/{ing_id}/information"
        params = {"amount": 100, "unit": "g", "apiKey": API_KEY}
        r2 = requests.get(info_url, params=params, timeout=10)
        r2.raise_for_status()
        info = r2.json()

        # parse nutrients into a simple mapping (calories, protein, fat, carbs)
        nut = {"calories_kcal": None, "protein_g": None, "fat_g": None, "carbs_g": None}
        for n in info.get("nutrition", {}).get("nutrients", []):
            name = n.get("name", "").lower()
            amount = n.get("amount")
            if name == "calories":
                nut["calories_kcal"] = amount
            elif name == "protein":
                nut["protein_g"] = amount
            elif name == "fat":
                nut["fat_g"] = amount
            elif name in ("carbohydrates", "carbs"):
                nut["carbs_g"] = amount

        return nut
    except Exception:
        return None


def get_external_nutrition(ingredient: str) -> Optional[Dict]:
    if API_PROVIDER == "spoonacular":
        return get_spoonacular_nutrition(ingredient)
    return None
