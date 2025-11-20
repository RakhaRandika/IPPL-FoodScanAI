from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.nutrition_service import (
    list_known_ingredients, 
    get_nutrition,
    get_nutrition_from_yolo_label,
    get_nutrition_for_ingredients
)

router = APIRouter(prefix="/api/nutrition", tags=["Nutrition"])


class IngredientsRequest(BaseModel):
    """Request model for getting nutrition of multiple ingredients"""
    ingredients: List[str]


@router.get("/known")
def known_ingredients():
    """Return list of ingredient keys known by the local nutrition DB."""
    return {"known": list_known_ingredients()}


@router.get("/{ingredient}")
def nutrition_for(ingredient: str):
    """Get nutrition info for a single ingredient (Indonesian name)."""
    info = get_nutrition(ingredient)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Nutrition info not found for '{ingredient}'")
    return {"ingredient": ingredient, "nutrition_per_100g": info}


@router.post("/batch")
def nutrition_for_batch(request: IngredientsRequest):
    """Get nutrition info for multiple ingredients (YOLO labels).
    
    This endpoint accepts YOLO detection labels (English) and returns
    nutrition information for each ingredient plus a total summary.
    
    Example request:
    {
        "ingredients": ["Chicken", "Garlic", "Tomato", "Onion"]
    }
    
    Example response:
    {
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
            "calories_kcal": 372,
            "protein_g": 39.4,
            "fat_g": 4.4,
            "carbs_g": 46.2
        },
        "found_count": 4,
        "not_found": []
    }
    """
    if not request.ingredients:
        raise HTTPException(status_code=400, detail="No ingredients provided")
    
    results = get_nutrition_for_ingredients(request.ingredients)
    
    return {
        "success": True,
        "data": results
    }
