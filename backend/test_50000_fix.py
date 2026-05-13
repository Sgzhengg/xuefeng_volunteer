#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重点测试50000位次的修复效果"""
import sys
sys.path.append('.')

from app.services.guangdong_recommendation_service import guangdong_recommendation_service

print("重点测试50000位次的修复效果\n")

# 测试之前有问题的50000位次
result = guangdong_recommendation_service.recommend_with_fallback(
    user_rank=50000,
    province="广东",
    subject_type="理科",
    target_majors=["计算机科学与技术"]
)

if result.get("success"):
    recommendations = result.get("data", {})

    print("50000位次推荐结果:")
    for category in ["冲刺", "稳妥", "保底"]:
        items = recommendations.get(category, [])
        print(f"\n{category} ({len(items)}条):")
        for i, rec in enumerate(items[:5], 1):
            uni = rec.get("university_name", "")
            major = rec.get("major_name", "")
            rank = rec.get("min_rank", 0)
            prov = rec.get("province", "")
            print(f"  {i}. {uni} - {major} (位次: {rank:,}, 省份: {prov})")

    # 验证修复效果
    print("\n验证修复效果:")
    all_recs = []
    for category in ["冲刺", "稳妥", "保底"]:
        all_recs.extend(recommendations.get(category, []))

    # 1. 检查是否包含浙江大学等高分院校（不应该）
    high_unis = ["浙江大学", "中国科学技术大学", "北京大学", "清华大学"]
    found_high = [r.get("university_name") for r in all_recs if any(h in r.get("university_name", "") for h in high_unis)]

    if found_high:
        print(f"X 仍然包含高分院校: {set(found_high)}")
    else:
        print(f"√ 正确：没有包含浙江大学等高分院校")

    # 2. 检查是否包含广东本地院校（应该包含）
    local_unis = ["广东工业大学", "广州大学", "华南农业大学", "汕头大学", "深圳大学"]
    found_local = [r.get("university_name") for r in all_recs if any(l in r.get("university_name", "") for l in local_unis)]

    if found_local:
        print(f"√ 正确：包含广东本地院校: {set(found_local)}")
    else:
        print(f"X 注意：未包含预期的广东本地院校")

    # 3. 检查位次范围是否合理
    ranks = [r.get("min_rank", 0) for r in all_recs]
    if ranks:
        min_rec_rank = min(ranks)
        max_rec_rank = max(ranks)
        print(f"√ 位次范围: {min_rec_rank:,} - {max_rec_rank:,}")

        if 40000 <= min_rec_rank <= 60000 and 40000 <= max_rec_rank <= 60000:
            print(f"√ 正确：位次范围合理")
        else:
            print(f"X 警告：位次范围不合理")

    # 4. 统计省份分布
    provinces = {}
    for rec in all_recs:
        prov = rec.get("province", "unknown")
        provinces[prov] = provinces.get(prov, 0) + 1
    print(f"√ 省份分布: {provinces}")

else:
    print(f"API调用失败: {result.get('error')}")