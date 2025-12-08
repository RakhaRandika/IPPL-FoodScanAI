import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import re

class RecipeService:
    def __init__(self):
        """Initialize recipe service dengan DATABASE atau CSV fallback"""
        self.dataset_path = Path(__file__).parent.parent / "data" / "resep_dataset.csv"
        self.recipes_df = None
        self.load_dataset()
    
    def load_dataset(self):
        """Load dataset dari DATABASE (prioritas) atau CSV (fallback)"""
        try:
            from app.database import SessionLocal, Recipe
            session = SessionLocal()
            recipes = session.query(Recipe).all()
            
            if recipes:
                rows = []
                for r in recipes:
                    rows.append({
                        "Title": r.title,
                        "Category": r.category,
                        "Ingredients": r.ingredients,
                        "Steps": r.steps,
                        "URL": r.url,
                        "Loves": r.loves
                    })
                self.recipes_df = pd.DataFrame(rows)
                self.recipes_df['Ingredients'] = self.recipes_df['Ingredients'].astype(str)
                self.recipes_df['Title'] = self.recipes_df['Title'].astype(str)
                print(f"✅ Loaded {len(self.recipes_df)} recipes from DATABASE")
                session.close()
                return
            
            session.close()
        except Exception as e:
            print(f"⚠️ Database load failed: {e}")
        
        # Fallback CSV
        try:
            self.recipes_df = pd.read_csv(self.dataset_path)
            self.recipes_df['Ingredients'] = self.recipes_df['Ingredients'].astype(str)
            self.recipes_df['Title'] = self.recipes_df['Title'].astype(str)
            print(f"✅ Loaded {len(self.recipes_df)} recipes from CSV (fallback)")
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            self.recipes_df = pd.DataFrame()

    def normalize_ingredient(self, ingredient: str) -> tuple:
        """Normalize nama bahan makanan & mengembalikan tipe: protein/vegetable/spice"""
        ingredient_mapping = {
            # PROTEIN - SPECIFIC CHICKEN PARTS ONLY
            'beef': (['daging sapi', 'sapi'], 'protein'),
            'daging sapi': (['daging sapi', 'sapi'], 'protein'),
            'chicken': (['ayam utuh', 'daging ayam mentah', 'ayam potong', 'ayam segar', 'ayam kampung'], 'protein'),
            'pork': (['daging babi', 'babi'], 'protein'),
            'daging babi': (['daging babi', 'babi'], 'protein'),
            'egg': (['telur ayam', 'telur bebek', 'telur'], 'protein'),
            'telur': (['telur ayam', 'telur bebek', 'telur'], 'protein'),
            'galunggong': (['ikan galunggong', 'galunggong', 'ikan'], 'protein'),
            'ikan galunggong': (['ikan galunggong', 'galunggong', 'ikan'], 'protein'),
            'milkfish': (['ikan bandeng', 'bandeng', 'ikan'], 'protein'),
            'ikan bandeng': (['ikan bandeng', 'bandeng', 'ikan'], 'protein'),
            'tilapia': (['ikan nila', 'nila', 'mujair', 'ikan'], 'protein'),
            'ikan nila': (['ikan nila', 'nila', 'mujair', 'ikan'], 'protein'),

            # VEGETABLES
            'eggplant': (['terong', 'terung'], 'vegetable'),
            'terong': (['terong', 'terung'], 'vegetable'),
            'tomato': (['tomat'], 'vegetable'),
            'tomat': (['tomat'], 'vegetable'),
            'potato': (['kentang'], 'vegetable'),
            'kentang': (['kentang'], 'vegetable'),
            'carrots': (['wortel'], 'vegetable'),
            'wortel': (['wortel'], 'vegetable'),
            'cabbage': (['kol', 'kubis'], 'vegetable'),
            'kubis': (['kol', 'kubis'], 'vegetable'),
            'broccoli': (['brokoli'], 'vegetable'),
            'brokoli': (['brokoli'], 'vegetable'),
            'cauliflower': (['kembang kol'], 'vegetable'),
            'kembang kol': (['kembang kol'], 'vegetable'),
            'pumpkin': (['labu kuning', 'labu'], 'vegetable'),
            'labu': (['labu kuning', 'labu'], 'vegetable'),
            'bittergourd': (['pare'], 'vegetable'),
            'pare': (['pare'], 'vegetable'),
            'bottlegourd': (['labu air'], 'vegetable'),
            'labu air': (['labu air'], 'vegetable'),
            'sayote': (['labu siam'], 'vegetable'),
            'labu siam': (['labu siam'], 'vegetable'),
            'pechay': (['sawi', 'caisim'], 'vegetable'),
            'sawi': (['sawi', 'caisim'], 'vegetable'),
            'waterspinach': (['kangkung'], 'vegetable'),
            'kangkung': (['kangkung'], 'vegetable'),
            'stringbeans': (['buncis', 'kacang panjang'], 'vegetable'),
            'buncis': (['buncis', 'kacang panjang'], 'vegetable'),
            'papaya': (['pepaya'], 'vegetable'),
            'pepaya': (['pepaya'], 'vegetable'),

            # SPICES
            'onion': (['bawang merah', 'bawang bombai'], 'spice'),
            'bawang merah': (['bawang merah', 'bawang bombai'], 'spice'),
            'garlic': (['bawang putih'], 'spice'),
            'bawang putih': (['bawang putih'], 'spice'),
            'ginger': (['jahe'], 'spice'),
            'jahe': (['jahe'], 'spice')
        }
        
        ing = ingredient.lower().strip()
        if 'bandeng' in ing:
            return (['ikan bandeng', 'bandeng', 'ikan'], 'protein')
        if 'galunggong' in ing:
            return (['ikan galunggong', 'galunggong', 'ikan'], 'protein')
        if 'nila' in ing or 'mujair' in ing:
            return (['ikan nila', 'nila', 'mujair', 'ikan'], 'protein')
        
        # PRIORITY: Specific chicken parts
        if 'paha' in ing and 'ayam' in ing:
            return (['paha ayam', 'paha ayam potong'], 'protein')
        if 'sayap' in ing and 'ayam' in ing:
            return (['sayap ayam', 'sayap ayam potong'], 'protein')
        if ('dada' in ing or 'fillet' in ing) and 'ayam' in ing:
            return (['dada ayam', 'fillet ayam', 'daging ayam dada'], 'protein')
        if 'ceker' in ing:
            return (['ceker ayam'], 'protein')
        if 'hati' in ing and 'ayam' in ing:
            return (['hati ayam', 'ati ayam'], 'protein')
        
        if any(exclude in ing for exclude in ['mie ayam', 'ayam goreng', 'ayam geprek', 'ayam bakar', 'ayam rica', 'ayam penyet']):
            return ([], 'none') 
        
        if 'terong' in ing or 'eggplant' in ing:
            return ingredient_mapping['eggplant']

        for key, (values, ing_type) in ingredient_mapping.items():
            if ing == key or key in ing:
                return (values, ing_type)
        return ([ing], 'vegetable')
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'[0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', ' ', text)
        return text.lower().strip()

    def parse_ingredients_detailed(self, ingredients_str: str) -> List[str]:
        if not ingredients_str or ingredients_str == 'nan':
            return []
        raw_items = str(ingredients_str).split('--')
        return [item.strip() for item in raw_items if item.strip()]

    def parse_steps_detailed(self, steps_str: str) -> List[str]:
        if not steps_str or steps_str == 'nan':
            return []
        matches = re.findall(r'(\d+)\)\s*(.+?)(?=\d+\)|$)', str(steps_str), re.DOTALL)
        return [step.strip() for _, step in matches]
        
    def search_recipes(self, ingredients: List[str], min_match: int = 1, max_results: int = 200) -> List[Dict]:
        """Search resep dengan WEIGHTED SCORING (protein lebih berat)
        
        Args:
            ingredients: List bahan makanan untuk dicari
            min_match: Minimal bahan yang harus match (default 1)
            max_results: Maksimal hasil (default 200 = fokus kualitas, bukan kuantitas)
        """
        if self.recipes_df is None or len(self.recipes_df) == 0:
            return []

        search_keywords = []
        protein_keywords = []
        vegetable_keywords = []
        user_has_chicken = False
        user_has_beef = False
        user_has_fish = False
        user_has_egg = False  # NEW: Track telur separately from chicken
        
        # Normalize + classify
        for ing in ingredients:
            normalized, ing_type = self.normalize_ingredient(ing)
            search_keywords.extend(normalized)
            if ing_type == 'protein':
                protein_keywords.extend(normalized)
            elif ing_type == 'vegetable':
                vegetable_keywords.extend(normalized)
            
            # Track protein types untuk filtering
            ing_lower = ing.lower()
            
            # CRITICAL: Bedakan Chicken vs Egg detection
            if 'telur' in ing_lower or 'egg' in ing_lower:
                user_has_egg = True  # User punya TELUR
            elif 'ayam' in ing_lower or 'chicken' in ing_lower:
                user_has_chicken = True  # User punya AYAM mentah
            
            if 'sapi' in ing_lower or 'beef' in ing_lower:
                user_has_beef = True
            if 'ikan' in ing_lower or 'fish' in ing_lower or 'bandeng' in ing_lower or 'galunggong' in ing_lower or 'nila' in ing_lower:
                user_has_fish = True

        search_keywords = list(set(search_keywords))

        results = []

        for idx, row in self.recipes_df.iterrows():
            # EARLY FILTER: Skip category yang tidak relevan dengan bahan mentah
            category = str(row.get('Category', '')).lower()
            title = str(row.get('Title', '')).lower()
            
            # SKIP kategori bumbu/instant untuk SEMUA protein mentah
            skip_categories = ['bumbu', 'seasoning', 'instant', 'ready to eat', 'frozen', 'bumbu racik']
            if any(cat in category for cat in skip_categories):
                continue
            
            # Filter spesifik per protein
            if user_has_chicken:
                # SKIP produk olahan ayam
                if any(word in title for word in ['royco', 'royko', 'masako', 'bumbu racik', 'kaldu bubuk', 'kaldu ayam instant']):
                    continue
            
            if user_has_beef:
                # SKIP produk olahan sapi
                if any(word in title for word in ['kornet', 'dendeng', 'abon sapi', 'bakso sapi instant', 'kaldu sapi bubuk']):
                    continue
            
            if user_has_fish:
                # SKIP produk olahan ikan
                if any(word in title for word in ['ikan kaleng', 'sarden', 'ikan asin', 'terasi', 'petis', 'kaldu ikan bubuk']):
                    continue
            
            recipe_ingredients = self.parse_ingredients_detailed(str(row.get('Ingredients', '')))
            if not recipe_ingredients:
                continue

            matched = []
            protein_matches = 0
            vegetable_matches = 0
            missing = []
            score = 0

            for rec_ing in recipe_ingredients:
                rec_clean = self._clean_text(rec_ing)
                is_match = False

                for kw in search_keywords:
                    if f" {kw} " in f" {rec_clean} " or kw == rec_clean or kw in rec_clean:

                        # FILTER KETAT: Anti salah deteksi protein mentah vs produk olahan
                        
                        # Filter AYAM (tapi JANGAN filter telur jika user punya telur!)
                        if user_has_chicken and kw == "ayam":
                            skip_ingredients = [
                                "kaldu ayam", "kaldu", 
                                "bumbu ayam", "bumbu", "royco", "royko", "masako",
                                "penyedap rasa ayam", "penyedap", "tepung bumbu ayam",
                                "saos ayam", "kecap ayam", "abon ayam", "suwir ayam",
                                "nugget", "sosis", "bakso ayam", "tepung crispy",
                                "ayam goreng siap saji", "ayam frozen"
                            ]
                            
                            # CRITICAL: Jika ingredient ini telur, SKIP hanya jika user TIDAK punya telur
                            if "telur" in rec_clean:
                                if not user_has_egg:  # User punya ayam tapi TIDAK punya telur
                                    continue  # Skip telur ayam
                                # else: User punya telur DAN ayam, allow telur
                            elif any(skip in rec_clean for skip in skip_ingredients):
                                continue
                        
                        # Filter SAPI
                        if user_has_beef and ("sapi" in kw or "beef" in kw):
                            skip_ingredients = [
                                "kaldu sapi", "kaldu", "bumbu rendang instant",
                                "kornet", "kornet sapi", "dendeng", "abon sapi",
                                "bakso sapi", "sosis sapi", "daging kaleng"
                            ]
                            if any(skip in rec_clean for skip in skip_ingredients):
                                continue
                        
                        # Filter IKAN
                        if user_has_fish and "ikan" in kw:
                            skip_ingredients = [
                                "ikan kaleng", "sarden", "ikan asin", "ikan teri",
                                "terasi", "petis", "ebi", "kaldu ikan bubuk",
                                "nugget ikan", "bakso ikan", "otak-otak"
                            ]
                            if any(skip in rec_clean for skip in skip_ingredients):
                                continue

                        matched.append(rec_ing)
                        is_match = True

                        # Weighting
                        if kw in protein_keywords:
                            protein_matches += 1
                            score += 20
                        elif kw in vegetable_keywords:
                            vegetable_matches += 1
                            score += 10
                        else:
                            score += 5
                        break

                if not is_match:
                    missing.append(rec_ing)

            match_count = len(matched)

            if match_count >= min_match:
                title = str(row.get('Title', ''))
                title_lower = title.lower()

                # SKIP resep olahan/bumbu/makanan jadi jika user bawa bahan mentah
                if user_has_chicken:
                    # List lengkap makanan jadi ayam yang harus di-SKIP
                    processed_dishes = [
                        # Fast food & street food
                        'mie ayam', 'ayam goreng', 'ayam geprek', 'ayam bakar', 
                        'ayam rica', 'ayam penyet', 'ayam kremes', 'ayam crispy',
                        'nasi ayam', 'sop ayam', 'bubur ayam', 'rawon ayam',
                        
                        # Specific dishes
                        'ayam kecap', 'ayam teriyaki', 'ayam mentega', 'ayam suwir',
                        'ayam pop', 'ayam taliwang', 'ayam betutu', 'ayam sisit',
                        'ayam kodok', 'ayam tangkap', 'ayam rica-rica',
                        
                        # Bumbu & seasoning (CRITICAL!)
                        'bumbu ayam', 'bumbu racik ayam', 'royco ayam', 'royko ayam',
                        'kaldu ayam', 'masako ayam', 'penyedap ayam', 'tepung ayam',
                        'bumbu nasi ayam', 'bumbu geprek', 'bumbu bakar ayam',
                        
                        # Processed products
                        'nugget ayam', 'sosis ayam', 'bakso ayam', 'abon ayam',
                        'keripik ayam', 'dendeng ayam', 'serundeng ayam',
                        
                        # Mixed dishes (ayam bukan bahan utama)
                        'capcay ayam', 'kwetiau ayam', 'bihun ayam', 'nasi goreng ayam',
                        'omelet ayam', 'pizza ayam', 'sandwich ayam', 'burger ayam',
                        'pasta ayam', 'salad ayam', 'roti ayam', 'martabak ayam'
                    ]
                    if any(dish in title_lower for dish in processed_dishes):
                        continue  # SKIP resep ini!
                
                # SKIP resep olahan SAPI jika user bawa daging sapi mentah
                if user_has_beef:
                    processed_beef = [
                        # Processed products
                        'kornet sapi', 'kornet', 'dendeng sapi', 'dendeng balado',
                        'abon sapi', 'bakso sapi', 'sosis sapi', 'nugget sapi',
                        
                        # Instant/frozen
                        'daging sapi kaleng', 'rendang instant', 'semur instant',
                        'steak beku', 'burger patty'
                    ]
                    if any(dish in title_lower for dish in processed_beef):
                        continue
                
                # SKIP resep olahan IKAN jika user bawa ikan segar
                if user_has_fish:
                    processed_fish = [
                        # Processed products
                        'ikan asin', 'ikan teri', 'ikan kaleng', 'sarden',
                        'nugget ikan', 'bakso ikan', 'otak-otak', 'kerupuk ikan',
                        'terasi', 'petis ikan', 'ebi kering', 'ikan asap',
                        
                        # Instant/frozen
                        'fillet beku', 'fish stick', 'fish finger'
                    ]
                    if any(dish in title_lower for dish in processed_fish):
                        continue

                # Bonus jika keyword muncul di judul
                for kw in search_keywords:
                    if kw in title_lower:
                        score += 30

                # Parse steps
                steps_raw = str(row.get('Steps', ''))
                instructions = self.parse_steps_detailed(steps_raw)

                results.append({
                    'id': idx,
                    'name': title,
                    'category': str(row.get('Category', 'unknown')),
                    'loves': int(row.get('Loves', 0)),
                    'url': str(row.get('URL', '')),
                    'matched_count': match_count,
                    'missing_count': len(missing),  # ← FIX: Tambah ini
                    'protein_matches': protein_matches,
                    'vegetable_matches': vegetable_matches,
                    'match_percentage': round((match_count / len(recipe_ingredients)) * 100, 2),
                    'matched_ingredients': matched,
                    'missing_ingredients': missing,
                    'all_ingredients': recipe_ingredients,
                    'total_ingredients': len(recipe_ingredients),  # ← FIX: Tambah ini
                    'instructions': instructions,
                    'total_steps': len(instructions),  # ← FIX: Tambah ini
                    'score': score
                })

        results.sort(key=lambda x: (x['score'], x['matched_count'], x['loves']), reverse=True)
        return results[:max_results]

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Dict]:
        try:
            row = self.recipes_df.iloc[recipe_id]
            return {
                'id': recipe_id,
                'name': str(row.get('Title', 'Unknown')),
                'ingredients': self.parse_ingredients_detailed(str(row.get('Ingredients', ''))),
                'instructions': self.parse_steps_detailed(str(row.get('Steps', ''))),
                'category': str(row.get('Category', 'unknown')),
                'url': str(row.get('URL', '')),
                'loves': int(row.get('Loves', 0))
            }
        except:
            return None


# GLOBAL INSTANCE
_recipe_service = None

def get_recipe_service() -> RecipeService:
    global _recipe_service
    if _recipe_service is None:
        _recipe_service = RecipeService()
    return _recipe_service

recipe_service = get_recipe_service()
