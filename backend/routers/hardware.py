"""
Hardware Telemetry API Router - Real NodeMCU V3 (ESP8266) sensor data ingestion
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from datetime import datetime, timedelta
from typing import Optional
import aiosqlite
import hashlib
import secrets
import uuid

from models.schemas import HardwareTelemetry, DeviceStatus, PumpCommandRequest, PumpCommand, PumpCommandAcknowledge, PumpState, PumpStatus
from database.db import DB_PATH

router = APIRouter()

# ============================================================================
# NODEMCU V3 (ESP8266) TELEMETRY INGESTION
# ============================================================================

@router.post("/telemetry")
async def ingest_telemetry(
    telemetry: HardwareTelemetry,
    x_device_id: str = Header(...),
    x_api_key: str = Header(...)
):
    """
    Receive sensor telemetry from NodeMCU V3 (ESP8266)
    
    Hardware: LOLIN NodeMCU V3 (ESP8266 ESP-12E/ESP-12F)
    Sensors: DHT11, Analog Soil Moisture, Digital Water Level
    Motor Driver: TB6612FNG
    
    Required headers:
    - X-Device-ID: Unique device identifier
    - X-API-Key: Authentication key for the device
    
    Body (JSON):
    {
        "farm_id": 1,
        "timestamp": "2023-10-15T10:30:00Z",
        "temperature": 22.5,
        "humidity": 65.0,
        "soil_moisture": 450,
        "water_level": 100,
        "firmware_version": "1.0.0",
        "ip_address": "192.168.1.100"
    }
    """
    # Authenticate device
    device = await authenticate_device(x_device_id, x_api_key)
    if not device:
        raise HTTPException(status_code=401, detail="Invalid device credentials")
    
    # Validate telemetry data
    validation_errors = validate_telemetry(telemetry)
    if validation_errors:
        raise HTTPException(status_code=400, detail=f"Invalid telemetry: {', '.join(validation_errors)}")
    
    # Store telemetry
    async with aiosqlite.connect(DB_PATH) as db:
        timestamp = datetime.fromisoformat(telemetry.timestamp.replace('Z', '+00:00'))
        
        # Save each sensor reading
        for sensor_type, value, unit in [
            ("temperature", telemetry.temperature, "°C"),
            ("humidity", telemetry.humidity, "%"),
            ("soil_moisture", telemetry.soil_moisture, "%"),
            ("water_level", telemetry.water_level, "%")
        ]:
            if value is not None:
                await db.execute(
                    """INSERT INTO sensor_readings 
                       (farm_id, timestamp, sensor_type, value, unit, is_simulated, device_id, is_valid)
                       VALUES (?, ?, ?, ?, ?, 0, ?, 1)""",
                    (telemetry.farm_id, timestamp, sensor_type, value, unit, x_device_id)
                )
        
        # Update device last_seen
        await db.execute(
            """UPDATE hardware_devices 
               SET last_seen = ?, status = 'online', firmware_version = ?, ip_address = ?
               WHERE device_id = ?""",
            (datetime.now(), telemetry.firmware_version, telemetry.ip_address, x_device_id)
        )
        
        await db.commit()
    
    return {
        "status": "accepted",
        "device_id": x_device_id,
        "timestamp": telemetry.timestamp,
        "message": "Telemetry stored successfully"
    }

@router.get("/device/{device_id}/status", response_model=DeviceStatus)
async def get_device_status(device_id: str):
    """Get current status of a hardware device"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM hardware_devices WHERE device_id = ?",
            (device_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Device not found")
            
            device = dict(row)
            
            # Determine connection status
            if device['last_seen']:
                last_seen = datetime.fromisoformat(device['last_seen'])
                minutes_ago = (datetime.now() - last_seen).total_seconds() / 60
                
                if minutes_ago < 5:
                    status = "online"
                elif minutes_ago < 30:
                    status = "stale"
                else:
                    status = "offline"
            else:
                status = "offline"
            
            return DeviceStatus(
                device_id=device['device_id'],
                device_type=device['device_type'],
                farm_id=device['farm_id'],
                status=status,
                last_seen=device['last_seen'],
                firmware_version=device['firmware_version'],
                ip_address=device['ip_address']
            )

@router.get("/farm/{farm_id}/devices")
async def list_farm_devices(farm_id: int):
    """List all devices registered to a farm"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT device_id, device_type, status, last_seen, firmware_version FROM hardware_devices WHERE farm_id = ?",
            (farm_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            devices = []
            
            for row in rows:
                device = dict(row)
                # Update status based on last_seen
                if device['last_seen']:
                    last_seen = datetime.fromisoformat(device['last_seen'])
                    minutes_ago = (datetime.now() - last_seen).total_seconds() / 60
                    
                    if minutes_ago < 5:
                        device['status'] = "online"
                    elif minutes_ago < 30:
                        device['status'] = "stale"
                    else:
                        device['status'] = "offline"
                else:
                    device['status'] = "offline"
                
                devices.append(device)
            
            return devices

@router.get("/farm/{farm_id}/latest")
async def get_latest_readings(farm_id: int, device_id: Optional[str] = None):
    """
    Get latest sensor readings - prioritizes real hardware, falls back to CSV demo data
    
    Returns:
    - Real hardware readings (is_simulated = 0) if available within last 10 minutes
    - CSV demonstration readings (is_simulated = 1) if no real hardware
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cutoff_time = datetime.now() - timedelta(minutes=10)
        
        # Try to get real hardware readings first
        query_real = """
            SELECT sensor_type, value, unit, timestamp, device_id, is_simulated
            FROM sensor_readings
            WHERE farm_id = ? AND is_simulated = 0 AND timestamp > ?
        """
        params_real = [farm_id, cutoff_time]
        
        if device_id:
            query_real += " AND device_id = ?"
            params_real.append(device_id)
        
        query_real += " ORDER BY timestamp DESC"
        
        async with db.execute(query_real, params_real) as cursor:
            rows = await cursor.fetchall()
            
            if rows:
                # Real hardware data found
                readings = {}
                for row in rows:
                    sensor_type = row['sensor_type']
                    if sensor_type not in readings:
                        readings[sensor_type] = {
                            "value": row['value'],
                            "unit": row['unit'],
                            "timestamp": row['timestamp'],
                            "device_id": row['device_id']
                        }
                
                latest_timestamp = max(
                    datetime.fromisoformat(r['timestamp']) 
                    for r in readings.values()
                )
                minutes_old = (datetime.now() - latest_timestamp).total_seconds() / 60
                
                return {
                    "status": "stale" if minutes_old > 5 else "current",
                    "data_source": "hardware",
                    "is_simulated": False,
                    "readings": readings,
                    "latest_timestamp": latest_timestamp.isoformat(),
                    "minutes_old": round(minutes_old, 1)
                }
        
        # No real hardware - try CSV demonstration data
        query_csv = """
            SELECT sensor_type, value, unit, timestamp, device_id, is_simulated
            FROM sensor_readings
            WHERE farm_id = ? AND is_simulated = 1
            ORDER BY timestamp DESC
            LIMIT 1000
        """
        
        async with db.execute(query_csv, [farm_id]) as cursor:
            rows = await cursor.fetchall()
            
            if rows:
                # Group by timestamp to get complete sensor sets
                readings_by_time = {}
                for row in rows:
                    ts = row['timestamp']
                    if ts not in readings_by_time:
                        readings_by_time[ts] = {}
                    
                    sensor_type = row['sensor_type']
                    readings_by_time[ts][sensor_type] = {
                        "value": row['value'],
                        "unit": row['unit'],
                        "timestamp": row['timestamp'],
                        "device_id": row['device_id']
                    }
                
                # Get the most recent complete set
                sorted_times = sorted(readings_by_time.keys(), reverse=True)
                latest_time = sorted_times[0]
                readings = readings_by_time[latest_time]
                
                return {
                    "status": "csv_demo",
                    "data_source": "csv_demonstration",
                    "is_simulated": True,
                    "readings": readings,
                    "latest_timestamp": latest_time,
                    "total_csv_readings": len(sorted_times),
                    "message": "Displaying demonstration data from CSV import"
                }
        
        # No data at all
        return {
            "status": "no_data",
            "data_source": "none",
            "message": "No sensor readings available (hardware or CSV)",
            "readings": {}
        }

@router.get("/farm/{farm_id}/csv-readings")
async def get_csv_readings_sequence(farm_id: int, limit: int = 120):
    """
    Get CSV demonstration readings for Smart Farm preview mode
    
    Priority:
    1. Farm-specific readings (if farm has its own imported data)
    2. Shared demonstration readings from farm_id=1 (fallback for farms without data)
    3. No data available
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Try to get farm-specific readings first
        query = """
            SELECT DISTINCT timestamp
            FROM sensor_readings
            WHERE farm_id = ? AND is_simulated = 1
            ORDER BY timestamp ASC
            LIMIT ?
        """
        
        async with db.execute(query, [farm_id, limit]) as cursor:
            timestamps = [row['timestamp'] for row in await cursor.fetchall()]
        
        if timestamps:
            # Farm has its own readings
            readings_sequence = []
            
            for ts in timestamps:
                query_readings = """
                    SELECT sensor_type, value, unit, timestamp, device_id
                    FROM sensor_readings
                    WHERE farm_id = ? AND is_simulated = 1 AND timestamp = ?
                """
                
                async with db.execute(query_readings, [farm_id, ts]) as cursor:
                    rows = await cursor.fetchall()
                    
                    reading_set = {
                        "timestamp": ts,
                        "sensors": {}
                    }
                    
                    for row in rows:
                        reading_set["sensors"][row['sensor_type']] = {
                            "value": row['value'],
                            "unit": row['unit']
                        }
                    
                    readings_sequence.append(reading_set)
            
            return {
                "status": "success",
                "data_source": "farm_specific",
                "is_simulated": True,
                "farm_id": farm_id,
                "total_readings": len(readings_sequence),
                "readings": readings_sequence
            }
        
        # No farm-specific readings - try shared demonstration data from farm_id=1
        query_demo = """
            SELECT DISTINCT timestamp
            FROM sensor_readings
            WHERE farm_id = 1 AND is_simulated = 1
            ORDER BY timestamp ASC
            LIMIT ?
        """
        
        async with db.execute(query_demo, [limit]) as cursor:
            demo_timestamps = [row['timestamp'] for row in await cursor.fetchall()]
        
        if demo_timestamps:
            # Use shared demonstration data
            readings_sequence = []
            
            for ts in demo_timestamps:
                query_readings = """
                    SELECT sensor_type, value, unit, timestamp, device_id
                    FROM sensor_readings
                    WHERE farm_id = 1 AND is_simulated = 1 AND timestamp = ?
                """
                
                async with db.execute(query_readings, [ts]) as cursor:
                    rows = await cursor.fetchall()
                    
                    reading_set = {
                        "timestamp": ts,
                        "sensors": {}
                    }
                    
                    for row in rows:
                        reading_set["sensors"][row['sensor_type']] = {
                            "value": row['value'],
                            "unit": row['unit']
                        }
                    
                    readings_sequence.append(reading_set)
            
            return {
                "status": "success",
                "data_source": "shared_demonstration",
                "is_simulated": True,
                "farm_id": farm_id,
                "source_farm_id": 1,
                "total_readings": len(readings_sequence),
                "readings": readings_sequence,
                "note": "Example readings from shared demonstration dataset"
            }
        
        # No data available at all
        return {
            "status": "no_data",
            "message": "No demonstration data available",
            "farm_id": farm_id,
            "readings": []
        }

# ============================================================================
# DEVICE REGISTRATION & MANAGEMENT
# ============================================================================

@router.post("/register")
async def register_device(device_info: dict):
    """
    Register a new NodeMCU V3 (ESP8266) device
    
    Body:
    {
        "device_id": "NODEMCU_FARM001",
        "farm_id": 1,
        "device_type": "NodeMCU-V3-ESP8266"
    }
    
    Returns API key for authentication
    """
    device_id = device_info.get("device_id")
    farm_id = device_info.get("farm_id")
    device_type = device_info.get("device_type", "NodeMCU-V3-ESP8266")
    
    if not device_id or not farm_id:
        raise HTTPException(status_code=400, detail="device_id and farm_id required")
    
    # Generate API key
    api_key = secrets.token_urlsafe(32)
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Check if device already exists
        async with db.execute(
            "SELECT device_id FROM hardware_devices WHERE device_id = ?",
            (device_id,)
        ) as cursor:
            existing = await cursor.fetchone()
            if existing:
                raise HTTPException(status_code=409, detail="Device already registered")
        
        # Register device
        await db.execute(
            """INSERT INTO hardware_devices 
               (device_id, device_type, farm_id, api_key, status)
               VALUES (?, ?, ?, ?, 'offline')""",
            (device_id, device_type, farm_id, api_key_hash)
        )
        await db.commit()
    
    return {
        "device_id": device_id,
        "api_key": api_key,
        "message": "Device registered successfully. Save the API key securely - it cannot be retrieved later.",
        "endpoint": "/api/hardware/telemetry",
        "headers_required": ["X-Device-ID", "X-API-Key"]
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def authenticate_device(device_id: str, api_key: str) -> Optional[dict]:
    """Authenticate device using API key"""
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM hardware_devices WHERE device_id = ? AND api_key = ?",
            (device_id, api_key_hash)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

def validate_telemetry(telemetry: HardwareTelemetry) -> list:
    """Validate telemetry data ranges"""
    errors = []
    
    if telemetry.temperature is not None:
        if not -40 <= telemetry.temperature <= 80:
            errors.append("Temperature out of valid range (-40 to 80°C)")
    
    if telemetry.humidity is not None:
        if not 0 <= telemetry.humidity <= 100:
            errors.append("Humidity out of valid range (0-100%)")
    
    if telemetry.soil_moisture is not None:
        if not 0 <= telemetry.soil_moisture <= 100:
            errors.append("Soil moisture out of valid range (0-100%)")
    
    if telemetry.water_level is not None:
        if not 0 <= telemetry.water_level <= 100:
            errors.append("Water level out of valid range (0-100%)")
    
    return errors


# ============================================================================
# PUMP CONTROL ENDPOINTS
# ============================================================================

@router.post("/pump/command")
async def create_pump_command(command_req: PumpCommandRequest):
    """
    Create a pump control command (dashboard → backend)
    
    Command will be queued for NodeMCU to poll and execute.
    SAFETY: Commands expire after 60 seconds if not acknowledged.
    """
    # Validate device exists and is online
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Check device
        async with db.execute(
            "SELECT * FROM hardware_devices WHERE device_id = ? AND farm_id = ?",
            (command_req.device_id, command_req.farm_id)
        ) as cursor:
            device = await cursor.fetchone()
            if not device:
                raise HTTPException(status_code=404, detail="Device not found")
        
        # Check device is online (last_seen within 2 minutes)
        device_dict = dict(device)
        if device_dict['last_seen']:
            last_seen = datetime.fromisoformat(device_dict['last_seen'])
            minutes_ago = (datetime.now() - last_seen).total_seconds() / 60
            if minutes_ago > 2:
                raise HTTPException(
                    status_code=503, 
                    detail=f"Device offline (last seen {int(minutes_ago)} minutes ago)"
                )
        else:
            raise HTTPException(status_code=503, detail="Device has never connected")
        
        # Generate unique command ID
        command_id = str(uuid.uuid4())
        requested_at = datetime.now()
        expires_at = requested_at + timedelta(seconds=60)  # 60 second expiry
        
        # Insert command
        await db.execute(
            """INSERT INTO pump_commands 
               (command_id, device_id, farm_id, action, duration_seconds, 
                requested_at, expires_at, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')""",
            (command_id, command_req.device_id, command_req.farm_id, 
             command_req.action, command_req.duration_seconds,
             requested_at, expires_at)
        )
        
        await db.commit()
        
        return {
            "command_id": command_id,
            "status": "pending",
            "message": f"Pump {command_req.action} command queued",
            "expires_at": expires_at.isoformat()
        }

@router.get("/pump/commands/{device_id}/pending")
async def get_pending_commands(
    device_id: str,
    x_api_key: str = Header(...)
):
    """
    Get pending commands for NodeMCU to execute (NodeMCU → backend poll)
    
    Returns the oldest pending, non-expired command.
    NodeMCU polls this endpoint every few seconds.
    """
    # Authenticate device
    device = await authenticate_device(device_id, x_api_key)
    if not device:
        raise HTTPException(status_code=401, detail="Invalid device credentials")
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Mark expired commands
        await db.execute(
            """UPDATE pump_commands 
               SET status = 'expired'
               WHERE device_id = ? AND status = 'pending' AND expires_at < ?""",
            (device_id, datetime.now())
        )
        await db.commit()
        
        # Get oldest pending command
        async with db.execute(
            """SELECT * FROM pump_commands 
               WHERE device_id = ? AND status = 'pending' 
               ORDER BY requested_at ASC LIMIT 1""",
            (device_id,)
        ) as cursor:
            row = await cursor.fetchone()
            
            if not row:
                return {"command": None}
            
            command = dict(row)
            return {
                "command": {
                    "command_id": command['command_id'],
                    "action": command['action'],
                    "duration_seconds": command['duration_seconds'],
                    "expires_at": command['expires_at']
                }
            }

@router.post("/pump/commands/acknowledge")
async def acknowledge_pump_command(
    ack: PumpCommandAcknowledge,
    x_device_id: str = Header(...),
    x_api_key: str = Header(...)
):
    """
    NodeMCU acknowledges command execution status (NodeMCU → backend)
    
    Status can be:
    - acknowledged: Command received, executing
    - completed: Command executed successfully
    - failed: Command failed (with error_message)
    """
    # Authenticate device
    device = await authenticate_device(x_device_id, x_api_key)
    if not device:
        raise HTTPException(status_code=401, detail="Invalid device credentials")
    
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now()
        
        # Update command status
        if ack.status == 'acknowledged':
            await db.execute(
                """UPDATE pump_commands 
                   SET status = 'acknowledged', acknowledged_at = ?
                   WHERE command_id = ?""",
                (now, ack.command_id)
            )
        elif ack.status == 'completed':
            await db.execute(
                """UPDATE pump_commands 
                   SET status = 'completed', completed_at = ?, result = ?
                   WHERE command_id = ?""",
                (now, ack.result, ack.command_id)
            )
        elif ack.status == 'failed':
            await db.execute(
                """UPDATE pump_commands 
                   SET status = 'failed', completed_at = ?, error_message = ?
                   WHERE command_id = ?""",
                (now, ack.error_message, ack.command_id)
            )
        
        await db.commit()
        
        return {
            "status": "accepted",
            "command_id": ack.command_id,
            "acknowledgement": ack.status
        }

@router.post("/pump/state")
async def report_pump_state(
    state: PumpState,
    x_device_id: str = Header(...),
    x_api_key: str = Header(...)
):
    """
    NodeMCU reports current pump state (NodeMCU → backend)
    
    Sent with each telemetry update or when pump state changes.
    """
    # Authenticate device
    device = await authenticate_device(x_device_id, x_api_key)
    if not device:
        raise HTTPException(status_code=401, detail="Invalid device credentials")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Store pump state snapshot
        # In production, you might want to only store state changes to save space
        await db.execute(
            """INSERT INTO pump_states 
               (device_id, farm_id, state, started_at, command_id, fault_reason)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                state.device_id,
                device['farm_id'],
                'on' if state.pump_running else 'off',
                datetime.now(),
                state.current_command_id,
                state.fault_reason if state.fault_detected else None
            )
        )
        
        await db.commit()
        
        return {"status": "accepted"}

@router.get("/pump/status/{device_id}", response_model=PumpStatus)
async def get_pump_status(device_id: str):
    """
    Get current pump status for dashboard (dashboard → backend)
    
    Returns device connection status, pump state, and last command.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Get device
        async with db.execute(
            "SELECT * FROM hardware_devices WHERE device_id = ?",
            (device_id,)
        ) as cursor:
            device = await cursor.fetchone()
            if not device:
                raise HTTPException(status_code=404, detail="Device not found")
            
            device_dict = dict(device)
        
        # Determine device connection status
        if device_dict['last_seen']:
            last_seen = datetime.fromisoformat(device_dict['last_seen'])
            minutes_ago = (datetime.now() - last_seen).total_seconds() / 60
            
            if minutes_ago < 2:
                device_status = "online"
            elif minutes_ago < 10:
                device_status = "stale"
            else:
                device_status = "offline"
        else:
            device_status = "offline"
        
        # Get latest pump state
        async with db.execute(
            """SELECT * FROM pump_states 
               WHERE device_id = ? 
               ORDER BY started_at DESC LIMIT 1""",
            (device_id,)
        ) as cursor:
            state_row = await cursor.fetchone()
            state_dict = dict(state_row) if state_row else None
        
        # Get last command
        async with db.execute(
            """SELECT * FROM pump_commands 
               WHERE device_id = ? 
               ORDER BY requested_at DESC LIMIT 1""",
            (device_id,)
        ) as cursor:
            cmd_row = await cursor.fetchone()
            last_command = dict(cmd_row) if cmd_row else None
        
        # Determine pump state
        if device_status == "offline":
            pump_state = "unknown"
            commissioned = False
            fault_reason = "Device offline"
            water_level_ok = False
        elif not state_dict:
            pump_state = "unknown"
            commissioned = False
            fault_reason = "No state reported"
            water_level_ok = False
        else:
            pump_state = state_dict['state']
            commissioned = True  # Infer from presence of state data
            fault_reason = state_dict.get('fault_reason')
            water_level_ok = True  # Should be reported in state
            
            # If there's a pending acknowledged command, set state to transitioning
            if last_command and last_command['status'] == 'acknowledged':
                if last_command['action'] == 'start':
                    pump_state = "starting"
                elif last_command['action'] == 'stop':
                    pump_state = "stopping"
            
            if fault_reason:
                pump_state = "fault"
        
        return PumpStatus(
            device_id=device_id,
            device_status=device_status,
            pump_state=pump_state,
            commissioned=commissioned,
            fault_reason=fault_reason,
            water_level_ok=water_level_ok,
            last_command=last_command,
            last_update=datetime.fromisoformat(device_dict['last_seen']) if device_dict['last_seen'] else None
        )
