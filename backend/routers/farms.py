"""
Farms API Router - Farm management endpoints
Enhanced with favorites, search, rename, and safe delete
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import aiosqlite
import json
from datetime import datetime

from models.schemas import Farm, FarmCreate, FarmConfig, FarmUpdate
from database.db import get_db, DB_PATH

router = APIRouter()

@router.post("/", response_model=Farm)
async def create_farm(farm: FarmCreate):
    """Create a new farm"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO farms (name, latitude, longitude) 
               VALUES (?, ?, ?)""",
            (farm.name, farm.latitude, farm.longitude)
        )
        await db.commit()
        farm_id = cursor.lastrowid
        
        # Create default config
        await db.execute(
            """INSERT INTO farm_configs 
               (farm_id, soil_type, field_capacity, wilting_point, soil_depth, 
                irrigation_available, irrigation_capacity)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (farm_id, "loam", 0.30, 0.15, 1.0, 1, 20.0)
        )
        await db.commit()
        
        # Fetch and return created farm
        async with db.execute(
            "SELECT * FROM farms WHERE id = ?", (farm_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "latitude": row[2],
                    "longitude": row[3],
                    "created_at": row[4]
                }

@router.get("/", response_model=List[Farm])
async def list_farms(search: Optional[str] = Query(None)):
    """
    List all farms with sorting and optional search
    
    Sorting priority:
    1. Favorites first (is_favorite DESC)
    2. Recently selected (last_selected_at DESC)
    3. Recently created (created_at DESC)
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Build query with optional search
        query = """
            SELECT f.*, fc.soil_type, fc.field_capacity, fc.wilting_point, 
                   fc.soil_depth, fc.irrigation_available, fc.irrigation_capacity
            FROM farms f
            LEFT JOIN farm_configs fc ON f.id = fc.farm_id
        """
        
        params = []
        if search:
            query += " WHERE LOWER(f.name) LIKE LOWER(?)"
            params.append(f"%{search}%")
        
        query += " ORDER BY f.is_favorite DESC, f.last_selected_at DESC, f.created_at DESC"
        
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            farms = []
            for row in rows:
                farm_dict = dict(row)
                config = None
                if farm_dict.get('soil_type'):
                    config = {
                        "soil_type": farm_dict['soil_type'],
                        "field_capacity": farm_dict['field_capacity'],
                        "wilting_point": farm_dict['wilting_point'],
                        "soil_depth": farm_dict['soil_depth'],
                        "irrigation_available": bool(farm_dict['irrigation_available']),
                        "irrigation_capacity": farm_dict['irrigation_capacity']
                    }
                
                farms.append({
                    "id": farm_dict['id'],
                    "name": farm_dict['name'],
                    "latitude": farm_dict['latitude'],
                    "longitude": farm_dict['longitude'],
                    "created_at": farm_dict['created_at'],
                    "config": config,
                    "is_favorite": bool(farm_dict.get('is_favorite', 0)),
                    "last_selected_at": farm_dict.get('last_selected_at')
                })
            return farms

@router.get("/{farm_id}", response_model=Farm)
async def get_farm(farm_id: int):
    """Get a specific farm"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT f.*, fc.soil_type, fc.field_capacity, fc.wilting_point, 
                      fc.soil_depth, fc.irrigation_available, fc.irrigation_capacity
               FROM farms f
               LEFT JOIN farm_configs fc ON f.id = fc.farm_id
               WHERE f.id = ?""",
            (farm_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Farm not found")
            
            farm_dict = dict(row)
            config = None
            if farm_dict.get('soil_type'):
                config = {
                    "soil_type": farm_dict['soil_type'],
                    "field_capacity": farm_dict['field_capacity'],
                    "wilting_point": farm_dict['wilting_point'],
                    "soil_depth": farm_dict['soil_depth'],
                    "irrigation_available": bool(farm_dict['irrigation_available']),
                    "irrigation_capacity": farm_dict['irrigation_capacity']
                }
            
            return {
                "id": farm_dict['id'],
                "name": farm_dict['name'],
                "latitude": farm_dict['latitude'],
                "longitude": farm_dict['longitude'],
                "created_at": farm_dict['created_at'],
                "config": config
            }

@router.put("/{farm_id}", response_model=Farm)
async def update_farm(farm_id: int, update: FarmUpdate):
    """Update farm details"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Check farm exists
        async with db.execute("SELECT id FROM farms WHERE id = ?", (farm_id,)) as cursor:
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="Farm not found")
        
        # Update farm name if provided
        if update.name:
            await db.execute(
                "UPDATE farms SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (update.name, farm_id)
            )
        
        # Update config if provided
        if update.config:
            await db.execute(
                """UPDATE farm_configs SET
                   soil_type = ?, field_capacity = ?, wilting_point = ?,
                   soil_depth = ?, irrigation_available = ?, irrigation_capacity = ?
                   WHERE farm_id = ?""",
                (
                    update.config.soil_type,
                    update.config.field_capacity,
                    update.config.wilting_point,
                    update.config.soil_depth,
                    1 if update.config.irrigation_available else 0,
                    update.config.irrigation_capacity,
                    farm_id
                )
            )
        
        await db.commit()
        
        # Return updated farm
        return await get_farm(farm_id)

@router.delete("/{farm_id}")
async def delete_farm(farm_id: int):
    """
    Delete a farm safely
    
    This will cascade delete:
    - Farm configurations
    - Crop rotations and rotation crops
    - Sensor readings (both real and simulated)
    - Irrigation experiments
    - Climate cache entries
    - Forecast snapshots
    - Pump commands and states (if any)
    
    Hardware devices will have their farm_id set to NULL (not deleted)
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Check if farm exists
        async with db.execute("SELECT name FROM farms WHERE id = ?", (farm_id,)) as cursor:
            farm = await cursor.fetchone()
            if not farm:
                raise HTTPException(status_code=404, detail="Farm not found")
        
        # Get impact information before deletion
        async with db.execute(
            "SELECT COUNT(*) FROM rotations WHERE farm_id = ?", (farm_id,)
        ) as cursor:
            rotation_count = (await cursor.fetchone())[0]
        
        async with db.execute(
            "SELECT COUNT(*) FROM sensor_readings WHERE farm_id = ?", (farm_id,)
        ) as cursor:
            sensor_count = (await cursor.fetchone())[0]
        
        async with db.execute(
            "SELECT COUNT(*) FROM irrigation_experiments WHERE farm_id = ?", (farm_id,)
        ) as cursor:
            experiment_count = (await cursor.fetchone())[0]
        
        async with db.execute(
            "SELECT COUNT(*) FROM hardware_devices WHERE farm_id = ?", (farm_id,)
        ) as cursor:
            device_count = (await cursor.fetchone())[0]
        
        # Delete farm (CASCADE will handle related records)
        cursor = await db.execute("DELETE FROM farms WHERE id = ?", (farm_id,))
        await db.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Farm not found")
        
        return {
            "message": f"Farm '{farm[0]}' deleted successfully",
            "deleted": {
                "rotations": rotation_count,
                "sensor_readings": sensor_count,
                "irrigation_experiments": experiment_count,
                "devices_unlinked": device_count
            }
        }

@router.get("/{farm_id}/delete-impact")
async def get_delete_impact(farm_id: int):
    """
    Check what would be affected if this farm is deleted
    Used for confirmation dialogs
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Check if farm exists
        async with db.execute("SELECT name FROM farms WHERE id = ?", (farm_id,)) as cursor:
            farm = await cursor.fetchone()
            if not farm:
                raise HTTPException(status_code=404, detail="Farm not found")
        
        # Count related records
        async with db.execute(
            "SELECT COUNT(*) FROM rotations WHERE farm_id = ?", (farm_id,)
        ) as cursor:
            rotation_count = (await cursor.fetchone())[0]
        
        async with db.execute(
            "SELECT COUNT(*) FROM sensor_readings WHERE farm_id = ?", (farm_id,)
        ) as cursor:
            sensor_count = (await cursor.fetchone())[0]
        
        async with db.execute(
            "SELECT COUNT(*) FROM irrigation_experiments WHERE farm_id = ?", (farm_id,)
        ) as cursor:
            experiment_count = (await cursor.fetchone())[0]
        
        async with db.execute(
            "SELECT COUNT(*) FROM hardware_devices WHERE farm_id = ?", (farm_id,)
        ) as cursor:
            device_count = (await cursor.fetchone())[0]
        
        return {
            "farm_name": farm[0],
            "farm_id": farm_id,
            "impact": {
                "rotations": rotation_count,
                "sensor_readings": sensor_count,
                "irrigation_experiments": experiment_count,
                "connected_devices": device_count
            },
            "warning": "This action cannot be undone"
        }

@router.put("/{farm_id}/favorite")
async def toggle_favorite(farm_id: int, favorite: dict):
    """Toggle farm favorite status"""
    is_favorite = favorite.get("is_favorite", False)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Check farm exists
        async with db.execute("SELECT id FROM farms WHERE id = ?", (farm_id,)) as cursor:
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="Farm not found")
        
        # Update favorite status
        await db.execute(
            "UPDATE farms SET is_favorite = ? WHERE id = ?",
            (1 if is_favorite else 0, farm_id)
        )
        await db.commit()
        
        return {
            "success": True,
            "farm_id": farm_id,
            "is_favorite": is_favorite
        }

@router.put("/{farm_id}/select")
async def mark_farm_selected(farm_id: int):
    """Update last_selected_at timestamp when farm is selected"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Check farm exists
        async with db.execute("SELECT id FROM farms WHERE id = ?", (farm_id,)) as cursor:
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="Farm not found")
        
        # Update last_selected_at
        await db.execute(
            "UPDATE farms SET last_selected_at = ? WHERE id = ?",
            (datetime.now().isoformat(), farm_id)
        )
        await db.commit()
        
        return {"success": True, "farm_id": farm_id}

@router.put("/{farm_id}/rename")
async def rename_farm(farm_id: int, data: dict):
    """Rename a farm"""
    new_name = data.get("name", "").strip()
    
    if not new_name:
        raise HTTPException(status_code=400, detail="Farm name cannot be empty")
    
    if len(new_name) > 200:
        raise HTTPException(status_code=400, detail="Farm name too long (max 200 characters)")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Check farm exists
        async with db.execute("SELECT name FROM farms WHERE id = ?", (farm_id,)) as cursor:
            old_farm = await cursor.fetchone()
            if not old_farm:
                raise HTTPException(status_code=404, detail="Farm not found")
        
        # Check if name already exists (for another farm)
        async with db.execute(
            "SELECT id FROM farms WHERE name = ? AND id != ?", (new_name, farm_id)
        ) as cursor:
            if await cursor.fetchone():
                raise HTTPException(status_code=409, detail="A farm with this name already exists")
        
        # Update name
        await db.execute(
            "UPDATE farms SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_name, farm_id)
        )
        await db.commit()
        
        return {
            "success": True,
            "farm_id": farm_id,
            "old_name": old_farm[0],
            "new_name": new_name
        }

@router.delete("/{farm_id}")
async def delete_farm(farm_id: int):
    """Delete a farm"""
    cursor = await db.execute("DELETE FROM farms WHERE id = ?", (farm_id,))
    await db.commit()
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    return {"message": "Farm deleted successfully"}

@router.put("/{farm_id}/irrigation")
async def update_irrigation_capacity(farm_id: int, irrigation_config: dict):
    """
    Update farm irrigation capacity from farmer-friendly inputs
    
    Accepts either:
    1. Direct mm/week (advanced mode)
    2. Calculated effective mm/week from farmer inputs (bucket/pump)
    
    Body: {
        "irrigation_mm_week": 10.5,
        "irrigation_mm_day": 1.5,
        "source": "calculated" | "measured" | "advanced",
        "weekly_litres": 1500,
        "plot_area_m2": 1000,
        "efficiency_percent": 70,
        "method": "bucket" | "pump" | "rainwater" | "not_sure"
    }
    """
    irrigation_mm_week = irrigation_config.get("irrigation_mm_week", 0)
    irrigation_mm_day = irrigation_config.get("irrigation_mm_day", irrigation_mm_week / 7 if irrigation_mm_week else 0)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Check farm exists
        async with db.execute("SELECT id FROM farms WHERE id = ?", (farm_id,)) as cursor:
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="Farm not found")
        
        # Update irrigation capacity (convert weekly to daily for storage)
        await db.execute(
            """UPDATE farm_configs SET irrigation_capacity = ? WHERE farm_id = ?""",
            (irrigation_mm_day, farm_id)
        )
        await db.commit()
        
        return {
            "success": True,
            "farm_id": farm_id,
            "irrigation_capacity_mm_day": round(irrigation_mm_day, 3),
            "irrigation_capacity_mm_week": round(irrigation_mm_week, 3),
            "source": irrigation_config.get("source", "calculated"),
            "method": irrigation_config.get("method"),
            "message": "Irrigation capacity updated successfully"
        }
