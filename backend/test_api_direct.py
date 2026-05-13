#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Direct API test"""
import sys
sys.path.append('.')

from app.services.guangdong_recommendation_service import guangdong_recommendation_service

print("Testing recommendation service directly...")
result = guangdong_recommendation_service.recommend_with_fallback(
    user_rank=10000,
    province="广东",
    subject_type="理科",
    target_majors=["计算机科学与技术"]
)

print(f"Result type: {type(result)}")
print(f"Result keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
print(f"Success: {result.get('success') if isinstance(result, dict) else 'N/A'}")

if result.get('success'):
    data = result.get('data', {})
    print(f"Data keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
    for category in ["冲刺", "稳妥", "保底"]:
        items = data.get(category, [])
        print(f"  {category}: {len(items)} items")
        if items:
            print(f"    First item: {items[0]}")
