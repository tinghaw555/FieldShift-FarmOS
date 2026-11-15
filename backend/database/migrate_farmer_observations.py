"""
Database migration: Add farmer_observations table for Phase 2

This migration creates the table structure for farmer-provided data upload,
CSV import, and manual entry functionality.
"""

import asyncio
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent / "fieldshift.db"

async def migrate():
    """Add farmer_observations table"""
    async with aiosqlite.connect(DB_PATH) as db:
        
        # Create farmer_observations table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS farmer_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farm_id INTEGER NOT NULL,
                observation_date TEXT NOT NULL,
                observation_time TEXT,
                temperature REAL,
                humidity REAL,
                rainfall REAL,
                soil_moisture_raw INTEGER,
                soil_moisture_percent REAL,
                water_level TEXT CHECK(water_level IN ('Low', 'OK', 'Unknown', NULL)),
                notes TEXT,
                data_source TEXT DEFAULT 'Farmer-Provided',
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                upload_method TEXT DEFAULT 'csv',
                validation_status TEXT DEFAULT 'valid',
                validation_notes TEXT,
                FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
            )
        """)
        
        # Create index for efficient queries
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_farmer_obs_farm_date 
            ON farmer_observations(farm_id, observation_date DESC)
        """)
        
        # Add data_source column to sensor_readings if not exists
        try:
            await db.execute("""
                ALTER TABLE sensor_readings 
                ADD COLUMN data_source TEXT DEFAULT 'Real Sensor'
            """)
            print("✅ Added data_source column to sensor_readings")
        except Exception as e:
            # Column might already exist
            if "duplicate column" not in str(e).lower():
                print(f"⚠️  sensor_readings data_source: {e}")
        
        # Update existing simulated data
        await db.execute("""
            UPDATE sensor_readings 
            SET data_source = 'Demo Mode' 
            WHERE is_simulated = 1 AND (data_source IS NULL OR data_source = 'Real Sensor')
        """)
        
        await db.execute("""
            UPDATE sensor_readings 
            SET data_source = 'Real Sensor' 
            WHERE is_simulated = 0 AND (data_source IS NULL OR data_source = 'Demo Mode')
        """)
        
        await db.commit()
        
        # Verify the migration
        async with db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='farmer_observations'") as cursor:
            result = await cursor.fetchone()
            if result:
                print("✅ farmer_observations table created successfully")
            else:
                raise Exception("❌ Failed to create farmer_observations table")
        
        # Count existing farms
        async with db.execute("SELECT COUNT(*) FROM farms") as cursor:
            count = await cursor.fetchone()
            print(f"✅ Found {count[0]} existing farms")
        
        print(f"✅ Phase 2 database migration completed successfully")
        print(f"📂 Database: {DB_PATH}")

if __name__ == "__main__":
    asyncio.run(migrate())
