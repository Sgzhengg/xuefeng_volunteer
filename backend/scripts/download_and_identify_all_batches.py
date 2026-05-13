# -*- coding: utf-8 -*-
"""
Comprehensive script to download ALL PDFs from target pages, parse each one
to identify its actual content, rename correctly, and import the data.

Steps:
1. Download all PDFs from 6 target pages with unique temp names
2. Parse each PDF's first page to identify actual batch type
3. Rename PDFs with correct batch names
4. Parse and import all data into major_rank_data.json
"""
import requests, re, os, sys, io, json, shutil, pdfplumber
from pathlib import Path
from datetime import datetime
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = 'https://eea.gd.gov.cn'
DATA_DIR = Path(r'd:\xuefeng_volunteer\backend\data')
RAW_DIR = DATA_DIR / 'raw'
MAIN_FILE = DATA_DIR / 'major_rank_data.json'
BACKUP_DIR = DATA_DIR / 'backups'

RAW_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})

# Target pages with their label and expected batch group
TARGET_PAGES = [
    {
        'url': 'https://eea.gd.gov.cn/gkmlpt/content/4/4754/mpost_4754637.html',
        'label': '专科批普通类及艺体类',
        'batch_group': '专科批',
    },
    {
        'url': 'https://eea.gd.gov.cn/ptgk/content/post_4756547.html',
        'label': '专科征集志愿',
        'batch_group': '专科征集志愿',
    },
    {
        'url': 'https://eea.gd.gov.cn/gkmlpt/content/4/4753/mpost_4753260.html',
        'label': '提前批专科卫生专项',
        'batch_group': '提前批专科',
    },
    {
        'url': 'https://eea.gd.gov.cn/ptgk/content/post_4743597.html',
        'label': '提前批本科非军检及教师专项艺体',
        'batch_group': '提前批本科',
    },
    {
        'url': 'https://eea.gd.gov.cn/ptgk/content/post_4746199.html',
        'label': '提前批本科高校专项计划',
        'batch_group': '提前批本科',
    },
    {
        'url': 'https://eea.gd.gov.cn/ptgk/content/post_4742894.html',
        'label': '提前批本科军检院校',
        'batch_group': '提前批本科',
    },
]

KNOWN_985 = {
    '北京大学','清华大学','复旦大学','上海交通大学','浙江大学',
    '中国科学技术大学','南京大学','中国人民大学','中山大学',
    '华南理工大学','武汉大学','华中科技大学','西安交通大学',
    '哈尔滨工业大学','北京师范大学','南开大学','天津大学',
    '同济大学','东南大学','厦门大学','四川大学','电子科技大学',
    '吉林大学','东北大学','大连理工大学','山东大学',
    '中国海洋大学','西北工业大学','兰州大学','北京航空航天大学',
    '北京理工大学','中国农业大学','国防科技大学','中央民族大学',
    '华东师范大学','中南大学','湖南大学','重庆大学','西北农林科技大学',
}
KNOWN_211 = {
    '暨南大学','华南师范大学','北京邮电大学','北京交通大学',
    '北京科技大学','北京化工大学','北京工业大学','北京林业大学',
    '北京中医药大学','北京外国语大学','中国传媒大学',
    '中央财经大学','对外经济贸易大学','中国政法大学',
    '华北电力大学','中国矿业大学','中国石油大学',
    '中国地质大学','东北师范大学','东北林业大学',
    '华东理工大学','东华大学','上海外国语大学','上海财经大学',
    '上海大学','苏州大学','南京航空航天大学','南京理工大学',
    '中国药科大学','河海大学','江南大学','南京农业大学',
    '南京师范大学','合肥工业大学','安徽大学','福州大学',
    '南昌大学','郑州大学','武汉理工大学',
    '华中师范大学','华中农业大学','中南财经政法大学',
    '湖南师范大学','西南交通大学','四川农业大学',
    '西南大学','西南财经大学','贵州大学','云南大学',
    '西藏大学','西北大学','西安电子科技大学','长安大学',
    '陕西师范大学','青海大学','宁夏大学','新疆大学',
    '石河子大学','海南大学','广西大学','内蒙古大学',
    '延边大学','辽宁大学','大连海事大学','太原理工大学',
    '河北工业大学','哈尔滨工程大学','东北农业大学',
}


def find_pdfs_on_page(page_url):
    """Find all PDF links on a page"""
    pdf_urls = []
    try:
        r = session.get(page_url, timeout=30)
        r.encoding = 'utf-8'
        html = r.text
        print(f'  Status: {r.status_code}, Length: {len(html)}')

        # Pattern: href="/attachment/..." or full URLs
        patterns = [
            r'href="([^"]*\.pdf)"',
            r"href='([^']*\.pdf)'",
            r'href="([^"]*\.PDF)"',
            r"href='([^']*\.PDF)'",
        ]
        for pat in patterns:
            found = re.findall(pat, html, re.IGNORECASE)
            for p in found:
                if p.startswith('http'):
                    full = p
                elif p.startswith('/'):
                    full = f'{BASE}{p}'
                else:
                    full = f'{BASE}/{p}'
                if full not in pdf_urls:
                    pdf_urls.append(full)

        return pdf_urls, html
    except Exception as e:
        print(f'  Error: {e}')
        return [], ''


def download_pdf(pdf_url, temp_name):
    """Download a single PDF with a unique temp name"""
    out_path = RAW_DIR / temp_name
    if out_path.exists() and out_path.stat().st_size > 5000:
        print(f'    SKIP (exists): {temp_name}')
        return str(out_path)
    try:
        r = session.get(pdf_url, timeout=120)
        if r.status_code == 200 and len(r.content) > 5000:
            with open(out_path, 'wb') as f:
                f.write(r.content)
            print(f'    [OK] {temp_name} ({len(r.content)/1024:.1f} KB)')
            return str(out_path)
        else:
            print(f'    [FAIL] status={r.status_code}, size={len(r.content)}')
    except Exception as e:
        print(f'    [ERR] {e}')
    return None


def identify_batch_from_pdf(pdf_path):
    """Parse PDF first page to identify the actual batch/subject"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ''
            for pg in range(min(3, len(pdf.pages))):
                text = pdf.pages[pg].extract_text() or ''
                full_text += text + '\n'

            # The title is usually in the first line of the PDF
            lines = [l.strip() for l in full_text.split('\n') if l.strip()]
            title = lines[0] if lines else ''
            print(f'      Title: {title[:120]}')

            # Detect batch group
            is_zhuanke = '专科' in title
            is_tiqian = '提前批' in title
            is_zhengji = '征集' in title
            is_yitixi = any(kw in title for kw in ['艺体', '体育', '音乐', '美术', '舞蹈', '书法', '播音', '表('])
            is_jiaoshi = '教师' in title
            is_weisheng = '卫生' in title
            is_junjian = '军检' in title
            is_feijunjian = '非军检' in title
            is_gaoxiaozhuanxiang = '高校专项' in title
            is_kongjun = '空军' in title
            is_haijun = '海军' in title

            # Subject
            is_wuli = '物理' in title
            is_lishi = '历史' in title

            # Determine batch_group
            if is_tiqian:
                batch_group = '提前批本科' if not is_zhuanke else '提前批专科'
            elif is_zhuanke and is_zhengji:
                batch_group = '专科征集志愿'
            elif is_zhuanke:
                batch_group = '专科批'
            elif is_zhengji:
                batch_group = '本科征集志愿'
            else:
                batch_group = '本科批'

            # Determine subject
            if is_yitixi:
                if '体育' in title:
                    subject = '体育'
                elif '音乐' in title:
                    subject = '音乐'
                elif '舞蹈' in title:
                    subject = '舞蹈'
                elif '美术' in title:
                    subject = '美术与设计'
                elif '书法' in title:
                    subject = '书法'
                elif '播音' in title:
                    subject = '播音与主持'
                elif '表(' in title or '表(导)' in title:
                    subject = '表(导)演'
                else:
                    subject = '艺体'
            elif is_wuli:
                subject = '物理'
            elif is_lishi:
                subject = '历史'
            else:
                subject = '未知'

            # Determine category
            if is_junjian:
                category = '军检院校'
            elif is_feijunjian:
                category = '非军检院校'
            elif is_jiaoshi:
                category = '教师专项'
            elif is_weisheng:
                category = '卫生专项'
            elif is_gaoxiaozhuanxiang:
                category = '高校专项'
            elif is_kongjun or is_haijun:
                category = '空军海军招飞'
            elif is_zhengji:
                category = '征集志愿'
            elif is_yitixi:
                category = '艺体'
            else:
                category = '普通类'

            return {
                'title': title,
                'batch_group': batch_group,
                'subject': subject,
                'category': category,
                'is_wuli': is_wuli,
                'is_lishi': is_lishi,
                'is_yitixi': is_yitixi,
                'is_zhengji': is_zhengji,
                'is_tiqian': is_tiqian,
                'is_zhuanke': is_zhuanke,
            }
    except Exception as e:
        print(f'      Error reading PDF: {e}')
        return None


def get_canonical_name(batch_info):
    """Get standardized batch name from parsed info"""
    if not batch_info:
        return None, None

    group = batch_info['batch_group']
    subject = batch_info['subject']
    category = batch_info['category']

    if category in ('教师专项', '卫生专项'):
        return group, f'{group}{category}'
    elif category == '高校专项':
        return group, f'{group}高校专项计划'
    elif category == '军检院校':
        return group, f'{group}{category}({subject})'
    elif category == '非军检院校':
        return group, f'{group}{category}({subject})'
    elif category == '征集志愿':
        return group, f'{group}({subject})'
    elif subject in ('物理', '历史'):
        return group, f'{group}普通类({subject})'
    elif category == '艺体':
        return group, f'{group}{subject}类统考'
    elif category == '空军海军招飞':
        return group, '空军海军招飞'
    else:
        return group, f'{group}{category}({subject})'


def parse_pdf_data(pdf_path, batch_info):
    """Parse PDF and extract admission records"""
    records = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue
                    for row in table:
                        if not row or len(row) < 5:
                            continue
                        try:
                            # Standard format: 院校代码, 院校名称, 专业组代码, 计划数, 投档数, 投档最低分, 投档最低排位
                            uni_code = str(row[0] if len(row)>0 else '').strip()
                            uni_name = str(row[1] if len(row)>1 else '').strip()
                            group_code = str(row[2] if len(row)>2 else '').strip()

                            # Skip header rows
                            if not uni_name or uni_code in ('院校代码',''):
                                continue
                            if not uni_code.isdigit() or len(uni_code) < 4:
                                continue

                            # score col 5, rank col 6
                            min_score = 0
                            score_col = None
                            for col_idx in [5, 4]:
                                if col_idx < len(row) and row[col_idx]:
                                    try:
                                        v = int(str(row[col_idx]).strip().replace(',','').replace(' ',''))
                                        if 150 <= v <= 750:
                                            min_score = v
                                            score_col = col_idx
                                            break
                                    except:
                                        pass

                            min_rank = 0
                            rank_col = score_col + 1 if score_col is not None else 6
                            for col_idx in [rank_col, rank_col + 1, 6]:
                                if col_idx < len(row) and row[col_idx]:
                                    try:
                                        v = int(str(row[col_idx]).strip().replace(',','').replace(' ',''))
                                        if 1 <= v <= 1000000:
                                            min_rank = v
                                            break
                                    except:
                                        pass

                            if min_rank <= 0:
                                continue

                            level = '985' if uni_name in KNOWN_985 else ('211' if uni_name in KNOWN_211 else '普通本科')

                            records.append({
                                'year': 2025,
                                'province': '广东',
                                'university_name': uni_name,
                                'major_name': f'专业组{group_code}' if group_code else '未分类',
                                'min_rank': min_rank,
                                'min_score': min_score,
                                'university_level': level,
                                'university_province': '',
                                'subject_type': '理科' if batch_info and batch_info.get('is_wuli') else '文科',
                                'batch_group': batch_info.get('batch_group', '') if batch_info else '',
                                'batch_name': batch_info.get('canonical_name', '') if batch_info else '',
                                'data_source': f'广东省教育考试院_2025_{batch_info.get("canonical_name","")}' if batch_info else '',
                                'is_official': True,
                                'verified': True,
                                'group_code': group_code,
                            })
                        except Exception as e:
                            continue
    except Exception as e:
        print(f'    Error parsing PDF: {e}')
    return records


def main():
    print('=' * 60)
    print('Phase 1: Download all PDFs from target pages')
    print('=' * 60)

    # Step 1: Find and download ALL PDFs from each page with unique names
    all_downloaded = {}

    for page in TARGET_PAGES:
        print(f'\n[{page["label"]}]')
        print(f'URL: {page["url"]}')

        pdf_urls, html = find_pdfs_on_page(page['url'])
        if not pdf_urls:
            # Try alternative attachment URL patterns
            post_id_match = re.search(r'post_(\d+)', page['url'])
            pid = post_id_match.group(1) if post_id_match else 'unknown'
            print(f'  No PDFs found via href scan. Trying attachment patterns...')

            # gkmlpt pattern
            gkmlpt_match = re.search(r'/content/(\d+)/(\d+)/', page['url'])
            if gkmlpt_match:
                # Try to find PDF links via known patterns
                attach_base = f'{BASE}/gkmlpt/attach/-/'
                alt_url = f'{BASE}/gkmlpt/content/4/{gkmlpt_match.group(2)}/'
                try:
                    r2 = session.get(alt_url, timeout=15)
                    r2.encoding = 'utf-8'
                    extra_pdfs = re.findall(r'href="([^"]*\.pdf)"', r2.text, re.IGNORECASE)
                    for ep in extra_pdfs:
                        full = ep if ep.startswith('http') else f'{BASE}{ep}'
                        if full not in pdf_urls:
                            pdf_urls.append(full)
                except:
                    pass

        if pdf_urls:
            print(f'  Found {len(pdf_urls)} PDF(s):')
            for i, u in enumerate(pdf_urls):
                # Generate unique temp name: post_id + index
                post_id_match = re.search(r'post_(\d+)', page['url'])
                pid = post_id_match.group(1) if post_id_match else 'unknown'

                # Try to extract a unique identifier from the URL
                url_parts = u.split('/')
                # Get the last part as unique identifier
                unique_part = url_parts[-1]
                if not unique_part.endswith('.pdf'):
                    unique_part = url_parts[-2] + '_' + url_parts[-1] if len(url_parts) > 2 else f'pdf_{i}'

                temp_name = f'_temp_{pid}_{i:02d}_{unique_part}'
                if not temp_name.endswith('.pdf'):
                    temp_name += '.pdf'

                print(f'    [{i}] {u}')
                result = download_pdf(u, temp_name)
                if result:
                    all_downloaded[result] = {
                        'page_label': page['label'],
                        'batch_group': page['batch_group'],
                        'pdf_url': u,
                        'index': i,
                    }
        else:
            print(f'  No PDFs found!')

    print(f'\nTotal downloaded: {len(all_downloaded)} PDFs')

    # Step 2: Parse each PDF to identify content
    print(f'\n{"="*60}')
    print('Phase 2: Identifying each PDF content from first page')
    print('=' * 60)

    identified = []
    for pdf_path_str, meta in all_downloaded.items():
        pdf_path = Path(pdf_path_str)
        print(f'\n--- {pdf_path.name} ---')
        print(f'  From: {meta["page_label"]}')

        batch_info = identify_batch_from_pdf(pdf_path_str)
        if batch_info:
            group, canonical = get_canonical_name(batch_info)
            print(f'  Identified: group={group}, name={canonical}')
            identified.append({
                'path': pdf_path_str,
                'meta': meta,
                'batch_info': batch_info,
                'canonical_group': group,
                'canonical_name': canonical,
            })
        else:
            # Keep original, use page label for naming
            group = meta['batch_group']
            canonical = f'{group}_{meta["page_label"]}_{meta["index"]}'
            print(f'  Could not identify. Using: {canonical}')
            identified.append({
                'path': pdf_path_str,
                'meta': meta,
                'batch_info': None,
                'canonical_group': group,
                'canonical_name': canonical,
            })

    # Step 3: Rename PDFs with correct batch names
    print(f'\n{"="*60}')
    print('Phase 3: Renaming PDFs with correct batch names')
    print('=' * 60)

    renamed_map = {}

    # Count duplicates to handle them
    name_counter = Counter()
    for item in identified:
        name_counter[item['canonical_name']] += 1

    for item in identified:
        old_path = Path(item['path'])
        canonical_name = item['canonical_name']

        # Handle duplicates by appending number
        if name_counter.get(canonical_name, 0) > 1:
            count = 1
            unique_name = f'{canonical_name}_{count}'
            while unique_name in renamed_map.values() or (RAW_DIR / f'{unique_name}.pdf').exists():
                count += 1
                unique_name = f'{canonical_name}_{count}'
            canonical_name = unique_name

        # Sanitize filename
        safe_name = canonical_name.replace('/', '_').replace('\\', '_').replace(':', '_')
        safe_name = re.sub(r'[<>"|?*]', '_', safe_name)
        new_filename = f'2025_{safe_name}.pdf'

        # Check if a file with this meaningful name already exists
        existing = [f for f in RAW_DIR.glob(f'2025_{canonical_name}*.pdf')]
        if existing and item['batch_info']:
            new_filename = f'2025_{safe_name}_from_{old_path.stem.replace("_temp_","")}.pdf'

        new_path = RAW_DIR / new_filename

        if new_path.exists():
            if new_path.stat().st_size > 5000:
                print(f'  SKIP: {new_filename} (already exists with content)')
                renamed_map[str(new_path)] = item
                continue

        try:
            os.rename(str(old_path), str(new_path))
            print(f'  {old_path.name}')
            print(f'    -> {new_filename}')
            renamed_map[str(new_path)] = item
        except Exception as e:
            print(f'  FAIL: {e}')
            renamed_map[str(old_path)] = item

    print(f'\nRenamed: {len(renamed_map)} PDFs')

    # Step 4: Parse all PDFs and import data
    print(f'\n{"="*60}')
    print('Phase 4: Parsing and importing all PDF data')
    print('=' * 60)

    # Load current data
    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    existing_records = data.get('major_rank_data', [])
    print(f'Current records: {len(existing_records):,}')

    # Create set of existing keys to deduplicate
    existing_keys = set()
    for r in existing_records:
        if isinstance(r, dict):
            key = (
                r.get('year', ''),
                r.get('province', ''),
                r.get('university_name', ''),
                r.get('group_code', ''),
                r.get('batch_name', ''),
            )
            existing_keys.add(key)

    all_new_records = []
    total_parsed = 0

    for pdf_path_str, item in renamed_map.items():
        pdf_path = Path(pdf_path_str)
        if not pdf_path.exists():
            continue

        batch_info = item.get('batch_info', {})
        print(f'\nParsing: {pdf_path.name}')

        records = parse_pdf_data(str(pdf_path), batch_info)
        new_records = 0
        for r in records:
            key = (
                r.get('year', ''),
                r.get('province', ''),
                r.get('university_name', ''),
                r.get('group_code', ''),
                r.get('batch_name', ''),
            )
            if key not in existing_keys:
                existing_keys.add(key)
                all_new_records.append(r)
                new_records += 1

        print(f'  Parsed {len(records)} records, {new_records} new')
        total_parsed += len(records)

    print(f'\nTotal parsed: {total_parsed}, New unique: {len(all_new_records)}')

    if all_new_records:
        # Backup
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.copy2(MAIN_FILE, BACKUP_DIR / f'major_rank_data_{ts}.json')
        print(f'Backup: major_rank_data_{ts}.json')

        # Merge
        merged = existing_records + all_new_records
        data['major_rank_data'] = merged
        data['metadata']['total_records'] = len(merged)
        data['metadata']['last_updated'] = datetime.now().isoformat()
        data['metadata']['last_import'] = '2025 batch PDFs comprehensive import'

        with open(MAIN_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'Merged! Total records: {len(merged):,}')
    else:
        print('No new records to add. Data may already be up to date.')

    # Step 5: Summary
    print(f'\n{"="*60}')
    print('Files in raw directory:')
    print('=' * 60)
    for f in sorted(RAW_DIR.glob('2025_*.pdf')):
        size = f.stat().st_size / 1024
        print(f'  {f.name} ({size:.1f} KB)')

    # Batch statistics
    batches = Counter()
    for r in all_new_records:
        batches[r.get('batch_name', 'unknown')] += 1
    print(f'\nNew records by batch:')
    for b, c in batches.most_common():
        print(f'  {b}: {c:,}')


if __name__ == '__main__':
    main()
