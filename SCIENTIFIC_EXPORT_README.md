# Scientific Results Export - Quick Guide

**Feature**: Export scientific calculation results from FieldShift FarmOS  
**Status**: ✅ READY TO USE  
**Added**: November 15, 2026

---

## What's New?

A new **"Export Scientific Results"** button (emerald green, 🔬 icon) has been added to the "My Farm Data & Analysis" section.

---

## How It Works

### 1. Three Export Options

The "My Farm Data & Analysis" section now has **three export buttons**:

| Button | Color | Purpose |
|--------|-------|---------|
| 🔃 **Refresh Available Data** | Teal | Get latest NASA POWER & Open-Meteo data |
| 📦 **Export Raw Data** | Indigo | Download observations, forecasts, rotation plans |
| 🔬 **Export Scientific Results** | Emerald | Guidance for capturing calculated results |

### 2. What You Can Export

**Raw Data (📦 button)**:
- NASA POWER historical climate observations
- Open-Meteo weather forecasts
- Farmer-provided field observations
- Sensor telemetry readings
- Crop rotation structure (PLANS only, not calculations)

**Scientific Results (🔬 button)**:
- Provides guidance on capturing calculation results
- Explains on-demand calculation architecture
- Directs you to dashboard sections

---

## Why Two Export Buttons?

**📦 Export Raw Data**: Downloads actual observations, forecasts, and data you've uploaded

**🔬 Export Scientific Results**: Explains how to capture calculated analysis results (planting suitability, water balance, etc.)

---

## How to Capture Scientific Results

Scientific calculations (planting suitability, crop water balance, rotation comparisons, FlipPoint thresholds) are performed **on-demand** in the dashboard sections.

### Step-by-Step

1. **Run Calculation**:
   - Navigate to dashboard section (Planting Suitability, Rotation Lab, FlipPoint, etc.)
   - Enter your parameters (crop, date, rotations, etc.)
   - Click calculation button
   - View results immediately

2. **Capture Results**:
   - **Option A**: Screenshot the results table or chart
   - **Option B**: Copy key values to your notes
   - **Option C**: Use browser Print → Save as PDF
   - **Option D**: Click 🔬 button for detailed guidance

3. **Export Raw Data** (Optional):
   - Click 📦 button to download underlying observations
   - Select datasets (NASA POWER, farmer observations, etc.)
   - Choose format (CSV or JSON)
   - Download ZIP file

---

## Available Calculations

### 1. Planting Suitability

**Location**: "Check Planting Suitability" section  
**How**: Select crop & date → Click "Check Suitability"  
**Results**: Recommendation, reasons, climate evidence, farmer actions  
**Data Source**: NASA POWER (3-year average) + FAO-56 crop parameters

### 2. Crop Water Balance

**Location**: "Crop Rotation Lab" section  
**How**: Create rotations → Click "Compare Rotations"  
**Results**: Water demand, irrigation needs, stress days  
**Data Source**: NASA POWER daily data + FAO-56 ET0 calculation

### 3. Rotation Comparison

**Location**: "Crop Rotation Lab" section  
**How**: Select rotations → View comparison table  
**Results**: Rankings, water stress comparison, preferred rotation  
**Data Source**: NASA POWER + irrigation capacity constraints

### 4. FlipPoint Threshold

**Location**: "FlipPoint & Agricultural Risk" section  
**How**: Configure parameters → Click "Calculate FlipPoint"  
**Results**: Threshold value, chart, stress curves  
**Data Source**: NASA POWER + iterative water balance analysis

### 5. Ground Truth Accuracy

**Location**: "Ground Truth & Evidence" section  
**How**: Upload observations → View accuracy metrics  
**Results**: MAE, bias, observation count  
**Data Source**: Open-Meteo forecasts vs farmer observations

---

## Why On-Demand Calculations?

**Benefits**:
- ✅ Always uses latest climate data
- ✅ No stale or outdated results
- ✅ Fast calculations (< 15 seconds)
- ✅ Clear separation: data vs analysis
- ✅ No database bloat

**Trade-off**:
- ⚠️ Must capture results manually (screenshot/notes)
- ⚠️ Cannot export historical calculations (yet)

---

## Tips for Capturing Results

### For Documentation

1. **Screenshot**: Use Snipping Tool (Windows) or Cmd+Shift+4 (Mac)
2. **Print to PDF**: Use browser Print → Save as PDF
3. **Copy to Notes**: Select text, copy key values
4. **Organize**: Create folder structure (by farm, by date, by analysis type)

### For Excel/Google Sheets

1. **Run calculation in dashboard**
2. **Screenshot results table**
3. **Manually transcribe values to spreadsheet** OR
4. **Export raw data separately** (📦 button) and combine

### For Reports

1. **Run all needed calculations**
2. **Screenshot each result**
3. **Insert screenshots into document**
4. **Add captions with calculation parameters**
5. **Include this note**: "Calculated using NASA POWER data + FAO-56 methodology"

---

## Scientific Integrity

### Always Label Results

When sharing or reporting calculation results:

✅ **DO**:
- Label as "MODEL CALCULATION" or "Calculated Result"
- Note data source: "NASA POWER + FAO-56"
- Include calculation date
- Specify units (mm, °C, days, etc.)
- Mention parameters used (crop, date, year, etc.)

❌ **DON'T**:
- Call them "observed measurements"
- Mix with real sensor readings without labels
- Claim they are "NASA verified" farmer data
- Present as guaranteed predictions

### Example Citation

```
Planting Suitability for Corn (May 1, 2024)
Recommendation: Recommended
Data Source: NASA POWER 3-year historical average (2021-2023)
Methodology: FAO-56 crop water requirements
Calculation Date: November 15, 2026
Result Type: MODEL CALCULATION (not observed measurement)
```

---

## Future Enhancements

### Planned Features

1. **"Export This Result" Buttons**: Add export button directly in each dashboard section
2. **Database Persistence**: Store calculation results for historical export
3. **Clipboard API**: Copy results to clipboard with one click
4. **PDF Reports**: Generate formatted reports with charts
5. **Batch Export**: Export multiple calculations at once

### Current Workaround

The backend API endpoint for scientific results export already exists (`POST /api/farm-data/{farm_id}/export/scientific-results`) but requires calculation parameters. Future UI enhancement will capture parameters automatically from dashboard forms.

---

## FAQ

### Q: Why can't I auto-export scientific results like raw data?

**A**: Scientific results are calculated on-demand using the latest climate data and aren't stored in the database. This design ensures you always get fresh calculations with current data, not stale cached results.

### Q: How do I export past calculations?

**A**: Currently, you can re-run calculations with the same parameters. Future enhancement will add database persistence for historical export.

### Q: What's the difference between "Raw Data" and "Scientific Results"?

**A**:
- **Raw Data**: Actual observations, forecasts, measurements (what was observed)
- **Scientific Results**: Calculated analysis, recommendations (what was computed from observations)

### Q: Can I automate scientific exports?

**A**: Yes! The backend API endpoint exists (`POST /api/farm-data/{farm_id}/export/scientific-results`). You can call it with calculation parameters to get CSV or JSON exports. Future UI update will make this easier.

### Q: Are calculations accurate?

**A**: Calculations use:
- NASA POWER satellite observations (~50km resolution)
- FAO-56 internationally recognized crop water methodology
- 3-year climate averages for reliability

They provide reliable comparative analysis for decision support. Local conditions may vary.

### Q: What if NASA POWER service is down?

**A**: The system uses cached data automatically and labels it clearly as "cached". You'll see a warning but calculations still work.

---

## Support

### Getting Help

1. **Click 🔬 Button**: In-app guidance with detailed instructions
2. **Read Documentation**: `SCIENTIFIC_EXPORT_TEST_GUIDE.md` for detailed workflow
3. **Check Reports**: `SCIENTIFIC_RESULTS_EXPORT_IMPLEMENTATION.md` for technical details

### Reporting Issues

If you encounter problems:
1. Note which calculation type (planting, rotation, FlipPoint, etc.)
2. Note error message (if any)
3. Check browser console for errors (F12 → Console tab)
4. Try again with different parameters

---

## Quick Reference

### Button Locations

**Farm Data & Analysis Section** (after selecting a farm):
- Row 1: Download Template, Upload Data, Add Manually, View Data
- Row 2: **🔃 Refresh**, **📦 Export Raw Data**, **🔬 Export Scientific Results**

### Calculation Sections

1. **Check Planting Suitability** → Top of dashboard
2. **Crop Rotation Lab** → Middle section
3. **FlipPoint & Agricultural Risk** → Middle-lower section
4. **Ground Truth & Evidence** → Lower section
5. **Smart Farm Monitoring** → Bottom section

### Export Formats

- **CSV**: Excel/Google Sheets compatible
- **JSON**: Programmatic access
- **ZIP**: Multiple CSVs + README

---

## Version History

### v1.0.0 (November 15, 2026)

- ✅ Added "Export Scientific Results" button
- ✅ Added guidance dialog with navigation instructions
- ✅ Backend API endpoint for future automation
- ✅ Clear labeling: MODEL vs OBSERVED data
- ✅ Comprehensive documentation

---

**Status**: ✅ READY TO USE  
**For Help**: Click the 🔬 **Export Scientific Results** button in the app  
**Documentation**: See `SCIENTIFIC_RESULTS_EXPORT_IMPLEMENTATION.md` for details

🌱 **Happy Farming with NASA Data!** 🚜

