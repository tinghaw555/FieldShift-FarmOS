# FieldShift FarmOS - Pump Control Quick Start Guide

## What Was Implemented

Real water pump ON/OFF control for FieldShift FarmOS with end-to-end integration:
- ✅ Dashboard UI with pump status and control buttons
- ✅ FastAPI backend with authenticated command API
- ✅ NodeMCU V3 firmware with command polling and safety system
- ✅ Database schema for command tracking and state history
- ✅ Multi-layer safety architecture

## Safety Status

⚠️ **Physical pump activation is DISABLED by default and cannot be enabled remotely.**

To enable pump control, you must:
1. Complete hardware assembly with proper wiring
2. Add 10kΩ pull-down resistor to STBY pin (CRITICAL!)
3. Complete full commissioning checklist
4. Edit firmware: `pumpCommissioned = true`
5. Upload firmware to NodeMCU

**See:** `PUMP_COMMISSIONING_CHECKLIST.md` for complete safety procedures.

---

## Quick Command Reference

### Dashboard Actions

**Start Pump:**
1. Select farm
2. Click "Start Pump" in Smart Farm & Irrigation section
3. Confirm activation
4. Pump runs for 10 seconds (default)
5. Auto-stops

**Stop Pump:**
1. Click "Stop Pump" (emergency stop)
2. Pump stops immediately

**View Status:**
- Pump State: OFF / Starting / ON / Stopping / FAULT / Unknown
- Device Status: Online / Stale / Offline
- Reservoir Level: OK / Low
- Commissioned: Yes / No
- Fault Reason (if applicable)

### API Endpoints

**Create Pump Command:**
```bash
POST http://localhost:8000/api/hardware/pump/command
Content-Type: application/json

{
  "device_id": "NODEMCU_FARM001",
  "farm_id": 1,
  "action": "start",
  "duration_seconds": 10
}
```

**Get Pump Status:**
```bash
GET http://localhost:8000/api/hardware/pump/status/NODEMCU_FARM001
```

**Poll Commands (NodeMCU):**
```bash
GET http://localhost:8000/api/hardware/pump/commands/NODEMCU_FARM001/pending
X-API-Key: your_api_key_here
```

**Acknowledge Command (NodeMCU):**
```bash
POST http://localhost:8000/api/hardware/pump/commands/acknowledge
Content-Type: application/json
X-Device-ID: NODEMCU_FARM001
X-API-Key: your_api_key_here

{
  "command_id": "uuid-here",
  "status": "completed",
  "result": "Pump ran for 10 seconds"
}
```

**Report Pump State (NodeMCU):**
```bash
POST http://localhost:8000/api/hardware/pump/state
Content-Type: application/json
X-Device-ID: NODEMCU_FARM001
X-API-Key: your_api_key_here

{
  "device_id": "NODEMCU_FARM001",
  "pump_running": true,
  "commissioned": false,
  "fault_detected": false,
  "water_level_ok": true
}
```

### Firmware Configuration

**config.h:**
```cpp
const char* WIFI_SSID = "Your_Network_2.4GHz";
const char* WIFI_PASSWORD = "password";
const char* API_SERVER = "192.168.1.100";  // Your backend IP
const int API_PORT = 8000;
const char* DEVICE_ID = "NODEMCU_FARM001";
const char* API_KEY = "your_32_char_api_key_from_registration";
const int FARM_ID = 1;
const char* FIRMWARE_VERSION = "2.0.0-NodeMCU-V3-PumpControl";
#define TELEMETRY_INTERVAL_MS 60000  // 60 seconds
#define COMMAND_POLL_INTERVAL_MS 5000  // 5 seconds
```

**Enable commissioning (after safety verification):**
```cpp
// In FieldShift_NodeMCU_V3.ino line ~30
bool pumpCommissioned = true;  // Changed from false
```

---

## Hardware Pin Connections

### NodeMCU V3 → TB6612FNG
| NodeMCU Pin | GPIO | TB6612FNG Pin | Purpose |
|-------------|------|---------------|---------|
| 3.3V | - | VCC | Logic power |
| GND | - | GND | Common ground |
| D5 | GPIO14 | AIN1 | Motor direction |
| D7 | GPIO13 | AIN2 | Motor direction |
| D1 | GPIO5 | PWMA | Motor enable/PWM |
| D0 | GPIO16 | STBY | Driver enable |

**⚠️ CRITICAL:** Add 10kΩ resistor between STBY and GND (pull-down)

### TB6612FNG → Pump
| TB6612FNG Pin | Connection |
|---------------|------------|
| VM | External 5V supply (+) |
| GND | External 5V supply (-) AND NodeMCU GND |
| AO1 | Pump motor lead 1 |
| AO2 | Pump motor lead 2 |

**⚠️ NEVER power pump from NodeMCU 3.3V or GPIO pins!**

### Sensors → NodeMCU
| Sensor | NodeMCU Pin | GPIO | Notes |
|--------|-------------|------|-------|
| DHT11 DATA | D2 | GPIO4 | Temperature/humidity |
| Soil Moisture | A0 | ADC0 | ONLY analog input! |
| Water Level | D6 | GPIO12 | Digital sensor |

---

## System Architecture

```
┌─────────────────────┐
│  Dashboard (React)  │
│                     │
│  ┌───────────────┐  │
│  │ Pump Controls │  │
│  │ Start / Stop  │  │
│  │               │  │
│  │  Status Card  │  │
│  │  ● ON/OFF    │  │
│  │  ● Device     │  │
│  │  ● Reservoir  │  │
│  └───────┬───────┘  │
└──────────┼──────────┘
           │ HTTP REST
           ▼
┌─────────────────────┐
│ Backend (FastAPI)   │
│                     │
│  /pump/command      │ ← Dashboard creates command
│  /pump/status       │ ← Dashboard polls status
│  /pump/commands/... │ ← NodeMCU polls commands
│  /pump/state        │ ← NodeMCU reports state
│                     │
│  ┌───────────────┐  │
│  │   SQLite DB   │  │
│  │ pump_commands │  │
│  │ pump_states   │  │
│  └───────────────┘  │
└──────────┬──────────┘
           │ HTTP REST (polling)
           ▼
┌─────────────────────┐
│ NodeMCU V3 (ESP8266)│
│                     │
│  pollPumpCommands() │ ← Every 5 seconds
│  executeActiveCmd() │ ← Command execution
│  enforcePumpSafety()│ ← Every loop iteration
│  sendPumpState()    │ ← With telemetry
│                     │
│  ┌───────────────┐  │
│  │ Safety System │  │
│  │ ✓ Commissioned│  │
│  │ ✓ Water level │  │
│  │ ✓ WiFi conn.  │  │
│  │ ✓ Runtime max │  │
│  │ ✓ Cmd expiry  │  │
│  └───────┬───────┘  │
└──────────┼──────────┘
           │ GPIO Control
           ▼
┌─────────────────────┐
│ TB6612FNG Driver    │
│ STBY ← Pull-down!   │
│ AIN1, AIN2, PWMA    │
│                     │
│  AO1 ────┐          │
│          ├─→ Pump   │
│  AO2 ────┘          │
│  VM ← External 5V   │
└─────────────────────┘
```

---

## Command Flow Timeline

### START Command
```
T+0s    User clicks "Start Pump"
T+0.1s  POST /pump/command (backend)
T+0.2s  Command stored (status: pending)
T+5s    NodeMCU polls, receives command
T+5.1s  Acknowledges (status: acknowledged)
T+5.2s  Safety checks PASS
T+5.3s  🟢 PUMP STARTS (motor on)
T+5.4s  Reports state (pump_running: true)
T+6s    Dashboard shows "ON"
T+15.3s Duration complete (10 seconds)
T+15.4s 🔴 PUMP STOPS (motor off)
T+15.5s Acknowledges (status: completed)
T+15.6s Reports state (pump_running: false)
T+16s   Dashboard shows "OFF"
```

**Total latency:** 5-10 seconds (due to HTTP polling)

---

## Safety Features

### Multi-Layer Protection

**Dashboard Layer:**
- Validates device online
- Checks reservoir level
- Requires user confirmation
- Displays commissioning status

**Backend Layer:**
- Authenticates device
- Validates last_seen < 2 minutes
- Commands expire after 60 seconds
- Duration limited to 300 seconds max

**Firmware Layer:**
- Boot-safe pin initialization
- External pull-down on STBY
- Continuous safety monitoring (every 100ms)
- Emergency stop on any fault
- Nonblocking runtime enforcement
- Wi-Fi connection monitoring
- Water level protection
- Runtime limit (5 minutes max)
- Command expiry checking

### Emergency Stop Triggers
- 🔴 Low/invalid water level
- 🔴 WiFi disconnection
- 🔴 Runtime exceeded (5 min)
- 🔴 Command expired
- 🔴 User clicked Stop button

### Fail-Safe Design
- Pump OFF at boot
- Pump OFF during reset
- Pump OFF if WiFi lost
- Pump OFF if power lost
- Not commissioned by default
- Cannot enable remotely

---

## Troubleshooting

### "Device Offline"
**Cause:** NodeMCU not sending telemetry or last_seen > 2 minutes  
**Fix:** Check NodeMCU power, Wi-Fi, Serial Monitor

### "Pump not commissioned"
**Cause:** `pumpCommissioned = false` (CORRECT default!)  
**Fix:** Complete commissioning checklist, then edit firmware

### "Cannot start: Reservoir level is low"
**Cause:** Water level sensor reports LOW  
**Fix:** Add water, or check sensor wiring/polarity

### "Pump activates during boot"
**Cause:** ⚠️ MISSING pull-down resistor on STBY!  
**Fix:** Add 10kΩ resistor between STBY (D0) and GND

### Pump doesn't run when START sent
**Cause:** Hardware issue or commissioning disabled  
**Checks:**
1. Is `pumpCommissioned = true`?
2. Is water level OK?
3. Is TB6612FNG VM pin powered (5V)?
4. Are pump leads connected?
5. Does pump work with direct power?

### NodeMCU reboots when pump starts
**Cause:** Power supply overload  
**Fix:** Use external 5V supply for motor (VM pin), not NodeMCU

---

## Testing Without Physical Hardware

The system is designed to work even without physical NodeMCU:

**Backend:**
- ✅ All endpoints functional
- ✅ Command creation works
- ✅ Status API returns graceful "offline" state

**Dashboard:**
- ✅ Shows "Device Offline" message
- ✅ Disables pump start button
- ✅ Displays registered devices
- ✅ Demo mode still works for sensor simulation

**Result:** Safe development and testing without risk of physical activation.

---

## Files Modified

| File | Changes |
|------|---------|
| `backend/database/db.py` | Added pump_commands, pump_states tables |
| `backend/models/schemas.py` | Added pump control models |
| `backend/routers/hardware.py` | Added 5 pump control endpoints |
| `backend/migrate_pump_tables.py` | New migration script |
| `hardware/.../config.h` | Added COMMAND_POLL_INTERVAL_MS |
| `hardware/.../FieldShift_NodeMCU_V3.ino` | Added command polling and pump control |
| `frontend/.../SmartFarmSection.tsx` | Complete pump control UI |

---

## Next Steps

### Without Hardware
1. ✅ System is ready
2. ✅ Dashboard shows offline gracefully
3. ✅ Development continues normally

### With Hardware (After Commissioning)
1. ⚠️ Complete `PUMP_COMMISSIONING_CHECKLIST.md`
2. ⚠️ Verify ALL safety items
3. ⚠️ Test with pump disconnected first
4. ⚠️ Enable commissioning (`pumpCommissioned = true`)
5. ⚠️ Test with 2-second duration
6. ⚠️ Gradually increase duration
7. ⚠️ First production run: Supervised!

---

## Additional Documentation

- **Full Implementation Details:** `PUMP_CONTROL_IMPLEMENTATION_REPORT.md`
- **Complete Commissioning:** `PUMP_COMMISSIONING_CHECKLIST.md`
- **Hardware Setup:** `NODEMCU_V3_SETUP_GUIDE.md`
- **Quick Reference:** `NODEMCU_V3_QUICK_REFERENCE.md`

---

## Support

**System Status:**
- ✅ Backend: Running
- ✅ Frontend: Built (19.7 kB)
- ✅ Database: Migrated
- ⏳ Firmware: Requires Arduino IDE compilation
- ⏳ Hardware: Requires commissioning

**For Issues:**
1. Check Serial Monitor (firmware)
2. Check backend logs
3. Check browser console (dashboard)
4. Review troubleshooting section
5. Verify commissioning checklist

**Remember:** Physical pump activation is DISABLED by default for safety. This is intentional and correct behavior.
