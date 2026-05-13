# -*- coding: utf-8 -*-
"""测试2024和2023年广东高考投档PDF的下载URL"""

import requests
import re

def try_download_urls():
    """尝试各种可能的PDF URL模式"""

    # 2025年的已知URL模式:
    # 物理: https://eea.gd.gov.cn/attachment/0/585/585886/4746781.pdf
    # 历史: https://eea.gd.gov.cn/attachment/0/585/585885/4746781.pdf
    # post_id: 4746781, 附件路径: /attachment/0/585/585886/

    # 2024 post_id: 4458330, gkmlpt路径: /content/4/4458/
    # 2023 post_id: 4221647, news路径
    # 2019 post_id示例: 4221647 (从search结果中的2019归档)

    post_ids = {
        2024: 4458330,
        2023: 4221647,
    }

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/pdf,*/*',
    })

    for year, pid in post_ids.items():
        print(f"\n{'='*60}")
        print(f"测试 {year} 年 (post_id={pid})")
        print(f"{'='*60}")

        # 模式1: 与2025相同的结构
        path1 = pid // 8  # 585886 from 4746781
        path0 = pid // 8000  # 585 from 4746781
        urls_to_try = [
            f"https://eea.gd.gov.cn/attachment/0/{path0}/{path1}/{pid}.pdf",
            f"https://eea.gd.gov.cn/attachment/0/{path0}/{path1-1}/{pid}.pdf",
            f"https://eea.gd.gov.cn/attachment/0/{path0}/{path1+1}/{pid}.pdf",
            f"https://eea.gd.gov.cn/gkmlpt/attachment/0/{path0}/{path1}/{pid}.pdf",
            f"https://eea.gd.gov.cn/news/attachment/0/{path0}/{path1}/{pid}.pdf",
        ]

        for url in urls_to_try:
            try:
                r = session.head(url, timeout=15, allow_redirects=True)
                if r.status_code == 200:
                    content_type = r.headers.get('Content-Type', '')
                    size = r.headers.get('Content-Length', '?')
                    print(f"  SUCCESS [{r.status_code}] {url}")
                    print(f"    类型: {content_type}, 大小: {size}")
                elif r.status_code == 302:
                    print(f"  REDIRECT [{r.status_code}] {url} -> {r.headers.get('Location', '?')}")
                else:
                    print(f"  [{r.status_code}] {url}")
            except Exception as e:
                print(f"  [ERR] {url}: {str(e)[:60]}")

        # 也尝试用页面中可能引出的附件路径
        if year == 2024:
            # 尝试在gkmlpt页面中找到附件
            page_url = f"https://eea.gd.gov.cn/gkmlpt/content/4/4458/post_{pid}.html"
            try:
                r = session.get(page_url, timeout=30)
                r.encoding = 'utf-8'
                html = r.text
                # 查找所有可能的URL模式
                for pattern in [r'/attachment/[^"\']+\.pdf', r'/[^"\']+投档[^"\']+\.pdf']:
                    matches = re.findall(pattern, html)
                    for m in matches:
                        print(f"  在HTML中发现: {m}")
            except Exception as e:
                print(f"  无法获取页面: {e}")

if __name__ == "__main__":
    try_download_urls()
