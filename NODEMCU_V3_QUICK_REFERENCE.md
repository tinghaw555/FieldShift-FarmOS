# NodeMCU V3 Quick Reference Card

## Hardware: LOLIN NodeMCU V3 (ESP8266)

### Pin Connections

```
Component          NodeMCU Pin    ESP8266 GPIO
─────────────────────────────────────────────────
DHT11 DATA         D2             GPIO4
Soil Moisture AO   A0             ADC0 (ONLY analog!)
Water Level DO     D6             GPIO12
TB6612 AIN1        D5             GPIO14
TB6612 AIN2        D7             GPIO13
TB6612 PWMA        D1             GPIO5
TB6612 STBY        D0             GPIO16 (10kΩ pull-down!)
```

### Critical Safety

⚠️ **MANDATORY:**
- 10kΩ resistor: D0 (STBY) → GND
- Pump power: External 5V via TB6612 VM
- NEVER power pump from NodeMCU pins!

### Firmware Location

```
hardware/FieldShift_NodeMCU_V3/FieldShift_NodeMCU_V3.ino
```

### Configuration (config.h)

```cpp
const char* WIFI_SSID = "YourNetwork";         // 2.4GHz only!
const char* WIFI_PASSWORD = "password";
const char* API_SERVER = "192.168.1.100";      // LAN IP
const char* DEVICE_ID = "NODEMCU_FARM001";
const char* API_KEY = "your-api-key-here";
const int FARM_ID = 1;
```

### Arduino IDE Setup

**Board:** NodeMCU 1.0 (ESP-12E Module)  
**Upload Speed:** 115200  
**CPU:** 80 MHz or 160 MHz

**Libraries:**
- DHT sensor library by Adafruit
- Adafruit Unified Sensor
- ArduinoJson v6.x

### Device Registration

```bash
curl -X POST http://your-server:8000/api/hardware/register \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "NODEMCU_FARM001",
    "farm_id": 1,
    "device_type": "NodeMCU-V3-ESP8266"
  }'
```

### Telemetry Format

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

### ESP8266 Constraints

- **Wi-Fi:** 2.4 GHz ONLY (no 5 GHz!)
- **Analog:** ONE input only (A0)
- **ADC:** 10-bit (0-1023)
- **RAM:** 80 KB available
- **GPIO16 (D0):** No internal pull-resistor

### Pump Safety Interlocks

Pump OFF when:
- ❌ Not commissioned (default)
- ❌ Water level low/invalid
- ❌ Wi-Fi disconnected
- ❌ Runtime > 5 minutes
- ❌ No active command
- ❌ Boot/reset occurring

### Quick Troubleshooting

**Wi-Fi fails:**
- Check 2.4 GHz network
- Verify SSID/password

**DHT11 fails:**
- Check D2 wiring
- Wait 2+ seconds between reads

**Telemetry fails:**
- Use LAN IP (not localhost)
- Check backend running
- Verify API key

**Pump starts at boot:**
- ⚠️ CRITICAL! Disconnect power!
- Check 10kΩ STBY pull-down

### Documentation

- `NODEMCU_V3_SETUP_GUIDE.md` - Full setup
- `hardware/FieldShift_NodeMCU_V3/README.md` - Firmware details
- `NODEMCU_V3_INTEGRATION_REPORT.md` - Technical report

### Support

Backend: `http://your-server:8000/api/hardware/telemetry`  
Serial Monitor: 115200 baud  
Firmware Version: 1.0.0-NodeMCU-V3
