import httpx
import asyncio
import os
import time

BASE_URL = "http://127.0.0.1:8003"

async def test_analytics_and_rotation():
    print(f"Targeting: {BASE_URL}")

    # 1. Signup
    email = f"test_analytics_{int(time.time())}@example.com"
    password = "securepassword123"
    print(f"\n[1] Signing up user: {email}")
    
    api_key = None
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/auth/signup", 
            json={"email": email, "password": password, "full_name": "Test User"}
        )
        if resp.status_code == 200:
            data = resp.json()
            api_key = data.get("api_key")
            print(f"Signup Success. API Key: {api_key}")
        else:
            print(f"Signup Failed: {resp.text}")
            return

    if not api_key:
        print("No API Key, aborting.")
        return

    # 2. Generate some activity
    print("\n[2] Generating Activity (3 requests)...")
    headers = {"X-API-Key": api_key}
    prompt_text = "Summarize this very long text into a short sentence."
    
    async with httpx.AsyncClient() as client:
        for i in range(3):
            await client.post(
                f"{BASE_URL}/api/v1/compress",
                headers=headers,
                json={
                    "text": prompt_text,
                    "model": "gpt-4o-mini"
                }
            )
            print(f"  Request {i+1} sent.")

    # 3. Test Analytics Stats
    print("\n[3] Testing Analytics Stats...")
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/api/v1/analytics/stats", headers=headers)
        print(f"Stats Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Stats: {resp.json()}")
        else:
            print(f"Stats Failed: {resp.text}")

    # 4. Test Time Series
    print("\n[4] Testing Time Series...")
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/api/v1/analytics/time-series?days=7", headers=headers)
        print(f"Time Series Status: {resp.status_code}")
        if resp.status_code == 200:
            series = resp.json()
            print(f"Time Series Entries: {len(series)}")
            if len(series) > 0:
                print(f"Latest Entry: {series[-1]}")
        else:
            print(f"Time Series Failed: {resp.text}")

    # 5. Test Key Rotation
    print("\n[5] Testing API Key Rotation...")
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BASE_URL}/api/v1/auth/rotate-key", headers=headers)
        print(f"Rotation Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            new_key = data.get("api_key")
            print(f"New Key: {new_key}")
            
            if new_key == api_key:
                print("ERROR: Key did not change!")
            else:
                print("SUCCESS: Key rotated.")
                
            # Verify old key fails (optional, but good to know)
            print("Verifying old key fails...")
            resp_old = await client.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
            print(f"Old Key Access: {resp_old.status_code} (Expected 401)")

            # Verify new key works
            print("Verifying new key works...")
            headers_new = {"X-API-Key": new_key}
            resp_new = await client.get(f"{BASE_URL}/api/v1/auth/me", headers=headers_new)
            print(f"New Key Access: {resp_new.status_code} (Expected 200)")
            
        else:
            print(f"Rotation Failed: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_analytics_and_rotation())
