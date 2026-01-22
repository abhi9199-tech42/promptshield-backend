
import time
import os
import json
from passlib.context import CryptContext
from cryptography.fernet import Fernet

# --- 1. Benchmark Argon2 ---
print("--- Benchmarking Argon2 ---")

# Current Settings
pwd_context_current = CryptContext(
    schemes=["argon2"], 
    deprecated="auto",
    argon2__time_cost=12,
    argon2__memory_cost=65536,
    argon2__parallelism=1,
)

# Proposed Settings
pwd_context_proposed = CryptContext(
    schemes=["argon2"], 
    deprecated="auto",
    argon2__time_cost=2,      # Reduced from 12
    argon2__memory_cost=65536,
    argon2__parallelism=1,
)

start = time.time()
pwd_context_current.hash("password123")
duration_current = time.time() - start
print(f"Current Settings (t=12, m=64MB): {duration_current:.4f} seconds per hash")

start = time.time()
pwd_context_proposed.hash("password123")
duration_proposed = time.time() - start
print(f"Proposed Settings (t=2, m=64MB):  {duration_proposed:.4f} seconds per hash")
print(f"Speedup: {duration_current / duration_proposed:.2f}x")


# --- 2. Benchmark SecureStorage (Simulated) ---
print("\n--- Benchmarking SecureStorage (File I/O) ---")

KEY_FILE = "test_secret.key"
DATA_FILE = "test_secure_customers.enc"
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def write_data(data):
    json_data = json.dumps(data)
    encrypted_data = cipher_suite.encrypt(json_data.encode('utf-8'))
    with open(DATA_FILE, "wb") as f:
        f.write(encrypted_data)

def read_data():
    with open(DATA_FILE, "rb") as f:
        encrypted_data = f.read()
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    return json.loads(decrypted_data.decode('utf-8'))

# Simulate 1000 users
large_data = {f"user{i}@example.com": {"usage": i, "data": "x"*100} for i in range(1000)}

# Write once to setup
write_data(large_data)

# Measure update time (Read -> Modify -> Write)
start = time.time()
current_data = read_data()
current_data["user500@example.com"]["usage"] += 1
write_data(current_data)
duration_io = time.time() - start

print(f"SecureStorage update time (1000 users): {duration_io:.4f} seconds")
print("(This happens on every usage increment if using SecureStorage)")

# Cleanup
if os.path.exists(KEY_FILE): os.remove(KEY_FILE)
if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
