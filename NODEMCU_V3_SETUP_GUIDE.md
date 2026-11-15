# NodeMCU V3 (ESP8266) Hardware Setup Guide

## Overview

FieldShift FarmOS is ready to receive real sensor data from **LOLIN NodeMCU V3 (ESP8266)** devices via Wi-Fi and HTTP/JSON.

**IMPORTANT:** This guide is for **NodeMCU V3 (ESP8266)**, NOT ESP32. The hardware and firmware are completely different.

## Actual Hardware Configuration

### Controller
**LOLIN NodeMCU V3**
- Microcontroller: ESP8266 ESP-12E or ESP-12F
- CPU: 80 MHz / 160 MHz (1 core)
- RAM: 80 KB user-available
- Flash: 4 MB (typical)
- Wi-Fi: 2.4 GHz ONLY (802.11 b/g/n)
- Analog Input: **ONE only** (A0, 10-bit ADC, 0-1023)
- GPIO: 11 usable pins (D0-D8, with boot restrictions)
- Operating Voltage: 3.3V

### Sensors
**DHT11** - Temperature & Humidity
- Accuracy: ±2°C temperature, ±5% humidity
- Range: 0-50°C, 20-90% RH
- Pin: D2 (GPIO4)
- Power: 3.3V
- Sampling: Max once per 2 seconds

**Analog Soil Moisture Sensor**
- Type: Resistive or capacitive
- Output: Analog 0-3.3V (adjust based on your sensor)
- Pin: **A0 (ONLY analog input on ESP8266!)**
- Reads: Raw ADC value 0-1023
- Calibration: Required (dry=~1023, wet=~300)

**Water Level Sensor**
- Type: Digital switch/float sensor
- Output: Digital HIGH/LOW or similar
- Pin: D6 (GPIO12)
- **CRITICAL:** If your sensor is analog, you CANNOT use it simultaneously with analog soil sensor (ESP8266 has only ONE analog input!)

### Motor Driver & Pump
**TB6612FNG Motor Driver** (NOT L298N!)
- Dual H-bridge motor driver
- VM voltage: 4.5V-13.5V (use 5V for 3-5V pump)
- Logic voltage: 2.7V-5.5V (use NodeMCU 3.3V)
- Max current: 1.2A per channel (3.2A peak)
- Low standby current when STBY=LOW

**3-5V DC Submersible Water Pump**
- Rated voltage: 3-5V DC
- Power source: External regulated 5V supply via TB6612FNG VM
- **NEVER** power from NodeMCU GPIO or 3.3V pin!

**External 5V Regulated Power Supply**
- For TB6612FNG VM pin and pump
- Must provide adequate current for pump (typically 500mA-1A)
- Common ground with NodeMCU

## Pin Connections

### Complete Wiring Table

| Component | NodeMCU Pin | ESP8266 GPIO | Function | Notes |
|-----------|-------------|--------------|----------|-------|
| **DHT11 VCC** | 3.3V | - | Power | 3.3V supply |
| **DHT11 DATA** | D2 | GPIO4 | Digital I/O | Optional 10kΩ pull-up |
| **DHT11 GND** | GND | - | Ground | Common ground |
| **Soil VCC** | 3.3V or 5V | - | Power | Check sensor spec |
| **Soil AO** | A0 | ADC0 | Analog Input | **ONLY analog input!** |
| **Soil GND** | GND | - | Ground | Common ground |
| **Water VCC** | 3.3V or 5V | - | Power | Check sensor spec |
| **Water DO** | D6 | GPIO12 | Digital Input | Assuming digital output |
| **Water GND** | GND | - | Ground | Common ground |
| **TB6612 VCC** | 3.3V | - | Logic Power | Motor driver logic |
| **TB6612 GND** | GND | - | Ground | Common ground |
| **TB6612 VM** | - | - | Motor Power | **External 5V supply** |
| **TB6612 AIN1** | D5 | GPIO14 | Motor Direction | High/Low control |
| **TB6612 AIN2** | D7 | GPIO13 | Motor Direction | High/Low control |
| **TB6612 PWMA** | D1 | GPIO5 | Motor Speed | PWM control |
| **TB6612 STBY** | D0 | GPIO16 | Standby Control | **10kΩ pull-down REQUIRED!** |
| **TB6612 AO1** | - | - | Motor Output | Pump wire 1 |
| **TB6612 AO2** | - | - | Motor Output | Pump wire 2 |
| **Pump +** | - | - | Power | TB6612 AO1 |
| **Pump -** | - | - | Power | TB6612 AO2 |

### Critical Wiring Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOLIN NodeMCU V3 (ESP8266)                   │
│                                                                 │
│  3.3V ────┬───→ DHT11 VCC                                      │
│           ├───→ TB6612 VCC (logic)                             │
│           └───→ Soil/Water VCC (if 3.3V sensors)               │
│                                                                 │
│  GND ─────┴───→ All GND (DHT11, sensors, TB6612, ext supply)  │
│                                                                 │
│  D2 (GPIO4) ──→ DHT11 DATA                                     │
│  A0 (ADC0)  ──→ Soil Moisture ANALOG OUT  ⚠️ ONLY ANALOG!     │
│  D6 (GPIO12)──→ Water Level DIGITAL OUT                        │
│                                                                 │
│  D5 (GPIO14)──→ TB6612 AIN1                                    │
│  D7 (GPIO13)──→ TB6612 AIN2                                    │
│  D1 (GPIO5) ──→ TB6612 PWMA                                    │
│  D0 (GPIO16)──→ TB6612 STBY ──→ 10kΩ resistor ──→ GND  ⚠️     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                          │
                          │
            ┌─────────────┴──────────────┐
            │      TB6612FNG Driver      │
            │                            │
            │  VM ←── External 5V Supply │
            │  GND ←─ Common Ground      │
            │  AO1 ───┐                  │
            │  AO2 ───┼──→ 3-5V Pump     │
            └─────────┴──────────────────┘
```

### ⚠️ CRITICAL SAFETY REQUIREMENTS

1. **TB6612FNG STBY Pin Pull-Down Resistor**
   ```
   D0 (GPIO16) ──→ TB6612 STBY
                   │
                   └──→ 10kΩ resistor ──→ GND
   ```
   - **MANDATORY:** 10kΩ pull-down resistor from STBY to GND
   - GPIO16 has NO internal pull-up or pull-down
   - Without external resistor, STBY floats during boot/reset
   - Floating STBY can enable motor driver unexpectedly
   - **PUMP COULD START DURING BOOT WITHOUT THIS RESISTOR!**

2. **Pump Power Isolation**
   - TB6612 VM pin: Connect to EXTERNAL regulated 5V supply
   - TB6612 VCC pin: Connect to NodeMCU 3.3V (logic power)
   - AO1, AO2: Connect to 3-5V pump (match VM voltage)
   - **NEVER connect pump to NodeMCU GPIO pins**
   - **NEVER connect pump to NodeMCU 3.3V pin**
   - NodeMCU GPIO max: 12mA (pump needs 500mA-1A!)

3. **Voltage Levels**
   - NodeMCU GPIO: 3.3V logic (NOT 5V tolerant on all pins!)
   - A0 analog input: 0-1.0V (with built-in voltage divider for 0-3.2V input)
   - Verify your NodeMCU's A0 specification before connecting sensors
   - Some sensors output 5V - use voltage divider if needed

4. **ESP8266 Boot Behavior**
   - GPIO15 (D8): Must be LOW during boot
   - GPIO0 (D3): Must be HIGH during boot (LOW enters flash mode)
   - GPIO2 (D4): Must be HIGH during boot
   - GPIO16 (D0): Used for deep sleep wake, no pull-up/down
   - Avoid using D3, D4, D8 for critical outputs

## Backend API Endpoint

**Telemetry Endpoint:**
```
POST http://your-server-ip:8000/api/hardware/telemetry
```

**Required Headers:**
- `X-Device-ID`: Unique device identifier (e.g., "NODEMCU_FARM001")
- `X-API-Key`: Authentication key obtained during device registration
- `Content-Type`: application/json

**Request Body (JSON):**
```json
{
  "farm_id": 1,
  "timestamp": "2024-01-01T12:30:00Z",
  "temperature": 22.5,
  "humidity": 65.0,
  "soil_moisture": 450,
  "water_level": 100,
  "firmware_version": "1.0.0-NodeMCU-V3",
  "ip_address": "192.168.1.123"
}
```

**Notes on data format:**
- `temperature`: DHT11 reading in °C (±2°C accuracy)
- `humidity`: DHT11 reading in % (±5% accuracy)
- `soil_moisture`: Raw ADC value 0-1023 (NOT percentage)
- `water_level`: 0 (low) or 100 (OK) for digital sensor

## Device Registration

Before NodeMCU can send telemetry, it must be registered:

**Step 1: Register Device**
```bash
curl -X POST http://your-server-ip:8000/api/hardware/register \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "NODEMCU_FARM001",
    "farm_id": 1,
    "device_type": "NodeMCU-V3-ESP8266"
  }'
```

**Response:**
```json
{
  "device_id": "NODEMCU_FARM001",
  "api_key": "aBcDeFgHiJkLmNoPqRsTuVwXyZ123456789",
  "message": "Device registered successfully. Save the API key securely - it cannot be retrieved later.",
  "endpoint": "/api/hardware/telemetry",
  "headers_required": ["X-Device-ID", "X-API-Key"]
}
```

**⚠️ SAVE THE API KEY IMMEDIATELY - IT CANNOT BE RETRIEVED LATER**

## Firmware Upload

### Prerequisites

1. **Arduino IDE** (version 1.8.x or 2.x)
2. **ESP8266 Board Package** installed
3. **Required Libraries:**
   - DHT sensor library by Adafruit
   - Adafruit Unified Sensor
   - ArduinoJson (version 6.x)

### Upload Steps

1. **Install ESP8266 Board Package**
   - File → Preferences
   - Add to Additional Boards Manager URLs:
     ```
     http://arduino.esp8266.com/stable/package_esp8266com_index.json
     ```
   - Tools → Board → Boards Manager
   - Search "esp8266" and install

2. **Configure Board Settings**
   - Board: "NodeMCU 1.0 (ESP-12E Module)"
   - Upload Speed: "115200"
   - CPU Frequency: "80 MHz" (or 160 MHz)
   - Flash Size: "4MB (FS:2MB OTA:~1019KB)"
   - Port: Select your NodeMCU's COM port

3. **Edit config.h**
   ```cpp
   const char* WIFI_SSID = "YourNetwork";  // 2.4GHz only!
   const char* WIFI_PASSWORD = "password";
   const char* API_SERVER = "192.168.1.100";  // Your laptop's LAN IP
   const char* DEVICE_ID = "NODEMCU_FARM001";
   const char* API_KEY = "your-api-key-here";
   const int FARM_ID = 1;
   ```

4. **Upload Firmware**
   - Open `hardware/FieldShift_NodeMCU_V3/FieldShift_NodeMCU_V3.ino`
   - Click Upload button
   - Open Serial Monitor (115200 baud)
   - Press RST button on NodeMCU
   - Verify boot messages

## Testing & Commissioning

### 1. Safety Pre-Check

Before connecting any power:

- [ ] 10kΩ pull-down resistor installed on STBY pin
- [ ] TB6612 VM connected to external 5V supply (NOT NodeMCU)
- [ ] TB6612 VCC connected to NodeMCU 3.3V
- [ ] All grounds connected (common ground)
- [ ] Pump connected to AO1 and AO2 (NOT to NodeMCU)
- [ ] No >3.3V signals connected to NodeMCU GPIO
- [ ] Water level sensor wiring verified

### 2. Firmware Upload

- [ ] NodeMCU connected via USB
- [ ] Firmware uploaded successfully
- [ ] Serial Monitor shows boot messages
- [ ] Wi-Fi connection successful
- [ ] IP address displayed

### 3. Sensor Verification

Watch Serial Monitor for telemetry output:

**DHT11:**
```
"temperature":22.5,"humidity":65
```
Expected: Reasonable values (0-50°C, 20-90%)
If failed: Check wiring, power, wait 2+ seconds between readings

**Soil Moisture:**
```
"soil_moisture":450
```
Expected: 0-1023 (raw ADC value)
- ~1023 = sensor in air (dry)
- ~300-500 = moist soil
- <300 = in water (wet)

**Water Level:**
```
"water_level":100  (OK) or "water_level":0  (low)
```
Expected: Binary 0 or 100
Verify logic matches your sensor type

### 4. Backend Integration

- [ ] Telemetry POST returns 200 OK
- [ ] Data appears in Smart Farm dashboard
- [ ] Status shows "Connected" (green)
- [ ] Sensor readings update every 60 seconds

### 5. Pump Commissioning (LAST STEP)

**DO NOT ENABLE UNTIL ALL ABOVE STEPS PASS**

In firmware, line ~88:
```cpp
bool pumpCommissioned = false;  // Change to true ONLY after testing!
```

Only change to `true` after:
- [ ] All sensors working correctly
- [ ] Water level protection verified
- [ ] STBY pull-down confirmed working
- [ ] Manual pump test successful (disconnect from driver first)
- [ ] Emergency stop tested
- [ ] Maximum runtime verified

## Troubleshooting

### Wi-Fi Connection Failed
- Verify network is 2.4 GHz (ESP8266 does NOT support 5 GHz!)
- Check SSID and password in config.h
- Move closer to router
- Check signal strength (RSSI in Serial Monitor)

### DHT11 Read Failed
- Verify wiring: VCC (3.3V), GND, DATA (D2)
- Add 10kΩ pull-up resistor between DATA and VCC if needed
- Wait 2+ seconds between readings
- DHT11 works only in 0-50°C range

### HTTP Connection Refused
- Verify API_SERVER IP is your laptop's LAN IP (NOT localhost)
- Ensure backend running: `python main.py`
- Check firewall settings
- Test with: `curl http://your-ip:8000/api/health`

### Soil Moisture Always 1023
- Check sensor power (3.3V or 5V depending on sensor)
- Verify A0 connection
- Check sensor is in soil (not air)
- Try different ADC reading position

### Water Level Incorrect Logic
- Adjust `WATER_LEVEL_ACTIVE_LOW` in config.h
- Some sensors: LOW = water OK
- Others: HIGH = water OK
- Verify with multimeter

### Pump Activates During Boot
- **CRITICAL SAFETY ISSUE!**
- Immediately disconnect power
- Verify 10kΩ resistor from STBY (D0) to GND
- Measure resistance with multimeter
- Check resistor is actually connected to GND, not floating

### ESP8266 Keeps Rebooting
- Watchdog timer reset
- Add `delay(100)` in main loop
- Check power supply stability (needs stable 3.3V, 500mA+)
- Reduce telemetry frequency
- Check for blocking operations

## ESP8266 vs ESP32 Differences

This project previously used ESP32. Key differences:

| Feature | ESP8266 (NodeMCU V3) | ESP32 (Previous) |
|---------|----------------------|------------------|
| **Wi-Fi** | 2.4 GHz ONLY | 2.4 + 5 GHz |
| **Analog Inputs** | **1 (A0)** | 18 (ADC1/ADC2) |
| **ADC Resolution** | 10-bit (0-1023) | 12-bit (0-4095) |
| **CPU** | 1 core, 80/160 MHz | 2 cores, 240 MHz |
| **Libraries** | ESP8266WiFi.h | WiFi.h |
| **GPIO Count** | 11 usable | 34 usable |
| **Bluetooth** | No | Yes |
| **Boot Pins** | Specific requirements | Fewer restrictions |

**Code changes required:**
- Use `ESP8266WiFi.h` instead of `WiFi.h`
- Use `ESP8266HTTPClient.h` instead of ESP32's `HTTPClient.h`
- Only ONE analog sensor on A0 (not multiple)
- Account for GPIO boot behavior
- Lower RAM available (80KB vs 520KB)

## Support Files

- **Firmware:** `hardware/FieldShift_NodeMCU_V3/FieldShift_NodeMCU_V3.ino`
- **Configuration:** `hardware/FieldShift_NodeMCU_V3/config.h`
- **Detailed README:** `hardware/FieldShift_NodeMCU_V3/README.md`
- **Integration Report:** `NODEMCU_V3_INTEGRATION_REPORT.md`

## Safety Reminders

⚠️ **BEFORE COMMISSIONING:**
- TB6612FNG STBY must have 10kΩ pull-down resistor
- Pump must be powered from external 5V via TB6612 VM
- Never power pump from NodeMCU GPIO or 3.3V
- Test all safety interlocks before enabling pump
- Pump is disabled by default (requires code change)
- Monitor Serial output during all testing

## License

MIT License - See project LICENSE file
