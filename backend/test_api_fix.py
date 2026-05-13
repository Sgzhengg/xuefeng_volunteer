#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过API接口验证紧急fallback机制"""
import requests
import json

API_URL = "http://localhost:8000/api/v1/recommendation/generate"

print("通过API接口测试紧急fallback机制...")

# 测试用例：广东50000位次（关键问题段）
test_data = {
    "user_rank": 50000,
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

            print(f"✅ API调用成功")
            print(f"总推荐数: {len(all_recs)}")

            # 显示前5条推荐
            print("\n前5条推荐:")
            for i, rec in enumerate(all_recs[:5], 1):
                uni = rec.get('university_name', '')
                major = rec.get('major_name', '')
                rank = rec.get('min_rank', 0)
                print(f"{i}. {uni} - {major} (位次: {rank})")

            # 检查是否包含不合适的高分院校
            high_unis = ['浙江大学', '北京大学', '清华大学', '中国科学技术大学', '复旦大学', '上海交通大学']
            found_high = []
            for rec in all_recs:
                uni = rec.get('university_name', '')
                if any(h in uni for h in high_unis):
                    found_high.append(uni)

            # 检查是否包含广东本地院校
            local_unis = ['广东工业大学', '广州大学', '华南农业大学', '汕头大学', '深圳大学']
            found_local = []
            for rec in all_recs:
                uni = rec.get('university_name', '')
                if any(l in uni for l in local_unis):
                    found_local.append(uni)

            print(f"\n验证结果:")
            if found_high:
                print(f"❌ 发现不合适的高分院校: {set(found_high)}")
            else:
                print(f"✅ 没有不合适的高分院校")

            if found_local:
                print(f"✅ 包含广东本地院校: {set(found_local)}")
            else:
                print(f"⚠️ 未包含预期的广东本地院校")

        else:
            print(f"❌ API调用失败: {result.get('error')}")
    else:
        print(f"❌ HTTP错误: {response.status_code}")

except Exception as e:
    print(f"❌ 请求异常: {e}")

print("\n测试完成")