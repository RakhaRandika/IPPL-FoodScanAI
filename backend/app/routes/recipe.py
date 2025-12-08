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
    max_results: Optional[int] = 200  # Default 200 = fokus kualitas

# Initialize service
recipe_service = get_recipe_service()

@router.post("/recommend")
async def recommend_recipes(request: RecipeRecommendRequest):
    """
    Rekomendasi resep berdasarkan bahan makanan yang terdeteksi
    
    Input:
    - ingredients: List nama bahan dari deteksi YOLO (contoh: ["Chicken", "Garlic", "Tomato"])
    - min_match: Minimal bahan yang harus match (default: 1)
    - max_results: Max jumlah resep dikembalikan (default: 200, max: 500)
    
    Output:
    - List resep dengan informasi match percentage, bahan yang cocok, bahan yang kurang
    """
    try:
        if not request.ingredients:
            raise HTTPException(status_code=400, detail="Ingredients list cannot be empty")
        
        print(f"🔍 Recipe API - Ingredients: {request.ingredients}")
        print(f"🔍 Recipe API - max_results: {request.max_results}")
        
        recipes = recipe_service.search_recipes(
            ingredients=request.ingredients,
            min_match=request.min_match,
            max_results=request.max_results
        )
        
        print(f"✅ Recipe API - Found {len(recipes)} recipes")
        
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
        print(f"❌ Recipe API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/search")
async def search_recipes_by_ingredients(request: RecipeRecommendRequest):
    """
    Search resep berdasarkan ingredients (alias untuk /recommend)
    Endpoint ini lebih intuitif untuk frontend
    """
    try:
        if not request.ingredients:
            raise HTTPException(status_code=400, detail="Ingredients list cannot be empty")
        
        print(f"🔍 Search API - Ingredients: {request.ingredients}")
        print(f"🔍 Search API - max_results: {request.max_results}")
        
        recipes = recipe_service.search_recipes(
            ingredients=request.ingredients,
            min_match=request.min_match,
            max_results=request.max_results
        )
        
        print(f"✅ Search API - Returning {len(recipes)} recipes")
        
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
        print(f"❌ Search API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/search")
async def search_recipes_by_name(query: str, max_results: int = 20):
    """
    Cari resep berdasarkan nama
    
    Query params:
    - query: Nama resep yang dicari
    - max_results: Max jumlah hasil (default: 20)
    """
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        recipes = recipe_service.search_by_name(query, max_results=max_results)
        
        return {
            "success": True,
            "query": query,
            "recipes": recipes,
            "total_found": len(recipes)
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
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        return {
            "success": True,
            "recipe": recipe
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/")
async def get_all_recipes(limit: int = 50, offset: int = 0):
    """
    Get list semua resep dengan pagination
    
    Query params:
    - limit: Jumlah resep per page (default: 50)
    - offset: Skip berapa resep (default: 0)
    """
    try:
        if recipe_service.recipes_df is None or len(recipe_service.recipes_df) == 0:
            return {
                "success": True,
                "recipes": [],
                "total": 0,
                "limit": limit,
                "offset": offset
            }
        
        # Get slice of recipes
        total = len(recipe_service.recipes_df)
        recipes_slice = recipe_service.recipes_df.iloc[offset:offset+limit]
        
        recipes = []
        for idx, row in recipes_slice.iterrows():
            recipes.append({
                "id": int(idx),
                "name": str(row.get('Title', 'Unknown')),
                "category": str(row.get('Category', 'unknown')),
                "loves": int(row.get('Loves', 0)),
                "total_ingredients": len(str(row.get('Ingredients', '')).split('--')),
            })
        
        return {
            "success": True,
            "recipes": recipes,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
