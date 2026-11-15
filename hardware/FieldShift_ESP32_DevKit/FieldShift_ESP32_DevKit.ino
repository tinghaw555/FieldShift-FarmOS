/**
 * FieldShift FarmOS - ESP32 DevKit Firmware
 * 
 * Hardware: ESP32 DevKit (Dual-core Xtensa LX6, CH340 USB)
 * Sensors: DHT11, Analog Soil Moisture, Water Level (Analog/Digital)
 * Motor Driver: TB6612FNG
 * Pump: 3-5V DC submersible water pump
 * 
 * CRITICAL SAFETY NOTES:
 * - Pump control DISABLED by default until commissioned
 * - Pull-down resistor REQUIRED on TB6612FNG STBY pin
 * - Water level protection MUST be verified
 * - External regulated 5V supply for motor driver VM
 * - DO NOT power pump from ESP32 GPIO or 3.3V pin
 * 
 * Compatible with existing FieldShift FarmOS backend API
 * 
 * ESP32 ADVANTAGES OVER ESP8266:
 * - Dual-core CPU (240 MHz)
 * - More RAM (520 KB)
 * - Multiple ADC channels (18 total, 12-bit)
 * - Hardware PWM (LEDC)
 * - Bluetooth (not used in this firmware)
 * - 2.4GHz Wi-Fi (802.11 b/g/n)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ============================================================================
// CONFIGURATION - Edit config.h instead of this file
// ============================================================================
#include "config.h"

// ============================================================================
// PIN DEFINITIONS (ESP32 DevKit)
// ============================================================================
#define DHT_PIN 18          // GPIO18 - DHT11 DATA
#define SOIL_PIN 34         // GPIO34 (ADC1_CH6) - Soil Moisture Analog
#define WATER_PIN 35        // GPIO35 (ADC1_CH7) - Water Level Analog OR use GPIO33 for digital
#define MOTOR_AIN1 25       // GPIO25 - TB6612FNG AIN1
#define MOTOR_AIN2 26       // GPIO26 - TB6612FNG AIN2
#define MOTOR_PWMA 27       // GPIO27 - TB6612FNG PWMA (LEDC PWM)
#define MOTOR_STBY 23       // GPIO23 - TB6612FNG STBY (REQUIRES PULL-DOWN)

// PWM Configuration for ESP32 LEDC
#define PWM_CHANNEL 0       // LEDC channel 0
#define PWM_FREQ 5000       // 5 kHz PWM frequency
#define PWM_RESOLUTION 8    // 8-bit resolution (0-255)

// ADC Configuration for ESP32
#define ADC_RESOLUTION 12   // ESP32 has 12-bit ADC (0-4095)
#define ADC_MAX_VALUE 4095  // Maximum ADC reading

// Water level sensor type detection
// Set to true if using analog sensor, false if using digital sensor
#define WATER_SENSOR_ANALOG true  // Change to false if using digital DO sensor

// ============================================================================
// SENSOR INITIALIZATION
// ============================================================================
DHT dht(DHT_PIN, DHT11);  // DHT11 sensor (NOT DHT22!)

// ============================================================================
// GLOBAL STATE
// ============================================================================
WiFiClient wifiClient;
unsigned long lastTelemetryTime = 0;
unsigned long lastCommandPollTime = 0;
unsigned long lastWiFiCheck = 0;
bool pumpCommissioned = false;  // SAFETY: Must be manually enabled
bool pumpRunning = false;
unsigned long pumpStartTime = 0;
const unsigned long MAX_PUMP_RUNTIME = 300000; // 5 minutes max

// Current command being executed
struct ActiveCommand {
  String commandId = "";
  String action = "";
  int durationSeconds = 0;
  unsigned long startTime = 0;
  bool acknowledged = false;
} activeCommand;

// Pump safety interlocks
struct PumpSafety {
  bool waterLevelOK = false;
  bool commandActive = false;
  unsigned long commandExpiry = 0;
  bool faultDetected = false;
  String faultReason = "";
} pumpSafety;

// Sensor readings cache
struct SensorData {
  float temperature = NAN;
  float humidity = NAN;
  int soilMoistureRaw = 0;
  int waterLevelRaw = 0;
  bool waterLevelOK = false;
  bool waterLevelValid = false;
  bool dhtValid = false;
  unsigned long lastReadTime = 0;
} sensorData;

// ============================================================================
// SETUP
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(100);
  
  Serial.println();
  Serial.println("====================================");
  Serial.println("FieldShift FarmOS - ESP32 DevKit");
  Serial.println("ESP32 Dual-Core (Xtensa LX6)");
  Serial.println("====================================");
  
  // Configure ADC for ESP32
  configureADC();
  
  // Initialize pins SAFELY
  initializePinsSafe();
  
  // Initialize sensors
  Serial.println("Initializing DHT11 sensor...");
  dht.begin();
  delay(2000);  // DHT11 needs time to stabilize
  
  // Connect to Wi-Fi
  connectWiFi();
  
  Serial.println("Setup complete!");
  Serial.println();
  
  // Print pin configuration
  printPinConfiguration();
  
  // Print safety status
  printSafetyStatus();
}

// ============================================================================
// MAIN LOOP
// ============================================================================
void loop() {
  unsigned long currentTime = millis();
  
  // Check Wi-Fi connection every 30 seconds
  if (currentTime - lastWiFiCheck >= 30000) {
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Wi-Fi disconnected. Reconnecting...");
      pumpEmergencyStop("WiFi disconnected");
      connectWiFi();
    }
    lastWiFiCheck = currentTime;
  }
  
  // Read sensors
  readSensors();
  
  // Update pump safety interlocks
  updatePumpSafety();
  
  // Enforce pump safety (runs every loop)
  enforcePumpSafety();
  
  // Poll for pump commands
  if (currentTime - lastCommandPollTime >= COMMAND_POLL_INTERVAL_MS) {
    pollPumpCommands();
    lastCommandPollTime = currentTime;
  }
  
  // Execute active command (if any)
  executeActiveCommand();
  
  // Send telemetry at configured interval
  if (currentTime - lastTelemetryTime >= TELEMETRY_INTERVAL_MS) {
    sendTelemetry();
    sendPumpState();
    lastTelemetryTime = currentTime;
  }
  
  // Small delay to prevent watchdog issues
  delay(100);
}

// ============================================================================
// ADC CONFIGURATION - ESP32 SPECIFIC
// ============================================================================
void configureADC() {
  Serial.println("Configuring ESP32 ADC...");
  
  // Set ADC resolution to 12-bit (0-4095)
  analogReadResolution(ADC_RESOLUTION);
  
  // Set ADC attenuation for 0-3.3V range
  // ADC1 channels support WiFi, ADC2 channels do NOT work with WiFi!
  // Using ADC1_CH6 (GPIO34) and ADC1_CH7 (GPIO35)
  analogSetAttenuation(ADC_11db);  // 0-3.3V range (with some nonlinearity)
  
  Serial.println("  ADC Resolution: 12-bit (0-4095)");
  Serial.println("  ADC Attenuation: 11dB (0-3.3V range)");
  Serial.println("  Channels: ADC1_CH6 (GPIO34), ADC1_CH7 (GPIO35)");
  Serial.println("  ⚠️  Using ADC1 (ADC2 incompatible with WiFi)");
  Serial.println();
}

// ============================================================================
// PIN INITIALIZATION - SAFETY CRITICAL
// ============================================================================
void initializePinsSafe() {
  Serial.println("Initializing pins (SAFE MODE)...");
  
  // Configure sensor pins
  pinMode(SOIL_PIN, INPUT);
  pinMode(WATER_PIN, INPUT);
  
  // Configure motor driver pins - SAFE OUTPUTS FIRST
  pinMode(MOTOR_STBY, OUTPUT);
  digitalWrite(MOTOR_STBY, LOW);  // DISABLE driver first!
  
  pinMode(MOTOR_AIN1, OUTPUT);
  pinMode(MOTOR_AIN2, OUTPUT);
  pinMode(MOTOR_PWMA, OUTPUT);
  
  digitalWrite(MOTOR_AIN1, LOW);
  digitalWrite(MOTOR_AIN2, LOW);
  digitalWrite(MOTOR_PWMA, LOW);  // ESP32 GPIO low
  
  // Configure LEDC PWM for motor control
  ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(MOTOR_PWMA, PWM_CHANNEL);
  ledcWrite(PWM_CHANNEL, 0);  // PWM duty cycle 0
  
  Serial.println("  STBY: LOW (driver disabled)");
  Serial.println("  AIN1: LOW");
  Serial.println("  AIN2: LOW");
  Serial.println("  PWMA: 0 (LEDC PWM configured)");
  Serial.println("  Pump: DISABLED");
  
  // WARNING about pull-down resistor
  Serial.println();
  Serial.println("  ⚠️  CRITICAL: TB6612FNG STBY pin MUST have");
  Serial.println("      external ~10kΩ pull-down resistor!");
  Serial.println("      This prevents pump activation during boot/reset.");
  Serial.println();
}

// ============================================================================
// WI-FI CONNECTION
// ============================================================================
void connectWiFi() {
  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  Serial.println();
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Wi-Fi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    Serial.print("MAC Address: ");
    Serial.println(WiFi.macAddress());
  } else {
    Serial.println("Wi-Fi connection FAILED!");
    Serial.println("  - Check SSID and password in config.h");
    Serial.println("  - Ensure 2.4GHz network (ESP32 supports 2.4GHz only)");
    Serial.println("  - Check signal strength");
  }
  
  Serial.println();
}

// ============================================================================
// SENSOR READING
// ============================================================================
void readSensors() {
  unsigned long readStart = millis();
  
  // DHT11 - Temperature and Humidity
  // NOTE: DHT11 has ±2°C accuracy and ±5% humidity accuracy
  // Sampling rate: max once per 2 seconds
  if (millis() - sensorData.lastReadTime >= 2000) {
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    
    if (!isnan(temp) && !isnan(hum)) {
      // Validate ranges (DHT11 specs)
      if (temp >= 0 && temp <= 50 && hum >= 20 && hum <= 90) {
        sensorData.temperature = temp;
        sensorData.humidity = hum;
        sensorData.dhtValid = true;
      } else {
        Serial.println("DHT11 reading out of range!");
        sensorData.dhtValid = false;
      }
    } else {
      Serial.println("DHT11 read failed!");
      sensorData.dhtValid = false;
    }
    
    sensorData.lastReadTime = millis();
  }
  
  // Soil Moisture - Analog (ESP32 has multiple ADC channels!)
  // Raw ADC value: 0-4095 (ESP32 ADC is 12-bit)
  // Using GPIO34 (ADC1_CH6) - safe with WiFi
  int soilRaw = analogRead(SOIL_PIN);
  sensorData.soilMoistureRaw = soilRaw;
  
  // Water Level - Analog OR Digital depending on sensor type
  if (WATER_SENSOR_ANALOG) {
    // Analog water level sensor (0-4095)
    int waterRaw = analogRead(WATER_PIN);
    sensorData.waterLevelRaw = waterRaw;
    
    // Threshold for "OK" - adjust based on your sensor
    // Higher ADC value = more water (for typical analog sensors)
    const int WATER_OK_THRESHOLD = 2000;  // Adjust based on calibration
    sensorData.waterLevelOK = (waterRaw > WATER_OK_THRESHOLD);
    sensorData.waterLevelValid = true;
  } else {
    // Digital water level sensor (HIGH/LOW)
    // Configure as digital input if not already
    pinMode(WATER_PIN, INPUT);
    int waterDigital = digitalRead(WATER_PIN);
    
    // LOW = water OK, HIGH = water low (verify with YOUR sensor!)
    sensorData.waterLevelOK = (waterDigital == LOW);
    sensorData.waterLevelRaw = waterDigital ? 4095 : 0;  // Convert to ADC-like value
    sensorData.waterLevelValid = true;
  }
}

// ============================================================================
// PUMP SAFETY SYSTEM
// ============================================================================
void updatePumpSafety() {
  pumpSafety.waterLevelOK = sensorData.waterLevelOK && sensorData.waterLevelValid;
  
  // Check for fault conditions
  if (!pumpCommissioned) {
    pumpSafety.faultDetected = true;
    pumpSafety.faultReason = "Pump not commissioned";
  } else if (!pumpSafety.waterLevelOK) {
    pumpSafety.faultDetected = true;
    pumpSafety.faultReason = "Water level low or invalid";
  } else if (WiFi.status() != WL_CONNECTED) {
    pumpSafety.faultDetected = true;
    pumpSafety.faultReason = "WiFi disconnected";
  } else if (pumpRunning && (millis() - pumpStartTime) > MAX_PUMP_RUNTIME) {
    pumpSafety.faultDetected = true;
    pumpSafety.faultReason = "Maximum runtime exceeded";
  } else if (pumpSafety.commandActive && millis() > pumpSafety.commandExpiry) {
    pumpSafety.faultDetected = true;
    pumpSafety.faultReason = "Command expired";
  } else {
    pumpSafety.faultDetected = false;
    pumpSafety.faultReason = "";
  }
}

void enforcePumpSafety() {
  if (pumpSafety.faultDetected && pumpRunning) {
    pumpEmergencyStop(pumpSafety.faultReason);
  }
}

void pumpEmergencyStop(String reason) {
  Serial.println("🚨 PUMP EMERGENCY STOP!");
  Serial.print("   Reason: ");
  Serial.println(reason);
  
  pumpStop();
  pumpSafety.commandActive = false;
  pumpSafety.faultDetected = true;
  pumpSafety.faultReason = reason;
}

void pumpStop() {
  // TB6612FNG Motor Stop - Short Brake
  digitalWrite(MOTOR_AIN1, HIGH);
  digitalWrite(MOTOR_AIN2, HIGH);
  ledcWrite(PWM_CHANNEL, 0);  // PWM off
  
  // Disable driver
  digitalWrite(MOTOR_STBY, LOW);
  
  pumpRunning = false;
  
  Serial.println("Pump STOPPED");
}

// PUMP START - Only call after ALL safety checks pass!
void pumpStart() {
  if (!pumpCommissioned) {
    Serial.println("❌ Pump start DENIED: Not commissioned!");
    return;
  }
  
  if (pumpSafety.faultDetected) {
    Serial.println("❌ Pump start DENIED: Safety fault detected!");
    Serial.print("   Reason: ");
    Serial.println(pumpSafety.faultReason);
    return;
  }
  
  Serial.println("✅ Starting pump (commissioning mode)...");
  
  // Enable TB6612FNG driver
  digitalWrite(MOTOR_STBY, HIGH);
  
  // Motor forward (CW)
  digitalWrite(MOTOR_AIN1, HIGH);
  digitalWrite(MOTOR_AIN2, LOW);
  ledcWrite(PWM_CHANNEL, 255);  // Full speed (8-bit: 0-255)
  
  pumpRunning = true;
  pumpStartTime = millis();
  
  Serial.println("Pump RUNNING");
}

// ============================================================================
// TELEMETRY TRANSMISSION
// ============================================================================
void sendTelemetry() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Cannot send telemetry: WiFi not connected");
    return;
  }
  
  Serial.println("-----------------------------------");
  Serial.println("Sending telemetry...");
  
  // Create JSON payload
  StaticJsonDocument<512> doc;
  doc["farm_id"] = FARM_ID;
  doc["timestamp"] = getISOTimestamp();
  
  // Add sensor readings
  if (sensorData.dhtValid) {
    doc["temperature"] = sensorData.temperature;
    doc["humidity"] = sensorData.humidity;
  }
  
  // Soil moisture - send RAW 12-bit value (0-4095)
  // Backend can calibrate or convert to percentage
  doc["soil_moisture"] = sensorData.soilMoistureRaw;
  
  // Water level - send RAW value or percentage
  if (WATER_SENSOR_ANALOG) {
    // Convert 12-bit ADC to percentage (0-100%)
    int waterPercent = map(sensorData.waterLevelRaw, 0, 4095, 0, 100);
    doc["water_level"] = waterPercent;
  } else {
    // Digital sensor: 0% (low) or 100% (OK)
    doc["water_level"] = sensorData.waterLevelOK ? 100 : 0;
  }
  
  doc["firmware_version"] = FIRMWARE_VERSION;
  doc["ip_address"] = WiFi.localIP().toString();
  
  // Serialize JSON
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  Serial.println("Payload:");
  Serial.println(jsonPayload);
  
  // Send HTTP POST
  HTTPClient http;
  
  String url = String("http://") + API_SERVER + ":" + String(API_PORT) + "/api/hardware/telemetry";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-ID", DEVICE_ID);
  http.addHeader("X-API-Key", API_KEY);
  
  int httpCode = http.POST(jsonPayload);
  
  if (httpCode > 0) {
    Serial.print("HTTP Response: ");
    Serial.println(httpCode);
    
    if (httpCode == 200) {
      String response = http.getString();
      Serial.println("Response:");
      Serial.println(response);
      Serial.println("✅ Telemetry sent successfully!");
    } else {
      Serial.println("❌ Telemetry rejected by server");
    }
  } else {
    Serial.print("❌ HTTP Error: ");
    Serial.println(http.errorToString(httpCode));
  }
  
  http.end();
  Serial.println("-----------------------------------");
  Serial.println();
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================
String getISOTimestamp() {
  // Simple timestamp (actual implementation would use NTP)
  unsigned long seconds = millis() / 1000;
  char buffer[32];
  sprintf(buffer, "2024-01-01T%02d:%02d:%02dZ", 
          (int)((seconds / 3600) % 24),
          (int)((seconds / 60) % 60),
          (int)(seconds % 60));
  return String(buffer);
}

void printPinConfiguration() {
  Serial.println("====================================");
  Serial.println("PIN CONFIGURATION (ESP32)");
  Serial.println("====================================");
  Serial.println("DHT11 DATA:       GPIO18");
  Serial.println("Soil Moisture:    GPIO34 (ADC1_CH6) - 12-bit ADC");
  
  if (WATER_SENSOR_ANALOG) {
    Serial.println("Water Level:      GPIO35 (ADC1_CH7) - Analog");
  } else {
    Serial.println("Water Level:      GPIO33 - Digital");
  }
  
  Serial.println("TB6612FNG AIN1:   GPIO25");
  Serial.println("TB6612FNG AIN2:   GPIO26");
  Serial.println("TB6612FNG PWMA:   GPIO27 (LEDC PWM)");
  Serial.println("TB6612FNG STBY:   GPIO23 ⚠️  NEEDS 10kΩ PULL-DOWN!");
  Serial.println();
  Serial.println("⚠️  ESP32 NOTE: GPIO34-39 are INPUT ONLY!");
  Serial.println("   (No internal pull-up/pull-down)");
  Serial.println("====================================");
  Serial.println();
}

void printSafetyStatus() {
  Serial.println("====================================");
  Serial.println("SAFETY STATUS");
  Serial.println("====================================");
  Serial.print("Pump Commissioned:  ");
  Serial.println(pumpCommissioned ? "YES (ENABLED)" : "NO (DISABLED)");
  Serial.print("Water Level Valid:  ");
  Serial.println(sensorData.waterLevelValid ? "YES" : "NO");
  Serial.print("Water Level OK:     ");
  Serial.println(sensorData.waterLevelOK ? "YES" : "NO");
  Serial.print("WiFi Connected:     ");
  Serial.println(WiFi.status() == WL_CONNECTED ? "YES" : "NO");
  Serial.println();
  Serial.println("⚠️  CRITICAL SAFETY NOTES:");
  Serial.println("  - Pump is DISABLED by default");
  Serial.println("  - Set pumpCommissioned=true ONLY after:");
  Serial.println("    1. Verifying all wiring");
  Serial.println("    2. Testing pump manually");
  Serial.println("    3. Confirming water level protection");
  Serial.println("    4. Testing emergency stop");
  Serial.println("  - NEVER power pump from ESP32 3.3V!");
  Serial.println("  - Use external regulated 5V for TB6612FNG VM");
  Serial.println("====================================");
  Serial.println();
}

// ============================================================================
// PUMP COMMAND POLLING & EXECUTION
// ============================================================================
void pollPumpCommands() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  // Don't poll if already executing a command
  if (activeCommand.commandId != "" && !activeCommand.acknowledged) {
    return;
  }
  
  HTTPClient http;
  
  String url = String("http://") + API_SERVER + ":" + String(API_PORT) + 
               "/api/hardware/pump/commands/" + DEVICE_ID + "/pending";
  
  http.begin(url);
  http.addHeader("X-API-Key", API_KEY);
  
  int httpCode = http.GET();
  
  if (httpCode == 200) {
    String response = http.getString();
    
    // Parse JSON response
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, response);
    
    if (!error && doc.containsKey("command") && !doc["command"].isNull()) {
      JsonObject cmd = doc["command"];
      
      String commandId = cmd["command_id"].as<String>();
      String action = cmd["action"].as<String>();
      int duration = cmd["duration_seconds"] | 10;
      
      // New command received
      Serial.println("-----------------------------------");
      Serial.println("📩 New pump command received!");
      Serial.print("   Command ID: ");
      Serial.println(commandId);
      Serial.print("   Action: ");
      Serial.println(action);
      Serial.print("   Duration: ");
      Serial.print(duration);
      Serial.println(" seconds");
      Serial.println("-----------------------------------");
      
      // Store active command
      activeCommand.commandId = commandId;
      activeCommand.action = action;
      activeCommand.durationSeconds = duration;
      activeCommand.startTime = 0;
      activeCommand.acknowledged = false;
      
      // Acknowledge receipt
      acknowledgeCommand(commandId, "acknowledged", "", "");
    }
  }
  
  http.end();
}

void executeActiveCommand() {
  if (activeCommand.commandId == "") {
    return;
  }
  
  if (!activeCommand.acknowledged) {
    activeCommand.acknowledged = true;
    activeCommand.startTime = millis();
    
    if (activeCommand.action == "start") {
      pumpSafety.commandActive = true;
      pumpSafety.commandExpiry = millis() + (activeCommand.durationSeconds * 1000);
      
      if (pumpCommissioned && !pumpSafety.faultDetected) {
        pumpStart();
        Serial.println("✅ Pump START command executed");
      } else {
        String errorMsg = pumpCommissioned ? pumpSafety.faultReason : "Pump not commissioned";
        Serial.print("❌ Pump START denied: ");
        Serial.println(errorMsg);
        
        acknowledgeCommand(activeCommand.commandId, "failed", "", errorMsg);
        activeCommand.commandId = "";
        pumpSafety.commandActive = false;
        return;
      }
      
    } else if (activeCommand.action == "stop") {
      pumpStop();
      pumpSafety.commandActive = false;
      
      acknowledgeCommand(activeCommand.commandId, "completed", "Pump stopped", "");
      activeCommand.commandId = "";
      
      Serial.println("✅ Pump STOP command executed");
      return;
    }
  }
  
  if (activeCommand.action == "start" && pumpRunning) {
    unsigned long elapsed = (millis() - activeCommand.startTime) / 1000;
    
    if (elapsed >= activeCommand.durationSeconds) {
      pumpStop();
      pumpSafety.commandActive = false;
      
      String result = String("Pump ran for ") + elapsed + " seconds";
      acknowledgeCommand(activeCommand.commandId, "completed", result, "");
      activeCommand.commandId = "";
      
      Serial.println("✅ Pump duration completed, stopped automatically");
    }
  }
}

void acknowledgeCommand(String commandId, String status, String result, String errorMsg) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Cannot acknowledge command: WiFi not connected");
    return;
  }
  
  HTTPClient http;
  
  String url = String("http://") + API_SERVER + ":" + String(API_PORT) + 
               "/api/hardware/pump/commands/acknowledge";
  
  StaticJsonDocument<256> doc;
  doc["command_id"] = commandId;
  doc["status"] = status;
  if (result != "") doc["result"] = result;
  if (errorMsg != "") doc["error_message"] = errorMsg;
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-ID", DEVICE_ID);
  http.addHeader("X-API-Key", API_KEY);
  
  int httpCode = http.POST(jsonPayload);
  
  if (httpCode == 200) {
    Serial.print("✅ Command acknowledgement sent: ");
    Serial.println(status);
  } else {
    Serial.print("❌ Failed to acknowledge command: ");
    Serial.println(httpCode);
  }
  
  http.end();
}

void sendPumpState() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  StaticJsonDocument<512> doc;
  doc["device_id"] = DEVICE_ID;
  doc["pump_running"] = pumpRunning;
  doc["commissioned"] = pumpCommissioned;
  doc["fault_detected"] = pumpSafety.faultDetected;
  
  if (pumpSafety.faultDetected) {
    doc["fault_reason"] = pumpSafety.faultReason;
  }
  
  doc["water_level_ok"] = sensorData.waterLevelOK;
  
  if (pumpRunning) {
    doc["runtime_seconds"] = (millis() - pumpStartTime) / 1000;
  }
  
  if (activeCommand.commandId != "") {
    doc["current_command_id"] = activeCommand.commandId;
  }
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  HTTPClient http;
  
  String url = String("http://") + API_SERVER + ":" + String(API_PORT) + "/api/hardware/pump/state";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-ID", DEVICE_ID);
  http.addHeader("X-API-Key", API_KEY);
  
  int httpCode = http.POST(jsonPayload);
  
  if (httpCode == 200) {
    Serial.println("✅ Pump state sent");
  } else {
    Serial.print("❌ Failed to send pump state: ");
    Serial.println(httpCode);
  }
  
  http.end();
}
