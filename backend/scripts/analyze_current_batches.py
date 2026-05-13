# -*- coding: utf-8 -*-
"""Analyze current data for batch information"""
import json
from collections import Counter, defaultdict

with open(r'd:\xuefeng_volunteer\backend\data\major_rank_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
records = data.get('major_rank_data', [])

# What source fields exist?
sources = Counter()
categories = Counter()
batch_info = Counter()
years = Counter()
data_sources = set()

for r in records:
    if not isinstance(r, dict):
        continue
    years[r.get('year', '?')] += 1
    src = r.get('data_source', '')
    data_sources.add(src)
    sources[src.split('_')[0] if src else 'no_source'] += 1
    categories[r.get('category', r.get('subject_type', '?'))] += 1

print(f'Total records: {len(records)}')
print(f'\nYears: {dict(years)}')
print(f'\nCategories/Subjects: {dict(categories)}')
print(f'\nUnique data_sources ({len(data_sources)}):')
for s in sorted(data_sources):
    print(f'  {s}')

# Check for batch field
has_batch = sum(1 for r in records if isinstance(r, dict) and r.get('batch'))
print(f'\nRecords with batch field: {has_batch}')

# Check year 2025 specifically
yr2025 = [r for r in records if isinstance(r, dict) and r.get('year') == 2025]
print(f'\n2025 records: {len(yr2025)}')
sources_2025 = Counter(r.get('data_source', '') for r in yr2025)
print(f'2025 sources: {dict(sources_2025)}')

# Check for non-广东 records
non_gd = [r for r in records if isinstance(r, dict) and r.get('province') != '广东']
print(f'\nNon-Guangdong records: {len(non_gd)}')

# Key question: do we have data for non-本科 batches?
# Check if any records mention 提前批, 专科, 征集 etc
for keyword in ['提前批', '专科', '征集', '艺体', '艺术', '体育', '音乐', '美术']:
    count = sum(1 for r in records if isinstance(r, dict) and keyword in str(r.get('data_source', '')))
    print(f'Records with "{keyword}" in data_source: {count}')
