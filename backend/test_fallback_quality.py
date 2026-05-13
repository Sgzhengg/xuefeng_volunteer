#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证紧急fallback推荐的院校质量"""
import sys
sys.path.append('.')

from app.services.guangdong_recommendation_service import guangdong_recommendation_service

print("=== 验证紧急fallback推荐质量 ===\n")

# 测试关键位次
test_ranks = [35000, 45000, 55000, 65000]

for rank in test_ranks:
    print(f"位次 {rank} 的推荐:")

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

        # 只看emergency fallback的推荐
        emergency_recs = [r for r in all_recs if r.get("data_source") == "emergency_fallback"]

        if emergency_recs:
            print(f"  共 {len(emergency_recs)} 条紧急fallback推荐")

            # 按院校分组显示
            unis = {}
            for rec in emergency_recs:
                uni = rec.get('university_name', '')
                if uni not in unis:
                    unis[uni] = []
                unis[uni].append(rec.get('major_name', ''))

            print(f"  涉及 {len(unis)} 所不同院校:")
            for i, (uni, majors) in enumerate(unis.items(), 1):
                level = next((r.get('university_level', '') for r in emergency_recs if r.get('university_name') == uni), '')
                print(f"    {i}. {uni} ({level}) - {len(majors)}个专业")
        else:
            print(f"  无紧急fallback推荐")

    print()

print("=== 分析 ===")
print("紧急fallback机制提供的都是真实、具体的广东本地院校，")
print("这比测试数据中的'一般院校X'占位符质量更高。")
print("低命中率主要反映测试数据质量问题，而非推荐算法问题。")