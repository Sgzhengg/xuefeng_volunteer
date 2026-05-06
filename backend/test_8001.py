import requests
import json

def test_score(score):
    response = requests.post('http://127.0.0.1:8001/api/v1/recommendation/generate', json={
        'province': '江苏',
        'score': score,
        'subject_type': '理科',
        'target_majors': ['计算机']
    })

    result = response.json()
    data = result.get('data', {})
    total = data.get('analysis', {}).get('total_count', 0)

    print(f"\n分数 {score}:")
    print(f"  总学校数: {total}")

    for cat in ['冲刺', '稳妥', '保底']:
        schools = data.get(cat, [])
        if schools:
            print(f"  {cat}: {len(schools)}所学校")
            for school in schools[:2]:  # 只显示前2所
                print(f"    - {school.get('university_name', '未知')}: 概率{school.get('probability', 0)}%")
        else:
            print(f"  {cat}: 0所")

# 测试不同分数
print("测试不同分数的推荐结果 (端口8001):")
test_score(400)
test_score(500)
test_score(540)
test_score(600)
test_score(650)
