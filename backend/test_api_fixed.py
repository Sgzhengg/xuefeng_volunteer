#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test fixed API"""
import requests
import json

print("Testing fixed recommendation API...")

# Test data
test_data = {
    "province": "广东",
    "score": 650,
    "rank": 10000,
    "subject_type": "理科",
    "target_majors": ["计算机科学与技术"]
}

try:
    response = requests.post(
        "http://localhost:8000/api/v1/recommendation/generate",
        json=test_data,
        timeout=10
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    result = response.json()
    print(f"Response Keys: {result.keys()}")

    if result.get("code") == 0:
        data = result.get("data", {})
        recommendations = data.get("recommendations", [])
        summary = data.get("summary", {})

        print(f"API SUCCESS!")
        print(f"  Total Recommendations: {summary.get('total', 0)}")
        print(f"  chong: {summary.get('chong', 0)}")
        print(f"  wen: {summary.get('wen', 0)}")
        print(f"  bao: {summary.get('bao', 0)}")

        if recommendations:
            print(f"  First recommendation: {recommendations[0].get('university_name')} - {recommendations[0].get('major_name')}")
    else:
        print(f"API FAILED: {result.get('message')}")
        print(f"Error details: {result}")

except Exception as e:
    print(f"REQUEST FAILED: {e}")
