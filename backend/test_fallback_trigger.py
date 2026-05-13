#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试紧急fallback机制是否正确触发"""
import sys
sys.path.append('.')

from app.services.guangdong_recommendation_service import guangdong_recommendation_service

print("=== 测试紧急fallback触发条件 ===\n")

# 测试用例：广东30001-70000位次段
test_cases = [
    {"rank": 35000, "province": "广东", "subject_type": "理科", "target_majors": ["计算机科学与技术"]},
    {"rank": 50000, "province": "广东", "subject_type": "理科", "target_majors": ["计算机科学与技术"]},
    {"rank": 65000, "province": "广东", "subject_type": "理科", "target_majors": ["计算机科学与技术"]},
]

for i, test_case in enumerate(test_cases, 1):
    rank = test_case["rank"]
    province = test_case["province"]

    print(f"{i}. 测试位次 {rank}, 省份 {province}:")
    print(f"   触发条件: province == '广东' and 30001 <= {rank} <= 70000")
    print(f"   条件满足: {province == '广东' and 30001 <= rank <= 70000}")

    # 调用推荐服务
    result = guangdong_recommendation_service.recommend_with_fallback(
        user_rank=rank,
        province=province,
        subject_type="理科",
        target_majors=["计算机科学与技术"]
    )

    if result.get("success"):
        recommendations = result.get("data", {})
        all_recs = []
        for category in ["冲刺", "稳妥", "保底"]:
            all_recs.extend(recommendations.get(category, []))

        # 检查是否有emergency_fallback数据源
        emergency_count = 0
        for rec in all_recs:
            if rec.get("data_source") == "emergency_fallback":
                emergency_count += 1

        print(f"   总推荐数: {len(all_recs)}")
        print(f"   emergency_fallback推荐数: {emergency_count}")

        if emergency_count > 0:
            print(f"   SUCCESS: 紧急fallback机制已触发")
            # 显示前3条emergency fallback推荐
            print(f"   前3条emergency fallback推荐:")
            for j, rec in enumerate([r for r in all_recs if r.get("data_source") == "emergency_fallback"][:3], 1):
                uni = rec.get('university_name', '')
                major = rec.get('major_name', '')
                rec_rank = rec.get('min_rank', 0)
                print(f"   {j}. {uni} - {major} (位次: {rec_rank})")
        else:
            print(f"   PROBLEM: 紧急fallback机制未触发")
            # 显示实际推荐的前3条
            print(f"   实际推荐前3条:")
            for j, rec in enumerate(all_recs[:3], 1):
                uni = rec.get('university_name', '')
                major = rec.get('major_name', '')
                source = rec.get('data_source', 'unknown')
                rec_rank = rec.get('min_rank', 0)
                print(f"   {j}. {uni} - {major} (位次: {rec_rank}, 来源: {source})")
    else:
        print(f"   ERROR: {result.get('error')}")

    print()

print("=== 测试完成 ===")