"""
Recipe Service - Sistem rekomendasi resep berdasarkan bahan makanan
Terintegrasi dengan hasil deteksi YOLOv8 model best (3).pt
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import re

class RecipeService:
    def __init__(self):
        """Initialize recipe service dengan dataset CSV"""
        self.dataset_path = Path(__file__).parent.parent / "data" / "resep_dataset.csv"
        self.recipes_df = None
        self.load_dataset()
    
    def load_dataset(self):
        """Load dataset resep dari CSV"""
        try:
            self.recipes_df = pd.read_csv(self.dataset_path)
            print(f"✅ Loaded {len(self.recipes_df)} recipes from dataset")
        except Exception as e:
            print(f"❌ Error loading recipe dataset: {e}")
            self.recipes_df = pd.DataFrame()
    
    def normalize_ingredient(self, ingredient: str) -> List[str]:
        """Normalize nama bahan makanan untuk matching - FIXED EGGPLANT BUG"""
        
        ingredient_mapping = {
            'beef': ['daging sapi', 'sapi', 'beef', 'daging', 'has dalam', 'iga sapi'],
            'chicken': ['ayam', 'chicken', 'daging ayam', 'ayam kampung', 'ayam broiler', 
                       'fillet ayam', 'dada ayam', 'paha ayam'],
            'pork': ['daging babi', 'babi', 'pork'],
            
            # FIX: Pisahkan EGG dan EGGPLANT dengan jelas!
            'egg': ['telur', 'telor', 'telur ayam', 'telur bebek', 'telur rebus', 
                    'hintalu', 'telur dadar', 'telur ceplok'],  # TIDAK termasuk "egg" untuk avoid confusion
            'eggplant': ['terong', 'terung', 'terong ungu', 'terong hijau', 
                         'terong lalap', 'terong balado'],  # Terong ONLY
            
            'galunggong': ['ikan', 'galunggong', 'ikan galunggong'],
            'milkfish': ['ikan', 'bandeng', 'ikan bandeng'],
            'tilapia': ['ikan', 'nila', 'tilapia', 'ikan nila'],
            'tomato': ['tomat', 'tomat merah', 'tomat hijau'],
            'onion': ['bawang merah', 'bawang bombai', 'brambang', 'bamer'],
            'garlic': ['bawang putih', 'baputi', 'baput'],
            'ginger': ['jahe', 'halia', 'jahé'],
            'potato': ['kentang', 'ubi kentang'],
            'carrots': ['wortel', 'lobak merah'],
            'cabbage': ['kol', 'kubis', 'kobis'],
            'broccoli': ['brokoli'],
            'cauliflower': ['kembang kol', 'bunga kol'],
            'pumpkin': ['labu', 'labu kuning', 'waluh'],
            'bittergourd': ['pare', 'paria', 'peria'],
            'bottlegourd': ['labu air', 'gambas'],
            'sayote': ['labu siam', 'sayote', 'jipang', 'manisa'],
            'pechay': ['sawi', 'sawi putih', 'sawi hijau', 'caisim'],
            'waterspinach': ['kangkung', 'kangkong'],
            'stringbeans': ['buncis', 'kacang panjang', 'buncis hijau'],
            'papaya': ['pepaya', 'betik', 'kates'],
        }
        
        ingredient_lower = ingredient.lower().strip()
        
        # PRIORITY MATCHING: Cek exact match dulu
        if ingredient_lower == 'eggplant':
            return ingredient_mapping['eggplant']
        elif ingredient_lower == 'egg':
            return ingredient_mapping['egg']
        
        # Then check other mappings
        for key, values in ingredient_mapping.items():
            # Skip egg/eggplant untuk avoid confusion
            if key in ['egg', 'eggplant']:
                continue
                
            if ingredient_lower == key or key == ingredient_lower:
                return values
        
        # Fallback
        return [ingredient_lower]
    
    def search_recipes(self, ingredients: List[str], min_match: int = 1, max_results: int = 10) -> List[Dict]:
        """
        Cari resep berdasarkan bahan yang terdeteksi dari YOLO
        
        Args:
            ingredients: List bahan makanan dari deteksi YOLO (contoh: ["Chicken", "Garlic", "Tomato"])
            min_match: Minimal jumlah bahan yang harus match
            max_results: Max jumlah resep yang dikembalikan
        
        Returns:
            List of recipes dengan detail matching
        """
        if self.recipes_df is None or len(self.recipes_df) == 0:
            return []
        
        # Normalize ingredients dari YOLO
        normalized_ingredients = []
        for ing in ingredients:
            normalized_ingredients.extend(self.normalize_ingredient(ing))
        
        normalized_ingredients = list(set(normalized_ingredients))
        
        results = []
        
        for idx, row in self.recipes_df.iterrows():
            # Parse ingredients dari CSV (format: item1--item2--item3)
            ingredients_raw = str(row.get('Ingredients', ''))
            recipe_ingredients = self.parse_ingredients_detailed(ingredients_raw)
            
            if not recipe_ingredients:
                continue
            
            # Check matching
            matched = []
            missing = []
            
            for rec_ing in recipe_ingredients:
                rec_ing_lower = rec_ing.lower()
                is_matched = False
                
                for norm_ing in normalized_ingredients:
                    if norm_ing in rec_ing_lower or rec_ing_lower in norm_ing:
                        matched.append(rec_ing)  # Use original format dari CSV
                        is_matched = True
                        break
                
                if not is_matched:
                    missing.append(rec_ing)  # Use original format dari CSV
            
            match_count = len(matched)
            
            if match_count >= min_match:
                # Parse steps
                steps_raw = str(row.get('Steps', ''))
                instructions = self.parse_steps_detailed(steps_raw)
                
                match_percentage = (match_count / len(recipe_ingredients)) * 100 if recipe_ingredients else 0
                
                results.append({
                    'id': int(idx),
                    'name': str(row.get('Title', 'Unknown')),
                    'category': str(row.get('Category', 'unknown')),
                    'loves': int(row.get('Loves', 0)),
                    'url': str(row.get('URL', '')),
                    'total_ingredients': len(recipe_ingredients),
                    'total_steps': len(instructions),
                    'matched_count': match_count,
                    'match_percentage': round(match_percentage, 2),
                    'matched_ingredients': matched,
                    'missing_ingredients': missing,
                    'all_ingredients': recipe_ingredients,  # Format asli dari CSV
                    'instructions': instructions
                })
        
        # Sort by match percentage
        results.sort(key=lambda x: (x['match_percentage'], x['loves']), reverse=True)
        
        return results[:max_results]
    
    def parse_ingredients_detailed(self, ingredients_str: str) -> List[str]:
        """Parse ingredients dari format CSV (dipisah dengan --)"""
        if not ingredients_str or ingredients_str == 'nan':
            return []
        
        # Split by -- separator
        ingredients = []
        raw_items = str(ingredients_str).split('--')
        
        for item in raw_items:
            item = item.strip()
            if item:
                ingredients.append(item)
        
        return ingredients

    def parse_steps_detailed(self, steps_str: str) -> List[str]:
        """Parse steps dari format CSV"""
        if not steps_str or steps_str == 'nan':
            return []
        
        steps = []
        import re
        # Match pattern like "1) text", "2) text"
        step_pattern = r'(\d+)\)\s*(.+?)(?=\d+\)|$)'
        matches = re.findall(step_pattern, str(steps_str), re.DOTALL)
        
        for num, text in matches:
            steps.append(text.strip())
        
        return steps

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Dict]:
        """Get detail resep by ID dengan format asli dari CSV"""
        try:
            if recipe_id >= len(self.recipes_df):
                return None
            
            row = self.recipes_df.iloc[recipe_id]
            
            # Parse ingredients - format asli dari CSV
            raw_ingredients = str(row.get('Ingredients', ''))
            ingredients_list = self.parse_ingredients_detailed(raw_ingredients)
            
            # Parse steps
            raw_steps = str(row.get('Steps', ''))
            steps_list = self.parse_steps_detailed(raw_steps)
            
            return {
                'id': int(recipe_id),
                'name': str(row.get('Title', 'Unknown')),
                'ingredients': ingredients_list,  # Format: ["1 buah Pare", "2 bawang merah", ...]
                'total_ingredients': len(ingredients_list),
                'instructions': steps_list,
                'total_steps': len(steps_list),
                'category': str(row.get('Category', 'unknown')),
                'url': str(row.get('URL', '')),
                'loves': int(row.get('Loves', 0))
            }
        except Exception as e:
            print(f"Error getting recipe detail: {e}")
            return None
    
    def search_by_name(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search resep by nama"""
        if self.recipes_df is None or len(self.recipes_df) == 0:
            return []
        
        query = query.lower()
        results = []
        
        for idx, row in self.recipes_df.iterrows():
            title = str(row.get('Title', '')).lower()
            if query in title:
                results.append({
                    'id': int(idx),
                    'name': str(row.get('Title', 'Unknown')),
                    'category': str(row.get('Category', 'unknown')),
                    'loves': int(row.get('Loves', 0))
                })
        
        # Sort by loves
        results.sort(key=lambda x: x['loves'], reverse=True)
        
        return results[:max_results]

# Global instance
_recipe_service = None

def get_recipe_service() -> RecipeService:
    """Get singleton instance of recipe service"""
    global _recipe_service
    if _recipe_service is None:
        _recipe_service = RecipeService()
    return _recipe_service

# Export singleton instance for direct import
recipe_service = get_recipe_service()
