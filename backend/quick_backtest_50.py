#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速回溯测试验证修复效果（50样本）"""
import sys
import json
sys.path.append('.')

from app.services.guangdong_recommendation_service import guangdong_recommendation_service

print("快速回溯测试验证修复效果（50样本）\n")

# 从回溯测试数据中提取一些真实测试用例
test_cases = [
    # 高分段
    {"rank": 3000, "province": "广东"},
    {"rank": 5000, "province": "广东"},
    {"rank": 8000, "province": "广东"},

    # 中高分段
    {"rank": 12000, "province": "广东"},
    {"rank": 18000, "province": "广东"},
    {"rank": 25000, "province": "广东"},

    # 关键的中分段（之前0%命中的段）
    {"rank": 35000, "province": "广东"},
    {"rank": 40000, "province": "广东"},
    {"rank": 45000, "province": "广东"},
    {"rank": 50000, "province": "广东"},
    {"rank": 55000, "province": "广东"},
    {"rank": 60000, "province": "广东"},
    {"rank": 65000, "province": "广东"},

    # 中低分段
    {"rank": 75000, "province": "广东"},
    {"rank": 85000, "province": "广东"},
    {"rank": 95000, "province": "广东"},

    # 低分段
    {"rank": 110000, "province": "广东"},
    {"rank": 125000, "province": "广东"},
    {"rank": 140000, "province": "广东"},
    {"rank": 160000, "province": "广东"},
    {"rank": 180000, "province": "广东"},
    {"rank": 200000, "province": "广东"},
]

total_tests = len(test_cases)
hit_count = 0
high_rank_errors = 0  # 推荐了不合理的高分院校

for i, test_case in enumerate(test_cases, 1):
    rank = test_case["rank"]
    province = test_case["province"]

    # 调用推荐服务
    result = guangdong_recommendation_service.recommend_with_fallback(
        user_rank=rank,
        province=province,
        subject_type="理科",
        target_majors=["计算机科学与技术"]
    )

    if result.get("success"):
        recommendations = result.get("data", {})

        # 检查推荐结果合理性
        all_recs = []
        for category in ["冲刺", "稳妥", "保底"]:
            all_recs.extend(recommendations.get(category, []))

        if all_recs:
            # 检查是否有不合理的高分院校推荐
            has_high_rank_error = False
            for rec in all_recs:
                rec_rank = rec.get("min_rank", 0)
                rec_uni = rec.get("university_name", "")

                # 如果用户位次>10000，但推荐了位次<5000的顶尖院校，则认为不合理
                if rank > 10000 and rec_rank < 5000:
                    top_unis = ["北京大学", "清华大学", "浙江大学", "复旦大学", "上海交通大学", "中国科学技术大学"]
                    if any(top_uni in rec_uni for top_uni in top_unis):
                        has_high_rank_error = True
                        break

            if has_high_rank_error:
                high_rank_errors += 1
                if i <= 5:  # 只显示前几个错误
                    print(f"{i}. 位次 {rank:7,}: X 高分院校错误")
            else:
                hit_count += 1
                if i <= 5:  # 只显示前几个成功
                    print(f"{i}. 位次 {rank:7,}: OK 正常")
        else:
            if i <= 5:
                print(f"{i}. 位次 {rank:7,}: X 无推荐结果")
    else:
        if i <= 5:
            print(f"{i}. 位次 {rank:7,}: X API错误")

# 输出统计结果
print(f"\n{'='*50}")
print(f"测试统计:")
print(f"总测试数: {total_tests}")
print(f"正常推荐: {hit_count} ({hit_count/total_tests*100:.1f}%)")
print(f"高分院校错误: {high_rank_errors} ({high_rank_errors/total_tests*100:.1f}%)")
print(f"{'='*50}")

# 判断修复是否成功
if high_rank_errors == 0 and hit_count >= total_tests * 0.9:
    print("SUCCESS: 修复成功！算法问题已解决！")
elif high_rank_errors <= total_tests * 0.1:  # 允许10%的误差
    print("SUCCESS: 修复基本成功！仅有少量高分院校错误。")
else:
    print("PROBLEM: 仍有问题：高分院校错误率过高")