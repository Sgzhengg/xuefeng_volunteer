# -*- coding: utf-8 -*-
"""尝试gkmlpt框架的API获取附件链接"""

import requests
import re
import json

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})

# 2024 page
page_url = "https://eea.gd.gov.cn/gkmlpt/content/4/4458/post_4458330.html"
resp = session.get(page_url, timeout=30)
resp.encoding = 'utf-8'
html = resp.text

# Extract CSRF
csrf_m = re.search(r"CSRF:\s*'([^']+)'", html)
if not csrf_m:
    print("No CSRF found")
    exit(1)
csrf = csrf_m.group(1)
print(f"CSRF: {csrf}")

# Try various API endpoints
base = "https://eea.gd.gov.cn"
apis = [
    f"/gkmlpt/api/content/detail",
    f"/gkmlpt/api/content/4/4458/4458330",
    f"/gkmlpt/api/article/4458330",
]

for api in apis:
    url = base + api
    headers = {
        'X-CSRF-TOKEN': csrf,
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': page_url,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Try GET
    try:
        r = session.get(url, headers=headers, timeout=15)
        print(f"\nGET {api}: {r.status_code}")
        if r.status_code == 200:
            try:
                data = r.json()
                text = json.dumps(data, ensure_ascii=False)
                # Find PDF/attachment references
                pdfs = re.findall(r'["\']([^"\']*\.pdf[^"\']*)["\']', text)
                for p in pdfs[:10]:
                    print(f"  PDF: {p}")
                attrs = re.findall(r'["\']([^"\']*(?:attach|file|download)[^"\']*)["\']', text, re.IGNORECASE)
                for a in attrs[:10]:
                    print(f"  Attach: {a}")
                if not pdfs and not attrs:
                    print(f"  Content: {json.dumps(data, ensure_ascii=False)[:500]}")
            except:
                print(f"  Not JSON: {r.text[:200]}")
        else:
            print(f"  Response: {r.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")

    # Try POST
    try:
        params = {"contentId": "4458330", "siteId": "166"}
        r = session.post(url, headers=headers, json=params, timeout=15)
        print(f"\nPOST {api}: {r.status_code}")
        if r.status_code == 200:
            try:
                data = r.json()
                text = json.dumps(data, ensure_ascii=False)
                pdfs = re.findall(r'["\']([^"\']*\.pdf[^"\']*)["\']', text)
                for p in pdfs[:10]:
                    print(f"  PDF: {p}")
                if not pdfs:
                    print(f"  Content: {json.dumps(data, ensure_ascii=False)[:500]}")
            except:
                print(f"  Not JSON: {r.text[:200]}")
        else:
            print(f"  Response: {r.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")

# Try known working PDF download URL (2025 pattern)
# The 2025 URLs are: https://eea.gd.gov.cn/attachment/0/585/585886/4746781.pdf
# 585 = 4746781 // (post_id / 8114) roughly
# Let me try to get the actual content page for 2025 first to see the pattern
print("\n\n--- Checking 2025 page for comparison ---")
page2025 = "https://eea.gd.gov.cn/ptgk/content/post_4746781.html"
try:
    r = session.get(page2025, timeout=30)
    r.encoding = 'utf-8'
    h = r.text
    print(f"Status: {r.status_code}, Length: {len(h)}")
    # Check for PDF links
    pdf_links = re.findall(r'href="([^"]*\.pdf[^"]*)"', h, re.IGNORECASE)
    print(f"PDF links: {pdf_links}")
except Exception as e:
    print(f"Error: {e}")
