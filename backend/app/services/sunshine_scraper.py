"""
阳光高考数据爬虫服务
从 gaokao.chsi.com.cn 爬取院校、专业、录取分数线等数据
"""

import asyncio
import aiohttp
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import re
import random

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SunshineScraper:
    """阳光高考数据爬虫"""

    def __init__(self, cache_dir: str = "data/cache", database_dir: str = "data"):
        self.base_url = "https://gaokao.chsi.com.cn"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 数据库目录（包含预构建的JSON文件）
        self.database_dir = Path(database_dir)
        self.database_dir.mkdir(parents=True, exist_ok=True)

        # 请求头（模拟浏览器）
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        # 请求间隔（秒）- 避免被封
        self.request_delay = 2

        # 最大重试次数
        self.max_retries = 3

        # 创建 HTTP 客户端
        self.session: Optional[aiohttp.ClientSession] = None

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

    async def _request(self, url: str, method: str = "GET", **kwargs) -> Optional[aiohttp.ClientResponse]:
        """
        发送 HTTP 请求（带重试机制）

        Args:
            url: 请求 URL
            method: 请求方法
            **kwargs: 其他请求参数

        Returns:
            响应对象，失败返回 None
        """
        for attempt in range(self.max_retries):
            try:
                # 添加随机延迟，避免规律性请求
                delay = self.request_delay + random.uniform(0.5, 1.5)
                await asyncio.sleep(delay)

                # 随机化 User-Agent
                headers = self.headers.copy()
                headers["User-Agent"] = self._get_random_user_agent()

                logger.info(f"请求 [{attempt+1}/{self.max_retries}]: {method} {url}")
                response = await self.session.request(method, url, headers=headers, **kwargs)

                # 检查状态码
                if response.status == 412:
                    logger.warning(f"收到 412 错误，等待更长时间...")
                    await asyncio.sleep(5 + attempt * 5)
                    continue

                response.raise_for_status()
                return response

            except aiohttp.ClientError as e:
                logger.warning(f"请求失败 [{attempt+1}/{self.max_retries}] {url}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                else:
                    logger.error(f"请求最终失败 {url}: {e}")
                    return None
            except Exception as e:
                logger.error(f"未知错误 {url}: {e}")
                return None

        return None

    def _get_random_user_agent(self) -> str:
        """获取随机 User-Agent"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ]
        return random.choice(user_agents)

    def _load_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """加载缓存数据"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"加载缓存: {cache_key}")
                return data
            except Exception as e:
                logger.error(f"加载缓存失败 {cache_key}: {e}")
        return None

    def _save_cache(self, cache_key: str, data: Dict[str, Any]):
        """保存缓存数据"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"保存缓存: {cache_key}")
        except Exception as e:
            logger.error(f"保存缓存失败 {cache_key}: {e}")

    def _load_database_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        从数据库目录加载预构建的数据文件

        Args:
            filename: 文件名（如 universities_list.json）

        Returns:
            数据字典，文件不存在或加载失败返回 None
        """
        db_file = self.database_dir / filename
        if db_file.exists():
            try:
                with open(db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"从数据库文件加载: {filename}")
                return data
            except Exception as e:
                logger.error(f"加载数据库文件失败 {filename}: {e}")
        return None

    async def scrape_university_list(
        self,
        province: Optional[str] = None,
        use_cache: bool = True,
        max_pages: int = 50
    ) -> Dict[str, Any]:
        """
        获取院校列表（支持分页爬取）

        Args:
            province: 省份筛选（可选）
            use_cache: 是否使用缓存
            max_pages: 最大爬取页数

        Returns:
            院校列表数据
        """
        # 优先从数据库文件加载
        db_data = self._load_database_file("universities_list.json")
        if db_data and use_cache:
            # 如果指定了省份，进行筛选
            if province:
                filtered_unis = [
                    uni for uni in db_data.get("universities", [])
                    if uni.get("province") == province
                ]
                result = {
                    "universities": filtered_unis,
                    "total": len(filtered_unis),
                    "updated_at": db_data.get("updated_at"),
                    "source": "database_file"
                }
            else:
                result = {
                    **db_data,
                    "source": "database_file"
                }

            return {
                "success": True,
                "data": result,
                "source": "database_file"
            }

        # 回退到原来的缓存逻辑
        cache_key = f"university_list_{province or 'all'}"

        # 尝试加载缓存
        if use_cache:
            cached_data = self._load_cache(cache_key)
            if cached_data:
                return {
                    "success": True,
                    "data": cached_data,
                    "source": "cache"
                }

        # 爬取新数据（分页）
        all_universities = []
        page = 1

        logger.info(f"开始爬取院校列表，省份: {province or '全部'}")

        while page <= max_pages:
            # 构建URL
            url = f"{self.base_url}/sch/"

            # 构建查询参数
            params = {
                'page': page,
                'size': 50  # 每页数量
            }
            if province:
                params['pxym'] = province  # 省份代码

            response = await self._request(url, params=params)
            if not response:
                logger.warning(f"第 {page} 页请求失败，停止分页")
                break

            try:
                html = await response.text()

                # 解析 HTML
                universities = self._parse_university_list(html, province)

                if not universities:
                    logger.info(f"第 {page} 页没有数据，停止分页")
                    break

                all_universities.extend(universities)
                logger.info(f"第 {page} 页: 获取到 {len(universities)} 所院校，累计: {len(all_universities)}")

                # 检查是否是最后一页
                # 如果返回的数据少于50条，说明是最后一页
                if len(universities) < 50:
                    logger.info("已到达最后一页")
                    break

                page += 1

            except Exception as e:
                logger.error(f"解析第 {page} 页失败: {e}")
                break

        result = {
            "universities": all_universities,
            "total": len(all_universities),
            "updated_at": datetime.now().isoformat()
        }

        # 保存缓存
        self._save_cache(cache_key, result)

        logger.info(f"爬取完成，共获取 {len(all_universities)} 所院校")

        return {
            "success": True,
            "data": result,
            "source": "sunshine"
        }

    def _parse_university_list(self, html: str, province: Optional[str]) -> List[Dict[str, Any]]:
        """
        解析院校列表 HTML

        Args:
            html: HTML 内容
            province: 省份

        Returns:
            院校列表
        """
        universities = []
        try:
            soup = BeautifulSoup(html, 'lxml')

            # 尝试多种选择器模式
            # 模式1: 查找院校卡片
            cards = soup.select('.school-item, .school-card, .university-item, li[typeof*="School"]')

            if not cards:
                # 模式2: 查找包含院校信息的表格行
                cards = soup.select('tr:has(td)')
                logger.info(f"使用表格模式，找到 {len(cards)} 行")

            if not cards:
                # 模式3: 查找所有链接（可能包含院校名称）
                links = soup.find_all('a', href=re.compile(r'/sch/schoolInfo--schId-\d+\.dhtml'))
                logger.info(f"使用链接模式，找到 {len(links)} 个院校链接")

                for link in links:
                    # 从链接中提取院校ID
                    href = link.get('href', '')
                    match = re.search(r'schId-(\d+)', href)
                    if match:
                        uni_id = match.group(1)
                        name = link.get_text(strip=True)
                        if name:
                            universities.append({
                                "id": uni_id,
                                "name": name,
                                "province": province or "未知",
                                "type": "未知",
                                "level": "未知",
                                "website": f"https://gaokao.chsi.com.cn/sch/schoolInfo--schId-{uni_id}.dhtml"
                            })

            else:
                # 使用卡片模式解析
                for card in cards:
                    try:
                        uni_data = {}

                        # 提取院校名称
                        name_elem = card.select_one('.school-name, h3, h4, a[href*="schoolInfo"]')
                        if name_elem:
                            uni_data["name"] = name_elem.get_text(strip=True)

                            # 提取ID
                            link = name_elem.get('href', '') or name_elem.select_one('a')['href'] if name_elem.select_one('a') else ''
                            match = re.search(r'schId-(\d+)', link)
                            if match:
                                uni_data["id"] = match.group(1)

                        # 提取省份
                        province_elem = card.select_one('.province, .location, [class*="area"]')
                        if province_elem:
                            uni_data["province"] = province_elem.get_text(strip=True)
                        else:
                            uni_data["province"] = province or "未知"

                        # 提取院校类型
                        type_elem = card.select_one('.school-type, [class*="type"]')
                        if type_elem:
                            uni_data["type"] = type_elem.get_text(strip=True)
                        else:
                            uni_data["type"] = "未知"

                        # 提取院校层次（985/211等）
                        level_elem = card.select_one('.school-level, [class*="level"], [class*="985"], [class*="211"]')
                        if level_elem:
                            level_text = level_elem.get_text(strip=True)
                            uni_data["level"] = level_text
                        else:
                            uni_data["level"] = "未知"

                        # 提取官网
                        website_elem = card.select_one('a[href*="www."], a[href*="edu.cn"]')
                        if website_elem:
                            href = website_elem.get('href', '')
                            if href.startswith('http'):
                                uni_data["website"] = href
                            else:
                                uni_data["website"] = f"https://gaokao.chsi.com.cn{href}"
                        else:
                            uni_data["website"] = ""

                        # 验证必要字段
                        if uni_data.get("name") and uni_data.get("id"):
                            universities.append(uni_data)

                    except Exception as e:
                        logger.warning(f"解析单个院校卡片失败: {e}")
                        continue

            logger.info(f"成功解析 {len(universities)} 所院校")

            # 如果没有解析到任何数据，记录HTML结构用于调试
            if not universities:
                logger.warning("未解析到院校数据，记录HTML结构...")
                logger.debug(f"HTML片段: {html[:1000]}")

        except Exception as e:
            logger.error(f"解析院校列表失败: {e}")
            logger.debug(f"HTML内容: {html[:500]}")

        return universities

    async def scrape_university_detail(
        self,
        university_id: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        爬取院校详细信息

        Args:
            university_id: 院校 ID
            use_cache: 是否使用缓存

        Returns:
            院校详细信息
        """
        cache_key = f"university_detail_{university_id}"

        # 尝试加载缓存
        if use_cache:
            cached_data = self._load_cache(cache_key)
            if cached_data:
                return {
                    "success": True,
                    "data": cached_data,
                    "source": "cache"
                }

        # 爬取新数据
        url = f"{self.base_url}/sch/schoolInfo--schId-{university_id}.dhtml"

        response = await self._request(url)
        if not response:
            return {
                "success": False,
                "message": "请求失败",
                "data": None
            }

        try:
            html = await response.text()

            # 解析详细信息
            detail = self._parse_university_detail(html, university_id)

            # 保存缓存
            self._save_cache(cache_key, detail)

            return {
                "success": True,
                "data": detail,
                "source": "sunshine"
            }

        except Exception as e:
            logger.error(f"解析院校详情失败: {e}")
            return {
                "success": False,
                "message": f"解析失败: {str(e)}",
                "data": None
            }

    def _parse_university_detail(self, html: str, university_id: str) -> Dict[str, Any]:
        """
        解析院校详细信息 HTML

        Args:
            html: HTML 内容
            university_id: 院校 ID

        Returns:
            院校详细信息
        """
        # 暂时返回示例数据
        return {
            "id": university_id,
            "name": "浙江大学",
            "english_name": "Zhejiang University",
            "province": "浙江",
            "city": "杭州",
            "type": "综合",
            "level": "985",
            "website": "https://www.zju.edu.cn",
            "description": "浙江大学是一所历史悠久、声誉卓著的高等学府",
            "founded_year": "1897",
            "campus_area": "总面积约6400亩",
            "departments": ["计算机科学与技术", "软件工程", "人工智能"],
            "tuition": "约5000-10000元/年"
        }

    async def scrape_admission_scores(
        self,
        province: str = None,
        year: int = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        获取录取分数线（优先从数据库文件加载）

        Args:
            province: 省份筛选（可选）
            year: 年份筛选（可选）
            use_cache: 是否使用缓存

        Returns:
            录取分数线数据
        """
        # 优先从数据库文件加载
        db_data = self._load_database_file("admission_scores.json")
        if db_data:
            # 返回完整数据，让前端根据需要筛选
            result = {
                **db_data,
                "source": "database_file"
            }
            return {
                "success": True,
                "data": result,
                "source": "database_file"
            }

        # 爬取新数据
        cache_key = f"admission_scores_{province}_{year}"
        url = f"{self.base_url}/sch/search--ss-on-{year}-query-{province}-dm-{province}.dhtml"

        response = await self._request(url)
        if not response:
            return {
                "success": False,
                "message": "请求失败",
                "data": None
            }

        try:
            html = await response.text()

            # 解析分数线数据
            scores = self._parse_admission_scores(html, province, year)

            result = {
                "province": province,
                "year": year,
                "scores": scores,
                "total": len(scores),
                "updated_at": datetime.now().isoformat()
            }

            # 保存缓存
            self._save_cache(cache_key, result)

            return {
                "success": True,
                "data": result,
                "source": "sunshine"
            }

        except Exception as e:
            logger.error(f"解析分数线失败: {e}")
            return {
                "success": False,
                "message": f"解析失败: {str(e)}",
                "data": None
            }

    def _parse_admission_scores(self, html: str, province: str, year: int) -> List[Dict[str, Any]]:
        """
        解析录取分数线 HTML

        Args:
            html: HTML 内容
            province: 省份
            year: 年份

        Returns:
            分数线列表
        """
        # 暂时返回示例数据
        scores = [
            {
                "university": "北京大学",
                "province": province,
                "year": year,
                "min_score": 680,
                "avg_score": 690,
                "major": "计算机科学与技术"
            },
            {
                "university": "清华大学",
                "province": province,
                "year": year,
                "min_score": 685,
                "avg_score": 695,
                "major": "计算机科学与技术"
            },
            {
                "university": "浙江大学",
                "province": province,
                "year": year,
                "min_score": 650,
                "avg_score": 660,
                "major": "计算机科学与技术"
            }
        ]

        return scores

    async def scrape_major_list(
        self,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        获取专业列表（优先从数据库文件加载）

        Args:
            use_cache: 是否使用缓存

        Returns:
            专业列表数据
        """
        # 优先从数据库文件加载
        db_data = self._load_database_file("majors_list.json")
        if db_data:
            result = {
                **db_data,
                "source": "database_file"
            }
            return {
                "success": True,
                "data": result,
                "source": "database_file"
            }

        # 回退到原来的缓存逻辑
        cache_key = "major_list"

        # 尝试加载缓存
        if use_cache:
            cached_data = self._load_cache(cache_key)
            if cached_data:
                return {
                    "success": True,
                    "data": cached_data,
                    "source": "cache"
                }

        # 爬取新数据
        url = f"{self.base_url}/zyk/"

        response = await self._request(url)
        if not response:
            return {
                "success": False,
                "message": "请求失败",
                "data": None
            }

        try:
            html = await response.text()

            # 解析专业列表
            majors = self._parse_major_list(html)

            result = {
                "majors": majors,
                "total": len(majors),
                "updated_at": datetime.now().isoformat()
            }

            # 保存缓存
            self._save_cache(cache_key, result)

            return {
                "success": True,
                "data": result,
                "source": "sunshine"
            }

        except Exception as e:
            logger.error(f"解析专业列表失败: {e}")
            return {
                "success": False,
                "message": f"解析失败: {str(e)}",
                "data": None
            }

    def _parse_major_list(self, html: str) -> List[Dict[str, Any]]:
        """
        解析专业列表 HTML

        Args:
            html: HTML 内容

        Returns:
            专业列表
        """
        # 暂时返回示例数据
        majors = [
            {
                "code": "080901",
                "name": "计算机科学与技术",
                "category": "工学",
                "degree": "本科",
                "duration": "4年",
                "description": "培养具有良好科学素养，系统地掌握计算机科学与技术"
            },
            {
                "code": "080902",
                "name": "软件工程",
                "category": "工学",
                "degree": "本科",
                "duration": "4年",
                "description": "培养具有扎实的软件工程理论基础和专业技能"
            },
            {
                "code": "080910",
                "name": "数据科学与大数据技术",
                "category": "工学",
                "degree": "本科",
                "duration": "4年",
                "description": "培养掌握数据科学与大数据技术的基本理论"
            }
        ]

        return majors

    async def batch_scrape_universities(
        self,
        limit: int = 100,
        delay: float = 2.0
    ) -> Dict[str, Any]:
        """
        批量爬取院校数据

        Args:
            limit: 爬取数量限制
            delay: 每次请求间隔（秒）

        Returns:
            批量爬取结果
        """
        logger.info(f"开始批量爬取院校数据，限制: {limit}")

        # 更新请求延迟
        self.request_delay = delay

        # 爬取院校列表
        result = await self.scrape_university_list(use_cache=False)

        if not result.get("success"):
            return {
                "success": False,
                "message": "爬取院校列表失败",
                "data": None
            }

        universities = result["data"]["universities"][:limit]

        # 批量爬取详细信息
        detailed_universities = []
        for i, uni in enumerate(universities):
            logger.info(f"爬取院校详情 [{i+1}/{len(universities)}]: {uni['name']}")

            detail_result = await self.scrape_university_detail(
                uni["id"],
                use_cache=False
            )

            if detail_result.get("success"):
                detailed_universities.append(detail_result["data"])

        logger.info(f"批量爬取完成，成功: {len(detailed_universities)}/{len(universities)}")

        return {
            "success": True,
            "data": {
                "universities": detailed_universities,
                "total": len(detailed_universities),
                "updated_at": datetime.now().isoformat()
            }
        }


# 全局实例
sunshine_scraper = SunshineScraper()
