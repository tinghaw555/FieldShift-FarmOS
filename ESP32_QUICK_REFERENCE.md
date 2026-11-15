# ESP32 DevKit - Quick Reference Guide

**Hardware**: ESP32 DevKit with CH340  
**Firmware**: FieldShift FarmOS v2.0.0-ESP32  
**COM Port**: COM22  

---

## Quick Start Checklist

### 1. Arduino IDE Setup (One-Time)
```
✓ Install Arduino IDE (1.8.13+ or 2.x)
✓ Add ESP32 board URL in Preferences
✓ Install "esp32" via Boards Manager
✓ Install libraries: DHT sensor, Adafruit Unified Sensor, ArduinoJson
```

### 2. Board Configuration
```
Tools → Board: "ESP32 Dev Module"
Tools → Upload Speed: 115200
Tools → Port: COM22
```

### 3. Open Firmware
```
File → Open:
C:\Users\acer\Nasa challenge\hardware\FieldShift_ESP32_DevKit\FieldShift_ESP32_DevKit.ino
```

### 4. Update API Server IP (When on Hotspot)
```
1. Connect laptop to phone hotspot "Android 123"
2. Run: ipconfig
3. Find new IP address (e.g., 192.168.43.X)
4. Edit config.h → API_SERVER = "192.168.43.X"
5. Click Verify (✓)
```

### 5. Compile & Upload
```
1. Click Verify (✓) - Should say "Done compiling"
2. Start backend: cd backend → python main.py
3. Click Upload (→) - Wait for "Hard Resetting..."
4. Open Serial Monitor (115200 baud)
5. Watch for "Wi-Fi connected!" and "✅ Telemetry sent"
```

### 6. Verify Dashboard
```
1. Open: http://localhost:3000
2. Go to "Smart Farm" tab
3. Check device status: Offline → Connected
4. Verify real sensor readings displayed
```

---

## ESP32 Pin Wiring (NEW - NOT ESP8266!)

### ⚠️ CRITICAL: Remove all ESP8266 wiring first!

```
DHT11 Temperature/Humidity:
  VCC → 3.3V
  DATA → GPIO18
  GND → GND

Soil Moisture (Analog):
  VCC → 3.3V
  AO → GPIO34 (ADC1_CH6)
  GND → GND

Water Level (Analog):
  VCC → 3.3V
  AO → GPIO35 (ADC1_CH7)
  GND → GND

TB6612FNG Motor Driver:
  VCC → 3.3V
  GND → GND (common with ESP32)
  VM → External 5V supply (NOT ESP32!)
  
  STBY → GPIO23 + 10kΩ pull-down resistor to GND ⚠️
  AIN1 → GPIO25
  AIN2 → GPIO26
  PWMA → GPIO27
  
  AO1, AO2 → Water pump (3-5V DC)
```

### Pin Comparison (ESP8266 vs ESP32)

| Function | OLD (ESP8266) | NEW (ESP32) |
|----------|---------------|-------------|
| DHT11 | D2 (GPIO4) | **GPIO18** |
| Soil | A0 | **GPIO34** |
| Water | N/A | **GPIO35** |
| STBY | D0 (GPIO16) | **GPIO23** + pull-down |
| AIN1 | D5 (GPIO14) | **GPIO25** |
| AIN2 | D7 (GPIO13) | **GPIO26** |
| PWMA | D1 (GPIO5) | **GPIO27** |

---

## Troubleshooting

### Upload Fails
```
✓ Try board: "DOIT ESP32 DEVKIT V1"
✓ Lower upload speed: 921600 or 460800
✓ Press and hold BOOT button during upload
✓ Check USB cable (must be data cable)
✓ Close Serial Monitor before upload
```

### Compilation Errors
```
✓ Install ESP32 board support (Boards Manager)
✓ Select correct board (ESP32, not ESP8266!)
✓ Install DHT sensor library (Adafruit)
✓ Install ArduinoJson v6 (not v5 or v7)
```

### WiFi Connection Failed
```
✓ Check SSID exact match: "Android 123"
✓ Check password in config.h
✓ Ensure 2.4GHz hotspot (not 5GHz)
✓ Move closer to phone
```

### HTTP 401 Unauthorized
```
✓ Verify DEVICE_ID: NODEMCU_V3_ESP8266_001
✓ Verify API_KEY in config.h (no spaces)
✓ Check backend is running on port 8000
```

### Backend Not Reachable
```
✓ Update API_SERVER to laptop's hotspot IP
✓ Backend running: python main.py
✓ Check Windows Firewall allows port 8000
```

### Sensor Reads NaN or 4095
```
✓ Check sensor VCC connected
✓ Verify correct GPIO pin wiring
✓ Wait 2 seconds after boot (DHT11)
✓ Test voltage with multimeter (should be 0-3.3V)
```

### Dashboard Shows Offline
```
✓ Check Serial Monitor for "✅ Telemetry sent successfully!"
✓ Verify backend received data (200 response)
✓ Check farm_id = 1 in config.h
✓ Refresh browser (Ctrl+F5)
```

---

## Expected Serial Output (115200 Baud)

```
====================================
FieldShift FarmOS - ESP32 DevKit
ESP32 Dual-Core (Xtensa LX6)
====================================
Configuring ESP32 ADC...
  ADC Resolution: 12-bit (0-4095)
  ADC Attenuation: 11dB (0-3.3V range)
  Channels: ADC1_CH6 (GPIO34), ADC1_CH7 (GPIO35)

Initializing pins (SAFE MODE)...
  STBY: LOW (driver disabled)
  AIN1: LOW
  AIN2: LOW
  PWMA: 0 (LEDC PWM configured)
  Pump: DISABLED

Initializing DHT11 sensor...
Connecting to Wi-Fi: Android 123
........
Wi-Fi connected!
IP Address: 192.168.43.25
Signal Strength: -45 dBm

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
SAFETY STATUS
====================================
Pump Commissioned:  NO (DISABLED)
Water Level OK:     YES
WiFi Connected:     YES

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
  "ip_address":"192.168.43.25"
}
HTTP Response: 200
✅ Telemetry sent successfully!
-----------------------------------
```

If you see this output, everything is working! ✅

---

## Safety Notes

### 🚨 Pump Control Disabled
```
Pump is DISABLED by default (pumpCommissioned = false)
Cannot be enabled remotely - requires firmware edit + re-upload
This is INTENTIONAL for safety during testing
```

### Required Hardware Safety
```
✓ 10kΩ pull-down resistor on STBY (GPIO23 to GND)
✓ External 5V supply for motor driver VM (not from ESP32)
✓ Common ground between ESP32 and motor driver
✓ Never power pump from ESP32 GPIO or 3.3V pin
✓ Verify all sensor connections before powering on
```

### ESP32-Specific Warnings
```
✓ GPIO34-39 are INPUT-ONLY (cannot be outputs)
✓ GPIO34-39 have NO internal pull-up/pull-down
✓ GPIO pins are 3.3V max (no 5V tolerance on most pins)
✓ ADC2 channels do NOT work with WiFi (use ADC1 only)
```

---

## Configuration Reference

### Current Settings (config.h)
```cpp
// Wi-Fi
WIFI_SSID = "Android 123"
WIFI_PASSWORD = "udgt3699"

// API (UPDATE WHEN ON HOTSPOT!)
API_SERVER = "10.22.217.151"  // Change to hotspot IP
API_PORT = 8000

// Device (Registered)
DEVICE_ID = "NODEMCU_V3_ESP8266_001"
API_KEY = "qwXg3afBII7c6XVhyqf1XPiSNdqjLDsUTqGRz_h1a1g"
FARM_ID = 1

// Intervals
TELEMETRY_INTERVAL_MS = 60000   // 60 seconds
COMMAND_POLL_INTERVAL_MS = 5000 // 5 seconds
```

---

## Performance Specs

### ESP32 DevKit
- **CPU**: Dual-core 240 MHz (vs ESP8266: 80 MHz single-core)
- **RAM**: 520 KB (vs ESP8266: 80 KB)
- **ADC**: 12-bit, 18 channels (vs ESP8266: 10-bit, 1 channel)
- **PWM**: Hardware LEDC (vs ESP8266: software PWM)
- **Wi-Fi**: 2.4 GHz only (NOT 5 GHz)

### Sensor Readings
- **DHT11**: Every 2 seconds (±2°C, ±5% RH)
- **Soil Moisture**: Raw 12-bit ADC (0-4095)
- **Water Level**: Raw 12-bit ADC or digital
- **Telemetry**: Every 60 seconds
- **Commands**: Polled every 5 seconds

---

## File Locations

### Firmware (ESP32)
```
C:\Users\acer\Nasa challenge\hardware\FieldShift_ESP32_DevKit\
├── FieldShift_ESP32_DevKit.ino  (Main firmware)
├── config.h                      (Configuration)
└── README.md                     (Full documentation)
```

### Backend
```
C:\Users\acer\Nasa challenge\backend\
├── main.py                       (FastAPI server)
├── routers\hardware.py          (Telemetry & pump endpoints)
└── database\fieldshift.db       (SQLite database)
```

### Frontend
```
C:\Users\acer\Nasa challenge\frontend\
└── src\components\sections\SmartFarmSection.tsx  (Dashboard UI)
```

---

## Support Commands

### Find Laptop IP (Windows)
```powershell
ipconfig
# Look for "Wireless LAN adapter Wi-Fi" → IPv4 Address
```

### Start Backend
```powershell
cd "C:\Users\acer\Nasa challenge\backend"
python main.py
# Should show: Uvicorn running on http://0.0.0.0:8000
```

### Start Frontend
```powershell
cd "C:\Users\acer\Nasa challenge\frontend"
npm run dev
# Should show: ready - started server on http://localhost:3000
```

### Check Backend
```powershell
curl http://localhost:8000
# Should return: {"message":"FieldShift FarmOS API"}
```

### Check Database
```powershell
cd "C:\Users\acer\Nasa challenge\backend"
python -c "from database.db import get_db; db = next(get_db()); print(db.execute('SELECT * FROM devices').fetchall())"
```

---

## Quick Links

- **Full Report**: `ESP32_INTEGRATION_REPORT.md`
- **Detailed README**: `hardware/FieldShift_ESP32_DevKit/README.md`
- **Backend API**: http://localhost:8000/docs
- **Dashboard**: http://localhost:3000

---

**Last Updated**: 2024-01-15  
**Status**: ✅ Firmware ready for compilation and upload  
**Next Step**: Open Arduino IDE and compile firmware
