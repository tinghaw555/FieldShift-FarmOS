# FieldShift FarmOS - Farm Management & Data Analysis Implementation Plan

**Status**: Ready for Implementation  
**Priority**: High - Improves usability for multi-farm management  
**Scope**: Targeted improvements, NO redesign

---

## Implementation Phases

### Phase 1: Farm List Management (HIGH PRIORITY)
**Goal**: Show max 3 farms by default with expandable list

**Backend Changes**:
```python
# New database columns
ALTER TABLE farms ADD COLUMN is_favorite INTEGER DEFAULT 0;
ALTER TABLE farms ADD COLUMN last_selected_at TIMESTAMP;

# New endpoints
PUT /api/farms/{farm_id}/favorite
PUT /api/farms/{farm_id}/rename
POST /api/farms/bulk-delete
GET /api/farms/search?q={query}
```

**Frontend Changes**:
- `FarmSection.tsx`: Add collapsed/expanded states
- Show 3 farms max in default view
- "View All Farms (12)" button when > 3 farms
- Scrollable container (max-height: 400px) in expanded view
- "Show Less" button in expanded view
- Star icon for favorites
- Search box (filters client-side initially)

**Files to Modify**:
- `frontend/src/components/sections/FarmSection.tsx`
- `backend/routers/farms.py`
- `backend/database/db.py` (migration)

---

### Phase 2: Farm Actions (HIGH PRIORITY)
**Goal**: Rename, Delete, Favorite farms safely

**Features**:
- Three-dot menu on each farm card
- Rename dialog with validation
- Delete confirmation with impact warning
- Favorite/unfavorite toggle
- Bulk delete mode (optional checkbox UI)

**Safety Checks Before Delete**:
```sql
-- Check what would be affected
SELECT 
  (SELECT COUNT(*) FROM rotations WHERE farm_id = ?) as rotation_count,
  (SELECT COUNT(*) FROM sensor_readings WHERE farm_id = ?) as sensor_count,
  (SELECT COUNT(*) FROM irrigation_experiments WHERE farm_id = ?) as experiment_count,
  (SELECT COUNT(*) FROM hardware_devices WHERE farm_id = ?) as device_count
```

**Confirmation Dialog**:
```
⚠️ Delete Farm "My Farm"?

This will also delete:
- 3 crop rotations
- 125 sensor readings
- 2 irrigation experiments
- 1 connected device

This action cannot be undone.

[Cancel] [Delete Farm]
```

**Files to Modify**:
- `frontend/src/components/sections/FarmSection.tsx`
- `backend/routers/farms.py`

---

### Phase 3: Data Upload & Export (MEDIUM PRIORITY)
**Goal**: Allow farmers to import/export their own data

**New Section in Dashboard** (after Ground Truth):
```tsx
<section id="farm-data" className="scroll-mt-20">
  <FarmDataSection farm={selectedFarm} />
</section>
```

**Features**:
- CSV template download
- CSV upload with preview
- Manual data entry form
- Export farm analysis
- Data source labels (Farmer-Provided vs Real Sensor vs NASA)

**CSV Template** (downloadable):
```csv
# FieldShift FarmOS - Farmer Observations Template
# Farm: [Farm Name]
# Upload Date: [Date]
#
# Instructions:
# - observation_date: YYYY-MM-DD format (required)
# - temperature: Degrees Celsius (optional)
# - humidity: Percent 0-100 (optional)
# - rainfall: Millimeters (optional)
# - soil_moisture_raw: ADC reading 0-4095 (optional)
# - soil_moisture_percent: Only if calibrated (optional)
# - water_level: "Low", "OK", or "Unknown" (optional)
# - notes: Any text (optional)

observation_date,temperature,humidity,rainfall,soil_moisture_raw,soil_moisture_percent,water_level,notes
2024-01-15,22.5,65,,2450,45,OK,Morning reading
2024-01-16,23.1,63,5.2,,,OK,Light rain overnight
```

**Database Schema**:
```sql
CREATE TABLE farmer_observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  farm_id INTEGER NOT NULL,
  observation_date DATE NOT NULL,
  temperature REAL,
  humidity REAL,
  rainfall REAL,
  soil_moisture_raw INTEGER,
  soil_moisture_percent REAL,
  water_level TEXT,
  notes TEXT,
  data_source TEXT DEFAULT 'Farmer-Provided',
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  validation_status TEXT DEFAULT 'valid',
  FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
);
```

**New Backend Endpoints**:
```python
GET  /api/farms/{farm_id}/observations/template  # Download CSV template
POST /api/farms/{farm_id}/observations/upload    # Upload CSV
POST /api/farms/{farm_id}/observations/manual    # Manual entry
GET  /api/farms/{farm_id}/observations           # List observations
DELETE /api/farms/{farm_id}/observations/{obs_id} # Delete observation
GET  /api/farms/{farm_id}/export                 # Export all data
POST /api/farms/{farm_id}/refresh-data           # Refresh available data
```

**Files to Create**:
- `frontend/src/components/sections/FarmDataSection.tsx`
- `backend/routers/farm_data.py`

---

### Phase 4: Data Source Honesty (HIGH PRIORITY)
**Goal**: Always label data sources correctly

**Data Source Labels**:
```typescript
enum DataSource {
  NASA_POWER = "NASA POWER",
  OPEN_METEO = "Open-Meteo Forecast",
  FARMER_PROVIDED = "Farmer-Provided",
  REAL_SENSOR = "Real Sensor (ESP32)",
  DEMO_MODE = "Demo Mode (Simulated)",
  CALCULATED = "Calculated (Model Output)"
}
```

**Display Requirements**:
- Every data visualization must show source
- Sensor readings: Add badge "🟢 Real Sensor" or "🔵 Demo Mode"
- CSV exports: Include "data_source" column
- Never mix sources without clear labeling

**Example**:
```tsx
<div className="flex items-center gap-2">
  <span className="text-sm font-medium">Temperature: 22.5°C</span>
  <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded">
    Demo Mode
  </span>
</div>
```

**Files to Modify**:
- `frontend/src/components/sections/SmartFarmSection.tsx`
- `backend/routers/simulator.py`
- `backend/models/schemas.py`

---

### Phase 5: Refresh & Export (MEDIUM PRIORITY)
**Goal**: Update data and export analysis

**Refresh Available Data**:
- Fetches latest NASA POWER data for selected farm
- Fetches latest weather forecast
- Updates cache timestamps
- Shows "Last updated: 2 hours ago"
- Respects API rate limits

**Export Analysis**:
```json
{
  "farm": {
    "id": 1,
    "name": "My Farm",
    "latitude": 39.8283,
    "longitude": -98.5795
  },
  "export_date": "2024-01-15T10:30:00Z",
  "data_sources": {
    "nasa_power": {
      "available": true,
      "date_range": "2023-01-01 to 2023-12-31",
      "last_retrieved": "2024-01-15T08:00:00Z",
      "source": "NASA POWER"
    },
    "weather_forecast": {
      "available": true,
      "issue_time": "2024-01-15T06:00:00Z",
      "forecast_days": 7,
      "source": "Open-Meteo"
    },
    "farmer_observations": {
      "count": 15,
      "date_range": "2024-01-01 to 2024-01-15"
    },
    "real_sensors": {
      "available": false,
      "reason": "Hardware not yet connected"
    }
  },
  "planting_suitability": { ... },
  "crop_rotations": { ... },
  "flippoint_results": { ... }
}
```

**Files to Modify**:
- `frontend/src/components/sections/FarmDataSection.tsx`
- `backend/routers/farm_data.py`
- `backend/routers/climate.py`

---

## Database Migrations

### Migration 1: Farm Management Enhancements
```sql
-- Add favorite and last selected tracking
ALTER TABLE farms ADD COLUMN is_favorite INTEGER DEFAULT 0;
ALTER TABLE farms ADD COLUMN last_selected_at TIMESTAMP;

-- Create index for favorites and search
CREATE INDEX idx_farms_favorite ON farms(is_favorite DESC, last_selected_at DESC);
```

### Migration 2: Farmer Observations
```sql
-- Create farmer observations table
CREATE TABLE farmer_observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  farm_id INTEGER NOT NULL,
  observation_date DATE NOT NULL,
  temperature REAL,
  humidity REAL,
  rainfall REAL,
  soil_moisture_raw INTEGER,
  soil_moisture_percent REAL,
  water_level TEXT CHECK(water_level IN ('Low', 'OK', 'Unknown', NULL)),
  notes TEXT,
  data_source TEXT DEFAULT 'Farmer-Provided',
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  upload_method TEXT DEFAULT 'csv',  -- 'csv' or 'manual'
  validation_status TEXT DEFAULT 'valid',
  validation_notes TEXT,
  FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
);

-- Create index for observations
CREATE INDEX idx_farmer_obs_farm_date ON farmer_observations(farm_id, observation_date DESC);
```

### Migration 3: Data Source Tracking
```sql
-- Add data_source column to sensor_readings if not exists
ALTER TABLE sensor_readings ADD COLUMN data_source TEXT DEFAULT 'Real Sensor';

-- Update existing simulated data
UPDATE sensor_readings SET data_source = 'Demo Mode' WHERE is_simulated = 1;
UPDATE sensor_readings SET data_source = 'Real Sensor' WHERE is_simulated = 0;
```

---

## Implementation Order

### Week 1: Core Farm Management
1. ✅ Database migration for favorites and last_selected
2. ✅ Backend: Favorite/unfavorite endpoint
3. ✅ Backend: Rename endpoint
4. ✅ Backend: Safe delete with impact check
5. ✅ Frontend: 3-farm collapsed view
6. ✅ Frontend: Expandable scrollable list
7. ✅ Frontend: Favorite stars
8. ✅ Frontend: Search box

### Week 2: Delete Safety & Bulk Actions
1. ✅ Backend: Get delete impact endpoint
2. ✅ Frontend: Delete confirmation dialog
3. ✅ Frontend: Show impact (rotations, sensors, etc.)
4. ✅ Frontend: Bulk delete mode (optional)
5. ✅ Testing: Referential integrity checks

### Week 3: Data Upload
1. ✅ Database migration for farmer_observations
2. ✅ Backend: CSV template endpoint
3. ✅ Backend: CSV upload & validation
4. ✅ Backend: Manual entry endpoint
5. ✅ Frontend: FarmDataSection component
6. ✅ Frontend: CSV upload UI with preview
7. ✅ Frontend: Manual entry form

### Week 4: Data Export & Source Labels
1. ✅ Backend: Export analysis endpoint
2. ✅ Backend: Refresh data endpoint
3. ✅ Frontend: Export button & download
4. ✅ Frontend: Refresh button with timestamps
5. ✅ Frontend: Data source badges everywhere
6. ✅ Testing: CSV export security (no credentials)

---

## Testing Checklist

### Farm Management
- [ ] Default view shows max 3 farms
- [ ] "View All Farms (N)" appears when > 3 farms
- [ ] Expanded list scrolls (max-height)
- [ ] "Show Less" returns to 3-farm view
- [ ] Favorites sort first
- [ ] Search filters farms correctly
- [ ] Selected farm remains visible
- [ ] Map centers when farm selected
- [ ] Rename updates farm name
- [ ] Delete shows impact warning
- [ ] Delete removes farm and related data
- [ ] Bulk delete works correctly
- [ ] No unrelated data deleted

### Data Upload
- [ ] CSV template downloads correctly
- [ ] Valid CSV uploads successfully
- [ ] Invalid CSV shows errors
- [ ] Preview shows data before import
- [ ] Duplicate handling works
- [ ] Manual entry saves observations
- [ ] Observations retain "Farmer-Provided" label
- [ ] Can delete own observations

### Data Export
- [ ] Export includes all available data
- [ ] Export labels data sources correctly
- [ ] Export never includes credentials
- [ ] CSV is safe (no formula injection)
- [ ] Refresh updates timestamps
- [ ] Missing data shown as "unavailable"

### Data Source Honesty
- [ ] Demo Mode clearly labeled
- [ ] Real Sensor clearly labeled
- [ ] NASA POWER labeled
- [ ] Farmer-Provided labeled
- [ ] No source mixing without labels
- [ ] Simulated data never claimed as real

### Regression
- [ ] Farm creation still works
- [ ] GPS location still works
- [ ] Planting suitability still works
- [ ] Crop rotations still work
- [ ] FlipPoint still works
- [ ] Smart Farm still works
- [ ] Ground Truth still works
- [ ] Frontend builds without errors
- [ ] Backend tests pass

---

## Files to Modify

### Frontend
- `src/components/sections/FarmSection.tsx` (major changes)
- `src/components/sections/FarmDataSection.tsx` (new file)
- `src/components/sections/SmartFarmSection.tsx` (add source labels)
- `src/app/page.tsx` (add FarmDataSection)

### Backend
- `routers/farms.py` (add endpoints)
- `routers/farm_data.py` (new file)
- `models/schemas.py` (add models)
- `database/db.py` (migrations)

### Documentation
- Update README with new features
- CSV template instructions
- Data source documentation

---

## Risks & Mitigations

**Risk**: Breaking existing farm selection logic  
**Mitigation**: Preserve selectedFarm state, test thoroughly

**Risk**: Accidental data deletion  
**Mitigation**: Multi-step confirmation, show impact, no bulk delete by default

**Risk**: CSV injection attacks  
**Mitigation**: Sanitize CSV output, validate input

**Risk**: Mixing data sources  
**Mitigation**: Strict labeling, separate tables, validation

**Risk**: Performance with 100+ farms  
**Mitigation**: Pagination, virtualized lists, client-side filtering

---

## Success Criteria

✅ Farmers can manage 100+ farms comfortably  
✅ Default view shows max 3 farms  
✅ Favorites work and persist  
✅ Search finds farms quickly  
✅ Delete requires confirmation and shows impact  
✅ CSV upload/export works reliably  
✅ All data sources clearly labeled  
✅ No existing features broken  
✅ Frontend builds successfully  
✅ Backend tests pass  

---

**Next Steps**: Begin Phase 1 implementation (Farm List Management)
