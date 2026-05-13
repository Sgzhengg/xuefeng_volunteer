# -*- coding: utf-8 -*-
import pdfplumber, os, json

# Find the 2024 Physics PDF
data_dir = r'd:\xuefeng_volunteer\backend\data'
temp_2024 = os.path.join(data_dir, 'temp_2024')
temp_2023 = os.path.join(data_dir, 'temp_2023')

# Find PDFs
def find_pdf(d, keyword):
    for f in os.listdir(d):
        if keyword in f and f.endswith('.pdf'):
            return os.path.join(d, f)
    return None

for dir_path, year, label in [(temp_2024, 2024, '物理'), (temp_2023, 2023, '物理')]:
    print(f'\n{"="*60}')
    pdf_path = find_pdf(dir_path, label)
    if not pdf_path:
        # Try by file size
        pdfs = sorted([f for f in os.listdir(dir_path) if f.endswith('.pdf')],
                       key=lambda f: os.path.getsize(os.path.join(dir_path, f)), reverse=True)
        if pdfs:
            pdf_path = os.path.join(dir_path, pdfs[0])
            print(f'Using largest PDF: {pdfs[0]}')
    if not pdf_path:
        print(f'No PDF found for {year} {label}')
        continue

    print(f'PDF: {os.path.basename(pdf_path)}')
    print(f'Size: {os.path.getsize(pdf_path) / 1024:.1f} KB')

    with pdfplumber.open(pdf_path) as pdf:
        print(f'Pages: {len(pdf.pages)}')

        # Examine first 2 pages
        for pg in range(min(3, len(pdf.pages))):
            page = pdf.pages[pg]
            print(f'\n--- Page {pg+1} ---')

            # Get all text
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                print(f'  Text lines: {len(lines)}')
                print(f'  First 10 lines:')
                for l in lines[:10]:
                    print(f'    {l[:120]}')

            # Get tables
            tables = page.extract_tables()
            print(f'  Tables found: {len(tables)}')
            for ti, table in enumerate(tables):
                print(f'  Table {ti+1}: {len(table)} rows, {len(table[0]) if table else 0} cols')
                # Show first 3 rows
                for ri in range(min(5, len(table))):
                    row = table[ri]
                    print(f'    Row {ri}: {row}')

        # Also check the last page
        if len(pdf.pages) > 3:
            page = pdf.pages[-1]
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                print(f'\n--- Last Page ({len(pdf.pages)}) ---')
                print(f'  Last 5 lines:')
                for l in lines[-5:]:
                    print(f'    {l[:120]}')

# Output stats to file
with open(os.path.join(data_dir, 'pdf_structure_analysis.json'), 'w', encoding='utf-8') as f:
    f.write('{"done": true}')
print('\n\nAnalysis complete.')
