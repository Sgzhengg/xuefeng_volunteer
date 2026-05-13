# -*- coding: utf-8 -*-
"""
Targeted download of 2025 Guangdong Gaokao batch PDFs.
Scans the ptgk listing page and nearby post IDs for matching batches.
"""
import requests, re, os, json, time, sys, io
from pathlib import Path
from urllib.parse import urljoin, unquote

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = 'https://eea.gd.gov.cn'
DATA_DIR = Path(r'd:\xuefeng_volunteer\backend\data')
RAW_DIR = DATA_DIR / 'raw'
RAW_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
})

# Keywords to identify batch types from PDF filenames/titles
BATCH_PATTERNS = {
    '本科普通类（物理）': ['普通类（物理）', '普通类物理', '本科批次普通类'],
    '本科普通类（历史）': ['普通类（历史）', '普通类历史', '本科批次普通类'],
    '专科普通类（物理）': ['专科批次普通类（物理）', '专科普通类（物理）'],
    '专科普通类（历史）': ['专科批次普通类（历史）', '专科普通类（历史）'],
    '艺体类统考': ['艺体类', '体育类', '音乐类', '美术类', '舞蹈类', '书法类', '播音与主持', '表（导）演'],
    '教师专项': ['教师专项'],
    '卫生专项': ['卫生专项'],
    '提前批': ['提前批', '空军', '招飞'],
    '征集志愿': ['征集志愿'],
}

def get_pdf_filename_from_url(pdf_url):
    """Extract a clean filename from PDF URL"""
    # Try to get original filename
    parts = unquote(pdf_url).split('/')
    return parts[-1] if parts[-1].endswith('.pdf') else f'unknown_{abs(hash(pdf_url))}.pdf'

def identify_batch_from_url(pdf_url, page_title=''):
    """Identify which batch a PDF belongs to based on URL and title"""
    combined = unquote(pdf_url) + ' ' + page_title
    for batch_name, patterns in BATCH_PATTERNS.items():
        for pat in patterns:
            if pat in combined:
                return batch_name
    return None

def get_page_post_ids():
    """Get all post IDs from the ptgk listing page"""
    post_ids = []
    try:
        r = session.get(f'{BASE}/ptgk/', timeout=30)
        r.encoding = 'utf-8'
        html = r.text
        # Extract all post_XXXXXXX.html links
        matches = re.findall(r'post_(\d+)\.html', html)
        post_ids = [int(m) for m in matches]
        print(f'Found {len(post_ids)} posts on ptgk listing page')
    except Exception as e:
        print(f'Error accessing ptgk listing: {e}')
    return post_ids

def find_pdfs_on_page(pid):
    """Find PDF links on a specific post page"""
    url = f'{BASE}/ptgk/content/post_{pid}.html'
    try:
        r = session.get(url, timeout=30)
        r.encoding = 'utf-8'
        html = r.text
        if r.status_code != 200:
            return None, None, None

        title_match = re.search(r'<title>([^<]+)</title>', html)
        title = title_match.group(1) if title_match else ''

        # Find PDF links
        pdf_urls = []
        for pattern in [r'href="([^"]*\.pdf)"', r'href="([^"]*\.PDF)"']:
            pdf_urls.extend(re.findall(pattern, html, re.IGNORECASE))

        # Also check for attachment URLs
        for pattern in [r'/attachment/([^"\']+\.pdf)']:
            found = re.findall(pattern, html, re.IGNORECASE)
            for f in found:
                full = f'{BASE}/attachment/{f}'
                if full not in pdf_urls:
                    pdf_urls.append(full)

        if not pdf_urls:
            # Check for 附件 (attachments) links in the page
            attach_links = re.findall(r'(/attachment/[^"\'\s]+)', html)
            for link in attach_links:
                if link.lower().endswith('.pdf'):
                    full = urljoin(BASE, link)
                    if full not in pdf_urls:
                        pdf_urls.append(full)

        return pdf_urls, title, html
    except Exception as e:
        return None, str(e), ''

def download_pdf(pdf_url, filename):
    """Download a PDF file"""
    out_path = RAW_DIR / filename
    if out_path.exists():
        print(f'  Already exists: {filename}')
        return str(out_path)

    try:
        full_url = pdf_url if pdf_url.startswith('http') else urljoin(BASE, pdf_url)
        r = session.get(full_url, timeout=120)
        if r.status_code == 200 and len(r.content) > 5000:
            with open(out_path, 'wb') as f:
                f.write(r.content)
            size_kb = len(r.content) / 1024
            print(f'  [OK] {filename} ({size_kb:.1f} KB)')
            return str(out_path)
        else:
            print(f'  [FAIL] {full_url}: status={r.status_code}, size={len(r.content)}')
            return None
    except Exception as e:
        print(f'  [ERR] {e}')
        return None

def main():
    print('=' * 60)
    print('Downloading 2025 Guangdong Gaokao Batch PDFs')
    print('=' * 60)

    # Step 1: Get all post IDs from ptgk listing
    post_ids = get_page_post_ids()
    if not post_ids:
        print('No posts found on ptgk listing page. Using fallback range.')
        # Use a broad range around the known post
        post_ids = list(range(4746781 - 3000, 4895000, 1))

    # Step 2: Scan each post page for batch-related PDFs
    downloaded = {}
    total = len(post_ids)
    batch_keywords = ['投档', '专科', '提前批', '征集', '艺体', '专项', '教师', '卫生', '空军', '招飞']

    for i, pid in enumerate(post_ids):
        if (i+1) % 50 == 0:
            print(f'  Progress: {i+1}/{total} ({len(downloaded)} downloads so far)')

        pdf_urls, title, html = find_pdfs_on_page(pid)
        if not pdf_urls or not title:
            continue

        # Check if the page is about admissions batches
        is_batch_page = any(kw in title + (html or '') for kw in batch_keywords)
        if not is_batch_page:
            continue

        print(f'\n[Post {pid}] {title}')

        # For each PDF, identify the batch and download
        for pdf_url in pdf_urls:
            batch = identify_batch_from_url(pdf_url, title)
            filename = get_pdf_filename_from_url(pdf_url)
            # Add batch prefix
            if batch:
                safe_batch = batch.replace('（', '(').replace('）', ')').replace('/', '_')
                filename = f'2025_{safe_batch}_{filename}'

            if batch or '投档' in (title or ''):
                print(f'  Batch: {batch or "general_admission"} | {filename}')
                result = download_pdf(pdf_url, filename)
                if result:
                    downloaded[filename] = {'batch': batch, 'pid': pid, 'title': title}

    # Step 3: Also check the known 4746781 page for specific batch PDFs
    print(f'\n--- Checking main 本科批 post (4746781) ---')
    pdf_urls, title, html = find_pdfs_on_page(4746781)
    if pdf_urls:
        print(f'  Title: {title}')
        for pdf_url in pdf_urls:
            batch = identify_batch_from_url(pdf_url, title)
            print(f'  PDF: {pdf_url} -> batch={batch}')
            # Download if not already
            if batch:
                filename = f'2025_{batch}_{get_pdf_filename_from_url(pdf_url)}'
                download_pdf(pdf_url, filename)

    # Summary
    print(f'\n{"="*60}')
    print(f'Results: Downloaded {len(downloaded)} PDFs')
    print(f'{"="*60}')

    if downloaded:
        print(f'\nDownloaded files ({len(downloaded)}):')
        for f, info in downloaded.items():
            print(f'  {f} | batch={info["batch"]} | pid={info["pid"]}')
    else:
        print(f'\nNo batch PDFs were found/downloaded.')
        # Generate manual guide
        print(f'\nGenerating manual download guide...')
        guide_path = RAW_DIR / 'manual_download_guide.txt'
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write('Manual Download Guide\n')
            f.write('='*60 + '\n')
            f.write('Visit: https://eea.gd.gov.cn/\n')
            f.write('Navigate: 通知公告 -> 普通高考\n')
            f.write('\nSearch for the following 2025 batch PDFs:\n')
            batches_manual = [
                ('专科普通类（物理）', '2025年专科批次普通类（物理）投档情况'),
                ('专科普通类（历史）', '2025年专科批次普通类（历史）投档情况'),
                ('专科艺体类统考', '2025年专科批次艺体类统考投档情况'),
                ('本科艺体类统考', '2025年本科批次艺体类统考投档情况'),
                ('本科教师专项', '2025年提前批本科教师专项投档情况'),
                ('本科卫生专项', '2025年提前批本科卫生专项投档情况'),
                ('提前批本科普通类', '2025年提前批本科普通类投档情况'),
                ('提前批专科普通类', '2025年提前批专科普通类投档情况'),
                ('本科征集志愿', '2025年本科批次征集志愿投档情况'),
                ('专科征集志愿', '2025年专科批次征集志愿投档情况'),
            ]
            for label, keyword in batches_manual:
                f.write(f'\n[{label}] -> search: "{keyword}"\n')
                f.write(f'Save as: 2025_{label}.pdf\n')
            f.write(f'\nPut all PDFs in: {RAW_DIR}\n')
        print(f'Guide saved to: {guide_path}')

    # Print what's now in raw directory
    print(f'\nFiles in {RAW_DIR}:')
    for f in sorted(RAW_DIR.glob('*')):
        if f.is_file():
            print(f'  {f.name} ({f.stat().st_size/1024:.1f} KB)')


if __name__ == '__main__':
    main()
