"""
Merge all recipe datasets into SQLite database
"""
import pandas as pd
from pathlib import Path
from app.database.db import SessionLocal, engine
from app.database.models import Recipe, Base

def merge_all_datasets():
    """Merge semua CSV dataset ke database"""
    
    data_folder = Path(__file__).parent / "app" / "data"
    
    # Daftar file CSV yang akan digabung
    csv_files = [
        ("resep_dataset.csv", "Ingredients"),      # Dataset utama
        ("resep_dataset2.csv", "Ingredients"),     # Dataset tambahan English
        ("dataset-sapi.csv", "Ingredients"),       # Dataset daging sapi
        ("dataset-ikan.csv", "Ingredients"),       # Dataset ikan
        ("dataset-ayam.csv", "Ingredients")        # Dataset ayam
    ]
    
    all_dataframes = []
    
    print("="*60)
    print("🔄 MERGING ALL RECIPE DATASETS")
    print("="*60)
    
    # Baca semua CSV
    for csv_file, ing_col in csv_files:
        csv_path = data_folder / csv_file
        
        if not csv_path.exists():
            print(f"⚠️  File tidak ditemukan: {csv_file}")
            continue
        
        try:
            df = pd.read_csv(csv_path)
            
            # Normalisasi kolom names
            if 'Title' not in df.columns:
                df['Title'] = df.get('title', '')
            if 'Category' not in df.columns:
                df['Category'] = df.get('category', 'General')
            if 'Ingredients' not in df.columns:
                if 'ingredients' in df.columns:
                    df['Ingredients'] = df['ingredients']
                elif 'Cleaned_Ingredients' in df.columns:
                    df['Ingredients'] = df['Cleaned_Ingredients']
            if 'Steps' not in df.columns:
                if 'steps' in df.columns:
                    df['Steps'] = df['steps']
                elif 'Instructions' in df.columns:
                    df['Steps'] = df['Instructions']
            if 'URL' not in df.columns:
                if 'url' in df.columns:
                    df['URL'] = df['url']
                else:
                    df['URL'] = ''
            if 'Loves' not in df.columns:
                df['Loves'] = df.get('loves', 0)
            
            # Keep only needed columns
            df = df[['Title', 'Category', 'Ingredients', 'Steps', 'URL', 'Loves']]
            
            print(f"✅ Loaded {len(df):,} recipes from {csv_file}")
            all_dataframes.append(df)
        except Exception as e:
            print(f"❌ Error reading {csv_file}: {e}")
            import traceback
            traceback.print_exc()
    
    if not all_dataframes:
        print("❌ Tidak ada dataset yang berhasil dibaca!")
        return
    
    # Gabungkan semua dataframe
    print(f"\n📊 Menggabungkan {len(all_dataframes)} dataset...")
    merged_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Hapus duplikat berdasarkan Title
    print(f"🔍 Total recipes sebelum de-duplicate: {len(merged_df):,}")
    merged_df = merged_df.drop_duplicates(subset=['Title'], keep='first')
    print(f"✨ Total recipes setelah de-duplicate: {len(merged_df):,}")
    
    # Drop existing tables and recreate
    print(f"\n🔄 Recreating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
        print(f"💾 Populating database dengan {len(merged_df):,} recipes...")
        success_count = 0
        error_count = 0
        
        for idx, row in merged_df.iterrows():
            try:
                recipe = Recipe(
                    id=int(idx),
                    title=str(row.get("Title", "") or ""),
                    category=str(row.get("Category", "") or "General"),
                    ingredients=str(row.get("Ingredients", "") or ""),
                    steps=str(row.get("Steps", "") or ""),
                    url=str(row.get("URL", "") or ""),
                    loves=int(row.get("Loves", 0) or 0)
                )
                session.add(recipe)
                success_count += 1
                
                # Commit setiap 1000 recipes
                if idx % 1000 == 0 and idx > 0:
                    print(f"   Progress: {idx:,}/{len(merged_df):,} ({(idx/len(merged_df)*100):.1f}%)")
                    session.commit()
                    
            except Exception as e:
                error_count += 1
                if error_count <= 5:  # Show first 5 errors only
                    print(f"   ⚠️  Error pada index {idx}: {e}")
        
        # Commit sisa
        session.commit()
        
        print("\n" + "="*60)
        print(f"✅ SELESAI!")
        print(f"   Total berhasil: {success_count:,} recipes")
        if error_count > 0:
            print(f"   Total error: {error_count}")
        print("="*60)
        
        # Verifikasi database
        total_in_db = session.query(Recipe).count()
        print(f"\n📊 Total recipes di database: {total_in_db:,}")
        
        # Show sample per category
        print(f"\n📝 Sample resep dari database:")
        samples = session.query(Recipe).limit(10).all()
        for s in samples:
            print(f"   - {s.title} (Category: {s.category})")
        
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    merge_all_datasets()
