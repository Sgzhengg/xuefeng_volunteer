"""
官方数据源采集器
从教育部官方渠道和公开数据源采集院校信息
"""

import asyncio
import aiohttp
import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import random

logger = logging.getLogger(__name__)


class OfficialDataSource:
    """官方数据源采集器"""

    def __init__(self, cache_dir: str = "data/cache"):
        self.base_url = "https://www.moe.gov.cn"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

        self.session = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=timeout
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()

    async def fetch_from_wikipedia(self) -> List[Dict[str, Any]]:
        """
        从维基百科获取中国院校列表
        维基百科有较完整的中国大学列表，且没有严格的反爬虫限制
        """
        universities = []

        try:
            # 维基百科中国大学列表页面
            urls = [
                "https://zh.wikipedia.org/wiki/中国高等院校列表",
                "https://zh.wikipedia.org/wiki/中华人民共和国高等学校列表"
            ]

            for url in urls:
                await asyncio.sleep(random.uniform(2, 4))

                logger.info(f"抓取: {url}")
                async with self.session.get(url) as response:
                    if response.status != 200:
                        logger.warning(f"请求失败: {response.status}")
                        continue

                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')

                    # 查找所有表格
                    tables = soup.find_all('table', {'class': 'wikitable'})

                    for table in tables:
                        rows = table.find_all('tr')

                        for row in rows[1:]:  # 跳过表头
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 2:
                                try:
                                    name = cells[0].get_text(strip=True)
                                    # 跳过空行和无关行
                                    if not name or '类别' in name or '注释' in name:
                                        continue

                                    uni_data = {
                                        "name": name,
                                        "province": self._extract_province(cells),
                                        "type": self._extract_type(cells),
                                        "level": self._extract_level(cells),
                                        "website": ""
                                    }

                                    universities.append(uni_data)

                                except Exception as e:
                                    logger.debug(f"解析行失败: {e}")
                                    continue

                    logger.info(f"从 {url} 获取到 {len(universities)} 所院校")

        except Exception as e:
            logger.error(f"从维基百科获取数据失败: {e}")

        logger.info(f"总共获取到 {len(universities)} 所院校")
        return universities

    def _extract_province(self, cells) -> str:
        """从单元格中提取省份"""
        # 尝试从第二个单元格提取省份
        if len(cells) > 1:
            text = cells[1].get_text(strip=True)
            # 移除括号内容
            text = text.split('（')[0].split('(')[0]
            return text if text else "未知"
        return "未知"

    def _extract_type(self, cells) -> str:
        """从单元格中提取院校类型"""
        type_keywords = {
            "综合": ["综合", "综合性"],
            "理工": ["理工", "工科", "理工科"],
            "师范": ["师范"],
            "医学": ["医学", "医药"],
            "农林": ["农林", "农业", "林业"],
            "财经": ["财经", "经济"],
            "政法": ["政法", "法律"],
            "艺术": ["艺术", "美术", "音乐"],
            "体育": ["体育"],
            "语言": ["语言", "外语"],
        }

        all_text = " ".join([cell.get_text() for cell in cells])

        for type_name, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in all_text:
                    return type_name

        return "其他"

    def _extract_level(self, cells) -> str:
        """从单元格中提取院校层次"""
        all_text = " ".join([cell.get_text() for cell in cells])

        if "985" in all_text:
            return "985"
        elif "211" in all_text:
            return "211"
        elif "双一流" in all_text or "一流大学" in all_text:
            return "双一流"
        elif "本科" in all_text:
            return "普通本科"
        else:
            return "高职专科"

    async def build_complete_database(self) -> Dict[str, Any]:
        """
        构建完整的院校数据库
        """
        logger.info("开始构建完整院校数据库...")

        universities = await self.fetch_from_wikipedia()

        # 添加ID
        for idx, uni in enumerate(universities, 1):
            uni["id"] = str(idx)

        result = {
            "universities": universities,
            "total": len(universities),
            "updated_at": datetime.now().isoformat(),
            "source": "wikipedia_official"
        }

        # 保存到数据库文件
        db_file = Path("data/universities_list.json")
        db_file.parent.mkdir(parents=True, exist_ok=True)

        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        logger.info(f"数据库已保存到 {db_file}")

        return result


async def main():
    """主函数"""
    logging.basicConfig(level=logging.INFO)

    async with OfficialDataSource() as source:
        result = await source.build_complete_database()

        print(f"\n构建完成!")
        print(f"总共: {result['total']} 所院校")
        print(f"数据已保存到: data/universities_list.json")


if __name__ == "__main__":
    asyncio.run(main())
