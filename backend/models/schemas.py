"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date

# ============================================================================
# FARM MODELS
# ============================================================================

class FarmBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class FarmCreate(FarmBase):
    pass

class FarmConfig(BaseModel):
    soil_type: Optional[str] = "loam"
    field_capacity: Optional[float] = Field(default=0.30, ge=0, le=1)  # volumetric
    wilting_point: Optional[float] = Field(default=0.15, ge=0, le=1)  # volumetric
    soil_depth: Optional[float] = Field(default=1.0, gt=0, le=3.0)  # meters
    irrigation_available: bool = True
    irrigation_capacity: Optional[float] = Field(default=20.0, ge=0)  # mm/day

class Farm(FarmBase):
    id: int
    created_at: datetime
    config: Optional[FarmConfig] = None
    is_favorite: Optional[bool] = False
    last_selected_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FarmUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[FarmConfig] = None

# ============================================================================
# CROP MODELS
# ============================================================================

class CropInRotation(BaseModel):
    crop_name: str
    planting_date: str  # Format: "MM-DD" or "YYYY-MM-DD"
    harvest_date: str
    sequence_order: int

    @field_validator('planting_date', 'harvest_date')
    @classmethod
    def validate_date_format(cls, v):
        # Accept MM-DD or YYYY-MM-DD format
        if len(v) == 5:  # MM-DD
            try:
                datetime.strptime(v, "%m-%d")
                return v
            except ValueError:
                raise ValueError("Date must be in MM-DD format")
        elif len(v) == 10:  # YYYY-MM-DD
            try:
                datetime.strptime(v, "%Y-%m-%d")
                return v
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        else:
            raise ValueError("Date must be in MM-DD or YYYY-MM-DD format")

class RotationBase(BaseModel):
    name: str
    rotation_type: str = Field(..., pattern="^(current|small_shift|alternative)$")
    crops: List[CropInRotation]

class RotationCreate(RotationBase):
    farm_id: int

class Rotation(RotationBase):
    id: int
    farm_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# CLIMATE MODELS
# ============================================================================

class ClimateDataPoint(BaseModel):
    date: str
    temperature_mean: Optional[float] = None
    temperature_max: Optional[float] = None
    temperature_min: Optional[float] = None
    precipitation: Optional[float] = None  # mm
    humidity: Optional[float] = None  # %
    wind_speed: Optional[float] = None  # m/s
    solar_radiation: Optional[float] = None  # MJ/m²/day

class ClimateRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    start_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD

class ClimateResponse(BaseModel):
    source: str = "NASA POWER"
    latitude: float
    longitude: float
    data: List[ClimateDataPoint]
    cached: bool = False

# ============================================================================
# WEATHER FORECAST MODELS
# ============================================================================

class WeatherForecastDay(BaseModel):
    date: str
    temperature_max: float
    temperature_min: float
    temperature_mean: float
    precipitation: float  # mm
    precipitation_probability: Optional[float] = None  # %
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None

class WeatherForecastResponse(BaseModel):
    source: str = "Open-Meteo"
    latitude: float
    longitude: float
    issue_time: datetime
    forecast: List[WeatherForecastDay]

# ============================================================================
# CROP WATER BALANCE MODELS
# ============================================================================

class WaterBalanceDay(BaseModel):
    date: str
    et0: float  # Reference ET (mm)
    etc: float  # Crop ET (mm)
    precipitation: float  # mm
    irrigation: float  # mm
    soil_water: float  # mm
    water_stress: bool
    drainage: float = 0.0  # mm

class CropWaterBalanceResult(BaseModel):
    crop_name: str
    planting_date: str
    harvest_date: str
    total_etc: float  # Total seasonal crop ET (mm)
    total_precipitation: float  # mm
    total_irrigation: float  # mm
    stress_days: int
    daily_balance: List[WaterBalanceDay]

# ============================================================================
# ROTATION COMPARISON MODELS
# ============================================================================

class RotationAnalysis(BaseModel):
    rotation_id: int
    rotation_name: str
    rotation_type: str
    total_water_demand: float  # mm
    total_irrigation_needed: float  # mm
    total_stress_days: int
    bare_soil_days: int
    crop_diversity_score: float
    has_nitrogen_fixer: bool
    crops_analysis: List[CropWaterBalanceResult]

class RotationComparisonRequest(BaseModel):
    farm_id: int
    rotation_ids: List[int] = Field(..., min_length=1, max_length=3)
    year: Optional[int] = None  # Use specific historical year, or None for recent

class RotationComparisonResponse(BaseModel):
    farm: Farm
    climate_year: int
    analyses: List[RotationAnalysis]
    recommendation: Optional[str] = None

# ============================================================================
# FLIPPOINT MODELS
# ============================================================================

class FlipPointRequest(BaseModel):
    farm_id: int
    rotation_ids: List[int] = Field(..., min_length=2, max_length=3)
    parameter: str = Field(..., pattern="^(irrigation_capacity|soil_taw|stress_weight)$")
    min_value: float
    max_value: float
    steps: int = Field(default=20, ge=5, le=50)

class FlipPointDataPoint(BaseModel):
    parameter_value: float
    preferred_rotation_id: int
    preferred_rotation_name: str
    stress_days: dict  # rotation_id -> stress_days

class FlipPointResponse(BaseModel):
    parameter: str
    flip_threshold: Optional[float] = None
    data_points: List[FlipPointDataPoint]
    explanation: str

# ============================================================================
# SIMULATOR MODELS
# ============================================================================

class SensorReading(BaseModel):
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime
    is_simulated: bool = True

class SimulatorState(BaseModel):
    farm_id: int
    air_temperature: float  # °C
    air_humidity: float  # %
    soil_moisture: float  # % (0-100, uncalibrated)
    water_level: float  # % (0-100)
    valve_open: bool
    connected: bool
    last_update: datetime

class IrrigationRecommendation(BaseModel):
    action: str  # "water", "wait", "review", "insufficient_water", "sensor_error"
    reason: str
    urgency: str  # "low", "medium", "high"
    suggested_duration: Optional[int] = None  # seconds

class IrrigationCommand(BaseModel):
    farm_id: int
    action: str = Field(..., pattern="^(open|close)$")
    duration_seconds: Optional[int] = Field(default=None, ge=1, le=3600)
    farmer_approved: bool = True

# ============================================================================
# GROUND TRUTH MODELS
# ============================================================================

class ForecastSnapshot(BaseModel):
    id: int
    farm_id: int
    issue_time: datetime
    valid_time: datetime
    lead_hours: int
    temperature: Optional[float]
    precipitation: Optional[float]
    humidity: Optional[float]

class ForecastErrorMetrics(BaseModel):
    temperature_mae: Optional[float] = None  # Mean Absolute Error (°C)
    temperature_bias: Optional[float] = None  # Mean signed error (°C)
    precipitation_mae: Optional[float] = None  # mm
    observation_count: int
    forecast_source: str = "Open-Meteo"

class GroundTruthComparison(BaseModel):
    date: str
    forecast_temp: Optional[float]
    observed_temp: Optional[float]
    temp_error: Optional[float]
    forecast_precip: Optional[float]
    observed_precip: Optional[float]
    lead_hours: int

# ============================================================================
# IRRIGATION EXPERIMENT MODELS
# ============================================================================

class IrrigationExperiment(BaseModel):
    id: int
    farm_id: int
    start_time: datetime
    end_time: Optional[datetime]
    initial_soil_moisture: Optional[float]
    final_soil_moisture: Optional[float]
    initial_water_level: Optional[float]
    final_water_level: Optional[float]
    temperature: Optional[float]
    humidity: Optional[float]
    recommendation: Optional[str]
    farmer_approved: bool
    valve_opened: bool
    duration_seconds: Optional[int]
    notes: Optional[str]

    class Config:
        from_attributes = True


# ============================================================================
# HARDWARE TELEMETRY MODELS
# ============================================================================

class HardwareTelemetry(BaseModel):
    """NodeMCU V3 (ESP8266) sensor telemetry payload"""
    farm_id: int
    timestamp: str  # ISO 8601 format
    temperature: Optional[float] = None  # DHT11 temperature in °C (±2°C accuracy)
    humidity: Optional[float] = None  # DHT11 humidity in % (±5% accuracy)
    soil_moisture: Optional[float] = None  # Analog sensor raw ADC value (0-1023)
    water_level: Optional[float] = None  # Digital sensor (0=low, 100=OK)
    firmware_version: Optional[str] = None
    ip_address: Optional[str] = None

class DeviceStatus(BaseModel):
    """Hardware device status"""
    device_id: str
    device_type: str
    farm_id: Optional[int]
    status: str  # online, stale, offline
    last_seen: Optional[str]
    firmware_version: Optional[str]
    ip_address: Optional[str]


# ============================================================================
# PUMP CONTROL MODELS
# ============================================================================

class PumpCommandRequest(BaseModel):
    """Request to control pump ON/OFF"""
    device_id: str
    farm_id: int
    action: str = Field(..., pattern="^(start|stop)$")
    duration_seconds: Optional[int] = Field(default=10, ge=1, le=300)  # Max 5 minutes
    
class PumpCommand(BaseModel):
    """Pump command stored in database"""
    id: int
    command_id: str
    device_id: str
    farm_id: int
    action: str
    duration_seconds: Optional[int]
    requested_at: datetime
    expires_at: datetime
    acknowledged_at: Optional[datetime]
    completed_at: Optional[datetime]
    status: str  # pending, acknowledged, completed, expired, failed
    result: Optional[str]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True

class PumpCommandAcknowledge(BaseModel):
    """NodeMCU acknowledges command receipt"""
    command_id: str
    status: str = Field(..., pattern="^(acknowledged|completed|failed)$")
    result: Optional[str] = None
    error_message: Optional[str] = None

class PumpState(BaseModel):
    """Current pump state reported by NodeMCU"""
    device_id: str
    pump_running: bool
    commissioned: bool
    fault_detected: bool
    fault_reason: Optional[str] = None
    water_level_ok: bool
    runtime_seconds: Optional[int] = None
    current_command_id: Optional[str] = None

class PumpStatus(BaseModel):
    """Complete pump status for dashboard"""
    device_id: str
    device_status: str  # online, stale, offline
    pump_state: str  # off, starting, on, stopping, fault, unknown
    commissioned: bool
    fault_reason: Optional[str]
    water_level_ok: bool
    last_command: Optional[PumpCommand]
    last_update: Optional[datetime]


# ============================================================================
# FARMER OBSERVATIONS MODELS (Phase 2)
# ============================================================================

class FarmerObservationBase(BaseModel):
    """Base model for farmer-provided observations"""
    observation_date: str  # YYYY-MM-DD format
    observation_time: Optional[str] = None  # HH:MM:SS format
    temperature: Optional[float] = Field(default=None, ge=-50, le=60)  # °C
    humidity: Optional[float] = Field(default=None, ge=0, le=100)  # %
    rainfall: Optional[float] = Field(default=None, ge=0, le=1000)  # mm
    soil_moisture_raw: Optional[int] = Field(default=None, ge=0, le=4095)  # ADC value
    soil_moisture_percent: Optional[float] = Field(default=None, ge=0, le=100)  # %
    water_level: Optional[str] = Field(default=None, pattern="^(Low|OK|Unknown)$")
    notes: Optional[str] = Field(default=None, max_length=1000)

    @field_validator('observation_date')
    @classmethod
    def validate_observation_date(cls, v):
        """Validate date format YYYY-MM-DD"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("observation_date must be in YYYY-MM-DD format")

    @field_validator('observation_time')
    @classmethod
    def validate_observation_time(cls, v):
        """Validate time format HH:MM or HH:MM:SS"""
        if v is None:
            return v
        try:
            # Try HH:MM:SS
            datetime.strptime(v, "%H:%M:%S")
            return v
        except ValueError:
            try:
                # Try HH:MM
                datetime.strptime(v, "%H:%M")
                return v + ":00"  # Add seconds
            except ValueError:
                raise ValueError("observation_time must be in HH:MM or HH:MM:SS format")

class FarmerObservationCreate(FarmerObservationBase):
    """Create single farmer observation (manual entry)"""
    farm_id: int

class FarmerObservation(FarmerObservationBase):
    """Farmer observation response"""
    id: int
    farm_id: int
    data_source: str
    uploaded_at: datetime
    upload_method: str
    validation_status: str
    validation_notes: Optional[str]

    class Config:
        from_attributes = True

class FarmerObservationCSVRow(BaseModel):
    """Single row from CSV upload"""
    row_number: int
    observation_date: str
    observation_time: Optional[str] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: Optional[float] = None
    soil_moisture_raw: Optional[int] = None
    soil_moisture_percent: Optional[float] = None
    water_level: Optional[str] = None
    notes: Optional[str] = None
    validation_status: str = "valid"  # valid, warning, error
    validation_message: Optional[str] = None

class FarmerObservationCSVPreview(BaseModel):
    """Preview of CSV upload before import"""
    filename: str
    total_rows: int
    valid_rows: int
    warning_rows: int
    error_rows: int
    preview_rows: List[FarmerObservationCSVRow]
    columns_found: List[str]
    columns_expected: List[str]

class FarmerObservationImportRequest(BaseModel):
    """Request to import previewed CSV data"""
    farm_id: int
    rows: List[FarmerObservationCSVRow]

class FarmerObservationImportResponse(BaseModel):
    """Response after importing observations"""
    farm_id: int
    total_imported: int
    skipped_errors: int
    skipped_duplicates: int
    import_summary: str
