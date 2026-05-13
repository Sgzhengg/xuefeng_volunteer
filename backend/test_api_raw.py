#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试API原始响应"""
import requests
import json

API_URL = "http://localhost:8001/api/v1/recommendation/generate"

print("Testing API raw response\n")

test_data = {
    "rank": 50000,
    "score": 580,
    "province": "广东",
    "subject_type": "理科",
    "target_majors": ["计算机科学与技术"]
}

print("Request data:")
print(json.dumps(test_data, ensure_ascii=False, indent=2))
print()

try:
    response = requests.post(API_URL, json=test_data, timeout=10)

    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print()

    print("Raw Response:")
    print(response.text)
    print()

    try:
        json_response = response.json()
        print("Parsed JSON:")
        print(json.dumps(json_response, ensure_ascii=False, indent=2))
    except:
        print("Failed to parse as JSON")

except Exception as e:
    print(f"Exception: {e}")

print("\nTest completed")