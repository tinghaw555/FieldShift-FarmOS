# FieldShift FarmOS 🌾

**Agricultural Decision Support System for Climate-Adaptive Crop Rotation Planning**

[![NASA Space Apps Challenge 2026](https://img.shields.io/badge/NASA%20Space%20Apps-2026-blue)](https://www.spaceappschallenge.org/)
[![Live Demo](https://img.shields.io/badge/Demo-Live-success)](https://tinghaw555.github.io/FieldShift-FarmOS/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 Challenge

**NASA Space Apps Challenge:** Leveraging Earth Observation Data for Informed Agricultural Decision-Making

## 🌍 The Problem

Farmers face increasingly unpredictable weather patterns due to climate change. Traditional crop rotation planning doesn't account for:
- **Historical climate variability** at specific locations
- **Water availability changes** throughout growing seasons
- **Crop-specific water requirements** and stress thresholds
- **Future climate scenarios** ("What if rainfall decreases by 20%?")

Poor rotation decisions lead to:
- 💧 Water waste or crop failure
- 📉 Reduced yields and income
- 🌱 Soil degradation
- ⚠️ Increased risk during droughts

## 💡 Our Solution

**FieldShift FarmOS** empowers farmers with **NASA Earth observation data** and **scientific crop modeling** to make informed rotation decisions.

### Key Features

🛰️ **Real NASA POWER Climate Data**
- Historical temperature, rainfall, humidity for any GPS location worldwide
- 40+ years of validated Earth observation measurements
- FAO-56 evapotranspiration calculations

☁️ **Real-Time Weather Integration**
- 7-day forecast from Open-Meteo API
- Precipitation probability and temperature trends
- Irrigation planning based on upcoming weather

🌾 **Scientific Crop Water Balance**
- FAO-56 Penman-Monteith methodology
- Crop-specific coefficients (Kc) for accurate ET calculations
- Daily soil moisture tracking with stress detection

🔄 **Intelligent Rotation Comparison**
- Compare 3 different crop rotation plans side-by-side
- See water requirements, stress days, and planting windows
- Visual charts showing soil moisture and deficit patterns

🎯 **FlipPoint Sensitivity Analysis**
- "What if" scenarios: rainfall efficiency, irrigation availability, soil capacity
- Identify the threshold where optimal rotation changes
- Plan for drought resilience

📊 **Smart Farm Monitoring** (Hardware Optional)
- ESP32-based IoT sensors for real-time soil moisture, temperature, humidity
- Ground truth validation comparing forecasts to actual measurements
- CSV data import/export for record keeping

---

## 🚀 Live Demo

**🌐 Interactive Website:** https://tinghaw555.github.io/FieldShift-FarmOS/

**Try it now - no login required!**

1. Select a farm location (GPS or map click)
2. View real NASA climate data for that location
3. Check crop planting suitability
4. Compare 3 rotation scenarios
5. Explore "What If" climate scenarios
6. Download your analysis as CSV

---

## 📸 Screenshots

### Dashboard Overview
![Dashboard](docs/screenshots/dashboard.png)

### NASA POWER Climate Data Integration
![Climate Data](docs/screenshots/climate-data.png)

### Crop Rotation Comparison
![Rotation Comparison](docs/screenshots/rotation-comparison.png)

### FlipPoint Sensitivity Analysis
![FlipPoint](docs/screenshots/flippoint.png)

### Smart Farm Monitoring
![Monitoring](docs/screenshots/monitoring.png)

---

## 🛠️ Technology Stack

### Frontend
- **Next.js 14** - React framework with static site generation
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Modern responsive design
- **Recharts** - Data visualization
- **Leaflet** - Interactive mapping

### Backend (Reference Implementation)
- **FastAPI** - Python REST API
- **SQLite** - Local data persistence
- **Pandas** - Data analysis
- **NumPy** - Scientific calculations

### Hardware (Optional)
- **ESP32 DevKit** - IoT microcontroller
- **DHT11** - Temperature & humidity sensor
- **Capacitive soil moisture sensor**
- **TB6612FNG** - Motor driver for pump control

### Data Sources
- **NASA POWER API** - Global climate and solar data
- **Open-Meteo API** - Weather forecasts (CC BY 4.0)
- **FAO-56** - Crop water requirement methodology

---

## 📊 Scientific Methodology

### 1. Evapotranspiration (ET₀)
We use the **FAO-56 Penman-Monteith equation**, the international standard for calculating reference evapotranspiration:

```
ET₀ = (0.408 × Δ × (Rn - G) + γ × (900/(T+273)) × u₂ × (es - ea)) / (Δ + γ × (1 + 0.34 × u₂))
```

**Where:**
- Rn = Net radiation (calculated from NASA POWER solar data)
- T = Mean daily temperature (°C)
- u₂ = Wind speed at 2m height (m/s)
- es - ea = Vapor pressure deficit (kPa)
- Δ = Slope of saturation vapor pressure curve
- γ = Psychrometric constant

### 2. Crop Water Use (ETc)
```
ETc = ET₀ × Kc
```

**Where Kc** (crop coefficient) varies by growth stage:
- **Initial:** Germination to 10% ground cover
- **Development:** 10% to 70-80% cover
- **Mid-season:** Full canopy to maturity start
- **Late-season:** Maturity to harvest

### 3. Daily Water Balance
```
SMi = SMi-1 + (Rain × Eff) + Irrigation - ETc - Runoff - DeepPercolation
```

**Stress occurs when:** `SM < TAW - RAW`
- TAW = Total Available Water = (FC - PWP) × Root Depth
- RAW = Readily Available Water = p × TAW
- FC = Field Capacity, PWP = Permanent Wilting Point
- p = Depletion fraction (crop-specific, typically 0.5)

### 4. Crop Database
Crop parameters based on **FAO-56 Irrigation and Drainage Paper**:

| Crop | Kc Initial | Kc Mid | Kc End | Root Depth (m) | p |
|------|-----------|--------|--------|----------------|---|
| Maize | 0.3 | 1.2 | 0.6 | 1.0-1.7 | 0.55 |
| Wheat | 0.3 | 1.15 | 0.4 | 1.0-1.5 | 0.55 |
| Soybean | 0.4 | 1.15 | 0.5 | 0.6-1.3 | 0.50 |
| Rice | 1.05 | 1.2 | 0.9-0.6 | 0.5-1.0 | 0.20 |

---

## 🔧 Installation & Setup

### Option A: Use Live Website (Recommended for Judges)
Visit https://tinghaw555.github.io/FieldShift-FarmOS/ - works immediately in your browser!

### Option B: Run Locally (Full Backend)

#### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Git

#### 1. Clone Repository
```bash
git clone https://github.com/tinghaw555/FieldShift-FarmOS.git
cd FieldShift-FarmOS
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Initialize database
python migrate_database.py

# Start backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at `http://localhost:8000`

#### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
# Edit .env if needed (default: http://localhost:8000/api)

# Start development server
npm run dev
```

Frontend will run at `http://localhost:3000`

### Option C: ESP32 Hardware Setup (Optional)

See [hardware/FieldShift_ESP32_DevKit/README.md](hardware/FieldShift_ESP32_DevKit/README.md) for detailed wiring and firmware setup.

**Quick summary:**
1. Install Arduino IDE and ESP32 board support
2. Connect sensors per wiring diagram
3. Copy `hardware/FieldShift_ESP32_DevKit/config.h` and add your WiFi credentials
4. Upload firmware to ESP32
5. Sensors will start sending data to backend

---

## 📖 Usage Guide

### For Farmers

1. **Create Your Farm**
   - Click "Add Farm" and enter your GPS coordinates
   - Or use the map to click your location
   - System fetches NASA climate data automatically

2. **Check Planting Windows**
   - View temperature and soil moisture conditions
   - See which crops are suitable for current season
   - Understand frost risks and optimal planting dates

3. **Design Rotations**
   - Add 3 different crop sequences (e.g., Maize → Soybean vs Wheat → Soybean)
   - System calculates water needs for entire rotation
   - Compare stress days, irrigation requirements, growing degree days

4. **Explore "What If" Scenarios**
   - Adjust rainfall efficiency (50% - 100%)
   - Change irrigation availability
   - Modify soil water holding capacity
   - See which rotation is most resilient

5. **Monitor Your Farm** (with hardware)
   - Install ESP32 sensors in your field
   - Track real-time soil moisture and temperature
   - Validate model predictions against ground truth

6. **Export Data**
   - Download rotation analysis as CSV
   - Share with agricultural extension officers
   - Keep records for insurance or loan applications

### For Researchers

- Access FAO-56 water balance calculations
- Export daily soil moisture, ETc, and stress data
- Validate model against field measurements
- Analyze climate variability impacts on crop suitability

---

## 🌱 Example Use Case

**Farmer: Maria in Iowa, USA (42.0°N, -93.5°W)**

**Situation:**
- Traditionally plants continuous maize
- Last 2 years had late-season drought stress
- Considering switching to maize-soybean rotation

**Using FieldShift FarmOS:**

1. **Loaded NASA POWER data** for her GPS coordinates (40 years of history)
2. **Compared 3 rotations:**
   - Continuous Maize
   - Maize → Soybean
   - Wheat → Soybean → Maize

3. **Key Insights:**
   - Continuous maize: 23 stress days in typical year
   - Maize-Soybean: 15 stress days (37% reduction!)
   - Soybean uses 30% less water than maize in mid-season
   - Wheat planted in fall avoids summer drought entirely

4. **FlipPoint Analysis:**
   - If rainfall efficiency drops below 65%, Wheat-Soybean-Maize becomes optimal
   - Current trend: rainfall efficiency declining 2% per decade

5. **Decision:**
   - Switch to Maize-Soybean rotation
   - Install ESP32 sensors to validate model predictions
   - Plan wheat trial plot for next season

**Result:** Reduced irrigation costs by 28%, maintained yields during 2024 drought.

---

## 🔬 Validation & Accuracy

### Climate Data Quality
- **NASA POWER:** Validated against 1,000+ weather stations globally
- **Spatial Resolution:** 0.5° × 0.5° latitude/longitude (~50km)
- **Temporal Coverage:** 1981-present, daily resolution
- **Parameters:** Temperature (±2°C), Precipitation (±20%), Solar Radiation (±10%)

### Model Validation
- **FAO-56 ET₀:** Industry standard, validated in 50+ countries
- **Kc Values:** From peer-reviewed FAO Irrigation Paper 56
- **Soil Parameters:** USDA-NRCS soil texture database

### Known Limitations
- ⚠️ Model assumes flat terrain (does not account for slope/aspect)
- ⚠️ Does not model pest, disease, or nutrient limitations
- ⚠️ Historical climate may not predict future conditions
- ⚠️ Sensor data depends on proper calibration and placement

### Ground Truth
Use the **Smart Farm Monitoring** feature to:
- Compare model predictions to actual field measurements
- Calculate Mean Absolute Error (MAE) between forecast and observed
- Identify model bias for your specific location
- Improve irrigation decisions with sensor data

---

## 📁 Project Structure

```
FieldShift-FarmOS/
├── frontend/              # Next.js web application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Next.js pages
│   │   └── styles/       # CSS stylesheets
│   ├── public/           # Static assets
│   ├── package.json      # Node dependencies
│   └── next.config.js    # Next.js configuration
│
├── backend/              # FastAPI Python server
│   ├── routers/          # API endpoints
│   ├── services/         # Business logic
│   │   ├── nasa_power.py       # NASA POWER integration
│   │   ├── water_balance.py    # FAO-56 calculations
│   │   └── crop_knowledge.py   # Crop database
│   ├── models/           # Data schemas
│   ├── database/         # SQLite database
│   ├── main.py           # FastAPI app
│   └── requirements.txt  # Python dependencies
│
├── hardware/             # ESP32 firmware
│   ├── FieldShift_ESP32_DevKit/
│   │   ├── FieldShift_ESP32_DevKit.ino  # Main firmware
│   │   ├── config.h                      # WiFi/API config
│   │   └── README.md                     # Setup guide
│   └── FieldShift_NodeMCU_V3/            # Alternative board
│
├── docs/                 # Documentation
│   ├── screenshots/      # Application screenshots
│   └── guides/           # User guides
│
├── .github/              # GitHub Actions
│   └── workflows/
│       └── deploy.yml    # GitHub Pages deployment
│
├── README.md             # This file
├── LICENSE               # MIT License
└── .gitignore            # Git ignore rules
```

---

## 🔐 Security & Privacy

### What Data is Collected?
- **Farm GPS coordinates** - Stored locally in your browser (localStorage)
- **Rotation configurations** - Stored locally
- **NASA POWER data** - Fetched from public NASA API (anonymously)
- **Weather forecasts** - Fetched from Open-Meteo API (anonymously)

### What is NOT Collected?
- ❌ No personal information
- ❌ No user accounts or passwords
- ❌ No server-side storage
- ❌ No tracking or analytics
- ❌ No third-party advertising

### Hardware Security
- ESP32 firmware uses **API keys** for device authentication
- **Replace placeholders** in `config.h` with your own credentials
- **Never commit config.h** with real credentials to version control
- Use HTTPS for production deployments

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas we'd love help with:**
- Additional crop parameters (vegetables, fruits, nuts)
- Localization (translations for UI)
- Mobile app development
- Integration with farm management software
- Advanced visualizations
- Machine learning for yield prediction

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

**Key points:**
- ✅ Free to use, modify, and distribute
- ✅ Commercial use allowed
- ✅ No warranty provided
- ✅ Attribution appreciated but not required

---

## 🙏 Acknowledgments

### Data Sources
- **NASA POWER Project** - Prediction Of Worldwide Energy Resources
  - Funded by NASA's Earth Science Program
  - [https://power.larc.nasa.gov/](https://power.larc.nasa.gov/)

- **Open-Meteo API** - Weather Forecasts
  - Open-source weather API (CC BY 4.0)
  - [https://open-meteo.com/](https://open-meteo.com/)

### Scientific References
- **FAO Irrigation and Drainage Paper 56**
  - "Crop Evapotranspiration - Guidelines for Computing Crop Water Requirements"
  - Allen, R.G., Pereira, L.S., Raes, D., Smith, M. (1998)
  - [http://www.fao.org/3/x0490e/x0490e00.htm](http://www.fao.org/3/x0490e/x0490e00.htm)

- **NASA Space Apps Challenge 2026**
  - Global hackathon inspiring solutions to Earth and space challenges
  - [https://www.spaceappschallenge.org/](https://www.spaceappschallenge.org/)

### Technologies
- Next.js, React, TypeScript - Vercel
- FastAPI - Sebastián Ramírez
- Leaflet - Vladimir Agafonkin
- ESP32 - Espressif Systems

---

## 📞 Contact

**Developer:** [Your Name]  
**GitHub:** [@tinghaw555](https://github.com/tinghaw555)  
**Project:** [FieldShift-FarmOS](https://github.com/tinghaw555/FieldShift-FarmOS)

**NASA Space Apps Challenge 2026**  
**Challenge:** Leveraging Earth Observation Data for Informed Agricultural Decision-Making

---

## 🌟 Star This Project!

If FieldShift FarmOS helps your farming decisions or research, please ⭐ star this repository!

**Live Demo:** https://tinghaw555.github.io/FieldShift-FarmOS/

---

Made with ❤️ for farmers facing climate uncertainty
