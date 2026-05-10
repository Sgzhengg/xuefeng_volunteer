#!/usr/bin/env python3
"""
检查各类院校在不同位次段的覆盖情况
"""
import json
from pathlib import Path
from collections import defaultdict

# 位次段定义
RANK_SEGMENTS = {
    "超高分段 (1-10000)": 10000,
    "高分段 (10001-30000)": 30000,
    "中高分段 (30001-70000)": 70000,
    "中分段 (70001-120000)": 120000,
    "中低分段 (120001-200000)": 200000,
    "低分段 (200001-350000)": 350000
}

# 院校类型分类关键词
TYPE_KEYWORDS = {
    "985": [
        "清华大学", "北京大学", "复旦大学", "上海交通大学", "浙江大学",
        "中国科学技术大学", "南京大学", "华中科技大学", "武汉大学",
        "西安交通大学", "哈尔滨工业大学", "中山大学", "华南理工大学",
        "北京理工大学", "北京航空航天大学", "同济大学", "南开大学",
        "天津大学", "大连理工大学", "东北大学", "吉林大学", "四川大学",
        "重庆大学", "电子科技大学", "西北工业大学", "华东师范大学",
        "中南大学", "湖南大学", "山东大学", "中国海洋大学"
    ],
    "211": [
        "暨南大学", "华南师范大学", "南昌大学", "广西大学", "福州大学",
        "郑州大学", "云南大学", "贵州大学", "海南大学", "湖南师范大学",
        "武汉理工大学", "华中师范大学", "中南财经政法大学", "西南交通大学",
        "西南财经大学", "西安电子科技大学", "北京邮电大学", "上海财经大学",
        "中央财经大学", "对外经济贸易大学", "中国政法大学", "北京外国语大学",
        "上海外国语大学", "中央民族大学", "中国农业大学", "大连海事大学",
        "东北林业大学", "东北农业大学", "长安大学", "西北大学", "西北农林科技大学",
        "合肥工业大学", "安徽大学", "中国地质大学", "中国石油大学", "中国矿业大学",
        "河海大学", "江南大学", "南京师范大学", "中国药科大学", "南京航空航天大学",
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
        "广东培正学院", "广州商学院"
    ],
    "广东高职专科": [
        "深圳职业技术大学", "广东轻工职业技术学院", "广州番禺职业技术学院",
        "广东机电职业技术学院", "广东交通职业技术学院", "广东工贸职业技术学院",
        "广东水利电力职业技术学院", "广东科学技术职业学院", "广东职业技术学院",
        "广东邮电职业技术学院", "广东司法警官职业学院"
    ]
}

def check_rank_coverage():
    """检查各类院校的位次段覆盖情况"""
    print("=== 各类院校位次段覆盖情况分析 ===")

    # 加载数据
    data_path = Path("../data/major_rank_data.json")
    if not data_path.exists():
        data_path = Path("backend/data/major_rank_data.json")

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])
    print(f"\n总数据量：{len(records)} 条")

    # 按院校类型和位次段统计
    type_rank_stats = defaultdict(lambda: defaultdict(int))
    type_university_stats = defaultdict(lambda: defaultdict(set))

    for record in records:
        university = record.get("university_name", "")
        min_rank = record.get("min_rank", 0)

        if not university or not min_rank:
            continue

        # 确定院校类型
        university_type = "其他"
        for type_name, keywords in TYPE_KEYWORDS.items():
            if any(keyword in university for keyword in keywords):
                university_type = type_name
                break

        # 确定位次段
        rank_segment = None
        for segment_name, rank_limit in RANK_SEGMENTS.items():
            if min_rank <= rank_limit:
                rank_segment = segment_name
                break
        if not rank_segment:
            rank_segment = "超低分段 (>350000)"

        # 统计
        type_rank_stats[university_type][rank_segment] += 1
        type_university_stats[university_type][rank_segment].add(university)

    # 显示统计结果
    print(f"\n=== 各类院校在不同位次段的覆盖情况 ===")

    for type_name in ["985", "211", "广东重点本科", "广东普通本科", "广东独立学院", "广东民办本科", "广东高职专科", "其他"]:
        if type_name not in type_rank_stats:
            print(f"\n{type_name}: 无数据")
            continue

        print(f"\n{type_name}:")
        total_records = sum(type_rank_stats[type_name].values())
        print(f"  总记录数：{total_records}")

        for segment_name in RANK_SEGMENTS.keys():
            record_count = type_rank_stats[type_name].get(segment_name, 0)
            university_count = len(type_university_stats[type_name].get(segment_name, set()))
            percentage = record_count / total_records * 100 if total_records > 0 else 0

            status = "[OK]" if record_count > 0 else "[MISS]"
            print(f"  {status} {segment_name}: {record_count} 条记录, {university_count} 所院校 ({percentage:.1f}%)")

        # 检查超低分段
        low_segment = "超低分段 (>350000)"
        if low_segment in type_rank_stats[type_name]:
            record_count = type_rank_stats[type_name].get(low_segment, 0)
            university_count = len(type_university_stats[type_name].get(low_segment, set()))
            print(f"  [INFO] {low_segment}: {record_count} 条记录, {university_count} 所院校")

    # 生成覆盖问题报告
    print(f"\n=== 覆盖问题汇总 ===")

    issues = []

    # 检查广东重点本科覆盖
    if "广东重点本科" in type_rank_stats:
        guangdong_key_stats = type_rank_stats["广东重点本科"]
        high_rank_coverage = sum([guangdong_key_stats.get(s, 0) for s in list(RANK_SEGMENTS.keys())[:3]])
        if high_rank_coverage < 100:
            issues.append(f"广东重点本科在高分段（前7万位）覆盖不足：仅{high_rank_coverage}条记录")

    # 检查普通本科覆盖
    if "广东普通本科" in type_rank_stats:
        regular_coverage = sum(type_rank_stats["广东普通本科"].values())
        if regular_coverage < 50:
            issues.append(f"广东普通本科覆盖严重不足：仅{regular_coverage}条记录")

    # 检查独立学院覆盖
    if "广东独立学院" in type_rank_stats:
        independent_coverage = sum(type_rank_stats["广东独立学院"].values())
        if independent_coverage < 100:
            issues.append(f"广东独立学院覆盖不足：仅{independent_coverage}条记录")

    # 检查民办本科覆盖
    if "广东民办本科" in type_rank_stats:
        private_coverage = sum(type_rank_stats["广东民办本科"].values())
        if private_coverage < 50:
            issues.append(f"广东民办本科覆盖不足：仅{private_coverage}条记录")

    # 检查高职专科覆盖
    if "广东高职专科" in type_rank_stats:
        vocational_coverage = sum(type_rank_stats["广东高职专科"].values())
        if vocational_coverage < 200:
            issues.append(f"广东高职专科覆盖严重不足：仅{vocational_coverage}条记录")

    if issues:
        for issue in issues:
            print(f"  [ISSUE] {issue}")
    else:
        print("  [OK] 各类型院校覆盖基本充分")

    return type_rank_stats, type_university_stats

if __name__ == "__main__":
    check_rank_coverage()
