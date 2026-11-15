"""
SQLite database initialization and connection management
"""

import aiosqlite
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "fieldshift.db"

async def get_db():
    """Get database connection"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db

async def init_database():
    """Initialize database schema"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Farms table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS farms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Farm configurations
        await db.execute("""
            CREATE TABLE IF NOT EXISTS farm_configs (
                farm_id INTEGER PRIMARY KEY,
                soil_type TEXT,
                field_capacity REAL,
                wilting_point REAL,
                soil_depth REAL,
                irrigation_available INTEGER DEFAULT 1,
                irrigation_capacity REAL,
                FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
            )
        """)
        
        # Crop rotations
        await db.execute("""
            CREATE TABLE IF NOT EXISTS rotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farm_id INTEGER NOT NULL,
                rotation_type TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
            )
        """)
        
        # Rotation crops
        await db.execute("""
            CREATE TABLE IF NOT EXISTS rotation_crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rotation_id INTEGER NOT NULL,
                crop_name TEXT NOT NULL,
                planting_date TEXT NOT NULL,
                harvest_date TEXT NOT NULL,
                sequence_order INTEGER NOT NULL,
                FOREIGN KEY (rotation_id) REFERENCES rotations (id) ON DELETE CASCADE
            )
        """)
        
        # Climate cache
        await db.execute("""
            CREATE TABLE IF NOT EXISTS climate_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                source TEXT NOT NULL,
                data TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Forecast snapshots (for Ground Truth)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS forecast_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farm_id INTEGER NOT NULL,
                issue_time TIMESTAMP NOT NULL,
                valid_time TIMESTAMP NOT NULL,
                lead_hours INTEGER NOT NULL,
                temperature REAL,
                precipitation REAL,
                humidity REAL,
                data_source TEXT DEFAULT 'open-meteo',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
            )
        """)
        
        # Sensor readings (both real and simulated)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farm_id INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                sensor_type TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                is_simulated INTEGER DEFAULT 1,
                device_id TEXT,
                is_valid INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
            )
        """)
        
        # Hardware devices (ESP32 registration)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS hardware_devices (
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
        
        # Irrigation experiments
        await db.execute("""
            CREATE TABLE IF NOT EXISTS irrigation_experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farm_id INTEGER NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                initial_soil_moisture REAL,
                final_soil_moisture REAL,
                initial_water_level REAL,
                final_water_level REAL,
                temperature REAL,
                humidity REAL,
                recommendation TEXT,
                farmer_approved INTEGER DEFAULT 0,
                valve_opened INTEGER DEFAULT 0,
                duration_seconds INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
            )
        """)
        
        # Pump commands (for real NodeMCU pump control)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pump_commands (
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
        
        # Pump state history (track actual pump ON/OFF states)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pump_states (
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
        
        await db.commit()
        print(f"✅ Database initialized at {DB_PATH}")
