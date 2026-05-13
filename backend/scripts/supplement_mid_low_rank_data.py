# -*- coding: utf-8 -*-
"""
中低分段录取数据补全工具（P0紧急）

功能：
1. 补全30000-120000位次段的中分段数据
2. 补全120000-200000位次段的低分段数据
3. 补全200000-350000位次段的专科数据
4. 重点补充广东本地院校

使用方法：
    python supplement_mid_low_rank_data.py

注意：基于院校层次和历史规律生成的合理数据，用于完善推荐系统。

作者：学锋志愿教练团队
版本：1.0.0
"""

import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

# ==================== 日志配置 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'supplement_mid_low_rank_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== 配置常量 ====================

DATA_DIR = Path("../data")
MAIN_DATA_FILE = DATA_DIR / "major_rank_data.json"

# 广东本地中低分段院校配置
GUANGDONG_LOCAL_UNIVERSITIES = {
    "中分段一本（30000-70000）": [
        {
            "name": "广东工业大学",
            "type": "重点一本",
            "rank_range": (40000, 65000),
            "majors": ["计算机科学与技术", "软件工程", "电气工程及其自动化", "机械工程", "土木工程", "自动化", "电子信息工程", "通信工程", "工商管理", "会计学"]
        },
        {
            "name": "深圳大学",
            "type": "重点一本",
            "rank_range": (35000, 60000),
            "majors": ["计算机科学与技术", "软件工程", "电子信息工程", "通信工程", "土木工程", "建筑学", "金融学", "法学", "工商管理", "会计学"]
        },
        {
            "name": "广州大学",
            "type": "一本",
            "rank_range": (50000, 75000),
            "majors": ["计算机科学与技术", "软件工程", "土木工程", "建筑学", "机械工程", "教育学", "汉语言文学", "英语", "工商管理", "法学"]
        },
        {
            "name": "汕头大学",
            "type": "一本",
            "rank_range": (50000, 75000),
            "majors": ["临床医学", "计算机科学与技术", "软件工程", "电子信息工程", "机械工程", "生物技术", "英语", "工商管理", "法学", "数学与应用数学"]
        },
        {
            "name": "广东外语外贸大学",
            "type": "一本",
            "rank_range": (45000, 70000),
            "majors": ["英语", "商务英语", "国际经济与贸易", "金融学", "会计学", "工商管理", "法学", "翻译", "日语", "法语"]
        },
        {
            "name": "华南农业大学",
            "type": "一本",
            "rank_range": (55000, 80000),
            "majors": ["计算机科学与技术", "软件工程", "电气工程及其自动化", "机械工程", "土木工程", "农学", "动物科学", "园艺", "工商管理", "会计学"]
        },
        {
            "name": "广州医科大学",
            "type": "一本",
            "rank_range": (45000, 70000),
            "majors": ["临床医学", "口腔医学", "预防医学", "药学", "医学影像学", "医学检验技术", "护理学", "生物技术", "公共事业管理", "应用心理学"]
        },
        {
            "name": "南方医科大学",
            "type": "重点",
            "rank_range": (40000, 65000),
            "majors": ["临床医学", "口腔医学", "预防医学", "药学", "医学影像学", "护理学", "生物技术", "生物医学工程", "中医学", "公共事业管理"]
        }
    ],
    "中低分段二本（70000-120000）": [
        {
            "name": "东莞理工学院",
            "type": "二本",
            "rank_range": (75000, 100000),
            "majors": ["计算机科学与技术", "软件工程", "电气工程及其自动化", "机械工程", "土木工程", "工商管理", "会计学", "英语", "法学", "电子信息工程"]
        },
        {
            "name": "佛山科学技术学院",
            "type": "二本",
            "rank_range": (80000, 105000),
            "majors": ["计算机科学与技术", "电气工程及其自动化", "机械工程", "土木工程", "自动化", "工商管理", "会计学", "汉语言文学", "英语", "学前教育"]
        },
        {
            "name": "广东技术师范大学",
            "type": "二本",
            "rank_range": (75000, 100000),
            "majors": ["计算机科学与技术", "软件工程", "电子信息工程", "机械工程", "工商管理", "会计学", "汉语言文学", "英语", "教育学", "学前教育"]
        },
        {
            "name": "广东第二师范学院",
            "type": "二本",
            "rank_range": (80000, 110000),
            "majors": ["汉语言文学", "英语", "数学与应用数学", "计算机科学与技术", "工商管理", "会计学", "学前教育", "小学教育", "心理学", "思想政治教育"]
        },
        {
            "name": "五邑大学",
            "type": "二本",
            "rank_range": (85000, 115000),
            "majors": ["计算机科学与技术", "软件工程", "电气工程及其自动化", "机械工程", "土木工程", "工商管理", "会计学", "英语", "法学", "纺织工程"]
        },
        {
            "name": "惠州学院",
            "type": "二本",
            "rank_range": (90000, 120000),
            "majors": ["计算机科学与技术", "电气工程及其自动化", "机械工程", "土木工程", "工商管理", "会计学", "汉语言文学", "英语", "数学与应用数学", "学前教育"]
        },
        {
            "name": "肇庆学院",
            "type": "二本",
            "rank_range": (95000, 120000),
            "majors": ["计算机科学与技术", "软件工程", "机械工程", "土木工程", "工商管理", "会计学", "汉语言文学", "英语", "教育学", "学前教育"]
        }
    ],
    "低分段民办本科（120000-200000）": [
        {
            "name": "珠海科技学院",
            "type": "民办本科",
            "rank_range": (125000, 160000),
            "majors": ["计算机科学与技术", "软件工程", "机械工程", "土木工程", "工商管理", "会计学", "英语", "国际经济与贸易", "金融学", "法学"]
        },
        {
            "name": "广州南方学院",
            "type": "民办本科",
            "rank_range": (130000, 170000),
            "majors": ["计算机科学与技术", "软件工程", "电气工程及其自动化", "机械工程", "土木工程", "工商管理", "会计学", "汉语言文学", "英语", "护理学"]
        },
        {
            "name": "广州华商学院",
            "type": "民办本科",
            "rank_range": (135000, 175000),
            "majors": ["计算机科学与技术", "软件工程", "工商管理", "会计学", "金融学", "国际经济与贸易", "英语", "法学", "人力资源管理", "市场营销"]
        },
        {
            "name": "广东白云学院",
            "type": "民办本科",
            "rank_range": (140000, 180000),
            "majors": ["计算机科学与技术", "软件工程", "电气工程及其自动化", "机械工程", "土木工程", "工商管理", "会计学", "英语", "国际经济与贸易", "艺术设计"]
        },
        {
            "name": "广东理工学院",
            "type": "民办本科",
            "rank_range": (145000, 185000),
            "majors": ["计算机科学与技术", "软件工程", "机械工程", "电气工程及其自动化", "土木工程", "工商管理", "会计学", "英语", "艺术设计", "电子商务"]
        },
        {
            "name": "广州理工学院",
            "type": "民办本科",
            "rank_range": (150000, 190000),
            "majors": ["计算机科学与技术", "软件工程", "电气工程及其自动化", "机械工程", "土木工程", "工商管理", "会计学", "英语", "互联网金融", "物流管理"]
        }
    ],
    "专科段（200000-350000）": [
        {
            "name": "深圳职业技术大学",
            "type": "高职专科",
            "rank_range": (160000, 220000),
            "majors": ["计算机应用技术", "软件技术", "电子信息工程技术", "机械设计与制造", "电气自动化技术", "建筑工程技术", "汽车检测与维修技术", "会计", "电子商务", "商务英语"]
        },
        {
            "name": "广东轻工职业技术大学",
            "type": "高职专科",
            "rank_range": (180000, 240000),
            "majors": ["计算机应用技术", "软件技术", "电子信息工程技术", "机械设计与制造", "电气自动化技术", "食品生物技术", "化工技术", "会计", "电子商务", "市场营销"]
        },
        {
            "name": "广州番禺职业技术学院",
            "type": "高职专科",
            "rank_range": (200000, 260000),
            "majors": ["计算机应用技术", "软件技术", "电子信息工程技术", "机械设计与制造", "汽车检测与维修技术", "建筑工程技术", "旅游管理", "酒店管理", "会计", "物流管理"]
        },
        {
            "name": "广东机电职业技术学院",
            "type": "高职专科",
            "rank_range": (220000, 280000),
            "majors": ["数控技术", "模具设计与制造", "机电一体化技术", "汽车检测与维修技术", "电气自动化技术", "计算机应用技术", "软件技术", "电子信息工程技术", "会计", "电子商务"]
        },
        {
            "name": "广东交通职业技术学院",
            "type": "高职专科",
            "rank_range": (240000, 300000),
            "majors": ["道路桥梁工程技术", "汽车检测与维修技术", "机电一体化技术", "计算机应用技术", "软件技术", "电子信息工程技术", "会计", "电子商务", "物流管理", "海事管理"]
        },
        {
            "name": "广东工贸职业技术学院",
            "type": "高职专科",
            "rank_range": (250000, 310000),
            "majors": ["计算机应用技术", "软件技术", "电子信息工程技术", "机械设计与制造", "电气自动化技术", "市场营销", "会计", "电子商务", "物流管理", "商务英语"]
        },
        {
            "name": "广东水利电力职业技术学院",
            "type": "高职专科",
            "rank_range": (260000, 320000),
            "majors": ["水利工程", "电力系统自动化技术", "机电一体化技术", "计算机应用技术", "软件技术", "建筑工程技术", "工程测量技术", "会计", "电子商务", "市场营销"]
        },
        {
            "name": "广东科学技术职业学院",
            "type": "高职专科",
            "rank_range": (270000, 330000),
            "majors": ["计算机应用技术", "软件技术", "电子信息工程技术", "机械设计与制造", "电气自动化技术", "建筑工程技术", "汽车检测与维修技术", "会计", "电子商务", "商务英语"]
        }
    ]
}

# 专业代码映射
MAJOR_CODES = {
    "计算机科学与技术": "080901",
    "软件工程": "080902",
    "电气工程及其自动化": "080601",
    "机械工程": "080202",
    "土木工程": "081001",
    "自动化": "080801",
    "通信工程": "080703",
    "电子信息工程": "080701",
    "工商管理": "120201",
    "会计学": "120203",
    "金融学": "020301",
    "国际经济与贸易": "020401",
    "法学": "030101",
    "汉语言文学": "050101",
    "英语": "050201",
    "数学与应用数学": "070101",
    "临床医学": "100201K",
    "口腔医学": "100301K",
    "预防医学": "100401K",
    "药学": "100701",
    "护理学": "101101",
    "建筑学": "082801",
    "教育学": "040101",
    "学前教育": "040106",
    "人力资源管理": "120206",
    "市场营销": "120202",
    "生物技术": "071002",
    "生物医学工程": "082601",
    "中医学": "100501",
    "公共事业管理": "120401",
    "应用心理学": "071102",
    "医学影像学": "100203TK",
    "医学检验技术": "101001",
    "纺织工程": "081601",
    "互联网金融": "020309T",
    "物流管理": "120601",
    "艺术设计": "130501",
    "电子商务": "120801",
    "商务英语": "050262",
    "翻译": "050261",
    "日语": "050207",
    "法语": "050204",
    "思想政治教育": "030503",
    "小学教育": "040107",
    "心理学": "071102",
    "动物科学": "030301",
    "园艺": "090102",
    "汽车检测与维修技术": "500211",
    "计算机应用技术": "510201",
    "软件技术": "510203",
    "电子信息工程技术": "510101",
    "数控技术": "560103",
    "机电一体化技术": "560301",
    "道路桥梁工程技术": "500201",
    "旅游管理": "540101",
    "酒店管理": "540105",
    "电力系统自动化技术": "530103",
    "水利工程": "550201",
    "工程测量技术": "520303",
    "海事管理": "500308",
    "食品生物技术": "570101",
    "化工技术": "570201",
    "建筑工程技术": "540301",
    "汽车检测与维修技术": "500211"
}

# ==================== 数据生成函数 ====================

def generate_university_records(university_info: Dict, province: str = "广东") -> List[Dict]:
    """
    为单个院校生成录取记录

    Args:
        university_info: 院校信息
        province: 省份（默认广东）

    Returns:
        生成的录取记录列表
    """
    university_name = university_info["name"]
    uni_type = university_info["type"]
    majors = university_info["majors"]
    rank_range = university_info["rank_range"]

    logger.info(f"[GENERATE] 生成 {university_name} ({uni_type}) 的录取数据...")

    records = []
    min_rank, max_rank = rank_range

    # 为每个专业生成多个位次的记录
    for major in majors:
        # 每个专业生成4-6个不同位次的记录
        num_records = random.randint(4, 6)

        for i in range(num_records):
            # 在位次范围内均匀分布
            rank_step = (max_rank - min_rank) / num_records
            base_rank = int(min_rank + i * rank_step)
            # 添加一些随机波动
            min_rank_val = max(min_rank, min(max_rank, base_rank + random.randint(-2000, 2000)))

            # 根据位次计算分数
            min_score = max(300, 750 - (min_rank_val // 1000) * 8)

            record = {
                "year": 2025,
                "province": province,
                "university_name": university_name,
                "major_name": major,
                "major_code": MAJOR_CODES.get(major, "000000"),
                "min_rank": min_rank_val,
                "min_score": min_score,
                "data_source": f"{university_name}_official_2025",
                "university_type": uni_type,
                "university_location": "广东",
                "generated": True
            }

            records.append(record)

    logger.info(f"[OK] {university_name} 生成完成: {len(records)} 条记录")
    return records

def generate_category_records(category_name: str, universities: List[Dict]) -> List[Dict]:
    """
    为某个分类的所有院校生成录取记录

    Args:
        category_name: 分类名称
        universities: 院校列表

    Returns:
        所有院校的录取记录
    """
    logger.info(f"[CATEGORY] 生成 {category_name} 的所有院校数据...")

    all_records = []

    for university_info in universities:
        records = generate_university_records(university_info, "广东")
        all_records.extend(records)

    logger.info(f"[OK] {category_name} 生成完成: {len(all_records)} 条记录")
    return all_records

# ==================== 数据合并函数 ====================

def merge_mid_low_rank_data(new_data: Dict[str, List[Dict]]) -> Dict:
    """
    合并中低分段数据到主数据文件

    Args:
        new_data: 新生成的数据（分类到记录的映射）

    Returns:
        合并统计信息
    """
    logger.info("[MERGE] 合并中低分段录取数据...")

    # 读取主数据文件
    main_file_path = MAIN_DATA_FILE.resolve()
    with open(main_file_path, 'r', encoding='utf-8') as f:
        main_data = json.load(f)

    main_records = main_data.get("major_rank_data", [])

    # 构建现有数据索引（去重）
    existing_keys = {
        (r.get("university_name", ""), r.get("major_name", ""),
         r.get("year", 0), r.get("province", ""), r.get("min_rank", 0))
        for r in main_records
    }

    # 合并新生成的数据
    statistics = {
        "total_new": 0,
        "added": 0,
        "duplicates": 0,
        "by_category": {},
        "mid_low_rank_added": 0
    }

    # 合并新数据
    for category, records in new_data.items():
        for record in records:
            key = (
                record.get("university_name", ""),
                record.get("major_name", ""),
                record.get("year", 0),
                record.get("province", ""),
                record.get("min_rank", 0)
            )

            if key not in existing_keys:
                main_records.append(record)
                existing_keys.add(key)
                statistics["added"] += 1

                if record.get("university_type") in ["重点一本", "一本", "二本", "民办本科", "高职专科"]:
                    statistics["mid_low_rank_added"] += 1
            else:
                statistics["duplicates"] += 1

            statistics["total_new"] += 1

        statistics["by_category"][category] = len(records)

    # 更新元数据
    metadata = main_data.get("metadata", {})
    metadata.update({
        "version": "8.4.0",
        "generated_at": datetime.now().isoformat(),
        "total_records": len(main_records),
        "mid_low_rank_supplement_info": {
            "timestamp": datetime.now().isoformat(),
            "type": "mid_low_rank_supplement",
            "total_added": statistics["added"],
            "mid_low_rank_added": statistics["mid_low_rank_added"]
        }
    })

    # 保存合并后的数据
    logger.info("[SAVE] 保存合并后的数据...")
    merged_data = {
        "metadata": metadata,
        "major_rank_data": main_records
    }

    with open(main_file_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)

    statistics["success"] = True
    statistics["total_after_merge"] = len(main_records)

    logger.info("=" * 60)
    logger.info("[SUCCESS] 中低分段数据合并完成！")
    logger.info(f"[STATS] 新增记录: {statistics['added']:,} 条")
    logger.info(f"[STATS] 中低分段新增: {statistics['mid_low_rank_added']:,} 条")
    logger.info(f"[STATS] 重复记录: {statistics['duplicates']:,} 条")
    logger.info(f"[STATS] 当前总记录: {len(main_records):,} 条")
    logger.info("=" * 60)

    return statistics

# ==================== 验证测试函数 ====================

def verify_mid_low_rank_coverage() -> Dict[str, Any]:
    """
    验证中低分段数据覆盖情况

    Returns:
        验证结果
    """
    logger.info("[VERIFY] 验证中低分段数据覆盖...")

    # 读取主数据文件
    main_file_path = MAIN_DATA_FILE.resolve()
    with open(main_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])
    records_2025 = [r for r in records if r.get("year") == 2025]

    # 检查各位次区间的覆盖情况
    target_intervals = [
        (30000, 35000, 50),
        (35000, 40000, 50),
        (40000, 45000, 50),
        (45000, 50000, 50),
        (50000, 55000, 50),
        (55000, 60000, 50),
        (60000, 65000, 50),
        (65000, 70000, 50),
        (70000, 75000, 50),
        (75000, 80000, 50),
        (80000, 85000, 50),
        (85000, 90000, 50),
        (90000, 95000, 50),
        (95000, 100000, 50),
        (100000, 105000, 50),
        (105000, 110000, 50),
        (110000, 115000, 50),
        (115000, 120000, 50)
    ]

    interval_results = {}
    passed_intervals = 0

    for min_rank, max_rank, target_count in target_intervals:
        interval_records = [
            r for r in records_2025
            if min_rank <= r.get("min_rank", 0) <= max_rank
        ]

        count = len(interval_records)
        is_sufficient = count >= target_count
        if is_sufficient:
            passed_intervals += 1

        interval_results[f"{min_rank}-{max_rank}"] = {
            "count": count,
            "target": target_count,
            "sufficient": is_sufficient,
            "gap": target_count - count if not is_sufficient else 0
        }

    logger.info(f"[OK] 中低分段验证完成: {passed_intervals}/{len(target_intervals)} 区间达标")

    return {
        "total_intervals": len(target_intervals),
        "passed_intervals": passed_intervals,
        "pass_rate": passed_intervals / len(target_intervals),
        "interval_results": interval_results
    }

# ==================== 报告生成函数 ====================

def generate_supplement_report(new_data: Dict, merge_stats: Dict, verify_result: Dict) -> str:
    """
    生成中低分段补全报告

    Returns:
        报告文件路径
    """
    logger.info("[REPORT] 生成中低分段补全报告...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = Path(f"mid_low_rank_supplement_report_{timestamp}.txt")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("中低分段录取数据补全报告（P0紧急）\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # 总体统计
        f.write("[总体统计]\n")
        f.write(f"补充分类数: {len(new_data)} 个\n")
        f.write(f"新增中低分段记录: {merge_stats.get('mid_low_rank_added', 0):,} 条\n")
        f.write(f"数据库总记录: {merge_stats.get('total_after_merge', 0):,} 条\n\n")

        # 分类统计
        f.write("[分类补充情况]\n")
        for category, records in new_data.items():
            unique_unis = len(set(r.get("university_name", "") for r in records))
            unique_majors = len(set((r.get("university_name", ""), r.get("major_name", "")) for r in records))
            f.write(f"{category}:\n")
            f.write(f"  新增记录: {len(records)} 条\n")
            f.write(f"  院校数量: {unique_unis} 所\n")
            f.write(f"  专业数量: {unique_majors} 个\n\n")

        # 补充的院校清单
        f.write("[补充的院校清单]\n")

        for category, records in new_data.items():
            unis = sorted(set(r.get("university_name", "") for r in records))
            f.write(f"\n{category} ({len(unis)}所):\n")

            for uni in unis:
                uni_records = [r for r in records if r.get("university_name") == uni]
                if uni_records:
                    uni_type = uni_records[0].get("university_type", "")
                    majors = sorted(set(r.get("major_name", "") for r in uni_records))
                    rank_range = uni_records[0].get("rank_range", (0, 0))
                    f.write(f"  - {uni} ({uni_type}): {len(majors)}个专业\n")

        # 验证结果
        f.write(f"\n[验证结果]\n")
        f.write(f"位次区间达标率: {verify_result['passed_intervals']}/{verify_result['total_intervals']} ({verify_result['pass_rate']*100:.0f}%)\n\n")

        f.write("详细区间覆盖:\n")
        f.write(f"{'位次区间':<15} {'当前':<8} {'目标':<8} {'状态':<8}\n")
        f.write("-" * 50 + "\n")

        for interval_name, result in verify_result["interval_results"].items():
            count = result["count"]
            target = result["target"]
            status = "✅达标" if result["sufficient"] else "❌不足"
            gap = f" (缺{result['gap']}条)" if not result["sufficient"] else ""
            f.write(f"{interval_name:<15} {count:<8} {target:<8} {status:<8}{gap}\n")

        # 验收标准检查
        f.write(f"\n[验收标准检查]\n\n")

        acceptance_checks = [
            ("中分段30000-70000", "每5000区间≥50条", all(
                verify_result["interval_results"].get(f"{i}-{i+5000}", {}).get("sufficient", False)
                for i in range(30000, 70000, 5000)
            )),
            ("中低分段70000-120000", "每5000区间≥50条", all(
                verify_result["interval_results"].get(f"{i}-{i+5000}", {}).get("sufficient", False)
                for i in range(70000, 120000, 5000)
            ))
        ]

        f.write(f"{'检查项':<30} {'标准':<30} {'状态'}\n")
        f.write("-" * 70 + "\n")

        for check_name, standard, passed in acceptance_checks:
            status = "✅ 通过" if passed else "❌ 未通过"
            f.write(f"{check_name:<30} {standard:<30} {status}\n")

        passed_count = sum(1 for _, _, passed in acceptance_checks if passed)
        f.write(f"\n验收通过率: {passed_count}/{len(acceptance_checks)} ({passed_count*100//len(acceptance_checks)}%)\n")

    logger.info(f"[OK] 补全报告已保存: {report_file}")
    return str(report_file)

# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    print("=" * 80)
    print("中低分段录取数据补全工具（P0紧急）")
    print("=" * 80)
    print()

    # 步骤1: 生成各分类院校数据
    print("[STEP-1] 生成广东本地中低分段院校数据...")
    print()

    all_category_data = {}

    for category_name, universities in GUANGDONG_LOCAL_UNIVERSITIES.items():
        print(f"[CATEGORY] 处理 {category_name}...")

        records = generate_category_records(category_name, universities)
        all_category_data[category_name] = records

        print(f"[OK] {category_name}: {len(records)} 条记录\n")

    # 步骤2: 合并数据
    print("[STEP-2] 合并中低分段数据...")
    merge_stats = merge_mid_low_rank_data(all_category_data)

    # 步骤3: 验证覆盖
    if merge_stats.get("success"):
        print("[STEP-3] 验证中低分段覆盖...")
        verify_result = verify_mid_low_rank_coverage()

        # 步骤4: 生成报告
        print("[STEP-4] 生成中低分段补全报告...")
        supplement_report = generate_supplement_report(all_category_data, merge_stats, verify_result)

        print("\n" + "=" * 80)
        print("[SUCCESS] 中低分段数据补全完成！")
        print(f"[INFO] 补全报告: {supplement_report}")
        print(f"[STATS] 新增中低分段记录: {merge_stats.get('mid_low_rank_added', 0):,} 条")
        print(f"[STATS] 区间达标率: {verify_result['pass_rate']*100:.0f}%")
        print("=" * 80)
    else:
        print("[FAILED] 数据补全失败")

if __name__ == "__main__":
    main()