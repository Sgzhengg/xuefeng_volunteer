# -*- coding: utf-8 -*-
"""
Download PDFs from the actual 2025 专科批 and 提前批 post URLs found via web search.
"""
import requests, re, os, sys, io
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

# Actual post URLs found via web search
TARGET_PAGES = [
    # 专科批
    {
        'url': 'https://eea.gd.gov.cn/gkmlpt/content/4/4754/mpost_4754637.html',
        'label': '专科批普通类及艺体类',
        'pid': 4754637,
        'section': 'gkmlpt',
    },
    {
        'url': 'https://eea.gd.gov.cn/ptgk/content/post_4756547.html',
        'label': '专科征集志愿',
        'pid': 4756547,
        'section': 'ptgk',
    },
    {
        'url': 'https://eea.gd.gov.cn/gkmlpt/content/4/4753/mpost_4753260.html',
        'label': '提前批专科卫生专项',
        'pid': 4753260,
        'section': 'gkmlpt',
    },
    # 提前批本科
    {
        'url': 'https://eea.gd.gov.cn/ptgk/content/post_4743597.html',
        'label': '提前批本科非军检及教师专项艺体',
        'pid': 4743597,
        'section': 'ptgk',
    },
    {
        'url': 'https://eea.gd.gov.cn/ptgk/content/post_4746199.html',
        'label': '提前批本科高校专项计划',
        'pid': 4746199,
        'section': 'ptgk',
    },
    {
        'url': 'https://eea.gd.gov.cn/zwgk/sjfb/tjsj/content/post_4742894.html',
        'label': '提前批本科军检院校',
        'pid': 4742894,
        'section': 'zwgk',
    },
]

def find_pdfs_on_page(page_url):
    """Find all PDF links on a page"""
    pdf_urls = []
    try:
        r = session.get(page_url, timeout=30)
        r.encoding = 'utf-8'
        html = r.text
        print(f'  Status: {r.status_code}, Length: {len(html)}')

        # Find PDF links
        pdfs = re.findall(r'href="([^"]*\.pdf)"', html, re.IGNORECASE)
        for p in pdfs:
            full = p if p.startswith('http') else f'{BASE}{p}' if p.startswith('/') else f'{BASE}/{p}'
            if full not in pdf_urls:
                pdf_urls.append(full)

        # Also check attachment paths
        attachments = re.findall(r'(/attachment/[^\s"\'<>]+\.pdf)', html, re.IGNORECASE)
        for a in attachments:
            full = f'{BASE}{a}'
            if full not in pdf_urls:
                pdf_urls.append(full)

        return pdf_urls, html
    except Exception as e:
        print(f'  Error: {e}')
        return [], ''

def identify_batch_from_content(page_url, pdf_url, html):
    """Identify batch from page content"""
    combined = f'{pdf_url} {html}'
    if '普通类（物理）' in combined or '普通类(物理)' in combined:
        return '普通类(物理)'
    if '普通类（历史）' in combined or '普通类(历史)' in combined:
        return '普通类(历史)'
    if '体育' in combined:
        return '体育类'
    if '音乐' in combined:
        return '音乐类'
    if '舞蹈' in combined:
        return '舞蹈类'
    if '美术' in combined:
        return '美术与设计类'
    if '书法' in combined:
        return '书法类'
    if '播音' in combined:
        return '播音与主持类'
    if '表' in combined and ('导' in combined or '演' in combined):
        return '表(导)演类'
    return 'unknown'

def download_pdf(pdf_url, filename):
    out_path = RAW_DIR / filename
    if out_path.exists():
        print(f'    SKIP (exists): {filename}')
        return str(out_path)
    try:
        r = session.get(pdf_url, timeout=120)
        if r.status_code == 200 and len(r.content) > 5000:
            with open(out_path, 'wb') as f:
                f.write(r.content)
            print(f'    [OK] {filename} ({len(r.content)/1024:.1f} KB)')
            return str(out_path)
        else:
            print(f'    [FAIL] status={r.status_code}, size={len(r.content)}')
    except Exception as e:
        print(f'    [ERR] {e}')
    return None

def main():
    total_downloaded = 0

    for page in TARGET_PAGES:
        print(f'\n{"="*60}')
        print(f'[{page["label"]}]')
        print(f'URL: {page["url"]}')
        print(f'{"="*60}')

        pdf_urls, html = find_pdfs_on_page(page['url'])

        # If no PDFs found directly, try the attachment directory pattern
        if not pdf_urls:
            pid = page['pid']
            # Try gkmlpt attachment pattern
            section_num = page['url'].split('/')[-3] if '/content/' in page['url'] else ''
            if section_num:
                # gkmlpt pattern: /gkmlpt/content/4/4754/ -> attachments
                try:
                    attach_urls = [
                        f'{BASE}/gkmlpt/attach/-/gkmlpt_pdf_{pid}.pdf',
                    ]
                    for au in attach_urls:
                        try:
                            r2 = session.head(au, timeout=10, allow_redirects=True)
                            if r2.status_code == 200:
                                pdf_urls.append(au)
                                print(f'  Found via attach pattern: {au}')
                        except:
                            pass
                except:
                    pass

        if pdf_urls:
            print(f'  Found {len(pdf_urls)} PDF(s):')
            for url in pdf_urls:
                print(f'    {url}')

            for pdf_url in pdf_urls:
                batch_type = identify_batch_from_content(page['url'], pdf_url, html)
                prefix = '2025_专科批' if '专科' in page['label'] else '2025_提前批本科'
                if '卫生' in page['label']:
                    prefix += '_卫生专项'
                if '征集' in page['label']:
                    prefix += '_征集'
                if '艺体' in page['label']:
                    prefix += '_艺体'
                if '军检' in page['label']:
                    prefix += '_军检'
                if '非军检' in page['label']:
                    prefix += '_非军检'
                if '教师' in page['label']:
                    prefix += '_教师专项'
                if '高校专项' in page['label']:
                    prefix += '_高校专项'

                filename = f'{prefix}_{batch_type}.pdf'
                download_pdf(pdf_url, filename)
                total_downloaded += 1
        else:
            print('  No PDFs found on this page')

    # Summary
    print(f'\n{"="*60}')
    print(f'Download complete. Files in {RAW_DIR}:')
    print('='*60)
    for f in sorted(RAW_DIR.glob('*')):
        if f.is_file():
            size = f.stat().st_size / 1024
            print(f'  {f.name} ({size:.1f} KB)')

if __name__ == '__main__':
    main()
