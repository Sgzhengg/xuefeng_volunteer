#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用pdfplumber解析PDF表格数据
"""

import pdfplumber
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'pdf_table_parse_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PDFTableParser:
    """PDF表格解析器"""

    def __init__(self):
        self.all_records = []

    def parse_pdf_file(self, pdf_path: str, category: str) -> list:
        """解析PDF文件中的表格数据"""
        logger.info(f"解析PDF文件: {pdf_path}")
        logger.info(f"科类: {category}")

        records = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                logger.info(f"PDF页数: {len(pdf.pages)}")

                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"处理第 {page_num} 页...")

                    # 提取表格
                    tables = page.extract_tables()

                    if tables:
                        logger.info(f"  找到 {len(tables)} 个表格")

                        for table_num, table in enumerate(tables, 1):
                            logger.info(f"  表格 {table_num}: {len(table)} 行")

                            # 解析表格数据
                            page_records = self._parse_table(table, category)
                            if page_records:
                                records.extend(page_records)
                                logger.info(f"    提取到 {len(page_records)} 条记录")
                    else:
                        # 如果没有找到表格，尝试提取文本
                        text = page.extract_text()
                        if text:
                            logger.info(f"  未找到表格，提取文本: {len(text)} 字符")

        except Exception as e:
            logger.error(f"解析PDF失败: {e}")

        logger.info(f"页面 {category} 总共提取到 {len(records)} 条记录")
        return records

    def _parse_table(self, table, category: str) -> list:
        """解析表格数据"""
        records = []

        if not table or len(table) == 0:
            return records

        # 查找表头
        header_row = None
        header_row_index = 0

        for i, row in enumerate(table):
            if row and len(row) >= 4:
                # 检查是否包含表头关键词
                row_text = ' '.join([str(cell) if cell else '' for cell in row])
                if '院校' in row_text and ('代码' in row_text or '名称' in row_text):
                    header_row = row
                    header_row_index = i
                    logger.info(f"找到表头: {[str(cell) if cell else '' for cell in row]}")
                    break

        if not header_row:
            # 如果没找到表头，假设第一行是表头
            if table and len(table) > 0:
                header_row = table[0]
                header_row_index = 0
            else:
                return records

        # 解析数据行
        for row in table[header_row_index + 1:]:
            if not row or len(row) < 4:
                continue

            record = self._parse_row(row, header_row, category)
            if record and self._is_valid_record(record):
                records.append(record)

        return records

    def _parse_row(self, row, header, category: str) -> dict:
        """解析单行数据"""
        try:
            # 创建字段映射
            data = {}
            for i, cell in enumerate(row):
                if i < len(header):
                    header_text = str(header[i]) if header[i] else ''
                    cell_text = str(cell) if cell else ''

                    if header_text and cell_text:
                        data[header_text] = cell_text

            # 提取关键字段
            university_code = self._extract_university_code(data)
            university_name = self._extract_university_name(data)
            group_code = self._extract_group_code(data)
            min_score = self._extract_min_score(data)
            min_rank = self._extract_min_rank(data)
            plan_count = self._extract_plan_count(data)

            if university_name and group_code and min_score and min_rank:
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
            logger.debug(f"解析行失败: {row}, 错误: {e}")

        return None

    def _extract_university_code(self, data: dict) -> str:
        """提取院校代码"""
        for key, value in data.items():
            if '代码' in key or '院校' in key:
                if re.match(r'^\d{5}$', str(value).strip()):
                    return str(value).strip()
        return ''

    def _extract_university_name(self, data: dict) -> str:
        """提取院校名称"""
        for key, value in data.items():
            if '名称' in key or '院校' in key or '学校' in key:
                value_str = str(value).strip()
                # 过滤掉纯数字或代码
                if value_str and not re.match(r'^\d{5}$', value_str):
                    return value_str
        return ''

    def _extract_group_code(self, data: dict) -> str:
        """提取专业组代码"""
        for key, value in data.items():
            if '专业组' in key or '组' in key:
                value_str = str(value).strip()
                if value_str and value_str != 'None':
                    return value_str
        return ''

    def _extract_min_score(self, data: dict) -> int:
        """提取最低分"""
        for key, value in data.items():
            if '分数' in key or '投档' in key or '最低分' in key:
                try:
                    value_str = str(value).strip().replace(',', '')
                    if value_str and value_str != 'None':
                        score = int(value_str)
                        if 100 <= score <= 750:
                            return score
                except:
                    continue
        return 0

    def _extract_min_rank(self, data: dict) -> int:
        """提取最低排位"""
        for key, value in data.items():
            if '排位' in key or '位次' in key:
                try:
                    value_str = str(value).strip().replace(',', '')
                    if value_str and value_str != 'None':
                        rank = int(value_str)
                        if rank > 0:
                            return rank
                except:
                    continue
        return 0

    def _extract_plan_count(self, data: dict) -> int:
        """提取计划数"""
        for key, value in data.items():
            if '计划' in key:
                try:
                    value_str = str(value).strip().replace(',', '')
                    if value_str and value_str != 'None':
                        return int(value_str)
                except:
                    continue
        return 0

    def _is_valid_record(self, record: dict) -> bool:
        """验证记录是否有效"""
        return bool(
            record.get('university') and
            record.get('group_code') and
            record.get('min_score', 0) >= 100 and
            record.get('min_score', 0) <= 750 and
            record.get('min_rank', 0) > 0
        )

    def clean_data(self, records: list) -> list:
        """清理数据"""
        logger.info("开始数据清理...")

        cleaned_records = []
        removed_count = 0

        for record in records:
            # 检查是否包含无效关键词
            university = record.get('university', '')
            invalid_keywords = ['一般', '测试', '模拟', 'test', 'mock']

            if any(kw in university.lower() for kw in invalid_keywords):
                removed_count += 1
                continue

            # 检查数据有效性
            min_rank = record.get('min_rank', 0)
            min_score = record.get('min_score', 0)

            if not min_rank or min_rank == 0:
                removed_count += 1
                continue

            if min_score < 100 or min_score > 750:
                removed_count += 1
                continue

            cleaned_records.append(record)

        logger.info(f"清理前: {len(records)} 条")
        logger.info(f"清理后: {len(cleaned_records)} 条")
        logger.info(f"移除: {removed_count} 条")

        return cleaned_records

    def verify_completeness(self, records: list) -> tuple:
        """验证数据完整性"""
        logger.info("验证数据完整性...")

        total = len(records)
        logger.info(f"总记录数: {total}")

        if total == 0:
            return False, "FAILED_TO_FETCH_REAL_DATA"

        if total < 3000:
            return False, f"INCOMPLETE_DATA: {total}/3000"

        # 检查院校覆盖
        universities = set(r['university'] for r in records)
        has_985 = any(uni in universities for uni in ['北京大学', '清华大学', '中山大学', '华南理工大学'])
        has_private = any('民办' in uni or '独立学院' in uni for uni in universities)

        logger.info(f"独立院校: {len(universities)}")
        logger.info(f"包含985: {has_985}")
        logger.info(f"包含民办: {has_private}")

        if not has_985:
            return False, "INCOMPLETE_DATA: 缺少985院校"

        if not has_private:
            return False, "INCOMPLETE_DATA: 缺少民办院校"

        return True, "PASS"

    def export_results(self, records: list) -> bool:
        """导出结果"""
        logger.info("导出结果...")

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # 导出CSV
            csv_file = output_dir / f"guangdong_2025_admission_{timestamp}.csv"
            df = pd.DataFrame(records)
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            logger.info(f"✓ CSV文件: {csv_file}")

            # 导出Excel
            excel_file = output_dir / f"guangdong_2025_admission_{timestamp}.xlsx"
            df.to_excel(excel_file, index=False, engine='openpyxl')
            logger.info(f"✓ Excel文件: {excel_file}")

            # 导出数据质量报告
            quality_report = {
                'total_records': len(records),
                'data_source': '广东省教育考试院官方PDF',
                'verified': True,
                'categories': '物理,历史',
                'extraction_date': datetime.now().isoformat()
            }

            report_file = output_dir / f"data_quality_report_{timestamp}.json"
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(quality_report, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ 质量报告: {report_file}")

            return True

        except Exception as e:
            logger.error(f"导出失败: {e}")
            return False


def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("2025年广东高考投档线PDF表格解析系统")
    logger.info("=" * 80)

    parser = PDFTableParser()

    # 查找PDF文件
    output_dir = Path("output")
    physics_pdf = output_dir / "广东省2025年本科普通类(物理)投档情况.pdf"
    history_pdf = output_dir / "广东省2025年本科普通类(历史)投档情况.pdf"

    all_records = []

    # 解析物理类PDF
    if physics_pdf.exists():
        logger.info("\n解析物理类投档PDF...")
        physics_records = parser.parse_pdf_file(str(physics_pdf), '物理')
        all_records.extend(physics_records)
    else:
        logger.error(f"文件不存在: {physics_pdf}")

    # 解析历史类PDF
    if history_pdf.exists():
        logger.info("\n解析历史类投档PDF...")
        history_records = parser.parse_pdf_file(str(history_pdf), '历史')
        all_records.extend(history_records)
    else:
        logger.error(f"文件不存在: {history_pdf}")

    logger.info(f"\n总共提取到 {len(all_records)} 条记录")

    if not all_records:
        logger.error("没有提取到任何数据")
        return False

    # 数据清理
    all_records = parser.clean_data(all_records)

    # 验证完整性
    is_complete, message = parser.verify_completeness(all_records)

    if not is_complete:
        logger.error(f"验证失败: {message}")
        if "FAILED_TO_FETCH_REAL_DATA" in message:
            logger.error("\n" + "=" * 80)
            logger.error("FAILED_TO_FETCH_REAL_DATA")
            logger.error("=" * 80)
        elif "INCOMPLETE_DATA" in message:
            logger.error(f"\n{message}")
        return False

    # 导出结果
    if not parser.export_results(all_records):
        logger.error("导出结果失败")
        return False

    # 成功完成
    logger.info("\n" + "=" * 80)
    logger.info("✓ 数据解析完成！")
    logger.info("=" * 80)
    logger.info(f"✓ 成功解析 {len(all_records)} 条真实投档线数据")
    logger.info(f"✓ 数据来源: 广东省教育考试院官方PDF")
    logger.info(f"✓ 已通过完整性验证")
    logger.info(f"✓ 已生成所有输出文件")

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
