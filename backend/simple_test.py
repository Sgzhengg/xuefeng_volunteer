#!/usr/bin/env python3
import requests
import json
import os

url = "http://localhost:8000/api/v1/chat"
request_data = {
    "message": "test",
    "context": {
        "province": "广东",
        "score": 620
    }
}

print("Testing chat API...")
print(f"URL: {url}")
print(f"Request: {json.dumps(request_data, ensure_ascii=False)}")

try:
    response = requests.post(url, json=request_data, timeout=60)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            ai_response = result.get("response", "")
            print(f"\nAI Response: {ai_response[:200]}")
            print("\nAPI working!")
        else:
            print(f"API returned failure")
    else:
        print(f"HTTP error: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")

# Check API key
api_key = os.getenv("OPENROUTER_API_KEY")
if api_key:
    print(f"\nAPI Key found: {api_key[:10]}...")
else:
    print("\nNo API key found")
    print("Set it with: export OPENROUTER_API_KEY='your-key'")
