# -*- coding: utf-8 -*-
"""
Targeted search for 2025 专科批, 提前批, 征集志愿 posts.
Uses search API and focused ID ranges.
"""
import requests, re, os, sys, io, json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = 'https://eea.gd.gov.cn'
DATA_DIR = Path(r'd:\xuefeng_volunteer\backend\data')
RAW_DIR = DATA_DIR / 'raw'
RAW_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})

# Already have these from post 4746781
ALREADY_HAVE = {
    '本科普通类（物理）', '本科普通类（历史）',
    '本科体育类统考', '本科音乐类统考', '本科舞蹈类统考',
    '本科美术与设计类统考', '本科书法类统考',
    '本科播音与主持类统考', '本科表(导)演类统考',
}

def search_website(keyword):
    """Try various search approaches for a keyword"""
    print(f'\n  Searching: "{keyword}"')

    # Approach 1: site search URL
    urls = [
        f'{BASE}/ptgk/search?keyword={requests.utils.quote(keyword)}',
        f'{BASE}/search?keyword={requests.utils.quote(keyword)}',
        f'{BASE}/search/?searchword={requests.utils.quote(keyword)}',
    ]
    for url in urls:
        try:
            r = session.get(url, timeout=15)
            r.encoding = 'utf-8'
            if r.status_code == 200 and len(r.text) > 200:
                # Check for post links
                post_ids = re.findall(r'post_(\d+)\.html', r.text)
                if post_ids:
                    print(f'    Found {len(post_ids)} potential posts via {url[:60]}')
                    return [int(p) for p in post_ids]
        except:
            pass

    return []

def check_specific_posts(post_ids, batch_keywords):
    """Check specific post IDs for matching content"""
    found = []
    for pid in post_ids:
        try:
            url = f'{BASE}/ptgk/content/post_{pid}.html'
            r = session.get(url, timeout=15)
            r.encoding = 'utf-8'
            if r.status_code != 200:
                continue

            html = r.text
            title_m = re.search(r'<title>([^<]+)</title>', html)
            title = title_m.group(1).strip() if title_m else ''

            # Must contain 2025 and batch keyword
            if '2025' not in title:
                continue

            if not any(kw in title for kw in batch_keywords):
                continue

            pdfs = re.findall(r'href="([^"]*\.pdf)"', html, re.IGNORECASE)
            full_pdfs = [p if p.startswith('http') else f'{BASE}{p}' for p in pdfs]
            print(f'\n    [FOUND] {pid}: {title} ({len(pdfs)} PDFs)')
            for p in full_pdfs:
                print(f'      {p}')
            found.append({'pid': pid, 'title': title, 'pdfs': full_pdfs})
        except:
            pass
    return found

def download_pdf(pdf_url, filename):
    out_path = RAW_DIR / filename
    if out_path.exists():
        return str(out_path)
    try:
        r = session.get(pdf_url, timeout=120)
        if r.status_code == 200 and len(r.content) > 5000:
            with open(out_path, 'wb') as f:
                f.write(r.content)
            print(f'    [OK] {filename} ({len(r.content)/1024:.1f} KB)')
            return str(out_path)
    except Exception as e:
        print(f'    [ERR] {e}')
    return None

def main():
    print('='*60)
    print('Targeted search for 2025 专科批/提前批/征集 posts')
    print('='*60)

    # Strategy 1: Search for specific batch keywords
    search_terms = [
        '2025年专科批次', '2025年提前批本科', '2025年提前批专科',
        '卫生专项投档', '教师专项投档', '征集志愿投档',
    ]

    all_pids = set()
    for term in search_terms:
        pids = search_website(term)
        all_pids.update(pids)

    if all_pids:
        print(f'\nTotal unique post IDs found: {len(all_pids)}')
    else:
        print('\nNo posts found via search. Using known ranges.')

    # Strategy 2: Check posts in known 2025 July-August range
    # Post 4746781 is the main 本科批 (published ~July 2025)
    # 专科批 was published ~Aug 2025, so post IDs would be higher (4746800+)
    # 提前批 was published ~early July 2025, IDs would be lower (4746700-4746780)

    # Focus on specific narrow ranges where 2025 batch posts are likely
    ranges = [
        (4746740, 4746780, ['提前批', '2025']),     # 提前批 (just before main 本科批)
        (4746782, 4746850, ['专科', '2025']),        # 专科批 (just after)
        (4746850, 4747000, ['征集', '2025']),         # 征集志愿
        (4870000, 4871000, ['专科', '2025']),         # Alternative range
    ]

    all_found = []
    for start, end, keywords in ranges:
        print(f'\n  Checking range {start}-{end} for {keywords}...')
        found = check_specific_posts(range(start, end), keywords)
        all_found.extend(found)

    # Strategy 3: If still nothing found, try gkmlpt section
    if not all_found:
        print(f'\n  No results in ptgk - trying gkmlpt...')
        for section_url in [f'{BASE}/gkmlpt/content/4/4458/']:
            try:
                r = session.get(section_url, timeout=15)
                r.encoding = 'utf-8'
                links = re.findall(r'post_(\d+)\.html', r.text)
                if links:
                    print(f'  Found {len(links)} posts in gkmlpt')
                    found = check_specific_posts([int(l) for l in links], ['投档', '2025', '专科', '提前'])
                    all_found.extend(found)
            except:
                pass

    # Download found PDFs
    print(f'\n{"="*60}')
    print(f'Downloading PDFs from {len(all_found)} found pages...')
    print('='*60)

    for page in all_found:
        for pdf_url in page['pdfs']:
            filename = pdf_url.split('/')[-1]
            if not filename.endswith('.pdf'):
                filename = f'pid_{page["pid"]}.pdf'
            download_pdf(pdf_url, filename)

    # Print results
    print(f'\n{"="*60}')
    print(f'Results: Found {len(all_found)} pages')
    print('='*60)
    for page in all_found:
        print(f'  [{page["pid"]}] {page["title"][:80]}')

    # File listing
    print(f'\nFiles in {RAW_DIR}:')
    for f in sorted(RAW_DIR.glob('*.pdf')):
        print(f'  {f.name} ({f.stat().st_size/1024:.1f} KB)')


if __name__ == '__main__':
    main()
