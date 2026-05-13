# -*- coding: utf-8 -*-
"""
收集2025年广东省高考投档缺失批次的PDF文件

尝试从广东省教育考试院官网找到并下载缺失批次PDF。
如果自动下载失败，输出详细的手动下载指引。
"""
import requests, re, os, json, time
from pathlib import Path
from urllib.parse import urljoin

BASE = 'https://eea.gd.gov.cn'
DATA_DIR = Path(r'd:\xuefeng_volunteer\backend\data')
RAW_DIR = DATA_DIR / 'raw'
RAW_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
})

# Target batches to find (P0 first, then P1)
TARGET_BATCHES = [
    # P0
    {'keyword': '专科批次普通类（物理）投档情况', 'year': 2025, 'label': '专科批物理', 'filename': '2025_专科批_物理.pdf'},
    {'keyword': '专科批次普通类（历史）投档情况', 'year': 2025, 'label': '专科批历史', 'filename': '2025_专科批_历史.pdf'},
    # P1
    {'keyword': '专科批次艺体类统考投档情况', 'year': 2025, 'label': '专科批艺体', 'filename': '2025_专科批_艺体.pdf'},
    {'keyword': '本科批次艺体类统考投档情况', 'year': 2025, 'label': '本科批艺体', 'filename': '2025_本科批_艺体.pdf'},
    {'keyword': '提前批本科教师专项投档情况', 'year': 2025, 'label': '教师专项', 'filename': '2025_提前批本科_教师专项.pdf'},
    {'keyword': '提前批本科卫生专项投档情况', 'year': 2025, 'label': '卫生专项', 'filename': '2025_提前批本科_卫生专项.pdf'},
    {'keyword': '提前批本科普通类投档情况', 'year': 2025, 'label': '提前批本科普通类', 'filename': '2025_提前批本科_普通类.pdf'},
    {'keyword': '提前批专科普通类投档情况', 'year': 2025, 'label': '提前批专科普通类', 'filename': '2025_提前批专科_普通类.pdf'},
    {'keyword': '本科批次征集志愿投档情况', 'year': 2025, 'label': '本科征集志愿', 'filename': '2025_本科征集志愿.pdf'},
    {'keyword': '专科批次征集志愿投档情况', 'year': 2025, 'label': '专科征集志愿', 'filename': '2025_专科征集志愿.pdf'},
]

def find_pdf_on_page(page_url):
    """Try to find PDF links on a given page"""
    try:
        resp = session.get(page_url, timeout=30)
        resp.encoding = 'utf-8'
        html = resp.text
        if resp.status_code != 200:
            return None, f'HTTP {resp.status_code}'

        # Find PDF links
        pdf_patterns = [
            r'href="([^"]*\.pdf)"',
            r'href="([^"]*\.PDF)"',
            r'src="([^"]*\.pdf)"',
            r'<a[^>]*href="([^"]*attachment[^"]*\.pdf)"',
        ]
        pdfs = []
        for pat in pdf_patterns:
            found = re.findall(pat, html, re.IGNORECASE)
            pdfs.extend(found)

        if pdfs:
            # Deduplicate
            unique = []
            seen = set()
            for p in pdfs:
                if p not in seen:
                    seen.add(p)
                    unique.append(p)
            return unique, html
        return [], html
    except Exception as e:
        return None, str(e)

def search_site_for_batches():
    """Search the official website for batch pages"""
    results = {}

    # Strategy 1: Try the site search
    for batch in TARGET_BATCHES:
        label = batch['label']
        keyword = batch['keyword']

        print(f'\n{"="*60}')
        print(f'Searching: {label}')

        # Try search API
        search_url = f'{BASE}/ptgk/search'
        try:
            search_data = {'keyword': keyword.split('（')[0], 'page': 1}
            r = session.post(search_url, data=search_data, timeout=30)
            if r.status_code == 200:
                try:
                    data = r.json()
                    print(f'  Search returned: {type(data)}')
                except:
                    print(f'  Search response: {r.text[:200]}')
        except Exception as e:
            print(f'  Search error: {e}')

        # Strategy 2: Try known page URL patterns
        # The 2025 本科普通类 was at: /ptgk/content/post_4746781.html
        # Other batches might be at similar URLs
        results[label] = {'status': 'unknown', 'pdfs': []}

    return results

def try_known_2025_urls():
    """Try accessing known 2025 batch pages"""
    # Based on the working 2025 本科普通类 pattern
    # post_4746781 is the main 本科普通类
    # Other batches were likely published around the same time with nearby post IDs

    known_pages = []
    # The 2025 posts are in the ptgk section
    # Try a range of post IDs near the known one (4746781)
    base_id = 4746781

    # Extended range to find other batches (before and after the main post)
    for offset in range(-2500, 2501, 50):
        pid = base_id + offset

        # Skip unlikely ranges
        if pid < 4500000:
            continue

        known_pages.append({
            'pid': pid,
            'url': f'{BASE}/ptgk/content/post_{pid}.html'
        })

    print(f'Will scan {len(known_pages)} potential pages...')

    found_pdfs = {}
    count = 0
    for page in known_pages:
        count += 1
        if count % 20 == 0:
            print(f'  Scanned {count}/{len(known_pages)} pages...')
            time.sleep(0.5)

        url = page['url']
        try:
            r = session.head(url, timeout=10, allow_redirects=True)
            if r.status_code == 200:
                # Page exists, get full content
                pdfs, html = find_pdf_on_page(url)
                if pdfs:
                    # Check title
                    title_match = re.search(r'<title>([^<]+)</title>', html)
                    title = title_match.group(1) if title_match else 'Unknown'

                    # Check if related to admissions
                    if any(kw in html for kw in ['投档', '录取', '专科', '提前批', '征集', '艺体', '专项']):
                        found_pdfs[page['pid']] = {
                            'url': url,
                            'title': title,
                            'pdfs': pdfs,
                        }
                        print(f'  FOUND: [{page["pid"]}] {title} - {len(pdfs)} PDFs')
                        for p in pdfs:
                            print(f'    {p}')
            elif r.status_code == 404:
                pass  # Skip
            else:
                print(f'  UNEXPECTED [{r.status_code}] {url}')
        except Exception as e:
            pass

    return found_pdfs

def try_category_search(category, date_range=None):
    """Search within a specific category on the website"""
    # The ptgk section has a list page
    urls_to_try = [
        f'{BASE}/ptgk/',
        f'{BASE}/ptgk/index.html',
        f'{BASE}/ptgk/list.html',
        f'{BASE}/ptgk/content/',
    ]

    for url in urls_to_try:
        try:
            r = session.get(url, timeout=15)
            if r.status_code == 200:
                print(f'  Accessible: {url} ({len(r.text)} bytes)')
                # Check for links
                links = re.findall(r'href="([^"]+)"', r.text)
                ptgk_links = [l for l in links if 'ptgk' in l or 'post_' in l]
                print(f'  ptgk links: {len(ptgk_links)}')
                for l in ptgk_links[:20]:
                    print(f'    {l}')
                return r.text
        except:
            pass
    return None

def try_direct_ptgk_list():
    """Try to access the ptgk listing page"""
    print('\n--- Trying ptgk listing page ---')
    html = try_category_search('ptgk')
    return html

def download_pdf(pdf_url, filename):
    """Download a PDF file"""
    out_path = RAW_DIR / filename
    try:
        full_url = pdf_url if pdf_url.startswith('http') else urljoin(BASE, pdf_url)
        r = session.get(full_url, timeout=120)
        if r.status_code == 200 and len(r.content) > 5000:
            with open(out_path, 'wb') as f:
                f.write(r.content)
            print(f'  Downloaded: {filename} ({len(r.content)/1024:.1f} KB)')
            return str(out_path)
        else:
            print(f'  Download failed: {full_url} (status={r.status_code}, size={len(r.content)})')
            return None
    except Exception as e:
        print(f'  Error downloading: {e}')
        return None

def generate_manual_guide():
    """Generate the manual download guide"""
    guide = []

    guide.append('=' * 70)
    guide.append('广东省2025年高考投档数据 - 手动下载指引')
    guide.append('=' * 70)
    guide.append('')
    guide.append('官网: https://eea.gd.gov.cn/')
    guide.append('栏目: 通知公告 → 普通高考 → 广东省2025年...')
    guide.append('')
    guide.append('请按以下关键词在官网搜索并下载对应PDF文件:')
    guide.append('')

    for batch in TARGET_BATCHES:
        guide.append(f'  [{batch["label"]}]')
        guide.append(f'    搜索关键词: {batch["keyword"]}')
        guide.append(f'    保存为: {batch["filename"]}')
        guide.append('')

    guide.append('下载后放入: backend/data/raw/ 目录')
    guide.append(f'例如: d:\\xuefeng_volunteer\\backend\\data\\raw\\{TARGET_BATCHES[0]["filename"]}')
    guide.append('')
    guide.append('然后运行: cd backend && python scripts/supplement_missing_batches.py')
    guide.append('')

    guide_path = RAW_DIR / 'manual_download_guide.txt'
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(guide))

    return guide_path


def main():
    print('=' * 60)
    print('2025年广东省高考投档缺失批次 - 自动化数据收集')
    print('=' * 60)

    # Step 1: Try to access listing pages
    try_direct_ptgk_list()

    # Step 2: Try to scan pages near the known 2025 post ID
    print('\n--- Scanning for 2025 batch pages ---')
    found = try_known_2025_urls()

    if found:
        print(f'\nFound {len(found)} pages with PDFs!')
        # Download
        for pid, info in found.items():
            for pdf_url in info['pdfs']:
                # Determine which batch this belongs to
                title = info['title']
                html_text = info.get('html', '')

                # Match against target batches
                for batch in TARGET_BATCHES:
                    if batch['keyword'] in title or batch['keyword'] in pdf_url:
                        print(f'\n  Matched: {batch["label"]} <- {pdf_url}')
                        download_pdf(pdf_url, batch['filename'])
                        break
                else:
                    print(f'\n  Unmatched PDF: {pdf_url} (title: {title})')
    else:
        print('\nNo batch pages found automatically.')
        guide_path = generate_manual_guide()
        print(f'\nManual download guide generated: {guide_path}')
        print('\nPlease download the PDFs manually from the official website.')
        print('After downloading, run: python scripts/supplement_missing_batches.py')

    # Always generate the guide as backup
    guide_path = generate_manual_guide()
    print(f'\nGuide saved to: {guide_path}')


if __name__ == '__main__':
    main()
