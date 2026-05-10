#!/usr/bin/env python3
"""
分析10001-30000段位数据覆盖情况
"""
import json
from pathlib import Path
from collections import defaultdict, Counter
import pandas as pd

def analyze_rank_segment():
    print("=== 分析10001-30000段位数据覆盖情况 ===")

    # 1. 加载数据
    data_path = Path("data/major_rank_data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])

    # 2. 筛选10001-30000段位数据
    segment_records = []
    for record in records:
        min_rank = record.get("min_rank", 0)
        if 10000 < min_rank <= 30000:
            segment_records.append(record)

    print(f"\n10001-30000段位数据：{len(segment_records)} 条")

    # 3. 分析院校分布
    university_counter = Counter()
    category_counter = Counter()
    province_counter = Counter()

    for record in segment_records:
        university = record.get("university_name", "")
        category = record.get("category", "")
        province = record.get("province", "")

        university_counter[university] += 1
        if category:
            category_counter[category] += 1
        if province:
            province_counter[province] += 1

    print(f"\n院校数量：{len(university_counter)} 所")
    print(f"\n科类分布：")
    for category, count in category_counter.most_common():
        print(f"  {category}: {count} 条")

    print(f"\n省份分布（前10）：")
    for province, count in province_counter.most_common(10):
        print(f"  {province}: {count} 条")

    # 4. 分析专业覆盖
    major_counter = Counter()
    for record in segment_records:
        major = record.get("major_name", "")
        if major:
            major_counter[major] += 1

    print(f"\n专业数量：{len(major_counter)} 个")
    print(f"\n热门专业（前20）：")
    for major, count in major_counter.most_common(20):
        print(f"  {major}: {count} 条")

    # 5. 识别211院校
    # 中国211院校名单
    university_211_list = [
        "北京大学", "清华大学", "复旦大学", "上海交通大学", "南京大学",
        "浙江大学", "中国科学技术大学", "中国人民大学", "北京理工大学",
        "北京航空航天大学", "中央财经大学", "上海财经大学", "对外经济贸易大学",
        "同济大学", "华东师范大学", "南开大学", "天津大学",
        "大连理工大学", "东北大学", "吉林大学", "哈尔滨工业大学",
        "哈尔滨工程大学", "南京航空航天大学", "南京理工大学", "河海大学",
        "江南大学", "南京师范大学", "中国药科大学", "东南大学",
        "浙江大学", "安徽大学", "合肥工业大学", "厦门大学",
        "山东大学", "中国海洋大学", "中国石油大学(华东)", "武汉大学",
        "华中科技大学", "中国地质大学(武汉)", "武汉理工大学", "华中师范大学",
        "华中农业大学", "中南财经政法大学", "湖南大学", "中南大学",
        "湖南师范大学", "中山大学", "华南理工大学", "暨南大学",
        "华南师范大学", "广西大学", "四川大学", "重庆大学",
        "西南交通大学", "电子科技大学", "西南大学", "四川农业大学",
        "云南大学", "贵州大学", "西北大学", "西安交通大学",
        "西北工业大学", "西安电子科技大学", "长安大学", "西北农林科技大学",
        "兰州大学", "新疆大学", "内蒙古大学", "海南大学",
        "郑州大学", "南昌大学", "福州大学"
    ]

    # 统计211院校覆盖
    university_211_in_data = set()
    university_211_missing = set()

    for uni_211 in university_211_list:
        if uni_211 in university_counter:
            university_211_in_data.add(uni_211)
        else:
            university_211_missing.add(uni_211)

    print(f"\n=== 211院校覆盖情况 ===")
    print(f"总211院校数：{len(university_211_list)} 所")
    print(f"数据中包含的211院校：{len(university_211_in_data)} 所")
    print(f"数据中缺失的211院校：{len(university_211_missing)} 所")

    if university_211_missing:
        print(f"\n缺失的211院校：")
        for uni in sorted(university_211_missing):
            print(f"  - {uni}")

    # 6. 分析现有211院校的专业覆盖
    university_211_details = {}
    for record in segment_records:
        university = record.get("university_name", "")
        if university in university_211_in_data:
            if university not in university_211_details:
                university_211_details[university] = {
                    "total_records": 0,
                    "majors": set(),
                    "categories": set()
                }
            university_211_details[university]["total_records"] += 1
            university_211_details[university]["majors"].add(record.get("major_name", ""))
            university_211_details[university]["categories"].add(record.get("category", ""))

    print(f"\n=== 现有211院校专业覆盖（按专业数量排序）===")
    university_211_sorted = sorted(university_211_details.items(),
                                  key=lambda x: len(x[1]["majors"]),
                                  reverse=True)

    for university, details in university_211_sorted[:20]:
        print(f"{university}: {len(details['majors'])} 个专业, {details['total_records']} 条记录")

    # 7. 数据质量检查
    print(f"\n=== 数据质量检查 ===")

    # 检查缺失字段
    missing_university = 0
    missing_major = 0
    missing_score = 0
    missing_rank = 0

    for record in segment_records:
        if not record.get("university_name"):
            missing_university += 1
        if not record.get("major_name"):
            missing_major += 1
        if not record.get("min_score"):
            missing_score += 1
        if not record.get("min_rank"):
            missing_rank += 1

    total = len(segment_records)
    print(f"缺失院校名称：{missing_university}/{total} ({missing_university/total*100:.2f}%)")
    print(f"缺失专业名称：{missing_major}/{total} ({missing_major/total*100:.2f}%)")
    print(f"缺失分数：{missing_score}/{total} ({missing_score/total*100:.2f}%)")
    print(f"缺失位次：{missing_rank}/{total} ({missing_rank/total*100:.2f}%)")

    # 8. 位次分布分析
    rank_distribution = defaultdict(int)
    for record in segment_records:
        min_rank = record.get("min_rank", 0)
        if 10000 < min_rank <= 15000:
            rank_distribution["10001-15000"] += 1
        elif 15000 < min_rank <= 20000:
            rank_distribution["15001-20000"] += 1
        elif 20000 < min_rank <= 25000:
            rank_distribution["20001-25000"] += 1
        elif 25000 < min_rank <= 30000:
            rank_distribution["25001-30000"] += 1

    print(f"\n=== 位次细分分布 ===")
    for segment, count in sorted(rank_distribution.items()):
        percentage = count / len(segment_records) * 100
        print(f"{segment}: {count} 条 ({percentage:.1f}%)")

    # 9. 生成补充建议
    print(f"\n=== 数据补充建议 ===")

    # 需要补充的211院校
    if university_211_missing:
        print(f"建议补充以下{len(university_211_missing)}所211院校的专业数据：")
        for uni in sorted(university_211_missing):
            print(f"  - {uni}")

    # 专业覆盖较少的211院校
    low_coverage_211 = [(uni, details) for uni, details in university_211_details.items()
                        if len(details["majors"]) < 10]
    if low_coverage_211:
        print(f"\n建议补充以下{len(low_coverage_211)}所211院校的更多专业：")
        for uni, details in sorted(low_coverage_211, key=lambda x: len(x[1]["majors"])):
            print(f"  - {uni} (当前{len(details['majors'])}个专业)")

    return {
        "total_records": len(segment_records),
        "university_count": len(university_counter),
        "major_count": len(major_counter),
        "university_211_in_data": len(university_211_in_data),
        "university_211_missing": len(university_211_missing),
        "university_211_list": list(university_211_missing)
    }

if __name__ == "__main__":
    result = analyze_rank_segment()