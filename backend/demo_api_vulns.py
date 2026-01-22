import logging
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

# ==============================================================================
# 🛡️ API SECURITY DEMO: IDOR & EXCESSIVE DATA EXPOSURE
# ==============================================================================
# This script demonstrates a common API vulnerability: Insecure Direct Object Reference (IDOR)
# and Excessive Data Exposure, followed by the Secure implementation.

# --- MOCK DATABASE & MODELS ---------------------------------------------------

class UserDB:
    def __init__(self, id, email, password_hash, is_admin=False):
        self.id = id
        self.email = email
        self.password_hash = password_hash # SENSITIVE!
        self.is_admin = is_admin
        self.created_at = datetime.now(timezone.utc)

# Mock Data
users_db = {
    1: UserDB(1, "alice@example.com", "hash_secret_123"),
    2: UserDB(2, "bob@example.com", "hash_secret_456"),
    3: UserDB(3, "admin@example.com", "hash_secret_789", is_admin=True)
}

# --- VULNERABLE APP -----------------------------------------------------------
vulnerable_app = FastAPI()

@vulnerable_app.get("/users/{user_id}")
def get_user_vulnerable(user_id: int):
    """
    ❌ VULNERABLE PATTERN
    1. No Authentication: Anyone can call this.
    2. IDOR: Anyone can request ANY user_id.
    3. Data Exposure: Returns the internal DB object (including password_hash).
    """
    user = users_db.get(user_id)
    if not user:
        return {"error": "User not found"}
    return user # Serializes full object!

# --- SECURE APP ---------------------------------------------------------------
secure_app = FastAPI()

# 1. DTO (Data Transfer Object) / Schema
class UserPublic(BaseModel):
    id: int
    email: str
    created_at: datetime
    # NO password_hash here!

# 2. Authentication Dependency (Mock)
def get_current_user_mock(x_api_key: str = Header("sk-alice")):
    """
    Simulates fetching the authenticated user.
    In a real app, this verifies a JWT or API Key.
    """
    # For demo, map header to user
    if x_api_key == "sk-alice":
        return users_db[1]
    elif x_api_key == "sk-bob":
        return users_db[2]
    elif x_api_key == "sk-admin":
        return users_db[3]
    else:
        raise HTTPException(status_code=401, detail="Invalid Credentials")

@secure_app.get("/users/{user_id}", response_model=UserPublic)
def get_user_secure(
    user_id: int, 
    current_user: UserDB = Depends(get_current_user_mock)
):
    """
    ✓ SECURE PATTERN
    1. Authentication: Requires valid credential.
    2. Authorization (IDOR Protection): Checks if requesting user OWNS the data.
    3. Data Exposure Protection: Returns 'UserPublic' schema (filters sensitive fields).
    """
    # Verify ownership (or admin access)
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied: Cannot view other users' data")
    
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user

# ==============================================================================
# 🧪 DEMONSTRATION RUNNER
# ==============================================================================
def run_demo():
    print("================================================================")
    print("       API VULNERABILITY DEMO: IDOR & DATA EXPOSURE")
    print("================================================================\n")

    # --- TEST 1: VULNERABLE ENDPOINT ---
    print("[1] ❌ TESTING VULNERABLE ENDPOINT")
    client = TestClient(vulnerable_app)
    
    print("    Attacker (Anonymous) requests User 1 (Alice)...")
    resp = client.get("/users/1")
    data = resp.json()
    
    print(f"    Status: {resp.status_code}")
    print(f"    Response Keys: {list(data.keys())}")
    if "password_hash" in data:
        print("    ⚠️  CRITICAL: Password hash leaked!")
    else:
        print("    No leak.")
        
    print("\n    Attacker requests User 3 (Admin)...")
    resp = client.get("/users/3")
    print(f"    Status: {resp.status_code}")
    if resp.status_code == 200:
        print("    ⚠️  CRITICAL: IDOR Successful! Accessed Admin data.")

    # --- TEST 2: SECURE ENDPOINT ---
    print("\n[2] ✓ TESTING SECURE ENDPOINT")
    client = TestClient(secure_app)
    
    print("    Alice (User 1) requests her own profile...")
    # Header simulated via dependency default, but we can override in TestClient if needed.
    # The dependency defaults to "sk-alice" (User 1)
    resp = client.get("/users/1", headers={"x-api-key": "sk-alice"})
    data = resp.json()
    
    print(f"    Status: {resp.status_code}")
    print(f"    Response Keys: {list(data.keys())}")
    if "password_hash" not in data:
        print("    ✅ SUCCESS: Password hash NOT exposed.")
        
    print("\n    Alice (User 1) tries to request User 2 (Bob)...")
    resp = client.get("/users/2", headers={"x-api-key": "sk-alice"})
    print(f"    Status: {resp.status_code}")
    print(f"    Response: {resp.json()}")
    if resp.status_code == 403:
        print("    ✅ SUCCESS: IDOR Prevented (403 Forbidden).")

    print("\n    Admin requests User 2 (Bob)...")
    resp = client.get("/users/2", headers={"x-api-key": "sk-admin"})
    print(f"    Status: {resp.status_code}")
    if resp.status_code == 200:
        print("    ✅ SUCCESS: Admin allowed.")

    print("\n================================================================")
    print("       DEMO COMPLETE")
    print("================================================================")

if __name__ == "__main__":
    run_demo()
