# FieldShift FarmOS - ESP32 DevKit Firmware

**Board**: ESP32 DevKit (Dual-core Xtensa LX6)  
**USB Chip**: CH340 USB-to-Serial  
**Firmware Version**: 2.0.0-ESP32-DevKit-PumpControl

---

## ⚠️ CRITICAL: This is ESP32 Firmware, NOT ESP8266!

**If you previously used NodeMCU V3 (ESP8266) firmware, you MUST change the wiring!**

The pin numbers and capabilities are COMPLETELY DIFFERENT between ESP8266 and ESP32.

---

## Hardware Requirements

### ESP32 DevKit Specifications
- **MCU**: ESP32 (Dual-core Xtensa LX6, 240 MHz)
- **RAM**: 520 KB SRAM
- **Flash**: 4 MB
- **Wi-Fi**: 2.4 GHz (802.11 b/g/n)
- **ADC**: 18 channels, 12-bit (0-4095)
- **PWM**: 16 LEDC channels
- **USB**: CH340 USB-to-Serial

### Required Sensors
- **DHT11**: Temperature/Humidity sensor
- **Soil Moisture**: Analog capacitive or resistive sensor
- **Water Level**: Analog or digital sensor (configurable)

### Motor Driver & Pump
- **TB6612FNG**: Dual H-bridge motor driver
- **Pump**: 3-5V DC submersible water pump
- **External Power**: Regulated 5V DC supply for motor driver VM

---

## Pin Wiring (ESP32 DevKit)

### ⚠️ WARNING: DO NOT USE ESP8266/NODEMCU PIN NUMBERS!

**Sensors**:
```
DHT11 Sensor:
  VCC → ESP32 3.3V or 5V
  DATA → GPIO18
  GND → GND
  (Optional: 10kΩ pull-up from DATA to VCC)

Soil Moisture Sensor (Analog):
  VCC → ESP32 3.3V
  AO → GPIO34 (ADC1_CH6)
  GND → GND

Water Level Sensor (Analog - recommended):
  VCC → ESP32 3.3V or 5V
  AO → GPIO35 (ADC1_CH7)
  GND → GND

Water Level Sensor (Digital - alternative):
  VCC → ESP32 3.3V or 5V
  DO → GPIO33
  GND → GND
```

**TB6612FNG Motor Driver**:
```
Power:
  VCC → ESP32 3.3V
  GND → Common ground with ESP32
  VM → External 5V DC supply (NOT from ESP32!)

Motor Outputs:
  AO1 → Pump wire 1
  AO2 → Pump wire 2

Control Signals (from ESP32):
  STBY → GPIO23 + 10kΩ pull-down resistor to GND ⚠️ CRITICAL!
  AIN1 → GPIO25
  AIN2 → GPIO26
  PWMA → GPIO27
```

### Pin Summary Table

| Function | ESP32 Pin | Type | Notes |
|----------|-----------|------|-------|
| DHT11 DATA | GPIO18 | Digital I/O | General purpose |
| Soil Moisture | GPIO34 | ADC1_CH6 | Input-only, 12-bit ADC |
| Water Level (Analog) | GPIO35 | ADC1_CH7 | Input-only, 12-bit ADC |
| Water Level (Digital) | GPIO33 | Digital I/O | Alternative to analog |
| Motor STBY | GPIO23 | Output | **Needs 10kΩ pull-down!** |
| Motor AIN1 | GPIO25 | Output | Motor direction |
| Motor AIN2 | GPIO26 | Output | Motor direction |
| Motor PWMA | GPIO27 | LEDC PWM | Motor speed control |

---

## ESP32 vs ESP8266 Differences

### Major Changes in ESP32 Firmware

| Feature | ESP8266 (NodeMCU V3) | ESP32 (DevKit) |
|---------|----------------------|----------------|
| **CPU** | Single-core 80 MHz | Dual-core 240 MHz |
| **RAM** | 80 KB | 520 KB |
| **ADC Resolution** | 10-bit (0-1023) | 12-bit (0-4095) |
| **ADC Channels** | 1 (A0 only) | 18 (multiple GPIOs) |
| **PWM** | Software (analogWrite) | Hardware (LEDC) |
| **Pin Names** | D0, D1, D2, D5, D7 | GPIO18, GPIO23, GPIO25, etc. |
| **WiFi Library** | ESP8266WiFi.h | WiFi.h |
| **HTTP Library** | ESP8266HTTPClient.h | HTTPClient.h |

### Code Changes Made

1. **Headers**: `ESP8266WiFi.h` → `WiFi.h`, `ESP8266HTTPClient.h` → `HTTPClient.h`
2. **Pin Definitions**: Removed D0/D1/D2 aliases, using GPIO numbers directly
3. **ADC**: Updated max value from 1023 → 4095
4. **PWM**: Replaced `analogWrite()` with LEDC functions (`ledcSetup()`, `ledcWrite()`)
5. **ADC Configuration**: Added ESP32-specific ADC setup (resolution, attenuation)
6. **Multiple ADC**: Can now read soil AND water level analog simultaneously

---

## Arduino IDE Setup

### 1. Install ESP32 Board Support

**Arduino IDE → Tools → Board → Boards Manager**:
1. Search for "esp32"
2. Install "**esp32 by Espressif Systems**" (version 2.0.0 or later)
3. Wait for installation to complete

### 2. Select Board

**Tools → Board → ESP32 Arduino**:
- Select "**ESP32 Dev Module**"

**Alternative boards** (if "ESP32 Dev Module" doesn't work):
- "DOIT ESP32 DEVKIT V1"
- "ESP32-WROOM-DA Module"
- Try different options until upload succeeds

### 3. Configure Board Settings

**Tools Menu**:
- **Board**: "ESP32 Dev Module"
- **Upload Speed**: 115200
- **CPU Frequency**: 240MHz (WiFi/BT)
- **Flash Frequency**: 80MHz
- **Flash Mode**: QIO
- **Flash Size**: 4MB (32Mb)
- **Partition Scheme**: "Default 4MB with spiffs"
- **Core Debug Level**: "None"
- **Port**: COM22 (your CH340 device)

---

## Required Libraries

Install via **Sketch → Include Library → Manage Libraries**:

1. **DHT sensor library** by Adafruit (version 1.4.0+)
2. **Adafruit Unified Sensor** (dependency for DHT)
3. **ArduinoJson** by Benoit Blanchon (version 6.x)

**Built-in libraries** (no installation needed):
- WiFi.h (ESP32 core)
- HTTPClient.h (ESP32 core)

---

## Compilation & Upload

### 1. Verify Configuration

Check `config.h`:
- ✅ `WIFI_SSID` = Your phone hotspot name
- ✅ `WIFI_PASSWORD` = Your hotspot password
- ✅ `API_SERVER` = Your laptop IP on hotspot
- ✅ `DEVICE_ID` = Registered device ID
- ✅ `API_KEY` = Your secure API key
- ✅ `FARM_ID` = Your farm ID (1)

### 2. Compile

1. Open `FieldShift_ESP32_DevKit.ino` in Arduino IDE
2. Click **Verify** (✓) button
3. Wait for compilation

**Expected Output**:
```
Sketch uses XXXXX bytes (XX%) of program storage space. Maximum is 1310720 bytes.
Global variables use XXXXX bytes (XX%) of dynamic memory, leaving XXXXX bytes for local variables. Maximum is 327680 bytes.
```

### 3. Upload

1. Ensure ESP32 connected to **COM22**
2. Close Serial Monitor (if open)
3. Click **Upload** (→) button
4. Wait for "Hard Resetting via RTS pin..."

**If upload fails**:
- Try different board selection (DOIT ESP32 DEVKIT V1)
- Lower upload speed to 921600 or 460800
- Press and hold BOOT button on ESP32 during upload
- Check USB cable (must be data cable, not charge-only)

---

## Serial Monitor Output

**Baud Rate**: 115200

### Expected Boot Sequence

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
      This prevents pump activation during boot/reset.

Initializing DHT11 sensor...
Connecting to Wi-Fi: Android 123
........
Wi-Fi connected!
IP Address: 192.168.43.25
Signal Strength: -45 dBm
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

⚠️  ESP32 NOTE: GPIO34-39 are INPUT ONLY!
   (No internal pull-up/pull-down)
====================================

====================================
SAFETY STATUS
====================================
Pump Commissioned:  NO (DISABLED)
Water Level Valid:  YES
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

---

## Sensor Reading Notes

### DHT11 (Temperature/Humidity)
- **Accuracy**: ±2°C, ±5% RH
- **Range**: 0-50°C, 20-90% RH
- **Sampling**: Max once per 2 seconds
- **Output**: Floating point (e.g., 22.5°C, 65.0%)

### Soil Moisture (Analog)
- **ADC**: 12-bit (0-4095)
- **Raw Output**: Direct ADC value
- **Calibration**: Compare dry (in air) vs wet (in water)
- **Typical Range**: 1500-4000 (depends on sensor)
- **Higher ADC** = More moisture (for most sensors)

### Water Level (Analog)
- **ADC**: 12-bit (0-4095)
- **Raw Output**: Direct ADC value
- **Conversion**: Mapped to 0-100% for backend
- **Threshold**: Configurable in firmware (default 2000)
- **Higher ADC** = More water (for typical sensors)

### Water Level (Digital)
- **Output**: HIGH or LOW
- **Interpretation**: Depends on sensor (LOW=OK or HIGH=OK)
- **Check**: Verify with your actual sensor!
- **Configure**: Set in firmware WATER_SENSOR_ANALOG flag

---

## Safety Features

### Pump Control Safety (DISABLED by Default)

**Multi-layer protection**:
1. ✅ `pumpCommissioned = false` (hardcoded)
2. ✅ OFF during boot/reset (STBY pull-down)
3. ✅ WiFi loss = emergency stop
4. ✅ Water level low = cannot start
5. ✅ Maximum runtime: 5 minutes
6. ✅ Command expiry timeout
7. ✅ Authenticated commands only

**Cannot be enabled remotely**: Must edit firmware and re-upload

---

## Troubleshooting

### ESP32 Not Detected (COM22)
- Install CH340 driver: http://www.wch.cn/downloads/CH341SER_ZIP.html
- Try different USB cable (data, not charge-only)
- Try different USB port
- Check Device Manager for "Unknown Device"

### Compilation Errors
- Install ESP32 board support (Boards Manager)
- Install required libraries (DHT, ArduinoJson)
- Check Arduino IDE version (1.8.13+ or Arduino IDE 2.x)

### Upload Fails
- Close Serial Monitor
- Select correct board ("ESP32 Dev Module" or "DOIT ESP32 DEVKIT V1")
- Lower upload speed (921600 → 460800 → 115200)
- Press and hold BOOT button during upload
- Try pressing RESET after upload starts

### Wi-Fi Connection Failed
- Check SSID exact match (case-sensitive)
- Verify password correct
- Ensure 2.4GHz hotspot (ESP32 doesn't support 5GHz)
- Move closer to phone (signal strength)
- Check hotspot allows client connections

### HTTP 401 Unauthorized
- Verify DEVICE_ID matches registration
- Check API_KEY is correct (no spaces)
- Ensure device registered in backend database

### DHT11 Read Failed
- Check wiring (DATA → GPIO18, VCC → 3.3V, GND → GND)
- Add 10kΩ pull-up resistor (DATA to VCC)
- Wait 2+ seconds after power-on
- Verify it's DHT11 (not DHT22)

### ADC Readings Always 4095 or 0
- Check sensor VCC connected
- Verify GPIO34/35 wiring (input-only pins)
- Test with multimeter (should see 0-3.3V)
- Check ADC attenuation setting (11dB for 0-3.3V)

### Pump Doesn't Start (Even if Commissioned)
- Check water level sensor OK
- Verify WiFi connected
- Check TB6612FNG wiring
- Verify external 5V supply connected to VM
- Check STBY pin has 10kΩ pull-down
- Monitor Serial for fault messages

---

## Migrating from ESP8266

### Before Removing ESP8266

1. **Note your configuration**:
   - Wi-Fi SSID/password
   - API server IP
   - Device ID
   - API key
   - Farm ID

2. **Do NOT reuse same device ID** if both boards will be active

### Physical Rewiring Required

| Sensor/Component | ESP8266 Pin | ESP32 Pin | Notes |
|------------------|-------------|-----------|-------|
| DHT11 DATA | D2 (GPIO4) | GPIO18 | Different GPIO |
| Soil Moisture | A0 (ADC0) | GPIO34 (ADC1_CH6) | 12-bit vs 10-bit |
| Water Level | D6 (GPIO12) | GPIO35 or GPIO33 | Analog or digital |
| Motor STBY | D0 (GPIO16) | GPIO23 | **10kΩ pull-down!** |
| Motor AIN1 | D5 (GPIO14) | GPIO25 | Different GPIO |
| Motor AIN2 | D7 (GPIO13) | GPIO26 | Different GPIO |
| Motor PWMA | D1 (GPIO5) | GPIO27 | LEDC vs analogWrite |

### Configuration File

Copy `config.h` from ESP8266 folder:
- Update `FIRMWARE_VERSION` to include "ESP32"
- Keep same DEVICE_ID, API_KEY, FARM_ID
- Verify WIFI_SSID, WIFI_PASSWORD, API_SERVER

### Backend Compatibility

**No backend changes needed!** The ESP32 firmware uses the same:
- API endpoints (`/api/hardware/telemetry`, etc.)
- Authentication headers (X-Device-ID, X-API-Key)
- JSON payload format
- Pump command protocol

---

## Advanced Configuration

### Water Level Sensor Type

**In FieldShift_ESP32_DevKit.ino**, line ~50:
```cpp
#define WATER_SENSOR_ANALOG true  // Analog sensor on GPIO35
```

Change to `false` if using digital sensor on GPIO33:
```cpp
#define WATER_SENSOR_ANALOG false  // Digital sensor on GPIO33
```

### ADC Calibration

**In config.h**:
```cpp
#define SOIL_DRY_VALUE 4095   // ADC when sensor in air
#define SOIL_WET_VALUE 1500   // ADC when sensor in water
```

Measure actual values with your sensor and update.

### PWM Frequency/Resolution

**In FieldShift_ESP32_DevKit.ino**, lines ~37-39:
```cpp
#define PWM_CHANNEL 0       // LEDC channel
#define PWM_FREQ 5000       // 5 kHz (adjust if motor whines)
#define PWM_RESOLUTION 8    // 8-bit (0-255)
```

Increase frequency if motor makes audible noise.

---

## Performance Comparison

| Metric | ESP8266 | ESP32 | Improvement |
|--------|---------|-------|-------------|
| CPU Speed | 80 MHz | 240 MHz | 3x faster |
| CPU Cores | 1 | 2 | 2x cores |
| RAM | 80 KB | 520 KB | 6.5x more |
| ADC Channels | 1 | 18 | 18x more |
| ADC Resolution | 10-bit | 12-bit | 4x precision |
| Sensor Capacity | Limited | Multiple analog | More sensors |

---

## Files

- `FieldShift_ESP32_DevKit.ino` - Main firmware (ESP32-specific)
- `config.h` - Configuration (credentials, secrets)
- `README.md` - This file

---

## Support

**COM Port**: COM22 (CH340)  
**Board**: ESP32 Dev Module  
**Baud Rate**: 115200  

**Backend API**: http://localhost:8000/api  
**Dashboard**: http://localhost:3000  

**Firmware Version**: 2.0.0-ESP32-DevKit-PumpControl
