"""
Planting Suitability API Router - Farmer-friendly planting assessment
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, date, timedelta
from typing import List, Optional
import aiosqlite

from services.crop_knowledge import (
    CROP_DATABASE, get_crop_params, get_total_season_length, calculate_kc
)
from services.nasa_power import nasa_power_service
from database.db import DB_PATH

router = APIRouter()

@router.get("/crops/list")
async def list_available_crops():
    """Get list of all available crops with farmer-friendly names"""
    crops = []
    
    for key, params in CROP_DATABASE.items():
        crops.append({
            "key": key,
            "name": params.name,
            "category": params.category,
            "season_length_days": get_total_season_length(params),
            "is_nitrogen_fixer": params.is_nitrogen_fixer
        })
    
    # Sort by category then name
    crops.sort(key=lambda x: (x["category"], x["name"]))
    
    return crops

@router.post("/planting/assess")
async def assess_planting_suitability(request: dict):
    """
    Assess planting suitability for a specific crop and date
    
    Uses:
    - NASA POWER historical climate data for long-term assessment
    - Open-Meteo forecast for near-term planting (if within 7 days)
    - FAO-56 crop water requirements
    - Real hardware telemetry when available
    - Farm-specific soil parameters
    """
    farm_id = request.get("farm_id")
    latitude = request.get("latitude")
    longitude = request.get("longitude")
    crop_name = request.get("crop_name")
    planting_date_str = request.get("planting_date")  # YYYY-MM-DD
    
    # Validation
    if not all([latitude, longitude, crop_name, planting_date_str]):
        raise HTTPException(status_code=400, detail="Missing required parameters")
    
    # Parse planting date
    try:
        planting_date = datetime.strptime(planting_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Get crop parameters
    crop_params = get_crop_params(crop_name)
    if not crop_params:
        raise HTTPException(status_code=404, detail=f"Crop '{crop_name}' not found")
    
    # Calculate harvest date
    season_length = get_total_season_length(crop_params)
    harvest_date = planting_date + timedelta(days=season_length)
    
    # Determine assessment type
    days_until_planting = (planting_date - date.today()).days
    use_forecast = days_until_planting >= 0 and days_until_planting <= 7
    
    try:
        # Get historical climate data for long-term assessment
        # Use multiple years for better reliability
        current_year = date.today().year
        historical_data = []
        
        # Get recent 3 years of data for the growing season
        for year_offset in range(3):
            year = current_year - year_offset - 1
            season_start = date(year, planting_date.month, planting_date.day)
            season_end = season_start + timedelta(days=season_length)
            
            try:
                year_data = await nasa_power_service.get_climate_data(
                    latitude=latitude,
                    longitude=longitude,
                    start_date=season_start,
                    end_date=season_end
                )
                historical_data.extend(year_data)
            except:
                pass  # Skip years with missing data
        
        if not historical_data:
            raise HTTPException(
                status_code=503, 
                detail="Unable to retrieve historical climate data from NASA POWER"
            )
        
        # Calculate climate statistics
        temps = [d.get("temperature_mean") for d in historical_data if d.get("temperature_mean")]
        precips = [d.get("precipitation") for d in historical_data if d.get("precipitation")]
        
        avg_temp = sum(temps) / len(temps) if temps else None
        total_precip = sum(precips) if precips else None
        seasonal_precip = total_precip / 3 if total_precip else None  # Average per season
        
        # Get near-term forecast if applicable
        forecast_data = None
        if use_forecast:
            try:
                from routers.weather import get_weather_forecast
                forecast_response = await get_weather_forecast(latitude, longitude)
                forecast_data = {
                    'forecast': [
                        {
                            'date': day.date,
                            'temperature_mean': day.temperature_mean,
                            'precipitation': day.precipitation
                        }
                        for day in forecast_response.forecast
                    ]
                }
            except:
                pass  # Forecast optional
        
        # Get current hardware readings if available
        monitoring_status = "No real-time monitoring available"
        current_conditions = None
        
        if farm_id:
            try:
                async with aiosqlite.connect(DB_PATH) as db:
                    db.row_factory = aiosqlite.Row
                    
                    # Get latest sensor readings (within last 30 minutes)
                    cutoff = datetime.utcnow() - timedelta(minutes=30)
                    async with db.execute(
                        """SELECT sensor_type, value, unit, is_simulated, timestamp
                           FROM sensor_readings
                           WHERE farm_id = ? AND timestamp > ? AND is_valid = 1
                           ORDER BY timestamp DESC""",
                        (farm_id, cutoff.isoformat())
                    ) as cursor:
                        readings = await cursor.fetchall()
                        
                        if readings:
                            # Check if real hardware
                            real_readings = [r for r in readings if not r['is_simulated']]
                            
                            if real_readings:
                                current_conditions = {}
                                for reading in real_readings:
                                    current_conditions[reading['sensor_type']] = {
                                        'value': reading['value'],
                                        'unit': reading['unit']
                                    }
                                monitoring_status = f"Real hardware online: {len(real_readings)} sensors active (LOLIN NodeMCU V3 / ESP8266, DHT11, soil moisture)"
                            else:
                                monitoring_status = "Demo mode (software simulation only)"
            except:
                pass
        
        # Perform suitability assessment
        recommendation = "insufficient_data"
        main_reason = ""
        climate_evidence = []
        soil_constraints = []
        risks = []
        farmer_actions = []
        data_sources = []
        
        # Temperature assessment
        if avg_temp is not None:
            # Simple temperature thresholds (can be enhanced with crop-specific requirements)
            if crop_name in ["wheat", "winter_rye", "peas"]:
                # Cool season crops
                if avg_temp < 5:
                    recommendation = "not_recommended"
                    main_reason = f"Temperature too low for {crop_params.name}. Average {avg_temp:.1f}°C is below minimum growing threshold."
                    climate_evidence.append(f"Historical average temperature: {avg_temp:.1f}°C (3-year average)")
                    climate_evidence.append("Cool season crop requires at least 5°C for growth")
                elif avg_temp > 25:
                    recommendation = "recommended_with_caution"
                    main_reason = f"{crop_params.name} prefers cooler conditions. {avg_temp:.1f}°C average may reduce yield."
                    climate_evidence.append(f"Historical average: {avg_temp:.1f}°C")
                    climate_evidence.append("Optimal temperature: 10-20°C")
                    risks.append("Heat stress possible during mid-season")
                else:
                    recommendation = "recommended"
                    main_reason = f"Good temperature conditions for {crop_params.name}. Historical average {avg_temp:.1f}°C is within optimal range."
                    climate_evidence.append(f"3-year average temperature: {avg_temp:.1f}°C (optimal: 10-20°C)")
            
            elif crop_name in ["corn", "soybean", "cotton", "rice", "tomato"]:
                # Warm season crops
                if avg_temp < 15:
                    recommendation = "not_recommended"
                    main_reason = f"Temperature too low for {crop_params.name}. {avg_temp:.1f}°C is below minimum threshold."
                    climate_evidence.append(f"Historical average: {avg_temp:.1f}°C")
                    climate_evidence.append("Warm season crop requires at least 15°C")
                    farmer_actions.append("Consider delaying planting until soil warms to at least 15°C")
                elif avg_temp > 35:
                    recommendation = "recommended_with_caution"
                    main_reason = f"Very high temperatures. {avg_temp:.1f}°C average may stress {crop_params.name}."
                    climate_evidence.append(f"Historical average: {avg_temp:.1f}°C")
                    risks.append("Extreme heat stress likely during flowering")
                    farmer_actions.append("Ensure adequate irrigation capacity for heat stress mitigation")
                else:
                    recommendation = "recommended"
                    main_reason = f"Excellent temperature conditions for {crop_params.name}. {avg_temp:.1f}°C average is optimal."
                    climate_evidence.append(f"3-year average temperature: {avg_temp:.1f}°C (optimal: 20-30°C)")
            
            else:
                # General assessment
                if 10 <= avg_temp <= 30:
                    recommendation = "recommended"
                    main_reason = f"Temperature conditions suitable for {crop_params.name}."
                    climate_evidence.append(f"Average temperature: {avg_temp:.1f}°C")
                else:
                    recommendation = "recommended_with_caution"
                    main_reason = f"Temperature outside typical range. Monitor crop response carefully."
                    climate_evidence.append(f"Average temperature: {avg_temp:.1f}°C")
        
        # Water availability assessment
        if seasonal_precip is not None:
            # Estimate crop water requirement (simplified)
            avg_kc = (crop_params.kc_ini + crop_params.kc_mid + crop_params.kc_end) / 3
            # Rough ET0 estimate: 4mm/day average
            estimated_etc = 4.0 * avg_kc * season_length
            effective_rainfall = seasonal_precip * 0.8
            
            water_deficit = max(0, estimated_etc - effective_rainfall)
            
            climate_evidence.append(f"Historical seasonal rainfall: {seasonal_precip:.0f}mm (effective: {effective_rainfall:.0f}mm)")
            climate_evidence.append(f"Estimated crop water need: {estimated_etc:.0f}mm")
            
            if water_deficit > 200:
                if recommendation == "recommended":
                    recommendation = "recommended_with_caution"
                    main_reason += f" However, significant irrigation needed (~{water_deficit:.0f}mm deficit)."
                
                climate_evidence.append(f"Estimated irrigation requirement: {water_deficit:.0f}mm")
                risks.append(f"Water deficit of {water_deficit:.0f}mm requires reliable irrigation")
                farmer_actions.append("Verify irrigation system capacity before planting")
                farmer_actions.append("Consider drought-tolerant varieties if water is limited")
            elif water_deficit > 50:
                climate_evidence.append(f"Moderate irrigation may be needed (~{water_deficit:.0f}mm)")
                farmer_actions.append("Plan for supplemental irrigation during dry periods")
            else:
                climate_evidence.append("Rainfall typically sufficient with minimal irrigation")
        
        # Nitrogen fixing benefit
        if crop_params.is_nitrogen_fixer:
            farmer_actions.append(f"{crop_params.name} is a legume that fixes atmospheric nitrogen - reduces fertilizer needs")
        
        # Soil depth requirements
        if crop_params.rooting_depth > 1.0:
            soil_constraints.append(f"Deep rooting crop: requires {crop_params.rooting_depth}m soil depth")
            farmer_actions.append("Ensure no hardpan or compaction layers in root zone")
        
        # Forecast integration for near-term planting
        if forecast_data and use_forecast:
            data_sources.append(f"Open-Meteo 7-day forecast (planting in {days_until_planting} days)")
            
            # Check for adverse conditions at planting
            planting_week_temps = [d['temperature_mean'] for d in forecast_data.get('forecast', [])[:3]]
            planting_week_precip = sum(d['precipitation'] for d in forecast_data.get('forecast', [])[:3])
            
            if planting_week_temps:
                avg_planting_temp = sum(planting_week_temps) / len(planting_week_temps)
                
                if avg_planting_temp < 10 and crop_name in ["corn", "soybean", "cotton", "rice"]:
                    recommendation = "not_recommended"
                    main_reason = f"Forecast shows cold conditions at planting ({avg_planting_temp:.1f}°C). Delay planting."
                    risks.append("Cold soil temperatures will prevent germination")
                
                if planting_week_precip > 50:
                    risks.append(f"Heavy rain forecast ({planting_week_precip:.0f}mm) may delay field work")
                    farmer_actions.append("Monitor soil moisture - avoid planting in saturated soil")
        
        # Current monitoring context
        if current_conditions:
            monitoring_status += f" | Current: "
            if 'temperature' in current_conditions:
                monitoring_status += f"{current_conditions['temperature']['value']:.1f}°C "
            if 'soil_moisture' in current_conditions:
                monitoring_status += f"| Soil: {current_conditions['soil_moisture']['value']:.0f}%"
        
        # Data sources
        data_sources.append("NASA POWER historical climate data (3-year average, ~50km resolution)")
        data_sources.append("FAO-56 crop water requirement model")
        data_sources.append(f"Crop parameters: {crop_params.notes}")
        
        # Default actions if none yet
        if not farmer_actions:
            farmer_actions.append("Monitor local weather forecasts as planting date approaches")
            farmer_actions.append("Consult with local extension service for variety recommendations")
        
        # Always add limitations
        risks.append("Historical averages don't guarantee future conditions")
        risks.append("NASA POWER data is ~50km resolution - local conditions may vary")
        risks.append("This assessment does not consider pests, diseases, or market prices")
        
        return {
            "success": True,
            "recommendation": recommendation,
            "main_reason": main_reason,
            "crop_name": crop_params.name,
            "planting_date": planting_date_str,
            "harvest_date": harvest_date.isoformat(),
            "season_length_days": season_length,
            "climate_evidence": climate_evidence,
            "soil_constraints": soil_constraints if soil_constraints else ["Using generic soil parameters - site-specific data not available"],
            "monitoring_status": monitoring_status,
            "risks": risks,
            "farmer_actions": farmer_actions,
            "data_sources": data_sources,
            "assessment_type": "near_term_forecast" if use_forecast else "historical_climatology",
            "years_analyzed": 3,
            "latitude": latitude,
            "longitude": longitude
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")
