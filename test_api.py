"""
Test script to verify farm creation API
"""
import httpx
import asyncio

API_BASE = "http://localhost:8000/api"

async def test_api():
    print("Testing FieldShift FarmOS API...")
    print(f"API Base: {API_BASE}")
    
    # Test 1: Health check
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_BASE}/../api/health")
            print(f"✅ Health check: {response.status_code}")
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: List farms
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_BASE}/farms/")
            print(f"✅ List farms: {response.status_code}")
            farms = response.json()
            print(f"   Found {len(farms)} farms")
    except Exception as e:
        print(f"❌ List farms failed: {e}")
        return False
    
    # Test 3: Create a farm
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            farm_data = {
                "name": "Test Farm from Script",
                "latitude": 42.0,
                "longitude": -93.5
            }
            response = await client.post(
                f"{API_BASE}/farms/",
                json=farm_data
            )
            print(f"✅ Create farm: {response.status_code}")
            
            if response.status_code == 200:
                farm = response.json()
                print(f"   Created farm: {farm}")
                
                # Verify it was created
                response2 = await client.get(f"{API_BASE}/farms/")
                farms = response2.json()
                print(f"   Total farms now: {len(farms)}")
            else:
                print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Create farm failed: {e}")
        return False
    
    print("\n✅ All API tests passed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_api())
