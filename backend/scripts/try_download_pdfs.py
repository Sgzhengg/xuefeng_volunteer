# -*- coding: utf-8 -*-
"""尝试从广东省教育考试院官网下载2024和2023年投档PDF"""

import requests
import re
import json
from pathlib import Path

def try_fetch_attachments(page_url, year):
    """尝试获取页面附件"""
    print(f"\n{'='*60}")
    print(f"尝试获取 {year} 年数据: {page_url}")
    print(f"{'='*60}")

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    # 1. 获取页面
    resp = session.get(page_url, timeout=30)
    resp.encoding = 'utf-8'
    html = resp.text
    print(f"页面状态: {resp.status_code}, 长度: {len(html)}")

    # 2. 找CSRF
    csrf_m = re.search(r"CSRF:\s*'([^']+)'", html)
    if not csrf_m:
        print("未找到CSRF token")
        return None
    csrf = csrf_m.group(1)
    print(f"CSRF: {csrf}")

    # 3. 找附件（直接在HTML中）
    pdf_links = re.findall(r'href="([^"]*\.pdf[^"]*)"', html, re.IGNORECASE)
    print(f"HTML中找到 {len(pdf_links)} 个PDF链接:")
    for link in pdf_links:
        print(f"  {link}")

    # 4. 尝试各种API路径获取内容
    api_paths = [
        f"/gkmlpt/api/content/{page_url.split('/content/')[1].replace('.html', '').replace('post_', '')}",
        f"/gkmlpt/api/content/{page_url.split('/content/')[1].replace('post_', '')}",
        "/gkmlpt/api/content/detail",
    ]

    for api_path in api_paths:
        full_url = f"https://eea.gd.gov.cn{api_path}"
        try:
            r = session.get(full_url, timeout=30,
                headers={'X-CSRF-TOKEN': csrf, 'X-Requested-With': 'XMLHttpRequest'})
            if r.status_code == 200:
                try:
                    data = r.json()
                    print(f"\nAPI {api_path} 返回JSON, keys: {list(data.keys())[:10]}")
                    # 查找附件
                    text = json.dumps(data, ensure_ascii=False)
                    pdfs = re.findall(r'["\']([^"\']*\.pdf[^"\']*)["\']', text, re.IGNORECASE)
                    for p in pdfs[:20]:
                        print(f"  PDF引用: {p}")
                except:
                    print(f"\nAPI {api_path} 返回非JSON, 类型: {type(r.text)}")
        except Exception as e:
            pass

    # 5. 也尝试用content_id直接构造附件URL
    content_id = page_url.split('post_')[1].split('.')[0]
    possible_pdf_urls = [
        f"https://eea.gd.gov.cn/gkmlpt/attach/-/gkmlpt_pdf_{content_id}.pdf",
        f"https://eea.gd.gov.cn/gkmlpt/file/{content_id}.pdf",
    ]
    for pdf_url in possible_pdf_urls:
        r = requests.head(pdf_url, timeout=10)
        if r.status_code == 200:
            print(f"\n找到PDF: {pdf_url}")
            return pdf_url


if __name__ == "__main__":
    # 2024
    try_fetch_attachments(
        "https://eea.gd.gov.cn/gkmlpt/content/4/4458/post_4458330.html",
        2024
    )

    # 2023
    try_fetch_attachments(
        "https://eea.gd.gov.cn/news/content/post_4221647.html",
        2023
    )
