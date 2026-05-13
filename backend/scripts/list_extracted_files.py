# -*- coding: utf-8 -*-
import os

lines = []
for dirname in ['temp_2023', 'temp_2024']:
    path = os.path.join(r'd:\xuefeng_volunteer\backend\data', dirname)
    lines.append(f'=== {dirname} ===')
    for f in sorted(os.listdir(path)):
        size_kb = os.path.getsize(os.path.join(path, f)) / 1024
        lines.append(f'  {f} ({size_kb:.1f} KB)')
    lines.append('')

with open(r'd:\xuefeng_volunteer\backend\data\extracted_files_list.txt', 'w', encoding='utf-8') as fp:
    fp.write('\n'.join(lines))
print('Done - output written to extracted_files_list.txt')
