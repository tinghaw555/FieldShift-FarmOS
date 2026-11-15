# FieldShift FarmOS - Pump Control Commissioning Checklist

## ⚠️ CRITICAL SAFETY WARNING
**Physical pump control is DISABLED by default and MUST remain disabled until ALL commissioning steps are completed successfully.**

DO NOT enable pump commissioning (`pumpCommissioned = true`) until you have verified EVERY item on this checklist.

---

## Pre-Commissioning Requirements

### Required Hardware
- [ ] LOLIN NodeMCU V3 (ESP8266) board
- [ ] TB6612FNG motor driver module
- [ ] 3-5V DC submersible water pump
- [ ] DHT11 temperature/humidity sensor
- [ ] Analog soil moisture sensor
- [ ] Digital water level sensor
- [ ] **10kΩ resistor (CRITICAL for STBY pull-down)**
- [ ] External regulated 5V power supply (for pump motor)
- [ ] Breadboard and jumper wires (or custom PCB)
- [ ] USB cable and 5V supply for NodeMCU

### Required Tools
- [ ] Digital multimeter
- [ ] USB to Serial adapter (if not using NodeMCU USB)
- [ ] Wire stripper/cutter
- [ ] Small container for water reservoir
- [ ] Bucket for pump discharge testing

### Required Software
- [ ] Arduino IDE 2.x installed
- [ ] ESP8266 board support installed (v3.1.x+)
- [ ] DHT sensor library (Adafruit)
- [ ] ArduinoJson library (v6.x)
- [ ] FieldShift FarmOS backend running
- [ ] FieldShift FarmOS frontend built and running

---

## Phase 1: Hardware Assembly

### Step 1.1: TB6612FNG to NodeMCU Connections
- [ ] VCC (TB6612FNG) → 3.3V (NodeMCU)
- [ ] GND (TB6612FNG) → GND (NodeMCU)
- [ ] AIN1 (TB6612FNG) → D5 / GPIO14 (NodeMCU)
- [ ] AIN2 (TB6612FNG) → D7 / GPIO13 (NodeMCU)
- [ ] PWMA (TB6612FNG) → D1 / GPIO5 (NodeMCU)
- [ ] STBY (TB6612FNG) → D0 / GPIO16 (NodeMCU)

### Step 1.2: CRITICAL - STBY Pull-Down Resistor
- [ ] **10kΩ resistor connected between STBY pin and GND**
- [ ] One resistor leg soldered/connected to STBY pin
- [ ] Other resistor leg connected to common ground
- [ ] Connection is secure and will not come loose
- [ ] Multimeter verification: STBY pin reads ~0V when NodeMCU is OFF

> **WHY THIS IS CRITICAL:** GPIO16 (D0) does NOT have internal pull-resistors. Without external pull-down, the pin floats during boot/reset, potentially enabling the motor driver and activating the pump unexpectedly.

### Step 1.3: Motor Power Supply
- [ ] VM (TB6612FNG) → External regulated 5V supply (+)
- [ ] GND (External supply) → Common ground with NodeMCU and TB6612FNG
- [ ] **VERIFIED: VM is NOT connected to NodeMCU 3.3V or Vin**
- [ ] External supply can deliver at least 500mA (typical pump current)
- [ ] Supply voltage measured: 4.8V - 5.2V

> **WARNING:** NEVER power the pump from NodeMCU GPIO pins or 3.3V rail. The pump will draw too much current and damage the board.

### Step 1.4: Pump Connections
- [ ] AO1 (TB6612FNG) → Pump motor lead 1
- [ ] AO2 (TB6612FNG) → Pump motor lead 2
- [ ] Pump polarity noted (which lead is +)
- [ ] Connections are secure and insulated

### Step 1.5: Sensor Connections
- [ ] DHT11 DATA → D2 / GPIO4 (NodeMCU)
- [ ] DHT11 VCC → 3.3V (NodeMCU)
- [ ] DHT11 GND → GND (NodeMCU)
- [ ] Soil Moisture Signal → A0 (NodeMCU) - **ONLY analog input!**
- [ ] Soil Moisture VCC → 3.3V or 5V (check sensor specs)
- [ ] Soil Moisture GND → GND (NodeMCU)
- [ ] Water Level Signal → D6 / GPIO12 (NodeMCU)
- [ ] Water Level VCC → 3.3V or 5V (check sensor specs)
- [ ] Water Level GND → GND (NodeMCU)

### Step 1.6: Physical Installation
- [ ] Pump submerged in water reservoir (completely covered)
- [ ] Discharge hose attached to pump outlet
- [ ] Discharge hose directed into empty bucket (for testing)
- [ ] Water reservoir has at least 500ml of water
- [ ] Water level sensor positioned correctly in reservoir
- [ ] No water can reach electronic components
- [ ] All wiring secure and will not fall into water

---

## Phase 2: Firmware Configuration

### Step 2.1: Edit config.h
- [ ] Opened `hardware/FieldShift_NodeMCU_V3/config.h`
- [ ] Set `WIFI_SSID` to your 2.4GHz network name
- [ ] Set `WIFI_PASSWORD` to your network password
- [ ] Set `API_SERVER` to backend IP address (NOT localhost!)
- [ ] Set `API_PORT` to 8000 (or your backend port)
- [ ] **LEFT `pumpCommissioned = false`** (in .ino file, NOT config.h)

### Step 2.2: Device Registration
- [ ] Backend is running
- [ ] Used API client (Postman/curl) to register device:
  ```bash
  POST http://YOUR_API_SERVER:8000/api/hardware/register
  {
    "device_id": "NODEMCU_FARM001",
    "farm_id": 1,
    "device_type": "NodeMCU-V3-ESP8266"
  }
  ```
- [ ] Received API key in response
- [ ] Set `DEVICE_ID` in config.h to match registration
- [ ] Set `API_KEY` in config.h to received key
- [ ] Set `FARM_ID` in config.h to correct farm ID

### Step 2.3: Compile and Upload Firmware
- [ ] Opened Arduino IDE
- [ ] Opened `FieldShift_NodeMCU_V3.ino`
- [ ] Selected board: **Tools → Board → ESP8266 Boards → NodeMCU 1.0 (ESP-12E Module)**
- [ ] Selected correct COM port
- [ ] Upload settings:
  - Upload Speed: 115200
  - CPU Frequency: 80 MHz
  - Flash Size: 4MB (FS:2MB OTA:~1019KB)
- [ ] Clicked Verify (checkmark icon) - **compilation successful**
- [ ] Clicked Upload (arrow icon) - **upload successful**
- [ ] Opened Serial Monitor (115200 baud)

---

## Phase 3: Initial Boot Verification

### Step 3.1: Serial Monitor Boot Sequence
- [ ] Serial Monitor shows:
  ```
  ====================================
  FieldShift FarmOS - NodeMCU V3
  LOLIN NodeMCU V3 (ESP8266)
  ====================================
  ```
- [ ] Pin initialization message appears
- [ ] "STBY: LOW (driver disabled)" appears
- [ ] "Pump: DISABLED" appears
- [ ] Wi-Fi connection succeeds
- [ ] IP address is displayed
- [ ] Pump Commissioned shows: "NO (DISABLED)"

### Step 3.2: Physical Pin Verification (Multimeter)
**POWER OFF EVERYTHING FIRST**
- [ ] STBY pin voltage: ~0V (pulled down by resistor)
- [ ] AIN1 pin voltage: ~0V
- [ ] AIN2 pin voltage: ~0V
- [ ] PWMA pin voltage: ~0V

**POWER ON NodeMCU (DO NOT POWER MOTOR SUPPLY YET)**
- [ ] Immediately after boot:
  - [ ] STBY pin: LOW (~0V)
  - [ ] AIN1 pin: LOW (~0V)
  - [ ] AIN2 pin: LOW (~0V)

**POWER ON Motor Supply**
- [ ] VM pin on TB6612FNG: 5V
- [ ] AO1 and AO2 voltage: ~0V (motor driver disabled)
- [ ] Pump does NOT run

### Step 3.3: Reboot Testing (CRITICAL SAFETY TEST)
Repeat 5 times:
- [ ] Press NodeMCU RST button or power cycle
- [ ] During boot sequence:
  - [ ] STBY pin remains LOW
  - [ ] Pump does NOT activate
  - [ ] No clicking sound from TB6612FNG
  - [ ] After boot, "Pump: DISABLED" in Serial Monitor
- [ ] **All 5 reboot tests passed**

> If pump activates even ONCE during reboot, **STOP IMMEDIATELY**. Check pull-down resistor.

---

## Phase 4: Backend Connectivity

### Step 4.1: Telemetry Verification
- [ ] Serial Monitor shows "Sending telemetry..."
- [ ] HTTP Response: 200
- [ ] "Telemetry sent successfully!" appears
- [ ] Backend logs show received telemetry
- [ ] Dashboard shows device as "Online"
- [ ] Temperature and humidity values appear in dashboard
- [ ] Soil moisture value appears (raw ADC 0-1023)
- [ ] Water level shows "OK" (100%) with water present

### Step 4.2: Sensor Reading Validation
- [ ] DHT11:
  - [ ] Temperature: 15-40°C (reasonable room temperature)
  - [ ] Humidity: 20-90% (reasonable range)
  - [ ] No NaN readings
  
- [ ] Soil Moisture:
  - [ ] ADC value: 0-1023
  - [ ] Changes when sensor moved between air and water
  - [ ] In air (dry): High value (e.g., 800-1023)
  - [ ] In water (wet): Low value (e.g., 200-400)

- [ ] Water Level:
  - [ ] With water: Shows 100% / OK
  - [ ] Remove water: Shows 0% / LOW
  - [ ] Restore water: Shows 100% / OK again
  - [ ] **If inverted, set `WATER_LEVEL_ACTIVE_LOW = false` in config.h**

### Step 4.3: Dashboard Verification
- [ ] Opened FieldShift FarmOS dashboard
- [ ] Selected farm
- [ ] Smart Farm & Irrigation section shows:
  - [ ] Device status: "Online" with green badge
  - [ ] Temperature: Live value
  - [ ] Humidity: Live value
  - [ ] Soil Moisture: Live value
  - [ ] Reservoir Level: 100% (green)
  - [ ] Pump status card visible
  - [ ] Pump state: OFF
  - [ ] Device: Online
  - [ ] Reservoir: OK
  - [ ] Commissioned: No

---

## Phase 5: Command Flow Testing (Pump Still Disabled)

### Step 5.1: Command Polling Verification
- [ ] Serial Monitor shows polling messages every 5 seconds
- [ ] No errors during polling
- [ ] "command": null (no commands pending)

### Step 5.2: Rejected START Command Test
- [ ] Dashboard: Clicked "Start Pump" button
- [ ] Confirmation dialog appears
- [ ] Clicked "Confirm Start"
- [ ] Serial Monitor shows:
  - [ ] "New pump command received!"
  - [ ] "Pump START denied: Pump not commissioned"
- [ ] Command acknowledgement sent with status: "failed"
- [ ] Dashboard shows error: "Pump not commissioned"
- [ ] Pump did NOT run
- [ ] No voltage on AO1/AO2

### Step 5.3: Successful STOP Command Test
- [ ] Dashboard: Clicked "Stop Pump" button (even though pump is off)
- [ ] Serial Monitor shows:
  - [ ] Command received
  - [ ] "Pump STOPPED"
  - [ ] Acknowledgement: "completed"
- [ ] Dashboard updates to show command completed

---

## Phase 6: Water Level Protection Testing

### Step 6.1: Enable Commissioning (CAREFULLY!)
- [ ] **Read and understood all safety warnings**
- [ ] All previous tests passed
- [ ] Pump is properly submerged
- [ ] Discharge hose positioned into bucket
- [ ] Standing by with power disconnect switch
- [ ] Edit firmware line ~30:
  ```cpp
  bool pumpCommissioned = true;  // Changed from false
  ```
- [ ] Upload firmware
- [ ] Wait for boot
- [ ] Serial Monitor shows: "Pump Commissioned: YES (ENABLED)"
- [ ] Dashboard refreshes and shows: "Commissioned: Yes"

### Step 6.2: Low Water Protection Test
**DO NOT activate pump motor yet!**

- [ ] Remove water from reservoir (below sensor level)
- [ ] Serial Monitor shows: "Water Level OK: NO"
- [ ] Dashboard shows: "Reservoir: ⚠️ Low"
- [ ] Try to start pump from dashboard
- [ ] Serial Monitor shows: "Pump START denied: Water level low or invalid"
- [ ] Dashboard shows error: "Cannot start: Reservoir level is low"
- [ ] Pump did NOT run
- [ ] **Test PASSED: Low water protection works**

- [ ] Restore water to reservoir
- [ ] Serial Monitor shows: "Water Level OK: YES"
- [ ] Dashboard shows: "Reservoir: ✓ OK"

---

## Phase 7: First Pump Activation (2 Second Test)

### Step 7.1: Preparation
- [ ] Water reservoir full
- [ ] Pump fully submerged
- [ ] Discharge hose in empty bucket
- [ ] All personnel clear of water and electrical connections
- [ ] **Hand on power disconnect switch**
- [ ] Serial Monitor visible
- [ ] Dashboard visible

### Step 7.2: Modify Duration for Safety
- [ ] Edit firmware line containing `duration_seconds: Optional[int] = Field(default=10...`
- [ ] Or: Edit frontend SmartFarmSection.tsx to request 2 seconds:
  ```typescript
  duration_seconds: 2  // Changed from 10
  ```
- [ ] Rebuild frontend if changed
- [ ] Or: For firmware test, acknowledge 2 seconds manually

### Step 7.3: Execute 2-Second Test
- [ ] Dashboard: Click "Start Pump"
- [ ] Read confirmation dialog carefully
- [ ] Click "Confirm Start"
- [ ] Observe Serial Monitor:
  ```
  📩 New pump command received!
  ✅ Starting pump (commissioning mode)...
  Pump RUNNING
  ```
- [ ] Observe dashboard:
  - "Starting..." → "ON" (within 5-10 seconds)
- [ ] Observe motor:
  - [ ] TB6612FNG LED lights up (if present)
  - [ ] Pump makes humming/whirring sound
  - [ ] Water flows from discharge hose
- [ ] After 2 seconds:
  - [ ] Pump automatically stops
  - [ ] Serial Monitor: "Pump STOPPED"
  - [ ] Dashboard: "OFF"
  - [ ] Water flow ceases

### Step 7.4: Verify Safe Stop
- [ ] Pump is OFF
- [ ] No continuous running
- [ ] No errors in Serial Monitor
- [ ] Dashboard shows "OFF" status
- [ ] Command status: "completed"

**If pump did not stop after 2 seconds, or any abnormality:**
- 🚨 **DISCONNECT POWER IMMEDIATELY**
- Do not proceed
- Review wiring and firmware
- Check for firmware infinite loop

---

## Phase 8: Emergency Stop Testing

### Step 8.1: Manual Emergency Stop
- [ ] Dashboard: Start pump (2 second duration)
- [ ] While pump is running, immediately click "Stop Pump"
- [ ] Observe:
  - [ ] Pump stops within 1-2 seconds
  - [ ] Serial Monitor: "Pump STOPPED"
  - [ ] Dashboard: "OFF"
  - [ ] No errors or faults

### Step 8.2: Wi-Fi Disconnect Protection
- [ ] Start pump (5 second duration)
- [ ] **While running**, disconnect Wi-Fi:
  - Option A: Unplug router
  - Option B: Move NodeMCU out of Wi-Fi range
  - Option C: Disable Wi-Fi on router
- [ ] Observe:
  - [ ] Within 30 seconds, Serial Monitor shows: "Wi-Fi disconnected"
  - [ ] Serial Monitor: "🚨 PUMP EMERGENCY STOP!"
  - [ ] Pump stops immediately
  - [ ] Dashboard shows: "Offline"
- [ ] Restore Wi-Fi
- [ ] Verify reconnection

### Step 8.3: Low Water During Operation
- [ ] Start pump (10 second duration)
- [ ] **While running**, carefully remove water below sensor level
- [ ] Observe:
  - [ ] Serial Monitor: "🚨 PUMP EMERGENCY STOP! Reason: Water level low"
  - [ ] Pump stops immediately
  - [ ] Dashboard shows: "FAULT"
  - [ ] Fault reason displayed
- [ ] Restore water
- [ ] Pump remains stopped (fault state)
- [ ] Can manually restart after water restored

---

## Phase 9: Extended Runtime Testing

### Step 9.1: 10-Second Run
- [ ] Dashboard: Start pump (10 seconds - default)
- [ ] Monitor entire run:
  - [ ] Pump starts successfully
  - [ ] Runs continuously for 10 seconds
  - [ ] Auto-stops at 10 seconds
  - [ ] No overheating (touch TB6612FNG heatsink carefully)
  - [ ] No unexpected reboots
  - [ ] Water delivery consistent

### Step 9.2: 30-Second Run
- [ ] Modify frontend to request 30 seconds
- [ ] Start pump
- [ ] Monitor:
  - [ ] Pump runs for full 30 seconds
  - [ ] Auto-stops correctly
  - [ ] TB6612FNG temperature (should be warm, not burning hot)
  - [ ] No smoke or burning smell
  - [ ] NodeMCU does not reboot
  - [ ] Sufficient water remains in reservoir

### Step 9.3: Maximum Runtime Limit (Optional)
- [ ] Request 300 seconds (5 minutes - firmware maximum)
- [ ] Verify firmware enforces limit
- [ ] Monitor for entire duration
- [ ] Check motor driver and pump temperature
- [ ] Ensure reservoir has enough water

---

## Phase 10: Reliability Testing

### Step 10.1: Repeated Cycles
Perform 10 consecutive pump cycles:
- [ ] Cycle 1: Start → Run 10s → Auto-stop
- [ ] Cycle 2: Start → Run 10s → Auto-stop
- [ ] Cycle 3: Start → Run 10s → Auto-stop
- [ ] Cycle 4: Start → Run 10s → Auto-stop
- [ ] Cycle 5: Start → Run 10s → Auto-stop
- [ ] Cycle 6: Start → Run 10s → Auto-stop
- [ ] Cycle 7: Start → Run 10s → Auto-stop
- [ ] Cycle 8: Start → Run 10s → Auto-stop
- [ ] Cycle 9: Start → Run 10s → Auto-stop
- [ ] Cycle 10: Start → Run 10s → Auto-stop

**Verify:**
- [ ] All cycles completed successfully
- [ ] No failures or timeouts
- [ ] No reboots
- [ ] No command errors
- [ ] Consistent water delivery

### Step 10.2: Long-Term Connectivity
- [ ] Leave system running for 1 hour
- [ ] Telemetry continues every 60 seconds
- [ ] Command polling continues every 5 seconds
- [ ] No connection dropouts
- [ ] No memory leaks (monitor Serial output)
- [ ] Device remains "Online" in dashboard

---

## Phase 11: Production Readiness

### Step 11.1: Final Safety Verification
- [ ] 10kΩ pull-down resistor confirmed installed
- [ ] All wiring secure and insulated
- [ ] No exposed conductors
- [ ] Water cannot reach electronics
- [ ] Pump positioned safely
- [ ] Discharge properly routed
- [ ] Emergency power disconnect accessible
- [ ] All personnel trained on emergency stop procedure

### Step 11.2: Documentation
- [ ] Wiring diagram documented (photo or schematic)
- [ ] Pin assignments recorded
- [ ] Sensor calibration values noted
- [ ] Device ID and API key backed up securely
- [ ] Contact information for technical support
- [ ] Emergency procedures posted near installation

### Step 11.3: Operator Training
- [ ] Demonstrated dashboard pump controls
- [ ] Explained pump states (OFF, Starting, ON, Stopping, Fault)
- [ ] Practiced emergency stop
- [ ] Explained fault conditions
- [ ] Showed how to check reservoir level
- [ ] Demonstrated manual power disconnect

### Step 11.4: First Production Run
- [ ] All commissioning tests passed
- [ ] System running reliably for 24 hours
- [ ] No unexpected behaviors
- [ ] Supervisor present for first production watering
- [ ] Start with conservative duration (30 seconds)
- [ ] Monitor entire operation
- [ ] Verify expected soil moisture increase
- [ ] Document water delivery effectiveness

---

## Sign-Off

### Commissioning Completed By:
- Name: ___________________________
- Date: ___________________________
- Signature: ___________________________

### Verification Performed By (if different):
- Name: ___________________________
- Date: ___________________________
- Signature: ___________________________

### Commissioning Status:
- [ ] ✅ **PASSED** - System ready for production use
- [ ] ❌ **FAILED** - See notes below

### Notes / Issues:
```
_____________________________________________________________________________

_____________________________________________________________________________

_____________________________________________________________________________
```

---

## Decommissioning / Emergency Disable

**If at any time the pump system becomes unsafe or unreliable:**

1. **Immediate Actions:**
   - [ ] Disconnect pump motor power (VM supply)
   - [ ] Set `pumpCommissioned = false` in firmware
   - [ ] Upload firmware
   - [ ] Post warning sign on equipment

2. **Investigation Required Before Re-Enabling:**
   - [ ] Identify root cause of failure
   - [ ] Repair or replace faulty components
   - [ ] Re-run affected commissioning tests
   - [ ] Document changes made
   - [ ] Obtain second technician verification

---

**END OF CHECKLIST**

**Remember:** Safety first. If in doubt, leave pump disabled and consult technical support.
