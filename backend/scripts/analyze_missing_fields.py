# -*- coding: utf-8 -*-
"""Analyze records with missing fields and fix province/level detection"""
import json, os
from collections import Counter

DATA_DIR = r'd:\xuefeng_volunteer\backend\data'
with open(os.path.join(DATA_DIR, 'major_rank_data.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

records = data.get('major_rank_data', [])

# Check records with empty province
no_province = [r for r in records if isinstance(r, dict) and r.get('university_province') == '' and r.get('year') in [2023, 2024]]
print(f'2023/2024 records with empty province: {len(no_province)}')

# Sample some with empty province
sample = no_province[:30]
uni_names = Counter(r.get('university_name', '') for r in no_province)
print(f'\nTop 30 universities with empty province:')
for name, count in uni_names.most_common(30):
    print(f'  {name}: {count}')

# Check for universities not classified at all
all_2023_2024 = [r for r in records if isinstance(r, dict) and r.get('year') in [2023, 2024]]
all_unis = set(r.get('university_name', '') for r in all_2023_2024)
print(f'\nTotal unique universities in 2023/2024: {len(all_unis)}')

uni_with_province = set(r.get('university_name', '') for r in all_2023_2024 if r.get('university_province'))
uni_without_province = all_unis - uni_with_province
print(f'Universities WITH province: {len(uni_with_province)}')
print(f'Universities WITHOUT province: {len(uni_without_province)}')

if uni_without_province:
    print(f'\nSample universities without province:')
    for name in sorted(list(uni_without_province))[:30]:
        count = sum(1 for r in all_2023_2024 if r.get('university_name') == name)
        print(f'  {name}: {count} records')

# Check 2025 year distribution
yr_2025 = [r for r in records if isinstance(r, dict) and r.get('year') == 2025]
print(f'\n2025 records: {len(yr_2025)}')
print(f'  2025 with subject_type="?": {sum(1 for r in yr_2025 if r.get("subject_type") == "?")}')
print(f'  2025 with level: {sum(1 for r in yr_2025 if r.get("university_level"))}')
print(f'  2025 without level: {sum(1 for r in yr_2025 if not r.get("university_level"))}')
