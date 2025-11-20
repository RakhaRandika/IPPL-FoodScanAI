"""
Recipe Routes - API endpoints untuk rekomendasi resep
Terintegrasi dengan hasil deteksi YOLOv8
"""
from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from pydantic import BaseModel
from app.services.recipe_service import get_recipe_service

router = APIRouter(prefix="/api/recipes", tags=["Recipe Recommendations"])

# Request models
class RecipeRecommendRequest(BaseModel):
    ingredients: List[str]
    min_match: Optional[int] = 1
    max_results: Optional[int] = 10

# Initialize service
recipe_service = get_recipe_service()

@router.post("/recommend")
async def recommend_recipes(request: RecipeRecommendRequest):
    """
    Rekomendasi resep berdasarkan bahan makanan yang terdeteksi
    
    Input:
    - ingredients: List nama bahan dari deteksi YOLO (contoh: ["Chicken", "Garlic", "Tomato"])
    - min_match: Minimal bahan yang harus match (default: 1)
    - max_results: Max jumlah resep dikembalikan (default: 10)
    
    Output:
    - List resep dengan informasi match percentage, bahan yang cocok, bahan yang kurang
    """
    try:
        if not request.ingredients:
            raise HTTPException(status_code=400, detail="Ingredients list cannot be empty")
        
        recipes = recipe_service.search_recipes(
            ingredients=request.ingredients,
            min_match=request.min_match,
            max_results=request.max_results
        )
        
        if not recipes:
            return {
                "success": True,
                "message": "Tidak ada resep yang cocok dengan bahan yang terdeteksi",
                "detected_ingredients": request.ingredients,
                "recipes": [],
                "total_found": 0
            }
        
        return {
            "success": True,
            "message": f"Ditemukan {len(recipes)} resep yang cocok",
            "detected_ingredients": request.ingredients,
            "recipes": recipes,
            "total_found": len(recipes)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/search")
async def search_recipes(query: str, max_results: int = 10):
    """
    Cari resep berdasarkan nama
    
    Query params:
    - query: Nama resep yang dicari
    - max_results: Max jumlah hasil (default: 10)
    """
    try:
        results = recipe_service.search_by_name(query, max_results)
        
        return {
            "success": True,
            "query": query,
            "recipes": results,
            "total_found": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/{recipe_id}")
async def get_recipe_detail(recipe_id: int):
    """
    Get detail resep by ID dengan bahan & langkah lengkap
    
    Path params:
    - recipe_id: ID resep
    """
    try:
        recipe = recipe_service.get_recipe_by_id(recipe_id)
        
        if not recipe:
            raise HTTPException(status_code=404, detail=f"Recipe with ID {recipe_id} not found")
        
        return {
            "success": True,
            "recipe": recipe
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/")
async def get_all_recipes(limit: int = 20, offset: int = 0):
    """
    Get list semua resep dengan pagination
    
    Query params:
    - limit: Jumlah resep per page (default: 20)
    - offset: Skip berapa resep (default: 0)
    """
    try:
        # Simplified - return empty untuk sekarang karena dataset besar
        return {
            "success": True,
            "message": "Use /api/recipes/search or /api/recipes/recommend endpoints",
            "total_recipes": len(recipe_service.recipes_df) if recipe_service.recipes_df is not None else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
