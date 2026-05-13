#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新验证并导出已提取的2025年广东高考投档线数据
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataRevalidator:
    """数据重新验证器"""

    def __init__(self):
        self.records = []

    def recreate_from_pdf(self):
        """重新从PDF提取数据"""
        logger.info("重新从PDF提取数据...")

        import pdfplumber

        output_dir = Path("output")
        physics_pdf = output_dir / "广东省2025年本科普通类(物理)投档情况.pdf"
        history_pdf = output_dir / "广东省2025年本科普通类(历史)投档情况.pdf"

        all_records = []

        # 处理物理类
        if physics_pdf.exists():
            logger.info("处理物理类PDF...")
            with pdfplumber.open(physics_pdf) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if table and len(table) > 1:
                            # 跳过表头
                            for row in table[1:]:
                                if row and len(row) >= 7:
                                    record = self._parse_row(row, '物理')
                                    if record:
                                        all_records.append(record)

        # 处理历史类
        if history_pdf.exists():
            logger.info("处理历史类PDF...")
            with pdfplumber.open(history_pdf) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if table and len(table) > 1:
                            for row in table[1:]:
                                if row and len(row) >= 7:
                                    record = self._parse_row(row, '历史')
                                    if record:
                                        all_records.append(record)

        self.records = all_records
        logger.info(f"总共提取 {len(all_records)} 条记录")
        return all_records

    def _parse_row(self, row, category):
        """解析行数据"""
        try:
            university_code = str(row[0]).strip() if row[0] else ''
            university_name = str(row[1]).strip() if row[1] else ''
            group_code = str(row[2]).strip() if row[2] else ''
            plan_count = str(row[3]).strip() if row[3] else ''

            # 提取最低分
            min_score = 0
            if row[5]:
                try:
                    score_str = str(row[5]).strip().replace(',', '')
                    min_score = int(score_str)
                except:
                    pass

            # 提取最低排位
            min_rank = 0
            if row[6]:
                try:
                    rank_str = str(row[6]).strip().replace(',', '')
                    min_rank = int(rank_str)
                except:
                    pass

            # 验证数据有效性
            if university_name and group_code and 100 <= min_score <= 750 and min_rank > 0:
                return {
                    'university_code': university_code,
                    'university': university_name,
                    'category': category,
                    'group_code': group_code,
                    'min_score': min_score,
                    'min_rank': min_rank,
                    'plan_count': plan_count,
                    'source': '广东省教育考试院官方PDF',
                    'verified': True,
                    'has_major_details': False
                }
        except Exception as e:
            logger.debug(f"解析行失败: {e}")

        return None

    def verify_comprehensive(self, records):
        """全面验证数据"""
        logger.info("全面验证数据...")

        total = len(records)
        universities = set(r['university'] for r in records)

        physics_records = [r for r in records if r['category'] == '物理']
        history_records = [r for r in records if r['category'] == '历史']

        logger.info(f"总记录数: {total}")
        logger.info(f"独立院校数: {len(universities)}")
        logger.info(f"物理类记录: {len(physics_records)}")
        logger.info(f"历史类记录: {len(history_records)}")

        # 检查985/211
        top_unis = ['北京大学', '清华大学', '复旦大学', '上海交通大学',
                   '浙江大学', '南京大学', '中山大学', '华南理工大学']
        has_top = any(uni in universities for uni in top_unis)
        logger.info(f"包含顶尖院校: {has_top}")

        # 检查分数范围
        scores = [r['min_score'] for r in records]
        min_score = min(scores)
        max_score = max(scores)
        logger.info(f"分数范围: {min_score}-{max_score}")

        # 检查广东本地院校
        local_unis = [uni for uni in universities if '广东' in uni]
        logger.info(f"广东本地院校: {len(local_unis)}")

        # 检查各类院校类型（通过代码范围）
        code_ranges = {}
        for record in records:
            code = record.get('university_code', '')
            if code and len(code) == 5:
                code_prefix = code[:2]
                code_ranges[code_prefix] = code_ranges.get(code_prefix, 0) + 1

        logger.info(f"代码分布: {dict(list(code_ranges.items())[:5])}")

        return {
            'total': total,
            'universities': len(universities),
            'physics': len(physics_records),
            'history': len(history_records),
            'has_top': has_top,
            'score_range': f"{min_score}-{max_score}",
            'local_unis': len(local_unis)
        }

    def export_final_data(self, records):
        """导出最终数据"""
        logger.info("导出最终数据...")

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 导出CSV
        csv_file = output_dir / f"guangdong_2025_final_{timestamp}.csv"
        df = pd.DataFrame(records)
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        logger.info(f"✓ CSV文件: {csv_file}")

        # 导出Excel
        excel_file = output_dir / f"guangdong_2025_final_{timestamp}.xlsx"
        df.to_excel(excel_file, index=False, engine='openpyxl')
        logger.info(f"✓ Excel文件: {excel_file}")

        # 导出统计报告
        stats = self.verify_comprehensive(records)

        report_file = output_dir / f"final_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ 统计报告: {report_file}")

        return True


def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("2025年广东高考投档线数据重新验证和导出")
    logger.info("=" * 80)

    validator = DataRevalidator()

    # 重新提取数据
    records = validator.recreate_from_pdf()

    if len(records) < 3000:
        logger.error(f"数据量不足: {len(records)}/3000")
        return False

    # 全面验证
    stats = validator.verify_comprehensive(records)
    logger.info("\n数据统计:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")

    # 导出数据
    if not validator.export_final_data(records):
        logger.error("导出失败")
        return False

    logger.info("\n" + "=" * 80)
    logger.info("✓ 数据提取和验证完成！")
    logger.info("=" * 80)
    logger.info(f"✓ 成功处理 {len(records)} 条真实投档线数据")
    logger.info(f"✓ 数据来源: 广东省教育考试院官方PDF")
    logger.info(f"✓ 覆盖院校: {stats['universities']} 所")
    logger.info(f"✓ 物理类: {stats['physics']} 条，历史类: {stats['history']} 条")

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
