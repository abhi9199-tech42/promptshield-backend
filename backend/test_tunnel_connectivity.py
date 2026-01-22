import os
import requests
import sys
from dotenv import load_dotenv

# Load env directly to see what's on disk
load_dotenv()

frontend_url = os.getenv("FRONTEND_URL")
print(f"Checking FRONTEND_URL from .env: {frontend_url}")

if not frontend_url:
    print("Error: FRONTEND_URL not set in .env")
    sys.exit(1)

if "localhost" in frontend_url:
    print("Warning: FRONTEND_URL is still localhost. Tunnel might not be configured in .env yet.")

try:
    print(f"Sending request to {frontend_url}...")
    response = requests.get(frontend_url, timeout=30)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! Tunnel is reachable.")
        # Check if it looks like a Next.js app
        if "<!DOCTYPE html>" in response.text or "next" in response.text:
             print("Content verified: Looks like a web application.")
        else:
             print("Warning: Content does not look like standard HTML. First 100 chars:")
             print(response.text[:100])
    else:
        print("Failed to reach frontend via tunnel.")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Exception during request: {e}")
    print("Possible causes: Tunnel not running, Frontend not running on port 3000, or network issues.")
