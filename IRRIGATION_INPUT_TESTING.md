# Farmer-Friendly Irrigation Input - Testing Checklist

## Build Status: ✅ PASSED
```
✓ Compiled successfully
✓ Linting and checking validity of types
Route (app): 21.7 kB → 104 kB First Load JS
```

---

## Unit Conversion Tests

### Test 1: Basic Bucket Calculation
**Inputs:**
- Field: 1000 m²
- Method: Bucket
- Bucket size: 10 litres
- Buckets/day: 5
- Days/week: 3
- Efficiency: 70%

**Expected Results:**
- Weekly litres: 150 L
- Gross depth: 0.15 mm
- Effective depth: 0.105 mm
- Per m²: 0.15 L/m²/week

**Calculation Check:**
```
Weekly = 10 × 5 × 3 = 150 L ✓
Gross = 150 / 1000 = 0.15 mm ✓
Effective = 0.15 × 0.70 = 0.105 mm ✓
```

### Test 2: Pump Flow Calculation
**Inputs:**
- Field: 2000 m²
- Method: Pump
- Flow rate: 20 L/min
- Minutes/day: 30
- Days/week: 4
- Efficiency: 75%

**Expected Results:**
- Weekly litres: 2,400 L
- Gross depth: 1.2 mm
- Effective depth: 0.9 mm
- Per m²: 1.2 L/m²/week

**Calculation Check:**
```
Weekly = 20 × 30 × 4 = 2,400 L ✓
Gross = 2,400 / 2,000 = 1.2 mm ✓
Effective = 1.2 × 0.75 = 0.9 mm ✓
```

### Test 3: Hectare Conversion
**Inputs:**
- Field: 1 hectare (should show "10,000 m²")
- Method: Pump
- Flow: 50 L/min
- Minutes/day: 60
- Days/week: 3
- Efficiency: 80%

**Expected Results:**
- Weekly litres: 9,000 L
- Gross depth: 0.9 mm
- Effective depth: 0.72 mm
- Per m²: 0.9 L/m²/week

**Calculation Check:**
```
Area = 1 ha = 10,000 m² ✓
Weekly = 50 × 60 × 3 = 9,000 L ✓
Gross = 9,000 / 10,000 = 0.9 mm ✓
Effective = 0.9 × 0.80 = 0.72 mm ✓
```

### Test 4: Advanced Mode
**Inputs:**
- Field: 1500 m²
- Method: Advanced
- Irrigation: 25 mm/week

**Expected Results:**
- Weekly litres: 37,500 L (25 × 1500)
- Effective depth: 25 mm (direct input)
- Per m²: 25 L/m²/week

**Calculation Check:**
```
Volume = 25 × 1,500 = 37,500 L ✓
Depth = 25 mm (as entered) ✓
```

### Test 5: Rainwater Only
**Inputs:**
- Field: 1000 m²
- Method: Rainwater Only

**Expected Results:**
- Display: "Rainwater Only"
- Weekly litres: 0 L
- Effective depth: 0 mm
- Message: "Your crop rotation will depend entirely on rainfall"

### Test 6: Not Measured
**Inputs:**
- Field: 1000 m²
- Method: Not Sure / Not Measured

**Expected Results:**
- Display: "Not Yet Measured"
- Weekly litres: 0 L
- Effective depth: 0 mm
- Message: "Enter your watering details above..."

---

## Reactivity Tests

### Test 7: Plot Area Change
**Action:** Change field from 1000 m² → 2000 m²

**Expected:** With same litres per week
- mm/week should HALVE (same water over twice the area)
- Weekly litres stays SAME
- L/m²/week should HALVE

**Example:**
```
Before: 150 L over 1000 m² = 0.15 mm
After: 150 L over 2000 m² = 0.075 mm ✓
```

### Test 8: Efficiency Change
**Action:** Change efficiency from 70% → 50%

**Expected:** With same gross application
- Weekly litres stays SAME (gross water)
- Effective mm/week should DECREASE
- L/m²/week stays SAME (gross rate)

**Example:**
```
Gross: 150 L over 1000 m² = 0.15 mm
Before: 0.15 × 0.70 = 0.105 mm effective
After: 0.15 × 0.50 = 0.075 mm effective ✓
```

### Test 9: Watering Frequency Change
**Action:** Change days/week from 3 → 5

**Expected:**
- Weekly litres should INCREASE proportionally
- mm/week should INCREASE proportionally
- Calculation updates in real-time

**Example:**
```
Before: 10 L × 5 buckets × 3 days = 150 L
After: 10 L × 5 buckets × 5 days = 250 L ✓
```

### Test 10: Method Switch
**Action:** Switch from Bucket → Pump

**Expected:**
- Bucket inputs HIDE
- Pump inputs APPEAR
- Calculation RESETS to new method
- Previous values don't interfere

### Test 11: Unit Switch (m² ↔ hectares)
**Action:** Change from 10,000 m² → 1 hectare

**Expected:**
- Display shows: "1 hectares (10,000 m²)"
- Area in calculations: 10,000 m²
- Results stay SAME (conversion is transparent)

---

## Edge Cases

### Test 12: Zero Values
**Inputs:**
- Buckets/day: 0
- OR Minutes/day: 0

**Expected:**
- Weekly litres: 0
- Effective depth: 0 mm
- No errors or NaN

### Test 13: Very Small Field
**Inputs:**
- Field: 1 m²
- Weekly: 10 litres
- Efficiency: 100%

**Expected:**
- Depth: 10 mm/week
- No overflow errors
- Sensible display

### Test 14: Very Large Field
**Inputs:**
- Field: 10 hectares (100,000 m²)
- Weekly: 1,000 litres
- Efficiency: 70%

**Expected:**
- Depth: 0.007 mm/week
- Displays with appropriate precision
- No underflow errors

### Test 15: High Efficiency
**Inputs:**
- Efficiency: 95%

**Expected:**
- Slider at rightmost position
- Effective depth = 95% of gross
- Label shows "95%"

### Test 16: Low Efficiency
**Inputs:**
- Efficiency: 30%

**Expected:**
- Slider at leftmost position
- Effective depth = 30% of gross
- Label shows "30%"

---

## UI/UX Tests

### Test 17: Flow Measurement Help
**Action:** Click "How to measure flow?" button

**Expected:**
- Modal opens
- Shows step-by-step instructions
- Container + stopwatch method
- Example calculation
- Tips included
- Close button works

### Test 18: Parameter Selection
**Action:** Click between Irrigation / Soil TAW / Stress Priority

**Expected:**
- Selection highlights
- Content changes appropriately
- Irrigation shows watering inputs
- Others show sliders
- No layout shifts

### Test 19: Watering Method Buttons
**Action:** Click each watering method button

**Expected:**
- Selected method highlights (blue border)
- Appropriate inputs appear/disappear
- Smooth transitions
- No flashing or layout jumps

### Test 20: Real-Time Updates
**Action:** Type in any numeric input

**Expected:**
- Results update immediately (no button press needed)
- Smooth transitions
- No lag or freezing
- Calculations accurate

---

## Display Tests

### Test 21: Number Formatting
**Check:**
- Large numbers use commas: "1,500 litres"
- Decimals appropriate: "10.5 mm" (1 decimal)
- No unnecessary precision: Not "10.538461538 mm"

### Test 22: Unit Labels
**Check:**
- Weekly litres: "litres/week"
- Effective depth: "mm/week"
- Per m²: "litres/m²/week"
- All labels clear and consistent

### Test 23: Area Display
**Check:**
- m² mode: "1,000 m²"
- Hectare mode: "1 hectares (10,000 m²)"
- Conversion shown in parentheses
- Both units visible

### Test 24: Guidance Text
**Check:**
- Bucket size: "Common: 10-20 litres"
- Days/week: "0-7 days"
- Flow rate: "Actual measured flow"
- Efficiency: Typical values shown

---

## Integration Tests

### Test 25: Farm Selection Required
**Action:** Visit page without farm selected

**Expected:**
- Shows: "Select a farm to perform FlipPoint analysis"
- No errors in console
- Other sections still work

### Test 26: Farm Selected
**Action:** Select a farm

**Expected:**
- Full interface appears
- Default values loaded
- Calculations work
- All inputs responsive

### Test 27: FlipPoint Placeholder
**Check:** When irrigation parameter selected

**Expected:**
- Shows "Compare Crop Plans First" message
- No fake "Strategy B" result
- No arbitrary "65 mm/week" threshold
- Clear explanation of what to do next

### Test 28: Other Parameters
**Check:** Soil TAW and Stress Priority

**Expected:**
- Show appropriate sliders
- Include guidance ranges
- Also show "Compare Crop Plans First"
- No fake results

---

## Browser Compatibility

### Test 29: Input Types
**Check in multiple browsers:**
- Number inputs accept decimals
- Range sliders work smoothly
- Buttons respond to clicks
- Modal opens/closes correctly

### Test 30: Layout Responsiveness
**Check at different widths:**
- Desktop (>1024px): 3-column layout
- Tablet (768-1024px): Stacked properly
- Mobile (<768px): Single column, readable
- No horizontal scroll
- Buttons accessible

---

## Accessibility

### Test 31: Keyboard Navigation
**Action:** Tab through interface

**Expected:**
- All inputs focusable
- Tab order logical
- Enter key works on buttons
- Focus visible

### Test 32: Labels
**Check:**
- All inputs have labels
- Labels associated with inputs
- Placeholder text helpful
- Units clear

### Test 33: Color Contrast
**Check:**
- Text readable on backgrounds
- Disabled states clear
- Active states obvious
- Error messages visible

---

## Data Persistence

### Test 34: Navigate Away and Back
**Action:**
1. Enter irrigation details
2. Switch to different section
3. Return to FlipPoint

**Expected:**
- Values still present
- Calculations still correct
- No reset to defaults

### Test 35: Page Refresh
**Action:** Refresh browser

**Expected:**
- Farm selection may reset (expected)
- Section starts with defaults
- No errors
- System usable immediately

---

## Calculation Accuracy

### Test 36: Manual Verification
**For each test case:**
1. Note inputs
2. Calculate by hand or calculator
3. Compare with system result
4. Verify within rounding tolerance

**Tolerance:** ±0.1 mm or ±1 litre for rounding

### Test 37: Efficiency Math
**Verify formula:**
```
Effective = (Weekly Litres / Area m²) × (Efficiency / 100)
```

**Test cases:**
- 100% efficiency: Effective = Gross
- 50% efficiency: Effective = Half of Gross
- 70% efficiency: Effective = 0.7 × Gross

### Test 38: Area Conversion
**Verify:**
- 1 hectare = 10,000 m²
- 0.5 hectares = 5,000 m²
- 2.5 hectares = 25,000 m²

---

## Error Handling

### Test 39: Negative Values
**Action:** Try to enter negative numbers

**Expected:**
- Input prevents negative
- Or shows validation message
- No crash or NaN

### Test 40: Very Large Values
**Action:** Enter 999,999 in any field

**Expected:**
- System handles gracefully
- Result may be impractical but not broken
- No scientific notation in UI (or formatted properly)

### Test 41: Invalid Characters
**Action:** Try to type letters in number fields

**Expected:**
- Browser prevents or ignores
- No errors in console
- System remains usable

---

## Performance

### Test 42: Calculation Speed
**Action:** Rapidly change slider or type in inputs

**Expected:**
- Updates smoothly (< 100ms)
- No lag or freezing
- No memory leaks
- Browser stays responsive

### Test 43: Multiple Changes
**Action:** Change 10+ inputs in quick succession

**Expected:**
- All updates process
- Final result correct
- No race conditions
- Console clean

---

## Documentation Tests

### Test 44: Help Text Accuracy
**Verify:**
- Flow measurement instructions are correct
- Typical efficiency values are reasonable
- Examples match calculations
- Units are consistent

### Test 45: Placeholder Messaging
**Check:**
- "Not Measured" message clear
- "Compare Crop Plans First" actionable
- No contradictory messages
- Guidance points to right sections

---

## Regression Tests

### Test 46: Other Sections Unaffected
**Check that still working:**
- ✅ Farm Location selection
- ✅ Planting Suitability
- ✅ Crop Rotation comparison
- ✅ Ground Truth
- ✅ Smart Farm monitoring
- ✅ Earth Observation

### Test 47: NASA POWER Integration
**Check:**
- Climate data still loads
- Rainfall data separate from irrigation
- No interference with FlipPoint changes

### Test 48: Database Queries
**Check:**
- Farm data loads correctly
- No new database errors
- Existing APIs unchanged

---

## User Acceptance Criteria

### Test 49: Farmer Can Understand
**Show to non-technical user:**
- Can they find where to enter bucket size?
- Can they understand the results?
- Do they know what to do if "Not Measured"?
- Are the units familiar?

### Test 50: Agronomist Can Verify
**Show to technical user:**
- Can they verify calculations?
- Is mm/week still accessible?
- Can they use Advanced mode?
- Is efficiency assumption clear?

---

## Summary Checklist

### Build & Deploy
- [x] Frontend compiles without errors
- [x] TypeScript types correct
- [x] No console warnings
- [x] Bundle size acceptable (+2 kB)

### Core Functionality
- [ ] Bucket watering calculations correct
- [ ] Pump flow calculations correct
- [ ] Hectare conversion works
- [ ] Advanced mode passes through
- [ ] Rainwater/Not Measured show appropriate messages

### Reactivity
- [ ] Plot area changes update depth
- [ ] Efficiency changes update effective irrigation
- [ ] Method switches work smoothly
- [ ] All calculations real-time

### User Experience
- [ ] Flow measurement help clear
- [ ] Watering method selection intuitive
- [ ] Results display meaningful
- [ ] FlipPoint placeholder honest

### Quality Assurance
- [ ] No fake hardcoded results
- [ ] Efficiency explicitly shown
- [ ] Gross vs effective distinguished
- [ ] Unknown values handled transparently

### Preservation
- [ ] No breaking changes to other sections
- [ ] NASA POWER integration intact
- [ ] Database schemas unchanged
- [ ] Green FieldShift design preserved

---

## Testing Priority

**HIGH PRIORITY (Must Test):**
1. Basic bucket calculation (Test 1)
2. Basic pump calculation (Test 2)
3. Hectare conversion (Test 3)
4. Real-time updates (Test 20)
5. FlipPoint placeholder message (Test 27)

**MEDIUM PRIORITY (Should Test):**
6. Efficiency changes (Test 8)
7. Method switches (Test 10)
8. Flow measurement help (Test 17)
9. Other sections unaffected (Test 46)
10. Browser compatibility (Test 29-30)

**LOW PRIORITY (Nice to Test):**
11. Edge cases (Tests 12-16)
12. Large/small field extremes (Tests 13-14)
13. Keyboard navigation (Test 31)
14. Performance under load (Test 42-43)

---

## Test Results Log

**Tester:** _______________  
**Date:** _______________  
**Browser:** _______________  
**Version:** _______________

| Test # | Description | Pass/Fail | Notes |
|--------|-------------|-----------|-------|
| 1 | Basic bucket calc | | |
| 2 | Basic pump calc | | |
| 3 | Hectare conversion | | |
| ... | ... | | |

**Overall Status:** ☐ PASS ☐ FAIL  
**Blockers:** _______________  
**Recommendations:** _______________
