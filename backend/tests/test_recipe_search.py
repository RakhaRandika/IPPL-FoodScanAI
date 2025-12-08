from app.services.recipe_service import recipe_service

ingredients = ["BitterGourd", "Pork"]  # gunakan label yang muncul di UI
print("Searching for:", ingredients)
res = recipe_service.search_recipes(ingredients=ingredients, min_match=1, max_results=20)
print("Found:", len(res))
for i, r in enumerate(res[:10], 1):
    print(f"{i}. {r.get('name')} - {r.get('match_percentage')}% - matched: {r.get('matched_ingredients')}")