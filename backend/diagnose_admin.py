"""
管理后台诊断脚本
快速检查所有关键功能是否正常
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def test_server_status():
    """测试服务器是否运行"""
    print_section("1. 服务器状态检查")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print("[OK] 服务器运行正常")
            print(f"  - API状态: {data.get('status', 'unknown')}")
            print(f"  - 管理后台: {data.get('services', {}).get('admin', 'unknown')}")
            return True
        else:
            print(f"[ERROR] 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] 无法连接到服务器: {e}")
        return False

def test_admin_login():
    """测试管理员登录"""
    print_section("2. 管理员登录测试")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/admin/login", json={
            "username": "admin",
            "password": "password"
        })

        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print("[OK] 管理员登录成功")
                token = result["data"]["token"]
                return token
            else:
                print(f"[ERROR] 登录失败: {result.get('message')}")
                return None
        else:
            print(f"[ERROR] 登录接口异常: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] 登录请求失败: {e}")
        return None

def test_admin_stats(token):
    """测试统计数据API"""
    print_section("3. 统计数据API测试")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/stats",
                             headers={"Authorization": f"Bearer {token}"})

        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print("[OK] 统计数据获取成功")
                data = result["data"]
                print(f"  - 用户数: {data.get('user_count', 0)}")
                print(f"  - 院校数: {data.get('university_count', 0)}")
                print(f"  - 专业数: {data.get('major_count', 0)}")
                print(f"  - 更新时间: {data.get('updated_at', 'N/A')}")
                return True
            else:
                print(f"[ERROR] 获取统计失败: {result.get('message')}")
                return False
        else:
            print(f"[ERROR] 统计API异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] 统计请求失败: {e}")
        return False

def test_universities_api(token):
    """测试院校API"""
    print_section("4. 院校管理API测试")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/universities?page=1&limit=3",
                             headers={"Authorization": f"Bearer {token}"})

        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print("[OK] 院校列表获取成功")
                data = result["data"]
                print(f"  - 总数: {data.get('total', 0)}")
                print(f"  - 当前页: {data.get('page', 1)}/{data.get('total_pages', 1)}")
                print(f"  - 返回条数: {len(data.get('list', []))}")
                return True
            else:
                print(f"[ERROR] 获取院校列表失败: {result.get('message')}")
                return False
        else:
            print(f"[ERROR] 院校API异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] 院校请求失败: {e}")
        return False

def test_page_access():
    """测试页面访问"""
    print_section("5. 页面访问测试")
    pages = [
        ("管理后台登录", "http://localhost:8000/admin"),
        ("仪表盘", "http://localhost:8000/admin/dashboard"),
        ("院校管理", "http://localhost:8000/admin/universities"),
        ("数据导入", "http://localhost:8000/admin/admission-data"),
    ]

    for name, url in pages:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200 and "DOCTYPE html" in response.text:
                print(f"[OK] {name}: 页面正常")
            else:
                print(f"[ERROR] {name}: 页面异常 (状态码: {response.status_code})")
        except Exception as e:
            print(f"[ERROR] {name}: 访问失败 ({e})")

def check_file_structure():
    """检查文件结构"""
    print_section("6. 文件结构检查")
    import os

    required_files = [
        "app/api/admin.py",
        "admin/templates/login.html",
        "admin/templates/dashboard.html",
        "admin/templates/universities.html",
        "admin/templates/admission_data.html",
        "admin/static/css/style.css",
        "admin/static/js/admin.js",
    ]

    all_exist = True
    for file_path in required_files:
        full_path = os.path.join("backend", file_path)
        if os.path.exists(full_path):
            print(f"[OK] {file_path}")
        else:
            print(f"[ERROR] {file_path} - 文件不存在")
            all_exist = False

    return all_exist

def get_browser_test_guide():
    """提供浏览器测试指南"""
    print_section("7. 浏览器测试指南")
    print("""
如果API测试通过但浏览器显示500错误，请尝试以下步骤：

1. 打开浏览器开发者工具 (F12)
2. 查看Console标签页的错误信息
3. 查看Network标签页，找到失败的请求
4. 检查请求的Response内容

常见问题：
- localStorage中没有token（需要先登录）
- token过期（重新登录）
- 静态文件加载失败（检查路径）
- JavaScript错误（查看Console）

快速测试步骤：
1. 清除浏览器缓存
2. 访问 http://localhost:8000/admin
3. 输入 admin/password 登录
4. 检查是否正常跳转到仪表盘
5. 如果仍有问题，按F12查看具体错误
    """)

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║           🎓 学锋志愿教练 - 管理后台诊断工具              ║
╚══════════════════════════════════════════════════════════╝
    """)

    # 检查服务器
    if not test_server_status():
        print("\n[ERROR] 服务器未运行，请先启动服务器：")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload")
        return

    # 检查文件结构
    if not check_file_structure():
        print("\n[ERROR] 文件结构不完整，请检查项目文件")
        return

    # 测试管理员登录
    token = test_admin_login()
    if not token:
        return

    # 测试API功能
    test_admin_stats(token)
    test_universities_api(token)

    # 测试页面访问
    test_page_access()

    # 提供浏览器测试指南
    get_browser_test_guide()

    print("\n" + "="*60)
    print("✅ 后端API诊断完成")
    print("="*60)
    print("\n如果浏览器中仍有问题，请按F12打开开发者工具查看具体错误")

if __name__ == "__main__":
    main()
