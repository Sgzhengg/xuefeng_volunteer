"""
生成完整的院校专业关联表
从 major_rank_data.json 提取所有院校-专业关系
"""

import json
from pathlib import Path
from collections import defaultdict


def build_university_majors():
    """生成完整的院校专业关联表"""

    print("Building university_majors.json from major_rank_data.json...")

    data_dir = Path(__file__).parent.parent / "data"
    input_file = data_dir / "major_rank_data.json"
    output_file = data_dir / "university_majors.json"

    # 读取原始数据
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])
    print(f"Processing {len(records):,} records...")

    # 按院校组织专业数据
    uni_majors = {}

    for record in records:
        uni_id = record.get("university_id", "")
        uni_name = record.get("university_name", "")
        province = record.get("province", "")
        city = record.get("city", "")

        major_code = record.get("major_code", "")
        major_name = record.get("major_name", "")
        major_category = record.get("major_category", "")
        year = record.get("year", 2024)

        # 创建院校条目
        if uni_id not in uni_majors:
            uni_majors[uni_id] = {
                "university_id": uni_id,
                "university_name": uni_name,
                "province": province,
                "city": city,
                "majors": []
            }

        # 检查专业是否已存在
        existing_majors = uni_majors[uni_id]["majors"]
        major_exists = any(
            m.get("major_code") == major_code or m.get("major_name") == major_name
            for m in existing_majors
        )

        if not major_exists:
            # 添加专业信息
            major_info = {
                "major_code": major_code,
                "major_name": major_name,
                "major_category": major_category,
                "latest_year": year,
                "admission_info": {
                    "min_score": record.get("min_score"),
                    "avg_score": record.get("avg_score"),
                    "min_rank": record.get("min_rank"),
                    "avg_rank": record.get("avg_rank"),
                }
            }

            uni_majors[uni_id]["majors"].append(major_info)

    # 转换为列表
    result_list = list(uni_majors.values())

    # 按院校ID排序
    result_list.sort(key=lambda x: x["university_id"])

    # 统计信息
    total_unis = len(result_list)
    total_majors = sum(len(uni["majors"]) for uni in result_list)
    avg_majors = total_majors / total_unis if total_unis > 0 else 0

    # 保存结果
    output_data = {
        "metadata": {
            "version": "2.0.0",
            "generated_at": str(Path(__file__).stat().st_mtime),
            "total_universities": total_unis,
            "total_major_records": total_majors,
            "average_majors_per_university": round(avg_majors, 1)
        },
        "universities": result_list
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] Generated university_majors.json")
    print(f"  Total universities: {total_unis:,}")
    print(f"  Total major records: {total_majors:,}")
    print(f"  Average majors per university: {avg_majors:.1f}")
    print(f"  File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"  Saved to: {output_file}")


def generate_statistics():
    """生成数据统计信息"""

    data_dir = Path(__file__).parent.parent / "data"
    input_file = data_dir / "major_rank_data.json"

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])

    print(f"\n[Data Statistics]")
    print(f"=" * 60)

    # 按省份统计
    from collections import Counter
    provinces = [r.get("province", "Unknown") for r in records]
    province_counts = Counter(provinces)

    print(f"Total records: {len(records):,}")
    print(f"Total provinces: {len(province_counts)}")
    print(f"\nTop 10 provinces by record count:")
    for province, count in province_counts.most_common(10):
        print(f"  {province}: {count:,}")

    # 按年份统计
    years = [r.get("year", 0) for r in records]
    year_counts = Counter(years)

    print(f"\nYear distribution:")
    for year in sorted(year_counts.keys(), reverse=True):
        print(f"  {year}: {year_counts[year]:,}")

    # 按专业类别统计
    categories = [r.get("major_category", "Unknown") for r in records]
    category_counts = Counter(categories)

    print(f"\nTop 10 major categories:")
    for category, count in category_counts.most_common(10):
        print(f"  {category}: {count:,}")

    print(f"=" * 60)


if __name__ == "__main__":
    # 生成统计信息
    generate_statistics()

    # 构建完整的院校专业关联表
    build_university_majors()