#!/usr/bin/env python3
"""
从现有数据中提取所有广东本地院校，并分析覆盖情况
"""
import pandas as pd
import json
from pathlib import Path
from collections import defaultdict

# 广东本地院校清单（应覆盖的54所）
EXPECTED_GUANGDONG_UNIVERSITIES = {
    "广东重点本科": [
        "广东工业大学", "深圳大学", "广州大学", "汕头大学",
        "广东外语外贸大学", "华南农业大学", "广州医科大学", "南方医科大学"
    ],
    "广东普通本科": [
        "东莞理工学院", "佛山科学技术学院", "佛山大学", "五邑大学", "惠州学院",
        "肇庆学院", "广东石油化工学院", "韶关学院", "嘉应学院",
        "韩山师范学院", "岭南师范学院", "广东技术师范大学", "广东第二师范学院"
    ],
    "广东独立学院": [
        "珠海科技学院", "广州南方学院", "广州华商学院", "广东白云学院",
        "广东理工学院", "广州理工学院", "东莞城市学院", "广州新华学院",
        "电子科技大学中山学院", "北京理工大学珠海学院", "广州华立学院"
    ],
    "广东民办本科": [
        "广东科技学院", "广州软件学院", "广州工商学院", "广东东软学院",
        "广东培正学院", "广州商学院", "湛江科技学院"
    ],
    "广东高职专科": [
        "深圳职业技术大学", "深圳信息职业技术大学", "广东轻工职业技术学院",
        "广州番禺职业技术学院", "广东机电职业技术学院", "广东交通职业技术学院",
        "广东工贸职业技术学院", "广东水利电力职业技术学院", "广东科学技术职业学院",
        "广东职业技术学院", "广东邮电职业技术学院", "广东司法警官职业学院",
        "广东体育职业技术学院", "广东建设职业技术学院", "广东食品药品职业技术学院",
        "广东环境保护工程职业学院", "广东松山职业技术学院", "广东农工商职业技术学院",
        "广东女子职业技术学院"
    ]
}

# 广东院校关键词（用于识别）
GUANGDONG_KEYWORDS = [
    "广东", "广州", "深圳", "珠海", "汕头", "佛山", "东莞", "惠州",
    "肇庆", "韶关", "嘉应", "韩山", "岭南", "五邑", "茂名", "湛江",
    "中山", "江门", "潮州", "梅州", "河源", "清远", "云浮", "阳江",
    "汕尾", "揭阳", "顺德"
]

def is_guangdong_university(university_name):
    """判断是否为广东本地院校"""
    if not university_name:
        return False

    # 排除一些虽然是广东关键词但不是广东的院校
    excluded = ["广东工业大学", "广东外语外贸大学"]  # 这些应该包含

    # 检查是否包含广东关键词
    for keyword in GUANGDONG_KEYWORDS:
        if keyword in university_name:
            return True

    return False

def extract_guangdong_universities():
    """提取所有广东本地院校数据"""
    print("=" * 80)
    print("提取所有广东本地院校数据")
    print("=" * 80)

    # 加载数据文件
    data_files = [
        "backend/data/guangdong_2025_major_level.csv",
        "backend/data/guangdong_2025_major_level_intelligent.csv",
        "backend/data/major_rank_data.json"
    ]

    all_records = []
    all_guangdong_records = []

    # 加载CSV数据
    for csv_file in data_files[:2]:
        csv_path = Path(csv_file)
        if not csv_path.exists():
            continue

        print(f"\n加载文件: {csv_file}")
        try:
            df = pd.read_csv(csv_path)
            print(f"  总记录数: {len(df)}")

            # 筛选广东本地院校
            guangdong_df = df[df['university'].apply(is_guangdong_university)]
            print(f"  广东院校记录数: {len(guangdong_df)}")

            for _, row in guangdong_df.iterrows():
                record = {
                    "university_code": row.get("university_code", ""),
                    "university_name": row.get("university", ""),
                    "category": row.get("category", ""),
                    "group_code": row.get("group_code", ""),
                    "min_score": int(row.get("min_score", 0)) if pd.notna(row.get("min_score")) else 0,
                    "min_rank": int(row.get("min_rank", 0)) if pd.notna(row.get("min_rank")) else 0,
                    "plan_count": int(row.get("plan_count", 0)) if pd.notna(row.get("plan_count")) else 0,
                    "major_name": row.get("major_name", ""),
                    "source": csv_file
                }
                all_guangdong_records.append(record)

            all_records.extend(df.to_dict('records'))

        except Exception as e:
            print(f"  加载失败: {e}")

    # 加载JSON数据
    json_path = Path(data_files[2])
    if json_path.exists():
        print(f"\n加载文件: {json_path}")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            json_records = json_data.get("major_rank_data", [])
            print(f"  总记录数: {len(json_records)}")

            # 筛选广东本地院校
            for record in json_records:
                university = record.get("university_name", "")
                if is_guangdong_university(university):
                    guangdong_record = {
                        "university_code": record.get("university_code", ""),
                        "university_name": university,
                        "category": record.get("category", ""),
                        "group_code": record.get("group_code", ""),
                        "min_score": record.get("min_score", 0),
                        "min_rank": record.get("min_rank", 0),
                        "plan_count": record.get("plan_count", 0),
                        "major_name": record.get("major_name", ""),
                        "source": "major_rank_data.json"
                    }
                    all_guangdong_records.append(guangdong_record)

            print(f"  广东院校记录数: {len([r for r in all_guangdong_records if r['source'] == 'major_rank_data.json'])}")

        except Exception as e:
            print(f"  加载失败: {e}")

    print(f"\n总广东院校记录数: {len(all_guangdong_records)}")

    # 去重
    unique_records = {}
    for record in all_guangdong_records:
        key = f"{record['university_name']}_{record['group_code']}_{record['category']}_{record.get('major_name', '')}"
        if key not in unique_records:
            unique_records[key] = record

    unique_guangdong_records = list(unique_records.values())
    print(f"去重后记录数: {len(unique_guangdong_records)}")

    # 统计院校覆盖
    covered_universities = set(r['university_name'] for r in unique_guangdong_records)
    print(f"覆盖广东院校数: {len(covered_universities)}")

    # 分析覆盖情况
    print(f"\n" + "=" * 80)
    print("广东本地院校覆盖情况分析")
    print("=" * 80)

    coverage_report = {}
    all_missing = []

    for category, universities in EXPECTED_GUANGDONG_UNIVERSITIES.items():
        covered = []
        missing = []

        for uni in universities:
            # 检查是否包含（包括变体名称）
            is_covered = False
            for covered_uni in covered_universities:
                if uni in covered_uni or covered_uni in uni:
                    covered.append(uni)
                    is_covered = True
                    break

            if not is_covered:
                missing.append(uni)

        coverage_rate = len(covered) / len(universities) * 100 if universities else 0

        coverage_report[category] = {
            "total": len(universities),
            "covered": len(covered),
            "missing": len(missing),
            "coverage_rate": coverage_rate,
            "covered_list": covered,
            "missing_list": missing
        }

        status = "[OK]" if coverage_rate >= 90 else "[WARN]" if coverage_rate >= 50 else "[MISS]"
        print(f"\n{status} {category}")
        print(f"  覆盖率: {len(covered)}/{len(universities)} ({coverage_rate:.1f}%)")

        if covered:
            print(f"  已覆盖: {', '.join(covered)}")

        if missing:
            print(f"  缺失: {', '.join(missing)}")
            all_missing.extend([(category, uni) for uni in missing])

    # 生成提取的数据文件
    print(f"\n" + "=" * 80)
    print("生成数据文件")
    print("=" * 80)

    # 保存广东院校数据
    output_file = Path("backend/data/guangdong_universities_extracted.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(unique_guangdong_records, f, ensure_ascii=False, indent=2)
    print(f"[OK] 广东院校数据已保存: {output_file}")

    # 保存覆盖报告
    report_file = Path("backend/data/guangdong_coverage_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(coverage_report, f, ensure_ascii=False, indent=2)
    print(f"[OK] 覆盖报告已保存: {report_file}")

    # 生成文本报告
    text_report_file = Path("backend/data/guangdong_coverage_text_report.txt")
    with open(text_report_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("广东本地院校数据覆盖情况报告\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"数据来源：现有数据文件\n")
        f.write(f"提取时间：2026-05-10\n")
        f.write(f"总记录数：{len(unique_guangdong_records)}\n")
        f.write(f"覆盖院校数：{len(covered_universities)}\n\n")

        f.write("=" * 80 + "\n")
        f.write("一、各类院校覆盖情况\n")
        f.write("=" * 80 + "\n\n")

        total_expected = sum(len(unis) for unis in EXPECTED_GUANGDONG_UNIVERSITIES.values())
        total_covered = sum(stats["covered"] for stats in coverage_report.values())

        f.write(f"总体覆盖率：{total_covered}/{total_expected} ({total_covered/total_expected*100:.1f}%)\n\n")

        for category, stats in coverage_report.items():
            status = "[OK]" if stats["coverage_rate"] >= 90 else "[WARN]" if stats["coverage_rate"] >= 50 else "[MISS]"
            f.write(f"{status} {category}\n")
            f.write(f"  覆盖率：{stats['covered']}/{stats['total']} ({stats['coverage_rate']:.1f}%)\n")

            if stats["covered_list"]:
                f.write(f"  已覆盖：{', '.join(stats['covered_list'])}\n")

            if stats["missing_list"]:
                f.write(f"  缺失：{', '.join(stats['missing_list'])}\n")

            f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("二、缺失院校清单\n")
        f.write("=" * 80 + "\n\n")

        for category, uni in all_missing:
            f.write(f"- {uni} ({category})\n")

        f.write(f"\n共缺失：{len(all_missing)} 所院校\n")

    print(f"[OK] 文本报告已保存: {text_report_file}")

    # 显示汇总
    print(f"\n" + "=" * 80)
    print("提取完成汇总")
    print("=" * 80)
    print(f"总记录数：{len(unique_guangdong_records)}")
    print(f"覆盖院校数：{len(covered_universities)}")
    print(f"预期院校数：{total_expected}")
    print(f"已覆盖：{total_covered} ({total_covered/total_expected*100:.1f}%)")
    print(f"缺失：{len(all_missing)} ({len(all_missing)/total_expected*100:.1f}%)")

    return unique_guangdong_records, coverage_report

if __name__ == "__main__":
    extract_guangdong_universities()
