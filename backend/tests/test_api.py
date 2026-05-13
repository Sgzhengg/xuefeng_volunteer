import requests
import json

# 测试推荐接口
url = "http://localhost:8000/api/v1/recommendation/generate"
data = {
    "province": "广东",
    "score": 600,
    "subject_type": "理科",
    "target_majors": ["计算机科学与技术"]
}

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"错误: {e}")