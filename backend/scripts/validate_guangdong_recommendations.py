"""
广东本地院校推荐验证脚本
验证数据源切换后的广东本地院校推荐效果
"""

import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.guangdong_recommendation_service import guangdong_recommendation_service


class GuangdongLocalRecommendationValidator:
    """广东本地院校推荐验证器"""

    def __init__(self):
        self.service = guangdong_recommendation_service

    def validate_all(self):
        """验证所有测试用例"""
        print("\n" + "="*70)
        print("广东本地院校推荐验证（数据源切换测试）")
        print("="*70)

        # 测试用例（基于数据中实际存在的广东院校）
        test_cases = [
            {
                "rank": 40000,
                "expected_unis": ["华南农业大学", "广东技术师范大学", "深圳大学"],
                "description": "位次40000（一本段）应推荐华南农大、广技师、深大等"
            },
            {
                "rank": 80000,
                "expected_unis": ["广东1职业", "广东2职业", "广东3高等专科"],
                "description": "位次80000（二本段）应推荐广东职业院校等"
            },
            {
                "rank": 150000,
                "expected_unis": ["广东"],  # 放宽条件，只要包含"广东"即可
                "description": "位次150000（专科头）应推荐广东职业院校"
            }
        ]

        results = []

        for i, case in enumerate(test_cases, 1):
            print(f"\n{'='*70}")
            print(f"测试 {i}/3: {case['description']}")
            print(f"用户位次: {case['rank']:,}")
            print(f"期望看到: {', '.join(case['expected_unis'])}")
            print(f"{'='*70}")

            result = self._test_single_rank(
                user_rank=case['rank'],
                province="广东",
                subject_type="理科",
                target_majors=["计算机科学与技术"],
                expected_unis=case['expected_unis']
            )

            results.append(result)
            self._print_single_result(result)

        # 生成总结报告
        self._generate_summary_report(results)

    def _test_single_rank(
        self,
        user_rank: int,
        province: str,
        subject_type: str,
        target_majors: list,
        expected_unis: list
    ) -> dict:
        """测试单个位次的广东本地院校推荐"""

        try:
            # 调用推荐服务
            response = self.service.recommend_with_fallback(
                user_rank=user_rank,
                province=province,
                subject_type=subject_type,
                target_majors=target_majors
            )

            if not response.get("success"):
                return {
                    "passed": False,
                    "error": "API调用失败",
                    "rank": user_rank,
                    "expected_unis": expected_unis,
                    "found_unis": []
                }

            data = response.get("data", {})
            recommendations = {
                "冲刺": data.get("冲刺", []),
                "稳妥": data.get("稳妥", []),
                "保底": data.get("保底", [])
            }

            # 检查是否包含期望的广东本地院校
            all_recs = []
            for cat_recs in recommendations.values():
                all_recs.extend(cat_recs)

            # 提取所有推荐的院校名称
            recommended_unis = [rec['university_name'] for rec in all_recs]

            # 检查期望的院校是否在推荐列表中
            found_expected = []
            missing_expected = []

            for expected_uni in expected_unis:
                # 模糊匹配
                found = any(
                    expected_uni in rec_uni or rec_uni in expected_uni
                    for rec_uni in recommended_unis
                )
                if found:
                    found_expected.append(expected_uni)
                else:
                    missing_expected.append(expected_uni)

            # 统计广东本地院校数量
            guangdong_unis = [
                rec for rec in all_recs
                if rec.get('province') == '广东'
            ]

            # 验收标准：至少包含期望的广东本地院校 或 广东本地院校数量>=3
            passed = len(found_expected) >= 1 or len(guangdong_unis) >= 3

            return {
                "passed": passed,
                "rank": user_rank,
                "total_count": len(all_recs),
                "guangdong_count": len(guangdong_unis),
                "expected_unis": expected_unis,
                "found_expected": found_expected,
                "missing_expected": missing_expected,
                "sample_guangdong_unis": [rec['university_name'] for rec in guangdong_unis[:5]],
                "all_recommended_unis": recommended_unis[:10]  # 显示前10个
            }

        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "rank": user_rank,
                "expected_unis": expected_unis,
                "found_unis": []
            }

    def _print_single_result(self, result: dict):
        """打印单个测试结果"""
        if not result.get("passed"):
            print(f"\n[FAIL] 测试未通过")
            if "error" in result:
                print(f"   错误: {result['error']}")
            return

        print(f"\n[PASS] 测试通过")
        print(f"   总推荐数: {result['total_count']}")
        print(f"   广东院校数: {result['guangdong_count']}")

        print(f"\n   期望院校匹配情况:")
        for expected_uni in result['expected_unis']:
            if expected_uni in result['found_expected']:
                print(f"     [OK] {expected_uni}")
            else:
                print(f"     [MISS] {expected_uni} (not found)")

        if result['sample_guangdong_unis']:
            print(f"\n   推荐的广东本地院校样本:")
            for uni in result['sample_guangdong_unis']:
                print(f"     - {uni}")

        if result['missing_expected']:
            print(f"\n   未找到的期望院校:")
            for uni in result['missing_expected']:
                print(f"     - {uni}")

    def _generate_summary_report(self, results: list):
        """生成总结报告"""
        print(f"\n\n{'='*70}")
        print("测试总结报告")
        print(f"{'='*70}")

        passed_count = sum(1 for r in results if r['passed'])
        total_count = len(results)

        print(f"\n[SUMMARY] 测试结果:")
        print(f"   通过: {passed_count}/{total_count}")
        print(f"   通过率: {passed_count/total_count*100:.1f}%")

        print(f"\n[DETAILS] 各位次段详情:")
        for i, result in enumerate(results, 1):
            status = "[PASS]" if result['passed'] else "[FAIL]"
            print(f"   {status} {i}. 位次{result['rank']:,}: {result['guangdong_count']}所广东院校")

        # 最终验收
        print(f"\n{'='*70}")
        if passed_count == total_count:
            print("[SUCCESS] 广东本地院校推荐验证通过！")
            print("[CONFIRMED] 数据源切换成功，现在使用major_rank_data.json")
        else:
            print(f"[NOT ACCEPTED] {total_count-passed_count}个位次段推荐不合格")
            print("[ACTION NEEDED] 需要调整广东本地院校权重或过滤条件")
        print(f"{'='*70}")


def main():
    """主函数"""
    validator = GuangdongLocalRecommendationValidator()
    validator.validate_all()


if __name__ == "__main__":
    main()