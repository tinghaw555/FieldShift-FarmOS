# Smart Farm Multi-Farm Support - Fix Report

**Date:** November 15, 2026  
**Issue:** Sensor readings disappear when changing or selecting farms  
**Status:** ✅ FIXED

---

## PROBLEM SUMMARY

When users selected a farm other than Farm ID 1, the Smart Farm Monitoring dashboard showed empty sensor cards with "No Sensor Data Available" even though demonstration readings existed in the database.

### Symptoms

1. **Farm 1:** Worked perfectly, showing all 120 imported CSV readings
2. **Other Farms:** Sensor cards became empty, switching to offline mode
3. **Switching between farms:** Readings only appeared for Farm 1
4. **Creating new farms:** No sensor data available, monitoring appeared broken

---

## ROOT CAUSE ANALYSIS

### 1. Hardcoded Farm ID in Import Script

**File:** `backend/import_sensor_csv.py`

```python
# Default to farm_id = 1 (or prompt user)
farm_id = 1
```

All 120 demonstration CSV readings were imported with `farm_id = 1`, linking them exclusively to Farm 1.

### 2. Strict Farm ID Filtering in Backend API

**File:** `backend/routers/hardware.py` - `/csv-readings` endpoint

```python
WHERE farm_id = ? AND is_simulated = 1
```

The endpoint only returned readings matching the exact farm_id requested. No fallback mechanism existed for farms without their own data.

### 3. Frontend Shows "Offline" When No Data Found

**File:** `frontend/src/components/sections/SmartFarmSection.tsx`

```typescript
if (data.status === 'success' && data.readings && data.readings.length > 0) {
    // Load readings
} else {
    throw new Error('No sensor readings found')
    setDataMode('offline')
}
```

When the backend returned no readings, the frontend switched to offline mode and hid all sensor cards.

### 4. No Distinction Between Data Types

The system didn't differentiate between:
- Farm-specific imported readings (should stay with that farm)
- Shared demonstration readings (can be used as examples for all farms)
- No available readings (show appropriate empty state)

---

## SOLUTION IMPLEMENTED

### Three-Tier Data Priority System

**Priority 1: Farm-Specific Readings**
- If a farm has its own imported sensor data, always use it
- Preserve farm_id association
- Label as "Farm Data" in UI

**Priority 2: Shared Demonstration Readings**
- If farm has no data, fall back to shared demonstration dataset from Farm ID 1
- Do NOT save to the target farm (read-only reference)
- Label as "Example Readings" in UI

**Priority 3: No Data Available**
- Keep Smart Farm Monitoring interface visible (don't hide)
- Show appropriate message
- Allow future data import

---

## CODE CHANGES

### 1. Backend: Enhanced `/csv-readings` Endpoint ✅

**File:** `backend/routers/hardware.py`

**Changes:**
- Added three-tier fallback logic
- Try farm-specific readings first
- Fall back to shared demonstration data from farm_id=1
- Return clear data_source indicators
- Added `source_farm_id` for shared data

**New Response Fields:**
```python
{
    "status": "success",
    "data_source": "farm_specific" | "shared_demonstration" | "no_data",
    "farm_id": requested_farm_id,
    "source_farm_id": 1,  # Only for shared_demonstration
    "total_readings": 120,
    "readings": [...],
    "note": "Example readings from shared demonstration dataset"
}
```

**Benefits:**
- Farm 1 continues using its own 120 readings
- Other farms automatically get example readings
- Clear provenance for all data
- No data modification or duplication

### 2. Frontend: Enhanced Data Source Labels ✅

**File:** `frontend/src/components/sections/SmartFarmSection.tsx`

**Changes:**
- Updated `getDataSourceDescription()` to handle three data sources
- Added purple color scheme for shared demonstration data
- Enhanced Data Source Details panel with accurate descriptions
- Updated notes to explain data provenance

**New Labels:**
- **Farm-Specific:** "Preview Mode — Farm Data"
  - Description: "Displaying {Farm Name}'s imported readings"
  
- **Shared Demo:** "Preview Mode — Example Readings"
  - Description: "Displaying shared demonstration data (120 example readings)"
  
- **Hardware:** "Connected" (unchanged)
  - Description: "Receiving authenticated ESP32 telemetry"

**Color Coding:**
- 🟢 Green: Real hardware telemetry
- 🔵 Blue: Farm-specific imported data
- 🟣 Purple: Shared example readings
- ⚪ Gray: No data / offline

### 3. Data Source Details Panel Enhancement ✅

**New Information Display:**

```
Data Source: {Farm Name}'s Imported Data
Note: Preview data shows {Farm Name}'s imported measurements stored in database.
```

Or for shared data:

```
Data Source: Shared Example Readings
Note: Example readings from shared demonstration dataset, not specific to this farm.
```

---

## TESTING RESULTS

### Test Case 1: Reload Farm 1 ✅

**Action:** Navigate to Smart Farm Monitoring with Farm 1 selected

**Expected:**
- Shows 120 farm-specific readings
- Data source: "Farm Data"
- Label: "{Farm Name}'s Imported Data"

**Result:** ✅ PASSED
- Farm 1 displays its own 120 readings
- Correctly labeled as farm-specific
- Preview mode auto-enables
- Readings advance every 5 seconds

### Test Case 2: Edit Farm 1 GPS Coordinates ✅

**Action:** Change Farm 1 latitude/longitude without changing farm_id

**Expected:**
- Readings remain available
- farm_id stays 1
- 480 sensor records preserved in database

**Result:** ✅ PASSED
- Coordinate update preserves farm_id
- All 120 reading sets remain accessible
- No database records deleted
- Sensor data continues displaying

### Test Case 3: Create Farm 2 (No Own Readings) ✅

**Action:** Create new farm "Test Farm 2" at different GPS coordinates

**Expected:**
- Smart Farm Monitoring interface remains visible
- Shows shared demonstration readings
- Data source: "Example Readings"
- Label: "Shared demonstration dataset"
- Does NOT save readings to Farm 2

**Result:** ✅ PASSED
- Monitoring cards visible with data
- Shows 120 example readings from farm_id=1
- Labeled as "Example Readings"
- Purple color scheme applied
- Note explains data is shared, not farm-specific
- Database query confirms no new records created for farm_id=2

### Test Case 4: Switch Between Farms ✅

**Action:** 
1. Select Farm 1 → observe readings
2. Switch to Farm 2 → observe readings
3. Switch back to Farm 1 → observe readings

**Expected:**
- Farm 1 always shows farm-specific data (blue)
- Farm 2 always shows shared example data (purple)
- No data mixing or contamination
- Each farm maintains correct provenance

**Result:** ✅ PASSED
- Farm 1: 120 farm-specific readings, blue label
- Farm 2: 120 shared example readings, purple label
- Switching preserves correct data source
- No database records mixed between farms

### Test Case 5: Backend Restart Persistence ✅

**Action:** 
1. Stop backend server
2. Restart backend server
3. Reload Farm 1 and Farm 2

**Expected:**
- Farm 1 readings persist in SQLite
- Farm 2 still has access to shared example data
- No data loss

**Result:** ✅ PASSED
- All 480 records remain in sensor_readings table
- farm_id associations preserved
- is_simulated flags intact
- Both farms display correct data after restart

### Test Case 6: Database Query Verification ✅

**Action:** Query database directly

```sql
SELECT farm_id, COUNT(*) FROM sensor_readings 
WHERE is_simulated = 1 
GROUP BY farm_id;
```

**Expected:**
```
farm_id | count
--------|------
1       | 480
```

**Result:** ✅ PASSED
- Only farm_id=1 has records (120 × 4 metrics = 480)
- No duplicate records created
- Shared reading mechanism works via read-only reference

---

## DATA INTEGRITY VERIFICATION

### Sensor Readings Table

```sql
sqlite> SELECT farm_id, sensor_type, COUNT(*), MIN(timestamp), MAX(timestamp)
        FROM sensor_readings 
        WHERE is_simulated = 1 
        GROUP BY farm_id, sensor_type;
```

**Result:**
```
farm_id | sensor_type    | count | min_timestamp       | max_timestamp
--------|----------------|-------|---------------------|--------------------
1       | temperature    | 120   | 2026-11-15 08:00:00 | 2026-11-15 09:59:00
1       | humidity       | 120   | 2026-11-15 08:00:00 | 2026-11-15 09:59:00
1       | soil_moisture  | 120   | 2026-11-15 08:00:00 | 2026-11-15 09:59:00
1       | water_level    | 120   | 2026-11-15 08:00:00 | 2026-11-15 09:59:00
```

✅ All 480 records preserved  
✅ All timestamps intact  
✅ No duplicate farms created  
✅ is_simulated flag = 1 for all demonstration data

---

## PRESERVED FUNCTIONALITY

### ✅ All Existing Features Work

1. **Five-Second Refresh:** Preview readings advance every 5 seconds
2. **Preview Pump Control:** Software-only pump toggle works
3. **System Health Check:** Backend status badge updates
4. **Data Source Details:** Expandable panel shows provenance
5. **Farm Switching:** Instant context switch between farms
6. **Hardware Mode:** Real ESP32 telemetry path preserved
7. **Device Registration:** Physical hardware integration unaffected
8. **Pump Commands:** Physical pump control for hardware mode works
9. **Other Sections:** Crop rotation, FlipPoint, Ground Truth unchanged
10. **Database Schema:** No schema changes, backward compatible

---

## EDGE CASES HANDLED

### 1. Farm Without Any Demonstration Data ✅
**Scenario:** Backend has no farm_id=1 readings at all

**Behavior:**
```json
{
    "status": "no_data",
    "message": "No demonstration data available",
    "readings": []
}
```

Frontend shows: "No sensor data currently available"

### 2. Multiple Farms With Own Data ✅
**Scenario:** Import CSV data to multiple farm IDs

**Behavior:** Each farm uses its own farm-specific readings, labeled with farm name

### 3. Concurrent Farm Selection ✅
**Scenario:** Multiple users selecting different farms

**Behavior:** Each query isolated by farm_id, no data mixing

### 4. GPS Coordinate Updates ✅
**Scenario:** Change farm GPS without changing farm_id

**Behavior:** farm_id preserved, sensor readings remain associated correctly

---

## FUTURE ENHANCEMENT OPTIONS

### Optional: Import CSV to Specific Farm

If users want to import demonstration data to farms other than Farm 1:

```bash
cd backend
python import_sensor_csv.py --farm-id 2
```

**Modification Required:**
```python
# import_sensor_csv.py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--farm-id', type=int, default=1)
args = parser.parse_args()

farm_id = args.farm_id
```

### Optional: Copy Demonstration Data to New Farm

Add endpoint to create farm-specific copy:

```python
@router.post("/farm/{farm_id}/import-demo-data")
async def import_demo_data_to_farm(farm_id: int):
    """Copy shared demonstration data to farm-specific records"""
    # Copy all farm_id=1 readings to target farm_id
    # Set is_simulated=1, device_id={farm_name}_DEMO
    # Creates independent dataset for the farm
```

**Not Implemented:** Current solution uses read-only reference (more efficient, no data duplication)

---

## ARCHITECTURAL DECISIONS

### Why Read-Only Reference Instead of Copy?

**Decision:** Use farm_id=1 as shared demonstration source

**Rationale:**
1. **No Data Duplication:** 480 records stay as 480, not 480×N farms
2. **Storage Efficiency:** SQLite database stays small
3. **Consistency:** All farms see identical example data
4. **Clear Provenance:** Always know which data is farm-specific vs. shared
5. **Easy Updates:** Reimporting CSV updates all farms automatically

**Trade-off:** Farms share demonstration data (acceptable for examples)

### Why Keep Monitoring Visible When No Data?

**Decision:** Always show Smart Farm Monitoring interface

**Rationale:**
1. **User Expectation:** Users expect consistent UI across farms
2. **Future-Ready:** Allows connecting hardware without UI changes
3. **Example Data:** Shows what the feature does before hardware setup
4. **No Confusion:** Hiding sections implies feature unavailable

**Alternative Rejected:** Hide section entirely when no data (would confuse new users)

---

## DEPLOYMENT NOTES

### No Database Migration Required ✅

- Schema unchanged
- Existing data preserved
- No new tables or columns
- Backward compatible

### No Frontend Breaking Changes ✅

- API response extends existing format
- New fields optional (graceful degradation)
- Existing farms continue working

### Rollback Safety ✅

If issues arise:
1. Revert `hardware.py` to previous version
2. Frontend gracefully handles missing data source field
3. Falls back to existing behavior

---

## SUMMARY

### Problem
Sensor readings only appeared for Farm ID 1. Other farms showed empty cards, creating the impression that Smart Farm Monitoring was broken.

### Root Cause
1. CSV import hardcoded to farm_id=1
2. No fallback mechanism for farms without data
3. Frontend treated "no data" as complete failure

### Solution
1. **Backend:** Three-tier data priority (farm-specific → shared demo → no data)
2. **Frontend:** Enhanced labels distinguishing data sources
3. **UI:** Always visible monitoring interface with clear provenance
4. **Database:** Read-only reference to shared data (no duplication)

### Result
- ✅ Farm 1: Uses its own 120 imported readings
- ✅ Other farms: Show shared example readings with clear labels
- ✅ GPS coordinate changes preserve farm_id and readings
- ✅ No data duplication or database bloat
- ✅ All existing features preserved
- ✅ Clear data provenance throughout
- ✅ Future-ready for multiple farms with own sensor data

---

**Status:** ✅ READY FOR PRODUCTION  
**Testing:** ✅ All test cases passed  
**Data Integrity:** ✅ Verified  
**Backward Compatibility:** ✅ Maintained

