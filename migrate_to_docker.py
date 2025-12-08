"""
Migrate SQLite database to Docker PostgreSQL
Run this after Docker containers are up
"""
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path

def migrate_to_postgres():
    # PostgreSQL connection
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="foodscan_db",
        user="foodscan_user",
        password="foodscan_password"
    )
    cursor = conn.cursor()
    
    print("="*60)
    print("🐘 MIGRATING SQLITE TO POSTGRESQL")
    print("="*60)
    
    try:
        # Read from SQLite
        import sqlite3
        sqlite_path = Path(__file__).parent / "backend" / "foodscan.db"
        
        if not sqlite_path.exists():
            print(f"❌ SQLite database not found at: {sqlite_path}")
            return
        
        sqlite_conn = sqlite3.connect(sqlite_path)
        
        # Get all recipes
        df = pd.read_sql_query("SELECT * FROM recipes", sqlite_conn)
        print(f"✅ Read {len(df):,} recipes from SQLite")
        
        # Clear existing data in PostgreSQL
        cursor.execute("TRUNCATE TABLE recipes RESTART IDENTITY CASCADE")
        print(f"🗑️  Cleared existing PostgreSQL data")
        
        # Prepare data for insertion
        recipes_data = []
        for _, row in df.iterrows():
            recipes_data.append((
                row['title'],
                row['category'],
                row['ingredients'],
                row['steps'],
                row['url'],
                row['loves']
            ))
        
        # Bulk insert into PostgreSQL
        insert_query = """
            INSERT INTO recipes (title, category, ingredients, steps, url, loves)
            VALUES %s
        """
        
        print(f"💾 Inserting {len(recipes_data):,} recipes into PostgreSQL...")
        execute_values(cursor, insert_query, recipes_data, page_size=1000)
        
        conn.commit()
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM recipes")
        count = cursor.fetchone()[0]
        
        print("\n" + "="*60)
        print(f"✅ MIGRATION COMPLETE!")
        print(f"   Total recipes in PostgreSQL: {count:,}")
        print("="*60)
        
        # Show sample
        cursor.execute("SELECT title, category FROM recipes LIMIT 10")
        samples = cursor.fetchall()
        print(f"\n📝 Sample recipes:")
        for title, category in samples:
            print(f"   - {title} ({category})")
        
        sqlite_conn.close()
        
    except Exception as e:
        print(f"\n❌ Migration Error: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("\n⚠️  Make sure Docker containers are running:")
    print("   docker-compose up -d postgres")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    migrate_to_postgres()
