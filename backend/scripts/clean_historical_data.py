#!/usr/bin/env python3
"""
删除 2023-2024 年数据和模拟数据
"""
import json
import shutil
from pathlib import Path
from datetime import datetime

def clean_historical_data():
    # 1. 备份原文件
    original_path = Path("backend/data/major_rank_data.json")
    if not original_path.exists():
        print("[ERROR] 找不到数据文件: backend/data/major_rank_data.json")
        return

    backup_path = Path(f"backend/data/major_rank_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    shutil.copy(original_path, backup_path)
    print(f"[OK] 已备份到 {backup_path}")

    # 2. 加载数据
    with open(original_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 3. 过滤数据
    filtered = []
    removed_count = 0

    # 统计信息
    year_stats = {}
    category_stats = {}

    # 数据在 major_rank_data 数组中
    records = data.get("major_rank_data", [])
    for record in records:
        year = record.get("year")
        category = record.get("category")

        # 统计原始数据
        if year:
            year_stats[year] = year_stats.get(year, 0) + 1
        if category:
            category_stats[category] = category_stats.get(category, 0) + 1

        # 只保留 2025 年数据
        if year == 2025:
            # 检查是否为模拟数据
            university_name = record.get("university_name", "").lower()
            is_mock = False

            mock_keywords = ["一般院校", "测试", "模拟", "示例", "demo", "test", "placeholder"]
            for kw in mock_keywords:
                if kw in university_name:
                    is_mock = True
                    break

            if not is_mock:
                filtered.append(record)
            else:
                removed_count += 1
                print(f"[REMOVE] 模拟数据: {record.get('university_name', 'Unknown')} ({year})")
        else:
            removed_count += 1
            if year not in [2023, 2024]:
                print(f"[REMOVE] 其他年份: {year} - {record.get('university_name', 'Unknown')}")

    # 4. 保存清理后的数据
    result_data = {
        "major_rank_data": filtered
    }
    with open(original_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] 清理完成")
    print(f"    - 删除记录: {removed_count} 条")
    print(f"    - 保留记录: {len(filtered)} 条")

    # 5. 输出详细统计
    print("\n=== 数据统计 ===")
    print("原始数据分布:")
    for year, count in sorted(year_stats.items()):
        print(f"  {year}年: {count} 条")

    print("\n保留数据分布:")
    year_2025 = len([r for r in filtered if r.get("year") == 2025])
    print(f"  2025年: {year_2025} 条")

    if category_stats:
        print("\n科类分布:")
        for category, count in category_stats.items():
            filtered_count = len([r for r in filtered if r.get("category") == category])
            print(f"  {category}: {filtered_count} 条")

    # 6. 文件大小对比
    original_size = backup_path.stat().st_size
    new_size = original_path.stat().st_size
    saved_size = original_size - new_size

    print(f"\n文件大小变化:")
    print(f"  原文件: {original_size / 1024 / 1024:.2f} MB")
    print(f"  新文件: {new_size / 1024 / 1024:.2f} MB")
    print(f"  节省空间: {saved_size / 1024 / 1024:.2f} MB")

    return {
        "original_count": len(data),
        "filtered_count": len(filtered),
        "removed_count": removed_count,
        "year_stats": year_stats,
        "category_stats": category_stats,
        "backup_file": str(backup_path),
        "saved_size": abs(saved_size)
    }

if __name__ == "__main__":
    result = clean_historical_data()