import httpx
import sqlite3
import asyncio
import os
import time

BASE_URL = "http://127.0.0.1:8003"
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "promptshield.db")

async def test_playground_flow():
    print(f"Targeting: {BASE_URL}")
    print(f"DB Path: {DB_PATH}")

    # 1. Signup
    email = f"test_playground_{int(time.time())}@example.com"
    password = "securepassword123"
    print(f"\n[1] Signing up user: {email}")
    
    signup_api_key = None
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{BASE_URL}/api/v1/auth/signup", 
                json={"email": email, "password": password, "full_name": "Test User"}
            )
            print(f"Signup Status: {resp.status_code}")
            if resp.status_code == 200:
                signup_data = resp.json()
                signup_api_key = signup_data.get("api_key")
                print(f"Signup Success. API Key: {signup_api_key}")
            else:
                print(f"Signup Failed: {resp.text}")
                return
        except Exception as e:
            print(f"Connection Failed: {e}")
            return

    # 2. Get Verification Token from DB
    print("\n[2] Fetching OTP from DB...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT verification_token FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            token = row[0]
            print(f"Found Token: {token}")
        else:
            print("Error: User not found in DB!")
            return
    except Exception as e:
        print(f"DB Access Failed: {e}")
        return

    # 3. Verify
    print(f"\n[3] Verifying with token: {token}")
    async with httpx.AsyncClient() as client:
        # Pass API Key header!
        headers = {"X-API-Key": signup_api_key}
        resp = await client.post(
            f"{BASE_URL}/api/v1/auth/verify",
            params={"token": token},
            headers=headers
        )
        print(f"Verify Status: {resp.status_code}")
        print(f"Verify Response: {resp.json()}")

    # 4. Login
    print("\n[4] Logging in...")
    api_key = None
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        print(f"Login Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            api_key = data.get("api_key")
            print(f"Got API Key: {api_key}")
        else:
            print(f"Login Failed: {resp.text}")
            return

    # 5. Test Compress (Playground Feature 1)
    print("\n[5] Testing Compression Endpoint...")
    headers = {"X-API-Key": api_key}
    prompt_text = "Please could you kindly act as a python expert and write a script to hello world."
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/compress",
            headers=headers,
            json={
                "text": prompt_text,
                "model": "gpt-4o-mini",
                "format": "verbose"
            }
        )
        print(f"Compress Status: {resp.status_code}")
        if resp.status_code == 200:
            res = resp.json()
            print(f"Original Token Count: {res['tokens']['raw_tokens']}")
            print(f"Compressed Token Count: {res['tokens']['compressed_tokens']}")
            print(f"Savings: {res['tokens']['savings_ratio']*100:.1f}%")
            print(f"Compressed Text: {res['compressed_text']}")
        else:
            print(f"Compress Failed: {resp.text}")

    # 6. Test Execute (Playground Feature 2)
    print("\n[6] Testing Execute Endpoint (Mock/No-Key)...")
    # We expect an error string in the output because we don't have real keys set up in this env context
    # unless they are in .env. But the flow should succeed (200 OK) even if the LLM provider returns an error string.
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/execute",
            headers=headers,
            json={
                "text": "Write a haiku about code.",
                "provider": "openai",
                "model": "gpt-4o-mini"
            }
        )
        print(f"Execute Status: {resp.status_code}")
        if resp.status_code == 200:
            res = resp.json()
            print(f"Provider: {res['provider']}")
            print(f"Output: {res['output']}")
        else:
            print(f"Execute Failed: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_playground_flow())
