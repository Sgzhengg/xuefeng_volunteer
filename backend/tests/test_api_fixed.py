# -*- coding: utf-8 -*-
"""
验证API修复效果的简化测试脚本
"""

import requests
import json

# 测试API连接
def test_api_connection():
    try:
        # 测试简单请求
        url = "http://localhost:8000/docs"
        response = requests.get(url, timeout=5)
        print(f"[OK] API服务运行正常，状态码: {response.status_code}")
        return True
    except Exception as e:
        print(f"[ERROR] API服务连接失败: {e}")
        return False

# 测试推荐接口
def test_recommend_api():
    url = "http://localhost:8000/api/v1/recommendation/generate"
    data = {
        "province": "广东",
        "score": 600,
        "rank": 15000,
        "subject_type": "理科",
        "target_majors": ["计算机科学与技术"]
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"[INFO] API状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"[OK] API调用成功")
            print(f"[INFO] 响应格式: {list(result.keys())}")

            # 检查响应结构
            if result.get("success") or result.get("data"):
                data = result.get("data", result)
                if isinstance(data, dict):
                    categories = list(data.keys())
                    print(f"[INFO] 推荐类别: {categories}")

                    for category in categories:
                        items = data[category]
                        if isinstance(items, list):
                            print(f"[INFO] {category}: {len(items)} 条推荐")
                            if len(items) > 0:
                                print(f"[SAMPLE] {category}第1条: {items[0].get('university_name', 'N/A')}")
                return True
            else:
                print(f"[ERROR] API返回格式异常: {result}")
                return False
        else:
            print(f"[ERROR] HTTP错误: {response.status_code}")
            print(f"[INFO] 响应内容: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"[ERROR] 推荐接口调用失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("API修复效果验证测试")
    print("=" * 50)

    # 1. 测试API连接
    print("\n[TEST-1] 测试API连接...")
    if not test_api_connection():
        print("[FAILED] API连接测试失败，请确保后端服务已启动")
        exit(1)

    # 2. 测试推荐接口
    print("\n[TEST-2] 测试推荐接口...")
    if test_recommend_api():
        print("\n[SUCCESS] API修复成功！")
        print("[INFO] 现在可以运行回溯测试: python backtest.py --quick")
    else:
        print("\n[FAILED] 推荐接口仍有问题，需要进一步调试")

    print("=" * 50)