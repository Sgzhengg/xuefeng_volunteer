#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查广东省教育考试院官方页面的文件格式
"""

import requests
from bs4 import BeautifulSoup

url = "https://eea.gd.gov.cn/ptgk/content/post_4746781.html"

print("访问官方页面检查文件格式...")
print(f"URL: {url}")

try:
    response = requests.get(url, timeout=30)
    response.encoding = 'utf-8'

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找所有链接
        links = soup.find_all('a', href=True)

        print(f"\n找到 {len(links)} 个链接\n")

        # 投档相关链接
        admission_links = []
        for link in links:
            href = link['href']
            text = link.get_text().strip()

            if '投档' in text and '2025' in text:
                admission_links.append({
                    'text': text,
                    'href': href,
                    'full_url': href if href.startswith('http') else f"https://eea.gd.gov.cn{href}"
                })

        print("投档相关文件:")
        for i, link in enumerate(admission_links, 1):
            print(f"\n{i}. {link['text']}")
            print(f"   URL: {link['full_url']}")
            print(f"   文件类型: {link['href'].split('.')[-1] if '.' in link['href'] else '未知'}")

    else:
        print(f"访问失败，状态码: {response.status_code}")

except Exception as e:
    print(f"错误: {e}")
