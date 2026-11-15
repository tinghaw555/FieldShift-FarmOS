# [OBSOLETE] ESP32 Hardware Setup Guide

## ⚠️ THIS DOCUMENT IS OBSOLETE

**This guide was written for ESP32 hardware, which is NOT the actual hardware used in this project.**

**ACTUAL HARDWARE:** LOLIN NodeMCU V3 (ESP8266) with DHT11, NOT ESP32 with DHT22

**USE INSTEAD:**
- `NODEMCU_V3_SETUP_GUIDE.md` - Correct hardware setup guide
- `NODEMCU_V3_INTEGRATION_REPORT.md` - Technical integration details
- `hardware/FieldShift_NodeMCU_V3/` - Correct firmware

---

# Original ESP32 Documentation (Historical Reference Only)

## Backend API Endpoint

**Telemetry Endpoint:**
```
POST http://your-server-ip:8000/api/hardware/telemetry
```

**Required Headers:**
- `X-Device-ID`: Unique device identifier (e.g., "ESP32_FARM001")
- `X-API-Key`: Authentication key obtained during device registration
- `Content-Type`: application/json

**Request Body (JSON):**
```json
{
  "farm_id": 1,
  "timestamp": "2023-10-15T10:30:00Z",
  "temperature": 22.5,
  "humidity": 65.0,
  "soil_moisture": 45.0,
  "water_level": 75.0,
  "firmware_version": "1.0.0",
  "ip_address": "192.168.1.100"
}
```

## Device Registration

Before an ESP32 can send telemetry, it must be registered:

**Step 1: Register Device**
```bash
curl -X POST http://localhost:8000/api/hardware/register \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ESP32_FARM001",
    "farm_id": 1,
    "device_type": "ESP32"
  }'
```

**Response:**
```json
{
  "device_id": "ESP32_FARM001",
  "api_key": "YOUR_GENERATED_API_KEY_HERE",
  "message": "Device registered successfully. Save the API key securely - it cannot be retrieved later.",
  "endpoint": "/api/hardware/telemetry",
  "headers_required": ["X-Device-ID", "X-API-Key"]
}
```

**⚠️ IMPORTANT:** Save the API key immediately. It cannot be retrieved later.

## Hardware Requirements

### Sensors
- **DHT22** - Temperature & Humidity sensor
  - Pin: GPIO 4 (configurable)
  - 3.3V power
  - 10kΩ pull-up resistor
  
- **Capacitive Soil Moisture Sensor v1.2**
  - Pin: GPIO 34 (ADC1_CH6)
  - Analog output (0-3.3V)
  - Calibration required (0% = air, 100% = water)
  
- **Float Switch** - Water level detection
  - Pin: GPIO 27 (configurable)
  - Normally Open (NO) configuration
  - Internal pull-up enabled

### Control (Optional - Safety Lock Enabled)
- **12V NC Solenoid Valve** - Irrigation control
  - Driver: Relay module or MOSFET (e.g., IRF520)
  - Pin: GPIO 25 (configurable)
  - ⚠️ Physical irrigation control is DISABLED in software until commissioning

### Power
- ESP32 DevKit or similar (5V via USB or regulated supply)
- Stable Wi-Fi connection required

## ESP32 Firmware Configuration

**config.h:**
```cpp
// Wi-Fi Configuration
const char* WIFI_SSID = "YourNetworkSSID";
const char* WIFI_PASSWORD = "YourNetworkPassword";

// FieldShift API Configuration
const char* API_SERVER = "192.168.1.100"; // Your backend server IP
const int API_PORT = 8000;
const char* DEVICE_ID = "ESP32_FARM001";
const char* API_KEY = "YOUR_GENERATED_API_KEY_HERE";
const int FARM_ID = 1;

// Sensor Pins
#define DHT_PIN 4
#define SOIL_MOISTURE_PIN 34
#define FLOAT_SWITCH_PIN 27
#define VALVE_PIN 25

// Telemetry Configuration
#define TELEMETRY_INTERVAL 60000  // 60 seconds
#define FIRMWARE_VERSION "1.0.0"
```

## Sample ESP32 Code (Arduino)

**Required Libraries:**
- WiFi.h (built-in)
- HTTPClient.h (built-in)
- DHT sensor library by Adafruit
- ArduinoJson by Benoit Blanchon

**main.ino:**
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// Configuration
#include "config.h"

// Initialize sensors
DHT dht(DHT_PIN, DHT22);

void setup() {
  Serial.begin(115200);
  
  // Initialize sensors
  dht.begin();
  pinMode(SOIL_MOISTURE_PIN, INPUT);
  pinMode(FLOAT_SWITCH_PIN, INPUT_PULLUP);
  pinMode(VALVE_PIN, OUTPUT);
  digitalWrite(VALVE_PIN, LOW); // Valve closed
  
  // Connect to Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  sendTelemetry();
  delay(TELEMETRY_INTERVAL);
}

void sendTelemetry() {
  // Read sensors
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  float soilMoisture = readSoilMoisture();
  float waterLevel = readWaterLevel();
  
  // Validate readings
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("DHT22 read failed");
    return;
  }
  
  // Build JSON payload
  StaticJsonDocument<300> doc;
  doc["farm_id"] = FARM_ID;
  doc["timestamp"] = getISO8601Timestamp();
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["soil_moisture"] = soilMoisture;
  doc["water_level"] = waterLevel;
  doc["firmware_version"] = FIRMWARE_VERSION;
  doc["ip_address"] = WiFi.localIP().toString();
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  // Send HTTP POST
  HTTPClient http;
  String url = String("http://") + API_SERVER + ":" + API_PORT + "/api/hardware/telemetry";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-ID", DEVICE_ID);
  http.addHeader("X-API-Key", API_KEY);
  
  int httpCode = http.POST(jsonPayload);
  
  if (httpCode == 200) {
    Serial.println("Telemetry sent successfully");
  } else {
    Serial.print("Telemetry failed: ");
    Serial.println(httpCode);
    Serial.println(http.getString());
  }
  
  http.end();
}

float readSoilMoisture() {
  int raw = analogRead(SOIL_MOISTURE_PIN);
  // Calibrate: measure in air (dry) and water (wet)
  const int AIR_VALUE = 3200;    // Measure your sensor in air
  const int WATER_VALUE = 1500;  // Measure your sensor in water
  float percent = 100.0 * (AIR_VALUE - raw) / (AIR_VALUE - WATER_VALUE);
  return constrain(percent, 0.0, 100.0);
}

float readWaterLevel() {
  int floatState = digitalRead(FLOAT_SWITCH_PIN);
  // Simple float switch: HIGH = low water, LOW = water present
  // For percentage, you'd need multiple switches at different heights
  return floatState == LOW ? 75.0 : 20.0;  // Simplified
}

String getISO8601Timestamp() {
  // Implement NTP time sync or use RTC module
  // For now, return a placeholder
  return "2023-10-15T10:30:00Z";
}
```

## Testing the Integration

### 1. Register Device
```bash
curl -X POST http://localhost:8000/api/hardware/register \
  -H "Content-Type: application/json" \
  -d '{"device_id": "ESP32_TEST", "farm_id": 1, "device_type": "ESP32"}'
```

### 2. Send Test Telemetry
```bash
curl -X POST http://localhost:8000/api/hardware/telemetry \
  -H "Content-Type: application/json" \
  -H "X-Device-ID: ESP32_TEST" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "farm_id": 1,
    "timestamp": "2023-10-15T10:30:00Z",
    "temperature": 22.5,
    "humidity": 65.0,
    "soil_moisture": 45.0,
    "water_level": 75.0,
    "firmware_version": "1.0.0"
  }'
```

### 3. Verify in Dashboard
- Open http://localhost:3000
- Select your farm
- Navigate to "Smart Farm & Irrigation" section
- Status should show "Connected" with live data
- Readings should update automatically

## Data Validation

The backend automatically validates:
- Temperature: -40°C to 80°C
- Humidity: 0% to 100%
- Soil Moisture: 0% to 100%
- Water Level: 0% to 100%

Invalid readings are rejected with HTTP 400 error.

## Connection Status

The system tracks device status:
- **Online**: Telemetry received within last 5 minutes
- **Stale**: Telemetry received 5-30 minutes ago
- **Offline**: No telemetry for >30 minutes

## Security

- API keys are hashed (SHA-256) before storage
- Each device has unique authentication
- HTTPS recommended for production deployment
- No telemetry accepted without valid API key

## Troubleshooting

### "401 Unauthorized"
- Verify X-Device-ID and X-API-Key headers are correct
- Re-register device if API key was lost

### "400 Bad Request"
- Check sensor readings are within valid ranges
- Verify JSON payload format matches spec
- Ensure timestamp is in ISO 8601 format

### "No data appears in dashboard"
- Verify farm_id matches the farm you're viewing
- Check device shows "online" status
- Verify telemetry interval < 5 minutes for real-time updates

### ESP32 won't connect to Wi-Fi
- Check SSID and password
- Verify 2.4GHz network (ESP32 doesn't support 5GHz)
- Ensure router is within range

## Production Deployment

For production use:
1. Use HTTPS (TLS/SSL) for API communication
2. Implement NTP time synchronization on ESP32
3. Add watchdog timer for ESP32 resets
4. Implement exponential backoff for failed requests
5. Add local data buffering for connectivity issues
6. Use static IP or mDNS for stable addressing
7. Implement OTA firmware updates

## Safety Notes

⚠️ **Physical irrigation control is currently DISABLED in software.**

Before enabling:
1. Test valve operation manually (12V power test)
2. Verify safe driver circuit (relay isolation, MOSFET rating)
3. Test water-level protection (valve won't open if reservoir empty)
4. Add mechanical shutoff valve as backup
5. Test emergency stop functionality
6. Obtain appropriate licenses if required

Physical valve control will remain disabled until:
- Hardware commissioning is complete
- Safety systems are verified
- User explicitly enables in system settings
