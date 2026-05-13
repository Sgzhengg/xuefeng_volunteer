"""
测试认证和志愿表API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_auth_api():
    """测试认证API"""
    print("=== 测试认证API ===")

    # 1. 发送验证码
    print("\n1. 发送验证码...")
    response = requests.post(f"{BASE_URL}/auth/send_code", json={
        "phone": "13800138000"
    })
    print(f"发送验证码: {response.json()}")

    # 2. 登录
    print("\n2. 登录...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13800138000",
        "code": "123456"
    })
    login_result = response.json()
    print(f"登录结果: {login_result}")

    if login_result.get("code") == 0:
        token = login_result["data"]["token"]
        print(f"获取到token: {token[:50]}...")

        # 3. 获取用户信息
        print("\n3. 获取用户信息...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"用户信息: {response.json()}")

        return token
    else:
        print("登录失败，无法继续测试")
        return None


def test_plan_api(token):
    """测试志愿表API"""
    print("\n=== 测试志愿表API ===")

    headers = {"Authorization": f"Bearer {token}"}

    # 1. 获取志愿列表
    print("\n1. 获取志愿列表...")
    response = requests.get(f"{BASE_URL}/plan/list", headers=headers)
    print(f"志愿列表: {response.json()}")

    # 2. 添加志愿
    print("\n2. 添加志愿...")
    plan_data = {
        "university_id": "sysu",
        "major_id": "cs",
        "university_name": "中山大学",
        "major_name": "计算机科学与技术",
        "probability": 70,
        "roi_score": 85,
        "tag": "稳"
    }
    response = requests.post(f"{BASE_URL}/plan/add", headers=headers, json=plan_data)
    print(f"添加志愿: {response.json()}")

    # 添加更多志愿用于测试
    test_plans = [
        {
            "university_id": "scau", "major_id": "cs",
            "university_name": "华南农业大学", "major_name": "计算机科学与技术",
            "probability": 85, "roi_score": 75, "tag": "保"
        },
        {
            "university_id": "sysu", "major_id": "math",
            "university_name": "中山大学", "major_name": "数学与应用数学",
            "probability": 45, "roi_score": 90, "tag": "冲"
        },
        {
            "university_id": "hnu", "major_id": "cs",
            "university_name": "湖南大学", "major_name": "计算机科学与技术",
            "probability": 55, "roi_score": 80, "tag": "稳"
        }
    ]

    for plan in test_plans:
        requests.post(f"{BASE_URL}/plan/add", headers=headers, json=plan)

    # 3. 再次获取志愿列表
    print("\n3. 再次获取志愿列表...")
    response = requests.get(f"{BASE_URL}/plan/list", headers=headers)
    print(f"志愿列表: {response.json()}")

    # 4. 评估志愿表
    print("\n4. 评估志愿表...")
    response = requests.get(f"{BASE_URL}/plan/evaluate", headers=headers)
    evaluation = response.json()
    print(f"评估结果: {json.dumps(evaluation, indent=2, ensure_ascii=False)}")

    # 5. 删除志愿
    print("\n5. 删除志愿...")
    response = requests.delete(f"{BASE_URL}/plan/remove?major_id=cs", headers=headers)
    print(f"删除结果: {response.json()}")

    # 6. 再次评估志愿表
    print("\n6. 再次评估志愿表...")
    response = requests.get(f"{BASE_URL}/plan/evaluate", headers=headers)
    evaluation = response.json()
    print(f"评估结果: {json.dumps(evaluation, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    print("开始测试认证和志愿表API...")

    # 测试认证API并获取token
    token = test_auth_api()

    # 如果登录成功，测试志愿表API
    if token:
        test_plan_api(token)

    print("\n测试完成！")
