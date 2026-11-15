"""
Daily Crop Water Balance Model - FAO-56 Methodology

Reference: Allen, R.G., Pereira, L.S., Raes, D., Smith, M. (1998). 
Crop evapotranspiration - Guidelines for computing crop water requirements. 
FAO Irrigation and Drainage Paper 56.

This module implements:
1. FAO-56 Penman-Monteith reference evapotranspiration (ET0)
2. Crop coefficient method (ETc = Kc × ET0)
3. Daily soil water balance accounting
4. Water stress detection
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import date, timedelta
from dataclasses import dataclass

from services.crop_knowledge import CropParameters, calculate_kc

@dataclass
class SoilParameters:
    """Soil water holding parameters"""
    field_capacity: float  # volumetric (m³/m³)
    wilting_point: float  # volumetric (m³/m³)
    depth: float  # meters
    
    @property
    def taw(self) -> float:
        """Total Available Water (mm)"""
        return (self.field_capacity - self.wilting_point) * self.depth * 1000

@dataclass
class DailyWeather:
    """Daily weather data for ET0 calculation"""
    date: date
    temp_mean: float  # °C
    temp_max: float  # °C
    temp_min: float  # °C
    solar_radiation: float  # MJ/m²/day
    wind_speed: float  # m/s at 2m
    humidity_mean: Optional[float] = None  # % or None
    humidity_max: Optional[float] = None  # %
    humidity_min: Optional[float] = None  # %

@dataclass
class WaterBalanceDay:
    """Daily water balance result"""
    date: date
    dap: int  # Days after planting
    kc: float
    et0: float  # mm
    etc: float  # mm
    precipitation: float  # mm
    irrigation: float  # mm
    soil_water: float  # mm
    taw: float  # mm
    raw: float  # mm (readily available water threshold)
    drainage: float  # mm
    water_stress: bool

# ============================================================================
# REFERENCE EVAPOTRANSPIRATION (ET0) - FAO-56 Penman-Monteith
# ============================================================================

def calculate_et0_fao56(weather: DailyWeather, latitude: float, elevation: float = 100) -> float:
    """
    Calculate reference evapotranspiration using FAO-56 Penman-Monteith
    
    Args:
        weather: Daily weather data
        latitude: Latitude in degrees
        elevation: Elevation in meters (affects atmospheric pressure)
    
    Returns:
        ET0 in mm/day
    
    Reference: FAO-56 Equation 6 (full form)
    """
    # Constants
    SOLAR_CONSTANT = 0.0820  # MJ/m²/min
    STEFAN_BOLTZMANN = 4.903e-9  # MJ/K⁴/m²/day
    
    # Calculate saturation vapor pressure (es)
    es_tmax = 0.6108 * np.exp((17.27 * weather.temp_max) / (weather.temp_max + 237.3))
    es_tmin = 0.6108 * np.exp((17.27 * weather.temp_min) / (weather.temp_min + 237.3))
    es = (es_tmax + es_tmin) / 2  # kPa
    
    # Actual vapor pressure (ea)
    if weather.humidity_mean is not None:
        ea = es * (weather.humidity_mean / 100)
    elif weather.humidity_max is not None and weather.humidity_min is not None:
        ea_tmax = es_tmin * (weather.humidity_max / 100)
        ea_tmin = es_tmax * (weather.humidity_min / 100)
        ea = (ea_tmax + ea_tmin) / 2
    else:
        # Estimate from minimum temperature (FAO-56 Eq. 48)
        ea = 0.6108 * np.exp((17.27 * weather.temp_min) / (weather.temp_min + 237.3))
    
    # Slope of saturation vapor pressure curve (Δ) - FAO-56 Eq. 13
    delta = (4098 * (0.6108 * np.exp((17.27 * weather.temp_mean) / (weather.temp_mean + 237.3)))) / ((weather.temp_mean + 237.3) ** 2)
    
    # Atmospheric pressure (P) - FAO-56 Eq. 7
    P = 101.3 * ((293 - 0.0065 * elevation) / 293) ** 5.26  # kPa
    
    # Psychrometric constant (γ) - FAO-56 Eq. 8
    gamma = 0.000665 * P  # kPa/°C
    
    # Net radiation (Rn)
    # For simplicity, assuming provided solar_radiation is shortwave
    # Net shortwave radiation: Rns = (1 - albedo) * Rs
    # Albedo for grass reference = 0.23
    Rns = 0.77 * weather.solar_radiation  # MJ/m²/day
    
    # Net longwave radiation (Rnl) - FAO-56 Eq. 39
    # Simplified calculation
    Rnl = STEFAN_BOLTZMANN * (
        ((weather.temp_max + 273.16)**4 + (weather.temp_min + 273.16)**4) / 2
    ) * (0.34 - 0.14 * np.sqrt(ea)) * 1.0  # Assuming cloudiness factor = 1.0
    
    Rn = Rns - Rnl  # MJ/m²/day
    
    # Soil heat flux (G) - FAO-56 Eq. 42
    # For daily calculations, G ≈ 0
    G = 0
    
    # FAO-56 Penman-Monteith equation (Eq. 6)
    # ET0 = [0.408 Δ (Rn - G) + γ (900/(T+273)) u2 (es - ea)] / [Δ + γ (1 + 0.34 u2)]
    
    numerator = (0.408 * delta * (Rn - G) + 
                 gamma * (900 / (weather.temp_mean + 273)) * weather.wind_speed * (es - ea))
    denominator = delta + gamma * (1 + 0.34 * weather.wind_speed)
    
    et0 = numerator / denominator
    
    # Ensure non-negative
    return max(0, et0)

def calculate_et0_hargreaves(weather: DailyWeather, latitude: float) -> float:
    """
    Calculate ET0 using Hargreaves method (temperature-based)
    
    Fallback when wind speed or humidity data is unavailable
    Less accurate than Penman-Monteith but more robust
    
    Reference: Hargreaves and Samani (1985)
    """
    # Extraterrestrial radiation (Ra) calculation would go here
    # Simplified: assume Ra based on latitude and day of year
    # For now, use a simplified version
    
    TD = weather.temp_max - weather.temp_min
    
    # Hargreaves equation (simplified)
    et0 = 0.0023 * (weather.temp_mean + 17.8) * (TD ** 0.5) * weather.solar_radiation
    
    return max(0, et0)

# ============================================================================
# CROP EVAPOTRANSPIRATION
# ============================================================================

def calculate_etc(et0: float, kc: float) -> float:
    """
    Calculate crop evapotranspiration
    
    ETc = Kc × ET0 (FAO-56 Eq. 56)
    """
    return et0 * kc

# ============================================================================
# SOIL WATER BALANCE
# ============================================================================

class WaterBalanceModel:
    """Daily soil water balance model"""
    
    def __init__(
        self,
        soil: SoilParameters,
        crop: CropParameters,
        planting_date: date,
        harvest_date: date,
        initial_soil_water: Optional[float] = None,
        irrigation_schedule: Optional[Dict[date, float]] = None
    ):
        self.soil = soil
        self.crop = crop
        self.planting_date = planting_date
        self.harvest_date = harvest_date
        self.irrigation_schedule = irrigation_schedule or {}
        
        # Initial soil water (mm)
        if initial_soil_water is not None:
            self.initial_sw = initial_soil_water
        else:
            # Assume field capacity
            self.initial_sw = soil.taw
    
    def simulate(
        self,
        weather_data: List[DailyWeather],
        precipitation_data: Dict[date, float],  # mm
        latitude: float,
        effective_rainfall_fraction: float = 0.80
    ) -> List[WaterBalanceDay]:
        """
        Run daily water balance simulation
        
        Args:
            weather_data: Daily weather observations
            precipitation_data: Dictionary mapping dates to precipitation (mm)
            latitude: Latitude for ET0 calculation
            effective_rainfall_fraction: Fraction of rainfall that infiltrates (0-1)
        
        Returns:
            List of daily water balance results
        """
        results = []
        soil_water = self.initial_sw  # Current soil water content (mm)
        
        # Calculate RAW (Readily Available Water threshold)
        raw = self.crop.depletion_fraction * self.soil.taw
        
        for weather in weather_data:
            current_date = weather.date
            
            # Skip dates outside growing season
            if current_date < self.planting_date or current_date > self.harvest_date:
                continue
            
            # Days after planting
            dap = (current_date - self.planting_date).days
            
            # Crop coefficient for this day
            kc = calculate_kc(self.crop, dap)
            
            # Reference ET
            try:
                et0 = calculate_et0_fao56(weather, latitude)
            except Exception:
                # Fallback to Hargreaves if Penman-Monteith fails
                et0 = calculate_et0_hargreaves(weather, latitude)
            
            # Crop ET
            etc = calculate_etc(et0, kc)
            
            # Precipitation (effective)
            precip = precipitation_data.get(current_date, 0.0)
            precip_effective = precip * effective_rainfall_fraction
            
            # Irrigation
            irrigation = self.irrigation_schedule.get(current_date, 0.0)
            
            # Water inputs
            water_in = precip_effective + irrigation
            
            # Water outputs
            water_out = etc
            
            # Update soil water
            soil_water = soil_water + water_in - water_out
            
            # Drainage (water above field capacity drains)
            drainage = 0.0
            if soil_water > self.soil.taw:
                drainage = soil_water - self.soil.taw
                soil_water = self.soil.taw
            
            # Ensure non-negative soil water
            soil_water = max(0, soil_water)
            
            # Water stress check
            water_stress = soil_water < raw
            
            # Store result
            results.append(WaterBalanceDay(
                date=current_date,
                dap=dap,
                kc=kc,
                et0=et0,
                etc=etc,
                precipitation=precip,
                irrigation=irrigation,
                soil_water=soil_water,
                taw=self.soil.taw,
                raw=raw,
                drainage=drainage,
                water_stress=water_stress
            ))
        
        return results
    
    def calculate_irrigation_requirement(
        self,
        weather_data: List[DailyWeather],
        precipitation_data: Dict[date, float],
        latitude: float,
        effective_rainfall_fraction: float = 0.80,
        target_stress_days: int = 0
    ) -> Tuple[float, Dict[date, float]]:
        """
        Calculate irrigation needed to achieve target stress days
        
        Uses iterative simulation to determine irrigation schedule
        
        Returns:
            Tuple of (total_irrigation_mm, irrigation_schedule)
        """
        # First simulate with no irrigation to see baseline stress
        baseline = self.simulate(weather_data, precipitation_data, latitude, effective_rainfall_fraction)
        baseline_stress = sum(1 for day in baseline if day.water_stress)
        
        if baseline_stress <= target_stress_days:
            return 0.0, {}
        
        # Simple strategy: irrigate when soil water drops below RAW
        irrigation_schedule = {}
        soil_water = self.initial_sw
        raw = self.crop.depletion_fraction * self.soil.taw
        irrigation_amount = 20.0  # mm per irrigation event
        
        for weather in weather_data:
            current_date = weather.date
            
            if current_date < self.planting_date or current_date > self.harvest_date:
                continue
            
            dap = (current_date - self.planting_date).days
            kc = calculate_kc(self.crop, dap)
            
            try:
                et0 = calculate_et0_fao56(weather, latitude)
            except Exception:
                et0 = calculate_et0_hargreaves(weather, latitude)
            
            etc = calculate_etc(et0, kc)
            precip = precipitation_data.get(current_date, 0.0) * effective_rainfall_fraction
            
            # Check if irrigation needed
            if soil_water < raw:
                irrigation_schedule[current_date] = irrigation_amount
                soil_water += irrigation_amount
            
            # Update soil water
            soil_water = soil_water + precip - etc
            
            # Drainage
            if soil_water > self.soil.taw:
                soil_water = self.soil.taw
            
            soil_water = max(0, soil_water)
        
        total_irrigation = sum(irrigation_schedule.values())
        return total_irrigation, irrigation_schedule

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def summarize_water_balance(results: List[WaterBalanceDay]) -> Dict:
    """Generate summary statistics from water balance simulation"""
    if not results:
        return {}
    
    return {
        "total_etc": sum(r.etc for r in results),
        "total_precipitation": sum(r.precipitation for r in results),
        "total_irrigation": sum(r.irrigation for r in results),
        "stress_days": sum(1 for r in results if r.water_stress),
        "mean_soil_water": np.mean([r.soil_water for r in results]),
        "min_soil_water": min(r.soil_water for r in results),
        "season_length_days": len(results),
    }
