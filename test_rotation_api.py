"""
Test rotation calculation endpoints with real NASA POWER data
"""
import httpx
import asyncio
import json

API_BASE = "http://localhost:8000/api"

async def test_calculate():
    print("=" * 60)
    print("TEST: Calculate Water Needs Endpoint")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_BASE}/rotations/calculate",
            json={
                "farm_id": 1,
                "latitude": 42.0,
                "longitude": -93.5,
                "year": 2023,
                "crops": [
                    {"crop": "corn", "planting": "05-01", "harvest": "10-15"}
                ]
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        result = response.json()
        
        if result.get("success"):
            print("\n✅ SUCCESS - Real NASA POWER climate data retrieved")
            print(f"\nResults:")
            print(f"  - Total seasonal water demand: {result['total_seasonal_water_demand_mm']} mm")
            print(f"  - Total stress days: {result['total_stress_days']}")
            print(f"  - Total irrigation need: {result['total_irrigation_need_mm']} mm")
            print(f"  - Data source: {result['data_source']}")
            print(f"\nCrop Results:")
            for crop in result['crop_results']:
                print(f"  {crop['crop'].upper()}:")
                print(f"    - Season length: {crop['season_length_days']} days")
                print(f"    - Water demand: {crop['seasonal_water_demand_mm']} mm")
                print(f"    - Precipitation: {crop['precipitation_mm']} mm")
        else:
            print("\n❌ FAILED")
            print(json.dumps(result, indent=2))

async def test_compare():
    print("\n" + "=" * 60)
    print("TEST: Compare 3 Crop Plans Endpoint")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_BASE}/rotations/compare",
            json={
                "farm_id": 1,
                "latitude": 42.0,
                "longitude": -93.5,
                "year": 2023,
                "rotations": {
                    "current": [{"crop": "corn", "planting": "05-01", "harvest": "10-15"}],
                    "small_shift": [{"crop": "soybean", "planting": "05-15", "harvest": "10-01"}],
                    "alternative": [
                        {"crop": "wheat", "planting": "03-15", "harvest": "07-30"},
                        {"crop": "clover", "planting": "08-01", "harvest": "11-15"}
                    ]
                }
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        result = response.json()
        
        if result.get("success"):
            print("\n✅ SUCCESS - Compared 3 rotation strategies")
            print(f"\nComparison Result:")
            print(f"  - Preferred: {result['comparison']['preferred_rotation']}")
            print(f"  - Reason: {result['comparison']['preferred_reason']}")
            print(f"\nDetailed Results:")
            for rot_type, rot_result in result['results'].items():
                if rot_result.get('feasible'):
                    print(f"\n  {rot_type.upper()}:")
                    print(f"    - Water demand: {rot_result['total_seasonal_water_demand_mm']} mm")
                    print(f"    - Stress days: {rot_result['total_stress_days']}")
                    print(f"    - Irrigation need: {rot_result['total_irrigation_need_mm']} mm")
        else:
            print("\n❌ FAILED")
            print(json.dumps(result, indent=2))

async def main():
    print("\n" + "=" * 60)
    print("FIELD SHIFT FARMOS - ROTATION API TESTS")
    print("Testing real NASA POWER integration")
    print("=" * 60)
    
    await test_calculate()
    await test_compare()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
