import json
import csv
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1] / 'data'
MAJOR_RANK = BASE / 'major_rank_data.json'
DETAILED = BASE / 'group_code_to_majors.json'
SIMPLE = BASE / 'group_code_mapping.json'
OUT = BASE / 'missing_group_mappings.csv'

def clean_code(code):
    if code is None:
        return ''
    s = str(code).strip()
    if s.isdigit():
        return str(int(s))
    return s

def load_json(p):
    if not p.exists():
        return {}
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print('Scanning mappings...')
    majors = load_json(MAJOR_RANK).get('major_rank_data', [])
    detailed = load_json(DETAILED)
    simple = load_json(SIMPLE)

    # build set of keys from major_rank_data
    seen = {}
    for r in majors:
        uni = r.get('university_name', '').strip()
        code = clean_code(r.get('group_code', ''))
        if not uni or not code:
            continue
        key = f"{uni}_{code}"
        if key not in seen:
            seen[key] = {
                'university_name': uni,
                'group_code': code,
                'sample_major_name': r.get('major_name','')
            }

    # compare to detailed mapping
    missing = []
    for key, info in seen.items():
        if key not in detailed:
            # try normalized variants (leading zeros etc not necessary because we cleaned)
            in_simple = key in simple
            missing.append({
                'university_name': info['university_name'],
                'group_code': info['group_code'],
                'sample_major_name': info['sample_major_name'] or '',
                'in_simple': 'YES' if in_simple else 'NO',
                'auto_filled': 'NO'
            })

    # Auto-fill from simple mapping where possible
    if missing:
        # backup detailed
        bak = DETAILED.with_suffix('.json.bak')
        if not bak.exists():
            DETAILED.replace(bak) if DETAILED.exists() else None

        updated = False
        for m in missing:
            key = f"{m['university_name']}_{m['group_code']}"
            if key in simple:
                # create a minimal detailed entry
                entry = {
                    'group_code': m['group_code'],
                    'majors': [],
                    'subjects': '',
                    'plan_count': 0,
                    'tuition': None,
                    'duration': None,
                    'university_code': ''
                }
                sm = simple.get(key, {})
                majors_list = sm.get('majors', []) if isinstance(sm, dict) else []
                # convert string majors to dicts with major_name
                majors_converted = []
                for mj in majors_list:
                    if isinstance(mj, dict):
                        majors_converted.append(mj)
                    else:
                        majors_converted.append({'major_name': mj})
                entry['majors'] = majors_converted
                # write into detailed
                detailed[key] = entry
                m['auto_filled'] = 'YES'
                updated = True

        if updated:
            # write back detailed mapping
            with open(DETAILED, 'w', encoding='utf-8') as f:
                json.dump(detailed, f, ensure_ascii=False, indent=2)
            print('Updated detailed mapping with entries from simple mapping.')

    # write CSV
    with open(OUT, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = ['university_name', 'group_code', 'sample_major_name', 'suggested_majors', 'in_simple', 'auto_filled']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for m in missing:
            writer.writerow({
                'university_name': m['university_name'],
                'group_code': m['group_code'],
                'sample_major_name': m.get('sample_major_name',''),
                'suggested_majors': '',
                'in_simple': m.get('in_simple','NO'),
                'auto_filled': m.get('auto_filled','NO')
            })

    print(f'Found {len(missing)} missing mappings. CSV written to: {OUT}')


if __name__ == '__main__':
    main()
