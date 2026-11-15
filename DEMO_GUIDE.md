# FieldShift FarmOS - Demo Guide

## NASA Space Apps Challenge 2026 - Field Shift

**Purpose**: This guide walks through a complete demonstration of FieldShift FarmOS, showcasing how NASA Earth observations support agricultural decision-making.

---

## Prerequisites

### Running the Application

1. **Backend** (Terminal 1):
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

2. **Frontend** (Terminal 2):
```bash
cd frontend
npm install  # First time only
npm run dev
```

3. **Access**: Open http://localhost:3000

---

## Demo Scenario: Iowa Corn Farmer

**Context**: You're a corn-soybean farmer in Iowa considering rotation changes to adapt to increasing drought risk identified in NASA climate data.

---

## Part 1: Farm Setup (5 minutes)

### Step 1: Select Location

1. Navigate to **World Map & Farm Selection**
2. Click on central Iowa (approximately 42°N, -93.5°W)
3. Name your farm: "Prairie View Farm"
4. Click **Create**

**What to highlight**:
- ✅ Works anywhere in the world
- ✅ Single interface, no separate "modes"
- ✅ Data availability shown transparently

### Step 2: Configure Soil

1. Select "Prairie View Farm" from the farm list
2. Scroll to farm configuration (if implemented)
3. Set soil parameters:
   - Soil type: Loam
   - Field capacity: 30%
   - Wilting point: 15%
   - Rooting depth: 1.0 m

**What to highlight**:
- Farmer can input local knowledge
- Default values provided but adjustable
- Affects water-holding capacity calculations

---

## Part 2: Earth Observation (10 minutes)

### Step 3: NASA POWER Historical Climate

1. Scroll to **Earth Observation & Weather** section
2. Observe NASA POWER climate summary (auto-loads)
3. Point out:
   - Historical annual precipitation
   - Average temperatures
   - Growing season conditions
   - Data source attribution

**Key talking points**:
- 📡 Real NASA satellite and model data
- 📊 40+ years of daily climate records
- 🌍 Global coverage
- 🔬 Scientific foundation for crop water models

### Step 4: Weather Forecast

1. View 7-day Open-Meteo forecast
2. Show:
   - Daily temperature ranges
   - Expected precipitation
   - Forecast issue time

**Key talking points**:
- 🌦️ Integrates near-term weather
- ⏰ Updates irrigation recommendations
- 📉 Accuracy decreases with lead time (honest!)

---

## Part 3: Rotation Lab (15 minutes)

### Step 5: Define Current Rotation

1. Scroll to **Crop Rotation Lab**
2. Select **A: Current Rotation** tab
3. Configure:
   - Crop: Corn
   - Planting: 05-01
   - Harvest: 10-15

**What to highlight**:
- Simple calendar-based input
- Familiar to farmers
- Links to FAO-56 crop database

### Step 6: Small Shift Alternative

1. Click **B: Small Shift** tab
2. Configure:
   - Crop: Soybean
   - Planting: 05-15
   - Harvest: 10-01

**Explain**:
- Nitrogen-fixing legume
- Different water requirements
- Later planting date

### Step 7: Alternative Rotation

1. Click **C: Alternative** tab
2. Click **Add Crop** to create two crops:
   - Crop 1: Wheat (03-15 to 07-30)
   - Crop 2: Clover (08-01 to 11-15)
3. Click **Add Crop** for cover crop

**Explain**:
- Double-cropping strategy
- Reduces bare soil periods
- More complexity but potential benefits

### Step 8: Compare Rotations

1. Click **Run Water Balance Model**
2. Observe estimated results:
   - Seasonal water demand
   - Stress days
   - Bare soil periods
   - Crop diversity score

**Key scientific points**:
- 💧 Uses FAO-56 Penman-Monteith ET₀
- 🌱 Crop coefficients from peer-reviewed research
- 📈 Daily soil water balance
- ⚖️ Transparent comparison, not hidden AI

---

## Part 4: FlipPoint Analysis (10 minutes)

### Step 9: Test Irrigation Sensitivity

1. Scroll to **FlipPoint: Sensitivity Analysis**
2. Select **Irrigation Capacity** parameter
3. Move slider from 20 to 80 mm/week
4. Observe:
   - Preferred rotation changes
   - FlipPoint threshold identified
   - Explanation updates

**Key innovation**:
- 🎯 **"What would change my mind?"**
- 🔄 Re-runs actual model at each value
- 💡 Shows where better data/infrastructure matters
- 🚫 Not guessing—actual calculation

### Step 10: Test Soil Capacity

1. Switch to **Soil Water Capacity (TAW)**
2. Adjust slider
3. Show how soil quality affects rotation choice

**Explain**:
- Better soil = more buffering capacity
- Could justify more water-intensive crops
- Identifies value of soil testing

### Step 11: Bare-Soil Guardian

1. Scroll down to **Bare-Soil Guardian** panel
2. Review:
   - Identified exposed periods
   - Rainfall risk during gaps
   - Cover crop suggestions

**Highlight**:
- 🛡️ Links crop calendar to historical rainfall
- 🌾 Identifies erosion vulnerability
- ✅ Actionable recommendations

---

## Part 5: Smart Farm Simulator (10 minutes)

### Step 12: Sensor Monitoring

1. Scroll to **Smart Farm & Irrigation Simulator**
2. **READ THE RED WARNING BOX** (critical!)
3. Observe simulated sensors:
   - Air temperature
   - Air humidity
   - Soil moisture
   - Reservoir level

**CRITICAL talking points**:
- ⚠️ SOFTWARE SIMULATION ONLY
- 🖥️ No actual hardware connected
- 🔮 Demonstrates future ESP32 integration
- 🔬 Framework for Ground Truth validation

### Step 13: Irrigation Recommendation

1. View current irrigation advisory
2. Explain recommendation logic:
   - Soil moisture threshold
   - Reservoir availability
   - Weather forecast integration
   - Safety checks

### Step 14: Simulate Irrigation

1. Adjust soil moisture slider to 25% (low)
2. Observe recommendation changes to "Water Recommended"
3. Click **Irrigate 3 min** button
4. Watch:
   - Valve status updates
   - Safety confirmations
   - Experiment recorded

**Emphasize**:
- 👨‍🌾 Farmer approval required
- ✅ Safety checks enforced
- 📝 All actions logged for analysis
- 🚫 No real hardware affected

---

## Part 6: Ground Truth (10 minutes)

### Step 15: Forecast Error Metrics

1. Scroll to **Ground Truth & Evidence**
2. **READ THE YELLOW WARNING BOX**
3. View forecast error metrics:
   - Temperature MAE
   - Observation count
   - Data source

**Key points**:
- 📊 Framework for validation ready
- 🔬 Shows scientific methodology
- ⏳ Awaiting real sensor hardware
- ✅ Honest about limitations

### Step 16: Irrigation Experiments

1. View experiment log
2. Review recorded irrigation events:
   - Initial conditions
   - Duration
   - Recommendation followed

**Explain**:
- 📓 Documents decision-making
- 🔍 Enables learning from experience
- 📈 Could calibrate model over time
- 🎯 Supports adaptive management

### Step 17: Evidence Inspector

1. Review **What You Should Verify** list
2. Discuss scientific transparency:
   - What we know
   - What we don't know
   - How to improve

**Highlight**:
- 🔬 Scientific honesty
- 📖 Open about limitations
- 🎓 Educational approach
- ✅ Not overselling capabilities

---

## Part 7: Connecting the Story (5 minutes)

### NASA Space Apps Challenge Connection

**Challenge: Field Shift - Adapting Farms**

**FieldShift FarmOS demonstrates**:

1. **NASA Data Integration** ✅
   - NASA POWER climate observations
   - 40+ years global coverage
   - Powers crop water calculations

2. **Decision Support** ✅
   - Compare rotation strategies
   - Quantify water stress risk
   - Identify vulnerabilities

3. **Transparency** ✅
   - Model limitations documented
   - Calculations explainable
   - No hidden AI black box

4. **Farmer Control** ✅
   - Farmer's Veto system
   - FlipPoint sensitivity analysis
   - Ground Truth validation framework

5. **Global Applicability** ✅
   - Single interface worldwide
   - Adapts to data availability
   - Doesn't require US-only datasets

---

## Key Demo Messages

### What Makes FieldShift Different

1. **Honest About Uncertainty**
   - Clear limitations documentation
   - Simulation clearly labeled
   - No false precision

2. **Scientific Rigor**
   - FAO-56 peer-reviewed methods
   - Unit-tested calculations
   - Literature benchmarking

3. **Farmer Agency**
   - FlipPoint: "Change my mind"
   - Farmer's Veto constraints
   - Transparent trade-offs

4. **Validation Framework**
   - Ground Truth methodology ready
   - Experiment tracking built-in
   - Path from simulation to reality

---

## Common Questions & Answers

### Q: "Why is everything simulated?"

**A**: This is Phase P0A (Core Foundation). We're building the web application architecture and scientific models first. ESP32 hardware integration is a separate phase after the software is validated. This prevents firmware bugs from blocking the NASA challenge submission.

### Q: "Can it predict yields?"

**A**: No, by design. Yield prediction requires multi-year field trials, local calibration, and factors beyond water (pests, nutrients, etc.). FieldShift compares relative water stress risk—that's scientifically defensible without field validation.

### Q: "How accurate are the recommendations?"

**A**: Model outputs have ±20-40% uncertainty (documented in MODEL_LIMITATIONS.md). Accuracy improves with local soil data, sensor calibration, and field experience. Start with small trials!

### Q: "Does it work in [my country]?"

**A**: Yes! NASA POWER has global coverage. Some optional datasets (US CDL, NRCS soils) are US-only, but the core functionality works worldwide using the same interface.

### Q: "What about climate change?"

**A**: Historical NASA data shows past climate patterns. Future climate scenarios could be added in Phase P2. FlipPoint analysis helps identify which parameters matter most for adaptation planning.

---

## Demo Timing

| Section | Time | Key Highlight |
|---------|------|---------------|
| Farm Setup | 5 min | Global map, any location |
| Earth Observation | 10 min | Real NASA POWER data |
| Rotation Lab | 15 min | FAO-56 water balance |
| FlipPoint | 10 min | Sensitivity analysis innovation |
| Smart Farm | 10 min | Simulation + future hardware |
| Ground Truth | 10 min | Validation framework |
| Q&A | 10 min | Scientific honesty |
| **Total** | **70 min** | **Full demo** |

**Quick version (30 min)**: Farm setup + Earth Obs + Rotation Lab + FlipPoint highlights

---

## Post-Demo Discussion

### Technical Achievements

- ✅ One-page worldwide dashboard
- ✅ Real NASA POWER integration
- ✅ Scientific FAO-56 water balance
- ✅ Novel FlipPoint sensitivity analysis
- ✅ Ground Truth validation framework
- ✅ Transparent uncertainty documentation

### Future Roadmap

**Phase P0B**: Weather-aware irrigation, risk timeline  
**Phase P1**: ERA5-Land, Sentinel-2 vegetation  
**Phase P2**: SMAP, GLDAS, advanced features  
**Hardware**: ESP32 firmware, real sensor validation

---

## Competition Positioning

**FieldShift's Competitive Strengths**:

1. **Scientific Integrity**: Peer-reviewed methods, not proprietary AI
2. **Global Applicability**: One interface, worldwide
3. **Farmer Agency**: FlipPoint innovation, Farmer's Veto
4. **Honest Limitations**: Transparent about what it can't do
5. **Validation Path**: Ground Truth framework ready

**Not just a mockup**—functional web app with real NASA data and defensible science.

---

## Final Notes

Remember to emphasize:
- This is a **hackathon implementation** in ~48 hours
- Core functionality **actually works** (not vaporware)
- Scientific methodology is **sound and documented**
- Path to **real-world deployment** is clear
- **Honest** about current limitations

**The goal**: Show judges a functional, scientifically credible tool that meaningfully uses NASA data to support agricultural adaptation decisions.

---

**Questions?** See README.md, MODEL_LIMITATIONS.md, VALIDATION.md, and AI_DISCLOSURE.md for complete documentation.
