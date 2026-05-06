import requests
import json

response = requests.post('http://127.0.0.1:8000/api/v1/recommendation/generate', json={
    'province': '江苏',
    'score': 600,
    'subject_type': '理科',
    'target_majors': ['计算机']
})

print('Status:', response.status_code)
result = response.json()
print('Success:', result.get('success'))

data = result.get('data', {})
print('Total schools:', data.get('analysis', {}).get('total_count', 0))
print('Raw data keys:', list(data.keys()))

for cat in ['冲刺', '稳妥', '保底']:
    schools = data.get(cat, [])
    count = len(schools)
    print(f'{cat}: {count}所学校')
    if schools:
        for school in schools:
            print(f'  - {school.get("university_name", "未知")}: {school.get("probability", 0)}%')

# 打印完整的响应以便调试
print('\n完整响应:')
print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
