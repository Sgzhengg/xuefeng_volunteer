# -*- coding: utf-8 -*-
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
