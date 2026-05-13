"""
测试认证和志愿表API（修复编码问题后）
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_complete_workflow():
    """测试完整的工作流程"""
    print("=== 测试认证和志愿表API完整流程 ===")

    # 1. 发送验证码
    print("\n1. 发送验证码...")
    response = requests.post(f"{BASE_URL}/auth/send_code", json={
        "phone": "13900139000"
    })
    print(f"发送验证码: {response.json()}")

    # 2. 登录
    print("\n2. 登录...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": "13900139000",
        "code": "123456"
    })
    login_result = response.json()
    print(f"登录结果: {login_result}")

    if login_result.get("code") == 0:
        token = login_result["data"]["token"]
        print(f"[OK] Login successful, got token: {token[:50]}...")

        headers = {"Authorization": f"Bearer {token}"}

        # 3. 获取用户信息
        print("\n3. 获取用户信息...")
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"用户信息: {response.json()}")

        # 4. 获取志愿列表（初始为空）
        print("\n4. 获取志愿列表...")
        response = requests.get(f"{BASE_URL}/plan/list", headers=headers)
        print(f"志愿列表: {response.json()}")

        # 5. 添加志愿
        print("\n5. 添加志愿...")
        plans_to_add = [
            {
                "university_id": "sysu", "major_id": "cs",
                "university_name": "中山大学", "major_name": "计算机科学与技术",
                "probability": 70, "roi_score": 85, "tag": "稳"
            },
            {
                "university_id": "scau", "major_id": "cs",
                "university_name": "华南农业大学", "major_name": "计算机科学与技术",
                "probability": 85, "roi_score": 75, "tag": "保"
            },
            {
                "university_id": "hnu", "major_id": "cs",
                "university_name": "湖南大学", "major_name": "计算机科学与技术",
                "probability": 45, "roi_score": 90, "tag": "冲"
            }
        ]

        for plan in plans_to_add:
            response = requests.post(f"{BASE_URL}/plan/add", headers=headers, json=plan)
            print(f"添加 {plan['university_name']}: {response.json()}")

        # 6. 再次获取志愿列表
        print("\n6. 再次获取志愿列表...")
        response = requests.get(f"{BASE_URL}/plan/list", headers=headers)
        list_result = response.json()
        print(f"志愿列表: {json.dumps(list_result, indent=2, ensure_ascii=False)}")

        # 7. 评估志愿表
        print("\n7. 评估志愿表...")
        response = requests.get(f"{BASE_URL}/plan/evaluate", headers=headers)
        evaluation = response.json()
        print(f"评估结果:")
        print(json.dumps(evaluation, indent=2, ensure_ascii=False))

        # 8. 删除一个志愿
        print("\n8. 删除志愿...")
        major_id = "中山大学_计算机科学与技术"
        response = requests.delete(f"{BASE_URL}/plan/remove?major_id={major_id}", headers=headers)
        print(f"删除结果: {response.json()}")

        # 9. 再次评估志愿表
        print("\n9. 再次评估志愿表...")
        response = requests.get(f"{BASE_URL}/plan/evaluate", headers=headers)
        evaluation = response.json()
        print(f"删除后的评估结果:")
        print(json.dumps(evaluation, indent=2, ensure_ascii=False))

        print("\n" + "="*50)
        print("[SUCCESS] 所有API测试通过！")
        print("="*50)

    else:
        print("登录失败，无法继续测试")

if __name__ == "__main__":
    try:
        test_complete_workflow()
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
