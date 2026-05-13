#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过API接口验证紧急fallback机制 - 简化版"""
import requests
import json

API_URL = "http://localhost:8000/api/v1/recommendation/generate"

print("Testing emergency fallback via API...")

# Test case: Guangdong rank 50000
test_data = {
    "rank": 50000,
    "province": "广东",
    "subject_type": "理科",
    "target_majors": ["计算机科学与技术"]
}

try:
    response = requests.post(API_URL, json=test_data, timeout=30)

    if response.status_code == 200:
        result = response.json()

        if result.get("success"):
            recommendations = result.get("data", {})
            all_recs = []
            for category in ["冲刺", "稳妥", "保底"]:
                all_recs.extend(recommendations.get(category, []))

            print(f"API Success! Total recommendations: {len(all_recs)}")

            # Show first 5 recommendations
            print("\nFirst 5 recommendations:")
            for i, rec in enumerate(all_recs[:5], 1):
                uni = rec.get('university_name', '')
                major = rec.get('major_name', '')
                rank = rec.get('min_rank', 0)
                print(f"{i}. {uni} - {major} (rank: {rank})")

            # Check for high-rank universities (should NOT appear)
            high_unis = ['浙江大学', '北京大学', '清华大学', '中国科学技术大学']
            found_high = []
            for rec in all_recs:
                uni = rec.get('university_name', '')
                if any(h in uni for h in high_unis):
                    found_high.append(uni)

            # Check for Guangdong local universities (SHOULD appear)
            local_unis = ['华南农业大学', '汕头大学', '广东工业大学', '广州大学', '深圳大学']
            found_local = []
            for rec in all_recs:
                uni = rec.get('university_name', '')
                if any(l in uni for l in local_unis):
                    found_local.append(uni)

            print(f"\nValidation Results:")
            if found_high:
                print(f"PROBLEM: Found high-rank universities: {set(found_high)}")
            else:
                print(f"GOOD: No inappropriate high-rank universities")

            if found_local:
                print(f"GOOD: Contains Guangdong local universities: {set(found_local)}")
            else:
                print(f"WARNING: Missing expected Guangdong local universities")

        else:
            print(f"API Error: {result.get('error')}")
    else:
        print(f"HTTP Error: {response.status_code}")

except Exception as e:
    print(f"Exception: {e}")

print("\nTest completed")