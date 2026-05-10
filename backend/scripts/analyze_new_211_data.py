#!/usr/bin/env python3
"""
分析新增 211 院校的位次分布规律
"""
import json
from pathlib import Path
from collections import defaultdict, Counter
import pandas as pd

def analyze_new_211_data():
    print("=== 分析新增211院校数据分布 ===")

    # 1. 加载数据
    data_path = Path("../data/major_rank_data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_records = data.get("major_rank_data", [])
    print(f"总数据量：{len(all_records)} 条")

    # 2. 筛选新增的211院校数据
    new_211_list = [
        "上海财经大学", "中央财经大学", "西南财经大学", "对外经济贸易大学",
        "西安电子科技大学", "北京邮电大学", "中国政法大学", "北京外国语大学",
        "上海外国语大学", "中央民族大学", "中国农业大学", "大连海事大学",
        "东北林业大学", "东北农业大学", "西北大学", "长安大学",
        "西北农林科技大学", "安徽大学", "合肥工业大学", "福州大学",
        "南昌大学", "郑州大学", "云南大学", "贵州大学",
        "广西大学", "海南大学", "内蒙古大学", "新疆大学"
    ]

    new_211_data = []
    for record in all_records:
        if record.get("university_name") in new_211_list:
            new_211_data.append(record)

    print(f"新增211院校数据：{len(new_211_data)} 条")

    if not new_211_data:
        print("未找到新增211院校数据")
        return

    # 3. 分析位次分布
    ranks = [r.get("min_rank", 0) for r in new_211_data if r.get("min_rank")]
    scores = [r.get("min_score", 0) for r in new_211_data if r.get("min_score")]

    print(f"\n=== 基本统计 ===")
    print(f"位次范围：{min(ranks):,} - {max(ranks):,}")
    print(f"分数范围：{min(scores):.1f} - {max(scores):.1f}")
    print(f"位次平均值：{sum(ranks)/len(ranks):,.0f}")
    print(f"分数平均值：{sum(scores)/len(scores):.1f}")

    # 4. 按位次段统计
    rank_segments = {
        "1-10000": 0,
        "10001-20000": 0,
        "20001-30000": 0,
        "30001-40000": 0,
        "40000+": 0
    }

    for record in new_211_data:
        min_rank = record.get("min_rank", 0)
        if min_rank <= 10000:
            rank_segments["1-10000"] += 1
        elif min_rank <= 20000:
            rank_segments["10001-20000"] += 1
        elif min_rank <= 30000:
            rank_segments["20001-30000"] += 1
        elif min_rank <= 40000:
            rank_segments["30001-40000"] += 1
        else:
            rank_segments["40000+"] += 1

    print(f"\n=== 位次段分布 ===")
    for segment, count in rank_segments.items():
        percentage = count / len(new_211_data) * 100 if new_211_data else 0
        print(f"{segment}: {count} 条 ({percentage:.1f}%)")

    # 5. 按院校统计
    university_stats = defaultdict(lambda: {"count": 0, "ranks": []})
    for record in new_211_data:
        university = record.get("university_name", "")
        university_stats[university]["count"] += 1
        university_stats[university]["ranks"].append(record.get("min_rank", 0))

    print(f"\n=== 院校专业数量（前15）===")
    university_sorted = sorted(university_stats.items(), key=lambda x: x[1]["count"], reverse=True)
    for university, stats in university_sorted[:15]:
        avg_rank = sum(stats["ranks"]) / len(stats["ranks"]) if stats["ranks"] else 0
        print(f"{university}: {stats['count']} 个专业, 平均位次 {avg_rank:,.0f}")

    # 6. 按科类统计
    category_stats = defaultdict(int)
    for record in new_211_data:
        category = record.get("category", "")
        if category:
            category_stats[category] += 1

    print(f"\n=== 科类分布 ===")
    for category, count in category_stats.items():
        percentage = count / len(new_211_data) * 100 if new_211_data else 0
        print(f"{category}: {count} 条 ({percentage:.1f}%)")

    # 7. 分析推荐策略建议
    print(f"\n=== 推荐策略建议 ===")

    # 计算各位次段的密度
    segment_density = {}
    for segment, count in rank_segments.items():
        if "10001-20000" in segment or "20001-30000" in segment:
            segment_range = 10000
        else:
            segment_range = 10000
        density = count / segment_range
        segment_density[segment] = density

    print("位次段密度（每1000位次的记录数）：")
    for segment, density in segment_density.items():
        print(f"  {segment}: {density:.2f}")

    # 推荐范围建议
    if rank_segments["10001-20000"] > 0:
        print(f"\n10001-20000段位建议：")
        print(f"  冲刺范围：用户位次 ± 15%")
        print(f"  稳妥范围：用户位次 ± 25%")
        print(f"  保底范围：用户位次 + 20% ~ +50%")

    if rank_segments["20001-30000"] > 0:
        print(f"\n20001-30000段位建议：")
        print(f"  冲刺范围：用户位次 ± 12%")
        print(f"  稳妥范围：用户位次 ± 20%")
        print(f"  保底范围：用户位次 + 15% ~ +40%")

    # 8. 生成参数调整建议
    print(f"\n=== 算法参数调整建议 ===")

    total_records = len(all_records)
    new_211_ratio = len(new_211_data) / total_records

    print(f"新增211院校数据占比：{new_211_ratio:.2%}")

    # 基于数据密度建议参数
    if segment_density.get("10001-20000", 0) > 0.05:
        print(f"✅ 10001-20000段位数据充足，可扩大推荐范围")
        print(f"   建议RANK_RANGE_WEN从10000增加到15000")

    if segment_density.get("20001-30000", 0) > 0.05:
        print(f"✅ 20001-30000段位数据充足，可扩大推荐范围")
        print(f"   建议RANK_RANGE_WEN从10000增加到12000")

    return {
        "new_211_count": len(new_211_data),
        "rank_range": (min(ranks), max(ranks)),
        "score_range": (min(scores), max(scores)),
        "rank_segments": rank_segments,
        "segment_density": segment_density
    }

if __name__ == "__main__":
    result = analyze_new_211_data()