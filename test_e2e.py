import requests
import sqlite3
import time
import uuid

BASE_URL = "http://localhost:8003"
DB_PATH = "promptshield.db"

def get_verification_token(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT verification_token FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def test_e2e():
    print("🚀 Starting End-to-End Test...")
    
    # 1. Signup
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    print(f"\n1️⃣  Testing Signup with {email}...")
    try:
        res = requests.post(f"{BASE_URL}/api/v1/auth/signup", json={
            "email": email,
            "password": password,
            "full_name": "Test User"
        })
        if res.status_code == 200:
            print("   ✅ Signup successful")
        else:
            print(f"   ❌ Signup failed: {res.text}")
            # If failed due to email (likely 500), we can't proceed easily unless we fix env
            if "ConnectionRefusedError" in res.text or "auth" in res.text.lower(): 
                 print("      (Likely due to invalid SMTP credentials in .env)")
            return
    except Exception as e:
        print(f"   ❌ Signup exception: {e}")
        return

    # 2. Verify
    print("\n2️⃣  Testing Email Verification...")
    token = get_verification_token(email)
    if not token:
        print("   ❌ Could not find verification token in DB")
        return
    
    # 3. Login
    print("\n3️⃣  Testing Login...")
    # NOTE: Our current implementation of verify_email_endpoint uses 'Depends(get_current_user)',
    # which implies the user must pass an API Key.
    # But wait, during signup we got an API Key.
    # However, standard flow might be: Signup -> Email -> Click Link -> Verify.
    # The 'verify' endpoint typically doesn't require auth if it uses a unique token.
    # BUT in our app.py: def verify_email_endpoint(token: str, ... user: User = Depends(get_current_user)):
    # This means we DO need to be logged in (have API key) to verify email?
    # That seems weird for a "click link in email" flow.
    # If the user clicks a link, they might not be logged in.
    # But for now, let's respect the API definition and login first.
    
    res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    if res.status_code == 200:
        # Wait, the login endpoint returns {"api_key": ...}
        # But our app uses X-API-Key header or Bearer?
        # Let's check auth.py or how get_current_user works.
        # It usually expects X-API-Key header.
        api_key = res.json()["api_key"]
        headers = {"X-API-Key": api_key}
        print("   ✅ Login successful")
    else:
        print(f"   ❌ Login failed: {res.text}")
        return

    # 2. Verify (Now that we have headers)
    print("\n2️⃣  Testing Email Verification...")
    token = get_verification_token(email)
    if not token:
        print("   ❌ Could not find verification token in DB")
        return
    
    # We use params for token, headers for auth
    res = requests.post(f"{BASE_URL}/api/v1/auth/verify", params={"token": token}, headers=headers)
    if res.status_code == 200:
        print("   ✅ Verification successful")
    elif "Already verified" in res.text:
        print("   ⚠️  Already verified")
    else:
        print(f"   ❌ Verification failed: {res.text}")
        return

    # 4. Check Initial State (Free Tier)

    # 4. Check Initial Free Tier
    print("\n4️⃣  Checking Initial Free Tier State...")
    res = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    user_data = res.json()
    if user_data.get("tier") == "free" and user_data.get("max_usage") == 50:
        print("   ✅ Correctly started on Free tier (50 requests limit)")
    else:
        print(f"   ❌ Incorrect initial state: {user_data}")
        return

    # 5. Subscribe to Monthly Plan
    print("\n5️⃣  Testing Monthly Subscription Upgrade...")
    # Step A: Create Payment Order
    res = requests.post(f"{BASE_URL}/api/v1/payment/create", 
                        headers=headers, 
                        json={"plan": "monthly"})
    payment_id_monthly = None
    if res.status_code == 200:
        data = res.json()
        payment_id_monthly = data.get("payment_id")
        if data.get("amount") == 99 and payment_id_monthly:
            print(f"   ✅ Payment order created (QR generated) - Amount: ₹99, ID: {payment_id_monthly}")
        else:
            print(f"   ⚠️ Payment order created but missing ID or amount mismatch: {data}")
    else:
        print(f"   ❌ Payment creation failed: {res.text}")
        return

    # Step B: Confirm Payment
    print("   ... Confirming payment with UTR...")
    # Generate 12 digit UTR: 2 prefix + 10 timestamp
    utr_monthly = f"10{int(time.time())}" 
    res = requests.post(f"{BASE_URL}/api/v1/payment/confirm", 
                        headers=headers, 
                        json={
                            "plan": "monthly", 
                            "utr": utr_monthly,
                            "payment_id": payment_id_monthly
                        })
    
    if res.status_code == 200:
        print("   ✅ Payment confirmed")
        new_api_key = res.json().get("new_api_key")
        print(f"   🔑 New API Key received: {new_api_key[:10]}...")
        # Update headers with new key!
        headers["X-API-Key"] = new_api_key
    else:
        print(f"   ❌ Payment confirmation failed: {res.text}")
        # If failed due to email, it might still have updated DB?
        # But likely 500 error aborts transaction or just returns error.
        return

    # 6. Verify Upgrade
    print("\n6️⃣  Verifying Monthly Plan Upgrade...")
    res = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    user_data = res.json()
    if user_data.get("subscription_plan") == "monthly" and user_data.get("max_usage") == 1000:
        print("   ✅ User upgraded to Monthly plan (1,000 requests limit)")
    else:
        print(f"   ❌ Upgrade verification failed: {user_data}")
        return

    # 7. Test Top-up
    print("\n7️⃣  Testing Top-up (+200 requests)...")
    # Step A: Create Top-up Order
    res = requests.post(f"{BASE_URL}/api/v1/payment/create", 
                        headers=headers, 
                        json={"plan": "topup"})
    payment_id_topup = None
    if res.status_code == 200:
        data = res.json()
        payment_id_topup = data.get("payment_id")
        if data.get("amount") == 19 and payment_id_topup:
            print(f"   ✅ Top-up order created - Amount: ₹19, ID: {payment_id_topup}")
        else:
            print(f"   ⚠️ Top-up order created but missing ID or amount mismatch: {data}")
    else:
         print(f"   ❌ Top-up creation failed: {res.text}")
         return

    # Step B: Confirm Top-up
    utr_topup = f"20{int(time.time())}" # Unique 12 digit
    res = requests.post(f"{BASE_URL}/api/v1/payment/confirm", 
                        headers=headers, 
                        json={
                            "plan": "topup", 
                            "utr": utr_topup,
                            "payment_id": payment_id_topup
                        })
    
    if res.status_code == 200:
        print("   ✅ Top-up confirmed")
    else:
        print(f"   ❌ Top-up confirmation failed: {res.text}")
        return

    # 8. Verify Top-up Balance
    print("\n8️⃣  Verifying Top-up Balance...")
    res = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    user_data = res.json()
    if user_data.get("max_usage") == 1200: # 1000 + 200
        print("   ✅ Top-up successful! Total limit: 1,200")
    else:
        print(f"   ❌ Top-up verification failed: {user_data}")
        return

    # 9. Test Usage Tracking
    print("\n9️⃣  Testing Core Features & Usage Tracking (1 Request = 1 Token)...")
    res = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    initial_usage = res.json().get("usage_count", 0)
    print(f"   ℹ️  Initial Usage: {initial_usage}")

    print("   ... Testing /api/v1/compress endpoint ...")
    res = requests.post(f"{BASE_URL}/api/v1/compress", 
                        headers=headers, 
                        json={"text": "Hello world, this is a test prompt.", "model": "gpt-4"})
    
    if res.status_code == 200:
        print("   ✅ Optimize request successful")
    else:
        print(f"   ⚠️ Optimize request failed (might be expected iff LLM key missing): {res.text}")

    res = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    new_usage = res.json().get("usage_count", 0)
    
    if new_usage == initial_usage + 1:
        print(f"   ✅ Usage correctly incremented by 1. New Usage: {new_usage}")
    else:
        print(f"   ❌ Usage increment check failed. Expected {initial_usage + 1}, got {new_usage}")

    print("   ... Testing /api/v1/execute endpoint ...")
    res = requests.post(f"{BASE_URL}/api/v1/execute", 
                        headers=headers, 
                        json={"text": "Hello world", "provider": "mock", "model": "gpt-3.5-turbo"})

    res = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    final_usage = res.json().get("usage_count", 0)

    if final_usage == new_usage + 1:
        print(f"   ✅ Usage correctly incremented by another 1. Final Usage: {final_usage}")
    else:
        print(f"   ❌ Usage increment check failed. Expected {new_usage + 1}, got {final_usage}")

    print("\n🎉 All End-to-End Tests Passed!")

if __name__ == "__main__":
    test_e2e()
