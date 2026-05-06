import requests
import json

response = requests.post('http://127.0.0.1:8000/api/v1/recommendation/generate', json={
    'province': '江苏',
    'score': 540,
    'subject_type': '理科',
    'target_majors': ['计算机']
})

print('Status:', response.status_code)
result = response.json()
print('Success:', result.get('success'))

data = result.get('data', {})
print('Total schools:', data.get('analysis', {}).get('total_count', 0))
print('Categories:')
for cat in ['冲刺', '稳妥', '保底']:
    count = len(data.get(cat, []))
    print(f'  {cat}: {count}')

# Show first few recommendations
if data.get('冲刺'):
    print('\nFirst 冲刺 recommendation:')
    print(json.dumps(data['冲刺'][0], ensure_ascii=False, indent=2))
