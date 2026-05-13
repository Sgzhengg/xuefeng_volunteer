#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简化版回溯测试验证修复效果"""
import sys
sys.path.append('.')

from app.services.guangdong_recommendation_service import guangdong_recommendation_service

print("简化版回溯测试验证修复效果\n")

# 关键测试用例（各分数段代表）
test_cases = [
    {"rank": 5000, "name": "高分段"},
    {"rank": 25000, "name": "中高分段"},
    {"rank": 50000, "name": "中分段（之前0%命中）"},
    {"rank": 100000, "name": "中低分段"},
    {"rank": 200000, "name": "低分段"},
]

results = []

for test_case in test_cases:
    rank = test_case["rank"]
    name = test_case["name"]

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

        # 检查是否有不合理的高分院校
        has_high_rank_error = False
        high_rank_found = []
        for rec in all_recs:
            rec_rank = rec.get("min_rank", 0)
            rec_uni = rec.get("university_name", "")

            # 检查是否推荐了不合理的高分院校
            if rank > 10000 and rec_rank < 5000:
                top_unis = ["北京大学", "清华大学", "浙江大学", "复旦大学", "上海交通大学", "中国科学技术大学"]
                if any(top_uni in rec_uni for top_uni in top_unis):
                    has_high_rank_error = True
                    high_rank_found.append(f"{rec_uni}({rec_rank})")
                    break

        status = "PASS" if not has_high_rank_error else "FAIL"
        results.append({
            "rank": rank,
            "name": name,
            "status": status,
            "has_high_rank_error": has_high_rank_error,
            "high_rank_found": high_rank_found,
            "total_recs": len(all_recs)
        })

# 输出结果
print("="*60)
print("测试结果:")
print("="*60)

pass_count = sum(1 for r in results if r["status"] == "PASS")
total_count = len(results)

for r in results:
    print(f"{r['rank']:7,} ({r['name']:12s}): {r['status']} | 推荐{r['total_recs']}条")
    if r["has_high_rank_error"]:
        print(f"         错误推荐: {r['high_rank_found']}")
    else:
        print(f"         正常: 无不合理高分院校")

print("="*60)
print(f"通过率: {pass_count}/{total_count} ({pass_count/total_count*100:.1f}%)")

if pass_count == total_count:
    print("SUCCESS: 所有测试通过！修复成功！")
elif pass_count >= total_count * 0.8:
    print("GOOD: 大部分测试通过，基本修复成功")
else:
    print("PROBLEM: 仍有较多测试失败，需要继续调整")