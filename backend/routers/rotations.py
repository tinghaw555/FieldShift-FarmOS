"""
Crop Rotations API Router - Rotation comparison and analysis
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, date, timedelta
from typing import List
import aiosqlite
import json

from models.schemas import (
    Rotation, RotationCreate, RotationAnalysis,
    RotationComparisonRequest, RotationComparisonResponse,
    CropWaterBalanceResult, WaterBalanceDay
)
from services.crop_knowledge import get_crop_params, get_total_season_length
from services.water_balance import (
    WaterBalanceModel, SoilParameters, DailyWeather,
    summarize_water_balance
)
from database.db import DB_PATH

router = APIRouter()

@router.post("/", response_model=Rotation)
async def create_rotation(rotation: RotationCreate):
    """Create a new crop rotation"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Create rotation
        cursor = await db.execute(
            """INSERT INTO rotations (farm_id, rotation_type, name)
               VALUES (?, ?, ?)""",
            (rotation.farm_id, rotation.rotation_type, rotation.name)
        )
        await db.commit()
        rotation_id = cursor.lastrowid
        
        # Add crops
        for crop in rotation.crops:
            await db.execute(
                """INSERT INTO rotation_crops 
                   (rotation_id, crop_name, planting_date, harvest_date, sequence_order)
                   VALUES (?, ?, ?, ?, ?)""",
                (rotation_id, crop.crop_name, crop.planting_date, 
                 crop.harvest_date, crop.sequence_order)
            )
        
        await db.commit()
        
        # Fetch and return
        return await get_rotation(rotation_id)

@router.get("/{rotation_id}", response_model=Rotation)
async def get_rotation(rotation_id: int):
    """Get a rotation with its crops"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Get rotation
        async with db.execute(
            "SELECT * FROM rotations WHERE id = ?", (rotation_id,)
        ) as cursor:
            rotation_row = await cursor.fetchone()
            if not rotation_row:
                raise HTTPException(status_code=404, detail="Rotation not found")
        
        # Get crops
        async with db.execute(
            """SELECT * FROM rotation_crops 
               WHERE rotation_id = ? 
               ORDER BY sequence_order""",
            (rotation_id,)
        ) as cursor:
            crop_rows = await cursor.fetchall()
        
        crops = [
            {
                "crop_name": row['crop_name'],
                "planting_date": row['planting_date'],
                "harvest_date": row['harvest_date'],
                "sequence_order": row['sequence_order']
            }
            for row in crop_rows
        ]
        
        return {
            "id": rotation_row['id'],
            "farm_id": rotation_row['farm_id'],
            "rotation_type": rotation_row['rotation_type'],
            "name": rotation_row['name'],
            "created_at": rotation_row['created_at'],
            "crops": crops
        }

@router.get("/farm/{farm_id}")
async def list_farm_rotations(farm_id: int):
    """List all rotations for a farm"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id FROM rotations WHERE farm_id = ?", (farm_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            
            rotations = []
            for row in rows:
                rotation = await get_rotation(row['id'])
                rotations.append(rotation)
            
            return rotations

@router.post("/calculate")
async def calculate_water_needs(request: dict):
    """
    Calculate water needs for a single crop rotation
    
    Uses NASA POWER historical climate data and FAO-56 crop water model
    """
    from services.nasa_power import nasa_power_service
    import asyncio
    from datetime import date
    
    farm_id = request.get("farm_id")
    latitude = request.get("latitude")
    longitude = request.get("longitude")
    year = request.get("year", 2023)
    crops = request.get("crops", [])
    
    if not latitude or not longitude:
        raise HTTPException(status_code=400, detail="Farm coordinates required")
    
    if not crops:
        raise HTTPException(status_code=400, detail="At least one crop required")
    
    try:
        # Get historical climate data for the growing season
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        climate_data = await nasa_power_service.get_climate_data(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date
        )
        
        # Calculate water balance for each crop
        total_water_demand = 0.0
        total_stress_days = 0
        total_irrigation_need = 0.0
        analysis_results = []
        
        for crop_config in crops:
            crop_name = crop_config.get("crop", "corn")
            planting_str = crop_config.get("planting", "05-01")
            harvest_str = crop_config.get("harvest", "10-15")
            
            # Parse planting and harvest dates
            try:
                plant_month, plant_day = map(int, planting_str.split("-"))
                harvest_month, harvest_day = map(int, harvest_str.split("-"))
                
                planting_date = date(year, plant_month, plant_day)
                harvest_date = date(year, harvest_month, harvest_day)
            except:
                # Default to corn season if parsing fails
                planting_date = date(year, 5, 1)
                harvest_date = date(year, 10, 15)
            
            # Get crop parameters
            crop_params = get_crop_params(crop_name)
            if not crop_params:
                continue
            
            # Calculate seasonal ETc (simplified for hackathon)
            # In production, this would use full daily water balance model
            season_length = (harvest_date - planting_date).days
            avg_kc = (crop_params.kc_ini + crop_params.kc_mid + crop_params.kc_end) / 3
            
            # Filter climate data for growing season
            season_climate = [
                d for d in climate_data
                if planting_date.strftime("%Y-%m-%d") <= d["date"] <= harvest_date.strftime("%Y-%m-%d")
            ]
            
            if not season_climate:
                continue
            
            # Calculate ET0 and ETc (simplified)
            total_precip = sum(d.get("precipitation", 0) or 0 for d in season_climate)
            avg_temp = sum(d.get("temperature_mean", 20) or 20 for d in season_climate) / max(len(season_climate), 1)
            avg_rad = sum(d.get("solar_radiation", 15) or 15 for d in season_climate) / max(len(season_climate), 1)
            
            # Simplified ET0 calculation (MJ/m²/day to mm/day)
            # Using temperature-based approximation
            et0_daily = 0.0023 * (avg_temp + 17.8) * (avg_rad ** 0.5) * 0.408
            etc_daily = et0_daily * avg_kc
            
            seasonal_etc = etc_daily * season_length
            
            # Estimate water deficit
            water_deficit = max(0, seasonal_etc - total_precip * 0.8)  # 80% effective rainfall
            
            # Estimate stress days (simplified)
            stress_days = int(water_deficit / max(seasonal_etc / season_length * 3, 1))  # Rough estimate
            stress_days = min(stress_days, season_length // 3)  # Cap at 1/3 of season
            
            total_water_demand += seasonal_etc
            total_stress_days += stress_days
            total_irrigation_need += water_deficit
            
            analysis_results.append({
                "crop": crop_name,
                "planting_date": planting_date.strftime("%Y-%m-%d"),
                "harvest_date": harvest_date.strftime("%Y-%m-%d"),
                "season_length_days": season_length,
                "seasonal_water_demand_mm": round(seasonal_etc, 1),
                "precipitation_mm": round(total_precip, 1),
                "irrigation_need_mm": round(water_deficit, 1),
                "estimated_stress_days": stress_days
            })
        
        return {
            "success": True,
            "farm_id": farm_id,
            "latitude": latitude,
            "longitude": longitude,
            "year": year,
            "data_source": "NASA POWER Historical Climate",
            "total_seasonal_water_demand_mm": round(total_water_demand, 1),
            "total_stress_days": total_stress_days,
            "total_irrigation_need_mm": round(total_irrigation_need, 1),
            "crops_analyzed": len(analysis_results),
            "crop_results": analysis_results,
            "assumptions": {
                "effective_rainfall_fraction": 0.80,
                "model": "Simplified FAO-56 crop coefficient method",
                "climate_source": "NASA POWER daily data",
                "note": "Values are estimates for comparison, not precise predictions"
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@router.post("/compare")
async def compare_rotations(request: dict):
    """
    Compare three crop rotation strategies
    
    Calculates water needs for current, small_shift, and alternative rotations
    using the same farm location and climate year.
    Uses farm's configured irrigation capacity from database.
    """
    from services.nasa_power import nasa_power_service
    from datetime import date
    
    farm_id = request.get("farm_id")
    latitude = request.get("latitude")
    longitude = request.get("longitude")
    year = request.get("year", 2023)
    rotations = request.get("rotations", {})
    
    if not latitude or not longitude:
        raise HTTPException(status_code=400, detail="Farm coordinates required")
    
    if not rotations:
        raise HTTPException(status_code=400, detail="Rotation configurations required")
    
    # Fetch farm irrigation capacity from database
    irrigation_capacity_mm_day = None
    if farm_id:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT irrigation_capacity FROM farm_configs WHERE farm_id = ?",
                (farm_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    irrigation_capacity_mm_day = row[0]
    
    results = {}
    
    for rotation_type in ["current", "small_shift", "alternative"]:
        crops = rotations.get(rotation_type, [])
        
        if not crops:
            results[rotation_type] = {
                "error": "No crops configured",
                "feasible": False
            }
            continue
        
        # Calculate water needs for this rotation
        calc_request = {
            "farm_id": farm_id,
            "latitude": latitude,
            "longitude": longitude,
            "year": year,
            "crops": crops
        }
        
        try:
            # Call our calculate endpoint logic
            calc_result = await calculate_water_needs(calc_request)
            results[rotation_type] = calc_result
            
            # Check feasibility against irrigation capacity
            if irrigation_capacity_mm_day is not None:
                # Convert daily capacity to seasonal (26 weeks ~= 182 days)
                seasonal_irrigation_available_mm = irrigation_capacity_mm_day * 182
                total_irrigation_need = calc_result.get("total_irrigation_need_mm", 0)
                
                # Feasible if irrigation need can be met
                results[rotation_type]["feasible"] = total_irrigation_need <= seasonal_irrigation_available_mm
                results[rotation_type]["irrigation_capacity_mm_day"] = irrigation_capacity_mm_day
                results[rotation_type]["irrigation_deficit_mm"] = max(0, total_irrigation_need - seasonal_irrigation_available_mm)
            else:
                results[rotation_type]["feasible"] = True  # Unknown capacity, assume feasible
        except Exception as e:
            results[rotation_type] = {
                "error": str(e),
                "feasible": False
            }
    
    # Determine preferred rotation based on water stress and feasibility
    feasible_results = {k: v for k, v in results.items() if v.get("feasible")}
    
    if len(feasible_results) > 1:
        # Prefer rotation with lowest stress days among feasible options
        preferred = min(feasible_results.items(), key=lambda x: x[1].get("total_stress_days", 999))
        preferred_rotation = preferred[0]
        preferred_reason = f"Lowest estimated water stress days ({preferred[1]['total_stress_days']})"
    elif len(feasible_results) == 1:
        preferred_rotation = list(feasible_results.keys())[0]
        preferred_reason = "Only feasible rotation"
    else:
        preferred_rotation = None
        preferred_reason = "No feasible rotations with current irrigation capacity"
    
    return {
        "success": True,
        "farm_id": farm_id,
        "latitude": latitude,
        "longitude": longitude,
        "year": year,
        "irrigation_capacity_mm_day": irrigation_capacity_mm_day,
        "data_source": "NASA POWER Historical Climate",
        "results": results,
        "comparison": {
            "preferred_rotation": preferred_rotation,
            "preferred_reason": preferred_reason,
            "note": "Comparison based on estimated water stress and irrigation capacity. Consider other factors: yield, labor, equipment, markets."
        }
    }

@router.delete("/{rotation_id}")
async def delete_rotation(rotation_id: int):
    """Delete a rotation"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM rotations WHERE id = ?", (rotation_id,)
        )
        await db.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Rotation not found")
        
        return {"message": "Rotation deleted successfully"}

@router.post("/flippoint")
async def calculate_flippoint(request: dict):
    """
    Calculate FlipPoint threshold where preferred rotation changes
    
    Tests rotation preference across a range of irrigation capacity values
    to find the threshold where the optimal choice switches.
    
    Body: {
        "farm_id": 1,
        "latitude": 40.0,
        "longitude": -95.0,
        "year": 2023,
        "rotations": {
            "current": [...],
            "small_shift": [...],
            "alternative": [...]
        },
        "parameter": "irrigation_capacity",
        "current_value": 10.5,  // Current mm/week
        "min_value": 0,
        "max_value": 100,
        "steps": 20
    }
    """
    from services.nasa_power import nasa_power_service
    from datetime import date
    import numpy as np
    
    farm_id = request.get("farm_id")
    latitude = request.get("latitude")
    longitude = request.get("longitude")
    year = request.get("year", 2023)
    rotations_config = request.get("rotations", {})
    parameter = request.get("parameter", "irrigation_capacity")
    current_value = request.get("current_value", 0)
    min_value = request.get("min_value", 0)
    max_value = request.get("max_value", 100)
    steps = request.get("steps", 20)
    
    if not latitude or not longitude:
        raise HTTPException(status_code=400, detail="Farm coordinates required")
    
    if parameter != "irrigation_capacity":
        return {
            "success": False,
            "error": "Only irrigation_capacity parameter supported currently",
            "parameter": parameter
        }
    
    if not rotations_config or len(rotations_config) < 2:
        return {
            "success": False,
            "error": "At least 2 rotations required for FlipPoint analysis",
            "rotations_provided": len(rotations_config)
        }
    
    # Generate test values
    test_values = np.linspace(min_value, max_value, steps)
    
    # For each test value, compare rotations
    data_points = []
    rotation_types = list(rotations_config.keys())
    
    for test_mm_week in test_values:
        # Calculate water stress for each rotation at this irrigation level
        stress_scores = {}
        
        for rot_type in rotation_types:
            crops = rotations_config[rot_type]
            
            if not crops:
                stress_scores[rot_type] = 999  # Very high penalty for empty rotation
                continue
            
            # Calculate water needs
            calc_request = {
                "farm_id": farm_id,
                "latitude": latitude,
                "longitude": longitude,
                "year": year,
                "crops": crops
            }
            
            try:
                result = await calculate_water_needs(calc_request)
                
                # Calculate stress based on irrigation deficit
                total_irrigation_need = result.get("total_irrigation_need_mm", 0)
                
                # Weekly irrigation available (mm/week)
                weekly_irrigation_available = test_mm_week * 7 / 7  # Already in mm/week
                
                # Seasonal irrigation available (roughly 26 weeks growing season)
                seasonal_irrigation_available = weekly_irrigation_available * 26
                
                # Calculate unmet irrigation need
                unmet_need = max(0, total_irrigation_need - seasonal_irrigation_available)
                
                # Stress score = base stress days + penalty for unmet irrigation
                base_stress = result.get("total_stress_days", 0)
                irrigation_deficit_penalty = unmet_need / 10  # 10mm deficit = 1 stress day equivalent
                
                stress_scores[rot_type] = base_stress + irrigation_deficit_penalty
                
            except Exception as e:
                print(f"Error calculating {rot_type} at {test_mm_week}: {e}")
                stress_scores[rot_type] = 999
        
        # Find preferred rotation (lowest stress)
        if stress_scores:
            preferred_rot = min(stress_scores.items(), key=lambda x: x[1])[0]
        else:
            preferred_rot = rotation_types[0] if rotation_types else "unknown"
        
        data_points.append({
            "irrigation_mm_week": round(float(test_mm_week), 2),
            "preferred_rotation": preferred_rot,
            "stress_scores": {k: round(float(v), 1) for k, v in stress_scores.items()}
        })
    
    # Detect FlipPoint threshold
    flip_threshold = None
    flip_from = None
    flip_to = None
    
    if len(data_points) >= 2:
        for i in range(1, len(data_points)):
            if data_points[i]["preferred_rotation"] != data_points[i-1]["preferred_rotation"]:
                # FlipPoint detected between i-1 and i
                flip_threshold = (data_points[i-1]["irrigation_mm_week"] + data_points[i]["irrigation_mm_week"]) / 2
                flip_from = data_points[i-1]["preferred_rotation"]
                flip_to = data_points[i]["preferred_rotation"]
                break
    
    # Find current preferred rotation
    current_preferred = None
    for dp in data_points:
        if abs(dp["irrigation_mm_week"] - current_value) < (max_value - min_value) / (steps * 2):
            current_preferred = dp["preferred_rotation"]
            break
    
    if not current_preferred and data_points:
        # Fallback: find closest
        current_preferred = min(data_points, key=lambda x: abs(x["irrigation_mm_week"] - current_value))["preferred_rotation"]
    
    return {
        "success": True,
        "farm_id": farm_id,
        "latitude": latitude,
        "longitude": longitude,
        "parameter": "irrigation_capacity",
        "current_value_mm_week": round(current_value, 2),
        "current_preferred_rotation": current_preferred,
        "flippoint_threshold_mm_week": round(flip_threshold, 2) if flip_threshold else None,
        "flippoint_from": flip_from,
        "flippoint_to": flip_to,
        "has_flippoint": flip_threshold is not None,
        "data_points": data_points,
        "rotations_analyzed": len(rotation_types),
        "test_range": {
            "min_mm_week": round(float(min_value), 2),
            "max_mm_week": round(float(max_value), 2),
            "steps": steps
        },
        "explanation": f"Analyzed {len(rotation_types)} rotations across {steps} irrigation capacity values from {min_value} to {max_value} mm/week."
    }
