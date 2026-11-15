# ESP32 Firmware Upload - Final Checklist

**Project**: FieldShift FarmOS  
**Hardware**: ESP32 DevKit (CH340)  
**Firmware**: v2.0.0-ESP32-DevKit-PumpControl  
**Status**: ✅ Firmware ready, awaiting upload  

---

## 📋 Pre-Upload Verification

### Stage 1: Arduino IDE Setup

**1.1 Arduino IDE Installed**
- [ ] Arduino IDE 1.8.13+ or Arduino IDE 2.x installed
- [ ] IDE launches without errors

**1.2 ESP32 Board Support**
- [ ] Preferences → Additional Board Manager URLs added:
      `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
- [ ] Tools → Board → Boards Manager → "esp32" installed
- [ ] ESP32 boards visible in board selection menu

**1.3 Required Libraries**
- [ ] Sketch → Include Library → Manage Libraries → "DHT sensor library" (Adafruit) installed
- [ ] "Adafruit Unified Sensor" (dependency) installed
- [ ] "ArduinoJson" version 6.x installed

**1.4 Board Configuration**
- [ ] Tools → Board: **"ESP32 Dev Module"** selected
- [ ] Tools → Upload Speed: **115200** selected
- [ ] Tools → CPU Frequency: **240MHz (WiFi/BT)** selected
- [ ] Tools → Flash Frequency: **80MHz** selected
- [ ] Tools → Flash Mode: **QIO** selected
- [ ] Tools → Flash Size: **4MB (32Mb)** selected
- [ ] Tools → Partition Scheme: **"Default 4MB with spiffs"** selected
- [ ] Tools → Port: **COM22** selected

---

### Stage 2: Firmware Configuration

**2.1 Firmware Files**
- [ ] Firmware opened: `C:\Users\acer\Nasa challenge\hardware\FieldShift_ESP32_DevKit\FieldShift_ESP32_DevKit.ino`
- [ ] config.h exists in same folder
- [ ] README.md exists for reference

**2.2 Network Configuration (config.h)**
```cpp
WIFI_SSID = "Android 123"              // ✓ Verified
WIFI_PASSWORD = "udgt3699"             // ✓ Verified
```
- [ ] SSID matches phone hotspot name exactly (case-sensitive)
- [ ] Password is correct

**2.3 API Configuration (config.h)**
```cpp
API_SERVER = "10.22.217.151"           // ⚠️ UPDATE when on hotspot!
API_PORT = 8000                        // ✓ Verified
```
- [ ] API_SERVER will be updated after connecting to hotspot
- [ ] Current value noted for reference

**2.4 Device Authentication (config.h)**
```cpp
DEVICE_ID = "NODEMCU_V3_ESP8266_001"   // ✓ Verified (registered)
API_KEY = "qwXg3afBII7c6XVhyqf1XPiSNdqjLDsUTqGRz_h1a1g"  // ✓ Verified
FARM_ID = 1                             // ✓ Verified
```
- [ ] Device ID matches backend registration
- [ ] API key is complete and correct (no spaces)
- [ ] Farm ID = 1 confirmed

**2.5 Safety Configuration (FieldShift_ESP32_DevKit.ino)**
```cpp
bool pumpCommissioned = false;         // ✓ DISABLED (correct for initial test)
```
- [ ] Pump commissioning is FALSE (pump will NOT activate)
- [ ] This is correct for initial testing

---

### Stage 3: Compilation Test

**3.1 Verify (Compile)**
- [ ] Click **Verify** button (✓ checkmark icon)
- [ ] Wait for compilation to complete
- [ ] Check console output

**Expected Output**:
```
Sketch uses XXXXX bytes (XX%) of program storage space. Maximum is 1310720 bytes.
Global variables use XXXXX bytes (XX%) of dynamic memory, leaving XXXXX bytes for local variables. Maximum is 327680 bytes.
```

**3.2 Compilation Success**
- [ ] Console shows "Done compiling" (green text)
- [ ] No errors in red text
- [ ] Program storage <100%
- [ ] Dynamic memory <100%

**If Compilation Fails**:
- [ ] Check error message for missing libraries
- [ ] Install missing libraries via Library Manager
- [ ] Verify ESP32 board selected (not ESP8266)
- [ ] Restart Arduino IDE if needed

---

### Stage 4: Hardware Connections

**4.1 ESP32 Physical Check**
- [ ] ESP32 DevKit board (not NodeMCU V3)
- [ ] CH340 USB chip visible on board
- [ ] USB cable connected (data cable, not charge-only)
- [ ] COM22 detected in Device Manager
- [ ] No visible damage to ESP32 board

**4.2 Sensor Wiring Verification**
- [ ] **DHT11**: DATA → GPIO18, VCC → 3.3V, GND → GND
- [ ] **Soil Moisture**: AO → GPIO34, VCC → 3.3V, GND → GND
- [ ] **Water Level**: AO → GPIO35 (or DO → GPIO33), VCC → 3.3V, GND → GND
- [ ] All sensor VCC connections verified (3.3V only, not 5V)

**4.3 Motor Driver Wiring Verification**
- [ ] **TB6612FNG VCC** → ESP32 3.3V
- [ ] **TB6612FNG GND** → Common GND (connected to ESP32 GND)
- [ ] **TB6612FNG VM** → External 5V supply (NOT from ESP32)
- [ ] **TB6612FNG STBY** → GPIO23
- [ ] **10kΩ resistor** from GPIO23 to GND (pull-down)
- [ ] **TB6612FNG AIN1** → GPIO25
- [ ] **TB6612FNG AIN2** → GPIO26
- [ ] **TB6612FNG PWMA** → GPIO27
- [ ] **Pump wires** → TB6612FNG AO1 and AO2

**4.4 Safety Checks**
- [ ] **No 5V to ESP32 GPIO** (all sensors 3.3V)
- [ ] **GPIO34, GPIO35 as inputs only** (not outputs)
- [ ] **Common ground** established between all components
- [ ] **External 5V supply** connected to motor driver VM
- [ ] **10kΩ pull-down** on STBY verified with multimeter
- [ ] **No short circuits** between VCC and GND (multimeter test)

**4.5 Multimeter Voltage Tests**
- [ ] ESP32 3.3V pin: 3.2-3.4V
- [ ] TB6612FNG VM pin: 4.8-5.2V
- [ ] STBY pin voltage: ~0V (pulled down)
- [ ] No unexpected voltages on any pin

---

### Stage 5: Network Setup

**5.1 Phone Hotspot**
- [ ] Phone hotspot enabled
- [ ] Hotspot name: "Android 123"
- [ ] Hotspot password: "udgt3699"
- [ ] 2.4GHz frequency confirmed (not 5GHz)
- [ ] Hotspot allows client connections

**5.2 Laptop Connection**
- [ ] Laptop connected to phone hotspot
- [ ] Internet access working (optional, but good to verify)
- [ ] `ipconfig` command run to get IP address
- [ ] Laptop IP address noted: ________________

**5.3 Update API Server IP**
- [ ] Edit config.h → API_SERVER = "[laptop hotspot IP]"
- [ ] Save config.h
- [ ] Re-verify firmware (click ✓ button)
- [ ] Compilation successful after config change

---

### Stage 6: Backend Verification

**6.1 Backend Running**
- [ ] Open Command Prompt
- [ ] Navigate to: `cd "C:\Users\acer\Nasa challenge\backend"`
- [ ] Run: `python main.py`
- [ ] Backend starts without errors
- [ ] Console shows: "Uvicorn running on http://0.0.0.0:8000"

**6.2 Backend Accessible**
- [ ] Open browser
- [ ] Navigate to: `http://localhost:8000`
- [ ] Page loads with: `{"message":"FieldShift FarmOS API"}`
- [ ] Navigate to: `http://localhost:8000/docs` (API documentation)

**6.3 Device Registration Check**
- [ ] Backend database contains device: NODEMCU_V3_ESP8266_001
- [ ] Farm ID 1 exists in database
- [ ] API key matches config.h

**Optional Backend Test Command**:
```powershell
cd "C:\Users\acer\Nasa challenge\backend"
python -c "from database.db import get_db; db = next(get_db()); print(db.execute('SELECT device_id, status FROM devices').fetchall())"
```
Expected: `[('NODEMCU_V3_ESP8266_001', 'offline')]`

---

### Stage 7: Frontend Verification (Optional)

**7.1 Frontend Running**
- [ ] Open second Command Prompt
- [ ] Navigate to: `cd "C:\Users\acer\Nasa challenge\frontend"`
- [ ] Run: `npm run dev`
- [ ] Frontend starts without errors
- [ ] Console shows: "ready - started server on http://localhost:3000"

**7.2 Dashboard Accessible**
- [ ] Open browser
- [ ] Navigate to: `http://localhost:3000`
- [ ] FieldShift dashboard loads
- [ ] Navigate to "Smart Farm" section
- [ ] Device shows as "Offline" (expected before ESP32 connects)

---

## 🚀 Upload Process

### Step 1: Prepare for Upload

- [ ] All above stages completed and checked
- [ ] Backend running (python main.py)
- [ ] Laptop connected to phone hotspot
- [ ] API_SERVER updated to hotspot IP
- [ ] Firmware verified (compiled successfully)
- [ ] Serial Monitor closed (if open)

### Step 2: Upload Firmware

**2.1 Initiate Upload**
- [ ] Click **Upload** button (→ arrow icon)
- [ ] Wait for upload process to start
- [ ] Watch progress bar in Arduino IDE

**2.2 Monitor Upload Progress**

**Expected Console Output**:
```
Connecting........_____.....
Chip is ESP32-D0WDQ6 (revision 1)
Features: WiFi, BT, Dual Core, 240MHz, VRef calibration in efuse, Coding Scheme None
Crystal is 40MHz
MAC: XX:XX:XX:XX:XX:XX
Uploading stub...
Running stub...
Stub running...
Configuring flash size...
Compressed XXXXXX bytes to XXXXXX...
Writing at 0x00001000... (X %)
...
Wrote XXXXXX bytes (XXXXXX compressed) at 0x00001000 in X.X seconds
Leaving...
Hard resetting via RTS pin...
```

**2.3 Upload Success Indicators**
- [ ] Console shows "Hard resetting via RTS pin..."
- [ ] Progress reaches 100%
- [ ] No red error messages
- [ ] ESP32 LED blinks during upload

**If Upload Fails** (see Troubleshooting section below):
- Try different board: "DOIT ESP32 DEVKIT V1"
- Lower upload speed: 921600 or 460800
- Press and hold BOOT button during upload
- Check USB cable (try different cable/port)

---

### Step 3: Monitor Serial Output

**3.1 Open Serial Monitor**
- [ ] Tools → Serial Monitor
- [ ] Set baud rate: **115200**
- [ ] Press ESP32 RESET button (or power cycle)
- [ ] Watch boot sequence

**3.2 Expected Boot Sequence**

```
====================================
FieldShift FarmOS - ESP32 DevKit
ESP32 Dual-Core (Xtensa LX6)
====================================
Configuring ESP32 ADC...
  ADC Resolution: 12-bit (0-4095)
  ADC Attenuation: 11dB (0-3.3V range)
  Channels: ADC1_CH6 (GPIO34), ADC1_CH7 (GPIO35)
  ⚠️  Using ADC1 (ADC2 incompatible with WiFi)

Initializing pins (SAFE MODE)...
  STBY: LOW (driver disabled)
  AIN1: LOW
  AIN2: LOW
  PWMA: 0 (LEDC PWM configured)
  Pump: DISABLED

  ⚠️  CRITICAL: TB6612FNG STBY pin MUST have
      external ~10kΩ pull-down resistor!

Initializing DHT11 sensor...
Connecting to Wi-Fi: Android 123
........
Wi-Fi connected!
IP Address: 192.168.43.XXX
Signal Strength: -XX dBm
MAC Address: XX:XX:XX:XX:XX:XX

Setup complete!

====================================
PIN CONFIGURATION (ESP32)
====================================
DHT11 DATA:       GPIO18
Soil Moisture:    GPIO34 (ADC1_CH6) - 12-bit ADC
Water Level:      GPIO35 (ADC1_CH7) - Analog
TB6612FNG AIN1:   GPIO25
TB6612FNG AIN2:   GPIO26
TB6612FNG PWMA:   GPIO27 (LEDC PWM)
TB6612FNG STBY:   GPIO23 ⚠️  NEEDS 10kΩ PULL-DOWN!
====================================

====================================
SAFETY STATUS
====================================
Pump Commissioned:  NO (DISABLED)
Water Level Valid:  YES
Water Level OK:     YES
WiFi Connected:     YES
====================================

-----------------------------------
Sending telemetry...
Payload:
{
  "farm_id":1,
  "timestamp":"2024-01-01T00:00:15Z",
  "temperature":22.5,
  "humidity":65.0,
  "soil_moisture":2450,
  "water_level":75,
  "firmware_version":"2.0.0-ESP32-DevKit-PumpControl",
  "ip_address":"192.168.43.XXX"
}
HTTP Response: 200
✅ Telemetry sent successfully!
-----------------------------------
```

**3.3 Boot Success Indicators**
- [ ] "ESP32 Dual-Core (Xtensa LX6)" appears
- [ ] ADC configuration messages appear
- [ ] "Initializing pins (SAFE MODE)" appears
- [ ] "Pump: DISABLED" appears
- [ ] "Wi-Fi connected!" appears
- [ ] ESP32 IP address displayed
- [ ] "✅ Telemetry sent successfully!" appears
- [ ] HTTP Response: 200

---

### Step 4: Verify Sensor Readings

**4.1 DHT11 Temperature/Humidity**
- [ ] Temperature reading appears (°C)
- [ ] Humidity reading appears (%)
- [ ] Values within reasonable range (temp: 0-50°C, humidity: 20-90%)
- [ ] No "NaN" (Not a Number) errors

**4.2 Soil Moisture**
- [ ] Raw ADC value appears (0-4095 range)
- [ ] Value changes when sensor moved between air/water
- [ ] Not stuck at 0 or 4095

**4.3 Water Level**
- [ ] Raw ADC value appears (if analog) or digital state (if digital)
- [ ] "Water Level OK: YES" or "NO" appears
- [ ] Value changes when sensor placed in/out of water

**4.4 Telemetry Transmission**
- [ ] Telemetry sent every 60 seconds
- [ ] JSON payload includes all sensor readings
- [ ] HTTP Response: 200 (success)
- [ ] No authentication errors (401)

---

### Step 5: Verify Dashboard Integration

**5.1 Device Status**
- [ ] Open frontend: http://localhost:3000
- [ ] Navigate to "Smart Farm" section
- [ ] Device status changes from "Offline" to "Connected"
- [ ] Last seen timestamp updates

**5.2 Sensor Data Display**
- [ ] Temperature value displayed
- [ ] Humidity value displayed
- [ ] Soil moisture value displayed
- [ ] Water level status displayed
- [ ] Values update every 60 seconds

**5.3 Pump Control Interface**
- [ ] Pump status shows "Disabled" or "Not Commissioned"
- [ ] Control buttons visible but inactive
- [ ] No unexpected pump activation

---

## ✅ Success Criteria

### Upload Successful When:

1. **Firmware Upload**
   - ✅ Upload completes without errors
   - ✅ "Hard resetting via RTS pin..." appears
   - ✅ ESP32 boots and runs firmware

2. **WiFi Connection**
   - ✅ ESP32 connects to "Android 123" hotspot
   - ✅ ESP32 obtains IP address (192.168.43.XXX)
   - ✅ Signal strength displayed (dBm)

3. **Sensor Readings**
   - ✅ DHT11 temperature/humidity valid
   - ✅ Soil moisture ADC reading valid
   - ✅ Water level reading valid
   - ✅ No sensor errors in Serial Monitor

4. **Backend Communication**
   - ✅ Telemetry sent successfully (HTTP 200)
   - ✅ Authentication accepted (no 401 errors)
   - ✅ Backend logs show received telemetry

5. **Dashboard Display**
   - ✅ Device status: "Connected"
   - ✅ Real sensor data displayed
   - ✅ Data updates every 60 seconds
   - ✅ Pump control interface visible

6. **Safety Status**
   - ✅ "Pump Commissioned: NO (DISABLED)" displayed
   - ✅ Pump does not activate
   - ✅ STBY pin LOW (driver disabled)
   - ✅ No unexpected motor activity

---

## 🔧 Troubleshooting

### Upload Issues

**Problem: "Failed to connect to ESP32"**
```
Solutions:
1. Try board "DOIT ESP32 DEVKIT V1" instead of "ESP32 Dev Module"
2. Lower upload speed to 921600 or 460800
3. Press and hold BOOT button during upload
4. Try different USB port or cable
5. Close Serial Monitor before upload
6. Check Device Manager shows COM22 (install CH340 driver if missing)
```

**Problem: "Timed out waiting for packet header"**
```
Solutions:
1. Press BOOT button when "Connecting..." appears
2. Hold BOOT throughout entire upload
3. Press RESET then BOOT in sequence
4. Try lower upload speed (115200)
```

**Problem: "Port COM22 not available"**
```
Solutions:
1. Close other programs using serial port
2. Unplug and replug USB cable
3. Restart Arduino IDE
4. Install CH340 driver from: http://www.wch.cn/downloads/CH341SER_ZIP.html
```

---

### WiFi Connection Issues

**Problem: "Wi-Fi connection FAILED!"**
```
Checklist:
- [ ] SSID exact match: "Android 123" (case-sensitive)
- [ ] Password correct in config.h
- [ ] Phone hotspot is 2.4GHz (not 5GHz)
- [ ] Hotspot allows client connections
- [ ] Move ESP32 closer to phone
- [ ] Restart hotspot on phone
```

**Serial Monitor Debug Output**:
```
If you see "Connecting to Wi-Fi: Android 123"
followed by many dots "........" without success:
- Check SSID/password
- Verify 2.4GHz network
- Check signal strength (move closer)
```

---

### Sensor Reading Issues

**Problem: DHT11 reads NaN**
```
Solutions:
1. Check DATA wire connected to GPIO18
2. Add 10kΩ pull-up resistor (DATA to VCC)
3. Wait 2-3 seconds after boot before first reading
4. Verify it's DHT11 sensor (not DHT22)
5. Check sensor power (VCC and GND connected)
```

**Problem: Soil moisture always 4095 or 0**
```
Solutions:
1. Verify sensor VCC connected (3.3V)
2. Check AO wire connected to GPIO34
3. Test sensor output with multimeter (should be 0-3.3V)
4. Try different sensor or GPIO pin
5. Check sensor not damaged
```

**Problem: Water level always invalid**
```
Solutions:
1. Verify WATER_SENSOR_ANALOG flag matches sensor type
2. Check AO wire connected to GPIO35 (analog) or DO to GPIO33 (digital)
3. Test sensor manually (place in water, check reading changes)
4. Verify sensor power and ground connections
```

---

### Backend Communication Issues

**Problem: HTTP 401 Unauthorized**
```
Solutions:
1. Verify DEVICE_ID in config.h matches registration
2. Check API_KEY is complete (no spaces or line breaks)
3. Verify device registered in backend database
4. Check backend console for authentication errors
```

**Problem: HTTP timeout or connection refused**
```
Solutions:
1. Verify API_SERVER IP is laptop's hotspot IP (not LAN IP)
2. Check backend running (python main.py shows "Uvicorn running")
3. Test backend: curl http://localhost:8000
4. Check Windows Firewall allows port 8000
5. Verify ESP32 and laptop on same hotspot network
```

**Problem: HTTP 404 Not Found**
```
Solutions:
1. Check backend version matches firmware (telemetry endpoint exists)
2. Verify URL in firmware: /api/hardware/telemetry
3. Check backend console for routing errors
```

---

### Dashboard Issues

**Problem: Device shows "Offline"**
```
Checklist:
- [ ] Serial Monitor shows "✅ Telemetry sent successfully!"
- [ ] Backend console shows received telemetry
- [ ] farm_id in config.h = 1 (matches database)
- [ ] Refresh browser (Ctrl+F5)
- [ ] Check browser console for errors (F12)
```

**Problem: Sensor values not updating**
```
Solutions:
1. Check Serial Monitor shows telemetry sent every 60 seconds
2. Verify HTTP Response: 200 in Serial Monitor
3. Check backend logs show received data
4. Refresh dashboard browser
5. Check frontend console (F12) for API call errors
```

---

## 📊 Post-Upload Testing

### Test 1: Sensor Accuracy (Optional)

**DHT11 Comparison**:
- [ ] Compare ESP32 reading with room thermometer
- [ ] Should be within ±2°C
- [ ] Humidity within ±5%

**Soil Moisture Calibration**:
- [ ] Note ADC value in air (dry): _______
- [ ] Note ADC value in water (wet): _______
- [ ] Update SOIL_DRY_VALUE and SOIL_WET_VALUE in config.h if desired

**Water Level Threshold**:
- [ ] Test sensor in empty container: reading = _______
- [ ] Test sensor in water: reading = _______
- [ ] Verify "Water Level OK" changes appropriately
- [ ] Update WATER_OK_THRESHOLD if needed

---

### Test 2: Backend Data Logging

**Database Verification**:
```powershell
cd "C:\Users\acer\Nasa challenge\backend"
python -c "from database.db import get_db; db = next(get_db()); import pandas as pd; print(pd.read_sql('SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 5', db))"
```

Expected: Recent sensor readings with timestamp, temperature, humidity, soil_moisture, water_level

---

### Test 3: Pump Control (DISABLED - Expected Behavior)

**Dashboard Pump Test**:
- [ ] Navigate to "Smart Farm" → Pump Control
- [ ] Click "Start Pump" button
- [ ] Pump should NOT activate
- [ ] Status should show "Not Commissioned" or "Disabled"
- [ ] Serial Monitor shows: "❌ Pump start DENIED: Not commissioned!"

This is **CORRECT** behavior. Pump commissioning requires firmware edit and re-upload (intentional safety feature).

---

## 🎯 Next Steps After Successful Upload

### Immediate (Testing Phase)

1. **Monitor for Stability**
   - [ ] Let ESP32 run for 10-15 minutes
   - [ ] Verify continuous telemetry transmission
   - [ ] Check for WiFi disconnections or errors
   - [ ] Monitor ESP32 temperature (should not get hot)

2. **Test WiFi Recovery**
   - [ ] Temporarily disable phone hotspot
   - [ ] Watch Serial Monitor for "Wi-Fi disconnected"
   - [ ] Re-enable hotspot
   - [ ] Verify ESP32 reconnects automatically

3. **Test Power Cycle**
   - [ ] Unplug ESP32 USB power
   - [ ] Wait 5 seconds
   - [ ] Replug USB power
   - [ ] Verify clean boot and WiFi reconnection

---

### Future (Optional Commissioning)

**⚠️ Only after thorough testing and wiring verification**

To enable pump control (later):
1. Verify all wiring with multimeter
2. Test water level protection manually
3. Confirm external 5V supply stable
4. Edit firmware: `pumpCommissioned = true`
5. Re-upload firmware
6. Test pump START command (with water present!)
7. Test emergency stop (disconnect WiFi)
8. Test timeout (5-minute maximum)

**Do not enable pump commissioning during initial testing!**

---

## 📝 Upload Log Template

**Date/Time**: _______________  
**Performed By**: _______________  

### Checklist Completion
- [ ] All pre-upload stages completed
- [ ] Firmware uploaded successfully
- [ ] Serial output shows boot sequence
- [ ] WiFi connected
- [ ] Telemetry sent (HTTP 200)
- [ ] Dashboard shows "Connected"
- [ ] All sensors reading valid data

### Observed Values
- ESP32 IP Address: _______________
- Temperature: _______________ °C
- Humidity: _______________ %
- Soil Moisture (Raw): _______________
- Water Level (Raw): _______________
- Signal Strength: _______________ dBm

### Issues Encountered
_____________________________________________
_____________________________________________

### Resolution
_____________________________________________
_____________________________________________

### Final Status
- [ ] ✅ PASS - All systems operational
- [ ] ⚠️ PARTIAL - Some issues but functional
- [ ] ❌ FAIL - Upload unsuccessful

### Notes
_____________________________________________
_____________________________________________

---

**Checklist Version**: 1.0  
**Last Updated**: 2024-01-15  
**Firmware Version**: 2.0.0-ESP32-DevKit-PumpControl
