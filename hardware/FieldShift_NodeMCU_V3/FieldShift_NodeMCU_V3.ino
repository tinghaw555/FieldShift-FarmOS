/**
 * FieldShift FarmOS - NodeMCU V3 (ESP8266) Firmware
 * 
 * Hardware: LOLIN NodeMCU V3 (ESP8266 ESP-12E/ESP-12F)
 * Sensors: DHT11, Analog Soil Moisture, Water Level (Digital)
 * Motor Driver: TB6612FNG
 * Pump: 3-5V DC submersible water pump
 * 
 * CRITICAL SAFETY NOTES:
 * - Pump control DISABLED by default until commissioned
 * - Pull-down resistor REQUIRED on TB6612FNG STBY pin
 * - Water level protection MUST be verified
 * - External regulated 5V supply for motor driver VM
 * - DO NOT power pump from NodeMCU GPIO or 3.3V pin
 * 
 * Compatible with existing FieldShift FarmOS backend API
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ============================================================================
// CONFIGURATION - Edit config.h instead of this file
// ============================================================================
#include "config.h"

// ============================================================================
// PIN DEFINITIONS (NodeMCU V3 / ESP8266)
// ============================================================================
#define DHT_PIN D2          // GPIO4  - DHT11 DATA
#define SOIL_PIN A0         // ADC0   - Soil Moisture Analog (ONLY analog input!)
#define WATER_PIN D6        // GPIO12 - Water Level Digital (DO)
#define MOTOR_AIN1 D5       // GPIO14 - TB6612FNG AIN1
#define MOTOR_AIN2 D7       // GPIO13 - TB6612FNG AIN2
#define MOTOR_PWMA D1       // GPIO5  - TB6612FNG PWMA
#define MOTOR_STBY D0       // GPIO16 - TB6612FNG STBY (REQUIRES PULL-DOWN)

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
  Serial.println("FieldShift FarmOS - NodeMCU V3");
  Serial.println("LOLIN NodeMCU V3 (ESP8266)");
  Serial.println("====================================");
  
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
  analogWrite(MOTOR_PWMA, 0);
  
  Serial.println("  STBY: LOW (driver disabled)");
  Serial.println("  AIN1: LOW");
  Serial.println("  AIN2: LOW");
  Serial.println("  PWMA: 0");
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
  } else {
    Serial.println("Wi-Fi connection FAILED!");
    Serial.println("  - Check SSID and password in config.h");
    Serial.println("  - Ensure 2.4GHz network (ESP8266 does NOT support 5GHz)");
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
  
  // Soil Moisture - Analog (A0 is ONLY analog input on ESP8266!)
  // Raw ADC value: 0-1023 (ESP8266 ADC is 10-bit)
  // CRITICAL: Verify your NodeMCU A0 input voltage range!
  // Most NodeMCU V3 have voltage divider: 0-3.2V → 0-1.0V ADC input
  int soilRaw = analogRead(SOIL_PIN);
  sensorData.soilMoistureRaw = soilRaw;
  
  // Water Level - Digital (assuming switch-type sensor)
  // LOW = water OK, HIGH = water low (depends on sensor type!)
  // CRITICAL: Verify with YOUR actual sensor!
  int waterDigital = digitalRead(WATER_PIN);
  sensorData.waterLevelOK = (waterDigital == LOW);  // Adjust based on sensor
  sensorData.waterLevelValid = true;
  
  // If water level sensor is analog type, display ERROR
  // ESP8266 has ONLY ONE analog input - cannot read both soil and water analog!
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
  analogWrite(MOTOR_PWMA, 0);
  
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
  analogWrite(MOTOR_PWMA, 255);  // Full speed (adjust if needed)
  
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
  
  // Soil moisture - send RAW value (let backend calibrate)
  doc["soil_moisture"] = sensorData.soilMoistureRaw;
  
  // Water level - convert boolean to percentage representation
  // (backend expects 0-100%, but we only have binary sensor)
  doc["water_level"] = sensorData.waterLevelOK ? 100 : 0;
  
  doc["firmware_version"] = FIRMWARE_VERSION;
  doc["ip_address"] = WiFi.localIP().toString();
  
  // Serialize JSON
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  Serial.println("Payload:");
  Serial.println(jsonPayload);
  
  // Send HTTP POST
  HTTPClient http;
  WiFiClient client;
  
  String url = String("http://") + API_SERVER + ":" + String(API_PORT) + "/api/hardware/telemetry";
  
  http.begin(client, url);
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
  Serial.println("PIN CONFIGURATION");
  Serial.println("====================================");
  Serial.println("DHT11 DATA:       D2  (GPIO4)");
  Serial.println("Soil Moisture:    A0  (ADC0) - ONLY analog input!");
  Serial.println("Water Level:      D6  (GPIO12) - Digital");
  Serial.println("TB6612FNG AIN1:   D5  (GPIO14)");
  Serial.println("TB6612FNG AIN2:   D7  (GPIO13)");
  Serial.println("TB6612FNG PWMA:   D1  (GPIO5)");
  Serial.println("TB6612FNG STBY:   D0  (GPIO16) ⚠️  NEEDS PULL-DOWN!");
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
  Serial.println("  - NEVER power pump from NodeMCU 3.3V!");
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
  WiFiClient client;
  
  String url = String("http://") + API_SERVER + ":" + String(API_PORT) + 
               "/api/hardware/pump/commands/" + DEVICE_ID + "/pending";
  
  http.begin(client, url);
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
      activeCommand.startTime = 0;  // Will be set when execution starts
      activeCommand.acknowledged = false;
      
      // Acknowledge receipt
      acknowledgeCommand(commandId, "acknowledged", "", "");
    }
  }
  
  http.end();
}

void executeActiveCommand() {
  if (activeCommand.commandId == "") {
    return;  // No active command
  }
  
  // Check if command has been acknowledged
  if (!activeCommand.acknowledged) {
    activeCommand.acknowledged = true;
    activeCommand.startTime = millis();
    
    if (activeCommand.action == "start") {
      // Execute START command
      pumpSafety.commandActive = true;
      pumpSafety.commandExpiry = millis() + (activeCommand.durationSeconds * 1000);
      
      if (pumpCommissioned && !pumpSafety.faultDetected) {
        pumpStart();
        
        Serial.println("✅ Pump START command executed");
      } else {
        // Cannot start - safety violation
        String errorMsg = pumpCommissioned ? pumpSafety.faultReason : "Pump not commissioned";
        Serial.print("❌ Pump START denied: ");
        Serial.println(errorMsg);
        
        acknowledgeCommand(activeCommand.commandId, "failed", "", errorMsg);
        activeCommand.commandId = "";  // Clear command
        pumpSafety.commandActive = false;
        return;
      }
      
    } else if (activeCommand.action == "stop") {
      // Execute STOP command
      pumpStop();
      pumpSafety.commandActive = false;
      
      acknowledgeCommand(activeCommand.commandId, "completed", "Pump stopped", "");
      activeCommand.commandId = "";  // Clear command
      
      Serial.println("✅ Pump STOP command executed");
      return;
    }
  }
  
  // Check if START command duration expired
  if (activeCommand.action == "start" && pumpRunning) {
    unsigned long elapsed = (millis() - activeCommand.startTime) / 1000;
    
    if (elapsed >= activeCommand.durationSeconds) {
      // Duration completed
      pumpStop();
      pumpSafety.commandActive = false;
      
      String result = String("Pump ran for ") + elapsed + " seconds";
      acknowledgeCommand(activeCommand.commandId, "completed", result, "");
      activeCommand.commandId = "";  // Clear command
      
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
  WiFiClient client;
  
  String url = String("http://") + API_SERVER + ":" + String(API_PORT) + 
               "/api/hardware/pump/commands/acknowledge";
  
  // Create JSON payload
  StaticJsonDocument<256> doc;
  doc["command_id"] = commandId;
  doc["status"] = status;
  if (result != "") doc["result"] = result;
  if (errorMsg != "") doc["error_message"] = errorMsg;
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  http.begin(client, url);
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
  
  // Create JSON payload
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
  
  // Send HTTP POST
  HTTPClient http;
  WiFiClient client;
  
  String url = String("http://") + API_SERVER + ":" + String(API_PORT) + "/api/hardware/pump/state";
  
  http.begin(client, url);
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
