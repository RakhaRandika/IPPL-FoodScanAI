# merge_all_datasets.py - Buat di folder backend
import pandas as pd
from pathlib import Path
from app.database import SessionLocal, init_db, Recipe

def merge_all_datasets():
    """Merge semua CSV dataset ke database"""
    
    data_folder = Path(__file__).parent / "app" / "data"
    
    # Daftar file CSV yang akan digabung
    csv_files = [
        "resep_dataset.csv",      # Dataset utama (14,945 resep)
        "resep_dataset2.csv",     # Dataset tambahan baru
        "dataset-sapi.csv",       # D
        "dataset-ikan.csv",       
        "dataset-ayam.csv"        
    ]
    
    # List untuk menampung semua dataframe
    all_dataframes = []
    
    print("="*60)
    print("🔄 MERGING ALL RECIPE DATASETS")
    print("="*60)
    
    # Baca semua CSV
    for csv_file in csv_files:
        csv_path = data_folder / csv_file
        
        if not csv_path.exists():
            print(f"⚠️  File tidak ditemukan: {csv_file}")
            continue
        
        try:
            df = pd.read_csv(csv_path)
            print(f"✅ Loaded {len(df):,} recipes from {csv_file}")
            all_dataframes.append(df)
        except Exception as e:
            print(f"❌ Error reading {csv_file}: {e}")
    
    if not all_dataframes:
        print("❌ Tidak ada dataset yang berhasil dibaca!")
        return
    
    # Gabungkan semua dataframe
    print(f"\n📊 Menggabungkan {len(all_dataframes)} dataset...")
    merged_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Hapus duplikat berdasarkan Title dan URL
    print(f"🔍 Total recipes sebelum de-duplicate: {len(merged_df):,}")
    merged_df = merged_df.drop_duplicates(subset=['Title', 'URL'], keep='first')
    print(f"✨ Total recipes setelah de-duplicate: {len(merged_df):,}")
    
    # Inisialisasi database
    print(f"\n🔄 Initializing database...")
    init_db()
    
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
                    category=str(row.get("Category", "") or ""),
                    ingredients=str(row.get("Ingredients", "") or ""),
                    steps=str(row.get("Steps", "") or ""),
                    url=str(row.get("URL", "") or ""),
                    loves=int(row.get("Loves", 0) or 0)
                )
                session.merge(recipe)  # Insert or update
                success_count += 1
                
                # Commit setiap 1000 recipes
                if idx % 1000 == 0:
                    print(f"   Progress: {idx:,}/{len(merged_df):,} ({(idx/len(merged_df)*100):.1f}%)")
                    session.commit()
                    
            except Exception as e:
                error_count += 1
                print(f"   ⚠️  Error pada index {idx}: {e}")
        
        # Commit sisa
        session.commit()
        
        print("\n" + "="*60)
        print(f"✅ SELESAI!")
        print(f"   Total berhasil: {success_count:,} recipes")
        print(f"   Total error: {error_count}")
        print("="*60)
        
        # Verifikasi database
        total_in_db = session.query(Recipe).count()
        print(f"\n📊 Total recipes di database: {total_in_db:,}")
        
        # Show sample
        print(f"\n📝 Sample resep dari masing-masing kategori:")
        categories = session.query(Recipe.category).distinct().limit(10).all()
        for cat in categories:
            count = session.query(Recipe).filter(Recipe.category == cat[0]).count()
            sample = session.query(Recipe).filter(Recipe.category == cat[0]).first()
            print(f"   - {cat[0]}: {count} resep (contoh: {sample.title})")
        
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    merge_all_datasets()