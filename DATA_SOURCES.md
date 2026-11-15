# Data Sources and Attribution

## Required Data Sources (P0)

### 1. NASA POWER

**Official Name**: NASA Prediction Of Worldwide Energy Resources

**Provider**: NASA Langley Research Center (LaRC)

**Website**: https://power.larc.nasa.gov/

**Purpose**: Historical meteorological variables for crop water calculations

**Variables Used**:
- `T2M`: Temperature at 2 Meters (°C)
- `T2M_MAX`: Maximum Temperature at 2 Meters (°C)
- `T2M_MIN`: Minimum Temperature at 2 Meters (°C)
- `PRECTOTCORR`: Precipitation Corrected (mm/day)
- `RH2M`: Relative Humidity at 2 Meters (%)
- `WS2M`: Wind Speed at 2 Meters (m/s)
- `ALLSKY_SFC_SW_DWN`: All Sky Surface Shortwave Downward Irradiance (MJ/m²/day)

**Temporal Coverage**: 1981-present (near real-time)

**Spatial Resolution**: 0.5° x 0.625° (approximately 50km at equator)

**Data Access**: Free, no authentication required for API access

**License**: NASA Open Data Policy - publicly available

**Citation**:
```
NASA Prediction of Worldwide Energy Resources (POWER) Project. 
Data obtained from the POWER Project, NASA Langley Research Center (LaRC).
Available at: https://power.larc.nasa.gov/
```

**API Endpoint**: https://power.larc.nasa.gov/api/temporal/daily/point

**Data Quality Notes**:
- Combines satellite observations with meteorological models
- Gridded estimates, not point measurements
- Quality varies by location and parameter
- Precipitation estimates have inherent uncertainty

---

### 2. Open-Meteo

**Provider**: Open-Meteo (open-source weather API)

**Website**: https://open-meteo.com/

**Purpose**: Short-term weather forecasts for irrigation planning

**Variables Used**:
- `temperature_2m`: Air temperature at 2m (°C)
- `precipitation`: Precipitation amount (mm)
- `precipitation_probability`: Probability of precipitation (%)
- `relative_humidity_2m`: Relative humidity at 2m (%)
- `wind_speed_10m`: Wind speed at 10m (m/s)

**Forecast Range**: 7 days

**Temporal Resolution**: Hourly data, aggregated to daily

**Spatial Resolution**: Varies by model, typically 11-25km

**Data Access**: Free, no authentication required

**License**: CC BY 4.0 (attribution required)

**Data Sources**: NOAA GFS, DWD ICON, Météo-France, and other national weather services

**Citation**:
```
Open-Meteo Weather Forecast API.
Data from national weather services.
Available at: https://open-meteo.com/
License: CC BY 4.0
```

**API Endpoint**: https://api.open-meteo.com/v1/forecast

**Data Quality Notes**:
- Forecast accuracy decreases with lead time
- Precipitation probability is modeled, not deterministic
- Local weather may differ from gridded forecasts

---

## Optional Enhancement Data Sources (P1/P2)

### 3. ERA5-Land (Optional)

**Provider**: Copernicus Climate Change Service (C3S), ECMWF

**Website**: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land

**Purpose**: Historical land surface and soil moisture reanalysis

**License**: Copernicus License (free with registration)

**Status**: Not yet implemented

---

### 4. Sentinel-2 (Optional)

**Provider**: European Space Agency (ESA) via Copernicus Data Space

**Website**: https://dataspace.copernicus.eu/

**Purpose**: Vegetation indices (NDVI) for bare-soil detection

**License**: Copernicus License (free with registration)

**Status**: Not yet implemented

---

### 5. NASA GPM IMERG (Optional)

**Provider**: NASA Goddard Space Flight Center

**Website**: https://gpm.nasa.gov/data

**Purpose**: High-resolution precipitation estimates

**License**: NASA Open Data Policy

**Status**: Not yet implemented

---

### 6. USDA Cropland Data Layer (Optional, US Only)

**Provider**: USDA National Agricultural Statistics Service (NASS)

**Website**: https://nassgeodata.gmu.edu/CropScape/

**Purpose**: Historical crop classification

**License**: Public domain

**Status**: Not yet implemented

---

### 7. USDA NRCS Soil Data (Optional, US Only)

**Provider**: USDA Natural Resources Conservation Service

**Website**: https://websoilsurvey.nrcs.usda.gov/

**Purpose**: Soil water-holding capacity

**License**: Public domain

**Status**: Not yet implemented

---

## Crop Knowledge Base

**Source**: FAO Irrigation and Drainage Paper No. 56 (FAO-56)

**Title**: "Crop Evapotranspiration - Guidelines for Computing Crop Water Requirements"

**Authors**: Allen, R.G., Pereira, L.S., Raes, D., Smith, M.

**Year**: 1998

**Publisher**: Food and Agriculture Organization of the United Nations

**ISBN**: 92-5-104219-5

**Website**: https://www.fao.org/3/x0490e/x0490e00.htm

**Purpose**: Crop coefficients, growth stages, rooting depths, reference evapotranspiration

**License**: FAO standard copyright (free educational use)

**Citation**:
```
Allen, R.G., Pereira, L.S., Raes, D., Smith, M. (1998). 
Crop evapotranspiration - Guidelines for computing crop water requirements. 
FAO Irrigation and Drainage Paper 56. 
Food and Agriculture Organization of the United Nations, Rome.
```

---

## Map Tiles

**Provider**: OpenStreetMap (OSM)

**Website**: https://www.openstreetmap.org/

**Purpose**: Base map tiles for farm location selection

**License**: Open Database License (ODbL)

**Tile Server**: https://tile.openstreetmap.org/

**Attribution Required**: © OpenStreetMap contributors

**Citation**:
```
OpenStreetMap contributors.
Available at: https://www.openstreetmap.org/
License: Open Database License (ODbL)
```

---

## Data Processing

All data retrieved from external sources is:
1. **Cached locally** with timestamps
2. **Attributed** to original source
3. **Quality-checked** for validity
4. **Unit-converted** when necessary
5. **Documented** with provenance metadata

## Data Limitations

### NASA POWER
- Gridded estimates, not site-specific measurements
- ~50km spatial resolution at equator
- Precipitation uncertainty higher than temperature
- Not suitable for small-scale (<1 km²) analysis

### Open-Meteo Forecasts
- Accuracy decreases beyond 3-day horizon
- Precipitation timing can be off by hours
- Local effects not captured in gridded models

### Crop Coefficients
- Generic values from FAO-56
- May not match specific cultivars
- Assume standard management practices
- Require local calibration for best accuracy

### Simulated Sensors
- **NOT REAL MEASUREMENTS**
- Software simulation only in current version
- Cannot validate model predictions without actual hardware

---

## Future Data Needs

For production deployment, farmers should supplement with:
- On-farm weather stations
- Actual soil moisture sensors
- Yield monitoring data
- Local extension service recommendations
- Regional crop coefficient calibrations

---

**Last Updated**: November 14, 2026
