import socket
import requests
import time
import sys

def check_port(host, port, timeout=2):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False

def check_url(url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False

def main():
    print("🔍 Verifying Deployment Status...")
    
    # Check Backend Port
    if check_port("localhost", 8003):
        print("✅ Backend Port (8003) is open")
    else:
        print("❌ Backend Port (8003) is closed or unreachable")
        
    # Check Frontend Port
    if check_port("localhost", 3000):
        print("✅ Frontend Port (3000) is open")
    else:
        print("❌ Frontend Port (3000) is closed or unreachable")

    # Check Backend Health
    print("⏳ Checking Backend Health...")
    if check_url("http://localhost:8003/docs"):
        print("✅ Backend is responding (Docs available)")
    else:
        print("❌ Backend is not responding correctly")

    # Check Frontend Health
    print("⏳ Checking Frontend Health...")
    if check_url("http://localhost:3000"):
        print("✅ Frontend is responding")
    else:
        print("❌ Frontend is not responding correctly")

if __name__ == "__main__":
    main()
