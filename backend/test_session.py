import httpx
import asyncio
import time

BASE_URL = "http://127.0.0.1:8003"

async def test_session_flow():
    print("🚀 Testing Session Authentication Flow...")
    
    # 1. Signup/Login to get Token
    email = f"session_test_{int(time.time())}@example.com"
    pwd = "secure_password"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Signup
        print(f"\n[1] Signing up {email}...")
        resp = await client.post(f"{BASE_URL}/api/v1/auth/signup", json={"email": email, "password": pwd})
        if resp.status_code != 200:
            print(f"Signup Failed: {resp.text}")
            return

        # Login
        print("\n[2] Logging in...")
        resp = await client.post(f"{BASE_URL}/api/v1/auth/login", json={"email": email, "password": pwd})
        if resp.status_code != 200:
            print(f"Login Failed: {resp.text}")
            return
            
        data = resp.json()
        token = data.get("access_token")
        api_key = data.get("api_key")
        
        if token:
            print(f"✅ Received Session Token: {token[:10]}...")
        else:
            print("❌ No Access Token in response!")
            return

        # 3. Access Protected Endpoint with Token
        print("\n[3] Accessing /auth/me with Bearer Token...")
        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        
        if resp.status_code == 200:
            user_data = resp.json()
            print(f"✅ Auth Success! User: {user_data.get('email')}")
        else:
            print(f"❌ Auth Failed: {resp.status_code} {resp.text}")

        # 4. Logout
        print("\n[4] Logging out...")
        resp = await client.post(f"{BASE_URL}/api/v1/auth/logout", headers=headers)
        print(f"Logout Status: {resp.status_code}")

        # 5. Try Accessing Again (Should Fail)
        print("\n[5] Accessing /auth/me after logout...")
        resp = await client.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        if resp.status_code == 401:
            print("✅ Access Denied (Expected 401)")
        else:
            print(f"❌ Unexpected Status: {resp.status_code}")
            
    print("\nSession Flow Verification Complete.")

if __name__ == "__main__":
    asyncio.run(test_session_flow())
