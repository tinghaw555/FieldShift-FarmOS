#!/usr/bin/env python3
"""
Device Registration Script for FieldShift FarmOS
Registers NodeMCU V3 and stores credentials securely in config.h
"""

import requests
import sys
import os
import re

# Configuration
API_BASE = "http://localhost:8000/api"
DEVICE_ID = "NODEMCU_V3_ESP8266_001"
DEVICE_TYPE = "NodeMCU-V3-ESP8266"
FARM_ID = 1  # Using first available farm

CONFIG_FILE = "FieldShift_NodeMCU_V3/config.h"

def register_device():
    """Register device with backend API"""
    print("=" * 60)
    print("FieldShift FarmOS - Device Registration")
    print("=" * 60)
    print()
    
    print(f"Registering device...")
    print(f"  Device ID: {DEVICE_ID}")
    print(f"  Device Type: {DEVICE_TYPE}")
    print(f"  Farm ID: {FARM_ID}")
    print()
    
    try:
        response = requests.post(
            f"{API_BASE}/hardware/register",
            json={
                "device_id": DEVICE_ID,
                "device_type": DEVICE_TYPE,
                "farm_id": FARM_ID
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            api_key = data['api_key']
            
            print("✅ Device registered successfully!")
            print()
            print(f"Device ID: {DEVICE_ID}")
            print(f"API Key: {'*' * 40} (stored securely)")
            print()
            
            return api_key
            
        elif response.status_code == 409:
            print("⚠️  Device already registered!")
            print("   Cannot retrieve existing API key for security.")
            print("   Options:")
            print("   1. Use existing config.h if you have it")
            print("   2. Contact admin to rotate credentials")
            print("   3. Register a new device with different ID")
            return None
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend!")
        print("   Make sure FastAPI is running on http://localhost:8000")
        print("   Start with: cd backend && python main.py")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def update_config_file(api_key, wifi_ssid, wifi_password, api_server):
    """Update config.h with device credentials"""
    print("Updating config.h...")
    
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Config file not found: {CONFIG_FILE}")
        return False
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            content = f.read()
        
        # Update values
        content = re.sub(
            r'const char\* WIFI_SSID = ".*?";',
            f'const char* WIFI_SSID = "{wifi_ssid}";',
            content
        )
        content = re.sub(
            r'const char\* WIFI_PASSWORD = ".*?";',
            f'const char* WIFI_PASSWORD = "{wifi_password}";',
            content
        )
        content = re.sub(
            r'const char\* API_SERVER = ".*?";',
            f'const char* API_SERVER = "{api_server}";',
            content
        )
        content = re.sub(
            r'const char\* DEVICE_ID = ".*?";',
            f'const char* DEVICE_ID = "{DEVICE_ID}";',
            content
        )
        content = re.sub(
            r'const char\* API_KEY = ".*?";',
            f'const char* API_KEY = "{api_key}";',
            content
        )
        content = re.sub(
            r'const int FARM_ID = \d+;',
            f'const int FARM_ID = {FARM_ID};',
            content
        )
        
        # Write back
        with open(CONFIG_FILE, 'w') as f:
            f.write(content)
        
        print("✅ config.h updated successfully!")
        print()
        print("Updated values:")
        print(f"  WIFI_SSID: {wifi_ssid}")
        print(f"  WIFI_PASSWORD: {'*' * len(wifi_password)}")
        print(f"  API_SERVER: {api_server}")
        print(f"  DEVICE_ID: {DEVICE_ID}")
        print(f"  API_KEY: {'*' * 40}")
        print(f"  FARM_ID: {FARM_ID}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating config.h: {e}")
        return False

def main():
    """Main registration flow"""
    print()
    print("⚠️  SECURITY NOTICE:")
    print("   This script will store credentials in config.h")
    print("   Ensure config.h is in .gitignore")
    print("   Never commit config.h to version control")
    print()
    
    # Get Wi-Fi credentials from user
    print("Enter your PHONE HOTSPOT credentials:")
    wifi_ssid = input("Wi-Fi SSID: ").strip()
    wifi_password = input("Wi-Fi Password: ").strip()
    print()
    
    # Get API server (laptop IP on hotspot)
    print("Enter your laptop's IP address on the hotspot:")
    print("(You'll get this after connecting to your phone hotspot)")
    print("Run: ipconfig (Windows) or ifconfig (Linux/Mac)")
    api_server = input("Laptop IP: ").strip()
    print()
    
    if not wifi_ssid or not wifi_password or not api_server:
        print("❌ All fields are required!")
        return 1
    
    # Register device
    api_key = register_device()
    
    if not api_key:
        print()
        print("Registration incomplete. Exiting.")
        return 1
    
    # Update config file
    if not update_config_file(api_key, wifi_ssid, wifi_password, api_server):
        print()
        print("❌ Failed to update config.h")
        return 1
    
    print("=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Verify config.h has correct values")
    print("2. Connect your laptop to phone hotspot")
    print("3. Update API_SERVER in config.h if IP changed")
    print("4. Compile and upload firmware to NodeMCU")
    print("5. Monitor Serial output (115200 baud)")
    print()
    print("IMPORTANT:")
    print("- Keep pumpCommissioned = false (safety)")
    print("- Test sensor readings first")
    print("- Verify telemetry appears in dashboard")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
