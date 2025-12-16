"""
Merge all recipe datasets into SQLite database
"""
import pandas as pd
import numpy as np
from pathlib import Path
from app.database.db import SessionLocal, engine
from app.database.models import Recipe, Base

def clean_text(text):
    """Clean text: handle NaN, strip whitespace, remove consecutive duplicates"""
    if pd.isna(text) or text is None:
        return ""
    
    text = str(text).strip()
    
    # Remove consecutive duplicate words
    words = text.split()
    cleaned_words = []
    prev_word = None
    
    for word in words:
        if word != prev_word:  # Skip if same as previous word
            cleaned_words.append(word)
        prev_word = word
    
    return " ".join(cleaned_words)

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
    before_dedup = len(merged_df)
    print(f"🔍 Total recipes sebelum de-duplicate: {before_dedup:,}")
    merged_df = merged_df.drop_duplicates(subset=['Title'], keep='first')
    after_dedup = len(merged_df)
    print(f"✨ Total recipes setelah de-duplicate: {after_dedup:,}")
    print(f"   Removed: {before_dedup - after_dedup:,} duplicates")
    
    # Clean all text columns
    print(f"\n🧹 Cleaning text data...")
    merged_df['Title'] = merged_df['Title'].apply(clean_text)
    merged_df['Category'] = merged_df['Category'].apply(clean_text)
    merged_df['Ingredients'] = merged_df['Ingredients'].apply(clean_text)
    merged_df['Steps'] = merged_df['Steps'].apply(clean_text)
    merged_df['URL'] = merged_df['URL'].apply(clean_text)
    
    # Handle Loves column (NaN -> 0)
    merged_df['Loves'] = pd.to_numeric(merged_df['Loves'], errors='coerce').fillna(0).astype(int)
    
    # Remove rows with empty title
    merged_df = merged_df[merged_df['Title'] != '']
    print(f"   Final valid recipes: {len(merged_df):,}")
    
    # Drop existing tables and recreate
    print(f"\n🔄 Recreating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
        print(f"💾 Populating database dengan {len(merged_df):,} recipes...")
        print(f"   Using bulk insert for better performance...")
        
        success_count = 0
        error_count = 0
        recipes_batch = []
        BATCH_SIZE = 500
        
        for idx, row in merged_df.iterrows():
            try:
                recipe = Recipe(
                    title=row['Title'],
                    category=row['Category'],
                    ingredients=row['Ingredients'],
                    steps=row['Steps'],
                    url=row['URL'],
                    loves=row['Loves']
                )
                recipes_batch.append(recipe)
                success_count += 1
                
                # Commit in batches
                if len(recipes_batch) >= BATCH_SIZE:
                    session.bulk_save_objects(recipes_batch)
                    session.commit()
                    progress = (success_count / len(merged_df)) * 100
                    print(f"   Progress: {success_count:,}/{len(merged_df):,} ({progress:.1f}%)")
                    recipes_batch = []
                    
            except Exception as e:
                error_count += 1
                if error_count <= 10:  # Show first 10 errors only
                    print(f"   ⚠️  Error at row {idx}: {str(e)[:80]}")
        
        # Commit remaining batch
        if recipes_batch:
            session.bulk_save_objects(recipes_batch)
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
