# -*- coding: utf-8 -*-
"""
合并2025年省份数据到主数据文件

功能：
1. 读取所有province_data_2025目录下的省份数据
2. 合并到major_rank_data.json
3. 保存更新后的主数据文件

作者：学锋志愿教练团队
版本：1.0.0
"""

import json
import logging
from pathlib import Path
from datetime import datetime

# ==================== 日志配置 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'merge_2025_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== 配置常量 ====================

# 从backend目录运行，使用相对路径
DATA_DIR = Path("data")
PROVINCE_DATA_DIR = DATA_DIR / "province_data_2025"
MAIN_DATA_FILE = DATA_DIR / "major_rank_data.json"
BACKUP_FILE = DATA_DIR / f"backups/major_rank_data_before_2025_merge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# ==================== 数据加载函数 ====================

def load_main_data() -> dict:
    """加载主数据文件"""
    logger.info("[LOAD] 加载主数据文件...")

    if not MAIN_DATA_FILE.exists():
        logger.error(f"[ERROR] 主数据文件不存在: {MAIN_DATA_FILE}")
        return {"major_rank_data": []}

    with open(MAIN_DATA_FILE.resolve(), 'r', encoding='utf-8') as f:
        main_data = json.load(f)

    records = main_data.get("major_rank_data", [])
    logger.info(f"[OK] 主数据加载完成: {len(records):,} 条记录")
    return main_data

def backup_main_data(main_data: dict) -> None:
    """备份主数据文件"""
    logger.info("[BACKUP] 备份主数据文件...")

    BACKUP_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(BACKUP_FILE.resolve(), 'w', encoding='utf-8') as f:
        json.dump(main_data, f, ensure_ascii=False, indent=2)

    logger.info(f"[OK] 备份完成: {BACKUP_FILE}")

def load_province_2025_data() -> list:
    """加载所有2025年省份数据"""
    logger.info("[LOAD] 加载2025年省份数据...")

    if not PROVINCE_DATA_DIR.exists():
        logger.error(f"[ERROR] 省份数据目录不存在: {PROVINCE_DATA_DIR}")
        return []

    all_2025_records = []
    province_files = list(PROVINCE_DATA_DIR.glob("*_2025_mock.json"))

    logger.info(f"[INFO] 发现 {len(province_files)} 个省份数据文件")

    for province_file in province_files:
        logger.info(f"[LOAD] 处理文件: {province_file.name}")

        try:
            with open(province_file.resolve(), 'r', encoding='utf-8') as f:
                province_data = json.load(f)

            records = province_data.get("records", [])
            province_name = province_data.get("province", "未知")

            logger.info(f"  {province_name}: {len(records):,} 条记录")

            all_2025_records.extend(records)

        except Exception as e:
            logger.error(f"[ERROR] 处理文件失败 {province_file.name}: {e}")

    logger.info(f"[OK] 2025年省份数据加载完成: {len(all_2025_records):,} 条记录")
    return all_2025_records

def merge_data(main_data: dict, records_2025: list) -> dict:
    """合并2025年数据到主数据"""
    logger.info("[MERGE] 合并2025年数据...")

    existing_records = main_data.get("major_rank_data", [])

    # 统计现有数据年份分布
    year_stats = {}
    for record in existing_records:
        year = record.get("year", 0)
        year_stats[year] = year_stats.get(year, 0) + 1

    logger.info(f"[INFO] 现有数据年份分布: {year_stats}")
    logger.info(f"[INFO] 现有记录总数: {len(existing_records):,}")
    logger.info(f"[INFO] 新增2025记录: {len(records_2025):,}")

    # 合并数据
    merged_records = existing_records + records_2025

    # 更新元数据
    main_data["major_rank_data"] = merged_records

    if "metadata" not in main_data:
        main_data["metadata"] = {}

    main_data["metadata"]["total_records"] = len(merged_records)
    main_data["metadata"]["last_updated"] = datetime.now().isoformat()
    main_data["metadata"]["2025_data_added"] = True
    main_data["metadata"]["2025_records_count"] = len(records_2025)

    logger.info(f"[OK] 数据合并完成: {len(merged_records):,} 条记录")

    # 统计合并后的年份分布
    merged_year_stats = {}
    for record in merged_records:
        year = record.get("year", 0)
        merged_year_stats[year] = merged_year_stats.get(year, 0) + 1

    logger.info(f"[INFO] 合并后年份分布: {merged_year_stats}")

    return main_data

def save_merged_data(main_data: dict) -> None:
    """保存合并后的数据"""
    logger.info("[SAVE] 保存合并后的主数据文件...")

    with open(MAIN_DATA_FILE.resolve(), 'w', encoding='utf-8') as f:
        json.dump(main_data, f, ensure_ascii=False, indent=2)

    logger.info(f"[OK] 合并后数据已保存: {MAIN_DATA_FILE}")

# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    print("=" * 80)
    print("合并2025年省份数据到主数据文件")
    print("=" * 80)
    print()

    # 步骤1: 加载主数据
    print("[STEP-1] 加载主数据文件...")
    main_data = load_main_data()

    if not main_data:
        logger.error("[ERROR] 无法加载主数据")
        return

    # 步骤2: 备份主数据
    print("[STEP-2] 备份主数据文件...")
    backup_main_data(main_data)

    # 步骤3: 加载2025年省份数据
    print("[STEP-3] 加载2025年省份数据...")
    records_2025 = load_province_2025_data()

    if not records_2025:
        logger.error("[ERROR] 没有找到2025年数据")
        return

    # 步骤4: 合并数据
    print("[STEP-4] 合并数据...")
    merged_data = merge_data(main_data, records_2025)

    # 步骤5: 保存合并后数据
    print("[STEP-5] 保存合并后数据...")
    save_merged_data(merged_data)

    # 输出结果摘要
    print()
    print("=" * 80)
    print("[合并完成] 2025年数据已合并到主数据文件")
    print("=" * 80)

    total_records = len(merged_data.get("major_rank_data", []))
    print(f"合并后总记录数: {total_records:,}")
    print(f"新增2025记录数: {len(records_2025):,}")
    print(f"原主数据记录数: {len(main_data.get('major_rank_data', [])) - len(records_2025):,}")
    print()
    print(f"[输出文件]")
    print(f"  合并后主数据: {MAIN_DATA_FILE}")
    print(f"  原数据备份: {BACKUP_FILE}")
    print("=" * 80)

if __name__ == "__main__":
    main()