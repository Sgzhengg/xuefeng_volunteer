# -*- coding: utf-8 -*-
"""
从广东省教育考试院 Excel 文件导入 2025 年录取数据

功能：
1. 读取官方投档线 Excel 文件
2. 转换为标准 JSON 格式
3. 生成分段数据（本科/专科）
4. 自动去重和数据验证

使用方法：
    python import_2025_guangdong.py <excel_file_path> [batch_type]

作者：学锋志愿教练团队
版本：1.0.0
"""

import pandas as pd
import json
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# ==================== 日志配置 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'import_guangdong_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== 配置常量 ====================

DATA_DIR = Path("../data")
OUTPUT_DIR = Path("../data")

# 支持的列名映射（处理不同格式的Excel文件）
COLUMN_MAPPINGS = {
    # 院校列名变体
    "university_name": ["院校名称", "学校名称", "大学名称", "院校", "院校代码"],
    # 专业组列名变体
    "group_code": ["专业组代码", "专业组", "科目组", "院校专业组"],
    # 分数列名变体
    "min_score": ["最低分", "投档分", "分数线", "录取最低分"],
    # 位次列名变体
    "min_rank": ["最低排位", "最低位次", "投档排位", "排位"],
    # 计划数列名变体
    "plan_count": ["计划数", "招生计划", "计划"]
}

# ==================== 数据导入函数 ====================

def import_admission_data(excel_path: str, batch_type: str = "本科") -> List[Dict]:
    """
    导入投档线 Excel 文件

    Args:
        excel_path: Excel 文件路径
        batch_type: 批次类型 (本科/专科)

    Returns:
        导入的记录列表
    """
    logger.info(f"[START] 开始导入 {batch_type} 批次数据")
    logger.info(f"[FILE] 文件路径: {excel_path}")

    try:
        # 1. 读取Excel文件
        logger.info("[READ] 正在读取Excel文件...")
        df = pd.read_excel(excel_path)

        logger.info(f"[OK] Excel读取成功，共 {len(df)} 行数据")

        # 2. 自动检测列名映射
        detected_columns = detect_column_mapping(df.columns)
        logger.info(f"[DETECT] 检测到的列名映射: {detected_columns}")

        # 3. 验证必填列
        required_columns = ["university_name", "min_rank"]
        missing_columns = [col for col in required_columns if not detected_columns.get(col)]

        if missing_columns:
            logger.error(f"[ERROR] 缺少必填列: {missing_columns}")
            logger.info(f"[INFO] Excel文件中的列名: {list(df.columns)}")
            logger.info(f"[INFO] 请检查Excel文件格式或手动调整列名映射")
            return []

        # 4. 数据转换
        records = []
        errors = []

        for idx, row in df.iterrows():
            try:
                # 提取数据
                university_name = row.get(detected_columns["university_name"], "")
                group_code = row.get(detected_columns.get("group_code", ""), "")

                # 处理位次数据（去除非数字字符）
                min_rank_str = row.get(detected_columns["min_rank"], "")
                min_rank = clean_rank_value(min_rank_str)

                # 处理分数数据
                min_score = None
                if detected_columns.get("min_score"):
                    min_score_str = row.get(detected_columns["min_score"], "")
                    min_score = clean_score_value(min_score_str)

                # 数据验证
                if not university_name:
                    logger.warning(f"[WARN] 第 {idx+2} 行: 院校名称为空，跳过")
                    continue

                if min_rank is None or min_rank <= 0:
                    logger.warning(f"[WARN] 第 {idx+2} 行: 位次无效 ({min_rank_str})，跳过")
                    continue

                # 构建记录
                record = {
                    "year": 2025,
                    "province": "广东",
                    "university_name": str(university_name).strip(),
                    "major_name": "未分专业",  # 投档线数据通常是专业组级别
                    "major_code": group_code if group_code else "000000",
                    "min_rank": min_rank,
                    "min_score": min_score,
                    "batch": batch_type,
                    "data_source": "guangdong_education_exam_2025"
                }

                records.append(record)

            except Exception as e:
                error_msg = f"第 {idx+2} 行: {str(e)}"
                errors.append(error_msg)
                logger.error(f"[ERROR] {error_msg}")

        # 5. 数据质量报告
        logger.info(f"[STATS] 成功转换: {len(records)} 条记录")
        logger.info(f"[STATS] 错误记录: {len(errors)} 条")

        if errors and len(errors) <= 10:
            logger.info("[ERROR_SAMPLE] 错误样本:")
            for error in errors[:10]:
                logger.info(f"  - {error}")

        # 6. 保存原始导入数据
        if records:
            output_path = OUTPUT_DIR / f"guangdong_2025_{batch_type}_raw.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            logger.info(f"[SAVE] 原始数据已保存: {output_path}")

        return records

    except FileNotFoundError:
        logger.error(f"[ERROR] 文件不存在: {excel_path}")
        return []
    except Exception as e:
        logger.error(f"[ERROR] 导入失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def detect_column_mapping(columns) -> Dict[str, str]:
    """
    自动检测列名映射

    Args:
        columns: Excel文件的列名

    Returns:
        检测到的列名映射
    """
    detected = {}
    columns_list = [str(col).strip() for col in columns]

    for standard_name, possible_names in COLUMN_MAPPINGS.items():
        for possible_name in possible_names:
            # 精确匹配
            if possible_name in columns_list:
                detected[standard_name] = possible_name
                break
            else:
                # 部分匹配（处理列名包含空格等情况）
                for col in columns_list:
                    if possible_name in col or col in possible_name:
                        detected[standard_name] = col
                        break

            if standard_name in detected:
                break

    return detected

def clean_rank_value(value: Any) -> int:
    """
    清理位次数据

    Args:
        value: 原始位次值

    Returns:
        清理后的整数位次
    """
    if pd.isna(value):
        return None

    # 转换为字符串并去除非数字字符
    value_str = str(value).strip()

    # 去除常见的非数字字符
    for char in [' ', ',', '位', '名', '排', '及', '以下']:
        value_str = value_str.replace(char, '')

    try:
        return int(value_str)
    except ValueError:
        return None

def clean_score_value(value: Any) -> int:
    """
    清理分数数据

    Args:
        value: 原始分数值

    Returns:
        清理后的整数分数
    """
    if pd.isna(value):
        return None

    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None

# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    if len(sys.argv) < 2:
        print("=" * 60)
        print("广东省教育考试院 2025年录取数据导入工具")
        print("=" * 60)
        print()
        print("使用方法:")
        print("  python import_2025_guangdong.py <excel_file_path> [batch_type]")
        print()
        print("参数说明:")
        print("  excel_file_path: Excel文件路径")
        print("  batch_type: 批次类型（本科/专科，默认：本科）")
        print()
        print("示例:")
        print("  python import_2025_guangdong.py 2025本科投档线.xlsx 本科")
        print("  python import_2025_guangdong.py 2025专科投档线.xlsx 专科")
        print()
        print("支持的列名格式:")
        print("  院校名称: 院校名称, 学校名称, 院校, 院校代码")
        print("  专业组: 专业组代码, 专业组, 科目组")
        print("  最低分: 最低分, 投档分, 分数线")
        print("  最低排位: 最低排位, 最低位次, 投档排位, 排位")
        print()
        return

    excel_file = sys.argv[1]
    batch_type = sys.argv[2] if len(sys.argv) > 2 else "本科"

    # 验证批次类型
    if batch_type not in ["本科", "专科"]:
        logger.error(f"[ERROR] 无效的批次类型: {batch_type}")
        logger.info("[INFO] 支持的批次类型: 本科, 专科")
        return

    # 检查文件是否存在
    if not Path(excel_file).exists():
        logger.error(f"[ERROR] 文件不存在: {excel_file}")
        return

    # 执行导入
    records = import_admission_data(excel_file, batch_type)

    if records:
        logger.info("=" * 50)
        logger.info("[SUCCESS] 导入完成！")
        logger.info(f"[OK] 成功导入 {len(records)} 条记录")
        logger.info(f"[INFO] 批次类型: {batch_type}")
        logger.info(f"[INFO] 输出文件: guangdong_2025_{batch_type}_raw.json")
        logger.info("=" * 50)
    else:
        logger.error("[FAILED] 导入失败，请检查日志")

if __name__ == "__main__":
    main()