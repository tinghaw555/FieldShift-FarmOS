#!/usr/bin/env python3
"""
Quick verification script for NodeMCU connection readiness
Tests backend accessibility and device registration
"""

import requests
import subprocess
import re
import socket

API_BASE = "http://localhost:8000/api"
DEVICE_ID = "NODEMCU_V3_ESP8266_001"

def print_header(text):
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")

def check_network():
    """Check current network connection"""
    print("🌐 Network Status:")
    print("-" * 70)
    
    try:
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
        output = result.stdout
        
        # Find Wi-Fi adapter
        lines = output.split('\n')
        in_wifi = False
        wifi_ip = None
        
        for line in lines:
            if 'Wireless LAN adapter Wi-Fi' in line:
                in_wifi = True
            elif in_wifi and 'IPv4 Address' in line:
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if ip_match:
                    wifi_ip = ip_match.group(1)
                    break
            elif in_wifi and line.strip() == '':
                break
        
        if wifi_ip:
            print(f"✅ Wi-Fi Connected")
            print(f"   IP Address: {wifi_ip}")
            
            # Determine network type
            if wifi_ip.startswith('10.22.'):
                print(f"   ⚠️  School/Work Network")
                print(f"   → You need to switch to phone hotspot!")
            elif wifi_ip.startswith('192.168.') or wifi_ip.startswith('172.20.'):
                print(f"   ✅ Likely Hotspot Network")
            else:
                print(f"   ℹ️  Unknown Network Type")
            
            return wifi_ip
        else:
            print("❌ No Wi-Fi connection detected")
            return None
            
    except Exception as e:
        print(f"❌ Error checking network: {e}")
        return None

def check_backend():
    """Check backend accessibility"""
    print("\n🔧 Backend Status:")
    print("-" * 70)
    
    try:
        # Test localhost
        response = requests.get(f"{API_BASE}/farms", timeout=5)
        if response.status_code == 200:
            farms = response.json()
            print(f"✅ Backend accessible on localhost")
            print(f"   Farms in database: {len(farms)}")
        else:
            print(f"⚠️  Backend responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend not accessible on localhost:8000")
        print("   Start backend: cd backend && python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Check if backend listens on network interface
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, shell=True)
        output = result.stdout
        
        if ':8000' in output:
            if '0.0.0.0:8000' in output:
                print("✅ Backend listening on all interfaces (0.0.0.0)")
            elif '127.0.0.1:8000' in output:
                print("⚠️  Backend only on localhost (127.0.0.1)")
                print("   NodeMCU won't be able to connect from network!")
                print("   Edit backend/main.py: host='0.0.0.0'")
        else:
            print("⚠️  No process listening on port 8000")
    except:
        pass
    
    return True

def check_device_registration():
    """Check if device is registered"""
    print("\n📱 Device Registration:")
    print("-" * 70)
    
    try:
        response = requests.get(f"{API_BASE}/hardware/device/{DEVICE_ID}/status", timeout=5)
        if response.status_code == 200:
            device = response.json()
            print(f"✅ Device registered")
            print(f"   Device ID: {device['device_id']}")
            print(f"   Type: {device['device_type']}")
            print(f"   Farm ID: {device['farm_id']}")
            print(f"   Status: {device['status']}")
            
            if device['last_seen']:
                print(f"   Last seen: {device['last_seen']}")
            else:
                print(f"   Last seen: Never (waiting for first connection)")
            
            return True
        elif response.status_code == 404:
            print(f"❌ Device not registered: {DEVICE_ID}")
            print("   Run setup script: python setup_nodemcu_automated.py")
            return False
        else:
            print(f"❌ Error checking device: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_firewall():
    """Check firewall status"""
    print("\n🔥 Firewall Status:")
    print("-" * 70)
    
    try:
        # Try to check firewall rules (requires admin)
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-NetFirewallRule -DisplayName "*FieldShift*" | Select-Object DisplayName, Enabled'],
            capture_output=True, text=True, shell=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ Firewall rule exists for FieldShift")
            print(result.stdout.strip())
        else:
            print("⚠️  No firewall rule found for FieldShift")
            print("   Run as Administrator:")
            print('   New-NetFirewallRule -DisplayName "FieldShift FarmOS API"')
            print('       -Direction Inbound -LocalPort 8000 -Protocol TCP')
            print('       -Action Allow -Profile Private')
            
    except Exception as e:
        print("ℹ️  Cannot check firewall (requires admin privileges)")
        print("   Ensure port 8000 is allowed on Private network")

def check_com_ports():
    """Check for available COM ports"""
    print("\n🔌 COM Ports:")
    print("-" * 70)
    
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-PnpDevice -Class Ports | Where-Object {$_.Status -eq "OK"} | Select-Object FriendlyName'],
            capture_output=True, text=True, shell=True
        )
        
        if result.returncode == 0:
            ports = [line.strip() for line in result.stdout.split('\n') if line.strip() and 'COM' in line]
            
            # Filter out Bluetooth ports
            usb_ports = [p for p in ports if 'Bluetooth' not in p and 'COM' in p]
            
            if usb_ports:
                print("✅ USB Serial ports detected:")
                for port in usb_ports:
                    com_match = re.search(r'COM\d+', port)
                    if com_match:
                        print(f"   {com_match.group(0)}: {port}")
            else:
                print("⚠️  No USB serial ports detected")
                print("   Connect NodeMCU via USB cable")
                print("   Install CH340G driver if needed:")
                print("   http://www.wch.cn/downloads/CH341SER_ZIP.html")
    except Exception as e:
        print(f"ℹ️  Could not check COM ports: {e}")

def test_api_reachability(laptop_ip):
    """Test if API is reachable from network"""
    if not laptop_ip:
        return
    
    print("\n🌍 Network API Reachability:")
    print("-" * 70)
    
    print(f"Testing if API is accessible from network IP...")
    print(f"URL: http://{laptop_ip}:8000/api/farms")
    print()
    print("You can test this from your phone's browser or another device")
    print("on the same network (hotspot).")

def main():
    print_header("FieldShift FarmOS - Connection Verification")
    
    laptop_ip = check_network()
    backend_ok = check_backend()
    device_ok = check_device_registration()
    check_firewall()
    check_com_ports()
    
    if laptop_ip:
        test_api_reachability(laptop_ip)
    
    # Summary
    print_header("Summary")
    
    all_good = True
    
    if backend_ok:
        print("✅ Backend accessible")
    else:
        print("❌ Backend not accessible")
        all_good = False
    
    if device_ok:
        print("✅ Device registered")
    else:
        print("❌ Device not registered")
        all_good = False
    
    if laptop_ip:
        if laptop_ip.startswith('10.22.'):
            print("⚠️  On school/work network - switch to phone hotspot")
            all_good = False
        else:
            print(f"✅ Network connected ({laptop_ip})")
    else:
        print("❌ No network connection")
        all_good = False
    
    print()
    
    if all_good:
        print("🎉 All checks passed! Ready to connect NodeMCU hardware.")
        print()
        print("Next steps:")
        print("1. Connect NodeMCU via USB")
        print("2. Upload firmware using Arduino IDE")
        print("3. Monitor Serial output (115200 baud)")
        print("4. Verify telemetry in dashboard")
    else:
        print("⚠️  Some checks failed. Review issues above.")
        print()
        print("Common fixes:")
        print("- Start backend: cd backend && python main.py")
        print("- Switch to phone hotspot if on school network")
        print("- Run setup: python setup_nodemcu_automated.py")
        print("- Add firewall rule (see above)")
    
    print()

if __name__ == "__main__":
    main()
