#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试端口8001 API是否正确返回紧急fallback数据"""
import requests
import json

API_URL = "http://localhost:8001/api/v1/recommendation/generate"

print("=== 测试端口8001 API紧急fallback ===\n")

test_data = {
    "rank": 50000,
    "score": 580,
    "province": "广东",
    "subject_type": "理科",
    "target_majors": ["计算机科学与技术"]
}

print("请求数据:")
print(json.dumps(test_data, ensure_ascii=False, indent=2))
print()

try:
    response = requests.post(API_URL, json=test_data, timeout=10)

    if response.status_code == 200:
        result = response.json()

        if result.get("code") == 0:
            recommendations = result.get("data", {}).get("recommendations", [])

            print(f"API成功响应，总推荐数: {len(recommendations)}")

            # 统计emergency_fallback数量
            emergency_count = 0
            for rec in recommendations:
                if rec.get("data_source") == "emergency_fallback":
                    emergency_count += 1

            print(f"emergency_fallback推荐数: {emergency_count}")

            if emergency_count > 0:
                print("SUCCESS: API正确返回紧急fallback数据")
                print("\n前5条emergency fallback推荐:")
                emergency_recs = [r for r in recommendations if r.get("data_source") == "emergency_fallback"]
                for i, rec in enumerate(emergency_recs[:5], 1):
                    uni = rec.get('university_name', '')
                    major = rec.get('major_name', '')
                    rank = rec.get('min_rank', 0)
                    print(f"{i}. {uni} - {major} (位次: {rank})")
            else:
                print("PROBLEM: API没有返回紧急fallback数据")
                print("\n前3条实际推荐:")
                for i, rec in enumerate(recommendations[:3], 1):
                    uni = rec.get('university_name', '')
                    major = rec.get('major_name', '')
                    source = rec.get('data_source', 'unknown')
                    rank = rec.get('min_rank', 0)
                    print(f"{i}. {uni} - {major} (位次: {rank}, 来源: {source})")
        else:
            print(f"API错误: {result}")
    else:
        print(f"HTTP错误: {response.status_code}")
        print(f"响应内容: {response.text}")

except Exception as e:
    print(f"请求异常: {e}")

print("\n=== 测试完成 ===")