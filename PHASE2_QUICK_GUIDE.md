# Phase 2: Farmer Data Upload - Quick User Guide

**Your farm observations are now uploadable! 📊**

---

## What's New?

A new section **"My Farm Data & Analysis"** has been added to your dashboard, located after the "Ground Truth" section.

You can now:
- 📥 Download a CSV template
- 📤 Upload your observations from a CSV file
- ✏️ Add measurements manually
- 👁️ View all your uploaded data
- 🗑️ Delete observations if needed

---

## Quick Start

### Option 1: CSV Upload (Recommended for Multiple Observations)

1. **Select your farm** in the "Farm Location" section
2. **Scroll down** to "My Farm Data & Analysis"
3. **Click "Download CSV Template"**
4. **Open the CSV** in Excel, LibreOffice, or Google Sheets
5. **Fill in your measurements** (follow the template instructions)
6. **Save the file**
7. **Click "Upload My Data"** and select your CSV
8. **Review the preview** (shows valid/warning/error rows)
9. **Click "Import X Valid Rows"** to save

### Option 2: Manual Entry (For Single Observations)

1. **Select your farm**
2. **Scroll to "My Farm Data & Analysis"**
3. **Click "Add Measurement Manually"**
4. **Fill in the form** (only date is required)
5. **Click "Save Observation"**

---

## What You Can Record

| Measurement | Unit | Required? | Example |
|-------------|------|-----------|---------|
| Date | YYYY-MM-DD | ✅ Yes | 2026-11-15 |
| Time | HH:MM | ⚪ No | 08:30 |
| Air Temperature | °C | ⚪ No | 22.5 |
| Air Humidity | % | ⚪ No | 65 |
| Rainfall | mm | ⚪ No | 5.2 |
| Soil Moisture (Raw) | ADC 0-4095 | ⚪ No | 2450 |
| Soil Moisture (%) | % 0-100 | ⚪ No | 45 |
| Water Level | Low/OK/Unknown | ⚪ No | OK |
| Notes | Text | ⚪ No | Any notes |

**Tips**:
- Only the **date** is required
- Leave fields blank if you don't have that measurement (don't use 0)
- Use **either** raw soil moisture **or** percentage (not both)
- Add notes for context (weather, soil condition, etc.)

---

## CSV Template Format

The CSV template includes:
- ✅ Instructions in comment lines
- ✅ Column headers with clear names
- ✅ Example rows showing correct format
- ✅ Units explained for each field

**Column Order**:
```
observation_date, observation_time, temperature, humidity, rainfall,
soil_moisture_raw, soil_moisture_percent, water_level, notes
```

**Example Row**:
```csv
2026-11-15,08:30,22.5,65,,2450,,OK,"Morning reading, clear sky"
```

---

## Validation & Preview

When you upload a CSV, the system checks:

✅ **Valid** (green) - All data correct, will be imported  
⚠️ **Warning** (yellow) - Minor issues, will be imported with notes  
❌ **Error** (red) - Critical problems, will be skipped  

**Common Errors**:
- Missing date (required field)
- Invalid date format (use YYYY-MM-DD)
- Temperature out of range (-50 to 60°C)
- Humidity out of range (0-100%)
- Invalid water level (must be Low, OK, or Unknown)

**The preview shows you**:
- How many rows are valid, have warnings, or have errors
- First 20 rows with validation status
- Validation messages explaining any issues

---

## Viewing Your Data

Click **"View My Data"** to see:
- All your observations in a scrollable table
- Date, time, and all measurements
- Upload method (CSV or Manual badge)
- Delete button for each observation

**Data is sorted** by date (most recent first)

---

## Deleting Data

To delete an observation:
1. Click **"View My Data"**
2. Find the observation you want to remove
3. Click the **🗑️ Delete** button on that row
4. Confirm the deletion

⚠️ **Warning**: Deletion cannot be undone!

---

## Data Source Labeling

**All your uploaded observations are labeled as:**
- 🏷️ **"Farmer-Provided"**

**Your data is kept completely separate from:**
- NASA POWER climate data
- Open-Meteo weather forecasts
- Real ESP32 sensor readings
- Demo/simulated data

✅ **Honest Science**: We never claim your observations are NASA data or real sensor data. Your data remains clearly identified as farmer-provided.

---

## FAQ

**Q: How many observations can I upload?**  
A: No hard limit. The preview shows the first 100 rows, but you can import thousands.

**Q: What if I upload the same observation twice?**  
A: Duplicates (same farm, date, and time) are automatically skipped to prevent double-counting.

**Q: Can I edit an observation after uploading?**  
A: Not yet. You need to delete the old one and add a new one.

**Q: Will my observations be used in planting suitability calculations?**  
A: Not yet. Phase 2 focuses on data collection. Phase 3 will explore optional integration with clear documentation.

**Q: Is my data private?**  
A: Yes! All data stays in your local SQLite database. Nothing is uploaded to the cloud.

**Q: Can I export my observations?**  
A: Not yet in Phase 2. CSV export is planned for Phase 3.

**Q: What happens if I delete a farm?**  
A: All observations for that farm are also deleted (CASCADE DELETE).

**Q: Can I use both raw and calibrated soil moisture?**  
A: You can record both in the CSV, but typically you'd use one or the other. The UI shows whichever you provided.

**Q: What if I don't have all measurements for a day?**  
A: That's fine! Leave unused fields blank. Partial records are allowed as long as you have a date.

**Q: Do I need to fill in the time?**  
A: No, time is optional. If you only know the date, that's enough.

---

## Troubleshooting

**Problem**: "Please select a farm first"  
**Solution**: Go to the "Farm Location" section and click on a farm card to select it.

**Problem**: CSV upload fails with "File must be UTF-8 encoded"  
**Solution**: In Excel, use "Save As" → "CSV UTF-8 (Comma delimited)". In LibreOffice, choose UTF-8 encoding when saving.

**Problem**: "Duplicate observation" message  
**Solution**: You already have an observation for that farm on that date/time. Delete the old one first if you want to replace it.

**Problem**: Preview shows many errors  
**Solution**: Check the validation messages. Common issues are date format (must be YYYY-MM-DD) or values out of range.

**Problem**: "View My Data" shows nothing  
**Solution**: You haven't uploaded any observations yet. Use "Upload My Data" or "Add Measurement Manually" first.

---

## Best Practices

✅ **Download the template** - Don't create CSV from scratch  
✅ **Use consistent dates** - YYYY-MM-DD format only  
✅ **Record regularly** - Daily or weekly observations build a good dataset  
✅ **Add notes** - Context helps you remember conditions later  
✅ **Leave blanks** - Don't put 0 if you didn't measure it  
✅ **Review preview** - Check validation before importing  
✅ **Keep raw data** - Don't delete your original CSV files  

---

## Navigation

To access the new section:
1. Click **"My Data"** in the navigation bar at the top
2. Or scroll down after "Ground Truth"

---

## Technical Details

**Backend Endpoints**:
- `GET /api/farm-data/{farm_id}/template`
- `POST /api/farm-data/{farm_id}/upload-preview`
- `POST /api/farm-data/{farm_id}/import`
- `POST /api/farm-data/{farm_id}/observations`
- `GET /api/farm-data/{farm_id}/observations`
- `DELETE /api/farm-data/{farm_id}/observations/{obs_id}`

**Database Table**: `farmer_observations`  
**Data Source**: Always `"Farmer-Provided"`  
**Upload Methods**: `"csv"` or `"manual"`

---

## What's Next? (Phase 3)

Future improvements planned:
- 📊 Charts comparing your observations to NASA POWER
- 📥 Export your data and analysis as CSV/JSON
- 🔄 Refresh button to fetch latest NASA data
- 📈 Optional integration with planting models (with clear documentation)
- 🎯 Show agreement between your data and satellite data

---

**Need Help?**

Check:
- `PHASE2_IMPLEMENTATION_REPORT.md` - Full technical documentation
- `DATA_SOURCES.md` - Information about data source separation

---

**Phase 2 Complete! ✅**

Start uploading your observations and build your farm's data history!

🌱 Happy Farming! 🚜
