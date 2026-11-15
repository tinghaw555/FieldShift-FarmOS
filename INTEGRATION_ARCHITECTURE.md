# Integration Architecture Diagram

**FieldShift FarmOS: Farmer Irrigation Inputs → Backend Scientific Model**

---

## Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FARMER INPUT LAYER                              │
│                         (FlipPointSection.tsx)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  📊 Field Area Input                                                     │
│  ├─ 1000 m² or 1 hectare                                                │
│  └─ Converted to m² for calculations                                    │
│                                                                           │
│  💧 Watering Method Selection                                            │
│  ├─ Rainwater Only → irrigation = 0 mm/week                             │
│  ├─ Bucket/Can → litres = size × buckets/day × days/week               │
│  ├─ Pump System → litres = L/min × min/day × days/week                 │
│  ├─ Not Sure → FlipPoint disabled, show "measure first"                │
│  └─ Advanced → direct mm/week input                                     │
│                                                                           │
│  ⚙️ Irrigation Efficiency Slider (30-95%)                                │
│  └─ User-configurable estimate for application losses                   │
│                                                                           │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND CALCULATION LAYER                            │
│                         (JavaScript/TypeScript)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  📐 Convert to Irrigation Depth                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ weeklyLitresGross = bucketSize × bucketsPerDay × daysPerWeek   │    │
│  │                  OR flowRate × minutesPerDay × daysPerWeek     │    │
│  │                                                                 │    │
│  │ grossDepthMm = weeklyLitresGross / plotAreaM2                  │    │
│  │                                                                 │    │
│  │ effectiveDepthMm = grossDepthMm × (efficiency / 100)           │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  🔄 Auto-Update Trigger (useEffect)                                      │
│  ├─ Watches: calculatedIrrigationMm                                     │
│  ├─ Debounce: 1 second                                                  │
│  └─ Prevents: Excessive API calls                                       │
│                                                                           │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND UPDATE API                               │
│                    PUT /api/farms/{farm_id}/irrigation                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  📥 Request Body                                                         │
│  {                                                                       │
│    "irrigation_mm_week": 0.153,                                         │
│    "irrigation_mm_day": 0.0219,      ← mm/week ÷ 7                     │
│    "source": "calculated",                                              │
│    "method": "pump",                                                    │
│    "weekly_litres": 1800,                                               │
│    "plot_area_m2": 10000,                                               │
│    "efficiency_percent": 85                                             │
│  }                                                                       │
│                                                                           │
│  💾 Database Update                                                      │
│  UPDATE farm_configs                                                    │
│  SET irrigation_capacity = 0.0219  -- mm/day (effective)               │
│  WHERE farm_id = 1                                                      │
│                                                                           │
│  ✅ Response                                                             │
│  { "success": true, "message": "Updated" }                              │
│                                                                           │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                                   │
│                      (SQLite - fieldshift.db)                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  📊 Table: farm_configs                                                  │
│  ┌──────────┬────────────────────┬──────────────────────────────┐      │
│  │ farm_id  │ irrigation_capacity│ soil_type                     │      │
│  ├──────────┼────────────────────┼──────────────────────────────┤      │
│  │    1     │      0.0219        │  loam                         │      │
│  │    2     │      0.0000        │  sandy                        │      │
│  │    3     │      0.0357        │  clay                         │      │
│  └──────────┴────────────────────┴──────────────────────────────┘      │
│                                                                           │
│  📝 Value stored: mm/day (effective irrigation)                          │
│  🔍 Used by: Rotation comparison, FlipPoint calculation                 │
│                                                                           │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
                 ▼                       ▼
┌─────────────────────────────┐  ┌─────────────────────────────────────┐
│  ROTATION COMPARISON API    │  │  FLIPPOINT CALCULATION API          │
│  POST /api/rotations/compare│  │  POST /api/rotations/flippoint      │
├─────────────────────────────┤  ├─────────────────────────────────────┤
│                             │  │                                     │
│ 1️⃣ Fetch irrigation capacity │  │ 1️⃣ Fetch configured rotations      │
│    FROM farm_configs        │  │    FROM rotations table             │
│                             │  │                                     │
│ 2️⃣ For each rotation:        │  │ 2️⃣ Generate test values:           │
│    - Calculate water demand │  │    test_range = [0, 5, 10, ..., 100]│
│    - Check feasibility      │  │    (20 irrigation capacity values) │
│    - Calculate deficit      │  │                                     │
│                             │  │ 3️⃣ For each test value:             │
│ 3️⃣ Rank rotations by stress  │  │    FOR rotation IN rotations:     │
│    among feasible options   │  │      stress = calc_water_stress()  │
│                             │  │    preferred = min(stress)         │
│ 4️⃣ Return honest ranking     │  │                                     │
│    (may not change)         │  │ 4️⃣ Detect FlipPoint:                │
│                             │  │    WHERE preferred[i] != preferred[i-1]│
└──────────────┬──────────────┘  │                                     │
               │                  │ 5️⃣ Return:                          │
               │                  │    - current_preferred_rotation    │
               │                  │    - flippoint_threshold_mm_week   │
               │                  │    - has_flippoint (boolean)       │
               │                  │    - data_points (all 20 tests)    │
               │                  │                                     │
               └──────────────────┴─────────────────┬───────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      SCIENTIFIC MODEL LAYER                              │
│                   (NASA POWER + FAO-56 Water Balance)                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  🛰️ NASA POWER Climate Data API                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ For each farm location (lat, lon):                             │    │
│  │ - Daily temperature (mean, max, min) °C                        │    │
│  │ - Daily precipitation (mm)                                     │    │
│  │ - Solar radiation (MJ/m²/day)                                  │    │
│  │ - Wind speed (m/s)                                             │    │
│  │ - Relative humidity (%)                                        │    │
│  │                                                                 │    │
│  │ Data source: Satellite + ground stations                       │    │
│  │ Coverage: Global, 1981-present                                 │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  📚 FAO-56 Crop Knowledge Base                                           │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ For 19 crops (corn, wheat, soybean, etc.):                     │    │
│  │ - Crop coefficient curves (Kc_ini, Kc_mid, Kc_end)            │    │
│  │ - Growth stage lengths (days)                                  │    │
│  │ - Root depth progression (meters)                              │    │
│  │ - Depletion fraction (p) for stress detection                 │    │
│  │                                                                 │    │
│  │ Data source: FAO Irrigation & Drainage Paper 56                │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  🧮 Daily Water Balance Calculation                                      │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ FOR each day in growing season:                                │    │
│  │                                                                 │    │
│  │   1. Calculate ET0 (Penman-Monteith)                           │    │
│  │      - Uses: temp, radiation, wind, humidity                   │    │
│  │                                                                 │    │
│  │   2. Get crop coefficient Kc (stage-based)                     │    │
│  │      - Days after planting determines growth stage             │    │
│  │                                                                 │    │
│  │   3. Calculate ETc = ET0 × Kc                                  │    │
│  │      - Crop-specific water demand                              │    │
│  │                                                                 │    │
│  │   4. Water balance:                                            │    │
│  │      soil_water[t] = soil_water[t-1]                           │    │
│  │                    + precipitation[t] × 0.8  (effective)       │    │
│  │                    + irrigation[t]                             │    │
│  │                    - ETc[t]                                    │    │
│  │                                                                 │    │
│  │   5. Check drainage (if soil_water > TAW)                      │    │
│  │                                                                 │    │
│  │   6. Detect water stress (if soil_water < RAW)                 │    │
│  │      - RAW = depletion_fraction × TAW                          │    │
│  │                                                                 │    │
│  │   7. Count stress days                                         │    │
│  │                                                                 │    │
│  │ RETURN: total_stress_days, irrigation_need_mm                  │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  🎯 FlipPoint Detection Algorithm                                        │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ test_values = linspace(0, 100, 20)  // mm/week                 │    │
│  │                                                                 │    │
│  │ FOR test_mm_week IN test_values:                               │    │
│  │   FOR rotation IN [current, small_shift, alternative]:         │    │
│  │     seasonal_irrigation = test_mm_week × 26 weeks              │    │
│  │     stress = calculate_water_balance(rotation, seasonal_irrig) │    │
│  │     scores[rotation] = stress_days                             │    │
│  │                                                                 │    │
│  │   preferred[test_mm_week] = min(scores)                        │    │
│  │                                                                 │    │
│  │ // Detect threshold where preference changes                   │    │
│  │ FOR i in range(1, 20):                                         │    │
│  │   IF preferred[i] != preferred[i-1]:                           │    │
│  │     flippoint = (test_values[i-1] + test_values[i]) / 2       │    │
│  │     RETURN flippoint                                           │    │
│  │                                                                 │    │
│  │ // No FlipPoint if preference stable across entire range       │    │
│  │ RETURN null                                                    │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                           │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND DISPLAY LAYER                              │
│                         (FlipPointSection.tsx)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  🎨 FlipPoint Results Display                                            │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ IF flipPointResult.success:                                     │    │
│  │                                                                 │    │
│  │   📊 Current Preferred Rotation                                │    │
│  │   "ALTERNATIVE (Wheat-Dry Beans)"                              │    │
│  │   "With 0.153 mm/week irrigation capacity"                     │    │
│  │                                                                 │    │
│  │   IF has_flippoint:                                            │    │
│  │     ⚠️ FlipPoint Detected                                       │    │
│  │     "Threshold: 45.2 mm/week"                                  │    │
│  │     "To reach this threshold, you would need:"                 │    │
│  │     "45,200 litres/week"                                       │    │
│  │     "Across your 1 hectare at 85% efficiency"                  │    │
│  │                                                                 │    │
│  │   ELSE:                                                        │    │
│  │     ✅ No FlipPoint Detected                                    │    │
│  │     "Your preferred rotation remains optimal"                  │    │
│  │     "across the tested irrigation range"                       │    │
│  │                                                                 │    │
│  │   ⏱️ Last Updated: "Calculated just now"                        │    │
│  │                                                                 │    │
│  │ ELSE:                                                          │    │
│  │   🔵 Call to Action                                             │    │
│  │   [Calculate FlipPoint Threshold] button                       │    │
│  │   "Requirements: 2+ rotations, GPS location, measured water"   │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  🔄 State Management                                                     │
│  ├─ isUpdatingIrrigation: Backend update in progress                    │
│  ├─ isCalculatingFlipPoint: FlipPoint API call in progress              │
│  ├─ flipPointResult: Calculated results or null                         │
│  ├─ lastCalculatedMm: Prevents redundant updates                        │
│  └─ flipPointError: Error message display                               │
│                                                                           │
│  ⚡ Real-Time Feedback                                                   │
│  ├─ Loading spinners during API calls                                   │
│  ├─ Error messages for missing requirements                             │
│  ├─ Success indicators when updates complete                            │
│  └─ Stale result invalidation when inputs change                        │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Integration Points

### 1. **Farmer Input → Effective Irrigation**
- **Location**: Frontend (FlipPointSection.tsx)
- **Calculation**: `effectiveMm = (litres / area) × (efficiency / 100)`
- **Units**: Litres/week → mm/week

### 2. **Effective Irrigation → Database**
- **Location**: Backend (PUT /farms/{id}/irrigation)
- **Storage**: `farm_configs.irrigation_capacity` (mm/day)
- **Conversion**: `mm_day = mm_week / 7`

### 3. **Database → Scientific Model**
- **Location**: Backend (rotations.py)
- **Fetched By**: FlipPoint calculation, rotation comparison
- **Used For**: Irrigation feasibility checks, water stress calculation

### 4. **Scientific Model → Results**
- **Location**: Backend (NASA POWER + FAO-56 model)
- **Calculates**: Stress days, irrigation need, preferred rotation
- **Returns**: FlipPoint threshold or "no flippoint"

### 5. **Results → Farmer Display**
- **Location**: Frontend (FlipPointSection.tsx)
- **Converts**: mm/week → litres/week for farmer's field
- **Explains**: "When you reach X litres/week, switch rotations"

---

## Data Persistence Flow

```
USER INPUT (Session)
    ↓
FRONTEND STATE (React)
    ↓
BACKEND API (REST)
    ↓
DATABASE (SQLite) ← PERSISTED
    ↓
SCIENTIFIC MODEL (Read from DB)
    ↓
RESULTS (Calculated on demand)
    ↓
FRONTEND DISPLAY (Session)
```

**Persisted**:
- ✅ Farm irrigation capacity (database)
- ✅ Crop rotations (database)
- ✅ Farm location (database)

**Session-Only**:
- ℹ️ FlipPoint results (recalculated on demand)
- ℹ️ Farmer input state (React state)
- ℹ️ UI preferences (not stored)

---

## Error Handling Flow

```
USER ACTION
    ↓
FRONTEND VALIDATION
    ├─ Missing requirements? → Show error, disable button
    ├─ Invalid inputs? → Prevent submission
    └─ Valid → Proceed
        ↓
API REQUEST
    ├─ Network error? → Show retry button
    ├─ 400 Bad Request? → Show clear error message
    ├─ 404 Not Found? → "Farm/rotation not found"
    ├─ 500 Server Error? → "Calculation failed, try again"
    └─ 200 Success → Display results
        ↓
RESULT VALIDATION
    ├─ No rotations? → "Create 2+ rotations first"
    ├─ No location? → "Add GPS coordinates"
    ├─ No flippoint? → Explain "rotation is stable"
    └─ Valid → Show FlipPoint threshold
```

---

## Performance Optimization

### Frontend
- ✅ **Debounced Updates**: 1 second delay prevents excessive API calls
- ✅ **Change Detection**: Only updates if value actually changed
- ✅ **Loading States**: User knows calculation in progress
- ✅ **Result Caching**: FlipPoint results stored until inputs change

### Backend
- ✅ **Database Indexing**: Fast irrigation capacity lookups
- ✅ **NASA POWER Caching**: Climate data cached after first request
- ✅ **Efficient Loops**: 20 test points balance accuracy vs speed
- ✅ **Early Exit**: Stop if no rotations configured

---

## Security Considerations

### Input Validation
- ✅ **Frontend**: TypeScript types, input ranges (min/max)
- ✅ **Backend**: Pydantic schemas, coordinate bounds
- ✅ **Database**: Foreign key constraints, NOT NULL checks

### Data Sanitization
- ✅ **SQL Injection**: Parameterized queries (aiosqlite)
- ✅ **Type Safety**: Pydantic validates all API inputs
- ✅ **Range Checks**: Irrigation 0-1000 mm/week, efficiency 30-95%

---

## Monitoring & Observability

### Frontend
- Console logs for API calls
- Error boundary for crash handling
- Network tab shows request/response

### Backend
- FastAPI automatic logging
- NASA POWER API call tracking
- Exception stack traces

---

## Summary

This architecture provides:

✅ **End-to-End Integration**: Farmer buckets → NASA satellites  
✅ **Scientific Integrity**: FAO-56 methodology maintained  
✅ **Honest Reporting**: Real thresholds, not hardcoded examples  
✅ **Farmer-Friendly**: Litres and clear explanations  
✅ **Performance**: Debounced updates, efficient calculations  
✅ **Reliability**: Error handling, validation, caching  
✅ **Traceability**: Every calculation documented and verifiable  

The system successfully bridges the gap between farmer-friendly inputs and rigorous scientific modeling, enabling evidence-based irrigation and crop rotation decisions.
