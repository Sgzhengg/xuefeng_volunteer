# -*- coding: utf-8 -*-
"""Verify multi-year data completeness after import"""
import json, os
from collections import defaultdict, Counter

DATA_DIR = r'd:\xuefeng_volunteer\backend\data'
with open(os.path.join(DATA_DIR, 'major_rank_data.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

records = data.get('major_rank_data', [])
with open(os.path.join(DATA_DIR, 'verify_multi_year_report.txt'), 'w', encoding='utf-8') as rf:

    rf.write(f'Multi-Year Data Verification Report\n')
    rf.write(f'{"="*60}\n')
    rf.write(f'Total records: {len(records):,}\n\n')

    # By year
    years = defaultdict(list)
    for r in records:
        if isinstance(r, dict):
            years[r.get('year', 'unknown')].append(r)

    for year in sorted(years.keys()):
        recs = years[year]
        rf.write(f'\n{"="*60}\n')
        rf.write(f'Year {year}\n')
        rf.write(f'{"="*60}\n')
        rf.write(f'  Total records: {len(recs):,}\n')

        unis = set(r.get('university_name', '') for r in recs)
        rf.write(f'  Unique universities: {len(unis)}\n')

        # By subject
        subjects = Counter(r.get('subject_type', '?') for r in recs)
        rf.write(f'  Subjects: {dict(subjects)}\n')

        # By level
        levels = Counter(r.get('university_level', '?') for r in recs)
        rf.write(f'  Levels: {dict(levels)}\n')

        # By province
        provinces = Counter(r.get('university_province', '?') for r in recs)
        local = provinces.get('广东', 0)
        out = sum(v for k, v in provinces.items() if k != '广东' and k != '')
        unknown = provinces.get('', 0)
        rf.write(f'  Guangdong local: {local}, Out-of-province: {out}, Unknown: {unknown}\n')

        # Rank range
        ranks = [r['min_rank'] for r in recs if r.get('min_rank', 0) > 0]
        if ranks:
            rf.write(f'  Rank range: {min(ranks):,} - {max(ranks):,}\n')

        # Score range
        scores = [r['min_score'] for r in recs if r.get('min_score', 0) > 0]
        if scores:
            rf.write(f'  Score range: {min(scores)} - {max(scores)}\n')

        # Top 5 and bottom 5 by rank (physics)
        physics = [r for r in recs if r.get('subject_type') == '理科']
        history = [r for r in recs if r.get('subject_type') == '文科']
        rf.write(f'  Physics: {len(physics)}, History: {len(history)}\n')

        if physics:
            physics_sorted = sorted(physics, key=lambda r: r.get('min_rank', 999999))
            rf.write(f'  Top 5 Physics (by rank):\n')
            for r in physics_sorted[:5]:
                rf.write(f'    {r["university_name"]} | {r["major_name"]} | Score={r["min_score"]} | Rank={r["min_rank"]} | {r.get("university_level","?")}\n')

        # Guangdong top universities
        gd = [r for r in recs if r.get('university_province') == '广东' and r.get('subject_type') == '理科']
        gd_sorted = sorted(gd, key=lambda r: r.get('min_rank', 999999))
        if gd_sorted:
            rf.write(f'\n  Top 5 Guangdong Physics:\n')
            for r in gd_sorted[:5]:
                rf.write(f'    {r["university_name"]} | {r["major_name"]} | Score={r["min_score"]} | Rank={r["min_rank"]} | {r.get("university_level","?")}\n')

    # Cross-year comparison
    rf.write(f'\n{"="*60}\n')
    rf.write(f'Cross-Year Comparison\n')
    rf.write(f'{"="*60}\n')

    # Universities present in all 3 years
    for year in [2023, 2024, 2025]:
        yr_recs = years.get(year, [])
        gd_yr = [r for r in yr_recs if r.get('province') == '广东' and r.get('subject_type') == '理科']
        unis_yr = set(r.get('university_name', '') for r in gd_yr)
        rf.write(f'  Year {year} Physics universities: {len(unis_yr)}\n')

    # Summary
    rf.write(f'\n{"="*60}\n')
    rf.write(f'Summary\n')
    rf.write(f'{"="*60}\n')
    for year in sorted(years.keys()):
        recs = years[year]
        rf.write(f'  {year}: {len(recs):,} records\n')
    rf.write(f'  Total: {len(records):,} records across {len(years)} years\n')

    # Data quality checks
    rf.write(f'\n{"="*60}\n')
    rf.write(f'Data Quality Checks\n')
    rf.write(f'{"="*60}\n')

    # Records missing level
    missing_level = [r for r in records if isinstance(r, dict) and not r.get('university_level')]
    rf.write(f'  Missing level: {len(missing_level)}\n')

    # Records missing province
    missing_province = [r for r in records if isinstance(r, dict) and not r.get('university_province')]
    rf.write(f'  Missing province: {len(missing_province)}\n')

    # Records with score 0
    missing_score = [r for r in records if isinstance(r, dict) and r.get('min_score', 0) == 0]
    rf.write(f'  Missing score (0): {len(missing_score)}\n')

    # Records missing level field entirely
    no_level = sum(1 for r in records if isinstance(r, dict) and 'university_level' not in r)
    rf.write(f'  No university_level field: {no_level}\n')

print('Report written to verify_multi_year_report.txt')
