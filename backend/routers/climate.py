"""
Climate API Router - NASA POWER data integration
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, date
import json
import aiosqlite

from models.schemas import ClimateRequest, ClimateResponse, ClimateDataPoint
from services.nasa_power import nasa_power_service, NASAPowerError
from database.db import DB_PATH

router = APIRouter()

@router.post("/", response_model=ClimateResponse)
async def get_climate_data(request: ClimateRequest):
    """
    Get historical climate data from NASA POWER
    
    Caches results to reduce API calls
    """
    # Parse dates
    try:
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Check cache first
    cached_data = await check_cache(
        request.latitude,
        request.longitude,
        request.start_date,
        request.end_date
    )
    
    if cached_data:
        return cached_data
    
    # Fetch from NASA POWER
    try:
        daily_data = await nasa_power_service.get_climate_data(
            latitude=request.latitude,
            longitude=request.longitude,
            start_date=start_date,
            end_date=end_date
        )
        
        # Convert to response format
        data_points = [
            ClimateDataPoint(
                date=record["date"],
                temperature_mean=record.get("temperature_mean"),
                temperature_max=record.get("temperature_max"),
                temperature_min=record.get("temperature_min"),
                precipitation=record.get("precipitation"),
                humidity=record.get("humidity"),
                wind_speed=record.get("wind_speed"),
                solar_radiation=record.get("solar_radiation")
            )
            for record in daily_data
        ]
        
        response = ClimateResponse(
            source="NASA POWER",
            latitude=request.latitude,
            longitude=request.longitude,
            data=data_points,
            cached=False
        )
        
        # Cache the result
        await cache_climate_data(
            request.latitude,
            request.longitude,
            request.start_date,
            request.end_date,
            response
        )
        
        return response
        
    except NASAPowerError as e:
        raise HTTPException(status_code=502, detail=f"NASA POWER API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/summary/{latitude}/{longitude}")
async def get_climate_summary(latitude: float, longitude: float, year: int = None):
    """
    Get climate summary statistics for a location
    
    If year is not provided, uses most recent complete year
    """
    if year is None:
        year = datetime.now().year - 1
    
    request = ClimateRequest(
        latitude=latitude,
        longitude=longitude,
        start_date=f"{year}-01-01",
        end_date=f"{year}-12-31"
    )
    
    climate_data = await get_climate_data(request)
    
    # Calculate summary statistics
    temps = [d.temperature_mean for d in climate_data.data if d.temperature_mean is not None]
    precips = [d.precipitation for d in climate_data.data if d.precipitation is not None]
    
    summary = {
        "year": year,
        "latitude": latitude,
        "longitude": longitude,
        "temperature": {
            "mean_annual": sum(temps) / len(temps) if temps else None,
            "max": max(temps) if temps else None,
            "min": min(temps) if temps else None
        },
        "precipitation": {
            "total_annual": sum(precips) if precips else None,
            "mean_daily": sum(precips) / len(precips) if precips else None,
            "days_with_rain": sum(1 for p in precips if p > 1.0)
        },
        "data_points": len(climate_data.data)
    }
    
    return summary

# ============================================================================
# CACHE HELPERS
# ============================================================================

async def check_cache(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str
) -> ClimateResponse | None:
    """Check if climate data is cached"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Look for exact match within tolerance
        async with db.execute(
            """SELECT data, cached_at FROM climate_cache
               WHERE ABS(latitude - ?) < 0.1
               AND ABS(longitude - ?) < 0.1
               AND start_date = ?
               AND end_date = ?
               AND source = 'NASA POWER'
               ORDER BY cached_at DESC
               LIMIT 1""",
            (latitude, longitude, start_date, end_date)
        ) as cursor:
            row = await cursor.fetchone()
            
            if row:
                # Parse cached data
                cached_json = json.loads(row[0])
                cached_json['cached'] = True
                return ClimateResponse(**cached_json)
    
    return None

async def cache_climate_data(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    response: ClimateResponse
):
    """Cache climate data for future use"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Convert response to JSON
        data_json = response.model_dump_json()
        
        await db.execute(
            """INSERT INTO climate_cache 
               (latitude, longitude, start_date, end_date, source, data)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (latitude, longitude, start_date, end_date, "NASA POWER", data_json)
        )
        await db.commit()
