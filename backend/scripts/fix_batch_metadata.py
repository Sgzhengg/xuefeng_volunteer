# -*- coding: utf-8 -*-
"""
Fix script:
1. Re-parse downloaded PDFs with correct batch_name info
2. Re-identify PDFs where title="院" by parsing deeper into pages
3. Try to download post 4742894 (军检院校) from zwgk URL
4. Update major_rank_data.json with correct batch metadata
"""
import requests, re, os, sys, io, json, shutil, pdfplumber
from pathlib import Path
from datetime import datetime

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


def identify_batch_from_pdf(pdf_path):
    """Parse PDF pages to identify the actual batch/subject - scan deeper"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ''
            # Read up to 5 pages to find the title
            for pg in range(min(5, len(pdf.pages))):
                text = pdf.pages[pg].extract_text() or ''
                full_text += text + '\n'

            lines = [l.strip() for l in full_text.split('\n') if l.strip()]

            # Find the actual title line - look for lines containing "广东省" and "投档"
            title = ''
            for line in lines:
                if '广东省' in line and ('投档' in line or '情况' in line):
                    title = line
                    break
            if not title:
                for line in lines:
                    if '普通类' in line or '专科' in line or '本科' in line or '艺体' in line:
                        title = line
                        break
            if not title:
                title = lines[0] if lines else ''

            print(f'      Title: {title[:120]}')

            is_zhuanke = '专科' in title
            is_tiqian = '提前批' in title
            is_zhengji = '征集' in title
            is_jiaoshi = '教师' in title
            is_weisheng = '卫生' in title
            is_junjian = '军检' in title
            is_feijunjian = '非军检' in title
            is_gaoxiaozhuanxiang = '高校专项' in title

            # Specific art categories
            art_keywords = {
                '体育': '体育',
                '音乐': '音乐',
                '舞蹈': '舞蹈',
                '美术': '美术与设计',
                '书法': '书法',
                '播音': '播音与主持',
                '表(导)': '表(导)演',
            }
            art_matched = None
            for kw, label in art_keywords.items():
                if kw in title:
                    art_matched = label
                    break

            is_yitixi = art_matched is not None

            is_wuli = '物理' in title
            is_lishi = '历史' in title

            # batch_group
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

            # category
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
            elif is_zhengji:
                category = '征集志愿'
            elif is_yitixi:
                category = '艺体'
            else:
                category = '普通类'

            # subject
            if art_matched:
                subject = art_matched
            elif is_wuli:
                subject = '物理'
            elif is_lishi:
                subject = '历史'
            else:
                subject = '综合'

            # canonical name
            if category in ('教师专项', '卫生专项'):
                canonical_name = f'{batch_group}{category}'
            elif category in ('高校专项',):
                canonical_name = f'{batch_group}高校专项计划'
            elif category in ('军检院校', '非军检院校'):
                canonical_name = f'{batch_group}{category}({subject})'
            elif category == '征集志愿':
                canonical_name = f'{batch_group}({subject})'
            elif category == '艺体':
                canonical_name = f'{batch_group}{subject}类统考'
            elif subject in ('物理', '历史', '综合'):
                canonical_name = f'{batch_group}普通类({subject})'
            else:
                canonical_name = f'{batch_group}{category}({subject})'

            return {
                'title': title,
                'batch_group': batch_group,
                'batch_name': canonical_name,
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
        print(f'      Error: {e}')
        return None


def parse_pdf_data(pdf_path, batch_info):
    """Parse PDF tables and extract admission records"""
    records = []
    bn = batch_info.get('batch_name', '') if batch_info else ''
    bg = batch_info.get('batch_group', '') if batch_info else ''
    is_wuli = batch_info.get('is_wuli', False) if batch_info else False

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
                            uni_code = str(row[0] if len(row)>0 else '').strip()
                            uni_name = str(row[1] if len(row)>1 else '').strip()
                            group_code = str(row[2] if len(row)>2 else '').strip()

                            if not uni_name or uni_code in ('院校代码',''):
                                continue
                            if not uni_code.isdigit() or len(uni_code) < 4:
                                continue

                            min_score = 0
                            for col_idx in [5, 4]:
                                if col_idx < len(row) and row[col_idx]:
                                    try:
                                        v = int(str(row[col_idx]).strip().replace(',','').replace(' ',''))
                                        if 150 <= v <= 750:
                                            min_score = v
                                            break
                                    except:
                                        pass

                            min_rank = 0
                            for col_idx in [6, 5, 7]:
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
                                'subject_type': '理科' if is_wuli or '物理' in bn else '文科',
                                'batch_group': bg,
                                'batch_name': bn,
                                'data_source': f'广东省教育考试院_2025_{bn}',
                                'is_official': True,
                                'verified': True,
                                'group_code': group_code,
                            })
                        except:
                            continue
    except Exception as e:
        print(f'    Error parsing PDF: {e}')
    return records


def find_and_download_junjian():
    """Try to find 军检院校 PDFs from the correct URL"""
    print(f'\n{"="*60}')
    print('Trying to find 军检院校 PDFs (post 4742894)')
    print('=' * 60)

    # Try various URL patterns
    urls_to_try = [
        'https://eea.gd.gov.cn/zwgk/sjfb/tjsj/content/post_4742894.html',
        'https://eea.gd.gov.cn/ptgk/content/post_4742894.html',
        'https://eea.gd.gov.cn/zwgk/content/post_4742894.html',
        'https://eea.gd.gov.cn/zwgk/sjfb/content/post_4742894.html',
    ]

    for url in urls_to_try:
        try:
            r = session.get(url, timeout=15)
            r.encoding = 'utf-8'
            print(f'  {url} -> status={r.status_code}')
            if r.status_code == 200 and len(r.text) > 200:
                pdfs = re.findall(r'href="([^"]*\.pdf)"', r.text, re.IGNORECASE)
                if pdfs:
                    print(f'  Found {len(pdfs)} PDF(s) at {url}')
                    for i, pdf_url in enumerate(pdfs):
                        full = pdf_url if pdf_url.startswith('http') else f'{BASE}{pdf_url}'
                        temp_name = f'_temp_4742894_{i:02d}.pdf'
                        out = RAW_DIR / temp_name
                        if out.exists():
                            continue
                        dr = session.get(full, timeout=120)
                        if dr.status_code == 200 and len(dr.content) > 5000:
                            with open(out, 'wb') as f:
                                f.write(dr.content)
                            print(f'    [OK] {temp_name} ({len(dr.content)/1024:.1f} KB)')
                    return True
                else:
                    # Check attachment patterns
                    attach_links = re.findall(r'(/attachment/[^\s"\'<>]+\.pdf)', r.text, re.IGNORECASE)
                    if attach_links:
                        print(f'  Found {len(attach_links)} attachment(s) at {url}')
                        for i, a in enumerate(attach_links):
                            full = f'{BASE}{a}'
                            temp_name = f'_temp_4742894_{i:02d}.pdf'
                            out = RAW_DIR / temp_name
                            if out.exists():
                                continue
                            dr = session.get(full, timeout=120)
                            if dr.status_code == 200 and len(dr.content) > 5000:
                                with open(out, 'wb') as f:
                                    f.write(dr.content)
                                print(f'    [OK] {temp_name} ({len(dr.content)/1024:.1f} KB)')
                        return True
        except Exception as e:
            print(f'  Error: {e}')

    print('  Could not access 军检院校 post.')
    return False


def main():
    # Step 1: Find all PDFs in raw directory
    all_pdfs = []
    for pattern in ['*.pdf']:
        all_pdfs.extend(RAW_DIR.glob(pattern))

    # Exclude obviously correct files and focus on ones that need fixing
    to_reprocess = []
    for f in all_pdfs:
        name = f.name
        # Files that need re-identification or were given wrong names
        if '未知' in name or '_from_' in name or name.startswith('_temp_'):
            to_reprocess.append((f, True))  # re-identify
        elif '普通类' not in name and '统考' not in name and '专项' not in name and '军检' not in name and '征集' not in name and '高校专项' not in name:
            to_reprocess.append((f, True))  # unknown type
        else:
            to_reprocess.append((f, False))  # keep current identification

    # Step 2: Re-identify and re-parse all PDFs
    print('=' * 60)
    print('Phase 1: Re-identifying and parsing all PDFs')
    print('=' * 60)

    all_records = []

    for pdf_path, needs_reid in to_reprocess:
        print(f'\n--- {pdf_path.name} ---')
        batch_info = identify_batch_from_pdf(str(pdf_path))
        if batch_info:
            canon = batch_info.get('batch_name', 'unknown')
            print(f'  Batch: {canon}')
            records = parse_pdf_data(str(pdf_path), batch_info)
            print(f'  Records: {len(records)}')
            all_records.extend(records)

            # Rename if needed
            safe_name = canon.replace('/', '_').replace('(', '(').replace(')', ')')
            safe_name = re.sub(r'[<>"|?*:]', '_', safe_name)
            expected_name = f'2025_{safe_name}.pdf'
            if pdf_path.name != expected_name and pdf_path.name != expected_name.replace('_1', ''):
                new_path = pdf_path.parent / expected_name
                if new_path.exists():
                    # Add counter
                    counter = 1
                    while new_path.exists():
                        counter += 1
                        new_path = pdf_path.parent / f'2025_{safe_name}_{counter}.pdf'
                try:
                    os.rename(str(pdf_path), str(new_path))
                    print(f'  Renamed: {pdf_path.name} -> {new_path.name}')
                except Exception as e:
                    print(f'  Rename failed: {e}')
        else:
            print(f'  Could not identify. Size: {pdf_path.stat().st_size/1024:.1f} KB')

    # Step 3: Try to get 军检院校 PDFs
    found_junjian = find_and_download_junjian()

    # Step 4: Process any new temp files
    for tempf in sorted(RAW_DIR.glob('_temp_*.pdf')):
        print(f'\n--- {tempf.name} (downloaded) ---')
        batch_info = identify_batch_from_pdf(str(tempf))
        if batch_info:
            canon = batch_info.get('batch_name', 'unknown')
            print(f'  Batch: {canon}')
            records = parse_pdf_data(str(tempf), batch_info)
            print(f'  Records: {len(records)}')
            all_records.extend(records)

            safe_name = canon.replace('/', '_')
            safe_name = re.sub(r'[<>"|?*:]', '_', safe_name)
            new_name = RAW_DIR / f'2025_{safe_name}.pdf'
            if new_name.exists():
                new_name = RAW_DIR / f'2025_{safe_name}_2.pdf'
            os.rename(str(tempf), str(new_name))
            print(f'  Renamed: {new_name.name}')

    print(f'\n\nTotal records parsed: {len(all_records)}')

    # Step 5: Merge with existing data
    print(f'\n{"="*60}')
    print('Phase 2: Merging data')
    print('=' * 60)

    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    existing = data.get('major_rank_data', [])

    # Remove ALL bad records (2025 with empty batch_name) first
    bad_count = 0
    cleaned = []
    for r in existing:
        if isinstance(r, dict) and r.get('year') == 2025 and not r.get('batch_name', ''):
            bad_count += 1
        else:
            cleaned.append(r)
    print(f'Removed {bad_count} bad records (empty batch_name, 2025)')
    existing = cleaned

    # Build dedup keys from remaining good records
    existing_keys = set()
    for r in existing:
        if isinstance(r, dict):
            key = (
                str(r.get('year', '')),
                str(r.get('province', '')),
                str(r.get('university_name', '')),
                str(r.get('group_code', '')),
            )
            existing_keys.add(key)

    new_count = 0
    for r in all_records:
        key = (
            str(r.get('year', '')),
            str(r.get('province', '')),
            str(r.get('university_name', '')),
            str(r.get('group_code', '')),
        )
        if key not in existing_keys:
            existing_keys.add(key)
            existing.append(r)
            new_count += 1

    # Backup
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy2(MAIN_FILE, BACKUP_DIR / f'major_rank_data_{ts}.json')

    data['major_rank_data'] = existing
    data['metadata']['total_records'] = len(existing)
    data['metadata']['last_updated'] = datetime.now().isoformat()

    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'New records added: {new_count}')
    print(f'Total records: {len(existing):,}')

    # Print batch stats
    from collections import Counter
    batch_counts = Counter()
    for r in existing:
        if isinstance(r, dict) and r.get('year') == 2025:
            batch_counts[r.get('batch_name', 'unknown')] += 1

    print(f'\nBatch distribution (2025 only):')
    for b, c in batch_counts.most_common():
        print(f'  {b}: {c:,}')


if __name__ == '__main__':
    main()
