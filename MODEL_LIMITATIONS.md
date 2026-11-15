# Model Limitations and Assumptions

## Critical Understanding

**FieldShift FarmOS is a decision-support tool, not a precision prediction system.**

The models provide scientifically defensible estimates to compare crop rotation strategies, but they cannot guarantee field-level accuracy or predict actual crop yields.

---

## Core Scientific Model: Daily Crop Water Balance

### Reference Evapotranspiration (ET₀)

**Method**: FAO-56 Penman-Monteith (when sufficient data available)

**Formula** (simplified representation):
```
ET₀ = [0.408 × Δ × (Rn - G) + γ × (900/(T+273)) × u₂ × (es - ea)] / [Δ + γ × (1 + 0.34 × u₂)]
```

**Required Inputs**:
- Temperature (mean, max, min)
- Solar radiation
- Wind speed at 2m
- Relative humidity or vapor pressure

**Assumptions**:
1. Grass reference surface (0.12m height)
2. Unlimited water supply to reference grass
3. Standard atmospheric conditions
4. Daily time step

**Limitations**:
- Requires complete meteorological data
- Sensitive to input data quality
- Not calibrated for specific location microclimates
- Daily timestep may miss sub-daily stress events

**Fallback**: If required variables unavailable, may use simplified Hargreaves method (temperature-based), which is less accurate but more robust to missing data.

---

### Crop Evapotranspiration (ETc)

**Method**: Crop coefficient approach from FAO-56

**Formula**:
```
ETc = Kc × ET₀
```

Where:
- **ETc** = Crop evapotranspiration (mm/day)
- **Kc** = Crop coefficient (dimensionless, varies by growth stage)
- **ET₀** = Reference evapotranspiration (mm/day)

**Crop Coefficient Stages**:
1. **Initial (Kc,ini)**: After planting, minimal canopy
2. **Development**: Vegetative growth
3. **Mid-season (Kc,mid)**: Full canopy, peak water use
4. **Late-season (Kc,end)**: Maturity, senescence

**Assumptions**:
1. Kc values from FAO-56 tables (generic, not cultivar-specific)
2. Standard crop management (adequate fertility, pest control)
3. No water stress (potential demand calculated, not actual under stress)
4. Well-managed fields
5. Growth stage timing estimated from planting date and typical durations

**Limitations**:
- **Generic Kc values**: FAO-56 provides typical ranges, not site-specific calibrations
- **Cultivar differences**: Different varieties have different water needs
- **Management sensitivity**: Poor soil or pest pressure changes water use
- **Growth stage timing**: Actual phenology varies with temperature, cultivar, planting date
- **No stress feedback**: Model calculates potential demand, doesn't adjust for actual water limitation

**Sources of Kc Uncertainty**:
- FAO-56 values may vary ±0.05 to ±0.15 depending on local conditions
- Planting and harvest date assumptions affect stage timing
- Climate affects growth rates

---

### Soil Water Balance

**Accounting Method**: Daily bookkeeping

**Formula**:
```
SWᵢ = SWᵢ₋₁ + Peff,i + Irrᵢ - ETc,i - DPᵢ - ROᵢ
```

Where:
- **SW** = Soil water content (mm)
- **Peff** = Effective precipitation (mm)
- **Irr** = Irrigation (mm)
- **ETc** = Crop evapotranspiration (mm)
- **DP** = Deep percolation/drainage (mm)
- **RO** = Runoff (mm)

**Soil Storage Bounds**:
```
0 ≤ SW ≤ TAW
```

Where:
- **TAW** = Total Available Water = (FC - WP) × root_depth
- **FC** = Field capacity (volumetric water content)
- **WP** = Wilting point (volumetric water content)

**Assumptions**:
1. **Uniform soil profile**: Single-layer model
2. **Effective precipitation**: Fixed percentage of total rainfall (e.g., 80%)
3. **Rooting depth**: Generic values from FAO-56 or user input
4. **Field capacity and wilting point**: Generic soil texture assumptions or user input
5. **Drainage**: Excess water above FC drains within one day
6. **No lateral flow**: Water moves only vertically
7. **Initial condition**: Soil at field capacity at start of simulation (or user-defined)

**Limitations**:
- **Soil heterogeneity ignored**: Real fields have variable soil properties
- **Single rooting depth**: Roots grow over time; model may use fixed or simple staged values
- **Effective rainfall crude**: Runoff and infiltration depend on rainfall intensity, soil, slope, cover
- **No groundwater interaction**: Model assumes no capillary rise from water table
- **Drainage simplification**: Real drainage is gradual, not instant
- **No salinity or toxicity**: Model doesn't account for salt accumulation or poor-quality water

**Typical TAW Values** (example for 1m root depth):
- Sandy soil: ~50-80 mm
- Loam: ~120-180 mm
- Clay: ~150-220 mm

These are estimates; actual values require soil testing.

---

### Water Stress Calculation

**Threshold Approach**:

Water stress occurs when soil water drops below a crop-specific threshold:

```
RAW = p × TAW
```

Where:
- **RAW** = Readily Available Water (mm)
- **p** = Depletion fraction before stress (from FAO-56, typically 0.4-0.6)
- **TAW** = Total Available Water (mm)

**Stress Indicator**:
```
If SW < RAW: potential stress day
```

**Assumptions**:
1. Stress is binary (yes/no) rather than gradual
2. Single threshold applies to entire growth cycle (actually varies by stage)
3. Stress immediately affects crop (no recovery time)

**Limitations**:
- **Binary stress**: Real stress is gradual and cumulative
- **No stress intensity**: Model doesn't quantify severity of stress
- **No phenological sensitivity**: Some growth stages are more sensitive than others
- **No yield relationship**: Model doesn't convert stress days to yield loss

**Why No Yield Prediction?**:
- Yield response to water stress is crop-, cultivar-, and timing-specific
- Requires calibration with local yield data
- Other factors (nutrients, pests, diseases) also affect yield
- Without validated local data, yield predictions would be unreliable

---

## Crop Rotation Comparison

### Scoring Methodology

Rotations are compared across multiple dimensions:

1. **Seasonal Water Demand**: Sum of ETc over growing season
2. **Water Stress Risk**: Count of days when SW < RAW
3. **Irrigation Requirement**: Estimated irrigation needed to avoid stress
4. **Bare Soil Days**: Count of days without crop cover
5. **Crop Diversity**: Number of different crop families
6. **Nitrogen Fixation**: Presence of legumes (qualitative)

**Assumptions**:
1. **Equal weighting**: Each factor weighted equally unless farmer adjusts
2. **Historical climate**: Uses past weather as proxy for future conditions
3. **Management equivalence**: All rotations managed with same skill level
4. **No economic factors**: Doesn't consider crop prices, input costs, labor

**Limitations**:
- **No yield estimates**: Model compares water risk, not profitability
- **Simplified diversity scoring**: Doesn't account for pest/disease cycles
- **Historical climate analog**: Past weather doesn't predict future conditions
- **No equipment constraints**: Doesn't model machinery availability, timing conflicts
- **No market dynamics**: Doesn't consider crop prices, contracts, storage

**What This Comparison Does**:
- Identifies which rotation has higher water stress risk under historical conditions
- Shows trade-offs between water use, bare soil, diversity
- Highlights seasons when irrigation is most critical

**What It Doesn't Do**:
- Guarantee one rotation will produce higher yields
- Account for farmer experience with specific crops
- Predict actual future weather
- Optimize for profit or other economic outcomes

---

## FlipPoint Sensitivity Analysis

### Methodology

FlipPoint identifies parameter thresholds where the preferred rotation changes.

**Variable Inputs**:
- Soil water-holding capacity (TAW)
- Irrigation availability (mm/week or total seasonal)
- Farmer priority weights (e.g., stress minimization vs. diversity)

**Process**:
1. Sweep parameter through plausible range
2. Recalculate rotation comparison at each step
3. Identify crossover point where ranking changes

**Assumptions**:
1. **Single parameter at a time**: Doesn't test parameter interactions
2. **Linear parameter space**: Doesn't capture non-linear thresholds
3. **Independent recalculation**: Each step uses same historical climate

**Limitations**:
- **Computational**: Only tests discrete parameter values
- **Parameter independence**: Real parameters may be correlated (e.g., soil type affects both TAW and Kc)
- **No uncertainty propagation**: Doesn't quantify confidence in flip point location
- **User-selected parameters only**: Doesn't test sensitivity to Kc, rooting depth, effective rainfall, etc.

**Value**:
- Shows which assumptions matter most for decision
- Identifies where better local data would be most valuable
- Makes model sensitivity transparent

---

## Historical Climate Scenarios

### Approach

Model replays each rotation using actual historical NASA POWER daily climate data.

**Scenarios**:
- Typical year (median rainfall)
- Dry year (e.g., 10th percentile rainfall)
- Wet year (e.g., 90th percentile rainfall)
- Hot year (highest mean temperature)

**Assumptions**:
1. **Historical analog**: Past weather is relevant to future decisions
2. **Independent years**: Each year treated independently
3. **Planting date fixed**: Same calendar dates used across years
4. **No climate trend**: Doesn't account for long-term warming or precipitation changes

**Limitations**:
- **Past ≠ Future**: Climate change may make historical extremes obsolete
- **Limited sample**: 40 years of data may not capture rarest events
- **No seasonal forecast**: Doesn't use current El Niño, La Niña, etc.
- **Fixed management**: Doesn't simulate farmer adaptation during season

**Proper Interpretation**:
- "In a year like 2012, this rotation would have experienced X stress days"
- NOT "Next year will be like 2012"

---

## Data Source Limitations

### NASA POWER

**Spatial Resolution**: ~50 km

**Implications**:
- Local rainfall variability not captured
- Microclimates (slopes, valleys) not resolved
- Individual farm conditions may differ significantly

**Temporal Resolution**: Daily

**Implications**:
- Sub-daily rainfall intensity not captured
- Dew and frost events may be missed
- Diurnal temperature extremes smoothed

**Data Quality**:
- Precipitation: Satellite estimates have ~20-30% uncertainty
- Temperature: Generally accurate (±1-2°C)
- Solar radiation: Modeled, not directly measured
- Wind, humidity: Modeled, coarse resolution

### Open-Meteo Forecasts

**Forecast Horizon**: 7 days

**Accuracy**:
- Days 1-3: Generally reliable for temperature
- Days 4-7: Decreasing skill, especially for precipitation
- Precipitation probability: Indicates likelihood, not certainty

**Limitations**:
- Cannot predict beyond ~10 days with skill
- Local convective rainfall often missed
- Timing errors of several hours common

---

## Simulated Sensors (Current Implementation)

**CRITICAL LIMITATION**: The current Smart Farm section uses **SOFTWARE SIMULATION ONLY**.

**What Is Simulated**:
- Soil moisture readings
- Air temperature and humidity (DHT22)
- Water level in reservoir
- Valve open/closed state

**What This Means**:
- **No real measurements**: All sensor values are generated by code
- **No model validation**: Cannot compare predictions to reality
- **No actual irrigation control**: Valve commands don't affect real hardware

**Purpose of Simulation**:
- Demonstrate user interface workflow
- Test irrigation decision logic
- Prepare data structures for future hardware integration

**Future Hardware Phase**:
- ESP32 microcontroller
- Actual DHT22 sensor
- Actual soil moisture sensor
- Actual water level sensor
- Safe low-voltage irrigation valve control

**Until Real Hardware**:
- Ground Truth Lab shows framework only
- Forecast error metrics use simulated "observations"
- No claims of validated model accuracy

---

## What This Tool Can and Cannot Do

### ✅ What FieldShift CAN Do

1. **Compare rotation water demand** using established FAO-56 methodology
2. **Identify stress risk patterns** under historical climate conditions
3. **Expose model sensitivity** through FlipPoint analysis
4. **Integrate NASA Earth observations** with local farm decisions
5. **Explain recommendations** with transparent calculations
6. **Respect farmer constraints** through Farmer's Veto
7. **Identify bare soil periods** that may warrant cover crops
8. **Provide weather-aware irrigation advisories** (when integrated with real sensors)

### ❌ What FieldShift CANNOT Do

1. **Predict actual crop yields** without local calibration data
2. **Guarantee superior performance** of recommended rotations
3. **Replace local agricultural expertise** and extension services
4. **Account for all management factors** (pests, diseases, fertility, timing)
5. **Predict weather beyond ~7 days** with useful skill
6. **Measure actual field conditions** without real sensors
7. **Optimize for profit** without economic data
8. **Account for climate change trends** in long-term planning

---

## Recommended Usage

1. **Use as a comparison tool**: Evaluate relative differences, not absolute predictions
2. **Validate locally**: Test recommendations on small areas before full adoption
3. **Combine with expertise**: Consult agricultural extension services
4. **Update assumptions**: Input your own soil data, crop coefficients, constraints
5. **Monitor reality**: Install sensors to compare forecasts vs. observations
6. **Iterate**: Adjust model parameters based on actual field performance

---

## Validation Status

### Unit Tests
- ✅ Water balance accounting
- ✅ ET₀ calculation formulas
- ✅ Crop coefficient application
- ✅ Soil storage bounds enforcement
- ✅ Date range handling
- ✅ Unit conversions

### Integration Tests
- ✅ NASA POWER data retrieval
- ✅ End-to-end rotation comparison
- ✅ FlipPoint parameter sweeps
- ✅ Forecast data processing

### Field Validation
- ❌ **Not yet performed**: No comparison with actual farm measurements
- ❌ **No yield validation**: No actual yield data collected
- ❌ **No sensor validation**: No real sensor data for Ground Truth Lab

**To validate model performance**, farmers would need to:
1. Install calibrated sensors
2. Record actual irrigation amounts
3. Measure crop yields
4. Compare model estimates to observations over multiple seasons
5. Calibrate Kc and soil parameters to local conditions

---

## Uncertainty Quantification

The model **does not provide confidence intervals** or uncertainty estimates.

**Sources of Uncertainty**:
1. **Input data**: NASA POWER precipitation ~20-30% error
2. **Crop coefficients**: FAO-56 Kc values ±10-20% variability
3. **Soil parameters**: Generic TAW values ±30% without soil testing
4. **Effective rainfall**: Crude approximation, ~20-40% error
5. **Growth stage timing**: ±1-2 weeks depending on temperature
6. **Future weather**: Forecast skill decreases with lead time

**Combined Effect**: Water stress day predictions likely have ±20-40% uncertainty, varying by location, season, and data quality.

**Implications**:
- Small differences between rotations may not be meaningful
- Model is most useful for identifying large differences and trade-offs
- Local calibration substantially improves accuracy

---

## Regulatory and Liability

**FieldShift FarmOS is a research and educational tool.**

- **Not certified** for regulatory compliance
- **Not validated** for crop insurance decisions
- **Not a substitute** for professional agronomic advice
- **No warranty** of fitness for any particular purpose
- **User assumes all risk** for management decisions

Farmers should:
- Verify recommendations with local experts
- Start with small-scale trials
- Monitor results carefully
- Maintain crop insurance and standard practices
- Not rely solely on model outputs for critical decisions

---

**Last Updated**: November 14, 2026

**Version**: 1.0 (P0A Core Foundation)
