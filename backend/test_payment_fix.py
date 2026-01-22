import httpx
import asyncio
import os
import time

BASE_URL = "http://127.0.0.1:8003"

async def test_real_verification_logic():
    print("--- Testing REAL Payment Verification Logic (via MockBankService) ---")
    
    email = f"pay_real_{int(time.time())}@example.com"
    password = "Password123!"
    
    async with httpx.AsyncClient() as client:
        # 1. Signup
        print(f"\n[1] Signing up user: {email}")
        resp = await client.post(f"{BASE_URL}/api/v1/auth/signup", json={"email": email, "password": password})
        if resp.status_code != 200:
            print(f"Signup Failed: {resp.text}")
            return
        api_key = resp.json()["api_key"]
        print(f"User created. API Key: {api_key}")

        # 2. Create Payment Order
        print("\n[2] Creating Payment Order (Monthly)...")
        headers = {"X-API-Key": api_key}
        resp = await client.post(f"{BASE_URL}/api/v1/payment/create", json={"plan": "monthly"}, headers=headers)
        if resp.status_code != 200:
            print(f"Create Payment Failed: {resp.text}")
            return
        data = resp.json()
        payment_id = data["payment_id"]
        print(f"Payment ID: {payment_id}")

        # 3. Test Scenario: Invalid UTR (Starts with 000)
        print("\n[3] Testing Invalid UTR (000...) - Should Fail")
        invalid_utr = "000123456789"
        resp = await client.post(f"{BASE_URL}/api/v1/payment/confirm", json={
            "plan": "monthly",
            "utr": invalid_utr,
            "payment_id": payment_id
        }, headers=headers)
        print(f"Status: {resp.status_code} | Response: {resp.json()}")
        if resp.status_code == 400 and "not found" in resp.text.lower():
            print("SUCCESS: Correctly rejected invalid UTR.")
        else:
            print("FAILED: Did not reject invalid UTR correctly.")

        # 4. Test Scenario: Expired Transaction (Starts with 999)
        print("\n[4] Testing Expired UTR (999...) - Should Fail")
        expired_utr = "999123456789"
        resp = await client.post(f"{BASE_URL}/api/v1/payment/confirm", json={
            "plan": "monthly",
            "utr": expired_utr,
            "payment_id": payment_id
        }, headers=headers)
        print(f"Status: {resp.status_code} | Response: {resp.json()}")
        if resp.status_code == 400 and "expired" in resp.text.lower():
            print("SUCCESS: Correctly rejected expired transaction.")
        else:
            print("FAILED: Did not reject expired transaction correctly.")

        # 5. Test Scenario: Amount Mismatch (Starts with 888)
        print("\n[5] Testing Amount Mismatch UTR (888...) - Should Fail")
        mismatch_utr = "888123456789"
        resp = await client.post(f"{BASE_URL}/api/v1/payment/confirm", json={
            "plan": "monthly",
            "utr": mismatch_utr,
            "payment_id": payment_id
        }, headers=headers)
        print(f"Status: {resp.status_code} | Response: {resp.json()}")
        if resp.status_code == 400 and "mismatch" in resp.text.lower():
            print("SUCCESS: Correctly rejected amount mismatch.")
        else:
            print("FAILED: Did not reject amount mismatch correctly.")

        # 6. Test Scenario: Valid Transaction (Random valid format) -> Should go to PENDING (Manual Mode)
        print("\n[6] Testing Valid UTR (Random 12 digits) - Should be PENDING")
        # Ensure it doesn't start with 000, 999, 888. 
        # Use 1 + random digits
        import random
        valid_utr = "1" + "".join([str(random.randint(0, 9)) for _ in range(11)])
        
        resp = await client.post(f"{BASE_URL}/api/v1/payment/confirm", json={
            "plan": "monthly",
            "utr": valid_utr,
            "payment_id": payment_id
        }, headers=headers)
        
        print(f"Status: {resp.status_code} | Response: {resp.json()}")
        
        if resp.status_code == 200 and resp.json().get("status") == "pending_verification":
            print("SUCCESS: Valid UTR correctly marked as PENDING for manual verification.")
        else:
            print(f"FAILED: Expected Pending, got {resp.json().get('status')}")

        # 7. Test Scenario: MAGIC UTR (123456789012) -> Should be CONFIRMED (Demo Mode)
        print("\n[7] Testing Magic UTR (123456789012) - Should be CONFIRMED")
        magic_utr = "123456789012"
        
        resp = await client.post(f"{BASE_URL}/api/v1/payment/confirm", json={
            "plan": "monthly",
            "utr": magic_utr,
            "payment_id": payment_id
        }, headers=headers)
        
        print(f"Status: {resp.status_code} | Response: {resp.json()}")
        
        if resp.status_code == 200 and resp.json().get("status") == "confirmed":
             print("SUCCESS: Magic UTR confirmed immediately.")
             print(f"New API Key: {resp.json().get('new_api_key')}")
        else:
             print(f"FAILED: Magic UTR was not confirmed.")

if __name__ == "__main__":
    asyncio.run(test_real_verification_logic())
