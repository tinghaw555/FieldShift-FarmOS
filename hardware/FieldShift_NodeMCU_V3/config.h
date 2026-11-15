/**
 * FieldShift FarmOS - NodeMCU V3 Configuration
 * 
 * IMPORTANT: Copy this file to config.h and edit with your settings
 * DO NOT commit config.h to version control (contains secrets)
 */

#ifndef CONFIG_H
#define CONFIG_H

// ============================================================================
// WI-FI CONFIGURATION
// ============================================================================
// CRITICAL: ESP8266 supports ONLY 2.4GHz networks (NOT 5GHz!)
const char* WIFI_SSID = "Android 123";
const char* WIFI_PASSWORD = "udgt3699";

// ============================================================================
// FIELDSHIFT API CONFIGURATION
// ============================================================================
// Use your laptop's LAN IP address (NOT localhost or 127.0.0.1)
// Find with: ipconfig (Windows) or ifconfig (Linux/Mac)
const char* API_SERVER = "10.22.217.151";  // Change to your server IP!
const int API_PORT = 8000;

// Device credentials (obtain from device registration)
const char* DEVICE_ID = "NODEMCU_V3_ESP8266_001";
const char* API_KEY = "qwXg3afBBI7c6XVhyqf1XPiSNdqjLDsUTqGRz_h1a1g";  // Get from registration response
const int FARM_ID = 1;

// ============================================================================
// FIRMWARE CONFIGURATION
// ============================================================================
const char* FIRMWARE_VERSION = "2.0.0-NodeMCU-V3-PumpControl";

// Telemetry interval (milliseconds)
#define TELEMETRY_INTERVAL_MS 60000  // 60 seconds

// Command polling interval (milliseconds)
#define COMMAND_POLL_INTERVAL_MS 5000  // 5 seconds

// ============================================================================
// SENSOR CALIBRATION (Optional)
// ============================================================================
// Soil Moisture ADC Calibration
// Measure with sensor in air (dry) and in water (wet)
#define SOIL_DRY_VALUE 1023   // ADC value in air (dry)
#define SOIL_WET_VALUE 300    // ADC value in water (wet)

// Water Level Sensor Type
// true = LOW when water OK, HIGH when low
// false = HIGH when water OK, LOW when low
#define WATER_LEVEL_ACTIVE_LOW true

// ============================================================================
// HARDWARE NOTES
// ============================================================================
/**
 * NodeMCU V3 (ESP8266) Specifications:
 * - CPU: ESP8266 (80 MHz / 160 MHz)
 * - RAM: 80 KB user available
 * - Flash: 4 MB (typical)
 * - Wi-Fi: 2.4 GHz ONLY (802.11 b/g/n)
 * - GPIO: 11 usable pins (some have boot restrictions)
 * - Analog Input: ONE only (A0, 0-1.0V, 10-bit ADC)
 * - PWM: Software PWM on most GPIO pins
 * - Operating Voltage: 3.3V (5V tolerant on some pins, check datasheet!)
 * 
 * CRITICAL ESP8266 BOOT BEHAVIOR:
 * - GPIO15 (D8): MUST be LOW during boot
 * - GPIO0 (D3): MUST be HIGH during boot (LOW = flash mode)
 * - GPIO2 (D4): MUST be HIGH during boot
 * - GPIO16 (D0): Connected to RST for deep sleep wake
 * 
 * Pin D0 (GPIO16) used for STBY has special behavior:
 * - Does NOT have internal pull-up/pull-down
 * - EXTERNAL pull-down resistor REQUIRED (~10kΩ)
 * - This prevents pump activation during boot/reset
 * 
 * A0 Analog Input Voltage Range:
 * - Most NodeMCU V3 boards: 0-3.2V input → 0-1.0V ADC
 * - Built-in voltage divider (220kΩ + 100kΩ)
 * - ADC reads 0-1023 (10-bit)
 * - VERIFY your board's actual range before connecting sensors!
 * 
 * TB6612FNG Motor Driver Connections:
 * - VCC → NodeMCU 3.3V
 * - GND → Common ground
 * - VM → External regulated 5V DC supply (for pump)
 * - AO1, AO2 → 3-5V DC pump
 * - STBY → D0 (GPIO16) + 10kΩ pull-down to GND
 * - AIN1 → D5 (GPIO14)
 * - AIN2 → D7 (GPIO13)
 * - PWMA → D1 (GPIO5)
 * 
 * NEVER:
 * - Power pump from NodeMCU GPIO or 3.3V pin
 * - Connect >3.3V to GPIO inputs (except 5V-tolerant pins)
 * - Draw >12mA from any single GPIO
 * - Use A0 for multiple sensors (only ONE analog input!)
 */

#endif // CONFIG_H
