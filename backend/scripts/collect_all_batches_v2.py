# -*- coding: utf-8 -*-
"""
Final version: Download all 2025 batch PDFs and search for missing posts.
Known mapping from post 4746781's 9 attachments.
"""
import requests, re, os, sys, io, time
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

# Known mapping: attachment_id -> batch_name
KNOWN_POST_4746781 = {
    '585885': '2025_本科普通类(历史).pdf',
    '585886': '2025_本科普通类(物理).pdf',
    '585887': '2025_本科体育类统考.pdf',
    '585888': '2025_本科音乐类统考.pdf',
    '585889': '2025_本科舞蹈类统考.pdf',
    '585890': '2025_本科美术与设计类统考.pdf',
    '585891': '2025_本科书法类统考.pdf',
    '585892': '2025_本科播音与主持类统考.pdf',
    '585893': '2025_本科表导演类统考.pdf',
}

def download_pdf(attach_id, filename):
    url = f'{BASE}/attachment/0/585/{attach_id}/4746781.pdf'
    out_path = RAW_DIR / filename
    if out_path.exists():
        print(f'  SKIP (exists): {filename}')
        return str(out_path)

    try:
        r = session.get(url, timeout=120)
        if r.status_code == 200 and len(r.content) > 5000:
            with open(out_path, 'wb') as f:
                f.write(r.content)
            print(f'  [OK] {filename} ({len(r.content)/1024:.1f} KB)')
            return str(out_path)
        else:
            print(f'  [FAIL] {url}: status={r.status_code}')
            return None
    except Exception as e:
        print(f'  [ERR] {e}')
        return None

def search_range_for_batches(start_pid, end_pid, keywords):
    """Search post IDs in given range for matching pages"""
    found = []
    step = 1
    total = (end_pid - start_pid) // step

    for i, pid in enumerate(range(start_pid, end_pid + 1, step)):
        if (i+1) % 100 == 0:
            print(f'  Scanning: {i+1}/{total} ({pid})...')

        url = f'{BASE}/ptgk/content/post_{pid}.html'
        try:
            r = session.head(url, timeout=6, allow_redirects=True)
            if r.status_code == 200:
                r2 = session.get(url, timeout=15)
                r2.encoding = 'utf-8'
                html = r2.text
                title_m = re.search(r'<title>([^<]+)</title>', html)
                title = title_m.group(1).strip() if title_m else ''

                if any(kw in title for kw in keywords):
                    pdfs = re.findall(r'href="([^"]*\.pdf)"', html, re.IGNORECASE)
                    full_pdfs = []
                    for p in pdfs:
                        full = p if p.startswith('http') else f'{BASE}{p}' if p.startswith('/') else f'{BASE}/{p}'
                        full_pdfs.append(full)

                    found.append({
                        'pid': pid,
                        'title': title,
                        'pdfs': full_pdfs,
                    })
                    print(f'\n  FOUND [{pid}]: {title} ({len(pdfs)} PDFs)')
                    for p in full_pdfs:
                        print(f'    {p}')
            elif r.status_code == 404:
                pass  # Skip
        except:
            pass

    return found

def search_gkmlpt_section(keywords):
    """Try gkmlpt section for 2025 data"""
    found = []
    urls_to_check = [
        f'{BASE}/gkmlpt/content/4/4458/',
        f'{BASE}/gkmlpt/',
    ]
    for url in urls_to_check:
        try:
            r = session.get(url, timeout=15)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                links = re.findall(r'href="([^"]+)"', r.text)
                for link in links:
                    if any(kw in link for kw in keywords):
                        print(f'  gkmlpt link: {link}')
                        full_url = link if link.startswith('http') else f'{BASE}{link}'
                        found.append({'url': full_url, 'link_text': link})
        except:
            pass
    return found

def download_found_pdfs(found_pages):
    """Download PDFs from found pages"""
    downloaded = []
    for page in found_pages:
        for pdf_url in page['pdfs']:
            # Get filename from URL
            parts = pdf_url.split('/')
            filename = parts[-1] if parts[-1].endswith('.pdf') else f'pid_{page["pid"]}.pdf'

            # Check if it already exists
            out_path = RAW_DIR / filename
            if out_path.exists():
                print(f'  SKIP: {filename}')
                downloaded.append(str(out_path))
                continue

            try:
                r = session.get(pdf_url, timeout=120)
                if r.status_code == 200 and len(r.content) > 5000:
                    with open(out_path, 'wb') as f:
                        f.write(r.content)
                    print(f'  [OK] {filename} ({len(r.content)/1024:.1f} KB)')
                    downloaded.append(str(out_path))
            except Exception as e:
                print(f'  [ERR] {e}')

    return downloaded

def main():
    print('=' * 60)
    print('Phase 1: Downloading all 9 PDFs from post 4746781')
    print('=' * 60)

    # Phase 1: Download all known 本科批 PDFs
    for attach_id, filename in KNOWN_POST_4746781.items():
        download_pdf(attach_id, filename)

    # Phase 2: Search for 专科批 posts in expanded range
    print(f'\n{"="*60}')
    print('Phase 2: Searching for 专科批 posts (near 4746781)')
    print('='*60)

    zhuanke_keywords = ['专科', '提前批', '卫生专项', '教师专项', '征集', '艺体类']

    # Search around post 4746781 (July 2025)
    found_zhuanke = search_range_for_batches(4740000, 4800000, zhuanke_keywords)

    # Also try a wider range for earlier/later posts
    if len(found_zhuanke) < 5:
        print(f'\n  Only found {len(found_zhuanke)} pages, expanding search...')
        found_more = search_range_for_batches(4680000, 4740000, zhuanke_keywords)
        found_zhuanke.extend(found_more)

    # Download found PDFs
    print(f'\nDownloading {len(found_zhuanke)} found pages\' PDFs...')
    downloaded = download_found_pdfs(found_zhuanke)

    # Phase 3: Try news section for 提前批/专科
    print(f'\n{"="*60}')
    print('Phase 3: Searching news section for 提前批/专科 posts')
    print('='*60)

    # Try various URL patterns
    for search_term in ['提前批本科', '专科批次', '卫生专项', '教师专项']:
        try:
            search_url = f'{BASE}/search/?keyword={search_term}'
            r = session.get(search_url, timeout=15)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                print(f'  Search "{search_term}": {len(r.text)} bytes')
        except:
            pass

    # Phase 4: Print final summary
    print(f'\n{"="*60}')
    print('Final file listing in raw/')
    print('='*60)

    total_size = 0
    pdf_files = sorted(RAW_DIR.glob('*.pdf'))
    for f in pdf_files:
        size = f.stat().st_size / 1024
        total_size += size
        print(f'  {f.name} ({size:.1f} KB)')

    print(f'\nTotal: {len(pdf_files)} PDFs, {total_size:.1f} KB total')

    # What do we have?
    have = set()
    for f in pdf_files:
        name = f.name.lower()
        if '物理' in name and '本科' in name:
            have.add('本科普通类（物理）')
        elif '历史' in name and '本科' in name:
            have.add('本科普通类（历史）')
        elif '体育' in name:
            have.add('本科体育类统考')
        elif '音乐' in name:
            have.add('本科音乐类统考')
        elif '舞蹈' in name:
            have.add('本科舞蹈类统考')
        elif '美术' in name:
            have.add('本科美术与设计类统考')
        elif '书法' in name:
            have.add('本科书法类统考')
        elif '播音' in name:
            have.add('本科播音与主持类统考')
        elif '表导' in name or '表(导)' in name:
            have.add('本科表(导)演类统考')
        else:
            have.add(f.name)

    print(f'\nIdentified batches ({len(have)}):')
    for h in sorted(have):
        print(f'  [COLLECTED] {h}')

    # What's still missing?
    needed = [
        '专科普通类（物理）', '专科普通类（历史）',
        '专科艺体类统考',
        '提前批本科普通类（物理）', '提前批本科普通类（历史）',
        '提前批本科教师专项', '提前批本科卫生专项',
        '提前批专科普通类（物理）', '提前批专科普通类（历史）',
        '提前批专科卫生专项',
        '本科征集志愿', '专科征集志愿',
    ]
    missing = [n for n in needed if n not in have]
    print(f'\nStill missing ({len(missing)}):')
    for m in missing:
        print(f'  [MISSING ] {m}')


if __name__ == '__main__':
    main()
