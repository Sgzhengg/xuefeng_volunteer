# -*- coding: utf-8 -*-
"""
数据清洗与2025年数据量统计工具

功能：
1. 清理重复记录（基于5字段组合去重）
2. 按年份分离统计数据
3. 2025年数据多维度统计分析
4. 生成清洗报告和清洗后数据文件

使用方法：
    python clean_and_statistics_data.py

作者：学锋志愿教练团队
版本：1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime
from collections import defaultdict

# ==================== 日志配置 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'data_cleaning_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== 配置常量 ====================

# 从backend目录运行，使用相对路径
DATA_DIR = Path("data")
MAIN_DATA_FILE = DATA_DIR / "major_rank_data.json"
CLEANED_DATA_FILE = DATA_DIR / "cleaned_major_rank_data.json"
CLEANING_REPORT_FILE = Path(f"data_cleaning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

# 位次段定义
RANK_SEGMENTS = []
for i in range(0, 350000, 5000):
    segment_name = f"{i+1}-{i+5000}"
    RANK_SEGMENTS.append((i+1, i+5000, segment_name))

# 主要位次段
MAIN_RANK_SEGMENTS = {
    "1-10000": (1, 10000),
    "10001-30000": (10001, 30000),
    "30001-70000": (30001, 70000),
    "70001-120000": (70001, 120000),
    "120001-200000": (120001, 200000),
    "200001-350000": (200001, 350000)
}

# 985和211院校清单（用于识别院校类型）
TOP_985_UNIVERSITIES = {
    '北京大学', '清华大学', '复旦大学', '上海交通大学', '浙江大学',
    '中国科学技术大学', '南京大学', '西安交通大学', '哈尔滨工业大学',
    '中山大学', '华中科技大学', '武汉大学', '四川大学', '吉林大学',
    '南开大学', '天津大学', '山东大学', '中南大学', '华南理工大学',
    '厦门大学', '同济大学', '东南大学', '重庆大学', '大连理工大学',
    '华东师范大学', '北京师范大学', '中国人民大学', '兰州大学',
    '西北工业大学', '湖南大学', '东北大学', '电子科技大学',
    '北京航空航天大学', '北京理工大学', '中国农业大学', '中央民族大学',
    '西北农林科技大学', '中国海洋大学', '国防科技大学'
}

TOP_211_UNIVERSITIES = {
    '上海财经大学', '中央财经大学', '对外经济贸易大学',
    '北京外国语大学', '上海外国语大学',
    '中国政法大学', '西南政法大学',
    '北京邮电大学', '西安电子科技大学',
    '华中师范大学', '华南师范大学', '南京师范大学',
    '西南交通大学', '苏州大学', '上海大学',
    '暨南大学', '南昌大学', '湖南师范大学',
    '武汉理工大学', '中南财经政法大学', '华中农业大学',
    '西南财经大学', '四川农业大学', '东北师范大学',
    '西北大学', '长安大学', '陕西师范大学',
    '福州大学', '福建师范大学', '华侨大学',
    '广西大学', '广西医科大学', '广西师范大学', '桂林电子科技大学'
}

# ==================== 数据加载函数 ====================

def load_data() -> List[Dict]:
    """加载主数据文件"""
    logger.info("[LOAD] 加载主数据文件...")

    with open(MAIN_DATA_FILE.resolve(), 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])

    logger.info(f"[OK] 数据加载完成: {len(records):,} 条记录")
    return records

# ==================== 数据去重函数 ====================

def remove_duplicates(records: List[Dict]) -> Dict[str, Any]:
    """
    清理重复记录

    Returns:
        去重结果统计和去重后的记录列表
    """
    logger.info("[CLEAN] 开始清理重复记录...")

    original_count = len(records)

    # 构建唯一键集合
    seen_keys = {}
    duplicates = []
    unique_records = []

    for record in records:
        # 构建5字段组合键
        key = (
            record.get("university_name", ""),
            record.get("major_name", ""),
            record.get("year", 0),
            record.get("province", ""),
            record.get("min_rank", 0)
        )

        # 检查是否重复
        if key in seen_keys:
            duplicates.append(key)
            continue

        seen_keys[key] = record
        unique_records.append(record)

    duplicate_count = len(duplicates)
    cleaned_count = len(unique_records)

    logger.info(f"[OK] 去重完成: {duplicate_count:,} 条重复记录已清除")
    logger.info(f"[OK] 保留记录: {cleaned_count:,} 条")

    return {
        "original_count": original_count,
        "duplicate_count": duplicate_count,
        "cleaned_count": cleaned_count,
        "duplicate_keys": list(set(duplicates)),  # 去重后的重复键集合
        "unique_records": unique_records  # 返回去重后的记录列表
    }

# ==================== 年份分离统计 ====================

def analyze_by_year(records: List[Dict]) -> Dict[str, Any]:
    """
    按年份分离统计数据

    Returns:
        年份分析结果
    """
    logger.info("[ANALYZE] 按年份分离统计数据...")

    year_stats = defaultdict(int)
    year_records = defaultdict(list)

    for record in records:
        year = record.get("year", 0)
        year_stats[year] += 1
        year_records[year].append(record)

    # 处理年份为0或缺失的记录
    unknown_year_count = year_stats.get(0, 0)

    logger.info(f"[OK] 年份统计完成:")
    for year in sorted(year_stats.keys(), reverse=True):
        if year != 0:
            logger.info(f"  {year}年: {year_stats[year]:,} 条")

    if unknown_year_count > 0:
        logger.info(f"  年份缺失: {unknown_year_count:,} 条")

    return {
        "year_breakdown": dict(year_stats),
        "year_records": dict(year_records),
        "unknown_year_count": unknown_year_count
    }

# ==================== 2025年数据详细统计 ====================

def analyze_2025_data(records_2025: List[Dict]) -> Dict[str, Any]:
    """
    分析2025年数据的多维度统计

    Returns:
        2025年数据分析结果
    """
    logger.info("[ANALYZE] 分析2025年数据多维度统计...")

    # 1. 省份统计
    province_stats = defaultdict(int)
    for record in records_2025:
        province = record.get("province", "未知")
        province_stats[province] += 1

    # 2. 位次段统计
    rank_segment_stats = defaultdict(int)
    for record in records_2025:
        min_rank = record.get("min_rank", 0)
        for segment_name, (min_r, max_r) in MAIN_RANK_SEGMENTS.items():
            if min_r <= min_rank <= max_r:
                rank_segment_stats[segment_name] += 1
                break

    # 3. 院校类型统计
    university_type_stats = defaultdict(int)
    for record in records_2025:
        university = record.get("university_name", "")
        uni_type = classify_university_type(university)
        university_type_stats[uni_type] += 1

    # 4. 专业覆盖率统计
    university_majors = defaultdict(set)
    for record in records_2025:
        university = record.get("university_name", "")
        major = record.get("major_name", "")
        if major and major not in ["未分专业", ""]:
            university_majors[university].add(major)

    major_coverage_stats = {
        "total_universities": len(university_majors),
        "universities_with_5plus_majors": sum(1 for majors in university_majors.values() if len(majors) >= 5),
        "average_majors_per_university": sum(len(majors) for majors in university_majors.values()) / len(university_majors) if university_majors else 0
    }

    logger.info(f"[OK] 2025年数据分析完成:")
    logger.info(f"  涉及省份: {len(province_stats)} 个")
    logger.info(f"  院校类型: {len(university_type_stats)} 种")
    logger.info(f"  院校数量: {major_coverage_stats['total_universities']} 所")

    return {
        "province_count": len(province_stats),
        "province_stats": dict(province_stats),
        "rank_segment_stats": dict(rank_segment_stats),
        "university_type_stats": dict(university_type_stats),
        "major_coverage_stats": major_coverage_stats
    }

def classify_university_type(university_name: str) -> str:
    """分类院校类型"""
    if not university_name:
        return "未知"

    for uni_985 in TOP_985_UNIVERSITIES:
        if uni_985 in university_name or university_name in uni_985:
            return "985"

    for uni_211 in TOP_211_UNIVERSITIES:
        if uni_211 in university_name or university_name in uni_211:
            return "211"

    # 根据名称特征判断
    if any(keyword in university_name for keyword in ["学院", "大学", "校本部"]):
        if "专科" in university_name or "职业技术" in university_name:
            return "高职专科"
        elif "独立学院" in university_name or any(keyword in university_name for keyword in ["科技", "理工", "财经", "工商"]):
            return "普通本科"
        else:
            return "普通本科"

    if "专科" in university_name or "职业技术" in university_name:
        return "高职专科"

    return "其他"

# ==================== 验证函数 ====================

def verify_cleaned_data(records: List[Dict]) -> Dict[str, Any]:
    """
    验证清洗后的数据

    Returns:
        验证结果
    """
    logger.info("[VERIFY] 验证清洗后的数据...")

    # 检查是否有重复键
    key_count = defaultdict(int)
    for record in records:
        key = (
            record.get("university_name", ""),
            record.get("major_name", ""),
            record.get("year", 0),
            record.get("province", ""),
            record.get("min_rank", 0)
        )
        key_count[key] += 1

    duplicate_keys = {key: count for key, count in key_count.items() if count > 1}

    # 检查2025年数据充足性
    records_2025 = [r for r in records if r.get("year") == 2025]

    rank_coverage = {}
    for segment_name, (min_r, max_r) in MAIN_RANK_SEGMENTS.items():
        count = sum(1 for r in records_2025 if min_r <= r.get("min_rank", 0) <= max_r)
        rank_coverage[segment_name] = {
            "count": count,
            "sufficient": count >= 50  # 最低标准
        }

    logger.info(f"[OK] 数据验证完成:")
    logger.info(f"  重复键: {len(duplicate_keys)} 个")
    logger.info(f"  2025年数据: {len(records_2025):,} 条")

    sufficient_segments = sum(1 for stats in rank_coverage.values() if stats["sufficient"])
    logger.info(f"  位次段充足: {sufficient_segments}/6")

    return {
        "has_duplicates": len(duplicate_keys) > 0,
        "duplicate_keys": dict(duplicate_keys),
        "total_2025_records": len(records_2025),
        "rank_coverage": rank_coverage,
        "sufficient_segments": sufficient_segments
    }

# ==================== 数据保存函数 ====================

def save_cleaned_data(records: List[Dict]) -> None:
    """保存清洗后的数据"""
    logger.info("[SAVE] 保存清洗后的数据...")

    cleaned_data = {
        "metadata": {
            "version": "9.0.0",
            "generated_at": datetime.now().isoformat(),
            "total_records": len(records),
            "data_cleaning_performed": True,
            "cleaning_timestamp": datetime.now().isoformat()
        },
        "major_rank_data": records
    }

    with open(CLEANED_DATA_FILE.resolve(), 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    logger.info(f"[OK] 清洗后数据已保存: {CLEANED_DATA_FILE}")

def save_cleaning_report(cleaning_result: Dict, year_analysis: Dict, stats_2025: Dict, verification: Dict) -> None:
    """保存清洗报告"""
    logger.info("[REPORT] 生成数据清洗报告...")

    cleaning_report = {
        "generation_time": datetime.now().isoformat(),
        "data_file": str(MAIN_DATA_FILE),
        "cleaned_data_file": str(CLEANED_DATA_FILE),

        # 清洗统计
        "cleaning_statistics": {
            "original_count": cleaning_result["original_count"],
            "duplicate_count": cleaning_result["duplicate_count"],
            "cleaned_count": cleaning_result["cleaned_count"],
            "reduction_rate": cleaning_result["duplicate_count"] / cleaning_result["original_count"] if cleaning_result["original_count"] > 0 else 0
        },

        # 年份分离统计
        "year_breakdown": year_analysis["year_breakdown"],
        "unknown_year_count": year_analysis["unknown_year_count"],

        # 2025年数据统计
        "2025_statistics": {
            "total_2025_records": stats_2025["province_count"],  # 这里用省份数量表示记录数，稍后修正

            # 各省份数据统计
            "province_stats": stats_2025["province_stats"],

            # 位次段统计
            "rank_segment_stats": stats_2025["rank_segment_stats"],

            # 院校类型统计
            "university_type_stats": stats_2025["university_type_stats"],

            # 专业覆盖统计
            "major_coverage_stats": stats_2025["major_coverage_stats"]
        },

        # 验证结果
        "verification": {
            "has_duplicates": verification["has_duplicates"],
            "duplicate_keys_count": len(verification["duplicate_keys"]),
            "total_2025_records": verification["total_2025_records"],
            "rank_coverage": verification["rank_coverage"],
            "sufficient_segments": verification["sufficient_segments"]
        }
    }

    # 修正2025年记录总数
    cleaning_report["2025_statistics"]["total_2025_records"] = verification["total_2025_records"]

    with open(CLEANING_REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(cleaning_report, f, ensure_ascii=False, indent=2)

    logger.info(f"[OK] 清洗报告已保存: {CLEANING_REPORT_FILE}")

# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    print("=" * 80)
    print("数据清洗与2025年数据量统计工具")
    print("=" * 80)
    print()

    # 步骤1: 加载数据
    print("[STEP-1] 加载主数据文件...")
    records = load_data()

    if not records:
        logger.error("[ERROR] 无法加载数据或数据为空")
        return

    # 步骤2: 清理重复记录
    print("[STEP-2] 清理重复记录...")
    cleaning_result = remove_duplicates(records)

    # 步骤3: 按年份分离统计
    print("[STEP-3] 按年份分离统计数据...")
    year_analysis = analyze_by_year(cleaning_result["unique_records"])

    # 步骤4: 2025年数据详细统计
    print("[STEP-4] 分析2025年数据多维度统计...")
    records_2025 = year_analysis["year_records"].get(2025, [])
    stats_2025 = analyze_2025_data(records_2025)

    # 步骤5: 验证清洗后数据
    print("[STEP-5] 验证清洗后数据...")
    verification = verify_cleaned_data(cleaning_result["unique_records"])

    # 步骤6: 保存清洗后数据和报告
    print("[STEP-6] 保存清洗后数据和报告...")
    save_cleaned_data(cleaning_result["unique_records"])
    save_cleaning_report(cleaning_result, year_analysis, stats_2025, verification)

    # 输出结果摘要
    print()
    print("=" * 80)
    print("[清洗完成] 数据清洗与统计报告")
    print("=" * 80)

    print(f"原始记录数: {cleaning_result['original_count']:,}")
    print(f"重复记录数: {cleaning_result['duplicate_count']:,}")
    print(f"清洗后记录数: {cleaning_result['cleaned_count']:,}")
    print(f"数据减少率: {cleaning_result['duplicate_count'] / cleaning_result['original_count'] * 100:.1f}%")
    print()

    print("[年份数据分布]")
    for year in sorted(year_analysis["year_breakdown"].keys(), reverse=True):
        if year != 0:
            print(f"  {year}年: {year_analysis['year_breakdown'][year]:,} 条")
    print(f"  年份缺失: {year_analysis['unknown_year_count']:,} 条")
    print()

    print(f"[2025年数据统计]")
    print(f"  总记录数: {verification['total_2025_records']:,} 条")
    print(f"  涉及省份: {stats_2025['province_count']} 个")
    print(f"  院校数量: {stats_2025['major_coverage_stats']['total_universities']} 所")
    print(f"  专业覆盖: {stats_2025['major_coverage_stats']['average_majors_per_university']:.1f} 个专业/院校")
    print()

    print(f"[验证结果]")
    print(f"  重复键检查: {'[通过]' if not verification['has_duplicates'] else '[失败]'}")
    print(f"  位次段充足: {verification['sufficient_segments']}/6 个段位达标")
    print()

    print(f"[输出文件]")
    print(f"  清洗后数据: {CLEANED_DATA_FILE}")
    print(f"  清洗报告: {CLEANING_REPORT_FILE}")
    print("=" * 80)

if __name__ == "__main__":
    main()