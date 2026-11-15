# Backend Integration Status Report

**FieldShift FarmOS - Scientific Model Connectivity**

---

## Overview

This document clarifies which calculations are genuinely connected to the backend scientific model (NASA POWER + FAO-56) versus which are UI-only conversions for farmer-friendly display.

---

## ✅ Backend-Connected (Scientific Calculations)

### 1. **NASA POWER Climate Data**
- **What**: Historical daily weather (temperature, precipitation, solar radiation, wind, humidity)
- **Where**: `services/nasa_power.py` → NASA POWER API
- **Used By**:
  - Crop water needs calculation
  - Rotation comparison
  - FlipPoint analysis
  - Planting suitability
- **Data Source**: Real satellite + ground station data from NASA
- **Status**: ✅ **FULLY INTEGRATED**

### 2. **Crop Water Needs (FAO-56 Model)**
- **What**: Daily crop evapotranspiration (ETc), water stress estimation
- **Where**: `services/water_balance.py`, `services/crop_knowledge.py`
- **Method**: 
  - FAO-56 Penman-Monteith ET0 calculation
  - Crop coefficient (Kc) curves for each growth stage
  - Daily soil water balance accounting
  - Water stress detection when soil water < RAW threshold
- **Crops Supported**: 19 crops with scientifically-validated Kc curves
- **Status**: ✅ **FULLY INTEGRATED** in rotation calculations

### 3. **FlipPoint Threshold Detection**
- **What**: Water supply level where optimal rotation changes
- **Where**: `routers/rotations.py` → `/flippoint` endpoint
- **Method**:
  1. Tests 20 irrigation capacity values (0 to 100+ mm/week)
  2. For each value, calculates water stress for all rotations
  3. Determines preferred rotation (lowest stress)
  4. Detects threshold where preference switches
- **Inputs**: Farm irrigation capacity (from farmer inputs)
- **Outputs**: Genuine threshold or "no flippoint" (stable preference)
- **Status**: ✅ **FULLY INTEGRATED** (as of this session)

### 4. **Rotation Comparison with Feasibility**
- **What**: Compare up to 3 rotations considering irrigation constraints
- **Where**: `routers/rotations.py` → `/compare` endpoint
- **Method**:
  - Calculates seasonal water demand for each rotation
  - Fetches farm irrigation capacity from database
  - Determines feasibility (demand ≤ available capacity)
  - Calculates irrigation deficit for infeasible rotations
- **Status**: ✅ **ENHANCED** (now uses farm irrigation capacity)

### 5. **Irrigation Capacity Storage**
- **What**: Farm-specific irrigation capacity in database
- **Where**: `database/db.py` → `farm_configs` table
- **Updated By**: `PUT /farms/{farm_id}/irrigation` endpoint
- **Used By**: Rotation comparison, FlipPoint calculation
- **Status**: ✅ **FULLY INTEGRATED** (as of this session)

### 6. **Planting Suitability Analysis**
- **What**: Assess crop viability based on climate constraints
- **Where**: `routers/planting.py` → `/suitability` endpoint
- **Method**:
  - Temperature range check (GDD accumulation)
  - Growing season length validation
  - Frost risk assessment
  - Water availability preliminary check
- **Data Source**: NASA POWER historical climate
- **Status**: ✅ **FULLY INTEGRATED** (existing feature)

### 7. **Ground Truth Forecast Verification**
- **What**: Compare weather forecasts to observed conditions
- **Where**: `routers/ground_truth.py`
- **Method**:
  - Store forecast snapshots with lead times
  - Compare to actual weather observations
  - Calculate MAE (Mean Absolute Error) for temperature, precipitation
- **Data Source**: Open-Meteo forecasts + NASA POWER observations
- **Status**: ✅ **FULLY INTEGRATED** (existing feature)

---

## ℹ️ UI-Only (Conversion & Display Logic)

### 1. **Farmer Input Conversions**
- **What**: Convert buckets/pumps to mm/week
- **Where**: `frontend/src/components/sections/FlipPointSection.tsx`
- **Calculations**:
  ```typescript
  // Bucket method
  weeklyLitres = bucketSize × bucketsPerDay × daysPerWeek
  grossDepthMm = weeklyLitres / plotAreaM2
  effectiveDepthMm = grossDepthMm × (efficiency / 100)
  
  // Pump method
  weeklyLitres = flowRate × minutesPerDay × daysPerWeek
  grossDepthMm = weeklyLitres / plotAreaM2
  effectiveDepthMm = grossDepthMm × (efficiency / 100)
  ```
- **Purpose**: Translate farmer-friendly inputs to scientific units
- **Status**: ✅ **COMPLETE** - Then sent to backend

### 2. **Area Unit Conversion**
- **What**: m² ↔ hectares
- **Where**: Frontend UI
- **Calculation**: `1 hectare = 10,000 m²`
- **Purpose**: Let farmers use familiar units
- **Status**: ✅ **COMPLETE**

### 3. **Irrigation Efficiency Slider**
- **What**: Configurable estimate of application efficiency
- **Where**: Frontend UI (30-95% range, default 70%)
- **Nature**: USER ESTIMATE, not measured
- **Purpose**: Account for runoff, evaporation, deep percolation losses
- **Applied**: Once in frontend before sending to backend
- **Status**: ✅ **COMPLETE** - Backend receives effective depth

### 4. **Litres/Week Display**
- **What**: Show total weekly water volume for farmer's field
- **Where**: Frontend display only
- **Calculation**: `effectiveMm × areaM2`
- **Purpose**: Farmer-friendly interpretation of mm/week
- **Status**: ✅ **COMPLETE**

### 5. **Flow Measurement Guide**
- **What**: Instructions for measuring pump flow with bucket + timer
- **Where**: Frontend modal (help button)
- **Purpose**: Help farmers measure actual flow rate
- **Status**: ✅ **COMPLETE**

---

## 🔄 Hybrid (Frontend Calculation → Backend Storage → Backend Model)

### 1. **Irrigation Capacity Workflow**

#### Frontend (Calculation)
```typescript
// FlipPointSection.tsx
weeklyLitres = pumpFlowRate × minutesPerDay × daysPerWeek
grossDepthMm = weeklyLitres / plotAreaM2
effectiveDepthMm = grossDepthMm × (efficiency / 100)
```

#### Frontend → Backend (Update)
```http
PUT /api/farms/{farm_id}/irrigation
{
  "irrigation_mm_week": 0.153,
  "irrigation_mm_day": 0.0219,
  "method": "pump",
  "efficiency_percent": 85
}
```

#### Backend (Storage)
```python
# routers/farms.py
await db.execute(
    "UPDATE farm_configs SET irrigation_capacity = ? WHERE farm_id = ?",
    (irrigation_mm_day, farm_id)
)
```

#### Backend (Scientific Model)
```python
# routers/rotations.py - FlipPoint calculation
for test_mm_week in range(0, 100, 5):
    # Calculate stress for each rotation at this irrigation level
    # Uses NASA POWER climate + FAO-56 crop water model
    stress = calculate_water_stress(rotation, test_mm_week)
```

**Status**: ✅ **COMPLETE END-TO-END FLOW**

---

## Comparison Table

| Calculation | Location | Data Source | Connected to Model |
|-------------|----------|-------------|-------------------|
| NASA POWER climate data | Backend | Satellite + ground stations | ✅ Yes |
| FAO-56 ET0 (Penman-Monteith) | Backend | Climate data | ✅ Yes |
| Crop coefficient (Kc) curves | Backend | FAO-56 Paper 56 | ✅ Yes |
| Daily soil water balance | Backend | ET, precip, irrigation | ✅ Yes |
| Water stress detection | Backend | Soil water vs RAW | ✅ Yes |
| FlipPoint threshold | Backend | Rotation comparison loop | ✅ Yes |
| Irrigation capacity | Database | Farmer inputs (effective) | ✅ Yes |
| Rotation feasibility check | Backend | Capacity vs demand | ✅ Yes |
| Planting suitability | Backend | Climate constraints | ✅ Yes |
| Ground truth verification | Backend | Forecast vs observed | ✅ Yes |
| **Bucket/pump to mm/week** | **Frontend** | **Farmer inputs** | **➡️ Then sent to backend** |
| **Irrigation efficiency** | **Frontend** | **User estimate** | **➡️ Applied once, then backend** |
| **m² ↔ hectares** | **Frontend** | **Unit conversion** | **ℹ️ Display only** |
| **Litres/week display** | **Frontend** | **mm × area** | **ℹ️ Display only** |
| **Flow measurement guide** | **Frontend** | **Educational content** | **ℹ️ Display only** |

---

## Verification Methods

### Backend-Connected Calculations
**How to Verify**:
1. Check browser Network tab (F12) → See API calls to `/flippoint`, `/compare`
2. Backend logs show NASA POWER API requests
3. Results vary with farm location (different climate data)
4. Results change when rotations modified
5. Stress days calculated, not hardcoded

**Example**:
```
Farm A (Iowa, 40°N): Corn rotation needs 450mm irrigation
Farm B (Arizona, 35°N): Same rotation needs 750mm irrigation
→ Different climate data from NASA POWER
```

### UI-Only Calculations
**How to Verify**:
1. No API calls triggered by these changes
2. Instant calculation (no loading spinner)
3. Results don't change with farm location
4. Simple arithmetic (litres → mm conversion)

**Example**:
```
Change area from 1000 m² to 1 hectare:
- Litres/week changes instantly (no API call)
- mm/week stays same (area cancels out)
```

---

## Honest Reporting Status

### ✅ We Are Honest About:
1. **Irrigation Efficiency**: Labeled as "estimate", not measured
2. **FlipPoint Existence**: May or may not exist (stable preference is valid)
3. **Rotation Rankings**: May not change (no forced differences)
4. **Data Source**: Always cite "NASA POWER Historical Climate"
5. **Model**: Clearly state "Simplified FAO-56" or "Full FAO-56"
6. **Assumptions**: Explicit about effective rainfall fraction (80%), etc.

### ❌ We Don't:
1. Show hardcoded "example" FlipPoints (65 mm/week removed)
2. Force ranking changes when they don't exist
3. Claim to measure things we estimate (efficiency)
4. Hide data sources or methodology
5. Use arbitrary default irrigation (50 mm/week) as if it's real

---

## What Changed in This Integration

### Before
- ❌ Irrigation inputs were UI-only (not connected to model)
- ❌ FlipPoint section showed placeholder "Compare Crop Plans First"
- ❌ Hardcoded FlipPoint example (65 mm/week)
- ❌ Rotation comparison didn't use farm irrigation capacity
- ❌ No automatic backend updates when irrigation changed

### After
- ✅ Irrigation inputs update backend database
- ✅ FlipPoint calculated using real NASA POWER + FAO-56 model
- ✅ Genuine threshold detection (or honest "no flippoint")
- ✅ Rotation comparison uses farm-specific capacity
- ✅ Automatic debounced updates on input changes
- ✅ Clear "last updated" timestamps
- ✅ Stale result invalidation when inputs change

---

## Future Backend Integration Opportunities

### 🔮 Could Be Enhanced

1. **Real-Time Weather Forecast**
   - Currently: Open-Meteo forecast stored but not used in rotation planning
   - Could: Recommend irrigation timing based on forecast rain

2. **Multi-Year Climate Analysis**
   - Currently: Single year (2023) for rotation comparison
   - Could: Test rotations across 5-10 historical years for robustness

3. **Soil Type Integration**
   - Currently: TAW calculated from generic soil parameters
   - Could: Connect farmer's soil description to USDA soil database

4. **Irrigation Scheduling**
   - Currently: Weekly capacity only
   - Could: Recommend specific watering days/amounts based on ET forecast

5. **Crop Yield Estimation**
   - Currently: Water stress days calculated
   - Could: Estimate yield penalty from stress using FAO-33 methodology

6. **Economic Analysis**
   - Currently: FlipPoint shows water threshold
   - Could: Show profit threshold (irrigation cost vs crop value)

---

## Summary

**Backend-Connected Calculations**: 7 major systems
- NASA POWER climate data ✅
- FAO-56 crop water model ✅
- FlipPoint threshold detection ✅
- Rotation comparison with feasibility ✅
- Irrigation capacity storage ✅
- Planting suitability ✅
- Ground truth verification ✅

**UI-Only Calculations**: 5 farmer-friendly helpers
- Bucket/pump conversions ℹ️ (then sent to backend)
- Area unit conversions ℹ️
- Irrigation efficiency slider ℹ️ (then sent to backend)
- Litres/week display ℹ️
- Flow measurement guide ℹ️

**Integration Status**: ✅ **COMPLETE**
- Farmer inputs → Backend scientific model → Honest results
- No hardcoded placeholders
- Clear distinction between measured vs estimated values
- Full traceability from farmer's bucket to NASA satellite data

---

**Last Updated**: Current Session  
**Integration Completion**: End-to-End Farmer Irrigation → Backend Scientific Model
