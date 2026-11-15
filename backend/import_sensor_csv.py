"""
Import simulated sensor readings from CSV into database

This script imports the demonstration sensor dataset into SQLite,
allowing the Smart Farm dashboard to display readings through the backend API.
"""

import asyncio
import aiosqlite
import csv
from datetime import datetime
from pathlib import Path
from database.db import DB_PATH

CSV_PATH = Path(__file__).parent.parent / "hardware" / "fieldshift_simulated_esp32_sensor_readings.csv"

async def import_csv_readings():
    """Import CSV sensor readings into database"""
    
    if not CSV_PATH.exists():
        print(f"❌ CSV file not found: {CSV_PATH}")
        return
    
    print(f"📂 Reading CSV: {CSV_PATH}")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Check if CSV data already imported
        cursor = await db.execute(
            "SELECT COUNT(*) FROM sensor_readings WHERE device_id = 'SIM_ESP32_DEMO_001' AND is_simulated = 1"
        )
        existing_count = (await cursor.fetchone())[0]
        
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing CSV records")
            response = input("Delete and re-import? (y/n): ")
            if response.lower() == 'y':
                await db.execute(
                    "DELETE FROM sensor_readings WHERE device_id = 'SIM_ESP32_DEMO_001' AND is_simulated = 1"
                )
                await db.commit()
                print("🗑️  Deleted existing CSV records")
            else:
                print("⏭️  Skipping import")
                return
        
        # Read and parse CSV (handle BOM)
        with open(CSV_PATH, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"📊 Found {len(rows)} sensor readings in CSV")
        
        # Default to farm_id = 1 (or prompt user)
        farm_id = 1
        
        # Check if farm exists
        cursor = await db.execute("SELECT id, name FROM farms WHERE id = ?", (farm_id,))
        farm = await cursor.fetchone()
        
        if not farm:
            print(f"⚠️  Farm ID {farm_id} not found. Creating demo farm...")
            await db.execute(
                """INSERT INTO farms (id, name, latitude, longitude) 
                   VALUES (?, 'Demo Farm', 14.5995, 120.9842)""",
                (farm_id,)
            )
            await db.commit()
            print(f"✅ Created demo farm")
        else:
            print(f"✅ Using existing farm: {farm[1]} (ID: {farm[0]})")
        
        # Import sensor readings
        imported_count = 0
        
        for row in rows:
            timestamp_iso = row['timestamp_iso']
            temp = float(row['temperature_c'])
            humidity = float(row['relative_humidity_pct'])
            soil_raw = int(row['soil_moisture_adc_raw'])
            reservoir_raw = int(row['reservoir_level_adc_raw'])
            soil_pct = float(row['soil_moisture_pct_demo'])
            reservoir_pct = float(row['reservoir_level_pct_demo'])
            device_id = row['device_id']
            data_source = row['data_source']
            
            # Parse timestamp
            timestamp = datetime.fromisoformat(timestamp_iso.replace('+08:00', ''))
            
            # Insert temperature
            await db.execute(
                """INSERT INTO sensor_readings 
                   (farm_id, timestamp, sensor_type, value, unit, is_simulated, device_id, is_valid)
                   VALUES (?, ?, 'temperature', ?, '°C', 1, ?, 1)""",
                (farm_id, timestamp, temp, device_id)
            )
            
            # Insert humidity
            await db.execute(
                """INSERT INTO sensor_readings 
                   (farm_id, timestamp, sensor_type, value, unit, is_simulated, device_id, is_valid)
                   VALUES (?, ?, 'humidity', ?, '%', 1, ?, 1)""",
                (farm_id, timestamp, humidity, device_id)
            )
            
            # Insert soil moisture (use percentage, not raw ADC)
            await db.execute(
                """INSERT INTO sensor_readings 
                   (farm_id, timestamp, sensor_type, value, unit, is_simulated, device_id, is_valid)
                   VALUES (?, ?, 'soil_moisture', ?, '%', 1, ?, 1)""",
                (farm_id, timestamp, soil_pct, device_id)
            )
            
            # Insert reservoir/water level (use percentage, not raw ADC)
            await db.execute(
                """INSERT INTO sensor_readings 
                   (farm_id, timestamp, sensor_type, value, unit, is_simulated, device_id, is_valid)
                   VALUES (?, ?, 'water_level', ?, '%', 1, ?, 1)""",
                (farm_id, timestamp, reservoir_pct, device_id)
            )
            
            imported_count += 1
        
        await db.commit()
        
        print(f"✅ Imported {imported_count} sensor readings ({imported_count * 4} total records)")
        print(f"📊 Temperature, Humidity, Soil Moisture, Reservoir Level")
        print(f"📍 Farm ID: {farm_id}")
        print(f"🏷️  Device ID: {device_id}")
        print(f"🔖 Source: {data_source} (is_simulated = 1)")
        
        # Verify import
        cursor = await db.execute(
            """SELECT sensor_type, COUNT(*), MIN(timestamp), MAX(timestamp)
               FROM sensor_readings 
               WHERE device_id = 'SIM_ESP32_DEMO_001' AND is_simulated = 1
               GROUP BY sensor_type"""
        )
        results = await cursor.fetchall()
        
        print(f"\n✅ Verification:")
        for row in results:
            sensor_type, count, min_ts, max_ts = row
            print(f"   {sensor_type}: {count} readings from {min_ts} to {max_ts}")

if __name__ == "__main__":
    print("=" * 60)
    print("FieldShift FarmOS - CSV Sensor Data Import")
    print("=" * 60)
    asyncio.run(import_csv_readings())
    print("=" * 60)
    print("✅ Import complete!")
    print("📡 Readings now available via FastAPI /hardware/farm/{farm_id}/latest")
    print("=" * 60)
