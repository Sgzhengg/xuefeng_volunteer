#!/usr/bin/env python3
"""
合并所有广东本地院校数据，并生成补充计划
"""
import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

def merge_guangdong_data():
    """合并所有广东院校数据"""
    print("=" * 80)
    print("合并所有广东本地院校数据")
    print("=" * 80)

    # 加载提取的广东院校数据
    extracted_file = Path("backend/data/guangdong_universities_extracted.json")
    if extracted_file.exists():
        with open(extracted_file, "r", encoding="utf-8") as f:
            extracted_data = json.load(f)
        print(f"加载提取的广东院校数据: {len(extracted_data)} 条")
    else:
        extracted_data = []
        print("[WARN] 未找到提取的广东院校数据")

    # 加载主数据文件中的广东院校数据
    main_data_file = Path("backend/data/major_rank_data.json")
    if main_data_file.exists():
        with open(main_data_file, "r", encoding="utf-8") as f:
            main_data = json.load(f)
            main_records = main_data.get("major_rank_data", [])

        # 筛选广东院校
        guangdong_keywords = ["广东", "广州", "深圳", "珠海", "汕头", "佛山", "东莞", "惠州"]
        main_guangdong = [r for r in main_records if any(kw in r.get("university_name", "") for kw in guangdong_keywords)]
        print(f"主数据中的广东院校: {len(main_guangdong)} 条")
    else:
        main_guangdong = []

    # 合并数据
    all_merged = extracted_data + main_guangdong

    # 去重
    unique_records = {}
    for record in all_merged:
        key = f"{record.get('university_name', '')}_{record.get('group_code', '')}_{record.get('category', '')}_{record.get('major_name', '')}"
        if key not in unique_records:
            unique_records[key] = record

    final_merged = list(unique_records.values())
    print(f"合并后总记录数: {len(final_merged)}")
    print(f"去重后记录数: {len(final_merged)}")

    # 统计院校分布
    universities = set(r.get('university_name', '') for r in final_merged)
    print(f"覆盖院校数: {len(universities)}")

    # 按院校分组统计
    university_stats = defaultdict(lambda: {"count": 0, "categories": set(), "groups": set()})
    for record in final_merged:
        uni_name = record.get('university_name', '')
        if uni_name:
            university_stats[uni_name]["count"] += 1
            university_stats[uni_name]["categories"].add(record.get('category', ''))
            university_stats[uni_name]["groups"].add(record.get('group_code', ''))

    # 显示统计信息
    print(f"\n" + "=" * 80)
    print("院校统计信息")
    print("=" * 80)

    sorted_universities = sorted(university_stats.items(), key=lambda x: x[1]["count"], reverse=True)

    for uni_name, stats in sorted_universities[:20]:  # 显示前20所
        categories = ", ".join(sorted(stats["categories"]))
        groups = len(stats["groups"])
        print(f"{uni_name}: {stats['count']} 条记录, {groups} 个专业组, 科类: {categories}")

    # 保存合并后的数据
    output_file = Path("backend/data/guangdong_universities_merged.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_merged, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] 合并数据已保存: {output_file}")

    # 生成CSV格式
    df = pd.DataFrame(final_merged)
    csv_file = Path("backend/data/guangdong_universities_merged.csv")
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    print(f"[OK] CSV文件已保存: {csv_file}")

    return final_merged

def generate_data_collection_plan():
    """生成数据收集计划"""
    print(f"\n" + "=" * 80)
    print("生成数据收集计划")
    print("=" * 80)

    # 加载覆盖报告
    report_file = Path("backend/data/guangdong_coverage_report.json")
    if report_file.exists():
        with open(report_file, "r", encoding="utf-8") as f:
            coverage_report = json.load(f)
    else:
        print("[ERROR] 未找到覆盖报告")
        return

    # 生成收集计划
    collection_plan = {
        "plan_date": "2026-05-10",
        "priority_tiers": {
            "tier_1_immediate": {  # 立即收集
                "description": "高优先级院校，建议立即收集数据",
                "universities": []
            },
            "tier_2_week": {  # 1周内收集
                "description": "中优先级院校，建议1周内收集",
                "universities": []
            },
            "tier_3_month": {  # 1个月内收集
                "description": "低优先级院校，建议1个月内收集",
                "universities": []
            }
        },
        "data_sources": [
            "广东省教育考试院官方PDF",
            "各院校招生官网",
            "阳光高考网",
            "夸克高考"
        ],
        "required_fields": [
            "院校代码",
            "院校名称",
            "专业组代码",
            "专业名称",
            "最低录取分数",
            "最低录取位次",
            "科类（物理/历史）",
            "计划数"
        ]
    }

    # 高优先级院校
    high_priority = [
        "广东工业大学", "深圳大学", "广州大学", "广东外语外贸大学",
        "东莞理工学院", "佛山科学技术学院", "广东技术师范大学",
        "珠海科技学院", "广州南方学院", "电子科技大学中山学院",
        "北京理工大学珠海学院", "深圳职业技术大学", "广东轻工职业技术学院",
        "广州番禺职业技术学院"
    ]

    # 中优先级院校
    medium_priority = [
        "汕头大学", "华南农业大学", "广州医科大学", "南方医科大学",
        "五邑大学", "惠州学院", "肇庆学院", "广东石油化工学院",
        "韩山师范学院", "岭南师范学院", "广东第二师范学院",
        "广州华商学院", "广东白云学院", "广东理工学院",
        "广州理工学院", "东莞城市学院", "广州新华学院",
        "广东科技学院", "广州软件学院", "广州工商学院",
        "广东东软学院", "广州商学院", "深圳信息职业技术大学",
        "广东机电职业技术学院", "广东交通职业技术学院",
        "广东工贸职业技术学院", "广东水利电力职业技术学院",
        "广东科学技术职业学院", "广东职业技术学院",
        "广东邮电职业技术学院", "广东建设职业技术学院",
        "广东食品药品职业技术学院", "广东农工商职业技术学院"
    ]

    # 低优先级院校
    low_priority = [
        "韶关学院", "嘉应学院", "广东培正学院", "广州商学院",
        "湛江科技学院", "广东司法警官职业学院", "广东体育职业技术学院",
        "广东环境保护工程职业学院", "广东松山职业技术学院",
        "广东女子职业技术学院"
    ]

    # 分类缺失院校
    for category, stats in coverage_report.items():
        for missing_uni in stats.get("missing_list", []):
            uni_info = {
                "name": missing_uni,
                "category": category,
                "reason": f"{category}缺失院校"
            }

            if missing_uni in high_priority:
                collection_plan["priority_tiers"]["tier_1_immediate"]["universities"].append(uni_info)
            elif missing_uni in medium_priority:
                collection_plan["priority_tiers"]["tier_2_week"]["universities"].append(uni_info)
            elif missing_uni in low_priority:
                collection_plan["priority_tiers"]["tier_3_month"]["universities"].append(uni_info)

    # 保存收集计划
    plan_file = Path("backend/data/guangdong_data_collection_plan.json")
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(collection_plan, f, ensure_ascii=False, indent=2)
    print(f"[OK] 数据收集计划已保存: {plan_file}")

    # 生成文本格式的收集计划
    text_plan_file = Path("backend/data/guangdong_data_collection_plan.txt")
    with open(text_plan_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("广东本地院校数据收集计划\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"制定日期：{collection_plan['plan_date']}\n")
        f.write(f"缺失院校总数：{len(collection_plan['priority_tiers']['tier_1_immediate']['universities']) + len(collection_plan['priority_tiers']['tier_2_week']['universities']) + len(collection_plan['priority_tiers']['tier_3_month']['universities'])}\n\n")

        f.write("=" * 80 + "\n")
        f.write("一、高优先级（立即收集）\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{collection_plan['priority_tiers']['tier_1_immediate']['description']}\n")
        f.write(f"共{len(collection_plan['priority_tiers']['tier_1_immediate']['universities'])}所院校\n\n")

        for uni_info in collection_plan['priority_tiers']['tier_1_immediate']['universities']:
            f.write(f"- {uni_info['name']} ({uni_info['category']})\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("二、中优先级（1周内收集）\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{collection_plan['priority_tiers']['tier_2_week']['description']}\n")
        f.write(f"共{len(collection_plan['priority_tiers']['tier_2_week']['universities'])}所院校\n\n")

        for uni_info in collection_plan['priority_tiers']['tier_2_week']['universities']:
            f.write(f"- {uni_info['name']} ({uni_info['category']})\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("三、低优先级（1个月内收集）\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{collection_plan['priority_tiers']['tier_3_month']['description']}\n")
        f.write(f"共{len(collection_plan['priority_tiers']['tier_3_month']['universities'])}所院校\n\n")

        for uni_info in collection_plan['priority_tiers']['tier_3_month']['universities']:
            f.write(f"- {uni_info['name']} ({uni_info['category']})\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("四、数据来源和字段要求\n")
        f.write("=" * 80 + "\n\n")

        f.write("推荐数据来源：\n")
        for source in collection_plan['data_sources']:
            f.write(f"  - {source}\n")

        f.write("\n必需字段：\n")
        for field in collection_plan['required_fields']:
            f.write(f"  - {field}\n")

    print(f"[OK] 文本收集计划已保存: {text_plan_file}")

    # 显示汇总
    tier_1_count = len(collection_plan['priority_tiers']['tier_1_immediate']['universities'])
    tier_2_count = len(collection_plan['priority_tiers']['tier_2_week']['universities'])
    tier_3_count = len(collection_plan['priority_tiers']['tier_3_month']['universities'])

    print(f"\n收集计划汇总：")
    print(f"  高优先级（立即）：{tier_1_count} 所")
    print(f"  中优先级（1周内）：{tier_2_count} 所")
    print(f"  低优先级（1月内）：{tier_3_count} 所")
    print(f"  总计：{tier_1_count + tier_2_count + tier_3_count} 所")

if __name__ == "__main__":
    # 合并数据
    merge_guangdong_data()

    # 生成收集计划
    generate_data_collection_plan()

    print(f"\n" + "=" * 80)
    print("数据处理完成")
    print("=" * 80)
    print("已生成以下文件：")
    print("1. backend/data/guangdong_universities_merged.json - 合并后的广东院校数据")
    print("2. backend/data/guangdong_universities_merged.csv - CSV格式数据")
    print("3. backend/data/guangdong_data_collection_plan.json - 数据收集计划")
    print("4. backend/data/guangdong_data_collection_plan.txt - 文本格式收集计划")
