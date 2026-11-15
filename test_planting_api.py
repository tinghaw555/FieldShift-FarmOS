"""
Test script for Planting Suitability API
Tests the new farmer-friendly planting assessment workflow
"""

import requests
import json
from datetime import date, timedelta

API_BASE = "http://localhost:8000/api"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_crops_list():
    """Test listing available crops"""
    print_section("TEST 1: List Available Crops")
    
    response = requests.get(f"{API_BASE}/crops/list")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        crops = response.json()
        print(f"✓ Found {len(crops)} crops")
        
        # Show sample crops
        print("\nSample crops:")
        for crop in crops[:5]:
            print(f"  • {crop['name']} ({crop['category']}) - {crop['season_length_days']} days")
            if crop['is_nitrogen_fixer']:
                print(f"    → Nitrogen fixer")
        
        return crops
    else:
        print(f"✗ Failed: {response.text}")
        return []

def test_planting_assessment(crop_key, planting_date_str):
    """Test planting suitability assessment"""
    print_section(f"TEST 2: Assess Planting - {crop_key}")
    
    # Example farm coordinates (Iowa, USA - corn belt)
    payload = {
        "farm_id": 1,
        "latitude": 42.0308,
        "longitude": -93.6319,
        "crop_name": crop_key,
        "planting_date": planting_date_str
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{API_BASE}/planting/assess", json=payload)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n{'='*60}")
        print(f"RECOMMENDATION: {result['recommendation'].upper()}")
        print(f"{'='*60}")
        print(f"\n{result['main_reason']}")
        
        print(f"\n📊 CLIMATE EVIDENCE:")
        for evidence in result.get('climate_evidence', []):
            print(f"  • {evidence}")
        
        if result.get('soil_constraints'):
            print(f"\n🌱 SOIL CONSTRAINTS:")
            for constraint in result['soil_constraints']:
                print(f"  • {constraint}")
        
        print(f"\n📡 MONITORING: {result.get('monitoring_status', 'N/A')}")
        
        if result.get('risks'):
            print(f"\n⚠️  RISKS:")
            for risk in result['risks']:
                print(f"  • {risk}")
        
        if result.get('farmer_actions'):
            print(f"\n✅ RECOMMENDED ACTIONS:")
            for action in result['farmer_actions']:
                print(f"  • {action}")
        
        print(f"\n📚 DATA SOURCES:")
        for source in result.get('data_sources', []):
            print(f"  • {source}")
        
        print(f"\nSeason: {result['season_length_days']} days")
        print(f"Harvest: {result['harvest_date']}")
        print(f"Assessment type: {result['assessment_type']}")
        
        return result
    else:
        print(f"✗ Failed: {response.text}")
        return None

def test_near_term_planting():
    """Test near-term planting (should use forecast)"""
    print_section("TEST 3: Near-Term Planting (Next Week)")
    
    # Planting in 3 days
    planting_date = (date.today() + timedelta(days=3)).isoformat()
    
    payload = {
        "latitude": 40.7128,
        "longitude": -74.0060,  # New York
        "crop_name": "corn",
        "planting_date": planting_date
    }
    
    response = requests.post(f"{API_BASE}/planting/assess", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Assessment type: {result['assessment_type']}")
        
        if result['assessment_type'] == 'near_term_forecast':
            print("✓ Correctly using forecast data for near-term planting")
        else:
            print("⚠ Expected near_term_forecast but got historical_climatology")
        
        return True
    else:
        print(f"✗ Failed: {response.text}")
        return False

def test_different_locations():
    """Test planting assessment in different climate zones"""
    print_section("TEST 4: Different Climate Zones")
    
    locations = [
        {"name": "Iowa (Corn Belt)", "lat": 42.0308, "lon": -93.6319},
        {"name": "California (Mediterranean)", "lat": 36.7783, "lon": -119.4179},
        {"name": "Florida (Subtropical)", "lat": 28.5383, "lon": -81.3792},
        {"name": "Kenya (Tropical)", "lat": -1.2921, "lon": 36.8219},
    ]
    
    planting_date = "2024-05-15"  # Spring planting
    
    for loc in locations:
        print(f"\n--- {loc['name']} ---")
        
        payload = {
            "latitude": loc['lat'],
            "longitude": loc['lon'],
            "crop_name": "corn",
            "planting_date": planting_date
        }
        
        response = requests.post(f"{API_BASE}/planting/assess", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Recommendation: {result['recommendation']}")
            print(f"  Reason: {result['main_reason'][:100]}...")
        else:
            print(f"✗ Failed")

def test_multiple_crops():
    """Test different crop types"""
    print_section("TEST 5: Different Crop Types")
    
    crops_to_test = ["wheat", "soybean", "tomato", "clover", "rice"]
    
    for crop_key in crops_to_test:
        print(f"\n--- {crop_key.upper()} ---")
        
        payload = {
            "latitude": 42.0308,
            "longitude": -93.6319,
            "crop_name": crop_key,
            "planting_date": "2024-05-01"
        }
        
        response = requests.post(f"{API_BASE}/planting/assess", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ {result['crop_name']}: {result['recommendation']}")
            print(f"  Season: {result['season_length_days']} days")
        else:
            print(f"✗ Failed")

def main():
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║     FIELDSHIFT FARMOS - PLANTING SUITABILITY API TEST     ║
    ║                                                            ║
    ║  Testing farmer-friendly planting assessment workflow     ║
    ║  Using NASA POWER climate data + FAO-56 crop models       ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    print("Prerequisites: Backend must be running on http://localhost:8000")
    
    try:
        # Test 1: List crops
        crops = test_crops_list()
        
        if not crops:
            print("\n⚠️  Cannot continue - crops list failed")
            return
        
        # Test 2: Full planting assessment
        test_planting_assessment("corn", "2024-05-15")
        
        # Test 3: Near-term forecast
        test_near_term_planting()
        
        # Test 4: Different locations
        test_different_locations()
        
        # Test 5: Multiple crops
        test_multiple_crops()
        
        print_section("TESTS COMPLETE")
        print("\n✓ All tests executed")
        print("\nNext steps:")
        print("1. Start frontend: npm run dev (in frontend/)")
        print("2. Navigate to http://localhost:3000")
        print("3. Test the workflow:")
        print("   • Click 'Use My Location' or click on map")
        print("   • Create a farm")
        print("   • Select a crop from dropdown")
        print("   • Pick a planting date")
        print("   • Click 'Check Planting Suitability'")
        print("   • View science-based recommendation")
        print("   • Click 'Compare Other Planting Plans'")
        
    except requests.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend")
        print("Please start the backend first:")
        print("  cd backend")
        print("  python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
