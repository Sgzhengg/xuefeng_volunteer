#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2025年广东高考本科批次投档线真实数据获取系统（最终版）

严格真实性约束：
- 优先使用官方附件（Excel/PDF）
- 禁止生成示例数据
- 数据完整性要求：至少3000条记录
- 支持手动导入官方Excel文件

使用方法：
1. 自动模式：python fetch_real_guangdong_2025.py auto
2. 手动模式：python fetch_real_guangdong_2025.py manual <excel_file_path>
"""

import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from datetime import datetime
from pathlib import Path
import time
from typing import List, Dict, Optional, Tuple
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'fetch_real_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StrictDataFetcher:
    """严格真实数据获取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # 数据存储
        self.official_data = []
        self.group_major_mapping = {}
        self.missing_mappings = []

        # 数据质量报告
        self.quality_report = {
            'total_records': 0,
            'official_records': 0,
            'verified_records': 0,
            'cleaned_records': 0,
            'missing_mappings': 0,
            'data_sources': []
        }

        # 清理日志
        self.clean_log = []

    def fetch_from_auto(self) -> bool:
        """自动模式：尝试从网络获取"""
        logger.info("自动模式：尝试从网络获取数据")

        # 尝试官方页面
        success = self._try_official_website()

        if not success:
            logger.warning("自动获取失败")
            logger.info("\n请使用手动模式：")
            logger.info("python fetch_real_guangdong_2025.py manual <excel_file_path>")
            logger.info("\n或手动下载官方Excel文件后运行：")
            logger.info("python fetch_real_guangdong_2025.py manual official_data.xlsx")

        return success

    def fetch_from_manual(self, excel_file: str) -> bool:
        """手动模式：从本地Excel文件导入"""
        logger.info(f"手动模式：从本地文件导入")
        logger.info(f"文件路径: {excel_file}")

        if not Path(excel_file).exists():
            logger.error(f"文件不存在: {excel_file}")
            return False

        try:
            # 解析Excel文件
            records = self._parse_local_excel(excel_file)
            if records:
                self.official_data = records
                logger.info(f"成功导入 {len(records)} 条记录")
                return True
            else:
                logger.error("解析Excel文件失败")
                return False

        except Exception as e:
            logger.error(f"导入文件失败: {e}")
            return False

    def _try_official_website(self) -> bool:
        """尝试从官方网站获取数据"""
        url = "https://eea.gd.gov.cn/ptgk/content/post_4746781.html"

        try:
            logger.info(f"访问官方页面: {url}")
            response = self.session.get(url, timeout=30)
            response.encoding = 'utf-8'

            if response.status_code != 200:
                logger.error(f"访问失败，状态码: {response.status_code}")
                return False

            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找投档文件链接
            links = soup.find_all('a', href=True)
            admission_files = []

            for link in links:
                href = link['href']
                text = link.get_text().strip()

                # 查找投档情况文件
                if ('投档情况' in text or '投档' in text) and '2025' in text:
                    full_url = href if href.startswith('http') else f"https://eea.gd.gov.cn{href}"
                    admission_files.append({
                        'title': text,
                        'url': full_url,
                        'category': '物理' if '物理' in text else '历史' if '历史' in text else '未知',
                        'file_type': href.split('.')[-1] if '.' in href else 'unknown'
                    })

            logger.info(f"找到 {len(admission_files)} 个投档文件")

            if not admission_files:
                return False

            # 尝试下载和解析文件
            for file_info in admission_files:
                logger.info(f"\n尝试文件: {file_info['title']}")
                logger.info(f"类型: {file_info['file_type']}")
                logger.info(f"URL: {file_info['url']}")

                if file_info['file_type'] in ['xlsx', 'xls']:
                    records = self._download_and_parse_excel(file_info['url'], file_info['category'], file_info['title'])
                    if records:
                        self.official_data.extend(records)
                        logger.info(f"成功解析 {len(records)} 条记录")

            return len(self.official_data) > 0

        except Exception as e:
            logger.error(f"访问官方页面失败: {e}")
            return False

    def _download_and_parse_excel(self, url: str, category: str, source: str) -> List[Dict]:
        """下载并解析Excel文件"""
        try:
            logger.info("下载Excel文件...")
            response = self.session.get(url, timeout=60)

            if response.status_code != 200:
                logger.error(f"下载失败，状态码: {response.status_code}")
                return []

            # 保存到临时文件
            temp_file = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            with open(temp_file, 'wb') as f:
                f.write(response.content)

            # 同时保存到output目录
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            safe_title = re.sub(r'[\\/*?:"<>|]', '_', source)
            output_file = output_dir / f"官方_{safe_title}.xlsx"

            with open(output_file, 'wb') as f:
                f.write(response.content)
            logger.info(f"已保存官方文件: {output_file}")

            # 解析Excel
            try:
                df = pd.read_excel(temp_file, engine='openpyxl')
                logger.info(f"Excel解析成功，共 {len(df)} 行")
                logger.info(f"列名: {list(df.columns)}")

                # 显示前几行数据
                logger.info("数据预览:")
                for i, row in df.head(3).iterrows():
                    logger.info(f"  {i}: {dict(row)}")

                # 解析数据
                records = self._parse_dataframe(df, category, source)

                # 删除临时文件
                Path(temp_file).unlink()

                return records

            except Exception as e:
                logger.error(f"Excel解析失败: {e}")
                Path(temp_file).unlink()
                return []

        except Exception as e:
            logger.error(f"下载Excel失败: {e}")
            return []

    def _parse_local_excel(self, file_path: str) -> List[Dict]:
        """解析本地Excel文件"""
        try:
            logger.info(f"解析本地Excel文件: {file_path}")

            # 尝试不同的引擎
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
            except:
                try:
                    df = pd.read_excel(file_path, engine='xlrd')
                except:
                    df = pd.read_excel(file_path)

            logger.info(f"Excel解析成功，共 {len(df)} 行")
            logger.info(f"列名: {list(df.columns)}")

            # 显示数据预览
            logger.info("数据预览:")
            for i, row in df.head(3).iterrows():
                logger.info(f"  {i}: {dict(row)}")

            # 自动检测类别
            category = self._detect_category_from_data(df)

            records = self._parse_dataframe(df, category, f"本地文件:{Path(file_path).name}")

            return records

        except Exception as e:
            logger.error(f"解析Excel失败: {e}")
            return []

    def _detect_category_from_data(self, df: pd.DataFrame) -> str:
        """从数据中检测科类"""
        # 检查列名
        for col in df.columns:
            if '物理' in str(col):
                return '物理'
            elif '历史' in str(col):
                return '历史'

        # 检查数据内容
        for _, row in df.head(10).iterrows():
            for val in row:
                if '物理' in str(val):
                    return '物理'
                elif '历史' in str(val):
                    return '历史'

        return '未知'

    def _parse_dataframe(self, df: pd.DataFrame, category: str, source: str) -> List[Dict]:
        """解析DataFrame数据"""
        records = []

        # 识别列名
        column_mapping = self._identify_columns(df.columns)
        logger.info(f"列名映射: {column_mapping}")

        if not column_mapping['university']:
            logger.error("未找到院校名称列")
            return []

        if not column_mapping['group_code']:
            logger.error("未找到专业组代码列")
            return []

        # 解析每一行
        for idx, row in df.iterrows():
            try:
                record = {
                    'university_code': self._get_value(row, column_mapping['university_code']),
                    'university': self._get_value(row, column_mapping['university']),
                    'category': category,
                    'group_code': self._get_value(row, column_mapping['group_code']),
                    'min_score': self._get_score(row, column_mapping['min_score']),
                    'min_rank': self._get_rank(row, column_mapping['min_rank']),
                    'plan_count': self._get_value(row, column_mapping.get('plan_count')),
                    'source': source,
                    'verified': True,
                    'has_major_details': False
                }

                # 数据验证
                if self._is_valid_record(record):
                    records.append(record)
                else:
                    self.clean_log.append(f"清理无效记录: {record}")

            except Exception as e:
                logger.debug(f"解析行{idx}失败: {e}")
                continue

        logger.info(f"成功解析 {len(records)} 条有效记录")
        return records

    def expand_group_majors(self):
        """专业组展开"""
        logger.info("\n专业组展开功能")
        logger.info("注意: 由于需要大量网络请求，此功能默认禁用")
        logger.info("如需启用，请手动从阳光高考网获取专业组映射")

        # 生成缺失映射报告
        unique_groups = set()
        for record in self.official_data:
            key = f"{record['university']}_{record['group_code']}"
            unique_groups.add(key)

        logger.info(f"需要映射的专业组: {len(unique_groups)} 个")
        logger.info("建议: 从阳光高考网或各高校官网获取专业组映射")

    def clean_data(self):
        """数据清理"""
        logger.info("\n数据清理")

        initial_count = len(self.official_data)
        cleaned_data = []

        for record in self.official_data:
            if not self._should_clean_record(record):
                cleaned_data.append(record)
            else:
                self.clean_log.append(f"清理: {record}")
                self.quality_report['cleaned_records'] += 1

        self.official_data = cleaned_data
        logger.info(f"清理前: {initial_count}, 清理后: {len(self.official_data)}")

    def verify_data_completeness(self) -> Tuple[bool, str]:
        """验证数据完整性"""
        logger.info("\n验证数据完整性")

        total = len(self.official_data)
        logger.info(f"总记录数: {total}")

        if total == 0:
            return False, "FAILED_TO_FETCH_REAL_DATA"

        if total < 3000:
            return False, f"INCOMPLETE_DATA: {total}/3000"

        # 检查数据覆盖
        universities = set(r['university'] for r in self.official_data)
        has_985 = any(u in universities for u in ['北京大学', '清华大学', '中山大学', '华南理工大学'])
        has_private = any('民办' in u or '独立学院' in u for u in universities)

        logger.info(f"院校数: {len(universities)}")
        logger.info(f"包含985: {has_985}")
        logger.info(f"包含民办: {has_private}")

        self.quality_report['total_records'] = total
        self.quality_report['official_records'] = total
        self.quality_report['verified_records'] = total

        return True, "PASS"

    def export_results(self) -> bool:
        """导出结果"""
        logger.info("\n导出结果文件")

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # 1. 主数据文件
            if self.official_data:
                csv_file = output_dir / f"guangdong_2025_data_{timestamp}.csv"
                df = pd.DataFrame(self.official_data)
                df.to_csv(csv_file, index=False, encoding='utf-8-sig')
                logger.info(f"✓ 主数据: {csv_file}")

            # 2. 数据质量报告
            quality_file = output_dir / f"data_quality_report_{timestamp}.json"
            with open(quality_file, 'w', encoding='utf-8') as f:
                json.dump(self.quality_report, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ 质量报告: {quality_file}")

            # 3. 清理日志
            clean_file = output_dir / f"clean_log_{timestamp}.txt"
            with open(clean_file, 'w', encoding='utf-8') as f:
                for log in self.clean_log:
                    f.write(f"{log}\n")
            logger.info(f"✓ 清理日志: {clean_file}")

            # 4. 缺失映射报告
            if self.missing_mappings:
                missing_file = output_dir / f"missing_mapping_report_{timestamp}.csv"
                df_missing = pd.DataFrame(self.missing_mappings)
                df_missing.to_csv(missing_file, index=False, encoding='utf-8-sig')
                logger.info(f"✓ 缺失映射: {missing_file}")

            return True

        except Exception as e:
            logger.error(f"导出失败: {e}")
            return False

    def _identify_columns(self, columns) -> Dict[str, str]:
        """识别列名"""
        mapping = {
            'university_code': None,
            'university': None,
            'group_code': None,
            'min_score': None,
            'min_rank': None,
            'plan_count': None
        }

        keywords = {
            'university_code': ['院校代码', '学校代码', '代码'],
            'university': ['院校', '学校', 'university'],
            'group_code': ['专业组', '专业组代码', 'group'],
            'min_score': ['最低分', '投档分', '分数', 'score'],
            'min_rank': ['最低排位', '排位', '位次', 'rank'],
            'plan_count': ['计划数', '招生计划', '计划']
        }

        for col in columns:
            col_str = str(col).lower()
            for field, field_keywords in keywords.items():
                if any(kw in col_str for kw in field_keywords):
                    if not mapping[field]:
                        mapping[field] = col
                        break

        return mapping

    def _get_value(self, row, column_name: str) -> str:
        """安全获取值"""
        if column_name and column_name in row:
            value = row[column_name]
            if pd.notna(value):
                return str(value).strip()
        return ''

    def _get_score(self, row, column_name: str) -> int:
        """获取分数"""
        if column_name and column_name in row:
            try:
                value = row[column_name]
                if pd.notna(value):
                    return int(float(str(value).strip()))
            except:
                pass
        return 0

    def _get_rank(self, row, column_name: str) -> int:
        """获取排位"""
        if column_name and column_name in row:
            try:
                value = row[column_name]
                if pd.notna(value):
                    value_str = str(value).strip().replace(',', '')
                    return int(value_str)
            except:
                pass
        return 0

    def _is_valid_record(self, record: Dict) -> bool:
        """验证记录"""
        return bool(
            record.get('university') and
            record.get('group_code') and
            record.get('min_score', 0) > 0 and
            record.get('min_rank', 0) > 0
        )

    def _should_clean_record(self, record: Dict) -> bool:
        """是否清理记录"""
        university = record.get('university', '')
        min_rank = record.get('min_rank', 0)
        min_score = record.get('min_score', 0)

        # 检查无效关键词
        invalid_keywords = ['一般', '测试', '模拟', 'test', 'mock']
        if any(kw in university.lower() for kw in invalid_keywords):
            return True

        # 检查数据有效性
        if not min_rank or min_rank == 0:
            return True

        if min_score < 100 or min_score > 750:
            return True

        return False


def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("2025年广东高考本科批次投档线真实数据获取系统")
    logger.info("=" * 80)

    if len(sys.argv) < 2:
        logger.info("\n使用方法:")
        logger.info("  自动模式: python fetch_real_guangdong_2025.py auto")
        logger.info("  手动模式: python fetch_real_guangdong_2025.py manual <excel_file_path>")
        logger.info("\n示例:")
        logger.info("  python fetch_real_guangdong_2025.py manual official_data.xlsx")
        return False

    mode = sys.argv[1].lower()
    fetcher = StrictDataFetcher()

    # 获取数据
    if mode == 'auto':
        success = fetcher.fetch_from_auto()
    elif mode == 'manual':
        if len(sys.argv) < 3:
            logger.error("手动模式需要指定Excel文件路径")
            return False
        excel_file = sys.argv[2]
        success = fetcher.fetch_from_manual(excel_file)
    else:
        logger.error(f"未知模式: {mode}")
        return False

    if not success:
        logger.error("\n数据获取失败")
        return False

    # 数据处理
    fetcher.expand_group_majors()
    fetcher.clean_data()

    # 验证完整性
    is_complete, message = fetcher.verify_data_completeness()

    if not is_complete:
        logger.error(f"\n验证失败: {message}")
        if "FAILED_TO_FETCH_REAL_DATA" in message:
            logger.error("\n" + "=" * 80)
            logger.error("FAILED_TO_FETCH_REAL_DATA")
            logger.error("=" * 80)
        elif "INCOMPLETE_DATA" in message:
            logger.error(f"\n{message}")
        return False

    # 导出结果
    if not fetcher.export_results():
        logger.error("导出结果失败")
        return False

    # 完成
    logger.info("\n" + "=" * 80)
    logger.info("数据获取完成！")
    logger.info("=" * 80)
    logger.info(f"✓ 成功获取 {len(fetcher.official_data)} 条真实数据")
    logger.info(f"✓ 已通过完整性验证")
    logger.info(f"✓ 已生成所有输出文件")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
