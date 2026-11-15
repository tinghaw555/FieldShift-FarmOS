# FieldShift FarmOS - Farmer-Friendly Workflow Quick Start

## What's New? 🌱

Your FieldShift FarmOS dashboard now has a **farmer-friendly primary workflow** for checking planting suitability using NASA climate data!

**New Workflow:** Location → Crop → Date → Check → Compare Rotations

---

## Quick Start (2 Minutes)

### 1. Start the System

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```
Wait for: `Application startup complete`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Wait for: `Ready on http://localhost:3000`

### 2. Open Dashboard

Navigate to: **http://localhost:3000**

### 3. Try the Workflow

1. **📍 Set Your Location**
   - Click the blue **"Use My Location"** button
   - Allow browser location permission
   - See your location appear as a blue marker on the map
   - Or click anywhere on the map manually

2. **🏡 Create a Farm**
   - Click "New Farm" or click your location on the map
   - Enter farm name (e.g., "My Test Farm")
   - Coordinates auto-filled from GPS or map click
   - Click "Create"

3. **🌱 Check Planting Suitability** (NEW SECTION!)
   - Scroll to "Check Planting Suitability" section
   - **Select a crop**: Choose from dropdown (e.g., "Corn (Maize, Field)")
   - **Pick planting date**: Use calendar picker (e.g., next month)
   - Click **"Check Planting Suitability"** button

4. **📊 View Results**
   - See science-based recommendation:
     - ✅ Recommended (green)
     - ⚠️ Recommended with Caution (yellow)
     - ❌ Not Recommended (red)
   - Read climate evidence from NASA POWER data
   - Review water requirements
   - See farmer action items

5. **🔄 Compare Rotation Plans**
   - Click **"Compare Other Planting Plans"** button
   - Jumps to Rotation Lab section
   - Compare 3 different crop rotation strategies
   - See water stress differences

---

## Navigation Updates

The navigation bar now shows the farmer workflow:

1. **Farm Location** - GPS or map selection
2. **Check Planting** ⭐ NEW - Primary assessment
3. **Climate Data** - NASA POWER historical data
4. **Compare Plans** - 3-rotation comparison
5. **What If** - FlipPoint sensitivity analysis
6. **Monitoring** - ESP32 hardware integration
7. **Validation** - Ground Truth verification

---

## What the Assessment Does

### Uses Real NASA Data
- 3 years of NASA POWER historical climate
- Temperature, rainfall, solar radiation
- ~50km resolution, global coverage
- Peer-reviewed FAO-56 crop models

### Calculates
- ✅ Temperature suitability for your crop
- ✅ Seasonal water requirements
- ✅ Irrigation needs estimate
- ✅ Climate risks
- ✅ Practical farmer actions

### Shows Honestly
- "Recommended" - Good conditions
- "Recommended with Caution" - Some risks
- "Not Recommended" - Major constraints
- "Insufficient Data" - Missing information

### Includes
- Climate evidence (NASA POWER data)
- Soil considerations
- Current monitoring status (if ESP32 online)
- Risks and uncertainties
- Recommended actions
- Data sources used

---

## Example Crops to Try

**Cool Season (Plant early spring/fall):**
- Wheat - 250 days
- Peas - 100 days
- Winter Rye - 170 days

**Warm Season (Plant late spring/summer):**
- Corn - 125 days
- Soybean - 135 days
- Tomato - 145 days

**Cover Crops (Soil health):**
- Clover - 170 days (nitrogen fixer!)
- Vetch - 160 days (nitrogen fixer!)

---

## Testing Different Scenarios

### Test 1: Good Conditions
- Location: Iowa, USA (42.03°, -93.63°)
- Crop: Corn
- Date: May 15
- Expected: ✅ Recommended (good temperature, adequate rainfall)

### Test 2: Cold Warning
- Location: Alaska, USA (64.84°, -147.72°)
- Crop: Corn
- Date: May 15
- Expected: ❌ Not Recommended (too cold)

### Test 3: Irrigation Needed
- Location: Arizona, USA (33.45°, -112.07°)
- Crop: Tomato
- Date: March 15
- Expected: ⚠️ Caution (hot, dry - irrigation critical)

### Test 4: Near-Term Forecast
- Any location
- Any crop
- Date: 3 days from today
- Expected: Uses 7-day weather forecast + historical data

---

## GPS Location Features

### "Use My Location" Button
- Requests browser geolocation permission
- Shows device location as **blue marker** 📍
- Farm locations shown as **green markers** 🌾
- Accuracy displayed (±50-100m typical)

### If GPS Fails
- Manual coordinate entry still works
- Click anywhere on map still works
- Clear error messages explain why

### Privacy
- Location only used locally in your browser
- Not stored unless you create a farm
- You control permission in browser settings

---

## Hardware Integration (Optional)

If you have an ESP8266 (NodeMCU) with sensors:

**Current Status Shows:**
- "Real hardware online: 2 sensors active"
- Current temperature and soil moisture
- Device type: LOLIN NodeMCU V3 / ESP8266, DHT11

**If Hardware Offline:**
- Assessment still works using NASA POWER data
- "No real-time monitoring available" message
- Demo mode available for testing

**Hardware Setup:** See `ESP32_SETUP_GUIDE.md`

---

## What Hasn't Changed

✅ All existing features preserved:
- Green dashboard design
- One-page layout
- Leaflet world map
- NASA POWER climate data
- 3-rotation comparison
- FlipPoint sensitivity analysis
- ESP32 hardware support
- Ground Truth validation
- Data source attributions

---

## Important Limitations

### This Tool CAN:
- ✅ Compare planting dates using NASA climate data
- ✅ Estimate crop water needs (FAO-56 method)
- ✅ Identify temperature suitability
- ✅ Calculate irrigation requirements
- ✅ Assess climate risks

### This Tool CANNOT:
- ❌ Predict exact yields
- ❌ Account for pests or diseases
- ❌ Provide soil fertility advice
- ❌ Guarantee future weather
- ❌ Replace local agronomic expertise

### Data Limitations:
- NASA POWER: ~50km resolution (not point measurements)
- Historical averages don't guarantee future
- Generic soil parameters (site-specific better)
- Forecast accuracy decreases after 3 days

---

## Troubleshooting

### "Cannot connect to backend"
```bash
# Check backend is running:
cd backend
python main.py
# Should see: Uvicorn running on http://0.0.0.0:8000
```

### "Location permission denied"
- Check browser location settings
- Use manual coordinate entry instead
- Click map to set farm location

### "Failed to load crops"
- Backend must be running
- Check console for errors: F12 → Console tab
- Verify backend is on http://localhost:8000

### "Assessment failed"
- Check internet connection (NASA POWER API requires internet)
- Verify farm coordinates are valid (-90 to 90 lat, -180 to 180 lon)
- Try different planting date

### Green styling missing
- Clear browser cache: Ctrl+F5
- Stop and restart frontend: Ctrl+C, then npm run dev

---

## API Testing (Optional)

Test backend directly:
```bash
python test_planting_api.py
```

Tests:
- ✅ Crop list (20 crops)
- ✅ Planting assessment
- ✅ Near-term forecast vs. historical
- ✅ Different climate zones
- ✅ Multiple crop types

---

## Next Steps

1. **Try the Workflow** - Create a farm, check planting suitability
2. **Compare Rotations** - See how 3-rotation strategies differ
3. **Test FlipPoint** - Find critical thresholds in your decision
4. **Add Hardware** (optional) - Connect ESP8266 for real monitoring
5. **Review Documentation** - See `FARMER_WORKFLOW_IMPLEMENTATION.md`

---

## Key Files

**Frontend:**
- `src/components/sections/PlantingSuitabilitySection.tsx` - NEW workflow
- `src/components/sections/FarmSection.tsx` - GPS location
- `src/components/Map.tsx` - Device location marker

**Backend:**
- `routers/planting.py` - NEW planting assessment API
- `services/crop_knowledge.py` - 20 crop database (FAO-56)
- `services/nasa_power.py` - NASA POWER integration

**Documentation:**
- `FARMER_WORKFLOW_IMPLEMENTATION.md` - Full technical report
- `FARMER_WORKFLOW_QUICKSTART.md` - This guide
- `test_planting_api.py` - API test script

---

## Support

**For Technical Issues:**
- Check `TROUBLESHOOTING.md`
- Review browser console (F12)
- Check backend logs in terminal

**For Scientific Questions:**
- See "Data Sources & Methodology" section (bottom of dashboard)
- Review `MODEL_LIMITATIONS.md`
- Check `VALIDATION.md`

---

**Ready to start? Run the backend, start the frontend, and visit http://localhost:3000!** 🚀

The system now guides farmers through a clear workflow from location to crop to planting date to science-based recommendation, all powered by NASA Earth observations.
