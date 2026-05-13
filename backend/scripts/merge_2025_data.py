# -*- coding: utf-8 -*-
"""
将新导入的 2025 年数据合并到 major_rank_data.json

功能：
1. 读取新的2025年数据
2. 合并到主数据文件
3. 自动去重（基于院校+专业+年份+省份+位次组合）
4. 更新元数据信息
5. 生成合并报告

使用方法：
    python merge_2025_data.py <new_data_json>

作者：学锋志愿教练团队
版本：1.0.0
"""

import json
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple

# ==================== 日志配置 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'merge_2025_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== 配置常量 ====================

MAIN_DATA_FILE = Path("../data/major_rank_data.json")
BACKUP_DIR = Path("../data/backups")

# ==================== 数据合并函数 ====================

def backup_main_data() -> Path:
    """
    备份主数据文件

    Returns:
        备份文件路径
    """
    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"major_rank_data_backup_{timestamp}.json"

    logger.info(f"[BACKUP] 正在备份主数据文件...")

    try:
        # 读取原数据
        with open(MAIN_DATA_FILE, 'r', encoding='utf-8') as f:
            main_data = json.load(f)

        # 写入备份文件
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(main_data, f, ensure_ascii=False, indent=2)

        logger.info(f"[OK] 备份完成: {backup_file}")
        return backup_file

    except Exception as e:
        logger.error(f"[ERROR] 备份失败: {e}")
        raise

def merge_data(new_data_path: str) -> Dict:
    """
    合并新数据到主数据文件，自动去重

    Args:
        new_data_path: 新数据文件路径

    Returns:
        合并统计信息
    """
    logger.info("[START] 开始合并2025年数据")
    logger.info(f"[NEW_DATA] 文件路径: {new_data_path}")

    # 1. 备份主数据文件
    backup_file = backup_main_data()

    # 2. 读取主数据文件
    logger.info("[READ] 正在读取主数据文件...")
    try:
        with open(MAIN_DATA_FILE, 'r', encoding='utf-8') as f:
            main_data = json.load(f)

        main_records = main_data.get("major_rank_data", [])
        logger.info(f"[OK] 主数据加载完成: {len(main_records):,} 条记录")

    except Exception as e:
        logger.error(f"[ERROR] 读取主数据失败: {e}")
        return {"success": False, "error": str(e)}

    # 3. 读取新数据文件
    logger.info("[READ] 正在读取新数据文件...")
    try:
        with open(new_data_path, 'r', encoding='utf-8') as f:
            new_data = json.load(f)

        new_records = new_data if isinstance(new_data, list) else new_data.get("records", new_data.get("major_rank_data", []))
        logger.info(f"[OK] 新数据加载完成: {len(new_records):,} 条记录")

    except Exception as e:
        logger.error(f"[ERROR] 读取新数据失败: {e}")
        return {"success": False, "error": str(e)}

    # 4. 构建现有数据索引（用于去重）
    logger.info("[INDEX] 正在构建现有数据索引...")
    existing_keys = build_data_index(main_records)
    logger.info(f"[OK] 索引构建完成: {len(existing_keys):,} 个唯一键")

    # 5. 合并数据（去重）
    logger.info("[MERGE] 正在合并数据...")
    statistics = {
        "total_new": len(new_records),
        "added": 0,
        "duplicates": 0,
        "errors": 0,
        "by_province": {},
        "by_year": {},
        "by_rank_range": {}
    }

    for record in new_records:
        try:
            # 构建数据键
            key = build_record_key(record)

            if key not in existing_keys:
                # 验证数据完整性
                if validate_record(record):
                    main_records.append(record)
                    existing_keys.add(key)
                    statistics["added"] += 1

                    # 统计信息
                    update_statistics(statistics, record)
                else:
                    statistics["errors"] += 1
            else:
                statistics["duplicates"] += 1

        except Exception as e:
            logger.error(f"[ERROR] 处理记录失败: {e}")
            statistics["errors"] += 1

    # 6. 更新元数据
    logger.info("[UPDATE] 正在更新元数据...")
    metadata = main_data.get("metadata", {})

    metadata.update({
        "version": "6.1.0",  # 更新版本号
        "generated_at": datetime.now().isoformat(),
        "total_records": len(main_records),
        "last_merge": {
            "timestamp": datetime.now().isoformat(),
            "source_file": new_data_path,
            "backup_file": str(backup_file),
            "records_added": statistics["added"],
            "records_skipped": statistics["duplicates"]
        }
    })

    # 7. 保存合并后的数据
    logger.info("[SAVE] 正在保存合并后的数据...")
    merged_data = {
        "metadata": metadata,
        "major_rank_data": main_records
    }

    with open(MAIN_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)

    # 8. 输出合并报告
    logger.info("=" * 60)
    logger.info("[SUCCESS] 数据合并完成！")
    logger.info(f"[STATS] 原有记录: {statistics['total_new'] + statistics['duplicates']:,} 条")
    logger.info(f"[STATS] 新增记录: {statistics['added']:,} 条")
    logger.info(f"[STATS] 重复记录: {statistics['duplicates']:,} 条")
    logger.info(f"[STATS] 错误记录: {statistics['errors']:,} 条")
    logger.info(f"[STATS] 当前总记录: {len(main_records):,} 条")
    logger.info(f"[BACKUP] 备份文件: {backup_file}")
    logger.info("=" * 60)

    # 9. 输出分省份数据统计
    if statistics["by_province"]:
        logger.info("[STATS] 分省份数量:")
        for province, count in sorted(statistics["by_province"].items()):
            logger.info(f"  {province}: {count:,} 条")

    # 10. 输出分年份数据统计
    if statistics["by_year"]:
        logger.info("[STATS] 分年份数量:")
        for year, count in sorted(statistics["by_year"].items()):
            logger.info(f"  {year}: {count:,} 条")

    # 11. 输出分位次段统计
    if statistics["by_rank_range"]:
        logger.info("[STATS] 分位次段数量:")
        for range_name, count in sorted(statistics["by_rank_range"].items()):
            logger.info(f"  {range_name}: {count:,} 条")

    statistics["success"] = True
    statistics["total_after_merge"] = len(main_records)

    # 12. 保存合并报告
    report_file = Path(f"merge_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(statistics, f, ensure_ascii=False, indent=2)
    logger.info(f"[REPORT] 合并报告已保存: {report_file}")

    return statistics

def build_data_index(records: List[Dict]) -> Set[Tuple]:
    """
    构建数据索引

    Args:
        records: 记录列表

    Returns:
        数据键集合
    """
    return {build_record_key(record) for record in records}

def build_record_key(record: Dict) -> Tuple:
    """
    构建记录的唯一键

    Args:
        record: 数据记录

    Returns:
        唯一键元组
    """
    return (
        record.get("university_name", ""),
        record.get("major_name", ""),
        record.get("year", 0),
        record.get("province", ""),
        record.get("min_rank", 0)
    )

def validate_record(record: Dict) -> bool:
    """
    验证记录数据完整性

    Args:
        record: 数据记录

    Returns:
        是否有效
    """
    # 必填字段检查
    required_fields = ["university_name", "major_name", "year", "province"]
    for field in required_fields:
        if not record.get(field):
            return False

    # 位次检查
    min_rank = record.get("min_rank")
    if min_rank is None or min_rank <= 0:
        return False

    # 年份检查
    year = record.get("year")
    if year not in [2023, 2024, 2025]:
        logger.warning(f"[WARN] 异常年份: {year}")
        return False

    return True

def update_statistics(statistics: Dict, record: Dict):
    """
    更新统计信息

    Args:
        statistics: 统计字典
        record: 数据记录
    """
    # 按省份统计
    province = record.get("province", "未知")
    statistics["by_province"][province] = statistics["by_province"].get(province, 0) + 1

    # 按年份统计
    year = record.get("year", 0)
    statistics["by_year"][str(year)] = statistics["by_year"].get(str(year), 0) + 1

    # 按位次段统计
    rank = record.get("min_rank", 0)
    rank_range = get_rank_range_name(rank)
    statistics["by_rank_range"][rank_range] = statistics["by_rank_range"].get(rank_range, 0) + 1

def get_rank_range_name(rank: int) -> str:
    """
    获取位次段名称

    Args:
        rank: 位次

    Returns:
        位次段名称
    """
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

# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    if len(sys.argv) < 2:
        print("=" * 60)
        print("2025年数据合并工具")
        print("=" * 60)
        print()
        print("使用方法:")
        print("  python merge_2025_data.py <new_data_json>")
        print()
        print("功能:")
        print("  1. 备份主数据文件")
        print("  2. 合并新数据到主文件")
        print("  3. 自动去重和数据验证")
        print("  4. 生成合并报告")
        print()
        print("示例:")
        print("  python merge_2025_data.py guangdong_2025_expanded.json")
        print()
        return

    new_data_file = sys.argv[1]

    # 验证文件路径
    if not Path(new_data_file).exists():
        logger.error(f"[ERROR] 新数据文件不存在: {new_data_file}")
        return

    # 验证主数据文件
    if not MAIN_DATA_FILE.exists():
        logger.error(f"[ERROR] 主数据文件不存在: {MAIN_DATA_FILE}")
        logger.info("[INFO] 请确保 major_rank_data.json 存在")
        return

    # 执行合并
    try:
        result = merge_data(new_data_file)

        if result.get("success"):
            logger.info("[SUCCESS] 数据合并成功完成！")
        else:
            logger.error(f"[FAILED] 数据合并失败: {result.get('error')}")

    except Exception as e:
        logger.error(f"[ERROR] 合并过程发生异常: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()