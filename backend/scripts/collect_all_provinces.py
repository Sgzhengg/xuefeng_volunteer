# -*- coding: utf-8 -*-
"""
2025年全国各省录取数据采集和补全工具

功能：
1. 检查当前数据覆盖情况
2. 多省份数据采集
3. 数据格式统一和验证
4. 分省份、分位次段统计
5. 自动合并到主数据文件

使用方法：
    python collect_all_provinces.py

作者：学锋志愿教练团队
版本：1.0.0
"""

import json
import logging
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
        logging.FileHandler(f'collect_provinces_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== 配置常量 ====================

DATA_DIR = Path("../data")
MAIN_DATA_FILE = DATA_DIR / "major_rank_data.json"
PROVINCE_DATA_DIR = DATA_DIR / "province_data_2025"

# 省份优先级配置
PROVINCE_PRIORITIES = {
    "P0": {
        "广东": {"min_records": 15000, "description": "主推省份"},
        "湖南": {"min_records": 5000, "description": "广东考生热门出省选择"},
        "江西": {"min_records": 5000, "description": "广东考生热门出省选择"},
        "广西": {"min_records": 5000, "description": "广东考生热门出省选择"},
        "福建": {"min_records": 5000, "description": "广东考生热门出省选择"},
    },
    "P1": {
        "湖北": {"min_records": 5000, "description": "生源大省"},
        "四川": {"min_records": 5000, "description": "生源大省"},
        "河南": {"min_records": 5000, "description": "生源大省"},
        "安徽": {"min_records": 5000, "description": "生源大省"},
        "北京": {"min_records": 3000, "description": "教育资源丰富"},
        "上海": {"min_records": 3000, "description": "教育资源丰富"},
        "江苏": {"min_records": 3000, "description": "教育资源丰富"},
        "浙江": {"min_records": 3000, "description": "教育资源丰富"},
    },
    "P2": {
        # 其他省份
    }
}

# 各位次段最低要求（每个省份）
RANK_RANGE_REQUIREMENTS = {
    "1-10000": 500,
    "10001-30000": 1000,
    "30001-70000": 1500,
    "70001-120000": 1000,
    "120001-200000": 500,
    "200001-350000": 500
}

# ==================== 数据分析函数 ====================

def analyze_current_data_coverage() -> Dict:
    """
    分析当前数据覆盖情况

    Returns:
        数据覆盖分析结果
    """
    logger.info("[ANALYZE] 正在分析当前数据覆盖情况...")

    try:
        with open(MAIN_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        records = data.get("major_rank_data", [])
        logger.info(f"[OK] 加载数据完成: {len(records):,} 条记录")

        # 按省份和年份分组
        coverage_data = defaultdict(lambda: defaultdict(int))
        province_year_rank_ranges = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        for record in records:
            province = record.get("province", "未知")
            year = record.get("year", 0)
            rank = record.get("min_rank", 0)

            if year == 2025:
                coverage_data[province]["total"] += 1

                # 统计位次段分布
                rank_range = get_rank_range_name(rank)
                province_year_rank_ranges[province][year][rank_range] += 1

        # 生成分析报告
        analysis = {
            "total_records_2025": sum(coverage_data[prov]["total"] for prov in coverage_data),
            "provinces_with_2025_data": len(coverage_data),
            "province_details": {},
            "rank_range_coverage": {},
            "missing_data": {}
        }

        # 各省份详情
        for province in sorted(coverage_data.keys()):
            total = coverage_data[province]["total"]
            analysis["province_details"][province] = {
                "total_records": total,
                "rank_ranges": dict(province_year_rank_ranges[province][2025])
            }

        # 整体位次段覆盖
        for province in coverage_data:
            for rank_range, count in province_year_rank_ranges[province][2025].items():
                analysis["rank_range_coverage"][rank_range] = (
                    analysis["rank_range_coverage"].get(rank_range, 0) + count
                )

        # 识别缺失数据
        all_provinces = set(PROVINCE_PRIORITIES["P0"].keys()) | \
                       set(PROVINCE_PRIORITIES["P1"].keys())

        for province in all_provinces:
            current_total = coverage_data.get(province, {}).get("total", 0)
            priority = get_province_priority(province)
            min_required = PROVINCE_PRIORITIES.get(priority, {}).get(province, {}).get("min_records", 0)

            if current_total < min_required:
                shortage = min_required - current_total
                analysis["missing_data"][province] = {
                    "current": current_total,
                    "required": min_required,
                    "shortage": shortage,
                    "priority": priority
                }

        return analysis

    except Exception as e:
        logger.error(f"[ERROR] 数据分析失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {}

def get_rank_range_name(rank: int) -> str:
    """获取位次段名称"""
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

def get_province_priority(province: str) -> str:
    """获取省份优先级"""
    for priority, provinces in PROVINCE_PRIORITIES.items():
        if province in provinces:
            return priority
    return "P2"

def analyze_rank_range_coverage(records: List[Dict], target_province: str) -> Dict:
    """
    分析特定省份的位次段覆盖情况

    Args:
        records: 数据记录列表
        target_province: 目标省份

    Returns:
        位次段覆盖分析
    """
    province_records = [
        r for r in records
        if r.get("province") == target_province and r.get("year") == 2025
    ]

    rank_range_counts = defaultdict(int)
    for record in province_records:
        rank = record.get("min_rank", 0)
        rank_range = get_rank_range_name(rank)
        rank_range_counts[rank_range] += 1

    coverage = {}
    for range_name, required in RANK_RANGE_REQUIREMENTS.items():
        current = rank_range_counts.get(range_name, 0)
        coverage[range_name] = {
            "current": current,
            "required": required,
            "shortage": max(0, required - current),
            "coverage_rate": (current / required * 100) if required > 0 else 0
        }

    return coverage

# ==================== 数据采集函数 ====================

def collect_province_data(province: str, data_sources: List[str]) -> List[Dict]:
    """
    采集单个省份的数据

    Args:
        province: 省份名称
        data_sources: 数据源文件列表

    Returns:
        采集的数据记录列表
    """
    logger.info(f"[COLLECT] 开始采集 {province} 省份数据...")

    collected_records = []

    for source_file in data_sources:
        try:
            source_path = Path(source_file)
            if not source_path.exists():
                logger.warning(f"[WARN] 数据源不存在: {source_file}")
                continue

            # 根据文件类型处理
            if source_path.suffix == '.xlsx' or source_path.suffix == '.xls':
                records = import_from_excel(source_path, province)
            elif source_path.suffix == '.json':
                records = import_from_json(source_path, province)
            else:
                logger.warning(f"[WARN] 不支持的文件类型: {source_path.suffix}")
                continue

            collected_records.extend(records)
            logger.info(f"[OK] 从 {source_path.name} 采集 {len(records)} 条记录")

        except Exception as e:
            logger.error(f"[ERROR] 处理数据源失败 {source_file}: {e}")

    logger.info(f"[OK] {province} 省份数据采集完成: {len(collected_records)} 条")
    return collected_records

def import_from_excel(file_path: Path, province: str) -> List[Dict]:
    """
    从Excel文件导入数据

    Args:
        file_path: Excel文件路径
        province: 省份名称

    Returns:
        数据记录列表
    """
    logger.info(f"[EXCEL] 正在读取Excel文件: {file_path.name}")

    try:
        df = pd.read_excel(file_path)
        records = []

        # 自动检测列名
        column_mapping = detect_excel_columns(df.columns)

        if not column_mapping.get("university_name"):
            logger.error(f"[ERROR] 无法识别Excel列名: {list(df.columns)}")
            return []

        for idx, row in df.iterrows():
            try:
                # 提取数据
                university_name = row.get(column_mapping["university_name"], "")
                min_rank_str = row.get(column_mapping.get("min_rank", ""), "")
                min_score_str = row.get(column_mapping.get("min_score", ""), "")

                # 数据清洗
                university_name = str(university_name).strip()
                min_rank = clean_rank_value(min_rank_str)
                min_score = clean_score_value(min_score_str)

                # 验证必填字段
                if not university_name or min_rank is None:
                    continue

                record = {
                    "year": 2025,
                    "province": province,
                    "university_name": university_name,
                    "major_name": "未分专业",  # Excel通常是投档线数据
                    "major_code": "000000",
                    "min_rank": min_rank,
                    "min_score": min_score,
                    "data_source": f"{province}_education_exam_2025"
                }

                records.append(record)

            except Exception as e:
                logger.debug(f"[DEBUG] 跳过第 {idx+2} 行: {e}")

        logger.info(f"[OK] Excel导入完成: {len(records)} 条有效记录")
        return records

    except Exception as e:
        logger.error(f"[ERROR] Excel文件处理失败: {e}")
        return []

def import_from_json(file_path: Path, province: str) -> List[Dict]:
    """
    从JSON文件导入数据

    Args:
        file_path: JSON文件路径
        province: 省份名称

    Returns:
        数据记录列表
    """
    logger.info(f"[JSON] 正在读取JSON文件: {file_path.name}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            records = data.get("records", data.get("major_rank_data", []))
        else:
            logger.error(f"[ERROR] 不支持的JSON格式")
            return []

        # 验证并添加省份信息
        validated_records = []
        for record in records:
            if isinstance(record, dict):
                record["province"] = province
                record["year"] = record.get("year", 2025)
                validated_records.append(record)

        logger.info(f"[OK] JSON导入完成: {len(validated_records)} 条记录")
        return validated_records

    except Exception as e:
        logger.error(f"[ERROR] JSON文件处理失败: {e}")
        return []

def detect_excel_columns(columns) -> Dict[str, str]:
    """
    自动检测Excel列名

    Args:
        columns: DataFrame列名

    Returns:
        列名映射字典
    """
    column_variants = {
        "university_name": ["院校名称", "学校名称", "大学名称", "院校", "院校代码"],
        "group_code": ["专业组代码", "专业组", "科目组"],
        "min_score": ["最低分", "投档分", "分数线"],
        "min_rank": ["最低排位", "最低位次", "投档排位", "排位"],
        "plan_count": ["计划数", "招生计划"]
    }

    detected = {}
    columns_list = [str(col).strip() for col in columns]

    for standard_name, variants in column_variants.items():
        for variant in variants:
            if variant in columns_list:
                detected[standard_name] = variant
                break

    return detected

def clean_rank_value(value: Any) -> int:
    """清理位次数据"""
    if pd.isna(value):
        return None
    value_str = str(value).strip()
    for char in [' ', ',', '位', '名', '排', '及', '以下']:
        value_str = value_str.replace(char, '')
    try:
        return int(value_str)
    except ValueError:
        return None

def clean_score_value(value: Any) -> int:
    """清理分数数据"""
    if pd.isna(value):
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None

# ==================== 数据合并函数 ====================

def merge_all_province_data(all_provinces_data: Dict[str, List[Dict]]) -> Dict:
    """
    合并所有省份数据到主数据文件

    Args:
        all_provinces_data: 各省份数据字典

    Returns:
        合并统计信息
    """
    logger.info("[MERGE] 开始合并所有省份数据...")

    # 读取主数据文件
    try:
        with open(MAIN_DATA_FILE, 'r', encoding='utf-8') as f:
            main_data = json.load(f)

        main_records = main_data.get("major_rank_data", [])
        logger.info(f"[OK] 主数据加载完成: {len(main_records):,} 条记录")

    except Exception as e:
        logger.error(f"[ERROR] 读取主数据失败: {e}")
        return {"success": False, "error": str(e)}

    # 构建现有数据索引（去重）
    existing_keys = {
        (r.get("university_name", ""), r.get("major_name", ""),
         r.get("year", 0), r.get("province", ""), r.get("min_rank", 0))
        for r in main_records
    }

    # 合并各省份数据
    statistics = {
        "total_new": 0,
        "added": 0,
        "duplicates": 0,
        "by_province": {},
        "by_year": {},
        "by_rank_range": {}
    }

    for province, records in all_provinces_data.items():
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

                        # 更新统计
                        update_statistics(statistics, record)
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

    # 更新元数据
    metadata = main_data.get("metadata", {})
    metadata.update({
        "version": "7.0.0",
        "generated_at": datetime.now().isoformat(),
        "total_records": len(main_records),
        "last_update": {
            "timestamp": datetime.now().isoformat(),
            "type": "multi_province_collection",
            "provinces_updated": len(all_provinces_data)
        }
    })

    # 保存合并后的数据
    logger.info("[SAVE] 正在保存合并后的数据...")
    merged_data = {
        "metadata": metadata,
        "major_rank_data": main_records
    }

    # 创建备份
    backup_file = create_backup()

    with open(MAIN_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)

    # 生成报告
    statistics["success"] = True
    statistics["total_after_merge"] = len(main_records)
    statistics["backup_file"] = str(backup_file)

    logger.info("=" * 60)
    logger.info("[SUCCESS] 数据合并完成！")
    logger.info(f"[STATS] 原有记录: {statistics['total_new'] + statistics['duplicates']:,} 条")
    logger.info(f"[STATS] 新增记录: {statistics['added']:,} 条")
    logger.info(f"[STATS] 重复记录: {statistics['duplicates']:,} 条")
    logger.info(f"[STATS] 当前总记录: {len(main_records):,} 条")
    logger.info(f"[BACKUP] 备份文件: {backup_file}")
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

    return True

def update_statistics(statistics: Dict, record: Dict):
    """更新统计信息"""
    province = record.get("province", "未知")
    year = record.get("year", 0)
    rank = record.get("min_rank", 0)

    statistics["by_year"][str(year)] = statistics["by_year"].get(str(year), 0) + 1

    rank_range = get_rank_range_name(rank)
    statistics["by_rank_range"][rank_range] = statistics["by_rank_range"].get(rank_range, 0) + 1

def create_backup() -> Path:
    """创建数据备份"""
    backup_dir = DATA_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"major_rank_data_backup_{timestamp}.json"

    import shutil
    shutil.copy2(MAIN_DATA_FILE, backup_file)

    logger.info(f"[BACKUP] 备份创建完成: {backup_file}")
    return backup_file

# ==================== 报告生成函数 ====================

def generate_coverage_report(analysis: Dict) -> str:
    """
    生成数据覆盖报告

    Args:
        analysis: 数据分析结果

    Returns:
        报告文件路径
    """
    logger.info("[REPORT] 正在生成数据覆盖报告...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = Path(f"data_coverage_report_{timestamp}.txt")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("2025年全国各省录取数据覆盖报告\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # 总体统计
        f.write("[总体统计]\n")
        f.write(f"2025年数据总量: {analysis['total_records_2025']:,} 条\n")
        f.write(f"覆盖省份数量: {analysis['provinces_with_2025_data']} 个\n\n")

        # 分省份统计
        f.write("[分省份统计]\n")
        for province, details in sorted(analysis["province_details"].items()):
            f.write(f"\n{province}:\n")
            f.write(f"  总记录数: {details['total_records']:,} 条\n")
            f.write(f"  位次段分布:\n")
            for rank_range, count in sorted(details["rank_ranges"].items()):
                f.write(f"    {rank_range}: {count} 条\n")

        # 整体位次段覆盖
        f.write("\n[整体位次段覆盖]\n")
        for rank_range, count in sorted(analysis["rank_range_coverage"].items()):
            f.write(f"{rank_range}: {count:,} 条\n")

        # 缺失数据
        if analysis["missing_data"]:
            f.write("\n[数据缺口]\n")
            f.write("省份 | 当前数量 | 目标数量 | 缺口 | 优先级\n")
            f.write("-" * 60 + "\n")

            for province, info in sorted(analysis["missing_data"].items()):
                f.write(f"{province} | {info['current']:,} | {info['required']:,} | ")
                f.write(f"{info['shortage']:,} | {info['priority']}\n")

        f.write("\n" + "=" * 80 + "\n")

    logger.info(f"[OK] 报告已保存: {report_file}")
    return str(report_file)

# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    print("=" * 80)
    print("2025年全国各省录取数据采集和补全工具")
    print("=" * 80)
    print()

    # 1. 分析当前数据覆盖情况
    logger.info("[STEP-1] 分析当前数据覆盖情况...")
    analysis = analyze_current_data_coverage()

    if not analysis:
        logger.error("[ERROR] 数据分析失败，请检查 major_rank_data.json")
        return

    # 2. 生成覆盖报告
    logger.info("[STEP-2] 生成数据覆盖报告...")
    report_file = generate_coverage_report(analysis)

    # 3. 检查省份数据目录
    PROVINCE_DATA_DIR.mkdir(exist_ok=True)

    # 4. 扫描已有数据源
    logger.info("[STEP-3] 扫描省份数据源...")
    province_files = {}
    for province_dir in PROVINCE_DATA_DIR.iterdir():
        if province_dir.is_dir():
            province_name = province_dir.name
            data_files = list(province_dir.glob("*.xlsx")) + list(province_dir.glob("*.json"))
            if data_files:
                province_files[province_name] = [str(f) for f in data_files]
                logger.info(f"[FOUND] {province_name}: {len(data_files)} 个数据文件")

    # 5. 采集各省份数据
    logger.info("[STEP-4] 开始采集各省份数据...")
    all_provinces_data = {}

    for province, data_files in province_files.items():
        province_data = collect_province_data(province, data_files)
        if province_data:
            all_provinces_data[province] = province_data

    # 6. 合并数据
    if all_provinces_data:
        logger.info("[STEP-5] 合并所有省份数据...")
        merge_result = merge_all_province_data(all_provinces_data)

        if merge_result.get("success"):
            # 7. 生成最终报告
            logger.info("[STEP-6] 生成最终验证报告...")
            final_analysis = analyze_current_data_coverage()
            final_report = generate_coverage_report(final_analysis)

            print("\n" + "=" * 80)
            print("[SUCCESS] 全国省份数据采集完成！")
            print(f"[INFO] 详细报告: {report_file}")
            print(f"[INFO] 最终报告: {final_report}")
            print("=" * 80)
        else:
            logger.error("[ERROR] 数据合并失败")
    else:
        logger.warning("[WARN] 没有找到任何省份数据文件")
        logger.info("[INFO] 请将各省份数据文件放入 data/province_data_2025/ 目录")
        logger.info("[INFO] 目录结构示例:")
        logger.info("  data/province_data_2025/")
        logger.info("    ├── 广东/")
        logger.info("    │   ├── 2025本科投档线.xlsx")
        logger.info("    │   └── 2025专科投档线.xlsx")
        logger.info("    ├── 湖南/")
        logger.info("    │   └── 2025年投档线.xlsx")
        logger.info("    └── ...")

if __name__ == "__main__":
    main()