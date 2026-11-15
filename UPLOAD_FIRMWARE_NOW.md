# 🚀 UPLOAD FIRMWARE NOW - Quick Action Guide

**Hardware Detected**: ✅ NodeMCU on COM22  
**Device Registered**: ✅ NODEMCU_V3_ESP8266_001  
**Config Ready**: ✅ Credentials stored

---

## ⚠️ BEFORE UPLOAD - 3 Critical Steps

### 1. Switch to Phone Hotspot (5 minutes)

```
Current: School Wi-Fi (10.22.217.151)
Target: "Android 123" (your phone)
```

**Do This**:
1. Enable hotspot on phone
2. Disconnect laptop from current Wi-Fi
3. Connect to "Android 123"
4. Run: `ipconfig`
5. **If new IP different from 10.22.217.151**:
   - Edit `hardware\FieldShift_NodeMCU_V3\config.h`
   - Change `API_SERVER = "10.22.217.151";` to new IP
   - Save

### 2. Restart Backend (2 minutes)

```powershell
# Kill all Python
Get-Process python | Stop-Process -Force

# Restart backend
cd backend
python main.py
```

**Verify**: Should show `Uvicorn running on http://0.0.0.0:8000`

### 3. Add Firewall Rule (1 minute)

**Run PowerShell as Administrator**:
```powershell
New-NetFirewallRule -DisplayName "FieldShift FarmOS API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -Profile Private
```

---

## 📤 UPLOAD FIRMWARE - 5 Steps

### Step 1: Open Arduino IDE
- Launch Arduino IDE
- File → Open
- Select: `hardware\FieldShift_NodeMCU_V3\FieldShift_NodeMCU_V3.ino`

### Step 2: Configure Board
**Tools menu**:
- Board: "NodeMCU 1.0 (ESP-12E Module)"
- Port: **COM22**
- Upload Speed: 115200
- Flash Size: "4MB (FS:2MB OTA:~1019KB)"

### Step 3: Compile
- Click ✓ (Verify button)
- Wait for "Done compiling"
- Check: "Sketch uses XXXXX bytes..."

### Step 4: Upload
- Click → (Upload button)
- Wait for progress bar
- Look for "Hard resetting via RTS pin..."

### Step 5: Monitor Serial
- Tools → Serial Monitor
- Baud: **115200**
- Watch for boot sequence

---

## ✅ SUCCESS INDICATORS

### Serial Monitor Shows:
```
FieldShift FarmOS - NodeMCU V3
...
Wi-Fi connected!
IP Address: 192.168.43.XXX
...
HTTP Response: 200
✅ Telemetry sent successfully!
```

### Dashboard Shows (http://localhost:3000):
- Device Status: **Connected** (was Offline)
- Temperature: Real value (e.g., 22.5°C)
- Humidity: Real value (e.g., 65%)
- Soil Moisture: ADC value (0-1023)
- Last Seen: Recent timestamp

---

## ❌ TROUBLESHOOTING

### Wi-Fi Failed
- Check SSID: "Android 123" (exact match)
- Ensure 2.4GHz hotspot (not 5GHz)
- Move NodeMCU closer to phone

### HTTP Error
- Verify laptop IP: `ipconfig`
- Update config.h if IP changed
- Test from phone: `http://LAPTOP_IP:8000/api/farms`

### Upload Failed
- Close Serial Monitor first
- Try Upload Speed: 57600
- Press FLASH button on NodeMCU

### No Sensor Data
- DHT11: Wait 2+ seconds, check wiring
- Soil: Verify A0 connection
- Water Level: Check D6 connection

---

## 🔒 SAFETY CONFIRMED

✅ `pumpCommissioned = false` in firmware  
✅ Pump DISABLED by default  
✅ Cannot be enabled remotely  
✅ Physical commissioning required  

**Do NOT modify** this setting until:
- Sensors tested for 24+ hours
- Water level protection verified
- Emergency stop tested
- Follow pump commissioning checklist

---

## 📊 EXPECTED TIMELINE

- **Upload**: 30 seconds
- **Boot**: 5 seconds
- **Wi-Fi connect**: 5-15 seconds
- **First telemetry**: 60 seconds
- **Dashboard update**: 60-120 seconds

**Total**: ~3 minutes from upload to dashboard showing "Connected"

---

## 🎯 YOUR CHECKLIST

Before clicking Upload:

- [ ] On phone hotspot "Android 123"
- [ ] config.h has correct IP
- [ ] Backend running (0.0.0.0:8000)
- [ ] Firewall rule added
- [ ] COM22 selected in Arduino IDE
- [ ] Serial Monitor closed

After upload:

- [ ] Serial shows Wi-Fi connected
- [ ] Serial shows HTTP 200
- [ ] Dashboard shows Connected
- [ ] Real sensor values appear
- [ ] Pump shows DISABLED

---

## 🚀 READY? 

**You have everything configured. Just need to**:
1. Switch to phone hotspot
2. Click Upload in Arduino IDE
3. Watch Serial Monitor
4. Verify dashboard

**Time to complete**: ~10 minutes total

Good luck! 🎉

---

**Full Documentation**: See `NODEMCU_FINAL_STATUS.md` for complete details
