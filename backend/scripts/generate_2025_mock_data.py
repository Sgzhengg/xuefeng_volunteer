# -*- coding: utf-8 -*-
"""
2025年全国录取数据模拟生成工具

功能：
1. 基于真实规律生成2025年模拟录取数据
2. 按省份优先级和位次段要求分配数据
3. 确保数据分布符合实际规律
4. 用于测试和演示数据收集流程

使用方法：
    python generate_2025_mock_data.py

注意：这是模拟数据，仅用于测试。生产环境请使用真实投档线数据。

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
        logging.FileHandler(f'mock_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== 配置常量 ====================

DATA_DIR = Path("../data")
MAIN_DATA_FILE = DATA_DIR / "major_rank_data.json"
PROVINCE_DATA_DIR = DATA_DIR / "province_data_2025"

# 省份优先级配置
PROVINCE_CONFIG = {
    "广东": {"priority": "P0", "target_records": 15000, "rank_distribution": {1: 2000, 2: 4000, 3: 3000, 4: 3000, 5: 2000, 6: 1000}},
    "湖南": {"priority": "P0", "target_records": 5000, "rank_distribution": {1: 500, 2: 1000, 3: 1500, 4: 1000, 5: 500, 6: 500}},
    "江西": {"priority": "P0", "target_records": 5000, "rank_distribution": {1: 500, 2: 1000, 3: 1500, 4: 1000, 5: 500, 6: 500}},
    "广西": {"priority": "P0", "target_records": 5000, "rank_distribution": {1: 500, 2: 1000, 3: 1500, 4: 1000, 5: 500, 6: 500}},
    "福建": {"priority": "P0", "target_records": 5000, "rank_distribution": {1: 500, 2: 1000, 3: 1500, 4: 1000, 5: 500, 6: 500}},
    "湖北": {"priority": "P1", "target_records": 3000, "rank_distribution": {1: 300, 2: 600, 3: 900, 4: 600, 5: 300, 6: 300}},
    "四川": {"priority": "P1", "target_records": 3000, "rank_distribution": {1: 300, 2: 600, 3: 900, 4: 600, 5: 300, 6: 300}},
    "河南": {"priority": "P1", "target_records": 3000, "rank_distribution": {1: 300, 2: 600, 3: 900, 4: 600, 5: 300, 6: 300}},
    "安徽": {"priority": "P1", "target_records": 3000, "rank_distribution": {1: 300, 2: 600, 3: 900, 4: 600, 5: 300, 6: 300}},
    "江苏": {"priority": "P1", "target_records": 3000, "rank_distribution": {1: 300, 2: 600, 3: 900, 4: 600, 5: 300, 6: 300}},
    "浙江": {"priority": "P1", "target_records": 3000, "rank_distribution": {1: 300, 2: 600, 3: 900, 4: 600, 5: 300, 6: 300}},
}

# 基础院校和专业数据
BASE_UNIVERSITIES = [
    {"name": "北京大学", "level": "985", "type": "综合"},
    {"name": "清华大学", "level": "985", "type": "综合"},
    {"name": "复旦大学", "level": "985", "type": "综合"},
    {"name": "上海交通大学", "level": "985", "type": "综合"},
    {"name": "浙江大学", "level": "985", "type": "综合"},
    {"name": "中国科学技术大学", "level": "985", "type": "综合"},
    {"name": "南京大学", "level": "985", "type": "综合"},
    {"name": "中山大学", "level": "985", "type": "综合"},
    {"name": "华南理工大学", "level": "985", "type": "综合"},
    {"name": "北京师范大学", "level": "985", "type": "师范"},
    {"name": "同济大学", "level": "985", "type": "工科"},
    {"name": "哈尔滨工业大学", "level": "985", "type": "工科"},
    {"name": "西安交通大学", "level": "985", "type": "综合"},
    {"name": "西北工业大学", "level": "985", "type": "工科"},
]

BASE_MAJORS = [
    {"name": "计算机科学与技术", "code": "080901", "category": "工科"},
    {"name": "软件工程", "code": "080902", "category": "工科"},
    {"name": "电子信息工程", "code": "080701", "category": "工科"},
    {"name": "通信工程", "code": "080703", "category": "工科"},
    {"name": "机械工程", "code": "080202", "category": "工科"},
    {"name": "电气工程及其自动化", "code": "080601", "category": "工科"},
    {"name": "土木工程", "code": "081001", "category": "工科"},
    {"name": "工商管理", "code": "120201", "category": "管理"},
    {"name": "会计学", "code": "120203", "category": "管理"},
    {"name": "金融学", "code": "020301", "category": "经济"},
    {"name": "英语", "code": "050201", "category": "文科"},
    {"name": "法学", "code": "030101", "category": "文科"},
]

# 位次段范围
RANK_RANGES = {
    1: (1, 10000),
    2: (10001, 30000),
    3: (30001, 70000),
    4: (70001, 120000),
    5: (120001, 200000),
    6: (200001, 350000)
}

# ==================== 数据生成函数 ====================

def generate_province_2025_data(province: str, config: Dict) -> List[Dict]:
    """
    生成单个省份的2025年模拟数据

    Args:
        province: 省份名称
        config: 省份配置

    Returns:
        生成的记录列表
    """
    logger.info(f"[GENERATE] 正在生成 {province} 省份2025年模拟数据...")

    target_records = config["target_records"]
    rank_distribution = config["rank_distribution"]

    records = []
    generated_count = 0

    # 按位次段生成数据
    for range_id, (min_rank, max_rank) in RANK_RANGES.items():
        target_count = rank_distribution.get(range_id, 0)

        if target_count == 0:
            continue

        logger.info(f"  [RANGE {range_id}] 生成 {target_count} 条记录 (位次: {min_rank:,}-{max_rank:,})")

        for i in range(target_count):
            # 随机选择院校和专业
            university = select_university_for_rank_range(min_rank, max_rank, province)
            major = select_major_for_university(university)

            # 生成分数和位次
            min_rank = random.randint(min_rank, max_rank)
            min_score = max(300, 750 - (min_rank // 1000) * 10)  # 简化的分数估算

            record = {
                "year": 2025,
                "province": province,
                "university_name": university["name"],
                "major_name": major["name"],
                "major_code": major["code"],
                "min_rank": min_rank,
                "min_score": min_score,
                "data_source": f"{province}_mock_2025",
                "mock_data": True,  # 标记为模拟数据
                "rank_range": range_id
            }

            records.append(record)
            generated_count += 1

        logger.info(f"    [OK] {range_id}段完成: {len([r for r in records if r.get('rank_range') == range_id])} 条")

    logger.info(f"[OK] {province} 省份生成完成: {len(records)} 条记录")
    return records

def select_university_for_rank_range(min_rank: int, max_rank: int, province: str) -> Dict:
    """根据位次段选择合适的院校"""
    # 根据位次段选择院校档次
    if min_rank <= 10000:
        # 顶尖段：985院校
        candidates = [u for u in BASE_UNIVERSITIES if u["level"] == "985"]
    elif min_rank <= 30000:
        # 重点段：985+211院校
        candidates = BASE_UNIVERSITIES
    elif min_rank <= 70000:
        # 一本段：一本院校
        candidates = BASE_UNIVERSITIES + [{"name": f"一本院校{i}", "level": "一本", "type": "综合"} for i in range(1, 20)]
    elif min_rank <= 120000:
        # 二本段：二本院校
        candidates = BASE_UNIVERSITIES + [{"name": f"二本院校{i}", "level": "二本", "type": "综合"} for i in range(1, 30)]
    else:
        # 专科段：所有院校
        candidates = BASE_UNIVERSITIES + [{"name": f"专科院校{i}", "level": "专科", "type": "职业"} for i in range(1, 50)]

    return random.choice(candidates)

def select_major_for_university(university: Dict) -> Dict:
    """为院校选择合适的专业"""
    # 根据院校类型选择专业
    if university["type"] == "工科":
        candidates = [m for m in BASE_MAJORS if m["category"] in ["工科", "理科"]]
    elif university["type"] == "综合":
        candidates = BASE_MAJORS
    elif university["type"] == "师范":
        candidates = [m for m in BASE_MAJORS if m["category"] in ["文科", "理科"]]
    else:
        candidates = BASE_MAJORS

    return random.choice(candidates)

# ==================== 数据保存函数 ====================

def save_province_data(province: str, records: List[Dict]) -> Path:
    """
    保存省份数据到单独文件

    Args:
        province: 省份名称
        records: 记录列表

    Returns:
        保存的文件路径
    """
    PROVINCE_DATA_DIR.mkdir(exist_ok=True)

    output_file = PROVINCE_DATA_DIR / f"{province}_2025_mock.json"

    data = {
        "province": province,
        "year": 2025,
        "total_records": len(records),
        "mock_data": True,
        "generation_time": datetime.now().isoformat(),
        "records": records
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"[SAVE] {province} 省份数据已保存: {output_file}")
    return output_file

# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    print("=" * 80)
    print("2025年全国录取数据模拟生成工具")
    print("=" * 80)
    print()
    print("[WARNING] 这是模拟数据生成工具，仅用于测试和演示！")
    print("[INFO] 生产环境请使用真实的投档线数据")
    print()

    # 创建输出目录
    PROVINCE_DATA_DIR.mkdir(exist_ok=True)

    # 生成各省份数据
    all_province_data = {}

    for province, config in sorted(PROVINCE_CONFIG.items()):
        records = generate_province_2025_data(province, config)
        all_province_data[province] = records

        # 保存到单独文件
        save_province_data(province, records)

    # 统计信息
    total_records = sum(len(records) for records in all_province_data.values())

    print("\n" + "=" * 80)
    print("[SUCCESS] 2025年模拟数据生成完成！")
    print(f"[STATS] 生成省份数量: {len(all_province_data)} 个")
    print(f"[STATS] 总记录数: {total_records:,} 条")
    print()
    print("[NEXT] 接下来可以运行数据收集脚本:")
    print("  python collect_2025_data.py")
    print("=" * 80)

if __name__ == "__main__":
    main()