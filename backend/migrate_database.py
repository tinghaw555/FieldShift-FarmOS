"""
Database migration script - Add hardware device support
Run this once to update existing databases
"""

import asyncio
import aiosqlite
from database.db import DB_PATH

async def migrate():
    print("Starting database migration...")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Check if hardware_devices table exists
        async with db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='hardware_devices'"
        ) as cursor:
            exists = await cursor.fetchone()
        
        if not exists:
            print("Creating hardware_devices table...")
            await db.execute("""
                CREATE TABLE hardware_devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT UNIQUE NOT NULL,
                    device_type TEXT DEFAULT 'ESP32',
                    farm_id INTEGER,
                    api_key TEXT NOT NULL,
                    last_seen TIMESTAMP,
                    firmware_version TEXT,
                    ip_address TEXT,
                    status TEXT DEFAULT 'offline',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE SET NULL
                )
            """)
            print("✅ Created hardware_devices table")
        else:
            print("✅ hardware_devices table already exists")
        
        # Check if sensor_readings has device_id column
        async with db.execute("PRAGMA table_info(sensor_readings)") as cursor:
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
        
        if 'device_id' not in column_names:
            print("Adding device_id column to sensor_readings...")
            await db.execute("ALTER TABLE sensor_readings ADD COLUMN device_id TEXT")
            print("✅ Added device_id column")
        else:
            print("✅ device_id column already exists")
        
        if 'is_valid' not in column_names:
            print("Adding is_valid column to sensor_readings...")
            await db.execute("ALTER TABLE sensor_readings ADD COLUMN is_valid INTEGER DEFAULT 1")
            print("✅ Added is_valid column")
        else:
            print("✅ is_valid column already exists")
        
        await db.commit()
        print("\n✅ Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate())
