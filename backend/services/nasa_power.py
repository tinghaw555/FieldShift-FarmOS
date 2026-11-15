"""
NASA POWER API Integration Service

Official API: https://power.larc.nasa.gov/api/temporal/daily/point

Data Source: NASA Prediction Of Worldwide Energy Resources (POWER)
Provider: NASA Langley Research Center (LaRC)
License: NASA Open Data Policy
"""

import httpx
from typing import Optional, List, Dict
from datetime import datetime, date
import asyncio

# NASA POWER API Configuration
NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

# Parameters we need for crop water calculations
# Reference: https://power.larc.nasa.gov/docs/services/api/
REQUIRED_PARAMETERS = [
    "T2M",              # Temperature at 2 Meters (°C)
    "T2M_MAX",          # Maximum Temperature at 2 Meters (°C)
    "T2M_MIN",          # Minimum Temperature at 2 Meters (°C)
    "PRECTOTCORR",      # Precipitation Corrected (mm/day)
    "RH2M",             # Relative Humidity at 2 Meters (%)
    "WS2M",             # Wind Speed at 2 Meters (m/s)
    "ALLSKY_SFC_SW_DWN" # All Sky Surface Shortwave Downward Irradiance (MJ/m²/day)
]

class NASAPowerError(Exception):
    """Custom exception for NASA POWER API errors"""
    pass

class NASAPowerService:
    """Service for retrieving NASA POWER climate data"""
    
    def __init__(self):
        self.base_url = NASA_POWER_BASE_URL
        self.timeout = 30.0
    
    async def get_daily_data(
        self,
        latitude: float,
        longitude: float,
        start_date: str,  # YYYYMMDD
        end_date: str,    # YYYYMMDD
    ) -> Dict:
        """
        Retrieve daily climate data from NASA POWER
        
        Args:
            latitude: Latitude in decimal degrees (-90 to 90)
            longitude: Longitude in decimal degrees (-180 to 180)
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format
        
        Returns:
            Dictionary with climate data
        
        Raises:
            NASAPowerError: If API request fails
        """
        # Build query parameters
        params = {
            "parameters": ",".join(REQUIRED_PARAMETERS),
            "community": "AG",  # Agricultural community
            "longitude": longitude,
            "latitude": latitude,
            "start": start_date,
            "end": end_date,
            "format": "JSON"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Validate response
                if "parameters" not in data and "properties" not in data:
                    raise NASAPowerError("Invalid NASA POWER response format")
                
                return data
                
        except httpx.TimeoutException:
            raise NASAPowerError("NASA POWER API request timed out")
        except httpx.HTTPError as e:
            raise NASAPowerError(f"NASA POWER API request failed: {str(e)}")
        except Exception as e:
            raise NASAPowerError(f"Unexpected error accessing NASA POWER: {str(e)}")
    
    def parse_daily_data(self, raw_data: Dict) -> List[Dict]:
        """
        Parse NASA POWER response into daily records
        
        Args:
            raw_data: Raw JSON response from NASA POWER
        
        Returns:
            List of daily climate data dictionaries
        """
        # NASA POWER API has multiple response formats depending on version
        # Format 1: properties.parameter contains date-keyed dicts
        # Format 2: parameters contains metadata, times contains dates
        
        parameters = raw_data.get("parameters", {})
        times = raw_data.get("times", [])
        properties = raw_data.get("properties", {})
        
        # Try to find the actual data - check properties.parameter first (new format)
        param_data = {}
        if isinstance(properties, dict) and "parameter" in properties:
            param_data = properties["parameter"]
        elif isinstance(parameters, dict):
            # Check if parameters has numeric date keys
            first_key = list(parameters.keys())[0] if parameters else None
            if first_key and isinstance(parameters.get(first_key), dict):
                # Check for date keys
                sample_keys = list(parameters[first_key].keys())[:5]
                if sample_keys and all(k.isdigit() for k in sample_keys if isinstance(k, str)):
                    param_data = parameters
        
        if not param_data:
            return []
        
        # Extract dates from times array if available
        dates = []
        if times and isinstance(times, list):
            dates = times
        else:
            # Extract from first parameter's keys
            first_param = list(param_data.keys())[0]
            if isinstance(param_data[first_param], dict):
                dates = [k for k in param_data[first_param].keys() if isinstance(k, str) and k.isdigit() and len(k) == 8]
                dates = sorted(dates)
        
        # Build daily records
        daily_records = []
        for date_str in dates:
            # Parse date (YYYYMMDD format)
            try:
                if len(date_str) == 8 and date_str.isdigit():  # YYYYMMDD
                    year = int(date_str[:4])
                    month = int(date_str[4:6])
                    day = int(date_str[6:8])
                    formatted_date = f"{year:04d}-{month:02d}-{day:02d}"
                else:
                    continue
            except (ValueError, IndexError):
                continue
            
            # Get parameter data - handle both nested and flat structures
            t2m_data = param_data.get("T2M", {})
            t2m_max_data = param_data.get("T2M_MAX", {})
            t2m_min_data = param_data.get("T2M_MIN", {})
            precip_data = param_data.get("PRECTOTCORR", {})
            rh2m_data = param_data.get("RH2M", {})
            ws2m_data = param_data.get("WS2M", {})
            solar_data = param_data.get("ALLSKY_SFC_SW_DWN", {})
            
            record = {
                "date": formatted_date,
                "temperature_mean": t2m_data.get(date_str) if isinstance(t2m_data, dict) else None,
                "temperature_max": t2m_max_data.get(date_str) if isinstance(t2m_max_data, dict) else None,
                "temperature_min": t2m_min_data.get(date_str) if isinstance(t2m_min_data, dict) else None,
                "precipitation": precip_data.get(date_str) if isinstance(precip_data, dict) else None,
                "humidity": rh2m_data.get(date_str) if isinstance(rh2m_data, dict) else None,
                "wind_speed": ws2m_data.get(date_str) if isinstance(ws2m_data, dict) else None,
                "solar_radiation": solar_data.get(date_str) if isinstance(solar_data, dict) else None,
            }
            
            # Replace -999 (NASA's missing data flag) with None
            for key in record:
                if isinstance(record[key], (int, float)) and record[key] == -999:
                    record[key] = None
            
            daily_records.append(record)
        
        return daily_records
    
    async def get_climate_data(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """
        High-level method to get parsed climate data
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            start_date: Start date (Python date object)
            end_date: End date (Python date object)
        
        Returns:
            List of daily climate records
        """
        # Format dates for NASA POWER API (YYYYMMDD)
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        # Fetch data
        raw_data = await self.get_daily_data(latitude, longitude, start_str, end_str)
        
        # Parse and return
        parsed = self.parse_daily_data(raw_data)
        return parsed
    
    def get_metadata(self, raw_data: Dict) -> Dict:
        """Extract metadata from NASA POWER response"""
        return {
            "source": "NASA POWER",
            "geometry": raw_data.get("geometry", {}),
            "header": raw_data.get("header", {}),
            "messages": raw_data.get("messages", []),
            "time_standard": raw_data.get("header", {}).get("time_standard", "UTC"),
        }

# Global service instance
nasa_power_service = NASAPowerService()

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def get_nasa_climate(
    latitude: float,
    longitude: float,
    start_date: date,
    end_date: date
) -> tuple[List[Dict], Dict]:
    """
    Convenience function to get NASA POWER climate data
    
    Returns:
        Tuple of (daily_data, metadata)
    """
    raw_data = await nasa_power_service.get_daily_data(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d")
    )
    
    daily_data = nasa_power_service.parse_daily_data(raw_data)
    metadata = nasa_power_service.get_metadata(raw_data)
    
    return daily_data, metadata

# ============================================================================
# TEST FUNCTION
# ============================================================================

async def test_nasa_power():
    """Test NASA POWER API integration"""
    print("Testing NASA POWER API...")
    
    # Test location: Iowa, USA (corn belt)
    latitude = 42.0
    longitude = -93.5
    start = date(2023, 4, 1)
    end = date(2023, 10, 31)
    
    try:
        daily_data, metadata = await get_nasa_climate(latitude, longitude, start, end)
        
        print(f"✅ Successfully retrieved {len(daily_data)} days of data")
        print(f"   Location: {latitude}, {longitude}")
        print(f"   Period: {start} to {end}")
        print("\nSample data (first 3 days):")
        for record in daily_data[:3]:
            print(f"  {record['date']}: T={record['temperature_mean']}°C, P={record['precipitation']}mm")
        
        return True
        
    except Exception as e:
        print(f"❌ NASA POWER test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_nasa_power())
