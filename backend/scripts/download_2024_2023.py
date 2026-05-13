# -*- coding: utf-8 -*-
"""下载2024和2023年广东高考投档PDF - 完整版"""

import requests
import re
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def find_and_download(year):
    """尝试查找并下载某一年份的PDF"""
    post_ids = {
        2024: 4458330,
        2023: 4221647,
    }
    pid = post_ids.get(year)
    if not pid:
        print(f"Unknown year: {year}")
        return []

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })

    print(f"\n{'='*60}")
    print(f"尝试获取 {year} 年广东省投档PDF")
    print(f"{'='*60}")

    # URL patterns to try
    urls_to_try = [
        f"https://eea.gd.gov.cn/ptgk/content/post_{pid}.html",
        f"https://eea.gd.gov.cn/gkmlpt/content/4/4458/post_{pid}.html" if year == 2024 else "",
        f"https://eea.gd.gov.cn/news/content/post_{pid}.html" if year == 2023 else "",
    ]

    pdf_urls = []

    for page_url in urls_to_try:
        if not page_url:
            continue
        print(f"\n  [尝试] {page_url}")
        try:
            resp = session.get(page_url, timeout=30)
            resp.encoding = 'utf-8'
            html = resp.text
            print(f"  Status: {resp.status_code}, Length: {len(html)}")

            if resp.status_code != 200:
                continue

            title = re.findall(r'<title>([^<]+)</title>', html)
            print(f"  Title: {title}")

            # Find all PDF links
            pdfs = re.findall(r'href="([^"]*\.pdf[^"]*)"', html, re.IGNORECASE)
            print(f"  PDF links: {len(pdfs)}")
            for p in pdfs:
                full_url = p if p.startswith("http") else f"https://eea.gd.gov.cn{p}"
                pdf_urls.append(full_url)
                print(f"    {p}")

            if pdfs:
                break  # Found PDFs, stop trying other URLs

        except Exception as e:
            print(f"  Error: {e}")

    # Download PDFs
    downloaded = []
    for pdf_url in pdf_urls:
        filename = pdf_url.split("/")[-1]
        # Add year prefix
        out_name = f"{year}_{filename}"
        out_path = DATA_DIR / out_name

        print(f"\n  [下载] {pdf_url}")
        try:
            r = session.get(pdf_url, timeout=120)
            if r.status_code == 200 and len(r.content) > 10000:
                with open(out_path, 'wb') as f:
                    f.write(r.content)
                size_mb = len(r.content) / 1024 / 1024
                print(f"  完成: {out_path} ({size_mb:.1f} MB)")
                downloaded.append(str(out_path))
            else:
                print(f"  失败: status={r.status_code}, size={len(r.content)}")
        except Exception as e:
            print(f"  错误: {e}")

    return downloaded


if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)

    for year in [2024, 2023]:
        files = find_and_download(year)
        if files:
            print(f"\n{year}年下载完成: {len(files)} 个文件")
        else:
            print(f"\n{year}年未找到可下载的PDF")

    # Also save the direct PDF URLs for manual download
    print("\n" + "=" * 60)
    print("如自动下载失败，请手动下载以下PDF文件：")
    print("=" * 60)
    print("""
2024年：
  可能需要从以下页面手动下载：
  https://eea.gd.gov.cn/gkmlpt/content/4/4458/post_4458330.html
  (用微信扫页面底部二维码获取附件)

2023年：
  可能需要从以下页面手动下载：
  https://eea.gd.gov.cn/news/content/post_4221647.html
  (用微信扫页面底部二维码获取附件)

下载后请将PDF文件放到 backend/data/ 目录，命名为：
  - 2024_物理.pdf, 2024_历史.pdf
  - 2023_物理.pdf, 2023_历史.pdf

然后运行导入命令：
  python scripts/import_multi_year.py --pdf data/2024_物理.pdf --year 2024
  python scripts/import_multi_year.py --pdf data/2024_历史.pdf --year 2024
  python scripts/import_multi_year.py --pdf data/2023_物理.pdf --year 2023
  python scripts/import_multi_year.py --pdf data/2023_历史.pdf --year 2023
""")
