#!/usr/bin/env python3
"""
分析当前数据中各类院校的覆盖情况
"""
import json
from pathlib import Path
from collections import defaultdict, Counter

# 院校类型分类关键词
TYPE_KEYWORDS = {
    "985": [
        "清华大学", "北京大学", "复旦大学", "上海交通大学", "浙江大学",
        "中国科学技术大学", "南京大学", "华中科技大学", "武汉大学",
        "西安交通大学", "哈尔滨工业大学", "中山大学", "华南理工大学",
        "北京理工大学", "北京航空航天大学", "同济大学", "南开大学",
        "天津大学", "大连理工大学", "东北大学", "吉林大学", "四川大学",
        "重庆大学", "电子科技大学", "西北工业大学", "华东师范大学",
        "中南大学", "湖南大学", "山东大学", "中国海洋大学", "中国海洋大学"
    ],
    "211": [
        "暨南大学", "华南师范大学", "南昌大学", "广西大学", "福州大学",
        "郑州大学", "云南大学", "贵州大学", "海南大学", "湖南师范大学",
        "武汉理工大学", "华中师范大学", "中南财经政法大学", "西南交通大学",
        "西南财经大学", "西安电子科技大学", "北京邮电大学", "上海财经大学",
        "中央财经大学", "对外经济贸易大学", "中国政法大学", "北京外国语大学",
        "上海外国语大学", "中央民族大学", "中国农业大学", "大连海事大学",
        "东北林业大学", "东北农业大学", "长安大学", "西北大学", "西北农林科技大学",
        "合肥工业大学", "安徽大学", "中国地质大学(武汉)", "中国地质大学(北京)",
        "中国石油大学(华东)", "中国石油大学(北京)", "中国矿业大学", "河海大学",
        "江南大学", "南京师范大学", "中国药科大学", "南京航空航天大学",
        "南京理工大学", "东华大学", "西南大学", "四川农业大学", "哈尔滨工程大学"
    ],
    "广东重点本科": [
        "广东工业大学", "深圳大学", "广州大学", "汕头大学",
        "广东外语外贸大学", "华南农业大学", "广州医科大学", "南方医科大学"
    ],
    "广东普通本科": [
        "东莞理工学院", "佛山科学技术学院", "五邑大学", "惠州学院",
        "肇庆学院", "广东石油化工学院", "韶关学院", "嘉应学院",
        "韩山师范学院", "岭南师范学院", "广东技术师范大学", "广东第二师范学院"
    ],
    "广东独立学院": [
        "珠海科技学院", "广州南方学院", "广州华商学院", "广东白云学院",
        "广东理工学院", "广州理工学院", "东莞城市学院", "广州新华学院",
        "电子科技大学中山学院", "北京理工大学珠海学院"
    ],
    "广东民办本科": [
        "广东科技学院", "广州软件学院", "广州工商学院", "广东东软学院",
        "广东培正学院", "广州商学院", "广东白云学院", "广东技术师范大学"
    ],
    "广东高职专科": [
        "深圳职业技术大学", "广东轻工职业技术学院", "广州番禺职业技术学院",
        "广东机电职业技术学院", "广东交通职业技术学院", "广东工贸职业技术学院",
        "广东水利电力职业技术学院", "广东科学技术职业学院", "广东职业技术学院",
        "广东邮电职业技术学院", "广东司法警官职业学院", "广东体育职业技术学院",
        "广东建设职业技术学院", "广东食品药品职业技术学院", "广东环境保护工程职业学院",
        "广东松山职业技术学院", "广东农工商职业技术学院", "广东女子职业技术学院"
    ]
}

def analyze_coverage():
    """分析院校类型覆盖情况"""
    print("=== 当前数据中的院校类型覆盖情况分析 ===")

    # 加载数据
    data_path = Path("../data/major_rank_data.json")
    if not data_path.exists():
        data_path = Path("backend/data/major_rank_data.json")

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])
    print(f"\n总数据量：{len(records)} 条")

    # 提取现有院校
    existing_universities = set()
    for record in records:
        university = record.get("university_name", "")
        if university:
            existing_universities.add(university)

    print(f"总院校数：{len(existing_universities)} 所")

    # 分析各类型院校覆盖情况
    print(f"\n=== 各类型院校覆盖情况 ===")
    coverage_report = {}

    for category, universities in TYPE_KEYWORDS.items():
        covered = [uni for uni in universities if uni in existing_universities]
        missing = [uni for uni in universities if uni not in existing_universities]
        coverage_rate = len(covered) / len(universities) * 100 if universities else 100

        coverage_report[category] = {
            "total": len(universities),
            "covered": len(covered),
            "missing": missing,
            "rate": coverage_rate,
            "covered_list": covered,
            "missing_list": missing
        }

        if coverage_rate >= 80:
            status = "[OK]"
        elif coverage_rate >= 50:
            status = "[WARN]"
        else:
            status = "[FAIL]"

        print(f"{status} {category}: {len(covered)}/{len(universities)} ({coverage_rate:.1f}%)")

        if missing:
            missing_display = missing[:3]
            if len(missing) > 3:
                missing_display.append(f"...等{len(missing)}所")
            print(f"   缺失: {', '.join(missing_display)}")

    # 统计所有院校的类型分布（基于名称推断）
    print(f"\n=== 数据中院校类型分布（基于名称推断）===")
    type_stats = defaultdict(int)

    # 首先统计明确包含985/211的院校
    for uni in existing_universities:
        is_985 = any(kw in uni for kw in TYPE_KEYWORDS["985"])
        is_211 = any(kw in uni for kw in TYPE_KEYWORDS["211"])

        if is_985:
            type_stats["985"] += 1
        elif is_211:
            type_stats["211"] += 1
        elif "学院" in uni or "大学" in uni:
            # 进一步细分
            if any(kw in uni for kw in ["师范", "农业", "医科", "财经", "外语", "工业", "理工"]):
                type_stats["特色院校"] += 1
            elif "学院" in uni:
                type_stats["普通本科"] += 1
            elif "大学" in uni:
                type_stats["普通本科"] += 1
            else:
                type_stats["其他"] += 1
        else:
            type_stats["其他"] += 1

    # 显示统计结果
    for type_name, count in sorted(type_stats.items(), key=lambda x: -x[1]):
        print(f"  {type_name}: {count} 所院校")

    return coverage_report, type_stats

if __name__ == "__main__":
    analyze_coverage()