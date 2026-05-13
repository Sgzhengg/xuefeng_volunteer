# -*- coding: utf-8 -*-
"""
广东省教育考试院 - 2025年全批次投档数据验证与补充采集

检查当前数据库是否覆盖了所有官方发布的投档批次，
生成缺失批次报告和补充采集任务清单。
"""
import json, os, sys, io
from pathlib import Path
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = Path(r'd:\xuefeng_volunteer\backend\data')
MAIN_FILE = DATA_DIR / 'major_rank_data.json'

# 2025年广东省教育考试院预期发布批次
EXPECTED_BATCHES_2025 = [
    {
        "batch_group": "提前批本科",
        "batches": [
            {"name": "空军海军招飞", "category": "特殊类型"},
            {"name": "提前批本科普通类（物理）", "category": "物理", "type": "普通类"},
            {"name": "提前批本科普通类（历史）", "category": "历史", "type": "普通类"},
            {"name": "提前批本科艺体类", "category": "艺体", "type": "艺体类"},
            {"name": "提前批本科教师专项", "category": "教师专项", "type": "专项"},
            {"name": "提前批本科卫生专项", "category": "卫生专项", "type": "专项"},
        ]
    },
    {
        "batch_group": "本科批",
        "batches": [
            {"name": "本科普通类（物理）", "category": "物理", "type": "普通类"},
            {"name": "本科普通类（历史）", "category": "历史", "type": "普通类"},
            {"name": "本科艺体类统考", "category": "艺体", "type": "艺体类"},
        ]
    },
    {
        "batch_group": "本科征集志愿",
        "batches": [
            {"name": "本科第一次征集志愿（物理）", "category": "物理", "type": "征集志愿"},
            {"name": "本科第一次征集志愿（历史）", "category": "历史", "type": "征集志愿"},
            {"name": "本科第二次征集志愿（物理）", "category": "物理", "type": "征集志愿"},
            {"name": "本科第二次征集志愿（历史）", "category": "历史", "type": "征集志愿"},
        ]
    },
    {
        "batch_group": "提前批专科",
        "batches": [
            {"name": "提前批专科普通类（物理）", "category": "物理", "type": "普通类"},
            {"name": "提前批专科普通类（历史）", "category": "历史", "type": "普通类"},
            {"name": "提前批专科卫生专项", "category": "卫生专项", "type": "专项"},
        ]
    },
    {
        "batch_group": "专科批",
        "batches": [
            {"name": "专科普通类（物理）", "category": "物理", "type": "普通类"},
            {"name": "专科普通类（历史）", "category": "历史", "type": "普通类"},
            {"name": "专科艺体类统考", "category": "艺体", "type": "艺体类"},
        ]
    },
    {
        "batch_group": "专科征集志愿",
        "batches": [
            {"name": "专科第一次征集志愿（物理）", "category": "物理", "type": "征集志愿"},
            {"name": "专科第一次征集志愿（历史）", "category": "历史", "type": "征集志愿"},
        ]
    },
    {
        "batch_group": "特殊类型招生",
        "batches": [
            {"name": "强基计划", "category": "特殊类型", "type": "特殊类型"},
            {"name": "综合评价", "category": "特殊类型", "type": "特殊类型"},
            {"name": "高校专项计划", "category": "特殊类型", "type": "特殊类型"},
        ]
    },
]


def load_current_data():
    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['major_rank_data']


def analyze_collected_batches(records):
    """Analyze what batches are in current data using batch_name field"""
    yr2025 = [r for r in records if isinstance(r, dict) and r.get('year') == 2025
              and r.get('province') == '广东']

    collected_batch_names = set()
    for r in yr2025:
        bn = r.get('batch_name', '')
        ds = r.get('data_source', '')
        un = r.get('university_name', '')
        if bn:
            collected_batch_names.add(bn)
        # Detect 招飞 from records
        if '招飞' in ds or '招飞' in bn:
            collected_batch_names.add('空军海军招飞')
        # Detect招飞 from known aviation schools
        if un in ('空军航空大学', '海军航空大学'):
            collected_batch_names.add('空军海军招飞')

    return collected_batch_names


def detect_currently_have(batch_name, collected_batch_names):
    """Check if a specific expected batch is covered by actual batch_name values"""
    # Check if any collected batch matches this expected batch
    for collected in collected_batch_names:
        if batch_matches(collected, batch_name):
            return True
    return False


def batch_matches(collected_batch, expected_batch):
    """Check if a collected batch_name matches an expected batch"""
    ce = collected_batch
    ex = expected_batch

    # Direct match
    if ce == ex:
        return True

    # Fuzzy matching based on batch group + category
    # 本科普通类（物理）matches 本科批普通类(物理) etc
    ex_normalized = ex.replace('（', '(').replace('）', ')').replace(' ', '')

    if ce == ex_normalized:
        return True

    # Split batches: 本科艺体类统考 matches 本科批体育类统考, 本科批音乐类统考, etc.
    if ex == '本科艺体类统考' and '本科批' in ce and ('体育' in ce or '音乐' in ce or '舞蹈' in ce
            or '美术' in ce or '书法' in ce or '播音' in ce or '表(' in ce):
        return True

    if ex == '专科艺体类统考' and '专科批' in ce and ('体育' in ce or '音乐' in ce or '舞蹈' in ce
            or '美术' in ce or '书法' in ce or '播音' in ce or '表(' in ce):
        return True

    # 提前批本科教师专项 -> matches any 提前批本科 + 教师专项
    if '教师专项' in ex and '教师专项' in ce and '提前批' in ce:
        return True

    # 提前批本科卫生专项
    if '卫生专项' in ex and '卫生专项' in ce and '提前批 本科' in ce.replace('批', '批 '):
        return True

    if '卫生专项' in ex and '卫生专项' in ce and '本科' in ce and '提前批' in ce:
        return True

    # 提前批专科卫生专项
    if '卫生专项' in ex and '卫生专项' in ce and '专科' in ce and '提前批' in ce:
        return True

    # 提前批本科普通类(物理/历史)
    if '提前批本科普通类' in ex and '提前批本科' in ce and '普通类' in ce:
        # Check subject match
        if '物理' in ex and '物理' in ce:
            return True
        if '历史' in ex and '历史' in ce:
            return True

    # 提前批专科普通类(物理/历史)
    if '提前批专科普通类' in ex and '提前批专科' in ce:
        if '物理' in ex and '物理' in ce:
            return True
        if '历史' in ex and '历史' in ce:
            return True

    # 高校专项计划
    if '高校专项计划' in ex and '高校专项' in ce:
        return True

    # 空军海军招飞
    if '招飞' in ex and '招飞' in ce:
        return True

    # 征集志愿 matching
    if '征集志愿' in ex and '征集' in ce:
        ex_subject = ''
        if '物理' in ex: ex_subject = '物理'
        elif '历史' in ex: ex_subject = '历史'
        ex_group = '本科' if '本科' in ex else '专科' if '专科' in ex else ''

        c_subject = ''
        if '物理' in ce: c_subject = '物理'
        elif '历史' in ce: c_subject = '历史'
        c_group = '本科' if '本科' in ce else '专科' if '专科' in ce else ''

        if ex_subject and c_subject and ex_subject == c_subject:
            if ex_group and c_group and ex_group == c_group:
                return True

    # General keyword matching fallback - only for batch types we're confident about
    ex_keywords = ex.replace('（', '(').replace('）', ')')

    # Only use fallback if the expected batch has identifiable keywords
    fallback_kws_1 = [kw for kw in ['物理', '普通类', '本科'] if kw in ex_keywords]
    fallback_kws_2 = [kw for kw in ['历史', '普通类', '本科'] if kw in ex_keywords]

    if fallback_kws_1 and all(kw in ce for kw in fallback_kws_1):
        if '提前批' not in ex_keywords or '提前批' in ce:
            if '征集' not in ex_keywords or '征集' in ce:
                return True
    if fallback_kws_2 and all(kw in ce for kw in fallback_kws_2):
        if '提前批' not in ex_keywords or '提前批' in ce:
            if '征集' not in ex_keywords or '征集' in ce:
                return True

    return False


def generate_report():
    records = load_current_data()
    collected = analyze_collected_batches(records)

    lines = []
    lines.append("=" * 70)
    lines.append("广东省2025年高考投档批次 - 数据完整度检查报告")
    lines.append("=" * 70)

    # Current coverage summary
    lines.append(f"\n当前数据概况:")
    lines.append(f"  总记录数: {len(records):,}")
    yd = Counter(r.get('year') for r in records if isinstance(r, dict))
    for yr in sorted(yd.keys()):
        gd_count = sum(1 for r in records if isinstance(r, dict) and r.get('year') == yr and r.get('province') == '广东')
        lines.append(f"  {yr}年广东数据: {gd_count:,} 条")

    lines.append(f"\n当前已覆盖批次 (batch_name values):")
    for bn in sorted(collected):
        lines.append(f"  - {bn}")

    # Check all expected batches
    total_expected = 0
    total_collected = 0
    all_missing = []

    lines.append(f"\n{'='*70}")
    lines.append("逐批次检查结果")
    lines.append(f"{'='*70}")

    for group in EXPECTED_BATCHES_2025:
        lines.append(f"\n--- {group['batch_group']} ---")
        for b in group['batches']:
            total_expected += 1
            have = detect_currently_have(b['name'], collected)
            if have:
                total_collected += 1
                lines.append(f"  [COLLECTED] {b['name']}")
            else:
                all_missing.append({"group": group['batch_group'], **b})
                lines.append(f"  [MISSING ] {b['name']} ({b.get('type', '?')})")

    # Summary
    lines.append(f"\n{'='*70}")
    lines.append(f"汇总")
    lines.append(f"{'='*70}")
    lines.append(f"  预期批次数: {total_expected}")
    lines.append(f"  已采集: {total_collected}")
    lines.append(f"  缺失: {len(all_missing)}")
    coverage_pct = total_collected / total_expected * 100 if total_expected > 0 else 0
    lines.append(f"  覆盖率: {coverage_pct:.1f}%")

    # Missing batches priority
    if all_missing:
        lines.append(f"\n优先补充建议:")
        priority_order = ['本科批', '提前批本科', '专科批', '本科征集志愿', '提前批专科', '特殊类型招生', '专科征集志愿']
        for p in priority_order:
            missing_in_group = [m for m in all_missing if m['group'] == p]
            if missing_in_group:
                lines.append(f"  1. [{p}] - {len(missing_in_group)} 个子批次缺失")

    report = "\n".join(lines)
    return report, all_missing


def main():
    report, all_missing = generate_report()

    # Print to console
    print(report)

    # Save report
    report_file = DATA_DIR / 'batch_completeness_report_2025.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存: {report_file}")

    # Save missing tasks JSON
    if all_missing:
        task_file = DATA_DIR / 'missing_batches_tasks_2025.json'
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(all_missing, f, ensure_ascii=False, indent=2)
        print(f"缺失批次任务清单: {task_file} ({len(all_missing)} 项)")

    # Also generate manual download guide
    guide_lines = []
    guide_lines.append("=" * 70)
    guide_lines.append("需要手动下载的PDF/XLSX文件清单")
    guide_lines.append("=" * 70)
    guide_lines.append("")
    guide_lines.append("访问广东省教育考试院官网: https://eea.gd.gov.cn/")
    guide_lines.append("在「通知公告」或「普通高考」栏目中搜索以下关键词：")
    guide_lines.append("")

    for m in all_missing:
        guide_lines.append(f"  - {m['name']}")
    guide_lines.append("")
    guide_lines.append("下载后将文件放入: backend/data/raw/ 目录")
    guide_lines.append("然后运行: python scripts/supplement_missing_batches.py")

    guide = "\n".join(guide_lines)
    print(f"\n{guide}")

    guide_file = DATA_DIR / 'download_guide_2025.txt'
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide)

    # Generate supplement script
    generate_supplement_script(all_missing)


def generate_supplement_script(missing_tasks):
    script = r'''# -*- coding: utf-8 -*-
"""
补充采集缺失批次的投档数据（2025年）

使用流程:
1. 根据 batch_completeness_report_2025.txt 确认缺失批次
2. 从广东省教育考试院官网下载对应PDF文件
3. 将PDF放入 backend/data/raw/ 目录
4. 运行: python scripts/supplement_missing_batches.py
"""
import json, os, sys, io, shutil, pdfplumber
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = Path(__file__).parent.parent / 'data'
RAW_DIR = DATA_DIR / 'raw'
MAIN_FILE = DATA_DIR / 'major_rank_data.json'
BACKUP_DIR = DATA_DIR / 'backups'

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

def parse_pdf(pdf_path, batch_info):
    records = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 5:
                        continue
                    try:
                        uni_code = str(row[0] if len(row)>0 else '').strip()
                        uni_name = str(row[1] if len(row)>1 else '').strip()
                        group_code = str(row[2] if len(row)>2 else '').strip()
                        if not uni_name or uni_code in ('院校代码',''):
                            continue
                        # score col 5, rank col 6
                        min_score = 0
                        if len(row)>5 and row[5]:
                            try:
                                v = int(str(row[5]).strip().replace(',',''))
                                if 150<=v<=750: min_score=v
                            except: pass
                        min_rank = 0
                        if len(row)>6 and row[6]:
                            try:
                                v = int(str(row[6]).strip().replace(',',''))
                                if 1<=v<=1000000: min_rank=v
                            except: pass
                        if min_rank<=0: continue

                        level = '985' if uni_name in KNOWN_985 else ('211' if uni_name in KNOWN_211 else '普通本科')

                        records.append({
                            'year':2025,'province':'广东','university_name':uni_name,
                            'major_name':f'专业组{group_code}' if group_code else '未分类',
                            'min_rank':min_rank,'min_score':min_score,
                            'university_level':level,'university_province':'',
                            'subject_type':'理科' if '物理' in batch_info.get('category','') else '文科',
                            'batch_group':batch_info.get('group',''),'batch_name':batch_info.get('name',''),
                            'data_source':f'广东省教育考试院_2025_{batch_info.get("name","")}',
                            'is_official':True,'verified':True,'group_code':group_code,
                        })
                    except: continue
    return records

def main():
    task_file = DATA_DIR / 'missing_batches_tasks_2025.json'
    if not task_file.exists():
        print('No missing batches task file found. Run validate_and_collect_all_batches.py first.')
        return

    with open(task_file,'r',encoding='utf-8') as f:
        tasks = json.load(f)

    if not RAW_DIR.exists():
        print(f'ERROR: {RAW_DIR} does not exist. Create it and put PDFs there.')
        return

    pdfs = list(RAW_DIR.glob('*.pdf'))
    print(f'Found {len(pdfs)} PDF(s) in {RAW_DIR}')
    for p in pdfs:
        print(f'  {p.name}')

    for task in tasks:
        matched = None
        for p in pdfs:
            pname = p.name.lower()
            if '物理' in task.get('category','') and '物理' not in pname:
                continue
            if '历史' in task.get('category','') and '历史' not in pname:
                continue
            matched = p
            break

        if matched:
            print(f'\nImporting: {task["name"]} from {matched.name}')
            records = parse_pdf(str(matched), task)
            print(f'  Parsed {len(records)} records')
            if records:
                # backup
                BACKUP_DIR.mkdir(exist_ok=True)
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                if MAIN_FILE.exists():
                    shutil.copy2(MAIN_FILE, BACKUP_DIR/f'major_rank_data_{ts}.json')
                # merge
                with open(MAIN_FILE,'r',encoding='utf-8') as f:
                    data = json.load(f)
                existing = data.get('major_rank_data',[])
                merged = existing + records
                data['major_rank_data'] = merged
                data['metadata']['total_records'] = len(merged)
                data['metadata']['last_updated'] = datetime.now().isoformat()
                data['metadata']['last_batch_added'] = task['name']
                with open(MAIN_FILE,'w',encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f'  Merged. Total now: {len(merged)}')
        else:
            print(f'\nSkipping {task["name"]} - no matching PDF found')

if __name__ == '__main__':
    main()
'''
    script_file = DATA_DIR.parent / 'scripts' / 'supplement_missing_batches.py'
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script)
    print(f"\n补充采集脚本已生成: {script_file}")


if __name__ == '__main__':
    main()
