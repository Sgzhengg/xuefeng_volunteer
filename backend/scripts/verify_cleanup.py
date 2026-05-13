#!/usr/bin/env python3
"""
验证清理后的数据质量
"""
import json
from pathlib import Path

def verify_cleanup():
    """验证清理结果"""
    print("=== 验证清理结果 ===")

    # 1. 检查数据文件
    data_path = Path("backend/data/major_rank_data.json")
    if not data_path.exists():
        print("[ERROR] 数据文件不存在")
        return False

    # 2. 加载数据
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])

    # 3. 验证年份
    years = set(record.get("year") for record in records)
    print(f"[OK] 剩余年份: {sorted(years)}")

    # 4. 检查是否还有模拟数据
    mock_keywords = ["一般院校", "测试", "模拟", "示例", "demo", "test", "placeholder"]
    mock_records = []

    for record in records:
        university_name = record.get("university_name", "").lower()
        for kw in mock_keywords:
            if kw in university_name:
                mock_records.append(record)
                break

    if mock_records:
        print(f"[WARN] 发现 {len(mock_records)} 条疑似模拟数据")
        for i, record in enumerate(mock_records[:5]):  # 只显示前5条
            print(f"  - {record.get('university_name')} ({record.get('year')})")
        if len(mock_records) > 5:
            print(f"  ... 还有 {len(mock_records) - 5} 条")
    else:
        print("[OK] 无模拟数据")

    # 5. 统计数据分布
    year_counts = {}
    category_counts = {}

    for record in records:
        year = record.get("year")
        category = record.get("category")

        year_counts[year] = year_counts.get(year, 0) + 1
        if category:
            category_counts[category] = category_counts.get(category, 0) + 1

    print("\n=== 数据统计 ===")
    print("年份分布:")
    for year in sorted(year_counts.keys()):
        print(f"  {year}年: {year_counts[year]} 条")

    if category_counts:
        print("\n科类分布:")
        for category, count in category_counts.items():
            print(f"  {category}: {count} 条")

    # 6. 检查位次覆盖
    ranks = [r.get("min_rank", 0) for r in records if r.get("min_rank")]
    if ranks:
        print(f"\n位次范围: {min(ranks)} - {max(ranks)}")

    # 7. 检查文件大小
    file_size = data_path.stat().st_size
    print(f"\n文件大小: {file_size / 1024 / 1024:.2f} MB")

    # 8. 检查语音功能是否清理
    print("\n=== 语音功能验证 ===")

    # 检查pubspec.yaml
    pubspec_path = Path("pubspec.yaml")
    if pubspec_path.exists():
        with open(pubspec_path, "r", encoding="utf-8") as f:
            pubspec_content = f.read()

        if "speech_to_text" in pubspec_content:
            print("[FAIL] pubspec.yaml 仍包含语音依赖")
        else:
            print("[OK] pubspec.yaml 无语音依赖")

    # 检查语音文件
    voice_files = [
        "lib/features/chat/widgets/voice_input_button.dart"
    ]

    for file_path in voice_files:
        if Path(file_path).exists():
            print(f"[FAIL] 语音文件仍存在: {file_path}")
        else:
            print(f"[OK] 语音文件已删除: {file_path}")

    # 检查Dart文件中的语音相关代码
    dart_files = list(Path("lib").rglob("*.dart"))
    voice_imports = []
    voice_calls = []

    for file_path in dart_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().lower()

            if "speech_to_text" in content:
                voice_imports.append(str(file_path))

            if any(keyword in content for keyword in ["startlistening", "stoplistening", "record", "voice"]):
                voice_calls.append(str(file_path))

    if voice_imports:
        print(f"[WARN] 以下文件仍包含语音导入: {voice_imports}")
    else:
        print("[OK] 无语音导入")

    if voice_calls:
        print(f"[WARN] 以下文件仍包含语音调用: {voice_calls}")
    else:
        print("[OK] 无语音调用")

    return {
        "total_records": len(records),
        "years": years,
        "mock_records": len(mock_records),
        "year_counts": year_counts,
        "category_counts": category_counts,
        "file_size": file_size
    }

if __name__ == "__main__":
    result = verify_cleanup()