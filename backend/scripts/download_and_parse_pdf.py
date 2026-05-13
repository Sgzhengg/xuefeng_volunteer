#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从广东省教育考试院下载并解析2025年投档线PDF文档
"""

import requests
import io
from pathlib import Path
import logging
import re
from datetime import datetime

# 尝试导入PDF解析库
try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    print("警告: 未安装PyPDF2，将尝试其他方法")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'pdf_download_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PDFDownloader:
    """PDF下载器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # 官方PDF链接
        self.pdf_urls = {
            '物理': 'https://eea.gd.gov.cn/attachment/0/585/585886/4746781.pdf',
            '历史': 'https://eea.gd.gov.cn/attachment/0/585/585885/4746781.pdf'
        }

    def download_pdfs(self):
        """下载所有PDF文件"""
        logger.info("=" * 80)
        logger.info("开始下载2025年广东高考投档线官方PDF文档")
        logger.info("=" * 80)

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        downloaded_files = {}

        for category, url in self.pdf_urls.items():
            logger.info(f"\n下载{category}类投档PDF...")
            logger.info(f"URL: {url}")

            try:
                response = self.session.get(url, timeout=60)
                if response.status_code == 200:
                    # 保存文件
                    filename = output_dir / f"广东省2025年本科普通类({category})投档情况.pdf"
                    with open(filename, 'wb') as f:
                        f.write(response.content)

                    downloaded_files[category] = filename
                    logger.info(f"✓ 下载成功: {filename}")
                    logger.info(f"  文件大小: {len(response.content)} 字节")
                else:
                    logger.error(f"下载失败，状态码: {response.status_code}")

            except Exception as e:
                logger.error(f"下载{category}类PDF失败: {e}")

        logger.info(f"\n成功下载 {len(downloaded_files)} 个PDF文件")
        return downloaded_files

    def parse_pdf_text(self, pdf_file: Path) -> list:
        """解析PDF文件中的文本数据"""
        logger.info(f"\n解析PDF文件: {pdf_file}")

        if not HAS_PDF:
            logger.error("未安装PyPDF2库，无法解析PDF")
            logger.info("请运行: pip install PyPDF2")
            return []

        try:
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                logger.info(f"PDF页数: {len(pdf_reader.pages)}")

                all_text = []
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        text = page.extract_text()
                        all_text.append(text)
                        logger.info(f"  页面{page_num}: 提取到 {len(text)} 字符")
                    except Exception as e:
                        logger.warning(f"  页面{page_num}提取失败: {e}")

                full_text = "\n".join(all_text)
                logger.info(f"总共提取到 {len(full_text)} 字符")

                # 尝试解析投档数据
                records = self._extract_admission_data(full_text)
                return records

        except Exception as e:
            logger.error(f"解析PDF失败: {e}")
            return []

    def _extract_admission_data(self, text: str) -> list:
        """从PDF文本中提取投档数据"""
        logger.info("尝试从PDF文本中提取投档数据...")

        records = []

        # 按行分割文本
        lines = text.split('\n')

        # 查找数据开始位置
        data_start = False
        for i, line in enumerate(lines):
            # 跳过空行
            if not line.strip():
                continue

            # 查找表头
            if '院校' in line and ('代码' in line or '名称' in line):
                logger.info(f"找到表头: {line}")
                data_start = True
                continue

            # 开始提取数据
            if data_start:
                # 尝试解析数据行
                record = self._parse_data_line(line)
                if record:
                    records.append(record)

        logger.info(f"从PDF文本中提取到 {len(records)} 条记录")
        return records

    def _parse_data_line(self, line: str) -> dict:
        """解析单行数据"""
        # 移除多余空格
        line = re.sub(r'\s+', ' ', line.strip())

        # 尝试匹配模式：院校代码 院校名称 专业组 最低分 最低排位
        # 例如：10561 华南理工大学 202 625 8500

        # 使用正则表达式提取数字和文本
        parts = line.split()

        if len(parts) >= 4:
            try:
                # 查找院校代码（通常是5位数字）
                university_code = None
                for i, part in enumerate(parts):
                    if re.match(r'^\d{5}$', part):
                        university_code = part
                        remaining_parts = parts[i+1:]
                        break

                if not university_code:
                    return None

                # 提取其他信息
                if len(remaining_parts) >= 3:
                    # 尝试解析分数和排位
                    min_score = None
                    min_rank = None
                    group_code = None

                    for j, part in enumerate(remaining_parts):
                        if re.match(r'^\d{3}$', part):  # 专业组代码（3位数字）
                            group_code = part
                        elif re.match(r'^\d{3}$', part) and int(part) > 100:  # 分数（3位数，通常>100）
                            min_score = int(part)
                        elif re.match(r'^\d{4,6}$', part):  # 排位（4-6位数字）
                            min_rank = int(part)

                    # 如果没有找到专业组代码，尝试其他方法
                    if not group_code and len(remaining_parts) >= 1:
                        group_code = remaining_parts[0]

                    # 提取院校名称（在代码和数字之间的部分）
                    university_name_parts = []
                    for part in remaining_parts:
                        if not re.match(r'^\d+$', part):
                            university_name_parts.append(part)
                        else:
                            break

                    university_name = ' '.join(university_name_parts) if university_name_parts else "未知"

                    if min_score and min_rank and group_code:
                        return {
                            'university_code': university_code,
                            'university': university_name,
                            'group_code': group_code,
                            'min_score': min_score,
                            'min_rank': min_rank,
                            'source': '广东省教育考试院PDF'
                        }

            except Exception as e:
                logger.debug(f"解析行失败: {line}, 错误: {e}")

        return None


def main():
    """主函数"""
    logger.info("2025年广东高考投档线PDF下载和解析系统")

    downloader = PDFDownloader()

    # 下载PDF文件
    pdf_files = downloader.download_pdfs()

    if not pdf_files:
        logger.error("没有成功下载任何PDF文件")
        return False

    # 解析PDF文件
    all_records = []
    for category, pdf_file in pdf_files.items():
        logger.info(f"\n解析{category}类投档PDF...")
        records = downloader.parse_pdf_text(pdf_file)
        if records:
            # 添加科类信息
            for record in records:
                record['category'] = category
            all_records.extend(records)

    logger.info(f"\n总共提取到 {len(all_records)} 条记录")

    if len(all_records) >= 3000:
        logger.info("✓ 数据量满足要求（≥3000条）")

        # 保存数据
        import pandas as pd
        output_file = Path("output") / f"guangdong_2025_admission_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df = pd.DataFrame(all_records)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"✓ 数据已保存: {output_file}")
        return True
    else:
        logger.warning(f"⚠ 数据量不足: {len(all_records)}/3000")
        logger.info("可能需要更精确的PDF解析方法")
        return False


if __name__ == "__main__":
    main()
