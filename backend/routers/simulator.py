"""
Sensor Simulator API Router - Software simulation of farm sensors

NOTE: This is SOFTWARE SIMULATION for demonstration purposes.
Real hardware uses NodeMCU V3 (ESP8266) with DHT11, soil moisture, and water level sensors.
See hardware/ directory for actual firmware.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import random
import aiosqlite

from models.schemas import (
    SimulatorState, SensorReading, IrrigationRecommendation,
    IrrigationCommand, IrrigationExperiment
)
from database.db import DB_PATH

router = APIRouter()

# In-memory simulator state (would use Redis/database in production)
simulator_states = {}

@router.get("/state/{farm_id}", response_model=SimulatorState)
async def get_simulator_state(farm_id: int):
    """Get current simulator state for a farm"""
    
    if farm_id not in simulator_states:
        # Initialize with random but realistic values
        simulator_states[farm_id] = {
            "air_temperature": 22.0 + random.uniform(-5, 5),
            "air_humidity": 60.0 + random.uniform(-10, 10),
            "soil_moisture": 65.0 + random.uniform(-15, 15),
            "water_level": 75.0 + random.uniform(-20, 20),
            "valve_open": False,
            "connected": True,
            "last_update": datetime.now()
        }
    
    state = simulator_states[farm_id]
    
    return SimulatorState(
        farm_id=farm_id,
        air_temperature=state["air_temperature"],
        air_humidity=state["air_humidity"],
        soil_moisture=max(0, min(100, state["soil_moisture"])),
        water_level=max(0, min(100, state["water_level"])),
        valve_open=state["valve_open"],
        connected=state["connected"],
        last_update=state["last_update"]
    )

@router.post("/state/{farm_id}")
async def update_simulator_state(farm_id: int, updates: dict):
    """Update simulator state (for testing/demonstration)"""
    
    if farm_id not in simulator_states:
        simulator_states[farm_id] = {
            "air_temperature": 22.0,
            "air_humidity": 60.0,
            "soil_moisture": 65.0,
            "water_level": 75.0,
            "valve_open": False,
            "connected": True,
            "last_update": datetime.now()
        }
    
    # Update provided values
    for key in ["air_temperature", "air_humidity", "soil_moisture", "water_level", "connected"]:
        if key in updates:
            simulator_states[farm_id][key] = updates[key]
    
    simulator_states[farm_id]["last_update"] = datetime.now()
    
    # Save sensor reading
    await save_sensor_reading(farm_id, simulator_states[farm_id])
    
    return await get_simulator_state(farm_id)

@router.get("/recommendation/{farm_id}", response_model=IrrigationRecommendation)
async def get_irrigation_recommendation(farm_id: int):
    """
    Get smart irrigation recommendation based on sensor state and weather
    """
    state = await get_simulator_state(farm_id)
    
    # Simple rule-based recommendation logic
    if not state.connected:
        return IrrigationRecommendation(
            action="sensor_error",
            reason="Simulator not connected",
            urgency="high"
        )
    
    if state.water_level < 20:
        return IrrigationRecommendation(
            action="insufficient_water",
            reason=f"Water reservoir low ({state.water_level:.0f}%)",
            urgency="high"
        )
    
    if state.soil_moisture < 30:
        return IrrigationRecommendation(
            action="water",
            reason=f"Soil moisture low ({state.soil_moisture:.0f}%)",
            urgency="high",
            suggested_duration=300  # 5 minutes
        )
    
    if state.soil_moisture < 50:
        return IrrigationRecommendation(
            action="review",
            reason=f"Soil moisture moderate ({state.soil_moisture:.0f}%)",
            urgency="medium",
            suggested_duration=180  # 3 minutes
        )
    
    return IrrigationRecommendation(
        action="wait",
        reason=f"Soil moisture adequate ({state.soil_moisture:.0f}%)",
        urgency="low"
    )

@router.post("/irrigate/{farm_id}")
async def control_irrigation(farm_id: int, command: IrrigationCommand):
    """
    Control simulated irrigation valve
    
    IMPORTANT: This is SOFTWARE SIMULATION ONLY
    No actual hardware is controlled
    """
    state = await get_simulator_state(farm_id)
    
    # Safety checks
    if not command.farmer_approved:
        raise HTTPException(status_code=403, detail="Farmer approval required")
    
    if command.action == "open":
        if state.water_level < 20:
            raise HTTPException(status_code=400, detail="Insufficient water in reservoir")
        
        # Simulate opening valve
        simulator_states[farm_id]["valve_open"] = True
        
        # Record experiment start
        experiment_id = await start_irrigation_experiment(farm_id, command.duration_seconds)
        
        return {
            "status": "valve_opened",
            "message": "SIMULATED: Irrigation valve opened",
            "experiment_id": experiment_id,
            "duration_seconds": command.duration_seconds,
            "warning": "This is software simulation - no real hardware affected"
        }
    
    elif command.action == "close":
        simulator_states[farm_id]["valve_open"] = False
        
        return {
            "status": "valve_closed",
            "message": "SIMULATED: Irrigation valve closed",
            "warning": "This is software simulation - no real hardware affected"
        }

@router.get("/experiments/{farm_id}")
async def list_experiments(farm_id: int, limit: int = 20):
    """List recent irrigation experiments"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM irrigation_experiments 
               WHERE farm_id = ? 
               ORDER BY created_at DESC 
               LIMIT ?""",
            (farm_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def save_sensor_reading(farm_id: int, state: dict):
    """Save sensor reading to database"""
    async with aiosqlite.connect(DB_PATH) as db:
        timestamp = datetime.now()
        
        # Save each sensor type
        for sensor_type, value, unit in [
            ("temperature", state["air_temperature"], "°C"),
            ("humidity", state["air_humidity"], "%"),
            ("soil_moisture", state["soil_moisture"], "%"),
            ("water_level", state["water_level"], "%")
        ]:
            await db.execute(
                """INSERT INTO sensor_readings 
                   (farm_id, timestamp, sensor_type, value, unit, is_simulated)
                   VALUES (?, ?, ?, ?, ?, 1)""",
                (farm_id, timestamp, sensor_type, value, unit)
            )
        
        await db.commit()

async def start_irrigation_experiment(farm_id: int, duration_seconds: int):
    """Start a new irrigation experiment"""
    state = simulator_states.get(farm_id, {})
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO irrigation_experiments
               (farm_id, start_time, initial_soil_moisture, initial_water_level,
                temperature, humidity, farmer_approved, valve_opened, duration_seconds)
               VALUES (?, ?, ?, ?, ?, ?, 1, 1, ?)""",
            (
                farm_id,
                datetime.now(),
                state.get("soil_moisture"),
                state.get("water_level"),
                state.get("air_temperature"),
                state.get("air_humidity"),
                duration_seconds
            )
        )
        await db.commit()
        return cursor.lastrowid
