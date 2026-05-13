#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API分析工具 - 用于分析高考网站的数据接口

使用Playwright分析网站并找到真实的JSON接口
"""

from playwright.async_api import async_playwright
import json
import re
from typing import List, Dict
from urllib.parse import urlparse, parse_qs
import asyncio


class APIAnalyzer:
    """API分析器"""

    def __init__(self):
        self.captured_requests = []

    async def analyze_gaokao_cn(self):
        """分析高考直通车网站"""
        print("分析高考直通车...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            # 监听所有网络请求
            def log_request(request):
                url = request.url
                method = request.method
                print(f"请求: {method} {url}")

                # 记录可能的API请求
                if any(keyword in url.lower() for keyword in ['api', 'json', 'ajax', 'query', 'batch']):
                    self.captured_requests.append({
                        'url': url,
                        'method': method,
                        'headers': request.headers,
                        'post_data': request.post_data
                    })

            page.on("request", log_request)

            # 访问页面
            target_url = "https://www.gaokao.cn/"
            await page.goto(target_url)

            # 尝试导航到广东2025投档线页面
            # 这里需要根据实际网站结构调整

            # 等待用户手动导航
            print("请在浏览器中手动导航到2025年广东本科投档线页面...")
            print("按Enter继续...")
            input()

            # 等待一段时间捕获请求
            await asyncio.sleep(10)

            await browser.close()

        # 分析捕获的请求
        self.analyze_captured_requests()

    async def analyze_gaokaopai(self):
        """分析掌上高考网站"""
        print("分析掌上高考...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            # 监听所有网络请求
            def log_request(request):
                url = request.url
                method = request.method
                print(f"请求: {method} {url}")

                # 记录可能的API请求
                if any(keyword in url.lower() for keyword in ['api', 'json', 'ajax', 'query', 'batch']):
                    self.captured_requests.append({
                        'url': url,
                        'method': method,
                        'headers': request.headers,
                        'post_data': request.post_data
                    })

            page.on("request", log_request)

            # 访问页面
            target_url = "https://www.gaokaopai.com/"
            await page.goto(target_url)

            # 等待用户手动导航
            print("请在浏览器中手动导航到2025年广东本科投档线页面...")
            print("按Enter继续...")
            input()

            # 等待一段时间捕获请求
            await asyncio.sleep(10)

            await browser.close()

        # 分析捕获的请求
        self.analyze_captured_requests()

    async def analyze_eol(self):
        """分析中国教育在线网站"""
        print("分析中国教育在线...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            # 监听所有网络请求
            def log_request(request):
                url = request.url
                method = request.method
                print(f"请求: {method} {url}")

                # 记录可能的API请求
                if any(keyword in url.lower() for keyword in ['api', 'json', 'ajax', 'query', 'batch']):
                    self.captured_requests.append({
                        'url': url,
                        'method': method,
                        'headers': request.headers,
                        'post_data': request.post_data
                    })

            page.on("request", log_request)

            # 访问页面
            target_url = "https://www.eol.cn/"
            await page.goto(target_url)

            # 等待用户手动导航
            print("请在浏览器中手动导航到2025年广东本科投档线页面...")
            print("按Enter继续...")
            input()

            # 等待一段时间捕获请求
            await asyncio.sleep(10)

            await browser.close()

        # 分析捕获的请求
        self.analyze_captured_requests()

    async def analyze_official(self):
        """分析广东省教育考试院官网"""
        print("分析广东省教育考试院官网...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            # 监听所有网络请求
            def log_request(request):
                url = request.url
                method = request.method
                print(f"请求: {method} {url}")

                # 特别关注Excel/PDF文件
                if any(keyword in url.lower() for keyword in ['.xls', '.xlsx', '.pdf']):
                    print(f"发现文档下载链接: {url}")
                    self.captured_requests.append({
                        'url': url,
                        'method': method,
                        'type': 'document'
                    })

            page.on("request", log_request)

            # 访问页面
            target_url = "https://eea.gd.gov.cn/"
            await page.goto(target_url)

            # 等待用户手动导航
            print("请在浏览器中查找2025年广东本科投档线相关公告和附件...")
            print("按Enter继续...")
            input()

            # 等待一段时间捕获请求
            await asyncio.sleep(10)

            await browser.close()

        # 分析捕获的请求
        self.analyze_captured_requests()

    def analyze_captured_requests(self):
        """分析捕获的请求"""
        print("\n" + "=" * 80)
        print("捕获的API请求分析")
        print("=" * 80)

        if not self.captured_requests:
            print("未捕获到API请求")
            return

        # 去重
        unique_urls = set()
        for req in self.captured_requests:
            unique_urls.add(req['url'])

        print(f"\n共捕获 {len(unique_urls)} 个唯一URL:\n")

        for url in unique_urls:
            print(f"URL: {url}")

            # 分析URL参数
            parsed = urlparse(url)
            params = parse_qs(parsed.query)

            if params:
                print("  参数:")
                for key, values in params.items():
                    print(f"    {key}: {values[0]}")

            # 尝试推断API的功能
            self.guess_api_function(url)

            print()

    def guess_api_function(self, url: str):
        """根据URL推断API功能"""
        url_lower = url.lower()

        if 'admission' in url_lower or 'score' in url_lower:
            if 'guangdong' in url_lower:
                print("  功能推断: 广东投档线查询接口")
            else:
                print("  功能推断: 投档线查询接口")
        elif 'college' in url_lower or 'university' in url_lower:
            print("  功能推断: 院校信息接口")
        elif 'major' in url_lower or 'professional' in url_lower:
            print("  功能推断: 专业信息接口")
        elif 'batch' in url_lower:
            print("  功能推断: 批次查询接口")
        elif 'query' in url_lower or 'search' in url_lower:
            print("  功能推断: 搜索查询接口")

    def save_analysis_report(self, filename: str = "api_analysis_report.json"):
        """保存分析报告"""
        report = {
            'timestamp': str(asyncio.get_event_loop().time()),
            'captured_requests': self.captured_requests,
            'unique_urls': list(set(req['url'] for req in self.captured_requests))
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n分析报告已保存: {filename}")


async def main():
    """主函数"""
    analyzer = APIAnalyzer()

    print("选择要分析的网站:")
    print("1. 高考直通车")
    print("2. 掌上高考")
    print("3. 中国教育在线")
    print("4. 广东省教育考试院")
    print("5. 分析全部")

    choice = input("请选择 (1-5): ").strip()

    if choice == '1':
        await analyzer.analyze_gaokao_cn()
    elif choice == '2':
        await analyzer.analyze_gaokaopai()
    elif choice == '3':
        await analyzer.analyze_eol()
    elif choice == '4':
        await analyzer.analyze_official()
    elif choice == '5':
        await analyzer.analyze_gaokao_cn()
        analyzer.captured_requests = []
        await analyzer.analyze_gaokaopai()
        analyzer.captured_requests = []
        await analyzer.analyze_eol()
        analyzer.captured_requests = []
        await analyzer.analyze_official()

    # 保存分析报告
    analyzer.save_analysis_report()


if __name__ == "__main__":
    asyncio.run(main())
