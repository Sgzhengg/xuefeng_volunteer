#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2025广东高考本科批次投档线采集系统

数据来源：
1. 高考直通车 (https://www.gaokao.cn/)
2. 掌上高考 (https://www.gaokaopai.com/)
3. 中国教育在线 (https://www.eol.cn/)
4. 广东省教育考试院 (https://eea.gd.gov.cn/)

技术要求：
- 优先使用官方JSON接口
- 禁止使用模拟数据
- 必须进行数据真实性校验
- 输出CSV和Excel格式
"""

import asyncio
import aiohttp
import json
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Set
from bs4 import BeautifulSoup
import re
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'guangdong_2025_scrape_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AdmissionRecord:
    """投档记录数据结构"""

    def __init__(self, university: str, category: str, group_code: str,
                 min_score: int, min_rank: int, source: str):
        self.university = university  # 院校名称
        self.category = category  # 科类（物理/历史）
        self.group_code = group_code  # 专业组代码
        self.min_score = min_score  # 最低分
        self.min_rank = min_rank  # 最低排位
        self.source = source  # 数据来源
        self.scrape_time = datetime.now().isoformat()  # 抓取时间
        self.verified = False  # 是否已验证

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'university': self.university,
            'category': self.category,
            'group_code': self.group_code,
            'min_score': self.min_score,
            'min_rank': self.min_rank,
            'source': self.source,
            'scrape_time': self.scrape_time,
            'verified': self.verified
        }

    def __str__(self):
        return f"{self.university} {self.category} {self.group_code} {self.min_score}分 {self.min_rank}位"


class DataValidator:
    """数据验证器"""

    def __init__(self):
        self.discrepancy_records = []

    def validate_records(self, records: List[AdmissionRecord]) -> Dict:
        """
        验证记录的真实性

        如果同一学校的同一专业组在多个来源中数据一致，标记为verified=True
        如果数据不一致，记录到discrepancy_records
        """
        logger.info(f"开始验证 {len(records)} 条记录...")

        # 按学校+专业组+科类分组
        grouped = {}
        for record in records:
            key = f"{record.university}_{record.group_code}_{record.category}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(record)

        verified_count = 0
        discrepancy_count = 0

        for key, group_records in grouped.items():
            if len(group_records) == 1:
                # 只有一个来源的数据，暂时标记为未验证
                group_records[0].verified = False
            else:
                # 检查多个来源的数据是否一致
                scores = set(r.min_score for r in group_records)
                ranks = set(r.min_rank for r in group_records)

                if len(scores) == 1 and len(ranks) == 1:
                    # 多个来源一致，标记为已验证
                    for record in group_records:
                        record.verified = True
                    verified_count += 1
                else:
                    # 数据不一致
                    discrepancy_count += 1
                    self.discrepancy_records.append({
                        'key': key,
                        'records': [r.to_dict() for r in group_records]
                    })
                    logger.warning(f"发现数据不一致: {key}")
                    for r in group_records:
                        logger.warning(f"  {r.source}: {r.min_score}分 {r.min_rank}位")

        logger.info(f"验证完成: {verified_count} 条已验证, {discrepancy_count} 条不一致")

        return {
            'total': len(records),
            'verified': verified_count,
            'discrepancy': discrepancy_count,
            'unverified': len(records) - verified_count
        }


class BaseScraper:
    """爬虫基类"""

    def __init__(self):
        self.session = None
        self.records = []

    async def create_session(self):
        """创建aiohttp会话"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = aiohttp.ClientSession(headers=headers)

    async def close_session(self):
        """关闭会话"""
        if self.session:
            await self.session.close()

    async def fetch(self, url: str) -> Optional[str]:
        """获取页面内容"""
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.error(f"请求失败: {url}, 状态码: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"请求异常: {url}, 错误: {e}")
            return None

    async def fetch_json(self, url: str) -> Optional[dict]:
        """获取JSON数据"""
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"JSON请求失败: {url}, 状态码: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"JSON请求异常: {url}, 错误: {e}")
            return None

    def parse_records(self) -> List[AdmissionRecord]:
        """解析记录，子类实现"""
        raise NotImplementedError


class GaokaoCNScraper(BaseScraper):
    """高考直通车爬虫"""

    async def scrape(self, category: str = "物理") -> List[AdmissionRecord]:
        """
        采集高考直通车数据

        Args:
            category: 科类（物理/历史）
        """
        logger.info(f"开始采集高考直通车 {category} 类数据...")

        # 首先尝试找JSON接口
        records = await self._try_json_api(category)

        if not records:
            # 如果没有找到JSON接口，解析HTML
            records = await self._parse_html(category)

        logger.info(f"高考直通车 {category} 类采集完成，获得 {len(records)} 条记录")
        return records

    async def _try_json_api(self, category: str) -> List[AdmissionRecord]:
        """尝试获取JSON接口数据"""
        # TODO: 需要实际分析高考直通车的接口
        # 这里提供示例URL模式
        possible_apis = [
            "https://api.gaokao.cn/admission/guangdong/2025/undergraduate",
            "https://www.gaokao.cn/api/college/query",
        ]

        for api_url in possible_apis:
            logger.info(f"尝试API: {api_url}")
            data = await self.fetch_json(api_url)
            if data:
                logger.info(f"找到API数据源: {api_url}")
                return self._parse_json_response(data, category)

        return []

    def _parse_json_response(self, data: dict, category: str) -> List[AdmissionRecord]:
        """解析JSON响应"""
        records = []
        # TODO: 根据实际API响应格式解析
        # 这里需要根据实际API返回的数据结构来编写
        return records

    async def _parse_html(self, category: str) -> List[AdmissionRecord]:
        """解析HTML页面"""
        url = f"https://www.gaokao.cn/colleges/province/guangdong?category={category}&year=2025"
        html = await self.fetch(url)

        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        records = []

        # TODO: 根据实际HTML结构解析
        # 需要查看页面结构后实现

        return records


class GaokaopaiScraper(BaseScraper):
    """掌上高考爬虫"""

    async def scrape(self, category: str = "物理") -> List[AdmissionRecord]:
        """采集掌上高考数据"""
        logger.info(f"开始采集掌上高考 {category} 类数据...")

        # 优先尝试JSON接口
        records = await self._try_json_api(category)

        if not records:
            records = await self._parse_html(category)

        logger.info(f"掌上高考 {category} 类采集完成，获得 {len(records)} 条记录")
        return records

    async def _try_json_api(self, category: str) -> List[AdmissionRecord]:
        """尝试获取JSON接口数据"""
        # 掌上高考可能的API端点
        possible_apis = [
            "https://www.gaokaopai.com/api/admission",
            "https://api.gaokaopai.com/batch/query",
        ]

        for api_url in possible_apis:
            logger.info(f"尝试API: {api_url}")
            data = await self.fetch_json(api_url)
            if data:
                logger.info(f"找到API数据源: {api_url}")
                return self._parse_json_response(data, category)

        return []

    def _parse_json_response(self, data: dict, category: str) -> List[AdmissionRecord]:
        """解析JSON响应"""
        records = []
        # TODO: 根据实际API响应格式解析
        return records

    async def _parse_html(self, category: str) -> List[AdmissionRecord]:
        """解析HTML页面"""
        url = f"https://www.gaokaopai.com/guangdong-{category}-2025.html"
        html = await self.fetch(url)

        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        records = []

        # TODO: 根据实际HTML结构解析

        return records


class EOLScraper(BaseScraper):
    """中国教育在线爬虫"""

    async def scrape(self, category: str = "物理") -> List[AdmissionRecord]:
        """采集中国教育在线数据"""
        logger.info(f"开始采集中国教育在线 {category} 类数据...")

        records = await self._try_json_api(category)

        if not records:
            records = await self._parse_html(category)

        logger.info(f"中国教育在线 {category} 类采集完成，获得 {len(records)} 条记录")
        return records

    async def _try_json_api(self, category: str) -> List[AdmissionRecord]:
        """尝试获取JSON接口数据"""
        possible_apis = [
            "https://www.eol.cn/api/guangdong/2025/score",
        ]

        for api_url in possible_apis:
            logger.info(f"尝试API: {api_url}")
            data = await self.fetch_json(api_url)
            if data:
                logger.info(f"找到API数据源: {api_url}")
                return self._parse_json_response(data, category)

        return []

    def _parse_json_response(self, data: dict, category: str) -> List[AdmissionRecord]:
        """解析JSON响应"""
        records = []
        # TODO: 根据实际API响应格式解析
        return records

    async def _parse_html(self, category: str) -> List[AdmissionRecord]:
        """解析HTML页面"""
        url = f"https://www.eol.cn/guangdong/2025/{category}/"
        html = await self.fetch(url)

        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        records = []

        # TODO: 根据实际HTML结构解析

        return records


class OfficialScraper(BaseScraper):
    """官方数据爬虫 - 广东省教育考试院"""

    async def scrape(self) -> List[AdmissionRecord]:
        """采集广东省教育考试院官方数据"""
        logger.info("开始采集广东省教育考试院官方数据...")

        records = []

        # 1. 首先访问官网，查找2025年投档线公告
        url = "https://eea.gd.gov.cn/"
        html = await self.fetch(url)

        if html:
            # 查找投档线相关链接
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', href=True)

            for link in links:
                href = link['href']
                text = link.get_text()

                # 查找包含"2025"、"投档"、"本科"等关键词的链接
                if '2025' in text and ('投档' in text or '本科' in text):
                    logger.info(f"找到相关链接: {text} - {href}")

                    # 如果是Excel文件，下载并解析
                    if href.endswith(('.xls', '.xlsx')):
                        excel_records = await self._parse_excel(href)
                        records.extend(excel_records)

        logger.info(f"官方数据采集完成，获得 {len(records)} 条记录")
        return records

    async def _parse_excel(self, url: str) -> List[AdmissionRecord]:
        """解析Excel文件"""
        logger.info(f"解析Excel文件: {url}")

        # 下载Excel文件
        data = await self.session.get(url)
        if data.status == 200:
            content = await data.read()

            # 使用pandas读取Excel
            try:
                df = pd.read_excel(content)
                records = []

                for _, row in df.iterrows():
                    # TODO: 根据实际Excel列名解析
                    record = self._parse_excel_row(row)
                    if record:
                        records.append(record)

                return records
            except Exception as e:
                logger.error(f"解析Excel失败: {e}")

        return []

    def _parse_excel_row(self, row) -> Optional[AdmissionRecord]:
        """解析Excel行"""
        # TODO: 根据实际Excel格式实现
        return None


class Guangdong2025AdmissionSystem:
    """2025广东高考本科批次投档线采集系统主类"""

    def __init__(self):
        self.scrapers = {
            'gaokao_cn': GaokaoCNScraper(),
            'gaokaopai': GaokaopaiScraper(),
            'eol': EOLScraper(),
            'official': OfficialScraper()
        }
        self.validator = DataValidator()
        self.all_records = []

    async def scrape_all(self, categories: List[str] = None):
        """
        采集所有数据源

        Args:
            categories: 科类列表，默认为["物理", "历史"]
        """
        if categories is None:
            categories = ["物理", "历史"]

        logger.info("=" * 80)
        logger.info("开始采集2025年广东高考本科批次投档线")
        logger.info("=" * 80)

        # 为每个爬虫创建会话
        for scraper in self.scrapers.values():
            await scraper.create_session()

        try:
            # 采集各个数据源
            for category in categories:
                logger.info(f"\n采集 {category} 类数据...")

                for source_name, scraper in self.scrapers.items():
                    try:
                        records = await scraper.scrape(category)
                        self.all_records.extend(records)
                    except Exception as e:
                        logger.error(f"{source_name} 采集失败: {e}")

        finally:
            # 关闭所有会话
            for scraper in self.scrapers.values():
                await scraper.close_session()

        logger.info(f"\n采集完成，共获得 {len(self.all_records)} 条记录")

    def deduplicate_records(self) -> List[AdmissionRecord]:
        """
        数据去重

        优先级：官方 > 高考直通车 > 掌上高考 > 中国教育在线
        """
        logger.info("开始数据去重...")

        # 按学校+专业组+科类分组
        grouped = {}
        for record in self.all_records:
            key = f"{record.university}_{record.group_code}_{record.category}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(record)

        # 去重，按优先级保留
        source_priority = {
            'official': 1,
            'gaokao_cn': 2,
            'gaokaopai': 3,
            'eol': 4
        }

        unique_records = []
        for key, records in grouped.items():
            # 按优先级排序
            records.sort(key=lambda r: source_priority.get(r.source, 999))
            unique_records.append(records[0])

        logger.info(f"去重完成，保留 {len(unique_records)} 条唯一记录")
        return unique_records

    def export_to_csv(self, records: List[AdmissionRecord], filename: str):
        """导出为CSV格式"""
        logger.info(f"导出CSV文件: {filename}")

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        filepath = output_dir / filename

        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['院校名称', '科类', '专业组代码', '最低分', '最低排位', '数据来源', '抓取时间', '验证状态'])

            for record in records:
                writer.writerow([
                    record.university,
                    record.category,
                    record.group_code,
                    record.min_score,
                    record.min_rank,
                    record.source,
                    record.scrape_time,
                    '已验证' if record.verified else '未验证'
                ])

        logger.info(f"CSV导出完成: {filepath}")

    def export_to_excel(self, records: List[AdmissionRecord], filename: str):
        """导出为Excel格式"""
        logger.info(f"导出Excel文件: {filename}")

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        filepath = output_dir / filename

        # 转换为DataFrame
        data = []
        for record in records:
            data.append({
                '院校名称': record.university,
                '科类': record.category,
                '专业组代码': record.group_code,
                '最低分': record.min_score,
                '最低排位': record.min_rank,
                '数据来源': record.source,
                '抓取时间': record.scrape_time,
                '验证状态': '已验证' if record.verified else '未验证'
            })

        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False, engine='openpyxl')

        logger.info(f"Excel导出完成: {filepath}")

    def export_discrepancy_report(self, filename: str):
        """导出数据不一致报告"""
        if not self.validator.discrepancy_records:
            logger.info("没有数据不一致记录")
            return

        logger.info(f"导出数据不一致报告: {filename}")

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        filepath = output_dir / filename

        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['学校', '专业组', '来源A', '分数A', '排位A', '来源B', '分数B', '排位B'])

            for item in self.validator.discrepancy_records:
                records = item['records']
                if len(records) >= 2:
                    writer.writerow([
                        records[0]['university'],
                        records[0]['group_code'],
                        records[0]['source'],
                        records[0]['min_score'],
                        records[0]['min_rank'],
                        records[1]['source'],
                        records[1]['min_score'],
                        records[1]['min_rank']
                    ])

        logger.info(f"不一致报告导出完成: {filepath}")

    def generate_summary_report(self) -> str:
        """生成汇总报告"""
        report = []
        report.append("=" * 80)
        report.append("2025年广东高考本科批次投档线采集汇总报告")
        report.append("=" * 80)
        report.append(f"采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"总记录数: {len(self.all_records)}")

        # 按来源统计
        source_stats = {}
        for record in self.all_records:
            source = record.source
            if source not in source_stats:
                source_stats[source] = 0
            source_stats[source] += 1

        report.append("\n按数据源统计:")
        for source, count in source_stats.items():
            report.append(f"  {source}: {count} 条")

        # 按科类统计
        category_stats = {}
        for record in self.all_records:
            category = record.category
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += 1

        report.append("\n按科类统计:")
        for category, count in category_stats.items():
            report.append(f"  {category}: {count} 条")

        report.append("=" * 80)

        return "\n".join(report)


async def main():
    """主函数"""
    # 创建采集系统
    system = Guangdong2025AdmissionSystem()

    # 采集所有数据
    await system.scrape_all()

    # 数据去重
    unique_records = system.deduplicate_records()

    # 数据验证
    validation_result = system.validator.validate_records(system.all_records)

    # 导出结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    system.export_to_csv(unique_records, f"guangdong_2025_admission_{timestamp}.csv")
    system.export_to_excel(unique_records, f"guangdong_2025_admission_{timestamp}.xlsx")
    system.export_discrepancy_report(f"discrepancy_report_{timestamp}.csv")

    # 生成汇总报告
    summary = system.generate_summary_report()
    print(summary)

    # 保存汇总报告
    report_file = f"output/summary_report_{timestamp}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(summary)

    logger.info(f"汇总报告已保存: {report_file}")

    logger.info("\n所有任务完成！")
    logger.info(f"请查看 output/ 目录下的结果文件")


if __name__ == "__main__":
    asyncio.run(main())
