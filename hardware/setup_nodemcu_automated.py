#!/usr/bin/env python3
"""
Automated NodeMCU V3 Setup for FieldShift FarmOS
Handles device registration and config.h generation
"""

import requests
import sys
import os
import re
import subprocess
import socket

# Configuration
API_BASE = "http://localhost:8000/api"
DEVICE_ID = "NODEMCU_V3_ESP8266_001"
DEVICE_TYPE = "NodeMCU-V3-ESP8266"
FARM_ID = 1

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "FieldShift_NodeMCU_V3", "config.h")

def print_header(text):
    """Print formatted header"""
    print()
    print("=" * 70)
    print(text.center(70))
    print("=" * 70)
    print()

def print_section(text):
    """Print section header"""
    print()
    print("-" * 70)
    print(text)
    print("-" * 70)

def get_wifi_ip():
    """Get current Wi-Fi IP address"""
    try:
        # Get ipconfig output
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
        output = result.stdout
        
        # Parse for Wi-Fi adapter
        lines = output.split('\n')
        in_wifi_section = False
        
        for i, line in enumerate(lines):
            if 'Wireless LAN adapter Wi-Fi' in line:
                in_wifi_section = True
            elif in_wifi_section and 'IPv4 Address' in line:
                # Extract IP
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if ip_match:
                    return ip_match.group(1)
            elif in_wifi_section and line.strip() == '':
                in_wifi_section = False
        
        return None
    except Exception as e:
        print(f"❌ Error getting IP: {e}")
        return None

def check_backend():
    """Check if backend is accessible"""
    print_section("STEP 1: Checking Backend")
    
    try:
        response = requests.get(f"{API_BASE}/farms", timeout=5)
        if response.status_code == 200:
            farms = response.json()
            print(f"✅ Backend accessible")
            print(f"   Found {len(farms)} farms in database")
            return True
        else:
            print(f"⚠️  Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend at http://localhost:8000")
        print()
        print("Please ensure:")
        print("  1. Backend is running: cd backend && python main.py")
        print("  2. Backend is on port 8000")
        print("  3. No firewall blocking localhost connections")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def register_device_api():
    """Register device with backend"""
    print_section("STEP 2: Device Registration")
    
    print(f"Registering device...")
    print(f"  Device ID: {DEVICE_ID}")
    print(f"  Device Type: {DEVICE_TYPE}")
    print(f"  Farm ID: {FARM_ID}")
    
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
            
            print()
            print("✅ Device registered successfully!")
            print()
            print("⚠️  SECURITY NOTICE:")
            print("   API Key will be stored in config.h")
            print("   This key cannot be retrieved again")
            print("   config.h is excluded from git (.gitignore)")
            print()
            
            return api_key
            
        elif response.status_code == 409:
            print()
            print("⚠️  Device already registered!")
            print()
            print("The device ID 'NODEMCU_V3_ESP8266_001' is already in the database.")
            print("For security, the API key cannot be retrieved.")
            print()
            print("Options:")
            print("  1. If you have the existing config.h with API key, use it")
            print("  2. Register with a different device ID (edit this script)")
            print("  3. Contact admin to reset device credentials")
            print()
            return None
            
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_user_input():
    """Get Wi-Fi credentials and server IP from user"""
    print_section("STEP 3: Network Configuration")
    
    print("📱 PHONE HOTSPOT SETUP")
    print()
    print("You need to provide:")
    print("  1. Your phone hotspot SSID (name)")
    print("  2. Your phone hotspot password")
    print("  3. Your laptop's IP when connected to hotspot")
    print()
    
    # Detect current IP
    current_ip = get_wifi_ip()
    if current_ip:
        print(f"ℹ️  Your current Wi-Fi IP: {current_ip}")
        print()
        if current_ip.startswith('10.22.'):
            print("⚠️  This looks like a school/work network IP")
            print("   You need to connect to your PHONE HOTSPOT first!")
            print()
            print("Steps:")
            print("  1. Enable hotspot on your phone")
            print("  2. Connect your laptop to the phone hotspot")
            print("  3. Run this script again")
            print()
            
            choice = input("Continue anyway? (y/n): ").strip().lower()
            if choice != 'y':
                print("Setup cancelled. Connect to phone hotspot and try again.")
                return None
        elif current_ip.startswith('192.168.') or current_ip.startswith('172.20.'):
            print("✅ This looks like a hotspot/mobile network IP")
            use_current = input(f"Use this IP ({current_ip}) as API_SERVER? (y/n): ").strip().lower()
            if use_current == 'y':
                api_server = current_ip
            else:
                api_server = input("Enter laptop IP on hotspot: ").strip()
        else:
            api_server = input("Enter laptop IP on hotspot: ").strip()
    else:
        print("⚠️  Could not detect current IP")
        api_server = input("Enter laptop IP on hotspot: ").strip()
    
    print()
    wifi_ssid = input("Enter phone hotspot SSID: ").strip()
    wifi_password = input("Enter phone hotspot password: ").strip()
    
    print()
    
    if not wifi_ssid or not wifi_password or not api_server:
        print("❌ All fields are required!")
        return None
    
    # Validate IP format
    try:
        socket.inet_aton(api_server)
    except socket.error:
        print(f"❌ Invalid IP address: {api_server}")
        return None
    
    return {
        'wifi_ssid': wifi_ssid,
        'wifi_password': wifi_password,
        'api_server': api_server
    }

def update_config_h(api_key, config):
    """Update config.h with credentials"""
    print_section("STEP 4: Updating config.h")
    
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Config file not found: {CONFIG_FILE}")
        return False
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update values using regex
        content = re.sub(
            r'const char\* WIFI_SSID = ".*?";',
            f'const char* WIFI_SSID = "{config["wifi_ssid"]}";',
            content
        )
        content = re.sub(
            r'const char\* WIFI_PASSWORD = ".*?";',
            f'const char* WIFI_PASSWORD = "{config["wifi_password"]}";',
            content
        )
        content = re.sub(
            r'const char\* API_SERVER = ".*?";',
            f'const char* API_SERVER = "{config["api_server"]}";',
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
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ config.h updated successfully!")
        print()
        print("Configuration:")
        print(f"  WIFI_SSID: {config['wifi_ssid']}")
        print(f"  WIFI_PASSWORD: {'*' * len(config['wifi_password'])}")
        print(f"  API_SERVER: {config['api_server']}")
        print(f"  API_PORT: 8000")
        print(f"  DEVICE_ID: {DEVICE_ID}")
        print(f"  API_KEY: {'*' * 40} (stored securely)")
        print(f"  FARM_ID: {FARM_ID}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating config.h: {e}")
        return False

def check_arduino_tools():
    """Check if Arduino IDE/CLI is available"""
    print_section("STEP 5: Checking Arduino Tools")
    
    # Check Arduino CLI
    try:
        result = subprocess.run(['arduino-cli', 'version'], 
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print("✅ Arduino CLI detected")
            print(f"   {result.stdout.strip()}")
            return 'cli'
    except:
        pass
    
    # Check Arduino IDE
    arduino_paths = [
        r"C:\Program Files (x86)\Arduino\arduino_debug.exe",
        r"C:\Program Files\Arduino\arduino_debug.exe",
        r"C:\Users\acer\AppData\Local\Arduino15\arduino-cli.exe"
    ]
    
    for path in arduino_paths:
        if os.path.exists(path):
            print(f"✅ Arduino IDE detected: {path}")
            return 'ide'
    
    print("⚠️  Arduino tools not detected")
    print()
    print("To upload firmware, you need:")
    print("  - Arduino IDE: https://www.arduino.cc/en/software")
    print("  OR")
    print("  - Arduino CLI: https://arduino.github.io/arduino-cli/")
    print()
    print("After installation, upload manually:")
    print("  1. Open FieldShift_NodeMCU_V3.ino in Arduino IDE")
    print("  2. Select Board: NodeMCU 1.0 (ESP-12E Module)")
    print("  3. Select Port: Your COM port")
    print("  4. Click Upload")
    
    return None

def main():
    """Main setup workflow"""
    print_header("FieldShift FarmOS - NodeMCU V3 Automated Setup")
    
    print("This script will:")
    print("  ✓ Check backend connectivity")
    print("  ✓ Register NodeMCU device")
    print("  ✓ Generate secure API key")
    print("  ✓ Configure Wi-Fi credentials")
    print("  ✓ Update config.h automatically")
    print()
    
    input("Press Enter to continue...")
    
    # Step 1: Check backend
    if not check_backend():
        print()
        print("❌ Setup cannot continue without backend access")
        return 1
    
    # Step 2: Register device
    api_key = register_device_api()
    if not api_key:
        print()
        print("❌ Setup incomplete. See options above.")
        return 1
    
    # Step 3: Get user input
    config = get_user_input()
    if not config:
        return 1
    
    # Step 4: Update config.h
    if not update_config_h(api_key, config):
        print()
        print("❌ Failed to update config.h")
        return 1
    
    # Step 5: Check Arduino tools
    arduino = check_arduino_tools()
    
    # Final summary
    print_header("✅ SETUP COMPLETE!")
    
    print("Next Steps:")
    print()
    print("1. 📱 Ensure your laptop is connected to PHONE HOTSPOT")
    print(f"   Expected network: {config['wifi_ssid']}")
    print(f"   Expected laptop IP: {config['api_server']}")
    print()
    print("2. 🔌 Connect NodeMCU V3 to laptop via USB")
    print("   - Use Micro-USB data cable (not charge-only)")
    print("   - Check Device Manager for COM port")
    print()
    print("3. 📤 Upload firmware:")
    
    if arduino == 'cli':
        print("   Using Arduino CLI:")
        print("   cd hardware\\FieldShift_NodeMCU_V3")
        print("   arduino-cli compile --fqbn esp8266:esp8266:nodemcuv2 .")
        print("   arduino-cli upload -p COMX --fqbn esp8266:esp8266:nodemcuv2 .")
    elif arduino == 'ide':
        print("   Using Arduino IDE:")
        print("   - Open: FieldShift_NodeMCU_V3.ino")
        print("   - Board: NodeMCU 1.0 (ESP-12E Module)")
        print("   - Port: Your COM port")
        print("   - Click Upload")
    else:
        print("   Install Arduino IDE or CLI first (see above)")
    
    print()
    print("4. 📊 Monitor Serial Output (115200 baud)")
    print("   Expected: Wi-Fi connected → Telemetry sent → HTTP 200")
    print()
    print("5. 🖥️  Check Dashboard")
    print("   URL: http://localhost:3000")
    print("   Section: Smart Farm")
    print("   Expected: Device status = Connected, real sensor values")
    print()
    print("⚠️  SAFETY REMINDER:")
    print("   - Pump is DISABLED (pumpCommissioned = false)")
    print("   - Test sensors first before any pump work")
    print("   - Never power pump from NodeMCU 3.3V pin")
    print()
    print("📖 Full guide: NODEMCU_SETUP_GUIDE.md")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
