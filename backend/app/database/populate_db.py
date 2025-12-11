# merge_all_datasets.py - Buat di folder backend
import sys
sys.path.insert(0, '/app')

import pandas as pd
from pathlib import Path
from app.database.db import SessionLocal, init_db
from app.database.models import Recipe

def merge_all_datasets():
    """Merge all CSV datasets to database"""
    
    # Fixed path - data is in /app/app/data/
    data_folder = Path("/app/app/data")
    
    csv_files = [
        "resep_dataset.csv",
        "resep_dataset2.csv",
        "dataset-sapi.csv",
        "dataset-ikan.csv",
        "dataset-ayam.csv"
    ]
    
    all_dataframes = []
    
    print("="*60)
    print("🔄 MERGING ALL RECIPE DATASETS")
    print("="*60)
    
    for csv_file in csv_files:
        csv_path = data_folder / csv_file
        
        if not csv_path.exists():
            print(f"⚠️  File not found: {csv_file}")
            continue
        
        try:
            df = pd.read_csv(csv_path)
            print(f"✅ Loaded {len(df):,} recipes from {csv_file}")
            all_dataframes.append(df)
        except Exception as e:
            print(f"❌ Error reading {csv_file}: {e}")
    
    if not all_dataframes:
        print("❌ No CSV files loaded!")
        return
    
    print(f"\n📊 Merging {len(all_dataframes)} datasets...")
    merged_df = pd.concat(all_dataframes, ignore_index=True)
    
    print(f"🔍 Total recipes before de-duplicate: {len(merged_df):,}")
    merged_df = merged_df.drop_duplicates(subset=['Title'], keep='first')
    print(f"✨ Total recipes after de-duplicate: {len(merged_df):,}")
    
    print(f"\n🔄 Initializing database...")
    init_db()
    
    session = SessionLocal()
    
    try:
        print(f"💾 Populating database with {len(merged_df):,} recipes...")
        success_count = 0
        
        # Bulk insert for better performance
        recipes_to_add = []
        for idx, row in merged_df.iterrows():
            try:
                recipe = Recipe(
                    id=int(idx),
                    title=str(row.get("Title", "") or ""),
                    category=str(row.get("Category", "") or ""),
                    ingredients=str(row.get("Ingredients", "") or ""),
                    steps=str(row.get("Steps", "") or ""),
                    url=str(row.get("URL", "") or ""),
                    loves=int(row.get("Loves", 0) or 0)
                )
                recipes_to_add.append(recipe)
                success_count += 1
                
                if len(recipes_to_add) >= 1000:
                    session.bulk_save_objects(recipes_to_add)
                    session.commit()
                    print(f"   Progress: {success_count:,}/{len(merged_df):,} ({(success_count/len(merged_df)*100):.1f}%)")
                    recipes_to_add = []
                    
            except Exception as e:
                print(f"   ⚠️  Error at index {idx}: {e}")
        
        # Save remaining
        if recipes_to_add:
            session.bulk_save_objects(recipes_to_add)
            session.commit()
        
        print("\n" + "="*60)
        print(f"✅ COMPLETED!")
        print(f"   Total inserted: {success_count:,} recipes")
        print("="*60)
        
        total_in_db = session.query(Recipe).count()
        print(f"\n📊 Total recipes in database: {total_in_db:,}")
        
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    merge_all_datasets()