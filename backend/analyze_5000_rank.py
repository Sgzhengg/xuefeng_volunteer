#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深入分析5000位次推荐问题"""
import sys
sys.path.append('.')

from app.services.guangdong_recommendation_service import guangdong_recommendation_service

print("深入分析5000位次推荐问题\n")

# 调用推荐服务
result = guangdong_recommendation_service.recommend_with_fallback(
    user_rank=5000,
    province="广东",
    subject_type="理科",
    target_majors=["计算机科学与技术"]
)

if result.get("success"):
    recommendations = result.get("data", {})

    print("推荐结果:")
    for category in ["冲刺", "稳妥", "保底"]:
        items = recommendations.get(category, [])
        print(f"\n{category} ({len(items)}条):")
        for i, rec in enumerate(items[:5], 1):
            uni = rec.get("university_name", "")
            major = rec.get("major_name", "")
            rank = rec.get("min_rank", 0)
            prov = rec.get("province", "")
            print(f"  {i}. {uni} - {major} (位次: {rank:,}, 省份: {prov})")

    # 分析问题
    print("\n问题分析:")
    all_recs = []
    for category in ["冲刺", "稳妥", "保底"]:
        all_recs.extend(recommendations.get(category, []))

    # 检查省份分布
    provinces = {}
    for rec in all_recs:
        prov = rec.get("province", "unknown")
        provinces[prov] = provinces.get(prov, 0) + 1
    print(f"省份分布: {provinces}")

    # 检查是否包含广东本地院校
    guangdong_unis = [r for r in all_recs if r.get("province") == "广东"]
    print(f"广东院校数量: {len(guangdong_unis)}")

    if guangdong_unis:
        print("广东院校示例:")
        for rec in guangdong_unis[:5]:
            print(f"  - {rec.get('university_name')} - {rec.get('major_name')} (位次: {rec.get('min_rank', 0):,})")

    # 检查是否包含不合理的高分院校
    high_rank_unis = []
    for rec in all_recs:
        rank = rec.get("min_rank", 0)
        if rank < 1000:  # 位次小于1000的院校
            high_rank_unis.append(f"{rec.get('university_name')} (位次: {rank:,})")

    if high_rank_unis:
        print(f"警告：发现超高分院校: {high_rank_unis}")
    else:
        print("正确：没有超高分院校")

else:
    print(f"API调用失败: {result.get('error')}")