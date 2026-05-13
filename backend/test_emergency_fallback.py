#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速验证紧急fallback机制是否生效"""
import requests
import json

API_URL = "http://localhost:8001/api/v1/recommendation/generate"

print("快速验证紧急fallback机制\n")

# 测试关键问题段：广东50000位次
test_cases = [
    {"rank": 50000, "score": 580, "province": "广东", "subject_type": "理科", "target_majors": ["计算机科学与技术"]},
    {"rank": 45000, "score": 590, "province": "广东", "subject_type": "理科", "target_majors": ["计算机科学与技术"]},
    {"rank": 60000, "score": 570, "province": "广东", "subject_type": "理科", "target_majors": ["计算机科学与技术"]},
]

for i, test_case in enumerate(test_cases, 1):
    rank = test_case["rank"]
    print(f"{i}. 测试位次 {rank}:")

    try:
        response = requests.post(API_URL, json=test_case, timeout=10)

        if response.status_code == 200:
            result = response.json()

            if result.get("success"):
                recommendations = result.get("data", {})
                all_recs = []
                for category in ["冲刺", "稳妥", "保底"]:
                    all_recs.extend(recommendations.get(category, []))

                if all_recs:
                    # 显示前3条推荐
                    print(f"   总推荐: {len(all_recs)}条")
                    print("   前3条推荐:")

                    for j, rec in enumerate(all_recs[:3], 1):
                        uni = rec.get('university_name', '')
                        major = rec.get('major_name', '')
                        rec_rank = rec.get('min_rank', 0)
                        print(f"   {j}. {uni} - {major} (位次: {rec_rank})")

                    # 检查是否包含合适的本地院校
                    local_unis = ['广东工业大学', '广州大学', '华南农业大学', '汕头大学', '深圳大学']
                    found_local = []
                    for rec in all_recs:
                        uni = rec.get('university_name', '')
                        if any(l in uni for l in local_unis):
                            found_local.append(uni)

                    if found_local:
                        print(f"   OK Contains local universities: {set(found_local)}")
                    else:
                        print(f"   WARNING Missing expected local universities")

                    # 检查是否有不合适的高分院校
                    high_unis = ['浙江大学', '北京大学', '清华大学', '中国科学技术大学']
                    found_high = []
                    for rec in all_recs:
                        uni = rec.get('university_name', '')
                        if any(h in uni for h in high_unis):
                            found_high.append(uni)

                    if found_high:
                        print(f"   PROBLEM Found inappropriate high-rank universities: {set(found_high)}")
                    else:
                        print(f"   OK No inappropriate high-rank universities")
                else:
                    print("   ERROR No recommendations")
            else:
                print(f"   ERROR API error: {result.get('error')}")
        else:
            print(f"   ERROR HTTP error: {response.status_code}")

    except Exception as e:
        print(f"   ERROR Exception: {e}")

    print()

print("快速验证完成")