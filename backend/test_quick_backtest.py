#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速回溯测试验证修复效果"""
import sys
sys.path.append('.')

from app.services.guangdong_recommendation_service import guangdong_recommendation_service

print("快速回溯测试验证修复效果\n")

# 测试用例：覆盖关键位次段
test_cases = [
    {"rank": 5000, "expected_contains": ["中山大学", "华南理工大学"], "expected_not_contains": ["北京大学", "清华大学"]},
    {"rank": 25000, "expected_contains": ["暨南大学", "华南师范大学"], "expected_not_contains": ["北京大学", "浙江大学"]},
    {"rank": 50000, "expected_contains": ["华南农业大学", "广州大学"], "expected_not_contains": ["北京大学", "中国科学技术大学"]},
    {"rank": 100000, "expected_contains": ["广东工业大学", "汕头大学"], "expected_not_contains": ["清华大学", "复旦大学"]},
]

total_tests = len(test_cases)
passed_tests = 0

for i, test_case in enumerate(test_cases, 1):
    rank = test_case["rank"]
    expected_contains = test_case["expected_contains"]
    expected_not_contains = test_case["expected_not_contains"]

    print(f"测试 {i}/{total_tests}: 位次 {rank:,}")

    # 调用推荐服务
    result = guangdong_recommendation_service.recommend_with_fallback(
        user_rank=rank,
        province="广东",
        subject_type="理科",
        target_majors=["计算机科学与技术"]
    )

    if result.get("success"):
        recommendations = result.get("data", {})
        all_recs = []
        for category in ["冲刺", "稳妥", "保底"]:
            all_recs.extend(recommendations.get(category, []))

        # 获取推荐的院校名称列表
        uni_list = [rec.get("university_name", "") for rec in all_recs]

        # 检查是否包含期望的院校
        contains_ok = True
        for expected in expected_contains:
            if expected not in uni_list:
                print(f"  ❌ 缺少期望院校: {expected}")
                contains_ok = False

        # 检查是否包含不应该出现的院校
        not_contains_ok = True
        for not_expected in expected_not_contains:
            if not_expected in uni_list:
                print(f"  ❌ 错误推荐高分院校: {not_expected}")
                not_contains_ok = False

        if contains_ok and not_contains_ok:
            print(f"  ✅ 通过")
            passed_tests += 1
        else:
            print(f"  推荐院校: {uni_list[:10]}")
    else:
        print(f"  ❌ API调用失败: {result.get('error')}")

    print()

print(f"测试结果: {passed_tests}/{total_tests} 通过 ({passed_tests/total_tests*100:.1f}%)")

if passed_tests == total_tests:
    print("🎉 所有测试通过！修复成功！")
else:
    print(f"⚠️  {total_tests - passed_tests} 个测试失败，需要进一步调整")