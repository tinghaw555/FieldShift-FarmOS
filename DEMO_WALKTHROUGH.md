# FieldShift FarmOS - Smart Farm Demo Walkthrough

## 🎬 What You'll See When You Run the Application

---

## Step 1: Start the Application

### Terminal Commands

```bash
# Backend (Terminal 1)
cd "c:\Users\acer\Nasa challenge\backend"
python -m uvicorn main:app --reload

# Frontend (Terminal 2)
cd "c:\Users\acer\Nasa challenge\frontend"
npm run dev
```

### Expected Output

**Backend:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Frontend:**
```
▲ Next.js 14.0.4
- Local:        http://localhost:3000
✓ Ready in 2.5s
```

Open browser: **http://localhost:3000**

---

## Step 2: Dashboard Loads

You'll see:
- ✅ **Three farm cards** (Sunrise Valley Farm, Green Horizon Farm, Millstone Fields)
- ✅ **Green dashboard theme** (forest colors)
- ✅ **View All Farms** button
- ✅ **Leaflet map** showing farm locations

---

## Step 3: Select a Farm

Click any farm card (e.g., "Sunrise Valley Farm")

The page scrolls to show **8 sections:**

1. 📍 Farm Details & Map
2. 🌍 Earth Observation Data
3. 🌤️ Climate & Weather
4. 🌱 Planting Suitability
5. 🔄 Compare Crop Rotations
6. 📊 What If Conditions Change? (FlipPoint)
7. 🛰️ Ground Truth Lab
8. **💻 Smart Farm & Irrigation** ← Focus here

---

## Step 4: Smart Farm Section (Offline State)

Scroll to **"Smart Farm & Irrigation"**

You'll see:

```
┌─────────────────────────────────────────────────┐
│ 💻 Smart Farm & Irrigation          ⚪ Offline │
├─────────────────────────────────────────────────┤
│                                                 │
│ 📡 Sensor Readings                              │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │         📡 WifiOff Icon                  │  │
│  │                                          │  │
│  │      ESP32 Device Offline                │  │
│  │  Live sensor readings unavailable        │  │
│  │                                          │  │
│  │      [Enable Demo Mode]                  │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Status Badge:** Grey "Offline" indicator

---

## Step 5: Click "Enable Demo Mode"

### The Transform Happens

**Before:** Grey offline box  
**After:** Fully functional sensor dashboard

You'll see:

```
┌──────────────────────────────────────────────────────────────┐
│ 💻 Smart Farm & Irrigation    🔵 DEMO MODE — SIMULATED DATA │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ 🔵 DEMO MODE — SIMULATED SENSOR DATA                        │
│ Playing back historical simulated samples from dataset.      │
│ These are not current physical sensor measurements.          │
│                                                              │
│ Dataset: 120 readings          Playback: 1 of 120           │
│ Device ID: SIM_ESP32_DEMO_001  Sample Time: 08:00:00        │
└──────────────────────────────────────────────────────────────┘
```

---

## Step 6: Sensor Cards Appear

### Four Sensor Cards Side-by-Side

#### 🌡️ Temperature Card (Orange/Red gradient)
```
┌──────────────────────────────┐
│ 🌡️ Temperature               │
│            DATASET PLAYBACK  │
│                              │
│         28.3°C               │
│                              │
│ Simulated                    │
└──────────────────────────────┘
```

#### 💧 Humidity Card (Blue/Cyan gradient)
```
┌──────────────────────────────┐
│ 💧 Humidity                  │
│            DATASET PLAYBACK  │
│                              │
│         70%                  │
│                              │
│ Simulated                    │
└──────────────────────────────┘
```

#### 📊 Soil Moisture Card (Emerald/Green gradient)
```
┌──────────────────────────────┐
│ 📊 Soil Moisture             │
│            DATASET PLAYBACK  │
│                              │
│         53%                  │
│                              │
│ Soil ADC: 2186 / 4095        │
│ Simulated estimate           │
└──────────────────────────────┘
```

#### 💧 Reservoir Level Card (Cyan/Blue gradient)
```
┌──────────────────────────────┐
│ 💧 Reservoir Level           │
│            DATASET PLAYBACK  │
│                              │
│         93%                  │
│                              │
│ Level ADC: 3012 / 4095       │
│ Simulated estimate           │
└──────────────────────────────┘
```

**Key Feature:** ✅ **NO SLIDERS** - All read-only!

---

## Step 7: Watch Auto-Playback

### Every 5 Seconds, Values Update

**Second 0:**
```
Playback: 1 of 120
Temp: 28.3°C  |  Humidity: 70%  |  Soil: 53%  |  Reservoir: 93%
Sample Time: 08:00:00
```

**Second 5:**
```
Playback: 2 of 120
Temp: 28.4°C  |  Humidity: 70.5%  |  Soil: 53.9%  |  Reservoir: 93.2%
Sample Time: 08:01:00
```

**Second 10:**
```
Playback: 3 of 120
Temp: 28.5°C  |  Humidity: 69.8%  |  Soil: 53.2%  |  Reservoir: 92.7%
Sample Time: 08:02:00
```

**Second 15:**
```
Playback: 4 of 120
Temp: 28.5°C  |  Humidity: 69.5%  |  Soil: 52.9%  |  Reservoir: 92.8%
Sample Time: 08:03:00
```

Values change **automatically** - no user interaction needed!

---

## Step 8: Pump Control Section

On the right side, you'll see:

```
┌─────────────────────────────────────┐
│ Water Pump Control                  │
├─────────────────────────────────────┤
│                                     │
│ Pump Status (Simulated)        OFF │
│                                     │
│           ┌──────────┐              │
│           │●     OFF │              │
│           └──────────┘              │
│           Grey Toggle               │
│                                     │
│ ○ Pump OFF — Simulation             │
│ Simulated irrigation stopped.       │
│ This is software-only demonstration.│
│                                     │
│ ⚠️ Safety: Demo Mode never sends    │
│ commands to physical hardware.      │
└─────────────────────────────────────┘
```

---

## Step 9: Toggle the Pump (Demo)

### Click the Toggle Switch

**Action:** Click toggle  
**Result:** Switches from grey to green

```
┌─────────────────────────────────────┐
│ Pump Status (Simulated)         ON │
│                                     │
│           ┌──────────┐              │
│           │ ON     ●│              │
│           └──────────┘              │
│           Green Toggle              │
│                                     │
│ ✓ Pump ON — Simulation              │
│ Simulated irrigation running.       │
│ No physical hardware is activated.  │
└─────────────────────────────────────┘
```

**Click again:** Switches back to OFF (grey)

**Important:** Sensor values continue following CSV dataset - pump toggle doesn't affect them!

---

## Step 10: Watch the Loop

After **10 minutes** (120 readings × 5 seconds):

```
Playback: 119 of 120
Temp: 28.5°C  |  Humidity: 69.4%  |  Soil: 41.6%  |  Reservoir: 85.1%
Sample Time: 09:58:00
```

**5 seconds later:**

```
Playback: 120 of 120
Temp: 28.3°C  |  Humidity: 69.7%  |  Soil: 41.8%  |  Reservoir: 84.7%
Sample Time: 09:59:00
```

**5 seconds later - LOOPS BACK:**

```
Playback: 1 of 120
Temp: 28.3°C  |  Humidity: 70%  |  Soil: 53.4%  |  Reservoir: 93.0%
Sample Time: 08:00:00
```

Continues forever! Perfect for demo videos.

---

## Step 11: Try Other Features

### All Phase 1-3 Features Still Work

**Earth Observation:**
- Click "Fetch Latest Observations"
- See NASA satellites listed
- No changes from before

**Planting Suitability:**
- Select crop (corn, wheat, soybean, etc.)
- Enter growth stage
- Click "Calculate Suitability"
- Works perfectly

**Crop Rotations:**
- Configure rotations A, B, C
- Click "Compare 3 Crop Plans & Save"
- See water demand analysis
- Rotations saved for FlipPoint

**FlipPoint:**
- Enter water supply measurements
- Click "Calculate FlipPoint Threshold"
- See rotation preference changes
- Works as before

**Ground Truth:**
- Upload farmer observations CSV
- Manual entry form available
- Validation works

**Scientific Export:**
- Click "Export Scientific Results"
- Downloads ZIP with all calculations
- No simulated sensor data included

---

## Step 12: Switch Farms

**Action:** Select different farm from dropdown

**Result:**
1. Smart Farm section resets to "Offline"
2. Demo Mode disabled
3. Must click "Enable Demo Mode" again
4. Playback starts from reading #1

**This is correct behavior** - Demo Mode doesn't persist across farms.

---

## Step 13: If You Have Physical ESP32

### Connect Real Hardware

1. Power on ESP32
2. ESP32 connects to Wi-Fi
3. ESP32 registers: `POST /hardware/telemetry`
4. Frontend detects connection

### Status Changes

**Badge:** "Offline" → "Connected" (green)

**Sensor Cards:** "DATASET PLAYBACK" → "LIVE" (green)

**Demo Section:** Hidden

**Physical Pump Section:** Appears

```
┌─────────────────────────────────────┐
│ Physical Pump Status           OFF  │
│                                     │
│           ┌──────────┐              │
│           │●     OFF │              │
│           └──────────┘              │
│                                     │
│ Device: 🟢 Online                   │
│ Reservoir: ✓ OK                     │
│ Commissioned: Yes                   │
└─────────────────────────────────────┘
```

**Click Toggle:**
1. Shows confirmation dialog
2. "⚠️ Confirm Physical Pump Start"
3. Safety checklist displayed
4. User clicks "Confirm Start"
5. API call: `POST /hardware/pump/command`
6. ESP32 receives command
7. Physical relay activates
8. Water pump runs for 10 seconds
9. Toggle shows "ON" (green)

---

## What Makes This Demo-Ready?

### ✅ Fully Automatic
- No manual slider adjustment
- No button clicking during playback
- Set it and forget it

### ✅ Professional Appearance
- Clean card design
- Clear labels
- Smooth updates
- Color-coded badges

### ✅ 10+ Minute Runtime
- 120 readings × 5 seconds = 10 minutes
- Loops continuously
- Perfect for video recording

### ✅ Educational Value
- Shows real sensor data patterns
- Temperature/humidity correlation visible
- Soil moisture depletion realistic
- Reservoir level drawdown gradual

### ✅ NASA Space Apps Ready
- No hardware required
- Works on any computer
- Professional for judges
- Clear "simulated" labeling

---

## Common Questions

### Q: Can I speed up playback?
**A:** Currently fixed at 5 seconds. Could be made configurable in future.

### Q: Can I add my own CSV?
**A:** Yes! Replace `frontend/public/simulated_sensor_data.csv` with your data. Must match the same column structure.

### Q: Does pump toggle affect sensor values?
**A:** No. Demo pump is software-only. Sensor values follow CSV dataset exactly.

### Q: Can I pause playback?
**A:** Not currently. Playback is continuous. You can disable Demo Mode and re-enable to restart.

### Q: What if CSV fails to load?
**A:** Error message displayed: "Failed to load simulated sensor dataset". Check browser console for details.

### Q: Is this data real?
**A:** No. The CSV contains simulated realistic values for demonstration purposes. Clearly labeled "SIMULATED_DEMO" throughout.

### Q: Can I export this data?
**A:** The simulated readings are not included in scientific exports. Only real calculations and farmer-provided data are exported.

### Q: Will this work offline?
**A:** Frontend needs to be running (npm run dev), but no internet required. CSV loads from local file.

---

## Tips for Recording Demo Video

### 🎥 Video Recording Checklist

1. **Clean Browser Window**
   - Hide bookmarks bar
   - Full screen (F11)
   - Zoom to 100%
   - Clear console errors first

2. **Start at Farm Selection**
   - Show 3 farm cards
   - Select farm
   - Scroll to Smart Farm section

3. **Enable Demo Mode**
   - Show "Offline" state first
   - Click "Enable Demo Mode"
   - Let banner appear fully

4. **Highlight Key Features**
   - Point to "120 readings" info
   - Show "Playback 1 of 120"
   - Note sample timestamp
   - Wait for 2-3 updates (10-15 seconds)

5. **Show All 4 Sensors**
   - Emphasize: NO SLIDERS
   - Point out ADC values
   - Show "DATASET PLAYBACK" badges

6. **Demo Pump Toggle**
   - Toggle OFF → ON
   - Show green state
   - Read safety warning
   - Toggle ON → OFF
   - Show grey state

7. **Show Other Features**
   - Scroll to Crop Rotations
   - Quick FlipPoint demo
   - Show these still work

8. **End Strong**
   - Scroll back to Smart Farm
   - Show playback still advancing
   - Emphasize automatic nature

### 🎬 Suggested Narration

> "FieldShift FarmOS provides smart irrigation monitoring for smallholder farmers. Here's our Smart Farm dashboard in Demo Mode, playing back 120 realistic sensor readings. Notice how temperature, humidity, soil moisture, and reservoir level update automatically every 5 seconds - no manual adjustment needed. The pump control provides a simple ON/OFF toggle, clearly labeled as simulation. All values are read-only and sourced from our validated dataset, maintaining data integrity for scientific analysis."

---

## 🎉 Ready to Demo!

Your FieldShift FarmOS Smart Farm section is now:
- ✅ Fully functional
- ✅ Professionally designed
- ✅ Demo-ready
- ✅ Safety-verified
- ✅ NASA Space Apps worthy

**Enjoy your demonstration!** 🚀🌾

---

**Document Version:** 1.0  
**Last Updated:** November 15, 2026  
**Status:** Production Ready
