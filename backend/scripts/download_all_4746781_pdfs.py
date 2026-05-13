# -*- coding: utf-8 -*-
"""
Download all 9 PDFs from post 4746781 (2025 本科批) and identify each.
Also search for 专科批 and 提前批 posts separately.
"""
import requests, re, os, sys, io, pdfplumber, time
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

# 9 PDFs from post 4746781 (attachment IDs 585885-585893)
PDF_IDS = {
    '585885': 'post_4746781_01',
    '585886': 'post_4746781_02',
    '585887': 'post_4746781_03',
    '585888': 'post_4746781_04',
    '585889': 'post_4746781_05',
    '585890': 'post_4746781_06',
    '585891': 'post_4746781_07',
    '585892': 'post_4746781_08',
    '585893': 'post_4746781_09',
}

def download_pdf(name, save_as):
    url = f'{BASE}/attachment/0/585/{name}/4746781.pdf'
    out_path = RAW_DIR / save_as
    if out_path.exists():
        print(f'  Already: {save_as}')
        return str(out_path)

    try:
        r = session.get(url, timeout=120)
        if r.status_code == 200 and len(r.content) > 5000:
            with open(out_path, 'wb') as f:
                f.write(r.content)
            print(f'  [OK] {save_as} ({len(r.content)/1024:.1f} KB)')
            return str(out_path)
        else:
            print(f'  [FAIL] {url}: status={r.status_code}')
            return None
    except Exception as e:
        print(f'  [ERR] {e}')
        return None

def identify_pdf_content(pdf_path):
    """Parse first page of PDF to identify which batch it is"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page_text = pdf.pages[0].extract_text() or ''
            # Check first few pages
            for pg in range(min(3, len(pdf.pages))):
                page_text = pdf.pages[pg].extract_text() or ''
                lines = page_text.split('\n')[:10]
                for line in lines:
                    print(f'    {line[:120]}')
            return first_page_text
    except Exception as e:
        print(f'  Error reading PDF: {e}')
        return ''

def determine_batch_type(text):
    """Determine batch type from PDF text content using first line title"""
    # The first meaningful line of the PDF is usually the title
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    title_line = lines[0] if lines else ''

    # Direct title matching - the title IS the batch type
    if '本科普通类（历史）' in title_line or '本科普通类(历史)' in title_line:
        return '本科普通类（历史）'
    if '本科普通类（物理）' in title_line or '本科普通类(物理)' in title_line:
        return '本科普通类（物理）'
    if '本科体育类' in title_line:
        return '本科体育类统考'
    if '本科音乐类' in title_line:
        return '本科音乐类统考'
    if '本科舞蹈类' in title_line:
        return '本科舞蹈类统考'
    if '本科美术' in title_line:
        return '本科美术与设计类统考'
    if '本科书法类' in title_line:
        return '本科书法类统考'
    if '本科播音' in title_line:
        return '本科播音与主持类统考'
    if '本科表' in title_line and ('导' in title_line or '演' in title_line):
        return '本科表(导)演类统考'

    # Fallback matching
    text = text.replace(' ', '')
    if '专科' in text:
        if '物理' in text:
            return '专科普通类（物理）'
        if '历史' in text:
            return '专科普通类（历史）'
        if any(kw in text for kw in ['艺体','体育','音乐','美术','舞蹈','书法','播音','表(导)演']):
            return '专科艺体类统考'
    if '提前批' in text or '提前' in text:
        if '专科' in text:
            if '卫生' in text:
                return '提前批专科卫生专项'
            return '提前批专科普通类'
        if '教师' in text:
            return '提前批本科教师专项'
        if '卫生' in text:
            return '提前批本科卫生专项'
        if '物理' in text:
            return '提前批本科普通类（物理）'
        if '历史' in text:
            return '提前批本科普通类（历史）'
        return '提前批本科'
    if any(kw in text for kw in ['艺术','体育','音乐','美术','舞蹈','书法','播音','表(导)演']):
        return '本科艺体类'
    if '物理' in text or '物理类' in text:
        return '本科普通类（物理）'
    if '历史' in text or '历史类' in text:
        return '本科普通类（历史）'
    if '征集' in text:
        return '征集志愿'
    return None

def search_for_missing_posts():
    """Search for 专科批 and 提前批 posts using various approaches"""
    print('\n' + '='*60)
    print('Searching for 专科批 and 提前批 posts...')
    print('='*60)

    # Try to find 2025 posts by searching for specific file patterns
    # The gkmlpt section might have archived 2025 data
    search_urls = [
        f'{BASE}/gkmlpt/content/4/4458/post_4458330.html',  # Known 2024 pattern
    ]

    # Try to find 2025 专科批 and 提前批 pages
    # These would be published around July 2025, near post_4746781
    # Try a range around 4746781 for posts mentioning 专科/提前批
    found = []

    # First, try to search the gkmlpt or news sections for 2025 content
    for section in ['ptgk', 'gkmlpt', 'news']:
        try:
            r = session.get(f'{BASE}/{section}/', timeout=15)
            if r.status_code == 200:
                links = re.findall(r'href="([^"]+)"', r.text)
                relevant = [l for l in links if '2025' in l or '投档' in l or '专科' in l or '提前' in l]
                if relevant:
                    print(f'  {section}/ has {len(relevant)} relevant links:')
                    for l in relevant[:10]:
                        print(f'    {l}')
        except:
            pass

    # Try a smaller range of post IDs specifically looking for 2025 content
    for pid in range(4746000, 4747805, 5):
        url = f'{BASE}/ptgk/content/post_{pid}.html'
        try:
            r = session.head(url, timeout=8, allow_redirects=True)
            if r.status_code == 200:
                r2 = session.get(url, timeout=15)
                r2.encoding = 'utf-8'
                title_m = re.search(r'<title>([^<]+)</title>', r2.text)
                title = title_m.group(1) if title_m else ''
                if '2025' in title and ('专科' in title or '提前' in title or '征集' in title):
                    print(f'  FOUND [{pid}]: {title}')
                    # Get PDFs
                    pdfs = re.findall(r'href="([^"]*\.pdf)"', r2.text, re.IGNORECASE)
                    found.append({'pid': pid, 'title': title, 'pdfs': pdfs})
                    for p in pdfs:
                        print(f'    PDF: {p}')
            elif r.status_code == 404:
                pass
        except:
            pass

    return found

def main():
    print('='*60)
    print('Downloading all 9 PDFs from post 4746781 (2025 本科批)')
    print('='*60)

    # Download all 9 PDFs
    downloaded = {}
    for id_, label in PDF_IDS.items():
        filename = f'2025_raw_{label}.pdf'
        result = download_pdf(id_, filename)
        if result:
            downloaded[id_] = result

    # Identify each PDF's content
    print(f'\n{"="*60}')
    print('Identifying PDF contents...')
    print('='*60)

    pdf_contents = {}
    for id_, path in sorted(downloaded.items()):
        print(f'\n--- PDF {id_} ({os.path.basename(path)}) ---')
        text = identify_pdf_content(path)
        batch = determine_batch_type(text)
        pdf_contents[id_] = {'path': path, 'batch': batch, 'size_kb': os.path.getsize(path)/1024}
        print(f'  -> Identified as: {batch}')

    # Rename files based on identified content
    print(f'\n{"="*60}')
    print('Renaming PDFs by batch type...')
    print('='*60)

    renamed = {}
    for id_, info in pdf_contents.items():
        if info['batch']:
            safe_name = info['batch'].replace('（', '(').replace('）', ')').replace('/', '_')
            new_path = RAW_DIR / f'2025_{safe_name}.pdf'
            os.rename(info['path'], new_path)
            renamed[info['batch']] = str(new_path)
            print(f'  {info["batch"]} -> {new_path.name}')
        else:
            print(f'  [UNIDENTIFIED] {id_} (keeping original name)')

    # Search for missing posts (专科批, 提前批)
    search_for_missing_posts()

    # Print final file listing
    print(f'\n{"="*60}')
    print(f'Files in {RAW_DIR}:')
    print(f'{"="*60}')
    for f in sorted(RAW_DIR.glob('*.pdf')):
        size = f.stat().st_size / 1024
        print(f'  {f.name} ({size:.1f} KB)')

    print(f'\nIdentified batches:')
    for batch, path in renamed.items():
        print(f'  {batch}: {os.path.basename(path)}')

    # Summary: what we have vs what we need
    needed = set([
        '本科普通类（物理）', '本科普通类（历史）',
        '专科普通类（物理）', '专科普通类（历史）',
        '本科艺体类统考', '专科艺体类统考',
        '提前批本科教师专项', '提前批本科卫生专项',
        '提前批本科普通类（物理）', '提前批本科普通类（历史）',
        '提前批专科普通类', '提前批专科卫生专项',
        '本科征集志愿', '专科征集志愿',
    ])
    have = set(renamed.keys())
    missing = needed - have
    print(f'\nHave: {have}')
    print(f'Still missing: {missing}')


if __name__ == '__main__':
    main()
