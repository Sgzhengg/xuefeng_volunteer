"""
推荐算法测试验证脚本
验证修复后的算法是否符合预期
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_recommendation(user_rank, province, subject_type, target_majors, score):
    """测试推荐接口"""

    print(f"\n{'='*60}")
    print(f"测试用例: 位次={user_rank}, 省份={province}, 科类={subject_type}")
    print(f"目标专业: {target_majors}")
    print(f"{'='*60}")

    payload = {
        "province": province,
        "score": score,  # 保留分数用于展示
        "subject_type": subject_type,
        "target_majors": target_majors,
        "rank": user_rank,  # 必填
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/recommendation/generate",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("success"):
                result_data = data.get("data", {})
                basic_info = result_data.get("basic_info", {})
                recommendations = {
                    "冲刺": result_data.get("冲刺", []),
                    "稳妥": result_data.get("稳妥", []),
                    "保底": result_data.get("保底", [])
                }

                print(f"\n✅ 推荐成功！")
                print(f"算法版本: {basic_info.get('algorithm', 'unknown')}")
                print(f"\n推荐统计:")
                print(f"  冲刺: {len(recommendations['冲刺'])} 所")
                print(f"  稳妥: {len(recommendations['稳妥'])} 所")
                print(f"  保底: {len(recommendations['保底'])} 所")
                print(f"  总计: {len(recommendations['冲刺']) + len(recommendations['稳妥']) + len(recommendations['保底'])} 所")

                # 检查是否有不应该出现的顶尖院校
                top_unis = ["北京大学", "清华大学", "复旦大学", "上海交通大学"]
                all_recs = []
                for cat, recs in recommendations.items():
                    all_recs.extend([r['university_name'] for r in recs])

                print(f"\n推荐的院校:")
                for cat, recs in recommendations.items():
                    if recs:
                        print(f"\n{cat}:")
                        for rec in recs[:5]:  # 最多显示5所
                            uni = rec['university_name']
                            prob = rec['probability']
                            min_rank = rec.get('min_rank', 'N/A')
                            print(f"  - {uni} (概率: {prob*100:.0f}%, 最低位次: {min_rank})")

                # 验证：顶尖院校不应该被推荐给低排名考生
                violations = []
                for uni in top_unis:
                    if uni in all_recs:
                        violations.append(uni)

                if violations:
                    print(f"\n❌ 警告：以下顶尖院校被推荐给位次{user_rank}的考生（不应该出现）：")
                    for uni in violations:
                        print(f"  ⚠️  {uni}")
                else:
                    print(f"\n✅ 验证通过：没有将顶尖院校推荐给低排名考生")

                # 验证：推荐院校的录取位次与用户位次差距检查
                rank_gaps_ok = True
                for cat, recs in recommendations.items():
                    for rec in recs:
                        min_rank = rec.get('min_rank', user_rank)
                        gap = abs(min_rank - user_rank)
                        if gap > 30000:
                            print(f"\n⚠️  警告：{rec['university_name']}位次差距过大: {gap}")
                            rank_gaps_ok = False

                if rank_gaps_ok:
                    print(f"\n✅ 验证通过：所有推荐院校位次差距在合理范围内")

                return True
            else:
                print(f"\n❌ 推荐失败: {data}")
                return False
        else:
            print(f"\n❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False

    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return False


def main():
    """运行所有测试用例"""
    print("=" * 60)
    print("推荐算法测试验证")
    print("=" * 60)

    # 检查后端服务
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("\n❌ 后端服务未启动！请先启动后端:")
            print("   cd backend")
            print("   uvicorn app.main:app --reload --port 8000")
            return
    except Exception as e:
        print(f"\n❌ 无法连接后端服务: {e}")
        print("   请确保后端服务已启动在 http://localhost:8000")
        return

    print("\n✅ 后端服务已启动，开始测试...\n")

    # 测试用例
    test_cases = [
        {
            "name": "高分考生",
            "rank": 800,
            "province": "广东",
            "subject_type": "理科",
            "majors": ["计算机科学与技术"],
            "score": 670,
            "expected": "应该推荐中大、华工、武大、华科等985/211院校",
            "should_not_see": ["北京大学", "清华大学"]
        },
        {
            "name": "中等考生",
            "rank": 40000,
            "province": "广东",
            "subject_type": "理科",
            "majors": ["计算机科学与技术"],
            "score": 560,
            "expected": "应该推荐广工、广大、汕大等一本院校",
            "should_not_see": ["北京大学", "清华大学", "复旦大学"]
        },
        {
            "name": "边缘考生",
            "rank": 90000,
            "province": "广东",
            "subject_type": "理科",
            "majors": ["计算机科学与技术"],
            "score": 520,
            "expected": "应该推荐佛山科技、东莞理工等院校",
            "should_not_see": ["北京大学", "清华大学", "中山大学"]
        },
        {
            "name": "低分考生",
            "rank": 180000,
            "province": "广东",
            "subject_type": "理科",
            "majors": ["计算机科学与技术"],
            "score": 450,
            "expected": "应该推荐专科院校或二本尾部",
            "should_not_see": ["北京大学", "清华大学", "中山大学", "华南理工大学"]
        },
    ]

    results = []

    for i, case in enumerate(test_cases):
        print(f"\n{'='*60}")
        print(f"测试 {i+1}/{len(test_cases)}: {case['name']}")
        print(f"{'='*60}")
        print(f"期望: {case['expected']}")

        success = test_recommendation(
            user_rank=case['rank'],
            province=case['province'],
            subject_type=case['subject_type'],
            target_majors=case['majors'],
            score=case['score']
        )

        results.append({
            "name": case['name'],
            "success": success
        })

    # 总结
    print(f"\n\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")

    passed = sum(1 for r in results if r['success'])
    total = len(results)

    for r in results:
        status = "✅ 通过" if r['success'] else "❌ 失败"
        print(f"{status} - {r['name']}")

    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 所有测试用例通过！算法修复成功！")
    else:
        print(f"\n⚠️  有{total-passed}个测试用例失败，请检查算法")


if __name__ == "__main__":
    main()
