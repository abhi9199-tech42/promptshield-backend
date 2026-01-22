import requests
import sys

def get_ngrok_url():
    try:
        # Try the default ngrok API port
        response = requests.get("http://localhost:4040/api/tunnels", timeout=2)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get("tunnels", [])
            if tunnels:
                # Prefer HTTPS
                public_url = next((t["public_url"] for t in tunnels if t["public_url"].startswith("https")), None)
                if not public_url and tunnels:
                    public_url = tunnels[0]["public_url"]
                
                if public_url:
                    print(f"NGROK_URL_FOUND: {public_url}")
                    return public_url
    except Exception as e:
        print(f"NGROK_NOT_DETECTED: {e}")
    
    return None

if __name__ == "__main__":
    get_ngrok_url()
