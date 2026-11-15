"""
Unit tests for crop water balance model
"""

import pytest
from datetime import date
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.water_balance import (
    calculate_et0_fao56, calculate_etc, calculate_kc,
    SoilParameters, WaterBalanceModel, DailyWeather
)
from services.crop_knowledge import get_crop_params

class TestET0Calculation:
    """Test reference evapotranspiration calculations"""
    
    def test_et0_positive(self):
        """ET0 should always be non-negative"""
        weather = DailyWeather(
            date=date(2023, 7, 15),
            temp_mean=25.0,
            temp_max=32.0,
            temp_min=18.0,
            solar_radiation=25.0,
            wind_speed=2.0,
            humidity_mean=60.0
        )
        
        et0 = calculate_et0_fao56(weather, latitude=42.0)
        assert et0 >= 0, "ET0 must be non-negative"
        assert et0 < 20, "ET0 should be reasonable (< 20 mm/day)"
    
    def test_et0_temperature_sensitivity(self):
        """ET0 should increase with temperature"""
        weather_cool = DailyWeather(
            date=date(2023, 7, 15),
            temp_mean=15.0,
            temp_max=20.0,
            temp_min=10.0,
            solar_radiation=20.0,
            wind_speed=2.0,
            humidity_mean=60.0
        )
        
        weather_hot = DailyWeather(
            date=date(2023, 7, 15),
            temp_mean=30.0,
            temp_max=38.0,
            temp_min=22.0,
            solar_radiation=20.0,
            wind_speed=2.0,
            humidity_mean=60.0
        )
        
        et0_cool = calculate_et0_fao56(weather_cool, latitude=42.0)
        et0_hot = calculate_et0_fao56(weather_hot, latitude=42.0)
        
        assert et0_hot > et0_cool, "ET0 should be higher in hot conditions"

class TestCropCoefficient:
    """Test crop coefficient calculations"""
    
    def test_kc_corn_values(self):
        """Test Kc values for corn across growth stages"""
        corn = get_crop_params("corn")
        assert corn is not None
        
        # Initial stage
        kc_initial = calculate_kc(corn, days_after_planting=10)
        assert abs(kc_initial - corn.kc_ini) < 0.01
        
        # Mid-season
        mid_day = corn.stage_initial_days + corn.stage_development_days + 20
        kc_mid = calculate_kc(corn, mid_day)
        assert abs(kc_mid - corn.kc_mid) < 0.01
    
    def test_kc_development_interpolation(self):
        """Kc should interpolate linearly during development"""
        corn = get_crop_params("corn")
        
        # Start of development
        day_start = corn.stage_initial_days
        kc_start = calculate_kc(corn, day_start)
        
        # End of development
        day_end = corn.stage_initial_days + corn.stage_development_days
        kc_end = calculate_kc(corn, day_end)
        
        # Middle of development
        day_mid = corn.stage_initial_days + corn.stage_development_days // 2
        kc_mid = calculate_kc(corn, day_mid)
        
        # Check interpolation
        expected_mid = (kc_start + kc_end) / 2
        assert abs(kc_mid - expected_mid) < 0.1, "Kc should interpolate linearly"

class TestCropETC:
    """Test crop evapotranspiration"""
    
    def test_etc_calculation(self):
        """ETc = Kc × ET0"""
        et0 = 5.0  # mm/day
        kc = 1.2
        
        etc = calculate_etc(et0, kc)
        assert abs(etc - 6.0) < 0.01

class TestSoilParameters:
    """Test soil parameter calculations"""
    
    def test_taw_calculation(self):
        """Test Total Available Water calculation"""
        soil = SoilParameters(
            field_capacity=0.30,  # 30%
            wilting_point=0.15,   # 15%
            depth=1.0             # 1 meter
        )
        
        # TAW = (FC - WP) × depth × 1000
        # TAW = (0.30 - 0.15) × 1.0 × 1000 = 150 mm
        expected_taw = 150.0
        assert abs(soil.taw - expected_taw) < 0.1

class TestWaterBalance:
    """Test complete water balance simulation"""
    
    def test_soil_water_bounds(self):
        """Soil water should stay within physical bounds"""
        corn = get_crop_params("corn")
        soil = SoilParameters(
            field_capacity=0.30,
            wilting_point=0.15,
            depth=1.0
        )
        
        model = WaterBalanceModel(
            soil=soil,
            crop=corn,
            planting_date=date(2023, 5, 1),
            harvest_date=date(2023, 9, 15)
        )
        
        # Create simple weather data
        weather_data = []
        for day_offset in range(140):
            current_date = date(2023, 5, 1) + timedelta(days=day_offset)
            weather_data.append(DailyWeather(
                date=current_date,
                temp_mean=22.0,
                temp_max=28.0,
                temp_min=16.0,
                solar_radiation=20.0,
                wind_speed=2.0,
                humidity_mean=60.0
            ))
        
        # Precipitation data
        from datetime import timedelta
        precip_data = {
            weather.date: 5.0  # 5mm every day
            for weather in weather_data
        }
        
        # Run simulation
        results = model.simulate(
            weather_data=weather_data,
            precipitation_data=precip_data,
            latitude=42.0
        )
        
        # Check all soil water values are within bounds
        for day_result in results:
            assert day_result.soil_water >= 0, "Soil water cannot be negative"
            assert day_result.soil_water <= soil.taw + 1.0, "Soil water cannot exceed TAW significantly"
    
    def test_water_stress_detection(self):
        """Water stress should be detected when soil water is low"""
        corn = get_crop_params("corn")
        soil = SoilParameters(
            field_capacity=0.30,
            wilting_point=0.15,
            depth=1.0
        )
        
        # Start with very dry soil
        model = WaterBalanceModel(
            soil=soil,
            crop=corn,
            planting_date=date(2023, 5, 1),
            harvest_date=date(2023, 5, 30),
            initial_soil_water=30.0  # Low initial water
        )
        
        # No rain
        weather_data = [
            DailyWeather(
                date=date(2023, 5, 1),
                temp_mean=30.0,
                temp_max=35.0,
                temp_min=25.0,
                solar_radiation=25.0,
                wind_speed=3.0,
                humidity_mean=40.0
            )
        ]
        
        precip_data = {date(2023, 5, 1): 0.0}
        
        results = model.simulate(
            weather_data=weather_data,
            precipitation_data=precip_data,
            latitude=42.0
        )
        
        # Should have water stress with low soil water and no rain
        assert any(r.water_stress for r in results), "Should detect water stress"

def test_crop_knowledge_base():
    """Test crop database is accessible"""
    corn = get_crop_params("corn")
    assert corn is not None
    assert corn.kc_mid > corn.kc_ini
    assert corn.rooting_depth > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
