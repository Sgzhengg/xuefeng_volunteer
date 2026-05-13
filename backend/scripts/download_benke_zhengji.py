# -*- coding: utf-8 -*-
"""
Download and import 本科征集志愿 PDFs from 3 found posts.
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

# 本科征集志愿 posts
TARGETS = [
    {
        'url': 'https://eea.gd.gov.cn/gkmlpt/content/4/4750/mpost_4750002.html',
        'label': '本科第一次征集志愿',
        'round': '第一次',
    },
    {
        'url': 'https://eea.gd.gov.cn/gkmlpt/content/4/4751/post_4751672.html',
        'label': '本科第二次征集志愿',
        'round': '第二次',
    },
    {
        'url': 'https://eea.gd.gov.cn/gkmlpt/content/4/4753/post_4753101.html',
        'label': '本科第三次征集志愿',
        'round': '第三次',
    },
]


def download_pdf(pdf_url, temp_name):
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
    """Parse PDF pages to identify the actual batch/subject"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ''
            for pg in range(min(5, len(pdf.pages))):
                text = pdf.pages[pg].extract_text() or ''
                full_text += text + '\n'
            lines = [l.strip() for l in full_text.split('\n') if l.strip()]

            title = ''
            for line in lines:
                if '广东省' in line and ('投档' in line or '情况' in line):
                    title = line
                    break
            if not title:
                for line in lines:
                    if '普通类' in line or '体育' in line or '艺术' in line:
                        title = line
                        break
            if not title:
                title = lines[0] if lines else ''

            print(f'      Title: {title[:120]}')

            is_zhengji = '征集' in title
            is_wuli = '物理' in title
            is_lishi = '历史' in title

            art_keywords = {
                '体育': '体育', '音乐': '音乐', '舞蹈': '舞蹈',
                '美术': '美术与设计', '书法': '书法',
                '播音': '播音与主持', '表(导)': '表(导)演',
            }
            art_matched = None
            for kw, label in art_keywords.items():
                if kw in title:
                    art_matched = label
                    break

            if art_matched:
                batch_name = f'本科征集志愿({art_matched})'
                is_wuli_effective = False
            elif is_wuli:
                batch_name = '本科征集志愿(物理)'
                is_wuli_effective = True
            elif is_lishi:
                batch_name = '本科征集志愿(历史)'
                is_wuli_effective = False
            else:
                batch_name = '本科征集志愿(综合)'
                is_wuli_effective = False

            return {
                'title': title,
                'batch_group': '本科征集志愿',
                'batch_name': batch_name,
                'is_wuli': is_wuli_effective,
                'is_zhengji': is_zhengji,
            }
    except Exception as e:
        print(f'      Error: {e}')
    return None


def parse_pdf_data(pdf_path, batch_info):
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
                                'year': 2025, 'province': '广东',
                                'university_name': uni_name,
                                'major_name': f'专业组{group_code}' if group_code else '未分类',
                                'min_rank': min_rank, 'min_score': min_score,
                                'university_level': level, 'university_province': '',
                                'subject_type': '理科' if is_wuli else '文科',
                                'batch_group': bg, 'batch_name': bn,
                                'data_source': f'广东省教育考试院_2025_{bn}',
                                'is_official': True, 'verified': True,
                                'group_code': group_code,
                            })
                        except:
                            continue
    except Exception as e:
        print(f'    Error parsing PDF: {e}')
    return records


def main():
    all_records = []

    for target in TARGETS:
        print(f'\n{"="*60}')
        print(f'[{target["label"]}]')
        print(f'URL: {target["url"]}')
        print(f'{"="*60}')

        # Find and download PDFs
        try:
            r = session.get(target['url'], timeout=30)
            r.encoding = 'utf-8'
            html = r.text
            print(f'  Status: {r.status_code}, Length: {len(html)}')

            pdfs = re.findall(r'href="([^"]*\.pdf)"', html, re.IGNORECASE)
            if not pdfs:
                pdfs = re.findall(r'href="([^"]*\.PDF)"', html, re.IGNORECASE)

            if pdfs:
                print(f'  Found {len(pdfs)} PDF(s)')

                for i, pdf_url in enumerate(pdfs):
                    full = pdf_url if pdf_url.startswith('http') else f'{BASE}{pdf_url}'
                    pid = re.search(r'post[_-]?(\d+)', target['url'])
                    pid_str = pid.group(1) if pid else 'unknown'
                    temp_name = f'_temp_benke_zj_{pid_str}_{i:02d}.pdf'

                    result = download_pdf(full, temp_name)
                    if result:
                        batch_info = identify_batch_from_pdf(result)
                        if batch_info:
                            records = parse_pdf_data(result, batch_info)
                            print(f'  Parsed {len(records)} records')
                            all_records.extend(records)

                            # Rename
                            canon = batch_info['batch_name']
                            safe = canon.replace('/', '_').replace('(', '(').replace(')', ')')
                            safe = re.sub(r'[<>"|?*:]', '_', safe)
                            new_path = RAW_DIR / f'2025_{safe}_{target["round"]}.pdf'
                            try:
                                os.rename(result, str(new_path))
                                print(f'  -> {new_path.name}')
                            except:
                                pass
            else:
                print(f'  No PDFs found')
        except Exception as e:
            print(f'  Error: {e}')

    print(f'\n\nTotal records parsed: {len(all_records)}')

    if not all_records:
        print('No records to import.')
        return

    # Merge with existing data
    print(f'\n{"="*60}')
    print('Merging data')
    print('=' * 60)

    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    existing = data.get('major_rank_data', [])

    existing_keys = set()
    for r in existing:
        if isinstance(r, dict):
            key = (str(r.get('year','')), str(r.get('province','')),
                   str(r.get('university_name','')), str(r.get('group_code','')))
            existing_keys.add(key)

    new_count = 0
    for r in all_records:
        key = (str(r.get('year','')), str(r.get('province','')),
               str(r.get('university_name','')), str(r.get('group_code','')))
        if key not in existing_keys:
            existing_keys.add(key)
            existing.append(r)
            new_count += 1

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy2(MAIN_FILE, BACKUP_DIR / f'major_rank_data_{ts}.json')

    data['major_rank_data'] = existing
    data['metadata']['total_records'] = len(existing)
    data['metadata']['last_updated'] = datetime.now().isoformat()

    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'New records: {new_count}')
    print(f'Total: {len(existing):,}')


if __name__ == '__main__':
    main()
