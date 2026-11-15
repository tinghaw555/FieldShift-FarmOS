# Irrigation Integration Quick Start Guide

**Test the complete farmer irrigation input → FlipPoint calculation flow**

---

## Prerequisites

1. **Backend Running**
   ```bash
   cd backend
   python main.py
   # Should be running at http://localhost:8000
   ```

2. **Frontend Running**
   ```bash
   cd frontend
   npm run dev
   # Should be running at http://localhost:3000
   ```

3. **Database Initialized**
   - Farm created with GPS coordinates
   - At least 2 crop rotations configured

---

## Test Flow

### Step 1: Create a Farm (if needed)

**Via UI**: Dashboard → Add New Farm
- Name: "Test Farm"
- Location: Click map or use "Use My Location"
- Submit

**Via API**:
```bash
curl -X POST http://localhost:8000/api/farms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Farm",
    "latitude": 40.0,
    "longitude": -95.0
  }'
```

### Step 2: Create Crop Rotations

**You need at least 2 rotations to see FlipPoint**

**Example: Current Rotation (Corn-Soybean)**
```bash
curl -X POST http://localhost:8000/api/rotations \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": 1,
    "rotation_type": "current",
    "name": "Corn-Soybean (Traditional)",
    "crops": [
      {
        "crop_name": "corn",
        "planting_date": "05-01",
        "harvest_date": "10-15",
        "sequence_order": 1
      },
      {
        "crop_name": "soybean",
        "planting_date": "05-15",
        "harvest_date": "10-30",
        "sequence_order": 2
      }
    ]
  }'
```

**Example: Alternative Rotation (Wheat-Dry Beans)**
```bash
curl -X POST http://localhost:8000/api/rotations \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": 1,
    "rotation_type": "alternative",
    "name": "Wheat-Dry Beans (Low Water)",
    "crops": [
      {
        "crop_name": "wheat",
        "planting_date": "04-01",
        "harvest_date": "07-31",
        "sequence_order": 1
      },
      {
        "crop_name": "dry_beans",
        "planting_date": "05-20",
        "harvest_date": "09-15",
        "sequence_order": 2
      }
    ]
  }'
```

### Step 3: Test Farmer-Friendly Irrigation Inputs

**Navigate to**: "What If Conditions Change?" section

#### Test Case 1: Bucket Watering
1. **Select watering method**: "Bucket or Watering Can"
2. **Set field area**: 1000 m²
3. **Enter bucket details**:
   - Bucket size: 10 litres
   - Buckets per day: 5
   - Watering days/week: 3
4. **Set efficiency**: 60%
5. **Observe**:
   - Weekly water: 150 litres
   - Effective irrigation: 0.09 mm/week
   - Backend update indicator appears briefly

#### Test Case 2: Pump System
1. **Change method to**: "Pump or Irrigation System"
2. **Click**: "How to measure flow?" (read guide)
3. **Enter pump details**:
   - Flow rate: 20 L/min (measured)
   - Minutes per day: 30
   - Watering days/week: 3
4. **Set efficiency**: 85%
5. **Observe**:
   - Weekly water: 1800 litres
   - Effective irrigation: 0.153 mm/week

#### Test Case 3: Rainwater Only
1. **Select**: "Rainwater Only"
2. **Observe**:
   - Weekly water: Rainwater Only
   - Message: "Your crop rotation will depend entirely on rainfall"

### Step 4: Calculate FlipPoint

1. **Click**: "Calculate FlipPoint Threshold" button
2. **Wait**: 5-10 seconds (backend processing)
3. **Observe Results**:
   - Current preferred rotation displayed
   - FlipPoint threshold shown (if exists)
   - Farmer-friendly explanation with litres/week

**Expected Result with Example Rotations**:
```
At Your Current Water Supply:
ALTERNATIVE (Wheat-Dry Beans)

FlipPoint Detected!
Threshold: 45.2 mm/week

When your irrigation capacity increases above this threshold,
the optimal rotation switches from alternative to current.

To reach this threshold, you would need:
45,200 litres/week
Across your 1000 m² at 85% efficiency
```

### Step 5: Verify Backend Update

**Check farm irrigation capacity was updated**:
```bash
curl http://localhost:8000/api/farms/1
```

**Expected response includes**:
```json
{
  "config": {
    "irrigation_capacity": 0.0219,  // mm/day (0.153 mm/week ÷ 7)
    "irrigation_available": true,
    ...
  }
}
```

### Step 6: Test Rotation Comparison

**Compare rotations with irrigation capacity**:
```bash
curl -X POST http://localhost:8000/api/rotations/compare \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": 1,
    "latitude": 40.0,
    "longitude": -95.0,
    "year": 2023,
    "rotations": {
      "current": [
        {"crop": "corn", "planting": "05-01", "harvest": "10-15"},
        {"crop": "soybean", "planting": "05-15", "harvest": "10-30"}
      ],
      "alternative": [
        {"crop": "wheat", "planting": "04-01", "harvest": "07-31"},
        {"crop": "dry_beans", "planting": "05-20", "harvest": "09-15"}
      ]
    }
  }'
```

**Expected response includes**:
```json
{
  "irrigation_capacity_mm_day": 0.0219,
  "results": {
    "current": {
      "total_stress_days": 45,
      "irrigation_deficit_mm": 250.5,
      "feasible": false
    },
    "alternative": {
      "total_stress_days": 15,
      "irrigation_deficit_mm": 0,
      "feasible": true
    }
  },
  "comparison": {
    "preferred_rotation": "alternative",
    "preferred_reason": "Lowest estimated water stress days (15)"
  }
}
```

---

## Troubleshooting

### FlipPoint Button Disabled
**Cause**: Watering method is "Not Sure / Not Measured"
**Solution**: Select bucket, pump, or rainwater method

### Error: "At least 2 rotations required"
**Cause**: Farm has 0 or 1 rotations configured
**Solution**: Create rotations via "Compare Crop Rotations" section or API

### Error: "Farm location required"
**Cause**: Farm doesn't have GPS coordinates
**Solution**: Edit farm and set latitude/longitude

### FlipPoint Calculation Takes Too Long
**Cause**: Backend may be slow on first NASA POWER API call (cold start)
**Solution**: Wait up to 30 seconds for first calculation, subsequent calls are faster

### No FlipPoint Detected
**Cause**: One rotation dominates across entire irrigation range
**Solution**: This is valid! Message explains rotation is stable
**Example**: Drought-tolerant crops may be optimal from 0-100 mm/week

---

## Validation Checklist

### ✅ Irrigation Capacity Flow
- [ ] Frontend calculates mm/week from farmer inputs
- [ ] Backend receives PUT request to update irrigation capacity
- [ ] Farm config shows updated `irrigation_capacity` (mm/day)
- [ ] Previous FlipPoint results are cleared when inputs change

### ✅ FlipPoint Calculation
- [ ] Button enabled when requirements met
- [ ] Loading spinner appears during calculation
- [ ] Results display current preferred rotation
- [ ] FlipPoint threshold shown (if exists)
- [ ] Farmer-friendly litres/week conversion displayed

### ✅ Special Cases
- [ ] Rainwater only: Shows "Rainwater Only", allows FlipPoint calc
- [ ] Not sure: Disables FlipPoint, shows "measure first" message
- [ ] No rotations: Clear error "need 2+ rotations"
- [ ] No FlipPoint: Explains rotation is stable
- [ ] Unchanged ranking: Reports honestly

### ✅ Error Handling
- [ ] Missing farm location: Clear error message
- [ ] API failure: Shows error, allows retry
- [ ] Invalid inputs: Frontend validation prevents submission

---

## API Endpoints Reference

### Update Irrigation Capacity
```http
PUT /api/farms/{farm_id}/irrigation
Content-Type: application/json

{
  "irrigation_mm_week": 0.153,
  "irrigation_mm_day": 0.0219,
  "source": "calculated",
  "method": "pump",
  "weekly_litres": 1800,
  "plot_area_m2": 10000,
  "efficiency_percent": 85
}
```

### Calculate FlipPoint
```http
POST /api/rotations/flippoint
Content-Type: application/json

{
  "farm_id": 1,
  "latitude": 40.0,
  "longitude": -95.0,
  "year": 2023,
  "rotations": {
    "current": [...crops],
    "alternative": [...crops]
  },
  "parameter": "irrigation_capacity",
  "current_value": 0.153,
  "min_value": 0,
  "max_value": 100,
  "steps": 20
}
```

### Compare Rotations
```http
POST /api/rotations/compare
Content-Type: application/json

{
  "farm_id": 1,
  "latitude": 40.0,
  "longitude": -95.0,
  "year": 2023,
  "rotations": {
    "current": [...crops],
    "alternative": [...crops]
  }
}
```

---

## Expected Performance

- **Irrigation capacity update**: < 100ms
- **FlipPoint calculation**: 5-10 seconds (20 rotation comparisons)
- **Single rotation comparison**: 1-2 seconds (NASA POWER API call)
- **Frontend calculation**: Instant (pure JavaScript)

---

## Success Indicators

✅ **Integration Working** if:
1. Changing bucket/pump inputs updates backend (see loading indicator)
2. FlipPoint button enables when requirements met
3. Calculation completes in 5-10 seconds
4. Results show genuine threshold (not hardcoded)
5. Farmer can understand results (litres, not just mm)

✅ **Scientific Integrity Maintained** if:
1. FlipPoint may or may not exist (honest reporting)
2. Rotation ranking can be stable across irrigation range
3. Results cite NASA POWER and FAO-56 methodology
4. Stress days calculated from climate data, not assumptions

---

## Next Steps After Testing

1. **Create More Rotations**: Test with 3 rotations (current, small_shift, alternative)
2. **Vary Field Size**: See how litres/week changes with area
3. **Test Efficiency Range**: 30% vs 95% impact on FlipPoint
4. **Multi-Farm**: Create multiple farms, switch between them
5. **Real Hardware**: Connect NodeMCU for measured flow rate

---

## Support

**Documentation**: See `IRRIGATION_INTEGRATION_COMPLETE.md` for full technical details
**Issues**: Check browser console (F12) and backend logs for errors
**Data**: Database at `backend/database/fieldshift.db` (SQLite)
