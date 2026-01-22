
import requests
import json
import os
import sys

# Define base URL
BASE_URL = "http://127.0.0.1:8001"

# Define API Key
API_KEY = "sk-ps-7E-BH9GDWiV-JjG5lteIXg"

# Sample prompt designed to trigger compression heuristics and potential PTIL compression
# It contains politeness markers, passive voice, and redundant role definitions.
PROMPT_TEXT = """
Please act as a senior software engineer. I would like you to write a Python script that calculates the Fibonacci sequence.
The script should be written in a clean and efficient way.
Could you also please include comments to explain the code?
The code is being used for a student project.
"""

def test_optimize_endpoint():
    print("Testing /api/v1/optimize endpoint...")
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": PROMPT_TEXT,
        "model": "gpt-4o-mini",
        "format": "verbose"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/optimize", headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("Status: SUCCESS")
            print("-" * 40)
            print(f"Raw Text:\n{data['raw_text']}")
            print("-" * 40)
            print(f"Compressed Text:\n{data['compressed_text']}")
            print("-" * 40)
            print("Token Metrics:")
            tokens = data['tokens']
            print(f"  Raw Tokens:        {tokens['raw_tokens']}")
            print(f"  Compressed Tokens: {tokens['compressed_tokens']}")
            print(f"  Savings:           {tokens['savings']}")
            print(f"  Savings Ratio:     {tokens['savings_ratio']:.2%}")
            print("-" * 40)
            print("Suggestions:")
            for suggestion in data['suggestions']:
                print(f"  - {suggestion}")
        else:
            print(f"Status: FAILED ({response.status_code})")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def test_execute_endpoint():
    print("\nTesting /api/v1/execute endpoint (Optimization Check)...")
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Using 'gemini' provider but we might fail if no valid provider key is supplied.
    # However, we are mainly checking if the pipeline runs.
    # To avoid actual LLM failure if key is missing, we might see an error, but we want to see if it gets that far.
    
    payload = {
        "text": PROMPT_TEXT,
        "provider": "gemini",
        "model": "gemini-1.5-flash",
        "provider_key": "dummy_key_for_test" # This will fail at LLM stage but should pass optimization
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/execute", headers=headers, json=payload)
        
        # We expect a 200 if the key was valid, or a specific error message if invalid key.
        # But for this test script, we want to see the compression part if possible.
        # Since 'execute' runs compression first, if it fails at LLM, we might not see the compression result 
        # unless we catch the error or if the error response includes details.
        # Actually, the 'execute' endpoint in app.py returns ExecuteResult.
        # If LLM fails, it raises an exception or returns an error string in 'output'.
        # Let's see llm.py: generate() returns a string (error message) if key is invalid.
        # It does NOT raise an exception for invalid key configuration usually, just returns error text.
        
        if response.status_code == 200:
            data = response.json()
            print("Status: SUCCESS")
            print(f"LLM Output: {data['output']}")
            print(f"Compressed Text used: {data['compressed_text']}")
        else:
            print(f"Status: FAILED ({response.status_code})")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_optimize_endpoint()
    test_execute_endpoint()
