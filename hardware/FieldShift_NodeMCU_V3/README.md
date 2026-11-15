# FieldShift FarmOS - NodeMCU V3 (ESP8266) Firmware

## Hardware Configuration

**Controller:** LOLIN NodeMCU V3 (ESP8266 ESP-12E/ESP-12F)  
**Sensors:**
- DHT11 Temperature & Humidity
- Analog Soil Moisture Sensor
- Water Level Sensor (Digital)

**Motor Control:**
- TB6612FNG Motor Driver
- 3-5V DC Submersible Water Pump
- External Regulated 5V Power Supply

## Critical Safety Requirements

⚠️ **BEFORE UPLOADING FIRMWARE:**

1. **TB6612FNG STBY Pin Pull-Down**
   - Connect external ~10kΩ resistor from STBY pin to GND
   - This prevents pump activation during boot/reset
   - **WITHOUT THIS RESISTOR, PUMP MAY START UNEXPECTEDLY!**

2. **Power Supply Verification**
   - TB6612FNG VM pin: External regulated 5V DC
   - TB6612FNG VCC pin: NodeMCU 3.3V
   - Pump: Connected to TB6612FNG AO1 and AO2
   - **NEVER power pump from NodeMCU GPIO or 3.3V pin!**

3. **Voltage Level Verification**
   - NodeMCU GPIO: 3.3V logic level
   - Verify A0 input voltage range (typically 0-3.2V max)
   - **Do NOT connect 5V signals directly to GPIO!**

4. **Water Level Sensor Type**
   - Confirm if your sensor outputs Digital or Analog
   - ESP8266 has ONLY ONE analog input (A0)
   - If water sensor is analog, you CANNOT use it with analog soil sensor
   - Consider using digital water level switch instead

## Pin Connections

| Component | NodeMCU Pin | ESP8266 GPIO | Notes |
|-----------|-------------|--------------|-------|
| DHT11 DATA | D2 | GPIO4 | 3.3V power |
| Soil Moisture Analog | A0 | ADC0 | Only analog input! |
| Water Level Digital | D6 | GPIO12 | Verify sensor type |
| TB6612FNG AIN1 | D5 | GPIO14 | Motor direction |
| TB6612FNG AIN2 | D7 | GPIO13 | Motor direction |
| TB6612FNG PWMA | D1 | GPIO5 | Motor speed (PWM) |
| TB6612FNG STBY | D0 | GPIO16 | **Needs 10kΩ pull-down!** |

### TB6612FNG Wiring

```
TB6612FNG          NodeMCU V3         External
─────────────────────────────────────────────────
VCC          →     3.3V
GND          →     GND            →   GND (common)
VM           →     (not connected) →   5V regulated supply
AO1          →     (not connected) →   Pump wire 1
AO2          →     (not connected) →   Pump wire 2
AIN1         →     D5 (GPIO14)
AIN2         →     D7 (GPIO13)
PWMA         →     D1 (GPIO5)
STBY         →     D0 (GPIO16)    →   10kΩ to GND
```

### DHT11 Wiring

```
DHT11              NodeMCU V3
─────────────────────────────
VCC (+)      →     3.3V
DATA         →     D2 (GPIO4)
GND (-)      →     GND
```

Optional: 10kΩ pull-up resistor between DATA and VCC (some DHT11 modules have this built-in)

## Arduino IDE Setup

### 1. Install ESP8266 Board Package

1. Open Arduino IDE
2. Go to **File → Preferences**
3. Add to **Additional Boards Manager URLs**:
   ```
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
   ```
4. Go to **Tools → Board → Boards Manager**
5. Search for "esp8266"
6. Install **"esp8266 by ESP8266 Community"** (version 3.x or later)

### 2. Install Required Libraries

Go to **Sketch → Include Library → Manage Libraries** and install:

- **DHT sensor library** by Adafruit (version 1.4.x or later)
- **Adafruit Unified Sensor** (dependency for DHT library)
- **ArduinoJson** by Benoit Blanchon (version 6.x)

### 3. Board Configuration

Go to **Tools** menu and configure:

- **Board**: "NodeMCU 1.0 (ESP-12E Module)"
- **Upload Speed**: "115200"
- **CPU Frequency**: "80 MHz" (or 160 MHz for faster performance)
- **Flash Size**: "4MB (FS:2MB OTA:~1019KB)" or similar
- **Port**: Select your NodeMCU's COM port

## Firmware Configuration

### 1. Edit config.h

Copy `config.h` and edit these settings:

```cpp
// Wi-Fi (2.4GHz only!)
const char* WIFI_SSID = "YourNetwork";
const char* WIFI_PASSWORD = "YourPassword";

// FieldShift API (use your laptop's LAN IP, NOT localhost)
const char* API_SERVER = "192.168.1.100";  // Your server IP
const int API_PORT = 8000;

// Device credentials (get from registration)
const char* DEVICE_ID = "NODEMCU_FARM001";
const char* API_KEY = "your-api-key-here";
const int FARM_ID = 1;
```

### 2. Get API Key

Before uploading firmware, register your device:

```bash
curl -X POST http://your-server-ip:8000/api/hardware/register \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "NODEMCU_FARM001",
    "farm_id": 1,
    "device_type": "NodeMCU-V3-ESP8266"
  }'
```

Save the returned `api_key` and add it to `config.h`.

## Upload Procedure

### 1. Safety Check

- [ ] 10kΩ pull-down resistor installed on STBY pin
- [ ] Pump disconnected or power supply OFF
- [ ] Water level sensor wiring verified
- [ ] No >3.3V signals connected to GPIO
- [ ] External 5V supply ready (but not yet connected to VM)

### 2. Upload Firmware

1. Connect NodeMCU to computer via USB
2. Select correct COM port in Arduino IDE
3. Click **Upload** button (or Ctrl+U)
4. Wait for "Done uploading" message
5. Open **Serial Monitor** (115200 baud)
6. Press NodeMCU **RST** button
7. Watch boot messages

### 3. Verify Boot Sequence

You should see:

```
====================================
FieldShift FarmOS - NodeMCU V3
LOLIN NodeMCU V3 (ESP8266)
====================================
Initializing pins (SAFE MODE)...
  STBY: LOW (driver disabled)
  AIN1: LOW
  AIN2: LOW
  PWMA: 0
  Pump: DISABLED

  ⚠️  CRITICAL: TB6612FNG STBY pin MUST have
      external ~10kΩ pull-down resistor!
...
Connecting to Wi-Fi: YourNetwork
.....
Wi-Fi connected!
IP Address: 192.168.1.XXX
...
Setup complete!
...
Sending telemetry...
✅ Telemetry sent successfully!
```

### 4. Troubleshooting Upload Issues

**"Connecting..." forever:**
- Try holding **FLASH** button while uploading
- Try different USB cable
- Verify correct COM port selected

**"espcomm_sync failed":**
- NodeMCU may be in wrong mode
- Press and hold **FLASH**, press **RST**, release **RST**, release **FLASH**
- Try again

## Testing Sensors

### DHT11 Temperature & Humidity

Watch Serial Monitor output:
```
-----------------------------------
Sending telemetry...
Payload:
{"farm_id":1,"timestamp":"2024-01-01T00:01:00Z","temperature":22.5,"humidity":65}
```

**If you see "DHT11 read failed":**
- Check wiring (VCC, GND, DATA)
- Verify DHT11 is powered (3.3V)
- Try adding 10kΩ pull-up resistor on DATA line
- Wait 2+ seconds between readings

### Soil Moisture (Raw ADC)

Serial Monitor will show:
```
"soil_moisture":450
```

Value range: 0-1023
- ~1023 = sensor in air (dry)
- ~300-500 = moist soil
- <300 = in water (wet)

**Calibration:**
1. Place sensor in air, note value → SOIL_DRY_VALUE
2. Place sensor in water, note value → SOIL_WET_VALUE
3. Update values in config.h

### Water Level Sensor

Serial Monitor shows water level as 0 or 100:
```
"water_level":100  // OK
"water_level":0    // Low
```

**Verify correct logic:**
- If sensor is active-low (LOW = water OK), set `WATER_LEVEL_ACTIVE_LOW true` in config.h
- If sensor is active-high (HIGH = water OK), set `WATER_LEVEL_ACTIVE_LOW false`

**If water level sensor is ANALOG:**
- You CANNOT use it with analog soil sensor simultaneously
- ESP8266 has ONLY ONE analog input (A0)
- Options:
  1. Use digital water level switch instead
  2. Add external I2C ADC module (ADS1115)
  3. Use water sensor on A0, move soil to I2C moisture sensor

## Pump Commissioning

**BY DEFAULT, PUMP IS DISABLED FOR SAFETY**

### Before Enabling Pump

1. **Verify Wiring:**
   - [ ] TB6612FNG STBY has 10kΩ pull-down to GND
   - [ ] TB6612FNG VM connected to external 5V supply
   - [ ] Pump connected to AO1 and AO2
   - [ ] Common ground for all power supplies
   - [ ] No pump power from NodeMCU GPIO or 3.3V

2. **Test Motor Driver (No Pump):**
   - Upload firmware
   - Verify STBY stays LOW during boot
   - Measure AIN1, AIN2, PWMA all LOW
   - Use multimeter to verify no voltage on AO1/AO2

3. **Test Water Level Protection:**
   - Simulate low water (disconnect sensor or change state)
   - Verify pump cannot start
   - Restore water level
   - Verify safety system acknowledges

### Enable Pump (Code Change Required)

In `FieldShift_NodeMCU_V3.ino`, line ~88:

```cpp
bool pumpCommissioned = false;  // Change to true ONLY after testing!
```

Change to:
```cpp
bool pumpCommissioned = true;  // ⚠️  ENABLES PHYSICAL PUMP CONTROL!
```

Re-upload firmware and monitor carefully.

### Pump Safety Interlocks

The firmware enforces these safety conditions:

- ❌ Pump OFF when `pumpCommissioned = false`
- ❌ Pump OFF when water level low/invalid
- ❌ Pump OFF when WiFi disconnected
- ❌ Pump OFF when runtime exceeds 5 minutes
- ❌ Pump OFF when no active authorized command
- ❌ Pump OFF during boot and reset

**Emergency Stop** triggers if any condition becomes unsafe while running.

## Backend Integration

The firmware is compatible with existing FieldShift FarmOS backend:

**Endpoint:** `POST /api/hardware/telemetry`

**Headers:**
- `X-Device-ID`: Your device ID
- `X-API-Key`: Your API key
- `Content-Type`: application/json

**Payload:**
```json
{
  "farm_id": 1,
  "timestamp": "2024-01-01T00:01:00Z",
  "temperature": 22.5,
  "humidity": 65.0,
  "soil_moisture": 450,
  "water_level": 100,
  "firmware_version": "1.0.0-NodeMCU-V3",
  "ip_address": "192.168.1.123"
}
```

**Expected Response (200 OK):**
```json
{
  "status": "accepted",
  "device_id": "NODEMCU_FARM001",
  "timestamp": "2024-01-01T00:01:00Z",
  "message": "Telemetry stored successfully"
}
```

## ESP8266 vs ESP32 Differences

| Feature | ESP8266 (NodeMCU V3) | ESP32 (Previous) |
|---------|----------------------|------------------|
| **CPU** | 1 core, 80/160 MHz | 2 cores, 240 MHz |
| **RAM** | 80 KB user | 520 KB |
| **Wi-Fi** | 2.4 GHz only | 2.4 + 5 GHz |
| **Bluetooth** | No | Yes (BLE) |
| **Analog Inputs** | 1 (A0) | 18 (ADC1/ADC2) |
| **GPIO** | 11 usable | 34 usable |
| **PWM** | Software | Hardware (LEDC) |
| **ADC Resolution** | 10-bit (0-1023) | 12-bit (0-4095) |
| **Libraries** | ESP8266WiFi.h | WiFi.h (ESP32) |
| **Boot Behavior** | Specific pins HIGH/LOW | Fewer restrictions |

**Code Changes Required:**
- ✅ Use `ESP8266WiFi.h` instead of `WiFi.h`
- ✅ Use `ESP8266HTTPClient.h` instead of `HTTPClient.h`
- ✅ Use ONE analog sensor on A0 (not multiple)
- ✅ Use software PWM instead of `ledcSetup()`
- ✅ Account for GPIO boot restrictions

## Troubleshooting

### "DHT11 read failed"
- Check wiring (especially DATA pin)
- Verify power (3.3V, not 5V!)
- Add 10kΩ pull-up resistor if needed
- Wait 2+ seconds between readings

### "Wi-Fi connection FAILED"
- Verify SSID and password in config.h
- Ensure network is 2.4 GHz (NOT 5 GHz!)
- Check Wi-Fi signal strength
- Try moving closer to router

### "HTTP Error: connection refused"
- Verify API_SERVER IP address
- Ensure backend is running (`python main.py`)
- Check firewall settings
- Use LAN IP, not localhost

### "Telemetry rejected by server" (401)
- Verify API key is correct
- Re-register device if needed
- Check X-Device-ID header matches registration

### Pump activates during boot
- **CRITICAL SAFETY ISSUE!**
- Immediately disconnect power
- Verify 10kΩ pull-down resistor on STBY pin
- Check resistor is connected to actual GND

### Watchdog reset / ESP reboots
- Add `delay(100)` in main loop
- Reduce telemetry frequency
- Check for blocking operations
- Verify stable power supply

## Safety Reminders

⚠️ **CRITICAL:**
- TB6612FNG STBY pin MUST have 10kΩ pull-down resistor
- NEVER power pump from NodeMCU GPIO or 3.3V
- Use external regulated 5V for pump via TB6612FNG VM
- Pump disabled by default - requires code change to enable
- Test ALL safety interlocks before enabling pump
- Monitor Serial output during commissioning

## Support

For FieldShift FarmOS backend issues, see:
- `NODEMCU_V3_SETUP_GUIDE.md` - Complete hardware guide
- `NODEMCU_V3_INTEGRATION_REPORT.md` - Implementation details
- Backend API documentation

## License

MIT License - See project LICENSE file
