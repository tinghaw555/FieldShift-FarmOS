# NodeMCU V3 Setup Guide - Phone Hotspot Connection

**Hardware**: LOLIN NodeMCU V3 (ESP8266)  
**Goal**: Connect physical hardware to FieldShift FarmOS via phone hotspot

---

## Current Status

✅ **Backend**: Running on localhost:8000  
✅ **Database**: 10 farms available (using Farm ID: 1)  
✅ **Firmware**: Ready in `hardware/FieldShift_NodeMCU_V3/`  
❌ **Device**: Not yet registered  
❌ **Network**: Backend only accessible on localhost (needs configuration)  

---

## Step 1: Configure Backend for Network Access

The backend is currently only listening on 127.0.0.1 (localhost). We need to make it accessible on your network.

### Option A: Edit main.py (Recommended)

1. Open `backend/main.py`
2. Find the line with `uvicorn.run(...)`
3. Change `host="127.0.0.1"` to `host="0.0.0.0"`
4. Restart the backend

```python
# Before
uvicorn.run(app, host="127.0.0.1", port=8000)

# After
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Option B: Command Line Override

Stop the backend and restart with:
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Step 2: Configure Windows Firewall

Allow FastAPI to accept connections on your private network:

1. Open **Windows Defender Firewall with Advanced Security**
2. Click **Inbound Rules** → **New Rule**
3. Select **Port** → Next
4. **TCP**, Specific local ports: **8000** → Next
5. **Allow the connection** → Next
6. Check **Private** (uncheck Public and Domain) → Next
7. Name: "FieldShift FarmOS API" → Finish

**OR** use PowerShell (Run as Administrator):
```powershell
New-NetFirewallRule -DisplayName "FieldShift FarmOS API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -Profile Private
```

---

## Step 3: Connect to Phone Hotspot

1. **Enable hotspot** on your phone (Settings → Hotspot)
2. **Connect laptop** to your phone hotspot
3. **Get laptop IP** on hotspot:
   ```powershell
   ipconfig
   ```
   Look for "Wireless LAN adapter Wi-Fi" section
   Note the **IPv4 Address** (e.g., 192.168.43.xxx or similar)

**Expected IP range** (varies by phone):
- Android: Usually 192.168.43.xxx or 192.168.xxx.xxx
- iPhone: Usually 172.20.10.xxx

---

## Step 4: Register NodeMCU Device

Run the registration script:

```powershell
cd hardware
python register_device.py
```

**You'll be prompted for**:
- Wi-Fi SSID: Your phone hotspot name
- Wi-Fi Password: Your hotspot password  
- Laptop IP: The IP from Step 3

**The script will**:
- ✅ Register device with backend
- ✅ Generate secure API key
- ✅ Update config.h automatically
- ✅ Store credentials securely

**IMPORTANT**: API key is shown only once. It's stored in config.h (excluded from git).

---

## Step 5: Verify Configuration

Check `hardware/FieldShift_NodeMCU_V3/config.h`:

```cpp
const char* WIFI_SSID = "YourPhoneHotspot";
const char* WIFI_PASSWORD = "YourHotspotPassword";
const char* API_SERVER = "192.168.43.1";  // Your laptop IP
const int API_PORT = 8000;
const char* DEVICE_ID = "NODEMCU_V3_ESP8266_001";
const char* API_KEY = "generated_api_key_here";
const int FARM_ID = 1;
```

**Verify**:
- ✅ WIFI_SSID matches your hotspot name (case-sensitive!)
- ✅ WIFI_PASSWORD is correct
- ✅ API_SERVER is your laptop's hotspot IP
- ✅ DEVICE_ID is unique
- ✅ API_KEY is present (40+ characters)
- ✅ FARM_ID matches an existing farm

---

## Step 6: Test Backend Connectivity

From your phone or another device on the hotspot:

```bash
curl http://YOUR_LAPTOP_IP:8000/api/farms
```

**Expected**: JSON list of farms

If it fails:
- ❌ Check firewall rule
- ❌ Check backend is running with host="0.0.0.0"
- ❌ Verify laptop is on hotspot network
- ❌ Try pinging laptop IP from phone

---

## Step 7: Connect NodeMCU to Computer

1. **Connect NodeMCU** to laptop via Micro-USB cable
2. **Check COM port**:
   ```powershell
   mode
   ```
   Or in Device Manager → Ports (COM & LPT)
   
**Expected**: COM3, COM4, COM5, etc.

If no COM port appears:
- ❌ Install CH340G/CP2102 USB driver (NodeMCU V3 uses CH340G)
- ❌ Try different USB cable (must be data cable, not charge-only)
- ❌ Try different USB port

---

## Step 8: Upload Firmware

### Using Arduino IDE:

1. **Open**: `hardware/FieldShift_NodeMCU_V3/FieldShift_NodeMCU_V3.ino`
2. **Tools** → **Board** → "NodeMCU 1.0 (ESP-12E Module)"
3. **Tools** → **Port** → Select your COM port
4. **Upload speed**: 115200
5. **Flash size**: "4MB (FS:2MB OTA:~1019KB)"
6. Click **Verify** (checkmark icon) to compile
7. Click **Upload** (arrow icon) to flash

### Using Arduino CLI:

```powershell
cd hardware\FieldShift_NodeMCU_V3

# Compile
arduino-cli compile --fqbn esp8266:esp8266:nodemcuv2 FieldShift_NodeMCU_V3.ino

# Upload (replace COM3 with your port)
arduino-cli upload -p COM3 --fqbn esp8266:esp8266:nodemcuv2 FieldShift_NodeMCU_V3.ino
```

---

## Step 9: Monitor Serial Output

Open Serial Monitor (115200 baud):

**Expected output**:
```
====================================
FieldShift FarmOS - NodeMCU V3
LOLIN NodeMCU V3 (ESP8266)
====================================
Initializing pins (SAFE MODE)...
  STBY: LOW (driver disabled)
  ...
Connecting to Wi-Fi: YourPhoneHotspot
........
Wi-Fi connected!
IP Address: 192.168.43.25
Signal Strength: -45 dBm

====================================
SAFETY STATUS
====================================
Pump Commissioned:  NO (DISABLED)
...
-----------------------------------
Sending telemetry...
HTTP Response: 200
✅ Telemetry sent successfully!
-----------------------------------
```

---

## Step 10: Verify in Dashboard

1. Open browser: `http://localhost:3000` (or on laptop)
2. Navigate to **Smart Farm** section
3. Check **Device Status**: Should show "Connected"
4. Check **Sensor Readings**:
   - Temperature (DHT11)
   - Humidity (DHT11)
   - Soil Moisture (raw ADC value)
   - Water Level (0% or 100%)

---

## Troubleshooting

### Wi-Fi Connection Failed

**Symptoms**: "Wi-Fi connection FAILED!" in serial monitor

**Fixes**:
- ✅ Verify SSID exact match (case-sensitive)
- ✅ Verify password correct
- ✅ Ensure hotspot is 2.4GHz (ESP8266 doesn't support 5GHz)
- ✅ Check hotspot signal strength
- ✅ Try moving NodeMCU closer to phone
- ✅ Disable Wi-Fi MAC filtering on phone hotspot

### Cannot Reach API Server

**Symptoms**: "HTTP Error: connection refused" or "connection failed"

**Fixes**:
- ✅ Verify API_SERVER IP is correct (run `ipconfig` again)
- ✅ Ping laptop from NodeMCU network (if possible)
- ✅ Check firewall allows port 8000
- ✅ Verify backend running on 0.0.0.0:8000 (not 127.0.0.1)
- ✅ Test with curl from phone browser: `http://LAPTOP_IP:8000/api/farms`

### HTTP 401 Unauthorized

**Symptoms**: "Telemetry rejected by server" with HTTP 401

**Fixes**:
- ✅ Verify DEVICE_ID matches registration
- ✅ Verify API_KEY is correct (copy-paste, no extra spaces)
- ✅ Check device registered in database
- ✅ Try re-registering device (use different DEVICE_ID)

### HTTP 400 Bad Request

**Symptoms**: "Telemetry rejected by server" with HTTP 400

**Fixes**:
- ✅ Check sensor values are valid (not NaN or out of range)
- ✅ Verify DHT11 connected correctly (DATA → D2, VCC → 3.3V, GND → GND)
- ✅ Check Serial output for sensor reading errors
- ✅ Verify FARM_ID exists in database

### DHT11 Reading Failed

**Symptoms**: "DHT11 read failed!" or "DHT11 reading out of range!"

**Fixes**:
- ✅ Check DHT11 wiring (DATA → D2/GPIO4)
- ✅ Verify DHT11 has power (3.3V or 5V, check sensor specs)
- ✅ Try adding 10kΩ pull-up resistor on DATA line (DATA → 3.3V)
- ✅ Wait 2 seconds after power-on (DHT11 initialization time)
- ✅ Verify it's DHT11 not DHT22 (different timing)

### No COM Port Detected

**Symptoms**: NodeMCU not visible in Device Manager

**Fixes**:
- ✅ Install CH340G driver (most NodeMCU V3 use CH340G)
  - Download: http://www.wch.cn/downloads/CH341SER_ZIP.html
- ✅ Try different USB cable (must support data, not charge-only)
- ✅ Try different USB port
- ✅ Check Device Manager for "Unknown Device" or "Serial Port" errors
- ✅ Reboot laptop after driver install

### Upload Failed

**Symptoms**: "espcomm_upload_mem failed" or upload stalls

**Fixes**:
- ✅ Hold FLASH button during upload (if upload doesn't auto-start)
- ✅ Lower upload speed (Tools → Upload Speed → 9600 or 57600)
- ✅ Check USB cable quality
- ✅ Close Serial Monitor before uploading
- ✅ Try pressing RESET button after clicking Upload

---

## Safety Checklist

**Before ANY pump testing**:

- [ ] pumpCommissioned = **false** (default)
- [ ] Water level sensor tested and working
- [ ] TB6612FNG STBY has 10kΩ pull-down resistor
- [ ] Pump powered from external 5V (NOT NodeMCU 3.3V)
- [ ] All wiring verified and secure
- [ ] Emergency stop tested (WiFi disconnect = pump stops)

**Never**:
- ❌ Power pump from NodeMCU GPIO or 3.3V
- ❌ Set pumpCommissioned=true remotely (firmware only)
- ❌ Run pump without water level protection
- ❌ Exceed 5 minutes continuous runtime

---

## Network Diagram

```
Phone (Hotspot)
  └─ SSID: YourHotspotName
  └─ 2.4GHz Wi-Fi
      │
      ├─ Laptop (192.168.43.1 or similar)
      │   └─ FastAPI backend (port 8000)
      │   └─ Next.js frontend (port 3000)
      │
      └─ NodeMCU V3 (192.168.43.25 or assigned by phone)
          └─ Sends telemetry every 60 seconds
          └─ Polls commands every 5 seconds
```

---

## Expected Behavior

### Normal Operation:

1. **Power On**: NodeMCU boots, initializes pins SAFELY
2. **Connect**: Connects to phone hotspot Wi-Fi
3. **Register**: Gets IP from phone DHCP
4. **Telemetry**: Sends sensor data every 60 seconds
5. **Dashboard**: Shows "Connected" with real sensor values
6. **Pump**: Remains DISABLED (commissioning required)

### Data Flow:

```
NodeMCU Sensors
    ↓
Read every 2 seconds (cached)
    ↓
Send to backend every 60 seconds
    ↓
POST /api/hardware/telemetry
    ↓
Authenticated (X-Device-ID + X-API-Key)
    ↓
Stored in SQLite (sensor_readings table)
    ↓
Dashboard polls /api/hardware/farm/{farm_id}/latest
    ↓
Display real-time values
```

---

## Files Modified

- ✅ `hardware/FieldShift_NodeMCU_V3/config.h` (credentials)
- ✅ `backend/main.py` (host binding - if needed)
- ✅ Windows Firewall (port 8000 rule)

---

## Next Steps After Setup

1. **Verify Telemetry**: Check dashboard shows real sensor data
2. **Test Duration**: Run for 10+ minutes, verify stable
3. **Signal Strength**: Monitor Wi-Fi RSSI in Serial output
4. **Battery Test**: If using battery, monitor voltage/runtime
5. **Pump Testing**: Only after passing all safety checks

---

## Need Help?

**Check**:
- Serial Monitor output (115200 baud)
- Backend console logs
- Browser DevTools Network tab
- Database: `python -c "import sqlite3; conn = sqlite3.connect('backend/database/fieldshift.db'); ..."`

**Common Issues**:
- ESP8266 only supports 2.4GHz (NOT 5GHz)
- Phone hotspot must allow device-to-device communication
- Some carriers restrict hotspot functionality
- Backend must be on 0.0.0.0 (not 127.0.0.1)
- Firewall must allow private network access

---

**Ready to start? Run the registration script!**

```powershell
cd hardware
python register_device.py
```
