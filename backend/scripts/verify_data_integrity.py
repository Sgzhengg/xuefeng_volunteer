#!/usr/bin/env python3
"""
验证数据完整性
"""
import json
from pathlib import Path
from datetime import datetime

def verify_data_integrity():
    print("=== 数据完整性验证 ===")

    # 1. 检查数据文件
    data_path = Path("data/major_rank_data.json")
    if not data_path.exists():
        print("[ERROR] 数据文件不存在")
        return False

    # 2. 加载数据
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])

    # 3. 基本统计
    total_records = len(records)
    print(f"\n总记录数：{total_records:,} 条")

    # 4. 检查年份分布
    year_counts = {}
    category_counts = {}
    has_major_name = 0
    rank_min = float('inf')
    rank_max = float('-inf')

    for record in records:
        # 年份统计
        year = record.get("year")
        if year:
            year_counts[year] = year_counts.get(year, 0) + 1

        # 科类统计
        category = record.get("category")
        if category:
            category_counts[category] = category_counts.get(category, 0) + 1

        # 专业名称检查
        if record.get("major_name"):
            has_major_name += 1

        # 位次范围
        min_rank = record.get("min_rank", 0)
        if min_rank:
            rank_min = min(rank_min, min_rank)
            rank_max = max(rank_max, min_rank)

    # 5. 输出统计
    print(f"\n年份分布：")
    for year, count in sorted(year_counts.items()):
        percentage = (count / total_records) * 100
        print(f"  {year}年: {count:,} 条 ({percentage:.1f}%)")

    print(f"\n科类分布：")
    for category, count in sorted(category_counts.items()):
        percentage = (count / total_records) * 100
        print(f"  {category}: {count:,} 条 ({percentage:.1f}%)")

    print(f"\n专业名称完整性：{has_major_name / total_records * 100:.1f}% ({has_major_name:,}/{total_records:,})")
    print(f"\n位次范围：{rank_min:,} - {rank_max:,}")

    # 6. 检查模拟数据
    mock_keywords = ["一般院校", "测试", "模拟", "示例", "demo", "test", "placeholder"]
    mock_records = []

    for record in records:
        university_name = record.get("university_name", "").lower()
        for kw in mock_keywords:
            if kw in university_name:
                mock_records.append(record)
                break

    print(f"\n模拟数据：{len(mock_records)} 条")
    if mock_records:
        print("发现模拟数据：")
        for i, record in enumerate(mock_records[:5]):
            print(f"  - {record.get('university_name')} ({record.get('year')})")

    # 7. 检查位次段覆盖
    rank_segments = {
        "1-10000": 0,
        "10001-30000": 0,
        "30001-70000": 0,
        "70001-120000": 0,
        "120001-200000": 0,
        "200001-350000": 0
    }

    for record in records:
        min_rank = record.get("min_rank", 0)
        if min_rank <= 10000:
            rank_segments["1-10000"] += 1
        elif min_rank <= 30000:
            rank_segments["10001-30000"] += 1
        elif min_rank <= 70000:
            rank_segments["30001-70000"] += 1
        elif min_rank <= 120000:
            rank_segments["70001-120000"] += 1
        elif min_rank <= 200000:
            rank_segments["120001-200000"] += 1
        else:
            rank_segments["200001-350000"] += 1

    print(f"\n位次段覆盖：")
    for segment, count in rank_segments.items():
        percentage = (count / total_records) * 100
        print(f"  {segment} 位次: {count:,} 条 ({percentage:.1f}%)")

    # 8. 生成验证报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_records": total_records,
        "year_distribution": year_counts,
        "category_distribution": category_counts,
        "has_major_name_rate": has_major_name / total_records,
        "rank_range": {"min": rank_min, "max": rank_max},
        "mock_records_count": len(mock_records),
        "rank_segments": rank_segments,
        "data_quality": {
            "year_2025_percentage": year_counts.get(2025, 0) / total_records * 100,
            "complete_major_name_percentage": has_major_name / total_records * 100,
            "no_mock_data": len(mock_records) == 0,
            "all_segments_covered": all(count > 0 for count in rank_segments.values())
        }
    }

    # 保存验证报告
    report_path = Path("scripts/data_integrity_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] 验证报告已保存到: {report_path}")

    # 输出验证结果
    print("\n=== 验证结果 ===")
    print(f"✅ 总记录数：{total_records:,} 条")
    print(f"✅ 2025年记录：{year_counts.get(2025, 0):,} 条 ({year_counts.get(2025, 0)/total_records*100:.1f}%)")

    physical_count = category_counts.get("物理", 0)
    history_count = category_counts.get("历史", 0)
    print(f"✅ 物理类记录：{physical_count:,} 条")
    print(f"✅ 历史类记录：{history_count:,} 条")

    print(f"✅ 有专业名称的记录：{has_major_name / total_records * 100:.1f}%")
    print(f"✅ 位次段覆盖：{len([s for s in rank_segments.values() if s > 0])}/6 个段位")
    print(f"✅ 无模拟数据：{'是' if len(mock_records) == 0 else '否'}")

    return report

if __name__ == "__main__":
    verify_data_integrity()