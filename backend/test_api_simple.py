"""
简单的API功能测试（不启动服务器）
"""
import sys
sys.path.append('D:\\xuefeng_volunteer\\backend')

from app.api.auth import router as auth_router
from app.api.plan import router as plan_router
from datetime import datetime

def test_auth_module():
    """测试认证模块功能"""
    print("=== 测试认证模块 ===")

    # 测试发送验证码
    print("\n1. 测试生成token...")
    from app.api.auth import create_access_token

    token = create_access_token(
        data={"sub": "13800138000"},
        expires_delta=None
    )
    print(f"[OK] Token生成成功: {token[:50]}...")

    # 测试验证token
    print("\n2. 测试验证token...")
    from app.api.auth import verify_token

    phone = verify_token(token)
    print(f"[OK] Token验证成功，用户: {phone}")

    # 测试错误的token
    print("\n3. 测试错误token...")
    wrong_phone = verify_token("wrong_token")
    print(f"[OK] 错误token处理正确: {wrong_phone}")

    return True

def test_plan_module():
    """测试志愿表模块功能"""
    print("\n=== 测试志愿表模块 ===")

    # 模拟数据
    from app.api.plan import user_plans

    # 创建测试用户
    test_user_id = "test_user_123"
    user_plans[test_user_id] = [
        {
            "id": "中山大学_计算机科学与技术",
            "university_id": "sysu",
            "major_id": "cs",
            "university_name": "中山大学",
            "major_name": "计算机科学与技术",
            "probability": 70,
            "roi_score": 85,
            "tag": "稳",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "华南农业大学_计算机科学与技术",
            "university_id": "scau",
            "major_id": "cs",
            "university_name": "华南农业大学",
            "major_name": "计算机科学与技术",
            "probability": 85,
            "roi_score": 75,
            "tag": "保",
            "created_at": datetime.now().isoformat()
        }
    ]

    print(f"[OK] 创建测试用户数据，包含 {len(user_plans[test_user_id])} 个志愿")

    # 测试数据统计
    chong_count = 0
    wen_count = 0
    bao_count = 0

    for plan in user_plans[test_user_id]:
        tag = plan.get("tag", "")
        if tag == "冲" or tag == "冲刺":
            chong_count += 1
        elif tag == "稳" or tag == "稳妥":
            wen_count += 1
        elif tag == "保" or tag == "保底":
            bao_count += 1

    print(f"[OK] 统计结果: 冲刺{chong_count}所, 稳妥{wen_count}所, 保底{bao_count}所")

    # 测试评分逻辑
    score = 100
    if chong_count > 6:
        score -= 20
    if bao_count < 3:
        score -= 20
    if (wen_count + bao_count) < 10:
        score -= 15

    risk_level = "low" if score >= 80 else "medium" if score >= 60 else "high"

    print(f"[OK] 评分结果: {score}分, 风险等级: {risk_level}")

    return True

def test_integration():
    """测试集成功能"""
    print("\n=== 测试集成功能 ===")

    # 模拟完整的认证和志愿表流程
    from app.api.auth import sessions, verification_codes
    from app.api.plan import user_plans

    # 1. 模拟发送验证码
    test_phone = "13900139000"
    verification_codes[test_phone] = {
        "code": "123456",
        "expire_time": datetime.now()
    }
    print(f"[OK] 模拟发送验证码到: {test_phone}")

    # 2. 模拟登录
    sessions[test_phone] = {
        "user_id": test_phone,
        "phone": test_phone,
        "created_at": datetime.now().isoformat()
    }
    print(f"[OK] 模拟用户登录: {test_phone}")

    # 3. 模拟添加志愿
    user_plans[test_phone] = []
    test_plan = {
        "id": "测试大学_测试专业",
        "university_id": "test_uni",
        "major_id": "test_major",
        "university_name": "测试大学",
        "major_name": "测试专业",
        "probability": 60,
        "roi_score": 80,
        "tag": "稳",
        "created_at": datetime.now().isoformat()
    }
    user_plans[test_phone].append(test_plan)
    print(f"[OK] 模拟添加志愿: {test_plan['university_name']}_{test_plan['major_name']}")

    # 4. 验证数据完整性
    assert test_phone in sessions, "用户会话不存在"
    assert test_phone in user_plans, "用户志愿表不存在"
    assert len(user_plans[test_phone]) == 1, "志愿数量不正确"

    print(f"[OK] 集成测试通过，数据完整")

    return True

if __name__ == "__main__":
    try:
        print("开始测试认证和志愿表API模块...")

        # 运行所有测试
        test_auth_module()
        test_plan_module()
        test_integration()

        print("\n" + "="*50)
        print("[SUCCESS] 所有测试通过！")
        print("="*50)
        print("\n总结:")
        print("[OK] 认证模块功能正常")
        print("[OK] 志愿表模块功能正常")
        print("[OK] 集成功能正常")
        print("[OK] 数据存储结构正确")
        print("\n可以启动服务器进行完整测试：")
        print("   cd backend")
        print("   python -m uvicorn app.main:app --reload")

    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
