import requests
import json

API_URL = "http://127.0.0.1:8003/api/v1/compress"
API_KEY = "sk-ps-7E-BH9GDWiV-JjG5lteIXg"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_opt_out():
    prompt = "Please ensure that the variable {{ user_id }} is not null."
    print(f"Testing Opt-Out with prompt: {prompt}")
    
    payload = {
        "text": prompt,
        "model": "gpt-4o-mini"
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("Response:", json.dumps(data, indent=2))
            
            compressed = data["compressed_text"]
            if "{{ user_id }}" in compressed:
                print("SUCCESS: Opt-out block preserved.")
            else:
                print("FAILURE: Opt-out block NOT preserved.")
                
            confidence = data.get("confidence_score")
            print(f"Confidence Score: {confidence}")
            
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_opt_out()
