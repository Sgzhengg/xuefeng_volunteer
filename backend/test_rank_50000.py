#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试位次50000的推荐结果"""
import requests
import json

print("测试位次50000的推荐结果...")

# 测试数据
test_data = {
    "province": "广东",
    "score": 600,
    "rank": 50000,
    "subject_type": "理科",
    "target_majors": ["计算机科学与技术"]
}

try:
    response = requests.post(
        "http://localhost:8000/api/v1/recommendation/generate",
        json=test_data,
        timeout=10
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            data = result.get("data", {})
            recommendations = data.get("recommendations", [])

            print(f"\n总推荐数: {len(recommendations)}")
            print(f"\n前20条推荐:")

            for i, rec in enumerate(recommendations[:20], 1):
                uni = rec.get("university_name", "未知")
                major = rec.get("major_name", "未知")
                rank = rec.get("min_rank", 0)
                tag = rec.get("tag", "")
                print(f"{i}. {uni} - {major} (位次: {rank:,}, 分类: {tag})")

            # 检查是否包含错误的高分院校
            high_level_unis = ["浙江大学", "中国科学技术大学", "北京大学", "清华大学", "复旦大学", "上海交通大学"]
            found_high_level = []
            for rec in recommendations:
                uni = rec.get("university_name", "")
                if any(h in uni for h in high_level_unis):
                    found_high_level.append(uni)

            if found_high_level:
                print(f"\n❌ 警告：仍然推荐高分院校: {set(found_high_level)}")
            else:
                print(f"\n✅ 正确：没有推荐高分院校")

            # 检查是否包含广东本地院校
            local_unis = ["广东工业大学", "广州大学", "汕头大学", "华南农业大学"]
            found_local = []
            for rec in recommendations:
                uni = rec.get("university_name", "")
                if any(l in uni for l in local_unis):
                    found_local.append(uni)

            if found_local:
                print(f"✅ 正确：包含广东本地院校: {set(found_local)}")
            else:
                print(f"⚠️  注意：未包含预期的广东本地院校")

        else:
            print(f"API返回错误: {result}")
    else:
        print(f"HTTP错误: {response.text}")

except Exception as e:
    print(f"请求失败: {e}")
