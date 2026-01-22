import requests
import time
import sys

BASE_URL = "http://localhost:8003/api/v1"
# Use the known demo key or one from the logs
API_KEY = "sk-ps-demo-key-123" # Replace with valid key if needed, or signup

def test_rate_limit():
    print("Testing Rate Limiting for /api/v1/auth/me (Limit: 100/hour)")
    
    # 1. Login to get a valid key if needed (or assume one)
    # For demo, we might need to sign up a temp user to get a fresh key
    session = requests.Session()
    
    # Create temp user
    email = f"rate_test_{int(time.time())}@example.com"
    pwd = "password123"
    print(f"Creating temp user: {email}")
    try:
        resp = session.post(f"{BASE_URL}/auth/signup", json={"email": email, "password": pwd})
        if resp.status_code == 200:
            api_key = resp.json()["api_key"]
            print(f"Got API Key: {api_key}")
        else:
            print(f"Signup failed: {resp.text}")
            return
    except Exception as e:
        print(f"Connection error: {e}")
        print("Make sure Docker is running: docker-compose up -d --build backend")
        return

    headers = {"X-API-Key": api_key}
    
    # 2. Burst requests
    print("Sending burst of 110 requests...")
    success_count = 0
    blocked_count = 0
    
    for i in range(110):
        try:
            resp = session.get(f"{BASE_URL}/auth/me", headers=headers)
            if resp.status_code == 200:
                success_count += 1
                print(".", end="", flush=True)
            elif resp.status_code == 429:
                blocked_count += 1
                print("X", end="", flush=True)
            else:
                print(f"[{resp.status_code}]", end="", flush=True)
        except Exception as e:
            print("E", end="", flush=True)
            
    print("\n")
    print(f"Success: {success_count}")
    print(f"Blocked (429): {blocked_count}")
    
    if blocked_count > 0:
        print("✅ Rate Limiting is WORKING.")
    else:
        print("⚠️ Rate Limiting NOT triggered (Limit might be higher or not applied).")

if __name__ == "__main__":
    test_rate_limit()
