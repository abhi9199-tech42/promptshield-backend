import requests
import sys

BASE_URL = "http://localhost:8003/api/v1"

def test_csp_header():
    print("Testing CSP Headers on /api/v1/health...")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        csp = resp.headers.get("Content-Security-Policy")
        
        if csp:
            print("✅ CSP Header Found:")
            print(f"   {csp}")
            if "script-src 'self'" in csp:
                print("   - Script execution restricted to 'self'")
            else:
                print("   ⚠️  CSP exists but might be weak")
        else:
            print("❌ CSP Header MISSING!")
            sys.exit(1)
            
    except Exception as e:
        print(f"Connection error: {e}")
        print("Make sure Docker is running.")

if __name__ == "__main__":
    test_csp_header()
