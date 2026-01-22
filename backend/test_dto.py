import requests
import time

BASE_URL = "http://localhost:8003/api/v1"

def test_dto_security():
    print("Testing DTO Security for /api/v1/auth/me...")
    
    session = requests.Session()
    
    # Create temp user
    email = f"dto_test_{int(time.time())}@example.com"
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
        return

    headers = {"X-API-Key": api_key}
    
    # Get User Profile
    try:
        resp = session.get(f"{BASE_URL}/auth/me", headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            print(f"Response Keys: {list(data.keys())}")
            
            forbidden_fields = ["password_hash", "verification_token", "is_admin"]
            leaked = [f for f in forbidden_fields if f in data]
            
            if leaked:
                print(f"⚠️  CRITICAL: Sensitive data leaked: {leaked}")
            else:
                print("✅ DTO Security PASSED: No sensitive fields found.")
                
            # Verify allowed fields
            if "email" in data and "tier" in data:
                print("✅ Public fields present.")
            else:
                print("⚠️  Warning: Expected public fields missing.")
                
        else:
            print(f"Failed to get profile: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_dto_security()
