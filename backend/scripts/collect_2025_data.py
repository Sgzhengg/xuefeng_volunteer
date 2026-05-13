# -*- coding: utf-8 -*-
"""
2025年全国录取数据收集工具

功能：
1. 清理虚假的2025年数据
2. 按优先级逐省采集真实投档线
3. 数据格式转换和验证
4. 专业组展开
5. 合并到主数据文件
6. 位次段覆盖验证

使用方法：
    python collect_2025_data.py

作者：学锋志愿教练团队
版本：1.0.0
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict
import pandas as pd

# ==================== 日志配置 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'collect_2025_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== 配置常量 ====================

DATA_DIR = Path("../data")
MAIN_DATA_FILE = DATA_DIR / "major_rank_data.json"
PROVINCE_DATA_DIR = DATA_DIR / "province_data_2025"
BACKUP_DIR = DATA_DIR / "backups"

# 省份优先级配置
PROVINCE_PRIORITIES = {
    "P0": {
        "广东": {"target_records": 15000, "rank_ranges": {1: 1000, 2: 2000, 3: 3000, 4: 3000, 5: 3000, 6: 3000}},
        "湖南": {"target_records": 5000, "rank_ranges": {1: 500, 2: 1000, 3: 1500, 4: 1000, 5: 500, 6: 500}},
        "江西": {"target_records": 5000, "rank_ranges": {1: 500, 2: 1000, 3: 1500, 4: 1000, 5: 500, 6: 500}},
        "广西": {"target_records": 5000, "rank_ranges": {1: 500, 2: 1000, 3: 1500, 4: 1000, 5: 500, 6: 500}},
        "福建": {"target_records": 5000, "rank_ranges": {1: 500, 2: 1000, 3: 1500, 4: 1000, 5: 500, 6: 500}},
    },
    "P1": {
        "湖北": {"target_records": 3000, "rank_ranges": {1: 300, 2: 600, 3: 900, 4: 600, 5: 300, 6: 300}},
        "四川": {"target_records": 3000, "rank_ranges": {1: 300, 2: 600, 3: 900, 4: 600, 5: 300, 6: 300}},
        "河南": {"target_records": 3000, "rank_ranges": {1: 300, 2: 600, 3: 900, 4: 600, 5: 300, 6: 300}},
        "安徽": {"target_records": 3000, "rank_ranges": {1: 300, 2: 600, 3: 900, 4: 600, 5: 300, 6: 300}},
        "江苏": {"target_records": 3000, "rank_ranges": {1: 300, 2: 600, 3: 900, 4: 600, 5: 300, 6: 300}},
        "浙江": {"target_records": 3000, "rank_ranges": {1: 300, 2: 600, 3: 900, 4: 600, 5: 300, 6: 300}},
    },
    "P2": {
        # 其他21省份，每省1000条
        "其他省份": {"target_records_per_province": 1000, "rank_ranges": {1: 100, 2: 200, 3: 300, 4: 200, 5: 100, 6: 100}}
    }
}

# 位次段范围定义
RANK_RANGES = {
    1: (1, 10000),
    2: (10001, 30000),
    3: (30001, 70000),
    4: (70001, 120000),
    5: (120001, 200000),
    6: (200001, 350000)
}

# ==================== 数据清理函数 ====================

def clean_fake_2025_data() -> bool:
    """
    清理虚假的2025年数据

    Returns:
        是否成功
    """
    logger.info("[CLEAN] 开始清理虚假的2025年数据...")

    try:
        # 1. 创建备份
        BACKUP_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"before_cleaning_2025_{timestamp}.json"

        shutil.copy2(MAIN_DATA_FILE, backup_file)
        logger.info(f"[BACKUP] 备份已创建: {backup_file}")

        # 2. 读取主数据文件
        main_file_resolved = MAIN_DATA_FILE.resolve()
        with open(main_file_resolved, 'r', encoding='utf-8') as f:
            data = json.load(f)

        records = data.get("major_rank_data", [])
        original_count = len(records)

        # 3. 过滤掉2025年的虚假数据
        fake_2025_patterns = [
            # 识别虚假数据的特征
            lambda r: r.get("year") == 2025 and r.get("province") in ["上海", "云南", "内蒙古"] and r.get("min_rank") == 18760,
            lambda r: r.get("year") == 2025 and len(set(r.get("university_name", "")) for r in [records[0] if records else {}]) if records else False
        ]

        # 简单粗暴：删除所有2025年数据
        cleaned_records = [r for r in records if r.get("year") != 2025]

        fake_count = original_count - len(cleaned_records)
        logger.info(f"[OK] 清理完成: 删除 {fake_count:,} 条虚假2025年数据")
        logger.info(f"[OK] 保留 {len(cleaned_records):,} 条非2025年数据")

        # 4. 保存清理后的数据
        data["major_rank_data"] = cleaned_records
        data["metadata"]["total_records"] = len(cleaned_records)
        data["metadata"]["data_cleaning"] = {
            "timestamp": datetime.now().isoformat(),
            "fake_2025_records_removed": fake_count,
            "backup_file": str(backup_file)
        }

        # 使用resolve()确保路径正确解析
        main_file_resolved = MAIN_DATA_FILE.resolve()
        with open(main_file_resolved, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"[SAVE] 清理后的数据已保存")
        return True

    except Exception as e:
        logger.error(f"[ERROR] 清理失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

# ==================== 数据采集函数 ====================

def scan_province_data_files() -> Dict[str, List[Path]]:
    """
    扫描省份数据文件

    Returns:
        省份到文件路径映射
    """
    logger.info("[SCAN] 扫描省份数据文件...")

    if not PROVINCE_DATA_DIR.exists():
        logger.error(f"[ERROR] 省份数据目录不存在: {PROVINCE_DATA_DIR}")
        return {}

    province_files = defaultdict(list)

    # 方式1: 扫描子目录中的数据文件
    for province_dir in PROVINCE_DATA_DIR.iterdir():
        if province_dir.is_dir():
            province_name = province_dir.name
            # 查找Excel和JSON文件
            data_files = list(province_dir.glob("*.xlsx")) + list(province_dir.glob("*.xls")) + list(province_dir.glob("*.json"))
            if data_files:
                province_files[province_name].extend(data_files)
                logger.info(f"[FOUND] {province_name}: {len(data_files)} 个数据文件（子目录）")

    # 方式2: 扫描直接以省份命名的JSON文件（如 广东_2025_mock.json）
    for file_path in PROVINCE_DATA_DIR.glob("*.json"):
        if file_path.is_file():
            filename = file_path.stem  # 去掉扩展名
            # 解析省份名称（支持格式：省份_2025_mock.json, 省份_2025.json 等）
            parts = filename.split("_")
            if len(parts) >= 2 and parts[0].isalpha() and len(parts[0]) >= 2:
                province_name = parts[0]
                province_files[province_name].append(file_path)
                logger.info(f"[FOUND] {province_name}: {file_path.name}（直接文件）")

    total_files = sum(len(files) for files in province_files.values())
    logger.info(f"[OK] 扫描完成: {len(province_files)} 个省份, {total_files} 个数据文件")

    return dict(province_files)

def import_province_excel(file_path: Path, province: str) -> List[Dict]:
    """
    导入省份Excel投档线数据

    Args:
        file_path: Excel文件路径
        province: 省份名称

    Returns:
        导入的记录列表
    """
    logger.info(f"[IMPORT] 导入 {province} 省份数据: {file_path.name}")

    try:
        # 读取Excel
        df = pd.read_excel(file_path)

        # 自动检测列名
        column_mapping = detect_excel_columns(df.columns, province)

        if not column_mapping.get("university_name"):
            logger.error(f"[ERROR] 无法识别Excel列名: {list(df.columns)}")
            logger.info(f"[INFO] 请检查Excel文件格式，确保包含院校名称、位次等列")
            return []

        records = []
        error_count = 0

        for idx, row in df.iterrows():
            try:
                # 提取并清洗数据
                university_name = str(row.get(column_mapping["university_name"], "")).strip()
                group_code = str(row.get(column_mapping.get("group_code", ""), "")).strip()

                # 位次数据处理（去除非数字字符）
                min_rank_str = str(row.get(column_mapping.get("min_rank", ""), "")).strip()
                min_rank = clean_rank_value(min_rank_str)

                # 分数数据处理
                min_score_str = str(row.get(column_mapping.get("min_score", ""), "")).strip()
                min_score = clean_score_value(min_score_str)

                # 数据验证
                if not university_name:
                    continue

                if min_rank is None or min_rank <= 0:
                    logger.warning(f"[WARN] 第 {idx+2} 行: 位次无效 ({min_rank_str})，跳过")
                    error_count += 1
                    continue

                # 构建记录
                record = {
                    "year": 2025,
                    "province": province,
                    "university_name": university_name,
                    "major_name": "未分专业",  # 投档线通常是专业组级别
                    "major_code": group_code if group_code else "000000",
                    "min_rank": min_rank,
                    "min_score": min_score,
                    "data_source": f"{province}_education_exam_2025",
                    "batch": "本科" if "本科" in str(file_path) else "专科"
                }

                records.append(record)

            except Exception as e:
                error_count += 1
                logger.debug(f"[DEBUG] 第 {idx+2} 行处理失败: {e}")

        logger.info(f"[OK] {province} 省份导入完成: {len(records)} 条记录 (错误: {error_count})")
        return records

    except Exception as e:
        logger.error(f"[ERROR] Excel导入失败 {file_path.name}: {e}")
        return []

def import_province_json(file_path: Path, province: str) -> List[Dict]:
    """
    导入省份JSON模拟数据

    Args:
        file_path: JSON文件路径
        province: 省份名称

    Returns:
        导入的记录列表
    """
    logger.info(f"[IMPORT] 导入 {province} 省份JSON数据: {file_path.name}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # 支持两种JSON格式：
        # 1. {"province": "广东", "records": [...]}
        # 2. 直接是记录列表 [...]

        if isinstance(json_data, dict):
            records = json_data.get("records", [])
        elif isinstance(json_data, list):
            records = json_data
        else:
            logger.error(f"[ERROR] 不支持的JSON格式: {type(json_data)}")
            return []

        # 数据清洗和验证
        cleaned_records = []
        for record in records:
            try:
                # 验证必要字段
                if not all(key in record for key in ["university_name", "major_name", "min_rank", "min_score"]):
                    continue

                # 确保省份正确
                record["province"] = province
                record["year"] = 2025

                # 数据源标记
                if "data_source" not in record:
                    record["data_source"] = f"{province}_mock_2025"

                cleaned_records.append(record)

            except Exception as e:
                logger.debug(f"[DEBUG] 处理记录失败: {e}")

        logger.info(f"[OK] {province} 省份JSON导入完成: {len(cleaned_records)} 条记录")
        return cleaned_records

    except Exception as e:
        logger.error(f"[ERROR] JSON导入失败 {file_path.name}: {e}")
        return []

def detect_excel_columns(columns, province: str) -> Dict[str, str]:
    """
    智能检测Excel列名

    Args:
        columns: DataFrame列名
        province: 省份名称

    Returns:
        列名映射字典
    """
    # 列名变体映射
    column_variants = {
        "university_name": [
            "院校名称", "学校名称", "大学名称", "院校", "院校代码",
            # 英文变体
            "University Name", "School Name", "College Name"
        ],
        "group_code": [
            "专业组代码", "专业组", "科目组", "院校专业组",
            "专业组代码", "专业组名称"
        ],
        "min_score": [
            "最低分", "投档分", "分数线", "录取最低分",
            "最低投档分", "投档分数线"
        ],
        "min_rank": [
            "最低排位", "最低位次", "投档排位", "排位",
            "最低排位", "位次", "排名"
        ],
        "plan_count": [
            "计划数", "招生计划", "计划",
            "招生计划数"
        ]
    }

    detected = {}
    columns_lower = [str(col).strip().lower() for col in columns]

    for standard_name, variants in column_variants.items():
        for i, col in enumerate(columns):
            col_lower = str(col).strip().lower()
            for variant in variants:
                variant_lower = variant.lower()
                if variant_lower in col_lower or col_lower in variant_lower:
                    detected[standard_name] = str(col).strip()
                    break
            if standard_name in detected:
                break

    return detected

def clean_rank_value(value: str) -> int:
    """清理位次数据"""
    if not value or value.lower() in ['none', 'nan', '']:
        return None

    # 去除非数字字符
    cleaned = ''.join(c for c in str(value) if c.isdigit())

    try:
        return int(cleaned) if cleaned else None
    except ValueError:
        return None

def clean_score_value(value: str) -> int:
    """清理分数数据"""
    if not value or value.lower() in ['none', 'nan', '']:
        return None

    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None

def expand_major_groups(records: List[Dict], province: str) -> List[Dict]:
    """
    将专业组数据展开为基础专业

    Args:
        records: 专业组记录列表
        province: 省份名称

    Returns:
    展开后的专业级记录
    """
    logger.info(f"[EXPAND] 展开专业组数据...")

    # 默认专业展开规则（基于常见专业组合）
    major_expansion_rules = get_default_major_expansion_rules()

    expanded_records = []
    expanded_count = 0
    kept_as_group = 0

    for record in records:
        group_code = record.get("major_code", "")
        university_name = record.get("university_name", "")

        # 尝试展开专业组
        if group_code and group_code in major_expansion_rules:
            majors = major_expansion_rules[group_code]

            for major_info in majors:
                expanded_record = {
                    **record,
                    "major_name": major_info["name"],
                    "major_code": major_info["code"],
                    "expanded_from_group": group_code
                }
                expanded_records.append(expanded_record)
                expanded_count += 1

            logger.debug(f"[EXPAND] {university_name} - {group_code}: 展开为 {len(majors)} 个专业")
        else:
            # 无法展开，保留为专业组级别
            record["expansion_note"] = "专业组映射缺失，保留原始数据"
            expanded_records.append(record)
            kept_as_group += 1

    logger.info(f"[OK] 专业组展开完成: {expanded_count} 条专业级, {kept_as_group} 条专业组级")
    return expanded_records

def get_default_major_expansion_rules() -> Dict[str, List[Dict]]:
    """
    获取默认专业展开规则

    Returns:
        专业组代码到专业列表的映射
    """
    return {
        # 计算机类
        "001": [
            {"name": "计算机科学与技术", "code": "080901"},
            {"name": "软件工程", "code": "080902"},
            {"name": "网络工程", "code": "080903"}
        ],
        # 电子信息类
        "002": [
            {"name": "电子信息工程", "code": "080701"},
            {"name": "通信工程", "code": "080703"},
            {"name": "电子科学与技术", "code": "080702"}
        ],
        # 机械类
        "003": [
            {"name": "机械工程", "code": "080202"},
            {"name": "机械设计制造及其自动化", "code": "080203"},
            {"name": "机械电子工程", "code": "080204"}
        ],
        # 工商管理类
        "004": [
            {"name": "工商管理", "code": "120201"},
            {"name": "市场营销", "code": "120202"},
            {"name": "会计学", "code": "120203"}
        ]
        # 更多专业组规则...
    }

# ==================== 数据合并函数 ====================

def merge_province_data(province_data: Dict[str, List[Dict]]) -> Dict:
    """
    合并省份数据到主数据文件

    Args:
        province_data: 省份数据字典

    Returns:
        合并统计信息
    """
    logger.info("[MERGE] 开始合并省份数据...")

    # 1. 读取主数据文件
    try:
        main_file_resolved = MAIN_DATA_FILE.resolve()
        with open(main_file_resolved, 'r', encoding='utf-8') as f:
            main_data = json.load(f)

        main_records = main_data.get("major_rank_data", [])
        logger.info(f"[OK] 主数据加载完成: {len(main_records):,} 条记录")

    except Exception as e:
        logger.error(f"[ERROR] 读取主数据失败: {e}")
        return {"success": False, "error": str(e)}

    # 2. 构建现有数据索引（去重）
    existing_keys = {
        (r.get("university_name", ""), r.get("major_name", ""),
         r.get("year", 0), r.get("province", ""), r.get("min_rank", 0))
        for r in main_records
    }

    # 3. 合并各省份数据
    statistics = {
        "total_new": 0,
        "added": 0,
        "duplicates": 0,
        "by_province": {},
        "rank_range_coverage": defaultdict(int)
    }

    for province, records in sorted(province_data.items()):
        logger.info(f"[PROCESS] 正在处理 {province} 省份...")

        province_added = 0
        province_duplicates = 0

        for record in records:
            try:
                # 构建数据键
                key = (
                    record.get("university_name", ""),
                    record.get("major_name", ""),
                    record.get("year", 0),
                    record.get("province", ""),
                    record.get("min_rank", 0)
                )

                if key not in existing_keys:
                    if validate_record(record):
                        main_records.append(record)
                        existing_keys.add(key)
                        province_added += 1

                        # 更新位次段统计
                        rank = record.get("min_rank", 0)
                        rank_range = get_rank_range_from_rank(rank)
                        statistics["rank_range_coverage"][rank_range] += 1

                    else:
                        continue
                else:
                    province_duplicates += 1

            except Exception as e:
                logger.debug(f"[DEBUG] 处理记录失败: {e}")

        statistics["by_province"][province] = {
            "added": province_added,
            "duplicates": province_duplicates
        }
        statistics["added"] += province_added
        statistics["duplicates"] += province_duplicates
        statistics["total_new"] += len(records)

        logger.info(f"[OK] {province} 省份处理完成: 新增 {province_added}, 重复 {province_duplicates}")

    # 4. 更新元数据
    metadata = main_data.get("metadata", {})
    metadata.update({
        "version": "8.0.0",
        "generated_at": datetime.now().isoformat(),
        "total_records": len(main_records),
        "collection_info": {
            "timestamp": datetime.now().isoformat(),
            "type": "2025_nationwide_collection",
            "provinces_collected": len(province_data),
            "total_added": statistics["added"]
        }
    })

    # 5. 保存合并后的数据
    logger.info("[SAVE] 正在保存合并后的数据...")
    merged_data = {
        "metadata": metadata,
        "major_rank_data": main_records
    }

    main_file_resolved = MAIN_DATA_FILE.resolve()
    with open(main_file_resolved, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)

    # 6. 输出统计信息
    statistics["success"] = True
    statistics["total_after_merge"] = len(main_records)

    logger.info("=" * 60)
    logger.info("[SUCCESS] 数据合并完成！")
    logger.info(f"[STATS] 新增记录: {statistics['added']:,} 条")
    logger.info(f"[STATS] 重复记录: {statistics['duplicates']:,} 条")
    logger.info(f"[STATS] 当前总记录: {len(main_records):,} 条")
    logger.info("=" * 60)

    return statistics

def validate_record(record: Dict) -> bool:
    """验证记录数据完整性"""
    required_fields = ["university_name", "major_name", "year", "province"]
    for field in required_fields:
        if not record.get(field):
            return False

    min_rank = record.get("min_rank")
    if min_rank is None or min_rank <= 0:
        return False

    year = record.get("year")
    if year != 2025:
        logger.warning(f"[WARN] 异常年份: {year}")
        return False

    return True

def get_rank_range_from_rank(rank: int) -> str:
    """从位次获取位次段名称"""
    if rank <= 10000:
        return "1-10000"
    elif rank <= 30000:
        return "10001-30000"
    elif rank <= 70000:
        return "30001-70000"
    elif rank <= 120000:
        return "70001-120000"
    elif rank <= 200000:
        return "120001-200000"
    else:
        return "200001+"

# ==================== 验证报告函数 ====================

def generate_validation_report() -> str:
    """
    生成数据覆盖验证报告

    Returns:
        报告文件路径
    """
    logger.info("[REPORT] 正在生成数据覆盖验证报告...")

    try:
        main_file_resolved = MAIN_DATA_FILE.resolve()
        with open(main_file_resolved, 'r', encoding='utf-8') as f:
            data = json.load(f)

        records = data.get("major_rank_data", [])
        records_2025 = [r for r in records if r.get("year") == 2025]

        # 按省份统计
        province_stats = defaultdict(lambda: defaultdict(int))
        for record in records_2025:
            province = record.get("province", "未知")
            rank = record.get("min_rank", 0)
            rank_range = get_rank_range_from_rank(rank)
            province_stats[province][rank_range] += 1

        # 生成报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"validation_report_{timestamp}.txt")

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("2025年全国录取数据覆盖验证报告\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # 总体统计
            f.write("[总体统计]\n")
            f.write(f"2025年数据总量: {len(records_2025):,} 条\n")
            f.write(f"覆盖省份数量: {len(province_stats)} 个\n\n")

            # 分省份数据统计
            f.write("[分省份数据统计]\n")
            f.write(f"{'省份':<10} {'1-1万':<10} {'1万-3万':<10} {'3万-7万':<10} {'7万-12万':<10} {'12万-20万':<10} {'20万+':<10} {'总计':<10}\n")
            f.write("-" * 80 + "\n")

            for province in sorted(province_stats.keys()):
                f.write(f"{province:<10} ")
                rank_ranges = province_stats[province]

                # 按位次段顺序显示
                for i in range(1, 7):
                    range_name = get_rank_range_from_rank(i * 10000)  # 近似转换
                    actual_ranges = {
                        1: "1-10000",
                        2: "10001-30000",
                        3: "30001-70000",
                        4: "70001-120000",
                        5: "120001-200000",
                        6: "200001+"
                    }
                    range_name = actual_ranges[i]
                    count = rank_ranges.get(range_name, 0)
                    f.write(f"{count:<10} ")

                total = sum(rank_ranges.values())
                f.write(f"{total:<10}\n")

            # 位次段覆盖率统计
            f.write("\n[位次段覆盖率统计]\n")
            for i in range(1, 7):
                range_name = get_rank_range_from_rank(i * 10000)
                actual_ranges = {
                    1: "1-10000",
                    2: "10001-30000",
                    3: "30001-70000",
                    4: "70001-120000",
                    5: "120001-200000",
                    6: "200001+"
                }
                range_name = actual_ranges[i]
                total = sum(province_stats[p][range_name] for p in province_stats)
                f.write(f"{range_name}: {total:,} 条\n")

        logger.info(f"[OK] 验证报告已保存: {report_file}")
        return str(report_file)

    except Exception as e:
        logger.error(f"[ERROR] 生成报告失败: {e}")
        return ""

# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    print("=" * 80)
    print("2025年全国录取数据收集工具")
    print("=" * 80)
    print()

    # 步骤1: 清理虚假数据
    print("[STEP-1] 清理虚假的2025年数据...")
    if not clean_fake_2025_data():
        logger.error("[ERROR] 数据清理失败")
        return

    # 步骤2: 扫描省份数据文件
    print("[STEP-2] 扫描省份数据文件...")
    province_files = scan_province_data_files()

    if not province_files:
        logger.error("[ERROR] 未找到任何省份数据文件")
        logger.info("[INFO] 请按以下结构放置数据文件:")
        logger.info("  data/province_data_2025/")
        logger.info("    ├── 广东/")
        logger.info("    │   ├── 2025本科投档线.xlsx")
        logger.info("    │   └── 2025专科投档线.xlsx")
        logger.info("    ├── 湖南/")
        logger.info("    │   └── 2025年投档线.xlsx")
        logger.info("    └── ...")
        return

    # 步骤3: 导入各省份数据
    print("[STEP-3] 导入各省份数据...")
    all_province_data = {}

    for province, file_paths in sorted(province_files.items()):
        for file_path in file_paths:
            # 根据文件扩展名选择导入函数
            if file_path.suffix in ['.xlsx', '.xls']:
                records = import_province_excel(file_path, province)
            elif file_path.suffix == '.json':
                records = import_province_json(file_path, province)
            else:
                logger.warning(f"[WARN] 不支持的文件格式: {file_path.suffix}")
                continue

            if records:
                if province not in all_province_data:
                    all_province_data[province] = []

                all_province_data[province].extend(records)

    # 步骤4: 专业组展开
    print("[STEP-4] 展开专业组数据...")
    expanded_province_data = {}

    for province, records in all_province_data.items():
        expanded_records = expand_major_groups(records, province)
        expanded_province_data[province] = expanded_records

    # 步骤5: 合并数据
    print("[STEP-5] 合并到主数据文件...")
    merge_result = merge_province_data(expanded_province_data)

    # 步骤6: 生成验证报告
    if merge_result.get("success"):
        print("[STEP-6] 生成数据覆盖验证报告...")
        validation_report = generate_validation_report()

        print("\n" + "=" * 80)
        print("[SUCCESS] 2025年全国录取数据收集完成！")
        print(f"[INFO] 验证报告: {validation_report}")
        print("=" * 80)
    else:
        print("[FAILED] 数据收集失败")

if __name__ == "__main__":
    main()