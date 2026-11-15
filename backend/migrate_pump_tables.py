"""
Database migration to add pump control tables
"""
import asyncio
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "fieldshift.db"

async def migrate():
    print("Starting pump control tables migration...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if pump_commands table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pump_commands'")
    if cursor.fetchone():
        print("✅ pump_commands table already exists")
    else:
        print("Creating pump_commands table...")
        cursor.execute("""
            CREATE TABLE pump_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_id TEXT UNIQUE NOT NULL,
                device_id TEXT NOT NULL,
                farm_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                duration_seconds INTEGER,
                requested_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                acknowledged_at TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT DEFAULT 'pending',
                result TEXT,
                error_message TEXT,
                FOREIGN KEY (device_id) REFERENCES hardware_devices (device_id) ON DELETE CASCADE,
                FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
            )
        """)
        print("✅ pump_commands table created")
    
    # Check if pump_states table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pump_states'")
    if cursor.fetchone():
        print("✅ pump_states table already exists")
    else:
        print("Creating pump_states table...")
        cursor.execute("""
            CREATE TABLE pump_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                farm_id INTEGER NOT NULL,
                state TEXT NOT NULL,
                started_at TIMESTAMP NOT NULL,
                ended_at TIMESTAMP,
                duration_seconds INTEGER,
                water_delivered_ml INTEGER,
                command_id TEXT,
                fault_reason TEXT,
                FOREIGN KEY (device_id) REFERENCES hardware_devices (device_id) ON DELETE CASCADE,
                FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE,
                FOREIGN KEY (command_id) REFERENCES pump_commands (command_id) ON DELETE SET NULL
            )
        """)
        print("✅ pump_states table created")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate())
