"""
Database migration for farm management enhancements
Adds favorite, last_selected_at columns and indexes
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "fieldshift.db"

def migrate():
    """Add farm management columns"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(farms)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add is_favorite column if it doesn't exist
        if 'is_favorite' not in columns:
            print("Adding is_favorite column...")
            cursor.execute("ALTER TABLE farms ADD COLUMN is_favorite INTEGER DEFAULT 0")
            print("✓ Added is_favorite column")
        else:
            print("✓ is_favorite column already exists")
        
        # Add last_selected_at column if it doesn't exist
        if 'last_selected_at' not in columns:
            print("Adding last_selected_at column...")
            cursor.execute("ALTER TABLE farms ADD COLUMN last_selected_at TIMESTAMP")
            print("✓ Added last_selected_at column")
        else:
            print("✓ last_selected_at column already exists")
        
        # Create index for efficient sorting
        try:
            print("Creating index for favorites and sorting...")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_farms_favorite_selected 
                ON farms(is_favorite DESC, last_selected_at DESC, created_at DESC)
            """)
            print("✓ Created index")
        except sqlite3.Error as e:
            print(f"Index creation note: {e}")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Show current farms count
        cursor.execute("SELECT COUNT(*) FROM farms")
        count = cursor.fetchone()[0]
        print(f"📊 Current farms in database: {count}")
        
    except sqlite3.Error as e:
        print(f"❌ Migration error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Farm Management Enhancement Migration")
    print("=" * 60)
    migrate()
