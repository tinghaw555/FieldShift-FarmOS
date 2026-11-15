"""
Ground Truth API Router - Forecast vs Reality comparison
"""

from fastapi import APIRouter
from datetime import datetime
import aiosqlite

from models.schemas import ForecastErrorMetrics, GroundTruthComparison
from database.db import DB_PATH

router = APIRouter()

@router.get("/metrics/{farm_id}", response_model=ForecastErrorMetrics)
async def get_forecast_metrics(farm_id: int, days: int = 30):
    """
    Calculate forecast error metrics comparing forecasts to observations
    
    NOTE: In current implementation, observations are simulated
    Real validation requires actual ESP32 hardware integration
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Get forecast snapshots and matching sensor readings
        async with db.execute(
            """SELECT 
                   fs.temperature as forecast_temp,
                   sr.value as observed_temp,
                   fs.valid_time
               FROM forecast_snapshots fs
               LEFT JOIN sensor_readings sr ON 
                   sr.farm_id = fs.farm_id AND
                   sr.sensor_type = 'temperature' AND
                   DATE(sr.timestamp) = DATE(fs.valid_time)
               WHERE fs.farm_id = ?
               AND fs.created_at >= datetime('now', '-' || ? || ' days')
               ORDER BY fs.valid_time""",
            (farm_id, days)
        ) as cursor:
            rows = await cursor.fetchall()
        
        if not rows:
            return ForecastErrorMetrics(
                temperature_mae=None,
                temperature_bias=None,
                observation_count=0
            )
        
        # Calculate metrics
        errors = []
        for row in rows:
            if row['forecast_temp'] is not None and row['observed_temp'] is not None:
                error = abs(row['forecast_temp'] - row['observed_temp'])
                errors.append(error)
        
        if errors:
            mae = sum(errors) / len(errors)
        else:
            mae = None
        
        return ForecastErrorMetrics(
            temperature_mae=mae,
            temperature_bias=None,  # Would calculate if we had paired data
            observation_count=len(errors),
            forecast_source="Open-Meteo"
        )

@router.get("/comparison/{farm_id}")
async def get_ground_truth_comparison(farm_id: int, days: int = 7):
    """
    Get detailed forecast vs observation comparison
    """
    # Would return detailed comparison data
    return {
        "farm_id": farm_id,
        "note": "Ground Truth comparison framework - awaiting real sensor data",
        "status": "simulated",
        "warning": "Current observations are SOFTWARE SIMULATED, not real sensor measurements"
    }
