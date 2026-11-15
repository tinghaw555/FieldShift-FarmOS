"""
Weather Forecast API Router - Open-Meteo integration
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import httpx

from models.schemas import WeatherForecastResponse, WeatherForecastDay

router = APIRouter()

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

@router.get("/forecast/{latitude}/{longitude}", response_model=WeatherForecastResponse)
async def get_weather_forecast(latitude: float, longitude: float):
    """
    Get 7-day weather forecast from Open-Meteo
    
    Source: https://open-meteo.com/en/docs
    License: CC BY 4.0
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,relative_humidity_2m_mean,wind_speed_10m_max",
        "timezone": "auto",
        "forecast_days": 7
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(OPEN_METEO_URL, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Parse response
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        
        forecast_days = []
        for i, date_str in enumerate(dates):
            temp_max = daily.get("temperature_2m_max", [])[i]
            temp_min = daily.get("temperature_2m_min", [])[i]
            temp_mean = (temp_max + temp_min) / 2
            
            forecast_days.append(WeatherForecastDay(
                date=date_str,
                temperature_max=temp_max,
                temperature_min=temp_min,
                temperature_mean=temp_mean,
                precipitation=daily.get("precipitation_sum", [])[i],
                precipitation_probability=daily.get("precipitation_probability_max", [])[i],
                humidity=daily.get("relative_humidity_2m_mean", [])[i],
                wind_speed=daily.get("wind_speed_10m_max", [])[i]
            ))
        
        return WeatherForecastResponse(
            source="Open-Meteo",
            latitude=latitude,
            longitude=longitude,
            issue_time=datetime.now(),
            forecast=forecast_days
        )
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Open-Meteo API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching forecast: {str(e)}")
