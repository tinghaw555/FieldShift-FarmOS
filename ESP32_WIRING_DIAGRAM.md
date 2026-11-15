# ESP32 DevKit - Wiring Diagram & Connection Guide

**⚠️ CRITICAL WARNING**: This is for **ESP32 DevKit**, NOT ESP8266/NodeMCU V3!  
**Pin numbers are completely different!**

---

## Visual Wiring Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESP32 DevKit (CH340)                          │
│                                                                   │
│  3.3V ●───┬───────────────┬──────────────┬───────────────┐      │
│           │               │              │               │      │
│  GND  ●───┼───┬───────────┼──────────────┼───────────────┼────┐ │
│           │   │           │              │               │    │ │
│  GPIO18 ●─┼───┼───────────┼──────────────┼───────────────┼────┼─┼─→ DHT11 DATA
│           │   │           │              │               │    │ │
│  GPIO23 ●─┼───┼───────────┼──────────────┼───────────────┼────┼─┼─→ STBY (+ pull-down)
│           │   │           │              │               │    │ │
│  GPIO25 ●─┼───┼───────────┼──────────────┼───────────────┼────┼─┼─→ AIN1
│           │   │           │              │               │    │ │
│  GPIO26 ●─┼───┼───────────┼──────────────┼───────────────┼────┼─┼─→ AIN2
│           │   │           │              │               │    │ │
│  GPIO27 ●─┼───┼───────────┼──────────────┼───────────────┼────┼─┼─→ PWMA
│           │   │           │              │               │    │ │
│  GPIO34 ●─┼───┼───────────┼──────────────┼───────────────┼────┼─┼─→ Soil Moisture AO
│  (ADC1) input-only        │              │               │    │ │
│           │   │           │              │               │    │ │
│  GPIO35 ●─┼───┼───────────┼──────────────┼───────────────┼────┼─┼─→ Water Level AO
│  (ADC1) input-only        │              │               │    │ │
│           │   │           │              │               │    │ │
└───────────┼───┼───────────┼──────────────┼───────────────┼────┼─┘
            │   │           │              │               │    │
            ↓   ↓           ↓              ↓               ↓    ↓
         DHT11  Soil    Water Level    TB6612FNG      Common GND
                Sensor     Sensor      Motor Driver
```

---

## Component Connections

### 1. DHT11 Temperature/Humidity Sensor

```
DHT11 Sensor (3 pins)
┌─────────────┐
│   ┌───┐     │
│   │DHT│     │
│   │11 │     │
│   └───┘     │
│             │
│ [+] [-] [S] │  ← Looking at sensor from front
└──┬───┬───┬──┘
   │   │   │
   │   │   └────→ GPIO18 (ESP32)
   │   └────────→ GND (ESP32)
   └────────────→ 3.3V (ESP32) or 5V if available

Optional: 10kΩ resistor between [S] and [+] (pull-up)
```

**Connection Table**:
| DHT11 Pin | Wire Color (typical) | ESP32 Pin | Notes |
|-----------|----------------------|-----------|-------|
| VCC (+) | Red | 3.3V | Can use 5V if available |
| GND (-) | Black | GND | Common ground |
| DATA (S) | Yellow/White | GPIO18 | Digital data |

---

### 2. Soil Moisture Sensor (Analog Capacitive)

```
Soil Moisture Sensor
┌─────────────────┐
│  ┌───────────┐  │
│  │ Capacitive│  │
│  │   Sensor  │  │
│  └───────────┘  │
│                 │
│  [+] [-] [AO]   │
└───┬───┬───┬─────┘
    │   │   │
    │   │   └────→ GPIO34 (ADC1_CH6) - Input-only!
    │   └────────→ GND (ESP32)
    └────────────→ 3.3V (ESP32)

⚠️ GPIO34 is INPUT-ONLY (no internal pull resistors)
⚠️ Max voltage: 3.3V (no 5V tolerance!)
```

**Connection Table**:
| Sensor Pin | Wire Color (typical) | ESP32 Pin | Notes |
|------------|----------------------|-----------|-------|
| VCC (+) | Red | 3.3V | NOT 5V! |
| GND (-) | Black | GND | Common ground |
| AO (Analog) | Green/Yellow | GPIO34 | 12-bit ADC (0-4095) |

**Important**: Some soil sensors have both AO (analog) and DO (digital). Use AO pin.

---

### 3. Water Level Sensor (Analog)

```
Water Level Sensor (Analog)
┌─────────────────┐
│   ┌─────────┐   │
│   │ ≈≈≈≈≈≈≈ │   │  ← Water level detection area
│   │ ≈≈≈≈≈≈≈ │   │
│   │ ≈≈≈≈≈≈≈ │   │
│   └─────────┘   │
│                 │
│  [+] [-] [AO]   │
└───┬───┬───┬─────┘
    │   │   │
    │   │   └────→ GPIO35 (ADC1_CH7) - Input-only!
    │   └────────→ GND (ESP32)
    └────────────→ 3.3V (ESP32) or 5V if sensor supports

⚠️ GPIO35 is INPUT-ONLY (no internal pull resistors)
⚠️ If 5V sensor, use voltage divider to 3.3V max!
```

**Connection Table (Analog)**:
| Sensor Pin | Wire Color (typical) | ESP32 Pin | Notes |
|------------|----------------------|-----------|-------|
| VCC (+) | Red | 3.3V or 5V | Check sensor specs |
| GND (-) | Black | GND | Common ground |
| AO (Analog) | Yellow | GPIO35 | 12-bit ADC (0-4095) |

**Alternative: Digital Water Level Sensor**:
| Sensor Pin | ESP32 Pin | Notes |
|------------|-----------|-------|
| VCC (+) | 3.3V or 5V | Check sensor specs |
| GND (-) | GND | Common ground |
| DO (Digital) | GPIO33 | HIGH or LOW output |

If using digital sensor, update firmware: `WATER_SENSOR_ANALOG = false`

---

### 4. TB6612FNG Motor Driver + Water Pump

```
TB6612FNG Motor Driver
┌──────────────────────────────────────┐
│  POWER INPUTS                         │
│  ┌────────────────┐                  │
│  │ VCC  VM   GND  │                  │
│  └──┬────┬────┬───┘                  │
│     │    │    │                      │
│     │    │    └─────→ GND (Common)   │
│     │    └──────────→ External 5V ⚠️ │
│     └───────────────→ ESP32 3.3V     │
│                                      │
│  CONTROL INPUTS                      │
│  ┌────────────────────────────────┐  │
│  │ STBY AIN1 AIN2 PWMA BIN1 ... │  │
│  └───┬────┬────┬────┬────────────┘  │
│      │    │    │    │               │
│      │    │    │    └──→ GPIO27 (ESP32)
│      │    │    └───────→ GPIO26 (ESP32)
│      │    └────────────→ GPIO25 (ESP32)
│      └─────────────────→ GPIO23 (ESP32) + 10kΩ pull-down!
│                                      │
│  MOTOR OUTPUTS                       │
│  ┌────────────────┐                  │
│  │ AO1  AO2  ...  │                  │
│  └──┬────┬────────┘                  │
│     │    │                           │
│     └────┴───────→ Water Pump (3-5V) │
│                                      │
└──────────────────────────────────────┘

CRITICAL: 10kΩ Resistor Configuration
        GPIO23 ────┬────→ STBY pin
                   │
                   └──── 10kΩ ────→ GND

This pull-down ensures STBY stays LOW during boot/reset!
```

**TB6612FNG Connection Table**:

| TB6612FNG Pin | Connect To | Notes |
|---------------|------------|-------|
| **POWER** | | |
| VCC | ESP32 3.3V | Logic power |
| VM | **External 5V supply** | Motor power (NOT from ESP32!) |
| GND | Common GND | Connect to ESP32 GND |
| **CONTROL** | | |
| STBY | GPIO23 + 10kΩ to GND | **Pull-down resistor required!** |
| AIN1 | GPIO25 | Motor A direction bit 1 |
| AIN2 | GPIO26 | Motor A direction bit 2 |
| PWMA | GPIO27 | Motor A speed (LEDC PWM) |
| BIN1 | (unused) | Optional: second motor |
| BIN2 | (unused) | Optional: second motor |
| PWMB | (unused) | Optional: second motor |
| **MOTOR OUTPUTS** | | |
| AO1 | Pump wire 1 | Motor A output |
| AO2 | Pump wire 2 | Motor A output |
| BO1 | (unused) | Motor B output |
| BO2 | (unused) | Motor B output |

---

## Power Supply Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    POWER DISTRIBUTION                     │
└──────────────────────────────────────────────────────────┘

USB 5V (from PC/Laptop)
    │
    ├───→ ESP32 (CH340 → 3.3V regulator)
    │         │
    │         ├───→ 3.3V pin ───┬───→ DHT11 VCC
    │         │                 ├───→ Soil Sensor VCC
    │         │                 ├───→ Water Sensor VCC
    │         │                 └───→ TB6612FNG VCC (logic)
    │         │
    │         └───→ GND pin ─────────→ Common GND
    │
    │
External 5V DC Supply (regulated)
    │
    ├───→ TB6612FNG VM (motor power)
    │         │
    │         └───→ Water Pump (via AO1, AO2)
    │
    └───→ GND ──────────────────────→ Common GND


⚠️ CRITICAL POWER SAFETY:
1. Common ground between all components
2. ESP32 powered from USB (or external 5V)
3. Motor driver VM from SEPARATE 5V supply
4. NEVER power pump from ESP32 3.3V or GPIO
5. Total ESP32 3.3V current limit: ~500mA
6. GPIO max current: 40mA (12mA recommended)
```

---

## Complete Wiring Checklist

### Before Connecting Power

- [ ] **Remove ALL ESP8266 wiring** (if previously connected)
- [ ] **Verify ESP32 board** (not ESP8266!)
- [ ] **Check USB cable** (data cable, not charge-only)

### Sensor Connections

- [ ] **DHT11**: VCC → 3.3V, DATA → GPIO18, GND → GND
- [ ] **Soil Moisture**: VCC → 3.3V, AO → GPIO34, GND → GND
- [ ] **Water Level**: VCC → 3.3V, AO → GPIO35 (or DO → GPIO33), GND → GND

### Motor Driver Connections

- [ ] **TB6612FNG VCC** → ESP32 3.3V
- [ ] **TB6612FNG GND** → Common GND
- [ ] **TB6612FNG VM** → External 5V supply (NOT ESP32!)
- [ ] **TB6612FNG STBY** → GPIO23
- [ ] **10kΩ resistor** from GPIO23 to GND (pull-down)
- [ ] **TB6612FNG AIN1** → GPIO25
- [ ] **TB6612FNG AIN2** → GPIO26
- [ ] **TB6612FNG PWMA** → GPIO27
- [ ] **TB6612FNG AO1, AO2** → Pump wires

### Safety Verification

- [ ] **No 5V connections** to ESP32 GPIO pins (only 3.3V sensors)
- [ ] **GPIO34, GPIO35** not used as outputs (input-only pins)
- [ ] **Common ground** established between all components
- [ ] **External 5V supply** connected to motor driver VM only
- [ ] **10kΩ pull-down** on STBY verified with multimeter
- [ ] **No short circuits** between VCC and GND
- [ ] **Pump polarity** correct (if pump has polarity)

---

## Multimeter Testing (Before Power-On)

### Continuity Tests

1. **Common Ground**:
   ```
   Multimeter: Continuity mode
   Test: ESP32 GND ←→ TB6612FNG GND
   Expected: Beep (short circuit = good)
   ```

2. **No VCC-to-GND Short**:
   ```
   Multimeter: Continuity mode
   Test: ESP32 3.3V ←→ ESP32 GND
   Expected: No beep (open circuit = good)
   ```

3. **STBY Pull-Down**:
   ```
   Multimeter: Resistance mode
   Test: GPIO23 ←→ GND
   Expected: ~10kΩ (pull-down resistor present)
   ```

### Voltage Tests (After Power-On, Before Sensors)

1. **ESP32 3.3V Rail**:
   ```
   Multimeter: DC Voltage mode
   Test: 3.3V pin to GND
   Expected: 3.2-3.4V
   ```

2. **TB6612FNG VM**:
   ```
   Multimeter: DC Voltage mode
   Test: VM pin to GND
   Expected: 4.8-5.2V (from external supply)
   ```

3. **STBY Pin State**:
   ```
   Multimeter: DC Voltage mode
   Test: STBY pin to GND
   Expected: ~0V (pulled down, driver disabled)
   ```

---

## Common Wiring Mistakes

### ❌ WRONG - Will Damage Hardware

1. **Powering pump from ESP32 3.3V**:
   ```
   ❌ Pump → ESP32 3.3V (WILL DAMAGE ESP32!)
   ✅ Pump → TB6612FNG AO1/AO2 (VM from external 5V)
   ```

2. **5V sensor to GPIO34/35**:
   ```
   ❌ 5V Sensor AO → GPIO34 (WILL DAMAGE ESP32!)
   ✅ Use voltage divider: 5V → [Resistors] → 3.3V → GPIO34
   ✅ Or use 3.3V sensor directly
   ```

3. **Missing STBY pull-down**:
   ```
   ❌ GPIO23 → STBY (no pull-down)
      Result: Pump may activate during boot!
   ✅ GPIO23 → STBY + 10kΩ resistor to GND
   ```

4. **GPIO34/35 as outputs**:
   ```
   ❌ pinMode(34, OUTPUT); digitalWrite(34, HIGH);
      Result: Won't work, GPIO34-39 are input-only!
   ✅ Use GPIO34/35 only for analogRead()
   ```

5. **Using ESP8266 pin numbers**:
   ```
   ❌ DHT11 → D2 (ESP8266 pin)
      Result: Wrong ESP32 pin, sensor won't work!
   ✅ DHT11 → GPIO18 (ESP32 pin)
   ```

---

## Pin State Reference

### ESP32 Pin Modes

| GPIO | Direction | Pull Resistor | Purpose | Notes |
|------|-----------|---------------|---------|-------|
| GPIO18 | I/O | Available | DHT11 DATA | General purpose |
| GPIO23 | Output | External pull-down | Motor STBY | 10kΩ to GND required |
| GPIO25 | Output | Available | Motor AIN1 | Direction control |
| GPIO26 | Output | Available | Motor AIN2 | Direction control |
| GPIO27 | Output | Available | Motor PWMA | LEDC PWM channel 0 |
| GPIO34 | **Input-only** | **None** | Soil Moisture | ADC1_CH6, 12-bit |
| GPIO35 | **Input-only** | **None** | Water Level | ADC1_CH7, 12-bit |
| GPIO33 | I/O | Available | Water Level (alt) | Digital sensor option |

### Boot Pin States

| GPIO | Boot State | Safe for Use? |
|------|------------|---------------|
| GPIO0 | Pull-up | ✅ Yes (after boot) |
| GPIO2 | Pull-down | ✅ Yes (after boot) |
| GPIO5 | Pull-up | ✅ Yes (after boot) |
| GPIO12 | Pull-down | ✅ Yes (after boot) |
| GPIO15 | Pull-up | ✅ Yes (after boot) |
| GPIO18 | Float | ✅ Yes (safe) |
| GPIO23 | Float | ✅ Yes (we add pull-down) |
| GPIO25 | Float | ✅ Yes (safe) |
| GPIO26 | Float | ✅ Yes (safe) |
| GPIO27 | Float | ✅ Yes (safe) |
| GPIO34-39 | Float | ✅ Yes (input-only) |

---

## Troubleshooting Wiring Issues

### Problem: Sensor Reads 0 or 4095 (Max)

**Possible Causes**:
1. Sensor VCC not connected
2. Wrong GPIO pin
3. Sensor output exceeds 3.3V
4. Loose connection

**Debug Steps**:
```
1. Measure sensor output with multimeter (should be 0-3.3V)
2. Verify GPIO pin number in firmware matches physical wiring
3. Check continuity between sensor output and ESP32 GPIO
4. Try different sensor or GPIO pin to isolate issue
```

### Problem: DHT11 Always Returns NaN

**Possible Causes**:
1. DATA pin not on GPIO18
2. Missing pull-up resistor (10kΩ)
3. Sensor not initialized (wait 2 seconds after boot)
4. Wrong sensor type (DHT22 instead of DHT11)

**Debug Steps**:
```
1. Verify DATA wire connected to GPIO18
2. Add 10kΩ pull-up resistor (DATA to VCC)
3. Check Serial Monitor for initialization messages
4. Verify it's DHT11 sensor (has grid holes, not DHT22)
```

### Problem: Pump Activates During Boot

**Possible Causes**:
1. Missing 10kΩ pull-down on STBY
2. Pull-down resistor value too high (>100kΩ)
3. STBY pin floating

**Debug Steps**:
```
1. Measure resistance between GPIO23 and GND (should be ~10kΩ)
2. Verify pull-down resistor soldered/connected properly
3. Check STBY voltage during boot (should be ~0V)
4. Use lower resistor value if needed (4.7kΩ - 10kΩ range)
```

### Problem: Motor Driver Gets Hot

**Possible Causes**:
1. VM voltage too high (>5.5V)
2. Pump draws too much current
3. Short circuit in motor wiring
4. Driver enabled during idle

**Debug Steps**:
```
1. Measure VM voltage (should be 4.8-5.2V)
2. Check pump current draw (should be <1A for typical 5V pump)
3. Verify no short between AO1 and AO2
4. Check Serial Monitor shows "STBY: LOW" during idle
```

---

## Wire Color Conventions

### Standard Wire Colors (Not Mandatory)

| Color | Typical Use | Our Application |
|-------|-------------|-----------------|
| **Red** | Power (+) | VCC, 3.3V, 5V |
| **Black** | Ground (-) | GND, Common Ground |
| **Yellow** | Signal/Data | DHT11 DATA, Sensor AO |
| **Green** | Signal/Analog | Alternative analog signal |
| **White** | Signal/Data | Alternative data signal |
| **Blue** | Digital I/O | Motor control signals |
| **Orange** | PWM/Analog | PWMA (motor speed) |

**Note**: Wire colors are conventions only. Use a labeling system if colors don't match!

---

## Component Datasheets Reference

### ESP32 DevKit
- **GPIO Voltage**: 3.3V (0V = LOW, 3.3V = HIGH)
- **ADC Input**: 0-3.3V (with 11dB attenuation)
- **GPIO Current**: 40mA max, 12mA recommended
- **3.3V Pin Current**: ~500mA total (depends on board regulator)

### DHT11
- **Supply Voltage**: 3.3-5V
- **Signal Voltage**: 3.3V (compatible with ESP32)
- **Current**: <1mA (idle), ~2.5mA (measuring)
- **Sampling**: Max 1Hz (once per second)

### TB6612FNG
- **VCC (Logic)**: 2.7-5.5V (3.3V from ESP32 OK)
- **VM (Motor)**: 4.5-13.5V (use 5V for 3-5V pump)
- **Output Current**: 1.2A per channel (3.2A peak)
- **Logic HIGH**: >2.0V (3.3V from ESP32 OK)
- **Logic LOW**: <0.8V

### Typical 3-5V Pump
- **Operating Voltage**: 3-5V DC
- **Current Draw**: 100-300mA (typical), up to 600mA (stall)
- **Flow Rate**: ~80-120 L/h (depends on model)

---

## Final Pre-Upload Checklist

### Physical Connections ✓

- [ ] All sensors connected to correct ESP32 GPIO pins
- [ ] TB6612FNG motor driver wired correctly
- [ ] 10kΩ pull-down resistor on STBY (GPIO23 to GND)
- [ ] External 5V supply connected to VM
- [ ] Common ground established between all components
- [ ] No 5V connections to ESP32 GPIO (only 3.3V sensors)
- [ ] USB cable connected (COM22)

### Multimeter Tests ✓

- [ ] ESP32 3.3V rail: 3.2-3.4V
- [ ] TB6612FNG VM: 4.8-5.2V
- [ ] No VCC-to-GND short circuits
- [ ] STBY pull-down resistance: ~10kΩ
- [ ] All sensor outputs: 0-3.3V range

### Software Ready ✓

- [ ] Arduino IDE installed with ESP32 support
- [ ] Required libraries installed (DHT, ArduinoJson)
- [ ] Firmware opened: FieldShift_ESP32_DevKit.ino
- [ ] config.h reviewed (SSID, password, API key)
- [ ] Board selected: "ESP32 Dev Module"
- [ ] Port selected: COM22
- [ ] Firmware compiled successfully (no errors)

### Backend/Network ✓

- [ ] Phone hotspot "Android 123" enabled
- [ ] Laptop connected to hotspot
- [ ] Laptop IP address noted (ipconfig)
- [ ] config.h API_SERVER updated to hotspot IP
- [ ] Backend running: python main.py
- [ ] Backend accessible: http://<laptop-ip>:8000

---

**READY TO UPLOAD**: If all checkboxes above are checked, you can proceed with firmware upload! ✅

**Wiring Diagram Version**: 1.0  
**Last Updated**: 2024-01-15  
**Hardware**: ESP32 DevKit with CH340
