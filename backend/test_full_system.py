import httpx
import asyncio
import time
import secrets

BASE_URL = "http://127.0.0.1:8003"

async def run_full_system_check():
    print("================================================================")
    print("       🚀 PROMPTSHIELD ENTERPRISE READINESS SYSTEM CHECK       ")
    print("================================================================")
    
    # Generate unique test users
    ts = int(time.time())
    user_standard_email = f"std_user_{ts}@enterprise.test"
    user_vip_email = f"vip_user_{ts}@enterprise.test"
    password = "StrongPassword123!"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # --- 1. HEALTH CHECK ---
        print("\n[1] SYSTEM HEALTH CHECK")
        try:
            resp = await client.get(f"{BASE_URL}/")
            if resp.status_code == 200:
                print("✅ API Root is accessible.")
            else:
                print(f"❌ API Root failed: {resp.status_code}")
                return
        except Exception as e:
            print(f"❌ API Connection failed: {e}")
            return

        # --- 2. AUTHENTICATION & STANDARD USER FLOW ---
        print(f"\n[2] TESTING STANDARD USER FLOW (Signup -> Pending Payment)")
        
        # 2a. Signup
        print(f"   -> Signing up {user_standard_email}...")
        resp = await client.post(f"{BASE_URL}/api/v1/auth/signup", json={"email": user_standard_email, "password": password})
        if resp.status_code != 200:
            print(f"   ❌ Signup Failed: {resp.text}")
            return
        print("   ✅ Signup Successful")
        
        # 2b. Login
        print("   -> Logging in...")
        resp = await client.post(f"{BASE_URL}/api/v1/auth/login", json={"email": user_standard_email, "password": password})
        if resp.status_code != 200:
            print(f"   ❌ Login Failed: {resp.text}")
            return
        
        login_data = resp.json()
        api_key = login_data["api_key"]
        headers_std = {"X-API-Key": api_key}
        print(f"   ✅ Login Successful (API Key: {api_key[:8]}...)")
        
        # 2c. Check Initial Profile (Free Tier)
        print("   -> Checking Initial Profile...")
        resp = await client.get(f"{BASE_URL}/api/v1/auth/me", headers=headers_std)
        profile = resp.json()
        if profile["tier"] == "free" and profile["max_usage"] == 50:
             print("   ✅ Profile verified: Tier=Free, Limit=50")
        else:
             print(f"   ❌ Profile Mismatch: {profile}")
             
        # 2d. Create Payment (Monthly)
        print("   -> Creating Payment Order...")
        resp = await client.post(f"{BASE_URL}/api/v1/payment/create", json={"plan": "monthly"}, headers=headers_std)
        payment_id = resp.json()["payment_id"]
        
        # 2e. Confirm Payment with Valid UTR (Optimistic Verification Mode)
        print("   -> Submitting Valid UTR (Optimistic Mode)...")
        # Generate random valid UTR
        import random
        valid_utr = "1" + "".join([str(random.randint(0, 9)) for _ in range(11)])
        
        resp = await client.post(f"{BASE_URL}/api/v1/payment/confirm", json={
            "plan": "monthly",
            "utr": valid_utr,
            "payment_id": payment_id
        }, headers=headers_std)
        
        data = resp.json()
        if data["status"] == "provisional":
            print("   ✅ System correctly marked payment as PROVISIONAL (Immediate Access).")
            new_api_key_std = data["new_api_key"]
            headers_std = {"X-API-Key": new_api_key_std} # Update headers
        else:
            print(f"   ❌ Error: Expected 'provisional', got '{data.get('status')}'")
            
        # 2f. Verify Profile is NOW PREMIUM (Optimistic)
        print("   -> Verifying Profile is PREMIUM (Optimistic)...")
        resp = await client.get(f"{BASE_URL}/api/v1/auth/me", headers=headers_std)
        profile = resp.json()
        if profile["tier"] == "premium":
            print("   ✅ Optimistic Access Granted: User is Premium.")
        else:
            print(f"   ❌ Failed: User was NOT upgraded immediately! Profile: {profile}")

        # 2g. ADMIN APPROVAL
        print("   -> Admin approving payment (Finalizing)...")
        resp = await client.post(f"{BASE_URL}/api/v1/admin/payments/{payment_id}/approve?admin_secret=admin123")
        if resp.status_code == 200:
            print("   ✅ Admin Approval Successful.")
        else:
             print(f"   ❌ Admin Approval Failed: {resp.text}")

        # 2h. Verify Profile is STILL Premium
        print("   -> Verifying Profile after Approval...")
        resp = await client.get(f"{BASE_URL}/api/v1/auth/me", headers=headers_std)
        if resp.status_code != 200:
             print(f"   ❌ Failed to get profile: {resp.status_code} {resp.text}")
             return

        profile = resp.json()
        if profile.get("tier") == "premium":
            print("   ✅ Upgrade Verified: User is still Premium.")
        else:
            print(f"   ❌ Upgrade Failed after approval. Profile: {profile}")

        # --- 2i. REJECTION TEST (Downgrade) ---
        print("\n[2i] TESTING REJECTION & DOWNGRADE")
        # Create another dummy payment to reject
        print("   -> Creating another payment to reject...")
        resp = await client.post(f"{BASE_URL}/api/v1/payment/create", json={"plan": "topup"}, headers=headers_std)
        reject_payment_id = resp.json()["payment_id"]
        
        # Confirm it (get access)
        reject_utr = "9" + "".join([str(random.randint(0, 9)) for _ in range(11)])
        resp = await client.post(f"{BASE_URL}/api/v1/payment/confirm", json={
            "plan": "topup",
            "utr": reject_utr,
            "payment_id": reject_payment_id
        }, headers=headers_std)
        
        # Check limit increased (Topup = +200, so 1000 + 200 = 1200)
        # Wait, previous user was Monthly (1000). +200 = 1200.
        resp = await client.get(f"{BASE_URL}/api/v1/auth/me", headers=headers_std)
        if resp.json()["max_usage"] >= 1200:
             print("   ✅ Top-up applied successfully (Pre-Rejection).")
        
        # Reject it
        print("   -> Admin REJECTING the payment...")
        resp = await client.post(f"{BASE_URL}/api/v1/admin/payments/{reject_payment_id}/reject?admin_secret=admin123")
        if resp.status_code == 200:
             print("   ✅ Admin Rejection Successful.")
        else:
             print(f"   ❌ Admin Rejection Failed: {resp.text}")
             
        # Verify Downgrade
        print("   -> Verifying Downgrade...")
        resp = await client.get(f"{BASE_URL}/api/v1/auth/me", headers=headers_std)
        profile = resp.json()
        if profile["tier"] == "free" and profile["max_usage"] == 50:
             print("   ✅ Downgrade Verified: User back to Free tier.")
        else:
             print(f"   ❌ Downgrade Failed! Profile: {profile}")

        # --- 3. VIP / DEMO USER FLOW ---
        print(f"\n[3] TESTING VIP/DEMO FLOW (Signup -> Magic UTR -> Instant Upgrade)")
        
        # 3a. Signup VIP
        print(f"   -> Signing up {user_vip_email}...")
        await client.post(f"{BASE_URL}/api/v1/auth/signup", json={"email": user_vip_email, "password": password})
        
        # 3b. Login VIP
        resp = await client.post(f"{BASE_URL}/api/v1/auth/login", json={"email": user_vip_email, "password": password})
        login_data_vip = resp.json()
        api_key_vip = login_data_vip["api_key"]
        headers_vip = {"X-API-Key": api_key_vip}
        
        # 3c. Create Payment
        resp = await client.post(f"{BASE_URL}/api/v1/payment/create", json={"plan": "monthly"}, headers=headers_vip)
        payment_id_vip = resp.json()["payment_id"]
        
        # 3d. Submit MAGIC UTR
        print("   -> Submitting MAGIC UTR (123456789012)...")
        resp = await client.post(f"{BASE_URL}/api/v1/payment/confirm", json={
            "plan": "monthly",
            "utr": "123456789012",
            "payment_id": payment_id_vip
        }, headers=headers_vip)
        
        data = resp.json()
        if data["status"] == "confirmed":
            print("   ✅ Magic UTR accepted. Status: Confirmed.")
            new_api_key = data["new_api_key"]
            print(f"   ✅ New API Key issued: {new_api_key}")
            # Update headers with new key
            headers_vip = {"X-API-Key": new_api_key}
        else:
            print(f"   ❌ Magic UTR failed: {data}")
            
        # 3e. Verify Profile Upgrade
        print("   -> Verifying Profile Upgrade...")
        resp = await client.get(f"{BASE_URL}/api/v1/auth/me", headers=headers_vip)
        profile = resp.json()
        if profile["tier"] == "premium" and profile["max_usage"] == 1000:
            print("   ✅ Profile Verified: Tier=Premium, Limit=1000")
        else:
            print(f"   ❌ Upgrade Failed. Profile: {profile}")

        # --- 4. SECURITY & ERROR HANDLING ---
        print("\n[4] SECURITY & EDGE CASE TESTS")
        
        # 4a. Re-use UTR
        print(f"   -> Testing UTR Re-use (Replay Attack) using {valid_utr}...")
        resp = await client.post(f"{BASE_URL}/api/v1/payment/confirm", json={
            "plan": "monthly",
            "utr": valid_utr, # Already used in Step 2e
            "payment_id": payment_id_vip
        }, headers=headers_vip)
        
        if resp.status_code == 400 and "already been used" in resp.text:
            print("   ✅ Replay Attack Blocked (UTR Reuse prevented).")
        else:
            print(f"   ❌ Replay Attack Succeeded (or wrong error): {resp.text}")

        # 4b. Invalid Plan
        print("   -> Testing Invalid Plan Injection...")
        resp = await client.post(f"{BASE_URL}/api/v1/payment/create", json={"plan": "lifetime_free"}, headers=headers_std)
        if resp.status_code == 422 or resp.status_code == 400: # Fastapi validation or logic
             print("   ✅ Invalid Plan Rejected.")
        else:
             print(f"   ❌ Invalid Plan Accepted: {resp.status_code}")

    print("\n================================================================")
    print("       ✅ SYSTEM READINESS CHECK COMPLETE       ")
    print("================================================================")

if __name__ == "__main__":
    asyncio.run(run_full_system_check())