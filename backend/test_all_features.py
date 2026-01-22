import requests
import time
import os
import sys
import random
import string

# Configuration
BASE_URL = "http://localhost:8003"
API_V1 = f"{BASE_URL}/api/v1"
AUTH_URL = f"{API_V1}/auth"
PAYMENT_URL = f"{API_V1}/payment"
EXECUTE_URL = f"{API_V1}/execute"

# Generate random user
def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

TEST_EMAIL = f"test_user_{random_string()}@example.com"
TEST_PASSWORD = "TestPassword123!"
NEW_PASSWORD = "NewPassword456!"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def test_health():
    log("Testing Backend Health...")
    try:
        res = requests.get(BASE_URL)
        if res.status_code == 200:
            log("Backend is UP", "SUCCESS")
        else:
            log(f"Backend returned {res.status_code}", "ERROR")
            sys.exit(1)
    except Exception as e:
        log(f"Backend Unreachable: {e}", "CRITICAL")
        sys.exit(1)

def test_signup_login():
    log(f"Testing Signup for {TEST_EMAIL}...")
    
    # Signup
    signup_payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    res = requests.post(f"{AUTH_URL}/signup", json=signup_payload)
    if res.status_code == 200:
        log("Signup Successful", "SUCCESS")
    else:
        log(f"Signup Failed: {res.text}", "ERROR")
        sys.exit(1)

    # Login
    log("Testing Login...")
    # The endpoint is /api/v1/auth/login and it expects LoginRequest (json)
    login_payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    res = requests.post(f"{AUTH_URL}/login", json=login_payload)
    if res.status_code == 200:
        data = res.json()
        token = data.get("access_token")
        log("Login Successful, Token Received", "SUCCESS")
        return token
    else:
        log(f"Login Failed: {res.text} (URL: {AUTH_URL}/login)", "ERROR")
        sys.exit(1)

def test_profile(token):
    log("Testing User Profile...")
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{AUTH_URL}/me", headers=headers)
    if res.status_code == 200:
        data = res.json()
        if data["email"] == TEST_EMAIL:
            log(f"Profile Verified for {data['email']}", "SUCCESS")
            return data.get("api_key")
        else:
            log("Profile Email Mismatch", "ERROR")
    else:
        log(f"Profile Fetch Failed: {res.text}", "ERROR")

def test_api_execution(api_key):
    log("Testing API Execution (LLM Mock)...")
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    payload = {
        "text": "Hello, world!",
        "provider": "openai",
        "model": "gpt-4"
    }
    res = requests.post(EXECUTE_URL, json=payload, headers=headers)
    if res.status_code == 200:
        data = res.json()
        if "analysis" in data and "suggestions" in data:
            log("API Execution Successful", "SUCCESS")
        else:
            log("API Response Invalid Format", "WARNING")
    else:
        log(f"API Execution Failed: {res.text}", "ERROR")

def test_change_password(token):
    log("Testing Change Password...")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "old_password": TEST_PASSWORD,
        "new_password": NEW_PASSWORD
    }
    res = requests.post(f"{AUTH_URL}/change-password", json=payload, headers=headers)
    if res.status_code == 200:
        log("Password Changed Successfully", "SUCCESS")
    else:
        log(f"Change Password Failed: {res.text}", "ERROR")
        sys.exit(1)

    # Verify New Password Login
    log("Verifying Login with New Password...")
    login_payload = {"email": TEST_EMAIL, "password": NEW_PASSWORD}
    res = requests.post(f"{AUTH_URL}/login", json=login_payload)
    if res.status_code == 200:
        log("Login with New Password Successful", "SUCCESS")
    else:
        log(f"Login with New Password Failed: {res.text}", "ERROR")

def test_payment(token):
    log("Testing Payment QR Generation...")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"plan_id": "monthly"}
    res = requests.post(f"{PAYMENT_URL}/create", json=payload, headers=headers)
    if res.status_code == 200:
        data = res.json()
        if "qr_code" in data and "payment_id" in data:
            log("Payment QR Generated", "SUCCESS")
        else:
            log("Payment Response Invalid", "ERROR")
    else:
        log(f"Payment Request Failed: {res.text}", "ERROR")

def test_forgot_password_flow():
    log("Testing Forgot Password Flow...")
    # 1. Request Reset
    res = requests.post(f"{AUTH_URL}/forgot-password", json={"email": TEST_EMAIL})
    if res.status_code == 200:
        log("Forgot Password Email Sent (Mocked)", "SUCCESS")
    else:
        log(f"Forgot Password Request Failed: {res.text}", "ERROR")

def main():
    log("=== STARTING COMPREHENSIVE SYSTEM TEST ===")
    test_health()
    
    # Auth Flow
    token = test_signup_login()
    api_key = test_profile(token)
    
    if api_key:
        test_api_execution(api_key)
    
    test_payment(token)
    
    # Change Password Flow
    test_change_password(token)
    
    # Forgot Password Flow
    test_forgot_password_flow()
    
    log("=== ALL TESTS COMPLETED ===")

if __name__ == "__main__":
    main()
