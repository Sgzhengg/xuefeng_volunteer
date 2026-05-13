# -*- coding: utf-8 -*-
"""Parse 2023 and 2024 Guangdong Gaokao PDFs and import to major_rank_data.json"""
import os, sys, json, shutil, pdfplumber, io
from pathlib import Path
from datetime import datetime
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = Path(r'd:\xuefeng_volunteer\backend')
DATA_DIR = BASE_DIR / 'data'
MAIN_DATA_FILE = DATA_DIR / 'major_rank_data.json'
BACKUP_DIR = DATA_DIR / 'backups'

# Find PDFs by name pattern or size
def find_pdfs(directory, year):
    """Find physics and history PDFs in directory"""
    result = {'物理': None, '历史': None}
    path = Path(directory)
    pdfs_sorted = sorted(path.glob('*.pdf'), key=lambda f: f.stat().st_size, reverse=True)

    for f in pdfs_sorted:
        name = f.name
        # Try by name
        if '物理' in name:
            result['物理'] = str(f)
        elif '历史' in name:
            result['历史'] = str(f)

    # Fallback by size: largest = Physics, second = History
    if not result['物理'] and len(pdfs_sorted) >= 1:
        result['物理'] = str(pdfs_sorted[0])
    if not result['历史'] and len(pdfs_sorted) >= 2:
        result['历史'] = str(pdfs_sorted[1])

    return result

def parse_pdf_table(pdf_path, year, category):
    """Parse a single PDF and extract records"""
    print(f'\n[PDF] Parsing: {pdf_path}')
    records = []
    stats = {'pages': 0, 'tables': 0, 'rows_parsed': 0, 'rows_skipped': 0}

    with pdfplumber.open(pdf_path) as pdf:
        stats['pages'] = len(pdf.pages)
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            stats['tables'] += len(tables)

            for table_idx, table in enumerate(tables):
                for row_idx, row in enumerate(table):
                    if not row or len(row) < 5:
                        stats['rows_skipped'] += 1
                        continue

                    try:
                        # Actual Guangdong PDF format columns (7 cols):
                        # 0: 院校代码, 1: 院校名称, 2: 专业组代码,
                        # 3: 计划数, 4: 投档数, 5: 投档最低分, 6: 投档最低排位
                        uni_code = str(row[0] if len(row) > 0 else '').strip()
                        uni_name = str(row[1] if len(row) > 1 else '').strip()
                        group_code = str(row[2] if len(row) > 2 else '').strip()

                        # Skip header rows - check uni_code (col 0) for header text
                        if not uni_name or uni_name in ('院校名称', '院校代码', '', '序号'):
                            continue
                        if uni_code in ('院校代码', ''):
                            continue
                        if uni_name.replace(' ', '').replace('\n', '') == '':
                            continue

                        # col 5 = min_score, col 6 = min_rank
                        min_score = 0
                        min_rank = 0

                        if len(row) > 5 and row[5]:
                            try:
                                val = str(row[5]).strip().replace(',', '').replace(' ', '')
                                if val and val.isdigit():
                                    v = int(val)
                                    if 200 <= v <= 750:
                                        min_score = v
                            except (ValueError, AttributeError):
                                pass

                        if len(row) > 6 and row[6]:
                            try:
                                val = str(row[6]).strip().replace(',', '').replace(' ', '')
                                if val and val.isdigit():
                                    v = int(val)
                                    if 1 <= v <= 500000:
                                        min_rank = v
                            except (ValueError, AttributeError):
                                pass

                        if min_rank <= 0:
                            stats['rows_skipped'] += 1
                            continue

                        # University classification
                        uni_level = get_university_level(uni_name)
                        uni_province = get_province_from_name(uni_name)

                        subject_type = '理科' if category == '物理' else '文科'

                        record = {
                            'year': year,
                            'province': '广东',
                            'university_name': uni_name,
                            'major_name': f'专业组{group_code}' if group_code else '未分类',
                            'min_rank': min_rank,
                            'min_score': min_score,
                            'university_level': uni_level,
                            'university_province': uni_province,
                            'subject_type': subject_type,
                            'data_source': f'广东省教育考试院_{year}_官方PDF',
                            'is_official': True,
                            'verified': True,
                            'group_code': group_code,
                        }
                        records.append(record)
                        stats['rows_parsed'] += 1

                    except (ValueError, IndexError, AttributeError) as e:
                        stats['rows_skipped'] += 1
                        if stats['rows_skipped'] <= 3:
                            pass  # Just skip

    print(f'  Pages: {stats["pages"]}, Tables: {stats["tables"]}')
    print(f'  Rows parsed: {stats["rows_parsed"]}, Skipped: {stats["rows_skipped"]}')
    return records

# University classification data
KNOWN_985 = {
    '北京大学', '清华大学', '复旦大学', '上海交通大学', '浙江大学',
    '中国科学技术大学', '南京大学', '中国人民大学', '中山大学',
    '华南理工大学', '武汉大学', '华中科技大学', '西安交通大学',
    '哈尔滨工业大学', '北京师范大学', '南开大学', '天津大学',
    '同济大学', '东南大学', '厦门大学', '四川大学', '电子科技大学',
    '吉林大学', '东北大学', '大连理工大学', '山东大学',
    '中国海洋大学', '西北工业大学', '兰州大学', '北京航空航天大学',
    '北京理工大学', '中国农业大学', '国防科技大学', '中央民族大学',
    '华东师范大学', '中南大学', '湖南大学', '重庆大学', '西北农林科技大学',
}

KNOWN_211 = {
    '暨南大学', '华南师范大学', '北京邮电大学', '北京交通大学',
    '北京科技大学', '北京化工大学', '北京工业大学', '北京林业大学',
    '北京中医药大学', '北京外国语大学', '中国传媒大学',
    '中央财经大学', '对外经济贸易大学', '中国政法大学',
    '华北电力大学', '中国矿业大学', '中国石油大学',
    '中国地质大学', '东北师范大学', '东北林业大学',
    '华东理工大学', '东华大学', '上海外国语大学', '上海财经大学',
    '上海大学', '苏州大学', '南京航空航天大学', '南京理工大学',
    '中国药科大学', '河海大学', '江南大学', '南京农业大学',
    '南京师范大学', '合肥工业大学', '安徽大学', '福州大学',
    '南昌大学', '郑州大学', '武汉理工大学',
    '华中师范大学', '华中农业大学', '中南财经政法大学',
    '湖南师范大学', '西南交通大学', '四川农业大学',
    '西南大学', '西南财经大学', '贵州大学', '云南大学',
    '西藏大学', '西北大学', '西安电子科技大学', '长安大学',
    '陕西师范大学', '青海大学', '宁夏大学', '新疆大学',
    '石河子大学', '海南大学', '广西大学', '内蒙古大学',
    '延边大学', '辽宁大学', '大连海事大学', '太原理工大学',
    '河北工业大学', '哈尔滨工程大学', '东北农业大学',
}

PROVINCE_KEYWORDS = {
    '北京': '北京', '清华': '北京', '北大': '北京',
    '上海': '上海', '复旦': '上海', '同济': '上海',
    '天津': '天津', '南开': '天津',
    '重庆': '重庆',
    '广东': '广东', '广州': '广东', '深圳': '广东', '华南': '广东',
    '暨南': '广东', '中山': '广东', '东莞': '广东', '佛山': '广东',
    '汕头': '广东', '韶关': '广东', '惠州': '广东', '肇庆': '广东',
    '嘉应': '广东', '岭南': '广东', '五邑': '广东', '韩山': '广东',
    '广东': '广东',
    '浙江': '浙江',
    '江苏': '江苏', '南京': '江苏', '苏州': '江苏', '东南': '江苏', '河海': '江苏', '江南': '江苏',
    '湖北': '湖北', '武汉': '湖北', '华中': '湖北',
    '湖南': '湖南', '中南': '湖南',
    '四川': '四川', '电子科技': '四川', '西南交通': '四川',
    '山东': '山东', '中国海洋': '山东',
    '福建': '福建', '厦门': '福建',
    '陕西': '陕西', '西安': '陕西', '西北': '陕西', '长安': '陕西',
    '辽宁': '辽宁', '大连': '辽宁', '东北': '辽宁',
    '吉林': '吉林',
    '黑龙江': '黑龙江', '哈尔滨': '黑龙江',
    '安徽': '安徽', '中国科学技术': '安徽',
    '江西': '江西',
    '河南': '河南',
    '河北': '河北',
    '广西': '广西',
    '云南': '云南',
    '贵州': '贵州',
    '海南': '海南',
    '甘肃': '甘肃', '兰州': '甘肃',
}

def get_university_level(uni_name):
    if uni_name in KNOWN_985:
        return '985'
    if uni_name in KNOWN_211:
        return '211'
    if any(kw in uni_name for kw in ['大学']) and not any(kw in uni_name for kw in ['职业', '技术']):
        return '普通本科'
    if any(kw in uni_name for kw in ['职业', '技术', '专科']):
        return '高职'
    return '普通本科'

def get_province_from_name(uni_name):
    for keyword, province in PROVINCE_KEYWORDS.items():
        if keyword in uni_name:
            return province
    return ''

def merge_to_main(records, year):
    """Merge records into major_rank_data.json"""
    print(f'\n[Merge] Merging {len(records)} records for year {year}...')

    # Backup
    BACKUP_DIR.mkdir(exist_ok=True)
    if MAIN_DATA_FILE.exists():
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = BACKUP_DIR / f'major_rank_data_backup_{ts}.json'
        shutil.copy2(MAIN_DATA_FILE, backup_path)
        print(f'  Backed up to: {backup_path}')

    # Load existing data
    with open(MAIN_DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    existing = data.get('major_rank_data', [])
    print(f'  Existing records: {len(existing)}')

    # Remove old records for same year
    kept = [r for r in existing if isinstance(r, dict) and r.get('year') != year]
    removed = len(existing) - len(kept)
    print(f'  Removed old {year} data: {removed}')

    # Merge
    merged = kept + records
    print(f'  Merged total: {len(merged)}')

    # Save
    output = {
        'major_rank_data': merged,
        'metadata': {
            'total_records': len(merged),
            'last_updated': datetime.now().isoformat(),
            f'guangdong_{year}_source': '广东省教育考试院官方PDF',
        },
    }
    with open(MAIN_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return len(merged)

def stats_report(records, year):
    """Generate statistics for imported records"""
    print(f'\n[Stats] {year} year Guangdong data:')
    gd = [r for r in records if r.get('province') == '广东']
    print(f'  Total: {len(gd)}')
    unis = set(r['university_name'] for r in gd)
    print(f'  Universities: {len(unis)}')

    ranks = [r['min_rank'] for r in gd if r.get('min_rank')]
    if ranks:
        print(f'  Rank range: {min(ranks)} - {max(ranks)}')

    levels = defaultdict(int)
    for r in gd:
        levels[r.get('university_level', '?')] += 1
    print(f'  Levels: {dict(levels)}')

    provs = defaultdict(int)
    for r in gd:
        provs[r.get('university_province', '?')] += 1
    local = provs.pop('广东', 0)
    other = sum(provs.values())
    print(f'  Guangdong local: {local}, Out-of-province: {other}')

    physics = [r for r in gd if r.get('subject_type') == '理科']
    history = [r for r in gd if r.get('subject_type') == '文科']
    print(f'  Physics (理科): {len(physics)}, History (文科): {len(history)}')

def main():
    # Find PDFs
    data_dir = DATA_DIR

    pdfs_2024 = find_pdfs(data_dir / 'temp_2024', 2024)
    pdfs_2023 = find_pdfs(data_dir / 'temp_2023', 2023)

    print(f'2024 PDFs: Physics={pdfs_2024["物理"]}, History={pdfs_2024["历史"]}')
    print(f'2023 PDFs: Physics={pdfs_2023["物理"]}, History={pdfs_2023["历史"]}')

    # Parse all PDFs
    all_records_2024 = []
    all_records_2023 = []

    for year, pdfs, all_recs in [(2024, pdfs_2024, all_records_2024),
                                   (2023, pdfs_2023, all_records_2023)]:
        for cat in ['物理', '历史']:
            pdf_path = pdfs.get(cat)
            if pdf_path and os.path.exists(pdf_path):
                records = parse_pdf_table(pdf_path, year, cat)
                all_recs.extend(records)
                print(f'  {year} {cat}: {len(records)} records')
            else:
                print(f'  {year} {cat}: PDF NOT FOUND')

    # Show sample records
    print(f'\n[Sample] 2024 first 3 records:')
    for r in all_records_2024[:3]:
        print(f'  {r["university_name"]} | {r["major_name"]} | Score={r["min_score"]} | Rank={r["min_rank"]} | {r["subject_type"]} | Level={r["university_level"]}')

    print(f'\n[Sample] 2023 first 3 records:')
    for r in all_records_2023[:3]:
        print(f'  {r["university_name"]} | {r["major_name"]} | Score={r["min_score"]} | Rank={r["min_rank"]} | {r["subject_type"]} | Level={r["university_level"]}')

    # Stats
    stats_report(all_records_2024, 2024)
    stats_report(all_records_2023, 2023)

    # Merge
    if all_records_2024:
        merge_to_main(all_records_2024, 2024)
    if all_records_2023:
        merge_to_main(all_records_2023, 2023)

    print('\n[Done] Import complete!')

    # Also write summary to file
    with open(str(DATA_DIR / 'import_summary_2024_2023.txt'), 'w', encoding='utf-8') as rf:
        rf.write(f'Import Summary\n{"="*60}\n')
        rf.write(f'2024 records: {len(all_records_2024)}\n')
        rf.write(f'2023 records: {len(all_records_2023)}\n')
        rf.write(f'Total records in major_rank_data.json: - see file for count\n')
        rf.write(f'Timestamp: {datetime.now().isoformat()}\n')
    print('Summary written to import_summary_2024_2023.txt')

if __name__ == '__main__':
    main()
