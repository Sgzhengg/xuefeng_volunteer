"""
测试管理后台API功能
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_admin_login():
    """测试管理员登录"""
    print("=== 测试管理员登录 ===")
    response = requests.post(f"{BASE_URL}/admin/login", json={
        "username": "admin",
        "password": "password"
    })
    print(f"登录结果: {response.json()}")

    if response.json().get("code") == 0:
        token = response.json()["data"]["token"]
        print(f"[OK] Login successful, got token: {token[:50]}...")
        return token
    else:
        print("[ERROR] Login failed")
        return None


def test_admin_stats(token):
    """测试获取统计数据"""
    print("\n=== 测试获取统计数据 ===")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BASE_URL}/admin/stats", headers=headers)
    print(f"统计数据: {response.json()}")

    if response.json().get("code") == 0:
        print("[OK] Get stats successful")
    else:
        print("[ERROR] Get stats failed")


def test_universities_list(token):
    """测试获取院校列表"""
    print("\n=== 测试获取院校列表 ===")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BASE_URL}/admin/universities?page=1&limit=5", headers=headers)
    result = response.json()

    print(f"院校列表 (前5条):")
    if result.get("code") == 0:
        data = result["data"]
        print(f"  总数: {data['total']}")
        print(f"  当前页: {data['page']}/{data['total_pages']}")
        print(f"  院校数量: {len(data['list'])}")

        for uni in data['list'][:3]:  # 只显示前3个
            print(f"    - {uni.get('name', 'N/A')} ({uni.get('province', 'N/A')})")

        print("[OK] Get universities list successful")
    else:
        print("[ERROR] Get universities list failed")


def test_add_university(token):
    """测试添加院校"""
    print("\n=== 测试添加院校 ===")
    headers = {"Authorization": f"Bearer {token}"}

    new_university = {
        "name": "测试大学",
        "province": "广东",
        "city": "深圳",
        "type": "综合",
        "level": "本科",
        "website": "https://www.test.edu.cn",
        "founded": "2024",
        "description": "这是一所测试院校"
    }

    response = requests.post(f"{BASE_URL}/admin/universities", headers=headers, json=new_university)
    print(f"添加院校: {response.json()}")

    if response.json().get("code") == 0:
        print("[OK] Add university successful")
        return response.json()["data"]["id"]
    else:
        print("[ERROR] Add university failed")
        return None


def test_university_search(token):
    """测试院校搜索"""
    print("\n=== 测试院校搜索 ===")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BASE_URL}/admin/universities?keyword=北京&page=1&limit=3", headers=headers)
    result = response.json()

    print(f"搜索'北京'的结果:")
    if result.get("code") == 0:
        data = result["data"]
        print(f"  找到 {data['total']} 所院校")
        for uni in data['list']:
            print(f"    - {uni.get('name', 'N/A')}")
        print("[OK] Search function works properly")
    else:
        print("[ERROR] Search function failed")


if __name__ == "__main__":
    try:
        print("开始测试管理后台API...")

        # 测试登录
        token = test_admin_login()
        if not token:
            print("\n[ERROR] Login failed, cannot continue testing")
            exit(1)

        # 测试统计功能
        test_admin_stats(token)

        # 测试院校列表
        test_universities_list(token)

        # 测试添加院校
        new_id = test_add_university(token)

        # 测试搜索功能
        test_university_search(token)

        print("\n" + "="*50)
        print("[SUCCESS] All tests completed!")
        print("="*50)
        print("\nYou can visit these pages:")
        print("   Admin Panel: http://localhost:8000/admin")
        print("   API Docs: http://localhost:8000/docs")
        print("\nLogin credentials:")
        print("   Username: admin")
        print("   Password: password")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
