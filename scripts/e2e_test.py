import requests
import sys
import time

BASE_URL = "http://127.0.0.1:8001"
API_KEY = "sk-ps-7E-BH9GDWiV-JjG5lteIXg"
HEADERS = {"X-API-Key": API_KEY}

def test_health():
    print("Testing Health Endpoint...", end="")
    try:
        r = requests.get(f"{BASE_URL}/api/v1/health")
        if r.status_code == 200:
            print(" PASS")
            return True
        else:
            print(f" FAIL ({r.status_code})")
            return False
    except Exception as e:
        print(f" FAIL (Exception: {e})")
        return False

def test_compress():
    print("Testing Compress Endpoint...", end="")
    payload = {"text": "Hello world, this is a test prompt."}
    try:
        r = requests.post(f"{BASE_URL}/api/v1/compress", json=payload, headers=HEADERS)
        if r.status_code == 200:
            data = r.json()
            if "compressed_text" in data:
                print(" PASS")
                return True
        print(f" FAIL ({r.status_code} - {r.text})")
        return False
    except Exception as e:
        print(f" FAIL (Exception: {e})")
        return False

def test_execute():
    print("Testing Execute Endpoint...", end="")
    payload = {
        "text": "Optimize this database query: SELECT * FROM users;",
        "provider": "openai",
        "model": "gpt-3.5-turbo"
    }
    try:
        r = requests.post(f"{BASE_URL}/api/v1/execute", json=payload, headers=HEADERS)
        # Note: It might fail if no API Key is present, but we check if it handles it gracefully or returns result
        # Our mock provider returns a string even without key for now (or error string).
        if r.status_code == 200:
            print(" PASS")
            return True
        elif r.status_code == 400 or r.status_code == 500:
             # If it fails due to logic, print it
             print(f" FAIL ({r.status_code} - {r.text})")
             return False
        else:
            print(f" FAIL ({r.status_code})")
            return False
    except Exception as e:
        print(f" FAIL (Exception: {e})")
        return False

def test_analytics():
    print("Testing Analytics Endpoint...", end="")
    try:
        r = requests.get(f"{BASE_URL}/api/v1/stats/summary")
        if r.status_code == 200:
            print(" PASS")
            return True
        print(f" FAIL ({r.status_code})")
        return False
    except Exception as e:
        print(f" FAIL (Exception: {e})")
        return False

if __name__ == "__main__":
    print(f"Running E2E Validation against {BASE_URL}\n")
    
    checks = [
        test_health,
        test_compress,
        test_execute,
        test_analytics
    ]
    
    passed = 0
    for check in checks:
        if check():
            passed += 1
            
    print(f"\nResult: {passed}/{len(checks)} checks passed.")
    
    if passed == len(checks):
        sys.exit(0)
    else:
        sys.exit(1)
