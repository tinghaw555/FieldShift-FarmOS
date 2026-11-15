/**
 * FieldShift FarmOS - ESP32 DevKit Configuration
 * 
 * IMPORTANT: This file contains sensitive credentials
 * DO NOT commit config.h to version control (contains secrets)
 */

#ifndef CONFIG_H
#define CONFIG_H

// ============================================================================
// WI-FI CONFIGURATION
// ============================================================================
// CRITICAL: ESP32 supports 2.4GHz networks (NOT 5GHz!)
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// ============================================================================
// FIELDSHIFT API CONFIGURATION
// ============================================================================
// Use your laptop's LAN IP address (NOT localhost or 127.0.0.1)
// Find with: ipconfig (Windows) or ifconfig (Linux/Mac)
const char* API_SERVER = "192.168.1.100";  // Update to your server IP
const int API_PORT = 8000;

// Device credentials (obtained from device registration)
const char* DEVICE_ID = "YOUR_DEVICE_ID";
const char* API_KEY = "YOUR_API_KEY_HERE";
const int FARM_ID = 1;

// ============================================================================
// FIRMWARE CONFIGURATION
// ============================================================================
const char* FIRMWARE_VERSION = "2.0.0-ESP32-DevKit-PumpControl";

// Telemetry interval (milliseconds)
#define TELEMETRY_INTERVAL_MS 60000  // 60 seconds

// Command polling interval (milliseconds)
#define COMMAND_POLL_INTERVAL_MS 5000  // 5 seconds

// ============================================================================
// SENSOR CALIBRATION (Optional)
// ============================================================================
// Soil Moisture ADC Calibration (ESP32 12-bit: 0-4095)
// Measure with sensor in air (dry) and in water (wet)
#define SOIL_DRY_VALUE 4095   // ADC value in air (dry)
#define SOIL_WET_VALUE 1500   // ADC value in water (wet)

// Water Level Sensor Configuration
// If using ANALOG water level sensor (GPIO35/ADC1_CH7):
//   - Set WATER_SENSOR_ANALOG to true in .ino file
//   - Adjust WATER_OK_THRESHOLD based on calibration
//   - Higher ADC value typically = more water
// If using DIGITAL water level sensor (GPIO33):
//   - Set WATER_SENSOR_ANALOG to false in .ino file
//   - Connect DO pin to GPIO33
//   - Adjust logic (LOW=OK vs HIGH=OK) based on sensor

// ============================================================================
// HARDWARE NOTES - ESP32 DEVKIT
// ============================================================================
/**
 * ESP32 DevKit Specifications:
 * - CPU: Dual-core Xtensa LX6 (up to 240 MHz)
 * - RAM: 520 KB SRAM
 * - Flash: 4 MB (typical)
 * - Wi-Fi: 2.4 GHz (802.11 b/g/n)
 * - Bluetooth: Classic + BLE (not used in this firmware)
 * - GPIO: 34 total pins (some reserved)
 * - Analog Input: 18 channels (12-bit ADC, 0-4095)
 * - PWM: 16 channels (LEDC, hardware PWM)
 * - Operating Voltage: 3.3V (5V tolerant on some pins)
 * - USB: CH340 USB-to-Serial (most DevKit boards)
 * 
 * CRITICAL ESP32 PIN CHARACTERISTICS:
 * 
 * INPUT-ONLY PINS (Cannot be outputs):
 * - GPIO34, GPIO35, GPIO36, GPIO39 (VP)
 * - These pins have NO internal pull-up/pull-down resistors
 * - Use external pull resistors if needed for digital inputs
 * - Perfect for analog sensors (ADC1_CH6, ADC1_CH7)
 * 
 * ADC1 vs ADC2:
 * - ADC1: GPIO32-39 (8 channels) - Works WITH WiFi ✅
 * - ADC2: GPIO0, 2, 4, 12-15, 25-27 - Does NOT work with WiFi ❌
 * - ALWAYS use ADC1 channels for sensors when WiFi is active!
 * 
 * BOOT BEHAVIOR:
 * - GPIO0: Boot mode selection (must be HIGH for normal boot)
 * - GPIO2: Boot fails if pulled LOW
 * - GPIO12: Boot voltage selection (default LOW)
 * - GPIO15: Boot fails if pulled HIGH
 * - Avoid using these pins for critical outputs at boot
 * 
 * STRAPPING PINS (have internal pull-up/pull-down at boot):
 * - GPIO0, GPIO2, GPIO5, GPIO12, GPIO15
 * - Safe to use after boot, but consider boot state
 * 
 * PWM (LEDC):
 * - 16 independent PWM channels
 * - Configurable frequency and duty cycle
 * - Up to 20-bit resolution (practical: 8-16 bit)
 * - Used for TB6612FNG PWMA motor speed control
 * 
 * Pin Map for FieldShift FarmOS:
 * 
 * SENSORS:
 * - DHT11 DATA → GPIO18 (general purpose I/O)
 * - Soil Moisture → GPIO34 (ADC1_CH6, input-only)
 * - Water Level → GPIO35 (ADC1_CH7, input-only, analog)
 *              OR GPIO33 (general I/O, if digital sensor)
 * 
 * TB6612FNG MOTOR DRIVER:
 * - STBY → GPIO23 + 10kΩ pull-down to GND (CRITICAL!)
 * - AIN1 → GPIO25
 * - AIN2 → GPIO26
 * - PWMA → GPIO27 (LEDC channel 0)
 * - VCC → ESP32 3.3V
 * - GND → Common ground
 * - VM → External 5V DC supply (for pump)
 * - AO1, AO2 → 3-5V DC pump
 * 
 * POWER SUPPLY:
 * - ESP32: USB 5V or external 5V (regulated to 3.3V on board)
 * - Sensors: 3.3V from ESP32 (DHT11 can use 3.3V or 5V)
 * - Motor Driver VM: External 5V supply (NOT from ESP32!)
 * - Pump: Powered from TB6612FNG VM (external 5V)
 * 
 * CURRENT LIMITS:
 * - ESP32 GPIO: Max 40mA per pin (12mA recommended)
 * - ESP32 3.3V pin: Max ~500mA total (depends on regulator)
 * - NEVER power pump from ESP32 GPIO or 3.3V rail!
 * 
 * WIRING SAFETY:
 * - 10kΩ pull-down resistor on STBY (GPIO23 to GND)
 * - External 5V supply for TB6612FNG VM
 * - Separate ground connections to common GND
 * - Check voltage levels before connecting sensors
 * - GPIO34-39 are 3.3V max input (no overvoltage protection)
 * 
 * DIFFERENCES FROM ESP8266/NODEMCU V3:
 * - ESP32 has TWO cores (ESP8266 has one)
 * - ESP32 ADC is 12-bit 0-4095 (ESP8266 is 10-bit 0-1023)
 * - ESP32 has 18 ADC channels (ESP8266 has 1!)
 * - ESP32 uses LEDC for PWM (ESP8266 uses analogWrite)
 * - ESP32 GPIO numbers are direct (no D0/D1/D2 aliases)
 * - ESP32 has more RAM (520KB vs 80KB)
 * - ESP32 ADC1 safe with WiFi (ESP8266 ADC conflicts)
 * 
 * MIGRATION FROM ESP8266:
 * - Replace ESP8266WiFi.h → WiFi.h
 * - Replace ESP8266HTTPClient.h → HTTPClient.h
 * - Replace analogWrite() → ledcWrite()
 * - Update pin numbers (D0/D1 → GPIO23/GPIO25)
 * - Update ADC max from 1023 → 4095
 * - Use ADC1 channels only (GPIO32-39)
 * - Configure LEDC for PWM before use
 */

#endif // CONFIG_H
