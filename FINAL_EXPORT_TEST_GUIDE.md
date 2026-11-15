# Scientific Export - Final Test & Verification Guide

**Date**: November 15, 2026  
**Purpose**: Verify corrected scientific results export functionality

---

## Quick Start Test

### Prerequisites

1. **Start Backend**:
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Browser**: http://localhost:3001

---

## Test 1: Export Without Calculations (Error Handling)

**Purpose**: Verify error message when no calculations have been run

**Steps**:
1. Open FieldShift FarmOS
2. Select any farm from the list
3. Scroll to "My Farm Data & Analysis" section
4. Click **"Export Scientific Results"** (🔬 emerald button)

**Expected Result**:
```
❌ No calculated results found. Please run calculations in the 
dashboard sections first (Planting Suitability, Rotation Lab, 
FlipPoint, or Ground Truth).
```

**Verification**:
- ✅ Error message appears in red banner
- ✅ No file downloads
- ✅ Message is clear and actionable
- ✅ Button re-enables after error

**Status**: [ ] PASS / [ ] FAIL

---

## Test 2: Planting Suitability Export

**Purpose**: Verify export of planting suitability calculation

### Part A: Run Calculation

**Steps**:
1. Select farm (e.g., "My Farm")
2. Scroll to "Check Planting Suitability" section (top of dashboard)
3. Select crop: **Corn**
4. Select date: **2024-05-01** (May 1, 2024)
5. Click **"Check Suitability"** button
6. Wait 3-5 seconds for results

**Expected Result**:
- Results box appears with recommendation
- Shows: "Recommended" or "Recommended with Caution" or "Not Recommended"
- Displays main reason (e.g., "Good temperature conditions...")
- Shows climate evidence list
- Shows farmer actions list

**Note the values**:
- Recommendation: _______________
- Main Reason: _______________
- Temperature mention: _______________

### Part B: Export Results

**Steps**:
1. Scroll down to "My Farm Data & Analysis" section
2. Click **"Export Scientific Results"** button
3. Wait 1-2 seconds

**Expected Result**:
```
✅ Scientific results exported successfully! 
Included: planting_suitability
```

**File downloaded**: `fieldshift_scientific_results_My_Farm_2026-11-15.zip`

### Part C: Verify Export Content

**Steps**:
1. Open downloaded ZIP file
2. Extract contents

**Expected Files**:
- README.txt
- planting_suitability.csv

**Verify README.txt**:
- [ ] Contains farm name and ID
- [ ] Lists "Planting Suitability" as included calculation
- [ ] Mentions NASA POWER as data source
- [ ] Mentions FAO-56 methodology
- [ ] Notes that results are "MODEL CALCULATION"
- [ ] Includes units (°C, mm, days)

**Verify planting_suitability.csv**:

**Open in Excel/Google Sheets**:
1. File opens successfully
2. Headers visible

**Expected Columns**:
- farm_id
- farm_name
- latitude
- longitude
- crop_name
- planting_date
- harvest_date
- season_length_days
- recommendation
- main_reason
- assessment_type
- years_analyzed
- data_type
- calculation_timestamp

**Verify Data Row**:
- [ ] farm_id matches selected farm
- [ ] crop_name = "corn"
- [ ] planting_date = "2024-05-01"
- [ ] recommendation matches screen display
- [ ] main_reason matches screen display
- [ ] data_type = "MODEL_CALCULATION"
- [ ] calculation_timestamp is recent

**Critical Check**: Do exported values MATCH what you saw on screen?
- Recommendation: [ ] MATCH / [ ] MISMATCH
- Main Reason: [ ] MATCH / [ ] MISMATCH

**Verify CSV Comments** (at end of file):
- [ ] Climate Evidence section with bullet points
- [ ] Risks section with warnings
- [ ] Farmer Actions section with recommendations

**Status**: [ ] PASS / [ ] FAIL

---

## Test 3: Rotation Comparison Export

**Purpose**: Verify export of rotation water balance calculations

### Part A: Create Rotations

**Steps**:
1. Scroll to "Crop Rotation Lab" section
2. Create "Current Rotation":
   - Crop 1: Corn, Planting: 05-01, Harvest: 10-15
3. Create "Small Shift Rotation":
   - Crop 1: Soybean, Planting: 05-15, Harvest: 10-30

### Part B: Run Comparison

**Steps**:
1. In "Compare Rotations" subsection
2. Check both rotations created above
3. Set year: **2023**
4. Click **"Compare Rotations"** button
5. Wait 5-10 seconds

**Expected Result**:
- Comparison table appears
- Shows water demand for each rotation (mm)
- Shows stress days
- Shows irrigation needs (mm)
- Highlights preferred rotation

**Note the values**:
- Current rotation water demand: _______ mm
- Small shift water demand: _______ mm
- Current rotation stress days: _______ days
- Preferred rotation: _______________

### Part C: Export Results

**Steps**:
1. Scroll to "My Farm Data & Analysis"
2. Click **"Export Scientific Results"**

**Expected Result**:
```
✅ Scientific results exported successfully! 
Included: planting_suitability, rotation_comparison
```
(Includes previous planting result + new rotation result)

### Part D: Verify Export

**Open ZIP file, extract contents**

**Expected Files**:
- README.txt
- planting_suitability.csv (from Test 2)
- rotation_comparison.csv (NEW)

**Open rotation_comparison.csv**:

**Expected Columns**:
- farm_id
- rotation_type
- feasible
- total_seasonal_water_demand_mm
- total_stress_days
- total_irrigation_need_mm
- irrigation_capacity_mm_day
- preferred
- data_type
- calculation_timestamp

**Expected Rows**: 2 or more (one per rotation)
- Row 1: current rotation
- Row 2: small_shift rotation

**Verify Values**:
- [ ] Water demand matches screen display (within 1%)
- [ ] Stress days match screen display
- [ ] Preferred rotation marked "Yes" for correct one
- [ ] data_type = "MODEL_CALCULATION"

**Critical Check**: Do values MATCH screen?
- Water demand: [ ] MATCH / [ ] MISMATCH
- Stress days: [ ] MATCH / [ ] MISMATCH
- Preferred: [ ] MATCH / [ ] MISMATCH

**Status**: [ ] PASS / [ ] FAIL

---

## Test 4: FlipPoint Export

**Purpose**: Verify export of FlipPoint threshold calculations

### Part A: Calculate FlipPoint

**Steps**:
1. Scroll to "FlipPoint & Agricultural Risk" section
2. Ensure rotations are selected (from Test 3)
3. Parameter: **irrigation_capacity** (should be pre-selected)
4. Current value: **10** mm/week
5. Range: **0** to **50** mm/week
6. Steps: **20**
7. Click **"Calculate FlipPoint"**
8. Wait 10-15 seconds

**Expected Result**:
- Chart displays with curves
- Shows FlipPoint threshold value (e.g., "15.5 mm/week")
- Shows which rotations are preferred at different irrigation levels
- Table shows data points

**Note the values**:
- FlipPoint threshold: _______ mm/week
- FlipPoint from: _______________
- FlipPoint to: _______________

### Part B: Export Results

**Steps**:
1. Scroll to "My Farm Data & Analysis"
2. Click **"Export Scientific Results"**

**Expected Result**:
```
✅ Scientific results exported successfully! 
Included: planting_suitability, rotation_comparison, flippoint
```

### Part C: Verify Export

**Open ZIP, expected files**:
- README.txt
- planting_suitability.csv
- rotation_comparison.csv
- flippoint_analysis.csv (NEW)

**Open flippoint_analysis.csv**:

**Expected Columns**:
- irrigation_mm_week
- preferred_rotation
- stress_scores
- data_type
- calculation_timestamp

**Expected Rows**: 20 (one per step)

**Sample rows**:
```csv
irrigation_mm_week,preferred_rotation,stress_scores,data_type
10.0,current,"{""current"": 8.5, ""small_shift"": 12.3}",MODEL_CALCULATION
15.5,small_shift,"{""current"": 10.2, ""small_shift"": 9.1}",MODEL_CALCULATION
...
```

**Verify**:
- [ ] FlipPoint threshold row exists
- [ ] Preferred rotation changes at threshold
- [ ] Stress scores are numerical
- [ ] 20 data points present
- [ ] data_type = "MODEL_CALCULATION"

**Critical Check**: Does FlipPoint threshold MATCH chart?
- Threshold value: [ ] MATCH / [ ] MISMATCH

**Status**: [ ] PASS / [ ] FAIL

---

## Test 5: Ground Truth Export

**Purpose**: Verify export of forecast accuracy metrics

### Part A: Check Ground Truth

**Steps**:
1. Scroll to "Ground Truth & Evidence" section
2. Observe forecast accuracy metrics (if any observations exist)
3. Note displayed values:
   - Temperature MAE: _______ °C
   - Precipitation MAE: _______ mm
   - Observation count: _______

### Part B: Export Results

**Steps**:
1. Scroll to "My Farm Data & Analysis"
2. Click **"Export Scientific Results"**

**Expected Result**:
If Ground Truth metrics are available:
```
✅ Scientific results exported successfully! 
Included: planting_suitability, rotation_comparison, flippoint, groundtruth
```

If not available, only previous 3 exported.

### Part C: Verify Export

**If Ground Truth included**:

**Open ZIP, check for**: ground_truth_metrics.csv

**Expected Columns**:
- temperature_mae
- temperature_bias
- precipitation_mae
- observation_count
- forecast_source
- data_type

**Verify**:
- [ ] MAE values match screen
- [ ] Observation count matches screen
- [ ] data_type = "MODEL_CALCULATION"

**Status**: [ ] PASS / [ ] FAIL / [ ] N/A (no metrics)

---

## Test 6: Help Dialog

**Purpose**: Verify help dialog is still accessible

**Steps**:
1. Scroll to "My Farm Data & Analysis" section
2. Below the three export buttons, find help link:
   ```
   ℹ️ Need help? Click here for guidance on scientific exports
   ```
3. Click the help link

**Expected Result**:
- Dialog opens with guidance
- Title: "ℹ️ Scientific Export - Help & Guidance"
- Contains sections:
  - How Scientific Export Works
  - Workflow steps
  - Important Notes
  - Where to Run Calculations

**Verify**:
- [ ] Dialog explains export downloads actual results
- [ ] Dialog lists what gets exported
- [ ] Dialog provides navigation to calculation sections
- [ ] "Got It - Ready to Export" button works
- [ ] Close button works
- [ ] Dialog is optional (not forced)

**Status**: [ ] PASS / [ ] FAIL

---

## Test 7: Empty Farm Test

**Purpose**: Verify behavior with farm that has no calculation history

**Steps**:
1. Select a different farm (one you haven't run calculations on)
2. Click **"Export Scientific Results"**

**Expected Result**:
```
❌ No calculated results found. Please run calculations first...
```

**Verify**:
- [ ] Error message appears
- [ ] No download occurs
- [ ] Message is farm-specific (only exports for selected farm)

**Status**: [ ] PASS / [ ] FAIL

---

## Test 8: File Format Verification

**Purpose**: Verify exported files meet format requirements

### CSV Format

**Open any exported CSV in Excel**:
- [ ] File opens without errors
- [ ] Headers are readable
- [ ] Data is in correct columns
- [ ] No formula injection (cells don't start with =, +, -, @)
- [ ] UTF-8 encoding (special characters display correctly)
- [ ] Commas in data are properly escaped

**Open same CSV in Google Sheets**:
- [ ] File opens without errors
- [ ] Data displays correctly
- [ ] Can sort and filter data

**Open same CSV in text editor**:
- [ ] Valid CSV format
- [ ] Consistent delimiters
- [ ] Proper line endings

### ZIP Format

**Extract ZIP file**:
- [ ] Extracts without errors
- [ ] All files present
- [ ] File sizes reasonable (not empty)
- [ ] README is readable text

**Status**: [ ] PASS / [ ] FAIL

---

## Test 9: Data Accuracy Verification

**Purpose**: Verify exported numerical values match dashboard displays

### Create Reference Sheet

| Calculation | Screen Value | Exported Value | Match? |
|-------------|--------------|----------------|--------|
| Planting Recommendation | ____________ | ____________ | [ ] |
| Rotation Water Demand (Current) | _______ mm | _______ mm | [ ] |
| Rotation Water Demand (Small Shift) | _______ mm | _______ mm | [ ] |
| Rotation Stress Days (Current) | _______ days | _______ days | [ ] |
| FlipPoint Threshold | _______ mm/week | _______ mm/week | [ ] |
| Ground Truth Temp MAE | _______ °C | _______ °C | [ ] |

**Verification Rules**:
- Exact match required for: Recommendations, rotation type names
- Within 1% acceptable for: Water demand, stress days, thresholds
- Within 0.1 acceptable for: MAE values

**All Match?**: [ ] YES / [ ] NO

**Status**: [ ] PASS / [ ] FAIL

---

## Test 10: Regression Testing

**Purpose**: Verify all existing features still work

### Phase 1: Farm Management
- [ ] Create new farm works
- [ ] Rename farm works
- [ ] Delete farm works
- [ ] Favorites work
- [ ] Search works
- [ ] Map updates when farm selected

### Phase 2: Farmer Data Upload
- [ ] Download CSV template works
- [ ] Upload CSV works
- [ ] Preview shows validation
- [ ] Import saves observations
- [ ] Manual entry works
- [ ] View observations works
- [ ] Delete observation works

### Phase 3: Raw Data Export
- [ ] Refresh button works
- [ ] Export Raw Data button works
- [ ] NASA POWER exports
- [ ] Farmer observations export
- [ ] Multiple datasets export as ZIP

### Original Features
- [ ] Planting suitability calculates
- [ ] Crop rotations compare
- [ ] FlipPoint calculates
- [ ] Smart Farm monitoring displays
- [ ] Ground Truth shows metrics
- [ ] Pump controls visible

**Status**: [ ] PASS / [ ] FAIL

---

## Test 11: Edge Cases

### Test 11A: Very Large Rotation
**Steps**:
1. Create rotation with 5+ crops
2. Run comparison
3. Export results

**Expected**: CSV contains all crops, file size reasonable

**Status**: [ ] PASS / [ ] FAIL

### Test 11B: Special Characters in Farm Name
**Steps**:
1. Farm name: "Test Farm #1 (2024)"
2. Run calculation
3. Export results

**Expected**: Filename sanitized, export works

**Status**: [ ] PASS / [ ] FAIL

### Test 11C: Browser Refresh
**Steps**:
1. Run calculations
2. Refresh browser (F5)
3. Try to export

**Expected**: Either works (if localStorage persists) or shows error (if cleared)

**Status**: [ ] PASS / [ ] FAIL / [ ] N/A

---

## Test 12: Cross-Browser Testing

**Test in multiple browsers**:

| Browser | Version | Export Works? | Files Download? | CSVs Open? |
|---------|---------|---------------|-----------------|------------|
| Chrome | _______ | [ ] | [ ] | [ ] |
| Edge | _______ | [ ] | [ ] | [ ] |
| Firefox | _______ | [ ] | [ ] | [ ] |
| Safari | _______ | [ ] | [ ] | [ ] |

**Status**: [ ] PASS / [ ] FAIL

---

## Final Verification Checklist

### Functionality
- [ ] Export button downloads ZIP file
- [ ] ZIP contains CSV files with actual data
- [ ] Exported values match screen displays
- [ ] Error handling works when no calculations run
- [ ] Help dialog accessible and informative
- [ ] All 5 calculation types can be exported
- [ ] README documentation is comprehensive

### Data Quality
- [ ] No fake or fabricated data
- [ ] Values are numerically accurate
- [ ] Units are clearly labeled
- [ ] Data sources documented
- [ ] Methodology explained
- [ ] Calculation timestamps present
- [ ] Farm ID and coordinates correct

### File Format
- [ ] CSV opens in Excel
- [ ] CSV opens in Google Sheets
- [ ] ZIP extracts correctly
- [ ] UTF-8 encoding correct
- [ ] No formula injection
- [ ] README is readable

### Scientific Integrity
- [ ] Clear "MODEL CALCULATION" labels
- [ ] Data sources cited (NASA POWER, FAO-56)
- [ ] Not claiming to be observed measurements
- [ ] Distinguishes from real sensor data
- [ ] Includes limitations in README

### User Experience
- [ ] Clear button labels
- [ ] Helpful error messages
- [ ] Success feedback
- [ ] Optional help available
- [ ] Fast export (< 3 seconds)
- [ ] Intuitive workflow

### Regressions
- [ ] Phase 1 features work
- [ ] Phase 2 features work
- [ ] Phase 3 features work
- [ ] Original dashboard intact
- [ ] ESP32 firmware unchanged
- [ ] Green theme preserved

---

## Test Results Summary

**Test Date**: _______________  
**Tester**: _______________  
**Environment**: Development / Production

| Test | Status | Notes |
|------|--------|-------|
| 1. Error Handling | [ ] PASS [ ] FAIL | |
| 2. Planting Export | [ ] PASS [ ] FAIL | |
| 3. Rotation Export | [ ] PASS [ ] FAIL | |
| 4. FlipPoint Export | [ ] PASS [ ] FAIL | |
| 5. Ground Truth Export | [ ] PASS [ ] FAIL | |
| 6. Help Dialog | [ ] PASS [ ] FAIL | |
| 7. Empty Farm | [ ] PASS [ ] FAIL | |
| 8. File Format | [ ] PASS [ ] FAIL | |
| 9. Data Accuracy | [ ] PASS [ ] FAIL | |
| 10. Regressions | [ ] PASS [ ] FAIL | |
| 11. Edge Cases | [ ] PASS [ ] FAIL | |
| 12. Cross-Browser | [ ] PASS [ ] FAIL | |

**Overall Status**: [ ] ALL PASS [ ] SOME FAILURES [ ] BLOCKED

**Issues Found**: _______________________________________________

**Ready for Demo**: [ ] YES [ ] NO [ ] WITH CAVEATS

---

## Sign-Off

**Implementation Complete**: [ ] YES [ ] NO  
**All Tests Passing**: [ ] YES [ ] NO  
**Documentation Complete**: [ ] YES [ ] NO  
**Ready for NASA Space Apps Demo**: [ ] YES [ ] NO  

**Signature**: _______________  
**Date**: _______________

---

**Test Guide Complete**  
**Status**: Ready for execution  
**Expected Duration**: 45-60 minutes for complete test suite

