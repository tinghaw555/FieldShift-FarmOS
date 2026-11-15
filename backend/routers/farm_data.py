"""
Farm Data Upload & Export Router (Phase 2 & 3)

Endpoints for farmer-provided data import, CSV templates, manual entry,
data export, and refresh functionality.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
import aiosqlite
import csv
import io
import json
import zipfile
from datetime import datetime, date, timedelta

from database.db import get_db, DB_PATH
from models.schemas import (
    FarmerObservation,
    FarmerObservationCreate,
    FarmerObservationCSVRow,
    FarmerObservationCSVPreview,
    FarmerObservationImportRequest,
    FarmerObservationImportResponse
)
from services.nasa_power import nasa_power_service, NASAPowerError
import httpx

router = APIRouter(prefix="/api/farm-data", tags=["Farm Data"])


# ============================================================================
# CSV TEMPLATE DOWNLOAD
# ============================================================================

@router.get("/{farm_id}/template")
async def download_csv_template(farm_id: int, db: aiosqlite.Connection = Depends(get_db)):
    """
    Download CSV template for farmer observations
    
    Returns a CSV file with:
    - Header row with column names
    - Unit descriptions in comments
    - Example rows showing proper format
    """
    # Verify farm exists
    async with db.execute("SELECT name FROM farms WHERE id = ?", (farm_id,)) as cursor:
        farm = await cursor.fetchone()
        if not farm:
            raise HTTPException(status_code=404, detail=f"Farm {farm_id} not found")
    
    farm_name = farm[0]
    
    # Generate CSV template
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header comments
    output.write(f"# FieldShift FarmOS - Farmer Observations Template\n")
    output.write(f"# Farm: {farm_name} (ID: {farm_id})\n")
    output.write(f"# Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    output.write(f"#\n")
    output.write(f"# INSTRUCTIONS:\n")
    output.write(f"# - observation_date: Required. Format YYYY-MM-DD (e.g., 2024-01-15)\n")
    output.write(f"# - observation_time: Optional. Format HH:MM or HH:MM:SS (e.g., 08:30 or 14:45:00)\n")
    output.write(f"# - temperature: Optional. Air temperature in degrees Celsius (e.g., 22.5)\n")
    output.write(f"# - humidity: Optional. Relative humidity as percentage 0-100 (e.g., 65)\n")
    output.write(f"# - rainfall: Optional. Rainfall in millimeters (e.g., 5.2)\n")
    output.write(f"# - soil_moisture_raw: Optional. Raw ADC sensor value 0-4095 (e.g., 2450)\n")
    output.write(f"# - soil_moisture_percent: Optional. Calibrated soil moisture percentage 0-100 (e.g., 45)\n")
    output.write(f"# - water_level: Optional. Use exactly: Low, OK, or Unknown\n")
    output.write(f"# - notes: Optional. Any text notes or observations (max 1000 characters)\n")
    output.write(f"#\n")
    output.write(f"# TIPS:\n")
    output.write(f"# - Leave cells empty for missing measurements (do not use 0 unless actually zero)\n")
    output.write(f"# - Use soil_moisture_raw for raw sensor values OR soil_moisture_percent if calibrated\n")
    output.write(f"# - One observation per row\n")
    output.write(f"# - Delete these comment lines before uploading\n")
    output.write(f"# - Delete example rows and add your own data\n")
    output.write(f"#\n")
    
    # Column headers
    writer.writerow([
        'observation_date',
        'observation_time',
        'temperature',
        'humidity',
        'rainfall',
        'soil_moisture_raw',
        'soil_moisture_percent',
        'water_level',
        'notes'
    ])
    
    # Example rows
    today = date.today()
    writer.writerow([
        today.strftime('%Y-%m-%d'),
        '08:30',
        '22.5',
        '65',
        '',
        '2450',
        '',
        'OK',
        'Morning reading, clear sky'
    ])
    
    writer.writerow([
        (today.replace(day=today.day-1)).strftime('%Y-%m-%d'),
        '18:00',
        '23.1',
        '63',
        '5.2',
        '',
        '45',
        'OK',
        'Light rain overnight'
    ])
    
    writer.writerow([
        (today.replace(day=today.day-2)).strftime('%Y-%m-%d'),
        '',
        '',
        '',
        '12.5',
        '',
        '',
        'Low',
        'Heavy rain, water level dropped after irrigation'
    ])
    
    # Return as downloadable file
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="fieldshift_observations_{farm_name.replace(" ", "_")}.csv"'
        }
    )


# ============================================================================
# CSV UPLOAD & PREVIEW
# ============================================================================

@router.post("/{farm_id}/upload-preview")
async def upload_csv_preview(
    farm_id: int,
    file: UploadFile = File(...),
    db: aiosqlite.Connection = Depends(get_db)
):
    """
    Upload CSV and preview contents before importing
    
    Validates format, checks for errors, returns preview for user confirmation
    """
    # Verify farm exists
    async with db.execute("SELECT name FROM farms WHERE id = ?", (farm_id,)) as cursor:
        farm = await cursor.fetchone()
        if not farm:
            raise HTTPException(status_code=404, detail=f"Farm {farm_id} not found")
    
    # Check file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file (.csv extension)")
    
    # Read file content
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
    
    # Parse CSV
    rows = []
    reader = csv.DictReader(io.StringIO(content_str))
    
    # Expected columns
    expected_cols = {
        'observation_date', 'observation_time', 'temperature', 'humidity',
        'rainfall', 'soil_moisture_raw', 'soil_moisture_percent', 'water_level', 'notes'
    }
    
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no header row")
    
    columns_found = [col.strip() for col in reader.fieldnames if not col.startswith('#')]
    
    # Check for required column
    if 'observation_date' not in columns_found:
        raise HTTPException(
            status_code=400,
            detail="CSV must have 'observation_date' column. Download template for correct format."
        )
    
    valid_count = 0
    warning_count = 0
    error_count = 0
    row_number = 0
    
    for csv_row in reader:
        row_number += 1
        
        # Skip comment rows
        if csv_row.get('observation_date', '').startswith('#'):
            continue
        
        validation_status = "valid"
        validation_messages = []
        
        # Clean and parse row
        obs_date = csv_row.get('observation_date', '').strip()
        obs_time = csv_row.get('observation_time', '').strip() or None
        
        # Validate observation_date (REQUIRED)
        if not obs_date:
            validation_status = "error"
            validation_messages.append("observation_date is required")
        else:
            try:
                datetime.strptime(obs_date, "%Y-%m-%d")
            except ValueError:
                validation_status = "error"
                validation_messages.append("observation_date must be YYYY-MM-DD format")
        
        # Validate observation_time (OPTIONAL)
        if obs_time:
            try:
                datetime.strptime(obs_time, "%H:%M:%S")
            except ValueError:
                try:
                    datetime.strptime(obs_time, "%H:%M")
                    obs_time = obs_time + ":00"
                except ValueError:
                    validation_status = "warning"
                    validation_messages.append("observation_time should be HH:MM or HH:MM:SS format")
        
        # Parse numeric fields
        def parse_float(value, field_name, min_val=None, max_val=None):
            value = value.strip() if value else None
            if not value:
                return None
            try:
                num = float(value)
                if min_val is not None and num < min_val:
                    validation_messages.append(f"{field_name} below valid range ({min_val})")
                    return None if validation_status != "error" else None
                if max_val is not None and num > max_val:
                    validation_messages.append(f"{field_name} above valid range ({max_val})")
                    return None if validation_status != "error" else None
                return num
            except ValueError:
                validation_messages.append(f"{field_name} must be a number")
                return None
        
        def parse_int(value, field_name, min_val=None, max_val=None):
            value = value.strip() if value else None
            if not value:
                return None
            try:
                num = int(float(value))  # Allow 1234.0 format
                if min_val is not None and num < min_val:
                    validation_messages.append(f"{field_name} below valid range ({min_val})")
                    return None
                if max_val is not None and num > max_val:
                    validation_messages.append(f"{field_name} above valid range ({max_val})")
                    return None
                return num
            except ValueError:
                validation_messages.append(f"{field_name} must be an integer")
                return None
        
        temperature = parse_float(csv_row.get('temperature', ''), 'temperature', -50, 60)
        humidity = parse_float(csv_row.get('humidity', ''), 'humidity', 0, 100)
        rainfall = parse_float(csv_row.get('rainfall', ''), 'rainfall', 0, 1000)
        soil_moisture_raw = parse_int(csv_row.get('soil_moisture_raw', ''), 'soil_moisture_raw', 0, 4095)
        soil_moisture_percent = parse_float(csv_row.get('soil_moisture_percent', ''), 'soil_moisture_percent', 0, 100)
        
        # Validate water_level
        water_level = csv_row.get('water_level', '').strip() or None
        if water_level and water_level not in ['Low', 'OK', 'Unknown']:
            validation_status = "warning"
            validation_messages.append("water_level should be: Low, OK, or Unknown")
            water_level = None
        
        # Notes
        notes = csv_row.get('notes', '').strip() or None
        if notes and len(notes) > 1000:
            notes = notes[:1000]
            validation_status = "warning"
            validation_messages.append("notes truncated to 1000 characters")
        
        # Check if row has any data
        has_data = any([
            temperature is not None,
            humidity is not None,
            rainfall is not None,
            soil_moisture_raw is not None,
            soil_moisture_percent is not None,
            water_level is not None,
            notes is not None
        ])
        
        if not has_data and validation_status == "valid":
            validation_status = "warning"
            validation_messages.append("Row has no measurement data")
        
        # Update counts
        if validation_status == "error":
            error_count += 1
        elif validation_status == "warning":
            warning_count += 1
        else:
            valid_count += 1
        
        rows.append(FarmerObservationCSVRow(
            row_number=row_number,
            observation_date=obs_date,
            observation_time=obs_time,
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall,
            soil_moisture_raw=soil_moisture_raw,
            soil_moisture_percent=soil_moisture_percent,
            water_level=water_level,
            notes=notes,
            validation_status=validation_status,
            validation_message="; ".join(validation_messages) if validation_messages else None
        ))
    
    if len(rows) == 0:
        raise HTTPException(status_code=400, detail="CSV file contains no data rows")
    
    # Return preview (limit to first 100 rows for display)
    return FarmerObservationCSVPreview(
        filename=file.filename,
        total_rows=len(rows),
        valid_rows=valid_count,
        warning_rows=warning_count,
        error_rows=error_count,
        preview_rows=rows[:100],  # Show first 100 rows
        columns_found=columns_found,
        columns_expected=list(expected_cols)
    )


# ============================================================================
# IMPORT CSV DATA
# ============================================================================

@router.post("/{farm_id}/import")
async def import_farmer_observations(
    farm_id: int,
    import_request: FarmerObservationImportRequest,
    db: aiosqlite.Connection = Depends(get_db)
):
    """
    Import farmer observations from previewed CSV data
    
    Only imports rows with validation_status = "valid" or "warning"
    Skips rows with errors
    """
    if import_request.farm_id != farm_id:
        raise HTTPException(status_code=400, detail="Farm ID mismatch")
    
    # Verify farm exists
    async with db.execute("SELECT name FROM farms WHERE id = ?", (farm_id,)) as cursor:
        farm = await cursor.fetchone()
        if not farm:
            raise HTTPException(status_code=404, detail=f"Farm {farm_id} not found")
    
    imported_count = 0
    skipped_errors = 0
    skipped_duplicates = 0
    
    for row in import_request.rows:
        # Skip error rows
        if row.validation_status == "error":
            skipped_errors += 1
            continue
        
        # Check for duplicate (same farm_id, same date, same time)
        async with db.execute("""
            SELECT id FROM farmer_observations
            WHERE farm_id = ? AND observation_date = ? AND observation_time IS ?
        """, (farm_id, row.observation_date, row.observation_time)) as cursor:
            existing = await cursor.fetchone()
            if existing:
                skipped_duplicates += 1
                continue
        
        # Insert observation
        await db.execute("""
            INSERT INTO farmer_observations (
                farm_id, observation_date, observation_time,
                temperature, humidity, rainfall,
                soil_moisture_raw, soil_moisture_percent, water_level,
                notes, data_source, upload_method, validation_status, validation_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Farmer-Provided', 'csv', ?, ?)
        """, (
            farm_id,
            row.observation_date,
            row.observation_time,
            row.temperature,
            row.humidity,
            row.rainfall,
            row.soil_moisture_raw,
            row.soil_moisture_percent,
            row.water_level,
            row.notes,
            row.validation_status,
            row.validation_message
        ))
        
        imported_count += 1
    
    await db.commit()
    
    summary = f"Imported {imported_count} observations successfully."
    if skipped_errors > 0:
        summary += f" Skipped {skipped_errors} rows with errors."
    if skipped_duplicates > 0:
        summary += f" Skipped {skipped_duplicates} duplicate observations."
    
    return FarmerObservationImportResponse(
        farm_id=farm_id,
        total_imported=imported_count,
        skipped_errors=skipped_errors,
        skipped_duplicates=skipped_duplicates,
        import_summary=summary
    )


# ============================================================================
# MANUAL ENTRY
# ============================================================================

@router.post("/{farm_id}/observations", response_model=FarmerObservation)
async def create_farmer_observation(
    farm_id: int,
    observation: FarmerObservationCreate,
    db: aiosqlite.Connection = Depends(get_db)
):
    """
    Add a single farmer observation manually
    """
    if observation.farm_id != farm_id:
        raise HTTPException(status_code=400, detail="Farm ID mismatch")
    
    # Verify farm exists
    async with db.execute("SELECT id FROM farms WHERE id = ?", (farm_id,)) as cursor:
        farm = await cursor.fetchone()
        if not farm:
            raise HTTPException(status_code=404, detail=f"Farm {farm_id} not found")
    
    # Insert observation
    async with db.execute("""
        INSERT INTO farmer_observations (
            farm_id, observation_date, observation_time,
            temperature, humidity, rainfall,
            soil_moisture_raw, soil_moisture_percent, water_level,
            notes, data_source, upload_method
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Farmer-Provided', 'manual')
    """, (
        observation.farm_id,
        observation.observation_date,
        observation.observation_time,
        observation.temperature,
        observation.humidity,
        observation.rainfall,
        observation.soil_moisture_raw,
        observation.soil_moisture_percent,
        observation.water_level,
        observation.notes
    )) as cursor:
        observation_id = cursor.lastrowid
    
    await db.commit()
    
    # Fetch and return created observation
    async with db.execute("""
        SELECT * FROM farmer_observations WHERE id = ?
    """, (observation_id,)) as cursor:
        row = await cursor.fetchone()
        return FarmerObservation(
            id=row[0],
            farm_id=row[1],
            observation_date=row[2],
            observation_time=row[3],
            temperature=row[4],
            humidity=row[5],
            rainfall=row[6],
            soil_moisture_raw=row[7],
            soil_moisture_percent=row[8],
            water_level=row[9],
            notes=row[10],
            data_source=row[11],
            uploaded_at=datetime.fromisoformat(row[12]),
            upload_method=row[13],
            validation_status=row[14],
            validation_notes=row[15]
        )


# ============================================================================
# LIST OBSERVATIONS
# ============================================================================

@router.get("/{farm_id}/observations", response_model=List[FarmerObservation])
async def list_farmer_observations(
    farm_id: int,
    limit: int = 100,
    offset: int = 0,
    db: aiosqlite.Connection = Depends(get_db)
):
    """
    List farmer observations for a farm
    
    Returns observations ordered by date (most recent first)
    """
    # Verify farm exists
    async with db.execute("SELECT id FROM farms WHERE id = ?", (farm_id,)) as cursor:
        farm = await cursor.fetchone()
        if not farm:
            raise HTTPException(status_code=404, detail=f"Farm {farm_id} not found")
    
    # Fetch observations
    async with db.execute("""
        SELECT * FROM farmer_observations
        WHERE farm_id = ?
        ORDER BY observation_date DESC, observation_time DESC
        LIMIT ? OFFSET ?
    """, (farm_id, limit, offset)) as cursor:
        rows = await cursor.fetchall()
    
    observations = []
    for row in rows:
        observations.append(FarmerObservation(
            id=row[0],
            farm_id=row[1],
            observation_date=row[2],
            observation_time=row[3],
            temperature=row[4],
            humidity=row[5],
            rainfall=row[6],
            soil_moisture_raw=row[7],
            soil_moisture_percent=row[8],
            water_level=row[9],
            notes=row[10],
            data_source=row[11],
            uploaded_at=datetime.fromisoformat(row[12]),
            upload_method=row[13],
            validation_status=row[14],
            validation_notes=row[15]
        ))
    
    return observations


# ============================================================================
# DELETE OBSERVATION
# ============================================================================

@router.delete("/{farm_id}/observations/{observation_id}")
async def delete_farmer_observation(
    farm_id: int,
    observation_id: int,
    db: aiosqlite.Connection = Depends(get_db)
):
    """
    Delete a single farmer observation
    """
    # Verify observation exists and belongs to farm
    async with db.execute("""
        SELECT id FROM farmer_observations
        WHERE id = ? AND farm_id = ?
    """, (observation_id, farm_id)) as cursor:
        obs = await cursor.fetchone()
        if not obs:
            raise HTTPException(status_code=404, detail="Observation not found")
    
    # Delete observation
    await db.execute("DELETE FROM farmer_observations WHERE id = ?", (observation_id,))
    await db.commit()
    
    return {"message": "Observation deleted successfully", "id": observation_id}


# ============================================================================
# GET OBSERVATION COUNT
# ============================================================================

@router.get("/{farm_id}/observations/count")
async def get_observation_count(
    farm_id: int,
    db: aiosqlite.Connection = Depends(get_db)
):
    """
    Get count of farmer observations for a farm
    """
    async with db.execute("""
        SELECT COUNT(*) FROM farmer_observations WHERE farm_id = ?
    """, (farm_id,)) as cursor:
        count = await cursor.fetchone()
    
    return {"farm_id": farm_id, "observation_count": count[0]}


# ============================================================================
# PHASE 3: REFRESH AVAILABLE DATA
# ============================================================================

@router.post("/{farm_id}/refresh")
async def refresh_farm_data(farm_id: int, db: aiosqlite.Connection = Depends(get_db)):
    """
    Refresh available NASA POWER and Open-Meteo data for a farm
    
    Returns updated timestamps and data availability status
    """
    # Verify farm exists
    async with db.execute("SELECT name, latitude, longitude FROM farms WHERE id = ?", (farm_id,)) as cursor:
        farm = await cursor.fetchone()
        if not farm:
            raise HTTPException(status_code=404, detail=f"Farm {farm_id} not found")
    
    farm_name, latitude, longitude = farm[0], farm[1], farm[2]
    
    refresh_result = {
        "farm_id": farm_id,
        "farm_name": farm_name,
        "refreshed_at": datetime.now().isoformat(),
        "nasa_power": {"status": "unavailable", "message": "", "date_range": None, "cached": False},
        "open_meteo": {"status": "unavailable", "message": "", "forecast_days": 0, "issue_time": None}
    }
    
    # Refresh NASA POWER data (last complete year)
    try:
        current_year = datetime.now().year
        last_year = current_year - 1
        start_date = date(last_year, 1, 1)
        end_date = date(last_year, 12, 31)
        
        daily_data = await nasa_power_service.get_climate_data(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date
        )
        
        if daily_data:
            # Cache the data
            data_json = json.dumps({
                "source": "NASA POWER",
                "latitude": latitude,
                "longitude": longitude,
                "data": daily_data,
                "cached": False
            })
            
            # Update or insert cache
            await db.execute("""
                INSERT INTO climate_cache 
                (latitude, longitude, start_date, end_date, source, data)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT DO NOTHING
            """, (latitude, longitude, start_date.strftime('%Y-%m-%d'), 
                  end_date.strftime('%Y-%m-%d'), "NASA POWER", data_json))
            await db.commit()
            
            refresh_result["nasa_power"] = {
                "status": "success",
                "message": f"Retrieved {len(daily_data)} days of historical climate data",
                "date_range": f"{start_date} to {end_date}",
                "cached": False,
                "observation_count": len(daily_data)
            }
        else:
            refresh_result["nasa_power"]["status"] = "no_data"
            refresh_result["nasa_power"]["message"] = "No data returned from NASA POWER"
            
    except NASAPowerError as e:
        # Check for cached data
        async with db.execute("""
            SELECT data, cached_at FROM climate_cache
            WHERE ABS(latitude - ?) < 0.1 AND ABS(longitude - ?) < 0.1
            AND source = 'NASA POWER'
            ORDER BY cached_at DESC LIMIT 1
        """, (latitude, longitude)) as cursor:
            cached = await cursor.fetchone()
            
            if cached:
                cached_data = json.loads(cached[0])
                refresh_result["nasa_power"] = {
                    "status": "cached",
                    "message": f"Using cached data (NASA POWER unavailable: {str(e)})",
                    "cached_at": cached[1],
                    "cached": True
                }
            else:
                refresh_result["nasa_power"]["status"] = "error"
                refresh_result["nasa_power"]["message"] = f"NASA POWER unavailable and no cache: {str(e)}"
    
    # Refresh Open-Meteo forecast
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                    "timezone": "auto",
                    "forecast_days": 7
                }
            )
            response.raise_for_status()
            forecast_data = response.json()
            
            daily = forecast_data.get("daily", {})
            dates = daily.get("time", [])
            
            if dates:
                # Store forecast snapshots for Ground Truth
                issue_time = datetime.now()
                for i, date_str in enumerate(dates):
                    forecast_date = datetime.strptime(date_str, "%Y-%m-%d")
                    lead_hours = int((forecast_date - issue_time).total_seconds() / 3600)
                    
                    await db.execute("""
                        INSERT INTO forecast_snapshots 
                        (farm_id, issue_time, valid_time, lead_hours, temperature, precipitation, data_source)
                        VALUES (?, ?, ?, ?, ?, ?, 'open-meteo')
                    """, (
                        farm_id,
                        issue_time.isoformat(),
                        forecast_date.isoformat(),
                        lead_hours,
                        daily.get("temperature_2m_max", [])[i] if i < len(daily.get("temperature_2m_max", [])) else None,
                        daily.get("precipitation_sum", [])[i] if i < len(daily.get("precipitation_sum", [])) else None
                    ))
                
                await db.commit()
                
                refresh_result["open_meteo"] = {
                    "status": "success",
                    "message": f"Retrieved {len(dates)}-day forecast",
                    "forecast_days": len(dates),
                    "issue_time": issue_time.isoformat(),
                    "forecast_dates": dates
                }
            else:
                refresh_result["open_meteo"]["status"] = "no_data"
                refresh_result["open_meteo"]["message"] = "No forecast data available"
                
    except Exception as e:
        refresh_result["open_meteo"]["status"] = "error"
        refresh_result["open_meteo"]["message"] = f"Open-Meteo unavailable: {str(e)}"
    
    return refresh_result


# ============================================================================
# PHASE 3: EXPORT LATEST ANALYSIS
# ============================================================================

@router.get("/{farm_id}/export/metadata")
async def get_export_metadata(farm_id: int, db: aiosqlite.Connection = Depends(get_db)):
    """
    Get metadata about available datasets for export
    """
    # Verify farm exists
    async with db.execute("""
        SELECT id, name, latitude, longitude, created_at FROM farms WHERE id = ?
    """, (farm_id,)) as cursor:
        farm = await cursor.fetchone()
        if not farm:
            raise HTTPException(status_code=404, detail=f"Farm {farm_id} not found")
    
    farm_id, farm_name, latitude, longitude, created_at = farm
    
    # Check each dataset availability
    datasets = {
        "nasa_power": {"available": False, "count": 0, "date_range": None},
        "open_meteo": {"available": False, "count": 0, "latest_issue": None},
        "farmer_observations": {"available": False, "count": 0, "date_range": None},
        "sensor_readings": {"available": False, "count": 0, "date_range": None},
        "rotations": {"available": False, "count": 0},
        "forecast_snapshots": {"available": False, "count": 0},
        "scientific_results": {"available": False, "note": "Run calculations in dashboard first"}
    }
    
    # NASA POWER
    async with db.execute("""
        SELECT data, start_date, end_date FROM climate_cache
        WHERE ABS(latitude - ?) < 0.1 AND ABS(longitude - ?) < 0.1
        AND source = 'NASA POWER'
        ORDER BY cached_at DESC LIMIT 1
    """, (latitude, longitude)) as cursor:
        climate = await cursor.fetchone()
        if climate:
            cached_data = json.loads(climate[0])
            data_count = len(cached_data.get("data", []))
            datasets["nasa_power"] = {
                "available": True,
                "count": data_count,
                "date_range": f"{climate[1]} to {climate[2]}"
            }
    
    # Open-Meteo
    async with db.execute("""
        SELECT COUNT(*), MIN(valid_time), MAX(valid_time) 
        FROM forecast_snapshots
        WHERE farm_id = ? AND data_source = 'open-meteo'
    """, (farm_id,)) as cursor:
        forecast = await cursor.fetchone()
        if forecast and forecast[0] > 0:
            datasets["open_meteo"] = {
                "available": True,
                "count": forecast[0],
                "date_range": f"{forecast[1]} to {forecast[2]}"
            }
    
    # Farmer Observations
    async with db.execute("""
        SELECT COUNT(*), MIN(observation_date), MAX(observation_date)
        FROM farmer_observations
        WHERE farm_id = ?
    """, (farm_id,)) as cursor:
        obs = await cursor.fetchone()
        if obs and obs[0] > 0:
            datasets["farmer_observations"] = {
                "available": True,
                "count": obs[0],
                "date_range": f"{obs[1]} to {obs[2]}"
            }
    
    # Sensor Readings
    async with db.execute("""
        SELECT COUNT(*), data_source, MIN(timestamp), MAX(timestamp)
        FROM sensor_readings
        WHERE farm_id = ?
        GROUP BY data_source
    """, (farm_id,)) as cursor:
        sensors = await cursor.fetchall()
        sensor_summary = {}
        total_count = 0
        for row in sensors:
            sensor_summary[row[1]] = {"count": row[0], "date_range": f"{row[2]} to {row[3]}"}
            total_count += row[0]
        
        if total_count > 0:
            datasets["sensor_readings"] = {
                "available": True,
                "count": total_count,
                "by_source": sensor_summary
            }
    
    # Rotations
    async with db.execute("""
        SELECT COUNT(*) FROM rotations WHERE farm_id = ?
    """, (farm_id,)) as cursor:
        rot = await cursor.fetchone()
        if rot and rot[0] > 0:
            datasets["rotations"] = {
                "available": True,
                "count": rot[0]
            }
    
    return {
        "farm_id": farm_id,
        "farm_name": farm_name,
        "latitude": latitude,
        "longitude": longitude,
        "datasets": datasets,
        "export_generated_at": datetime.now().isoformat()
    }


@router.get("/{farm_id}/export/csv")
async def export_farm_data_csv(
    farm_id: int,
    datasets: str,  # Comma-separated: nasa_power,farmer_obs,sensors,etc
    db: aiosqlite.Connection = Depends(get_db)
):
    """
    Export farm data as CSV (or ZIP of multiple CSVs)
    
    Query param 'datasets': comma-separated list of:
    - nasa_power
    - open_meteo
    - farmer_observations
    - sensor_readings
    - rotations
    """
    # Verify farm exists
    async with db.execute("""
        SELECT name, latitude, longitude FROM farms WHERE id = ?
    """, (farm_id,)) as cursor:
        farm = await cursor.fetchone()
        if not farm:
            raise HTTPException(status_code=404, detail=f"Farm {farm_id} not found")
    
    farm_name, latitude, longitude = farm
    requested_datasets = [d.strip() for d in datasets.split(',')]
    
    # Create ZIP buffer if multiple datasets
    if len(requested_datasets) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add README
            readme = generate_readme(farm_id, farm_name, latitude, longitude, requested_datasets)
            zipf.writestr("README.txt", readme)
            
            # Add each dataset
            for dataset_name in requested_datasets:
                csv_content = await generate_dataset_csv(farm_id, farm_name, latitude, longitude, dataset_name, db)
                if csv_content:
                    zipf.writestr(f"{dataset_name}.csv", csv_content)
        
        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type='application/zip',
            headers={'Content-Disposition': f'attachment; filename="fieldshift_export_{farm_name.replace(" ", "_")}.zip"'}
        )
    
    # Single CSV
    else:
        dataset_name = requested_datasets[0]
        csv_content = await generate_dataset_csv(farm_id, farm_name, latitude, longitude, dataset_name, db)
        
        if not csv_content:
            raise HTTPException(status_code=404, detail=f"No data available for {dataset_name}")
        
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8')),
            media_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="fieldshift_{dataset_name}_{farm_name.replace(" ", "_")}.csv"'}
        )


@router.get("/{farm_id}/export/json")
async def export_farm_data_json(
    farm_id: int,
    datasets: str,
    db: aiosqlite.Connection = Depends(get_db)
):
    """
    Export farm data as JSON
    """
    # Verify farm exists
    async with db.execute("""
        SELECT name, latitude, longitude FROM farms WHERE id = ?
    """, (farm_id,)) as cursor:
        farm = await cursor.fetchone()
        if not farm:
            raise HTTPException(status_code=404, detail=f"Farm {farm_id} not found")
    
    farm_name, latitude, longitude = farm
    requested_datasets = [d.strip() for d in datasets.split(',')]
    
    export_data = {
        "farm": {
            "id": farm_id,
            "name": farm_name,
            "latitude": latitude,
            "longitude": longitude
        },
        "export_generated_at": datetime.now().isoformat(),
        "datasets": {}
    }
    
    # Export each requested dataset
    for dataset_name in requested_datasets:
        dataset_data = await generate_dataset_json(farm_id, latitude, longitude, dataset_name, db)
        if dataset_data:
            export_data["datasets"][dataset_name] = dataset_data
    
    return export_data


# ============================================================================
# PHASE 3.5: EXPORT SCIENTIFIC CALCULATION RESULTS
# ============================================================================

@router.post("/{farm_id}/export/scientific-results")
async def export_scientific_results(
    farm_id: int,
    request: dict,
    db: aiosqlite.Connection = Depends(get_db)
):
    """
    Export scientific calculation results (planting suitability, crop water balance, 
    rotation comparisons, FlipPoint thresholds)
    
    This endpoint DOES NOT perform new calculations. It requires calculation parameters
    from the dashboard to re-run the SAME calculations for export.
    
    Request body should contain:
    {
        "calculations": {
            "planting_suitability": {
                "crop_name": "corn",
                "planting_date": "2024-05-01",
                "latitude": 40.0,
                "longitude": -95.0
            },
            "crop_water_balance": {
                "crops": [...],
                "year": 2023,
                "latitude": 40.0,
                "longitude": -95.0
            },
            "rotation_comparison": {
                "rotations": {...},
                "year": 2023,
                "latitude": 40.0,
                "longitude": -95.0
            },
            "flippoint": {
                "rotations": {...},
                "parameter": "irrigation_capacity",
                "current_value": 10.5,
                "min_value": 0,
                "max_value": 100,
                "steps": 20,
                "year": 2023,
                "latitude": 40.0,
                "longitude": -95.0
            }
        },
        "format": "csv"  // or "json"
    }
    """
    # Verify farm exists
    async with db.execute("""
        SELECT name, latitude, longitude FROM farms WHERE id = ?
    """, (farm_id,)) as cursor:
        farm = await cursor.fetchone()
        if not farm:
            raise HTTPException(status_code=404, detail=f"Farm {farm_id} not found")
    
    farm_name, farm_latitude, farm_longitude = farm
    
    calculations = request.get("calculations", {})
    export_format = request.get("format", "csv")
    
    if not calculations:
        raise HTTPException(
            status_code=400, 
            detail="No calculations specified. Provide calculation parameters from dashboard."
        )
    
    results = {
        "farm_id": farm_id,
        "farm_name": farm_name,
        "export_timestamp": datetime.now().isoformat(),
        "data_type": "Scientific Model Calculations",
        "note": "These are calculated results using NASA POWER climate data and FAO-56 crop models. Not observed measurements.",
        "calculations": {}
    }
    
    # Import calculation functions
    from routers.planting import assess_planting_suitability
    from routers.rotations import calculate_water_needs, compare_rotations, calculate_flippoint
    
    # 1. Planting Suitability
    if "planting_suitability" in calculations:
        params = calculations["planting_suitability"]
        try:
            result = await assess_planting_suitability({
                "farm_id": farm_id,
                "latitude": params.get("latitude", farm_latitude),
                "longitude": params.get("longitude", farm_longitude),
                "crop_name": params["crop_name"],
                "planting_date": params["planting_date"]
            })
            results["calculations"]["planting_suitability"] = {
                "calculation_timestamp": datetime.now().isoformat(),
                "input_parameters": params,
                "result": result,
                "methodology": "FAO-56 crop water requirements + NASA POWER historical climate (3-year average)",
                "data_sources": ["NASA POWER satellite observations", "Open-Meteo forecast (if within 7 days)", "FAO-56 crop parameters"],
                "units": {
                    "temperature": "degrees_celsius",
                    "precipitation": "mm",
                    "water_demand": "mm"
                }
            }
        except Exception as e:
            results["calculations"]["planting_suitability"] = {
                "error": str(e),
                "note": "Calculation failed. Check input parameters."
            }
    
    # 2. Crop Water Balance
    if "crop_water_balance" in calculations:
        params = calculations["crop_water_balance"]
        try:
            result = await calculate_water_needs({
                "farm_id": farm_id,
                "latitude": params.get("latitude", farm_latitude),
                "longitude": params.get("longitude", farm_longitude),
                "year": params.get("year", 2023),
                "crops": params["crops"]
            })
            results["calculations"]["crop_water_balance"] = {
                "calculation_timestamp": datetime.now().isoformat(),
                "input_parameters": params,
                "result": result,
                "methodology": "Simplified FAO-56 crop coefficient method with daily ET0 calculation",
                "data_sources": ["NASA POWER daily climate data"],
                "units": {
                    "water_demand": "mm",
                    "precipitation": "mm",
                    "irrigation_need": "mm",
                    "temperature": "degrees_celsius"
                }
            }
        except Exception as e:
            results["calculations"]["crop_water_balance"] = {
                "error": str(e),
                "note": "Calculation failed. Check input parameters."
            }
    
    # 3. Rotation Comparison
    if "rotation_comparison" in calculations:
        params = calculations["rotation_comparison"]
        try:
            result = await compare_rotations({
                "farm_id": farm_id,
                "latitude": params.get("latitude", farm_latitude),
                "longitude": params.get("longitude", farm_longitude),
                "year": params.get("year", 2023),
                "rotations": params["rotations"]
            })
            results["calculations"]["rotation_comparison"] = {
                "calculation_timestamp": datetime.now().isoformat(),
                "input_parameters": params,
                "result": result,
                "methodology": "Compare multiple rotations using water stress days and irrigation capacity constraints",
                "data_sources": ["NASA POWER daily climate data", "Farm irrigation capacity configuration"],
                "units": {
                    "water_demand": "mm",
                    "irrigation_capacity": "mm_per_day",
                    "stress_days": "days"
                }
            }
        except Exception as e:
            results["calculations"]["rotation_comparison"] = {
                "error": str(e),
                "note": "Calculation failed. Check input parameters."
            }
    
    # 4. FlipPoint Analysis
    if "flippoint" in calculations:
        params = calculations["flippoint"]
        try:
            result = await calculate_flippoint({
                "farm_id": farm_id,
                "latitude": params.get("latitude", farm_latitude),
                "longitude": params.get("longitude", farm_longitude),
                "year": params.get("year", 2023),
                "rotations": params["rotations"],
                "parameter": params.get("parameter", "irrigation_capacity"),
                "current_value": params.get("current_value", 0),
                "min_value": params.get("min_value", 0),
                "max_value": params.get("max_value", 100),
                "steps": params.get("steps", 20)
            })
            results["calculations"]["flippoint"] = {
                "calculation_timestamp": datetime.now().isoformat(),
                "input_parameters": params,
                "result": result,
                "methodology": "Calculate threshold where preferred rotation changes based on varying irrigation capacity",
                "data_sources": ["NASA POWER daily climate data"],
                "units": {
                    "irrigation_capacity": "mm_per_week",
                    "water_demand": "mm",
                    "stress_score": "dimensionless"
                }
            }
        except Exception as e:
            results["calculations"]["flippoint"] = {
                "error": str(e),
                "note": "Calculation failed. Check input parameters."
            }
    
    # Return based on format
    if export_format == "json":
        return results
    
    elif export_format == "csv":
        # Generate CSV files for each calculation type
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # README
            readme_content = f"""FieldShift FarmOS - Scientific Calculation Results Export
================================================================================

Farm: {farm_name} (ID: {farm_id})
Coordinates: {farm_latitude}, {farm_longitude}
Export Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

IMPORTANT: DATA TYPE AND PROVENANCE
================================================================================

This export contains CALCULATED SCIENTIFIC RESULTS, not observed measurements.

Data Type: MODEL CALCULATIONS
Source: NASA POWER historical climate data + FAO-56 crop water models
Calculations: Performed on-demand using parameters from FieldShift dashboard

These results are:
  ✓ Scientific model outputs
  ✓ Based on NASA POWER satellite observations
  ✓ Calculated using internationally recognized FAO-56 methodology
  ✗ NOT direct field measurements
  ✗ NOT real-time sensor readings
  ✗ NOT farmer-provided observations

METHODOLOGY
================================================================================

Planting Suitability:
  - Uses 3-year NASA POWER climate averages
  - Applies crop-specific temperature and water requirements
  - Incorporates Open-Meteo 7-day forecast if planting within 7 days
  - Assesses temperature fit, water availability, and risks

Crop Water Balance:
  - Simplified FAO-56 crop coefficient method
  - Daily ET0 calculation using temperature and solar radiation
  - Seasonal ETc = ET0 × Kc (crop coefficient)
  - Compares rainfall vs crop water demand

Rotation Comparison:
  - Calculates water needs for each crop in rotation
  - Estimates water stress days
  - Considers farm irrigation capacity constraints
  - Recommends rotation with lowest stress

FlipPoint Analysis:
  - Tests rotations across range of irrigation capacity values
  - Identifies threshold where optimal rotation changes
  - Helps farmers understand infrastructure requirements

UNITS
================================================================================

Temperature: degrees Celsius (°C)
Precipitation: millimeters (mm)
Water Demand: millimeters (mm) per season
Irrigation Capacity: millimeters per week (mm/week)
Stress Days: number of days
Solar Radiation: MJ/m²/day

CALCULATIONS INCLUDED
================================================================================

"""
            
            for calc_type in results["calculations"].keys():
                if "error" not in results["calculations"][calc_type]:
                    readme_content += f"✓ {calc_type.replace('_', ' ').title()}\n"
                else:
                    readme_content += f"✗ {calc_type.replace('_', ' ').title()} (failed)\n"
            
            readme_content += f"""

DATA SOURCES
================================================================================

NASA POWER: NASA Prediction Of Worldwide Energy Resources
  - Source: Satellite observations and reanalysis
  - Resolution: ~50km grid cells
  - Parameters: Temperature, precipitation, solar radiation, humidity, wind
  - Website: https://power.larc.nasa.gov/

Open-Meteo: Open-source weather API
  - Source: Multiple weather models (NOAA GFS, DWD ICON, etc.)
  - Resolution: Varies by model
  - Parameters: Temperature, precipitation forecasts
  - Website: https://open-meteo.com/

FAO-56: FAO Irrigation and Drainage Paper No. 56
  - Crop Evapotranspiration guidelines
  - Crop coefficients (Kc values)
  - Standard reference methodology
  - Publication: Food and Agriculture Organization of the United Nations

LIMITATIONS
================================================================================

- Historical averages don't guarantee future conditions
- NASA POWER data is ~50km resolution - local conditions may vary
- Simplified ET0 calculation (not full Penman-Monteith)
- Does not consider: soil type details, pests, diseases, market prices
- Estimates are for comparison purposes, not precise predictions

CITATION
================================================================================

When using this data, please cite:

FieldShift FarmOS (2026). Scientific Calculation Results.
Data sources: NASA POWER, Open-Meteo, FAO-56 methodology.
Farm: {farm_name} (ID: {farm_id})
Generated: {datetime.now().strftime('%Y-%m-%d')}

================================================================================
"""
            
            zip_file.writestr("README.txt", readme_content)
            
            # Planting Suitability CSV
            if "planting_suitability" in results["calculations"] and "result" in results["calculations"]["planting_suitability"]:
                csv_buffer = io.StringIO()
                csv_buffer.write("# FieldShift FarmOS - Planting Suitability Assessment\n")
                csv_buffer.write(f"# Farm: {farm_name} (ID: {farm_id})\n")
                csv_buffer.write(f"# Calculation Timestamp: {results['calculations']['planting_suitability']['calculation_timestamp']}\n")
                csv_buffer.write("# Data Type: MODEL CALCULATION (not observed measurement)\n")
                csv_buffer.write("# Methodology: FAO-56 + NASA POWER 3-year climate average\n")
                csv_buffer.write("#\n")
                
                writer = csv.writer(csv_buffer)
                result_data = results["calculations"]["planting_suitability"]["result"]
                
                writer.writerow([
                    "farm_id", "farm_name", "latitude", "longitude",
                    "crop_name", "planting_date", "harvest_date", "season_length_days",
                    "recommendation", "main_reason", "assessment_type", "years_analyzed",
                    "data_type", "calculation_timestamp"
                ])
                
                writer.writerow([
                    farm_id, farm_name, result_data.get("latitude"), result_data.get("longitude"),
                    result_data.get("crop_name"), result_data.get("planting_date"), 
                    result_data.get("harvest_date"), result_data.get("season_length_days"),
                    result_data.get("recommendation"), result_data.get("main_reason"),
                    result_data.get("assessment_type"), result_data.get("years_analyzed"),
                    "MODEL_CALCULATION", results["calculations"]["planting_suitability"]["calculation_timestamp"]
                ])
                
                # Additional details
                csv_buffer.write("\n# Climate Evidence:\n")
                for evidence in result_data.get("climate_evidence", []):
                    csv_buffer.write(f"# - {evidence}\n")
                
                csv_buffer.write("\n# Risks:\n")
                for risk in result_data.get("risks", []):
                    csv_buffer.write(f"# - {risk}\n")
                
                csv_buffer.write("\n# Farmer Actions:\n")
                for action in result_data.get("farmer_actions", []):
                    csv_buffer.write(f"# - {action}\n")
                
                zip_file.writestr("planting_suitability.csv", csv_buffer.getvalue())
            
            # Crop Water Balance CSV
            if "crop_water_balance" in results["calculations"] and "result" in results["calculations"]["crop_water_balance"]:
                csv_buffer = io.StringIO()
                csv_buffer.write("# FieldShift FarmOS - Crop Water Balance Calculations\n")
                csv_buffer.write(f"# Farm: {farm_name} (ID: {farm_id})\n")
                csv_buffer.write(f"# Calculation Timestamp: {results['calculations']['crop_water_balance']['calculation_timestamp']}\n")
                csv_buffer.write("# Data Type: MODEL CALCULATION (not observed measurement)\n")
                csv_buffer.write("# Methodology: Simplified FAO-56 crop coefficient method\n")
                csv_buffer.write("# Units: Water demand and irrigation in millimeters (mm)\n")
                csv_buffer.write("#\n")
                
                writer = csv.writer(csv_buffer)
                result_data = results["calculations"]["crop_water_balance"]["result"]
                
                writer.writerow([
                    "farm_id", "crop_name", "planting_date", "harvest_date", "season_length_days",
                    "seasonal_water_demand_mm", "precipitation_mm", "irrigation_need_mm", 
                    "estimated_stress_days", "data_type", "calculation_timestamp"
                ])
                
                for crop_result in result_data.get("crop_results", []):
                    writer.writerow([
                        farm_id, crop_result.get("crop"), crop_result.get("planting_date"),
                        crop_result.get("harvest_date"), crop_result.get("season_length_days"),
                        crop_result.get("seasonal_water_demand_mm"), crop_result.get("precipitation_mm"),
                        crop_result.get("irrigation_need_mm"), crop_result.get("estimated_stress_days"),
                        "MODEL_CALCULATION", results["calculations"]["crop_water_balance"]["calculation_timestamp"]
                    ])
                
                zip_file.writestr("crop_water_balance.csv", csv_buffer.getvalue())
            
            # Rotation Comparison CSV
            if "rotation_comparison" in results["calculations"] and "result" in results["calculations"]["rotation_comparison"]:
                csv_buffer = io.StringIO()
                csv_buffer.write("# FieldShift FarmOS - Rotation Comparison Results\n")
                csv_buffer.write(f"# Farm: {farm_name} (ID: {farm_id})\n")
                csv_buffer.write(f"# Calculation Timestamp: {results['calculations']['rotation_comparison']['calculation_timestamp']}\n")
                csv_buffer.write("# Data Type: MODEL CALCULATION (not observed measurement)\n")
                csv_buffer.write("# Methodology: Water stress comparison across rotations\n")
                csv_buffer.write("#\n")
                
                writer = csv.writer(csv_buffer)
                result_data = results["calculations"]["rotation_comparison"]["result"]
                
                writer.writerow([
                    "farm_id", "rotation_type", "feasible", "total_seasonal_water_demand_mm",
                    "total_stress_days", "total_irrigation_need_mm", "irrigation_capacity_mm_day",
                    "preferred", "data_type", "calculation_timestamp"
                ])
                
                preferred = result_data.get("comparison", {}).get("preferred_rotation")
                
                for rot_type, rot_result in result_data.get("results", {}).items():
                    if "error" not in rot_result:
                        writer.writerow([
                            farm_id, rot_type, rot_result.get("feasible"),
                            rot_result.get("total_seasonal_water_demand_mm"),
                            rot_result.get("total_stress_days"),
                            rot_result.get("total_irrigation_need_mm"),
                            rot_result.get("irrigation_capacity_mm_day"),
                            "Yes" if rot_type == preferred else "No",
                            "MODEL_CALCULATION", results["calculations"]["rotation_comparison"]["calculation_timestamp"]
                        ])
                
                zip_file.writestr("rotation_comparison.csv", csv_buffer.getvalue())
            
            # FlipPoint CSV
            if "flippoint" in results["calculations"] and "result" in results["calculations"]["flippoint"]:
                csv_buffer = io.StringIO()
                csv_buffer.write("# FieldShift FarmOS - FlipPoint Threshold Analysis\n")
                csv_buffer.write(f"# Farm: {farm_name} (ID: {farm_id})\n")
                csv_buffer.write(f"# Calculation Timestamp: {results['calculations']['flippoint']['calculation_timestamp']}\n")
                csv_buffer.write("# Data Type: MODEL CALCULATION (not observed measurement)\n")
                csv_buffer.write("# Methodology: Iterative water stress analysis across irrigation capacity range\n")
                csv_buffer.write("#\n")
                
                result_data = results["calculations"]["flippoint"]["result"]
                
                csv_buffer.write(f"# FlipPoint Threshold: {result_data.get('flippoint_threshold_mm_week')} mm/week\n")
                csv_buffer.write(f"# Changes From: {result_data.get('flippoint_from')}\n")
                csv_buffer.write(f"# Changes To: {result_data.get('flippoint_to')}\n")
                csv_buffer.write(f"# Current Value: {result_data.get('current_value_mm_week')} mm/week\n")
                csv_buffer.write(f"# Current Preferred: {result_data.get('current_preferred_rotation')}\n")
                csv_buffer.write("#\n")
                
                writer = csv.writer(csv_buffer)
                writer.writerow([
                    "irrigation_mm_week", "preferred_rotation", "stress_scores", 
                    "data_type", "calculation_timestamp"
                ])
                
                for point in result_data.get("data_points", []):
                    writer.writerow([
                        point.get("irrigation_mm_week"),
                        point.get("preferred_rotation"),
                        json.dumps(point.get("stress_scores", {})),
                        "MODEL_CALCULATION",
                        results["calculations"]["flippoint"]["calculation_timestamp"]
                    ])
                
                zip_file.writestr("flippoint_analysis.csv", csv_buffer.getvalue())
        
        # Return ZIP file
        zip_buffer.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return StreamingResponse(
            zip_buffer,
            media_type='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename="fieldshift_scientific_results_{farm_name.replace(" ", "_")}_{timestamp}.zip"'
            }
        )
    
    else:
        raise HTTPException(status_code=400, detail="Format must be 'csv' or 'json'")


# ============================================================================
# EXPORT HELPERS
# ============================================================================

def generate_readme(farm_id: int, farm_name: str, latitude: float, longitude: float, datasets: List[str]) -> str:
    """Generate README for ZIP export"""
    content = f"""FieldShift FarmOS - Data Export
================================================================================

Farm Information:
  Name: {farm_name}
  Farm ID: {farm_id}
  Latitude: {latitude}
  Longitude: {longitude}

Export Details:
  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
  Datasets Included: {', '.join(datasets)}

================================================================================
IMPORTANT: CALCULATED RESULTS vs RAW DATA
================================================================================

This export contains RAW DATA and STRUCTURAL PLANS only.

AVAILABLE IN THIS EXPORT:
  ✅ NASA POWER historical climate observations
  ✅ Open-Meteo weather forecasts
  ✅ Farmer-provided field observations
  ✅ Sensor telemetry (real or simulated)
  ✅ Crop rotation PLANS (structure and dates)

NOT INCLUDED (Calculated On-Demand Only):
  ❌ Planting suitability recommendations
  ❌ Crop water balance calculations (ET0, ETc)
  ❌ Rotation comparison results and rankings
  ❌ FlipPoint threshold calculations
  ❌ Ground Truth forecast accuracy metrics
  ❌ Bare-Soil Guardian outputs

WHY NOT INCLUDED?
These scientific results are calculated on-demand in the dashboard and are
not currently persisted in the database. To obtain these results:

1. Navigate to the relevant section in FieldShift FarmOS:
   - Planting Suitability: "Check Planting Suitability" section
   - Crop Water Balance: "Crop Rotation Lab" → "Compare Rotations"
   - FlipPoint: "FlipPoint & Agricultural Risk" section
   - Ground Truth: "Ground Truth & Evidence" section

2. Run the analysis (results appear on screen immediately)

3. Screenshot or note the results manually

FUTURE ENHANCEMENT:
A future update may add database persistence and export support for
calculated scientific results. Currently, the focus is on exporting
raw observational data with clear provenance.

================================================================================
DATA SOURCE LABELS
================================================================================

This export clearly labels the source of all measurements:

• NASA POWER - Historical climate data from NASA satellite observations
  - Retrieved from: https://power.larc.nasa.gov/
  - Resolution: ~50km grid
  - Coverage: Historical daily data
  - License: NASA Open Data Policy

• Open-Meteo - Weather forecasts
  - Retrieved from: https://open-meteo.com/
  - Coverage: 7-day forecasts
  - License: CC BY 4.0

• Farmer-Provided - Observations uploaded or manually entered by the farmer
  - Source: User input (CSV upload or manual entry)
  - Not verified by NASA or hardware sensors

• Real Sensor - Authenticated physical telemetry from ESP32 hardware
  - Source: IoT devices registered to this farm
  - Requires device authentication

• Demo Mode - Simulated sensor readings
  - Source: Software simulation for demonstration
  - Not real measurements

• Calculated - Model outputs
  - Source: FAO-56 crop water balance calculations
  - Derived from climate data, not direct measurements

================================================================================
MEASUREMENT UNITS
================================================================================

Temperature: Degrees Celsius (°C)
Humidity: Percent (%)
Rainfall/Precipitation: Millimeters (mm)
Wind Speed: Meters per second (m/s)
Solar Radiation: Megajoules per square meter per day (MJ/m²/day)
Soil Moisture (Raw): ADC value (0-4095)
Soil Moisture (Calibrated): Percent (%)
Water Level: Categorical (Low, OK, Unknown)

================================================================================
FILE DESCRIPTIONS
================================================================================

"""
    
    for dataset in datasets:
        if dataset == "nasa_power":
            content += "nasa_power.csv - Historical climate data from NASA POWER satellite observations\n"
        elif dataset == "open_meteo":
            content += "open_meteo.csv - Weather forecast data from Open-Meteo\n"
        elif dataset == "farmer_observations":
            content += "farmer_observations.csv - Farmer-provided observations (uploaded or manual)\n"
        elif dataset == "sensor_readings":
            content += "sensor_readings.csv - Sensor telemetry (real or simulated)\n"
        elif dataset == "rotations":
            content += "rotations.csv - Crop rotation PLANS (structure only, not comparison results)\n"
    
    content += """
================================================================================
CROP ROTATION PLANS vs COMPARISON RESULTS
================================================================================

WHAT'S IN THIS EXPORT (rotations.csv):
  • Rotation structure (current, small_shift, alternative)
  • Crop sequences
  • Planting and harvest dates
  • Creation timestamps

WHAT'S NOT IN THIS EXPORT:
  • Water demand calculations (ET0, ETc)
  • Seasonal irrigation requirements
  • Water stress day estimates
  • Rotation rankings and recommendations
  • FlipPoint thresholds

TO GET COMPARISON RESULTS:
  1. Open FieldShift FarmOS dashboard
  2. Navigate to "Crop Rotation Lab"
  3. Select your rotations
  4. Click "Compare Rotations"
  5. Results calculated using NASA POWER climate data and FAO-56 model
  6. View or screenshot results (not auto-exported yet)

================================================================================
IMPORTANT NOTES
================================================================================

• Data Provenance: Each CSV file includes a 'data_source' column clearly
  identifying whether data is observed, forecast, farmer-provided, simulated,
  or calculated.

• No Secrets: This export does not contain API keys, Wi-Fi passwords, device
  credentials, or authentication tokens.

• Scientific Integrity: We never claim farmer-provided observations are NASA
  data or verified sensor measurements. All sources are honestly labeled.

• Forecast Uncertainty: Weather forecasts become less accurate beyond 3 days.
  Use short-term forecasts for immediate planning only.

• Model Limitations: Calculated values (crop water demand, etc.) are estimates
  based on simplified models. Local conditions may vary significantly.

• On-Demand Calculations: Planting suitability, crop water balance, and
  FlipPoint analyses are calculated on-demand in the dashboard and are not
  currently persisted or exported. Run analyses in the dashboard to view
  results.

• For More Information: See DATA_SOURCES.md and MODEL_LIMITATIONS.md in the
  FieldShift FarmOS project.

================================================================================
"""
    
    return content


async def generate_dataset_csv(
    farm_id: int,
    farm_name: str,
    latitude: float,
    longitude: float,
    dataset_name: str,
    db: aiosqlite.Connection
) -> Optional[str]:
    """Generate CSV content for a specific dataset"""
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    if dataset_name == "nasa_power":
        # NASA POWER climate data
        async with db.execute("""
            SELECT data, start_date, end_date, cached_at FROM climate_cache
            WHERE ABS(latitude - ?) < 0.1 AND ABS(longitude - ?) < 0.1
            AND source = 'NASA POWER'
            ORDER BY cached_at DESC LIMIT 1
        """, (latitude, longitude)) as cursor:
            climate = await cursor.fetchone()
            if not climate:
                return None
            
            cached_data = json.loads(climate[0])
            daily_data = cached_data.get("data", [])
            
            # Header
            output.write(f"# FieldShift FarmOS - NASA POWER Climate Data\n")
            output.write(f"# Farm: {farm_name} (ID: {farm_id})\n")
            output.write(f"# Location: {latitude}, {longitude}\n")
            output.write(f"# Date Range: {climate[1]} to {climate[2]}\n")
            output.write(f"# Retrieved: {climate[3]}\n")
            output.write(f"# Data Source: NASA POWER (https://power.larc.nasa.gov/)\n")
            output.write(f"# License: NASA Open Data Policy\n")
            output.write(f"# Note: Historical satellite observations, not real-time measurements\n")
            output.write(f"#\n")
            
            # Column headers
            writer.writerow([
                'date', 'temperature_mean_C', 'temperature_max_C', 'temperature_min_C',
                'precipitation_mm', 'humidity_percent', 'wind_speed_ms',
                'solar_radiation_MJm2day', 'data_source'
            ])
            
            # Data rows
            for record in daily_data:
                writer.writerow([
                    record.get('date'),
                    record.get('temperature_mean'),
                    record.get('temperature_max'),
                    record.get('temperature_min'),
                    record.get('precipitation'),
                    record.get('humidity'),
                    record.get('wind_speed'),
                    record.get('solar_radiation'),
                    'NASA POWER'
                ])
    
    elif dataset_name == "open_meteo":
        # Open-Meteo forecast
        async with db.execute("""
            SELECT issue_time, valid_time, lead_hours, temperature, precipitation
            FROM forecast_snapshots
            WHERE farm_id = ? AND data_source = 'open-meteo'
            ORDER BY valid_time
        """, (farm_id,)) as cursor:
            forecasts = await cursor.fetchall()
            if not forecasts:
                return None
            
            output.write(f"# FieldShift FarmOS - Open-Meteo Weather Forecast\n")
            output.write(f"# Farm: {farm_name} (ID: {farm_id})\n")
            output.write(f"# Location: {latitude}, {longitude}\n")
            output.write(f"# Data Source: Open-Meteo (https://open-meteo.com/)\n")
            output.write(f"# License: CC BY 4.0\n")
            output.write(f"# Note: These are forecasts, not observations\n")
            output.write(f"#\n")
            
            writer.writerow([
                'issue_time', 'valid_time', 'lead_hours',
                'temperature_C', 'precipitation_mm', 'data_source'
            ])
            
            for row in forecasts:
                writer.writerow([
                    row[0], row[1], row[2], row[3], row[4], 'Open-Meteo Forecast'
                ])
    
    elif dataset_name == "farmer_observations":
        # Farmer-provided observations
        async with db.execute("""
            SELECT observation_date, observation_time, temperature, humidity,
                   rainfall, soil_moisture_raw, soil_moisture_percent, water_level,
                   notes, upload_method, uploaded_at
            FROM farmer_observations
            WHERE farm_id = ?
            ORDER BY observation_date DESC
        """, (farm_id,)) as cursor:
            observations = await cursor.fetchall()
            if not observations:
                return None
            
            output.write(f"# FieldShift FarmOS - Farmer-Provided Observations\n")
            output.write(f"# Farm: {farm_name} (ID: {farm_id})\n")
            output.write(f"# Data Source: Farmer-Provided (User Input)\n")
            output.write(f"# Note: NOT verified NASA observations or real sensor data\n")
            output.write(f"#\n")
            
            writer.writerow([
                'observation_date', 'observation_time', 'temperature_C', 'humidity_percent',
                'rainfall_mm', 'soil_moisture_raw_ADC', 'soil_moisture_percent',
                'water_level', 'notes', 'upload_method', 'uploaded_at', 'data_source'
            ])
            
            for row in observations:
                writer.writerow([
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                    row[7], row[8], row[9], row[10], 'Farmer-Provided'
                ])
    
    elif dataset_name == "sensor_readings":
        # Sensor readings (real or simulated)
        async with db.execute("""
            SELECT timestamp, sensor_type, value, unit, data_source, device_id
            FROM sensor_readings
            WHERE farm_id = ?
            ORDER BY timestamp DESC
        """, (farm_id,)) as cursor:
            readings = await cursor.fetchall()
            if not readings:
                return None
            
            output.write(f"# FieldShift FarmOS - Sensor Readings\n")
            output.write(f"# Farm: {farm_name} (ID: {farm_id})\n")
            output.write(f"# Note: Check 'data_source' column - may be Real Sensor or Demo Mode\n")
            output.write(f"#\n")
            
            writer.writerow([
                'timestamp', 'sensor_type', 'value', 'unit', 'device_id', 'data_source'
            ])
            
            for row in readings:
                writer.writerow([row[0], row[1], row[2], row[3], row[5], row[4]])
    
    elif dataset_name == "rotations":
        # Crop rotations - PLANS ONLY (not calculated comparison results)
        async with db.execute("""
            SELECT r.id, r.name, r.rotation_type, r.created_at,
                   rc.crop_name, rc.planting_date, rc.harvest_date, rc.sequence_order
            FROM rotations r
            LEFT JOIN rotation_crops rc ON r.id = rc.rotation_id
            WHERE r.farm_id = ?
            ORDER BY r.id, rc.sequence_order
        """, (farm_id,)) as cursor:
            rotations = await cursor.fetchall()
            if not rotations:
                return None
            
            output.write(f"# FieldShift FarmOS - Crop Rotation Plans\n")
            output.write(f"# Farm: {farm_name} (ID: {farm_id})\n")
            output.write(f"# \n")
            output.write(f"# IMPORTANT: This export contains rotation PLANS (structure) only.\n")
            output.write(f"# This is NOT the comparison results or water balance calculations.\n")
            output.write(f"# \n")
            output.write(f"# To get scientific analysis results:\n")
            output.write(f"# 1. Go to 'Crop Rotation Lab' section in the dashboard\n")
            output.write(f"# 2. Select rotations to compare\n")
            output.write(f"# 3. Click 'Compare Rotations' to calculate water demands\n")
            output.write(f"# 4. Results will appear on screen (not auto-exported yet)\n")
            output.write(f"# \n")
            output.write(f"# Scientific calculations include:\n")
            output.write(f"# - Crop water requirements (ET0, ETc)\n")
            output.write(f"# - Seasonal irrigation needs\n")
            output.write(f"# - Water stress days\n")
            output.write(f"# - Rotation comparison and recommendations\n")
            output.write(f"# \n")
            output.write(f"# Status: Calculated On-Demand (Not Persisted in Database)\n")
            output.write(f"#\n")
            
            writer.writerow([
                'rotation_id', 'rotation_name', 'rotation_type', 'created_at',
                'crop_name', 'planting_date', 'harvest_date', 'sequence_order'
            ])
            
            for row in rotations:
                writer.writerow(row)
    
    else:
        return None
    
    output.seek(0)
    return output.getvalue()


async def generate_dataset_json(
    farm_id: int,
    latitude: float,
    longitude: float,
    dataset_name: str,
    db: aiosqlite.Connection
) -> Optional[dict]:
    """Generate JSON data for a specific dataset"""
    
    if dataset_name == "nasa_power":
        async with db.execute("""
            SELECT data, start_date, end_date, cached_at FROM climate_cache
            WHERE ABS(latitude - ?) < 0.1 AND ABS(longitude - ?) < 0.1
            AND source = 'NASA POWER'
            ORDER BY cached_at DESC LIMIT 1
        """, (latitude, longitude)) as cursor:
            climate = await cursor.fetchone()
            if not climate:
                return None
            
            cached_data = json.loads(climate[0])
            return {
                "data_source": "NASA POWER",
                "date_range": {"start": climate[1], "end": climate[2]},
                "retrieved_at": climate[3],
                "observation_type": "historical_satellite",
                "data": cached_data.get("data", [])
            }
    
    elif dataset_name == "farmer_observations":
        async with db.execute("""
            SELECT observation_date, observation_time, temperature, humidity,
                   rainfall, soil_moisture_raw, soil_moisture_percent, water_level,
                   notes, upload_method, uploaded_at
            FROM farmer_observations
            WHERE farm_id = ?
            ORDER BY observation_date DESC
        """, (farm_id,)) as cursor:
            observations = await cursor.fetchall()
            if not observations:
                return None
            
            return {
                "data_source": "Farmer-Provided",
                "observation_type": "user_input",
                "note": "NOT verified NASA observations or real sensor data",
                "count": len(observations),
                "observations": [
                    {
                        "date": row[0],
                        "time": row[1],
                        "temperature_C": row[2],
                        "humidity_percent": row[3],
                        "rainfall_mm": row[4],
                        "soil_moisture_raw_ADC": row[5],
                        "soil_moisture_percent": row[6],
                        "water_level": row[7],
                        "notes": row[8],
                        "upload_method": row[9],
                        "uploaded_at": row[10]
                    }
                    for row in observations
                ]
            }
    
    # Add other datasets as needed
    return None
