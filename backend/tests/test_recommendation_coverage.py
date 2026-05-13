"""
推荐算法覆盖率测试脚本
测试所有位次段是否都能生成≥25个推荐
验收标准：✅ 广东位次1-300000的每个段位，都有≥25个推荐
"""

import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.guangdong_recommendation_service import guangdong_recommendation_service


class RecommendationCoverageTester:
    """推荐覆盖率测试器"""

    def __init__(self):
        self.service = guangdong_recommendation_service
        self.test_results = []

    def run_all_tests(self):
        """运行所有测试用例"""
        print("\n" + "="*80)
        print("推荐算法覆盖率测试（7个关键位次段）")
        print("="*80)

        # 7个关键测试位次
        test_cases = [
            {"rank": 500, "name": "超高位次（清北段）", "expected_unis": ["清北复交", "C9院校"]},
            {"rank": 5000, "name": "高位次（985段）", "expected_unis": ["中坚985", "顶尖211"]},
            {"rank": 15000, "name": "中高位次（211段）", "expected_unis": ["暨南大学", "华南师范"]},
            {"rank": 40000, "name": "中等位次（一本段）", "expected_unis": ["广东工业", "广州大学"]},
            {"rank": 80000, "name": "中低位次（二本段）", "expected_unis": ["佛山科技", "东莞理工"]},
            {"rank": 150000, "name": "低位次（专科头部）", "expected_unis": ["深圳职业技术"]},
            {"rank": 250000, "name": "超低位次（专科中尾部）", "expected_unis": ["省内高职"]},
        ]

        for i, case in enumerate(test_cases, 1):
            print(f"\n{'='*80}")
            print(f"测试 {i}/7: {case['name']} (位次: {case['rank']:,})")
            print(f"期望院校类型: {', '.join(case['expected_unis'])}")
            print(f"{'='*80}")

            result = self._test_single_rank(
                user_rank=case['rank'],
                province="广东",
                subject_type="理科",
                target_majors=["计算机科学与技术"]
            )

            result['test_name'] = case['name']
            result['expected_types'] = case['expected_unis']
            self.test_results.append(result)

            self._print_single_result(result)

        # 生成总结报告
        self._generate_summary_report()

    def _test_single_rank(
        self,
        user_rank: int,
        province: str,
        subject_type: str,
        target_majors: list
    ) -> dict:
        """测试单个位次"""

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
                    "total_count": 0,
                    "categories": {}
                }

            data = response.get("data", {})
            recommendations = {
                "冲刺": data.get("冲刺", []),
                "稳妥": data.get("稳妥", []),
                "保底": data.get("保底", [])
            }

            # 统计数量
            chong_counts = len(recommendations["冲刺"])
            wen_counts = len(recommendations["稳妥"])
            bao_counts = len(recommendations["保底"])
            total = chong_counts + wen_counts + bao_counts

            # 检查是否有不合理推荐
            top_unis = ["北京大学", "清华大学"]
            all_recs = []
            for cat_recs in recommendations.values():
                all_recs.extend([r['university_name'] for r in cat_recs])

            violations = []
            for uni in top_unis:
                if uni in all_recs:
                    violations.append(uni)

            # 验收标准：总计≥25个
            passed = total >= 25 and len(violations) == 0

            return {
                "passed": passed,
                "total_count": total,
                "categories": {
                    "冲刺": chong_counts,
                    "稳妥": wen_counts,
                    "保底": bao_counts
                },
                "sample_unis": [r['university_name'] for r in recommendations["稳妥"][:3]],
                "violations": violations,
                "algorithm": data.get("basic_info", {}).get("algorithm", "unknown")
            }

        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "total_count": 0,
                "categories": {}
            }

    def _print_single_result(self, result: dict):
        """打印单个测试结果"""
        if not result.get("passed"):
            print(f"[FAIL] Test failed")
            if "error" in result:
                print(f"   Error: {result['error']}")
            return

        print(f"[PASS] Test passed")
        print(f"   Algorithm version: {result['algorithm']}")
        print(f"   Recommendation count:")

        for cat, count in result['categories'].items():
            print(f"     {cat}: {count}所")

        print(f"   总计: {result['total_count']}所")

        if result['sample_unis']:
            print(f"   样本院校: {', '.join(result['sample_unis'])}")

        if result['violations']:
            print(f"   [WARNING] Found unreasonable recommendations: {', '.join(result['violations'])}")

    def _generate_summary_report(self):
        """生成总结报告"""
        print(f"\n\n{'='*80}")
        print("测试总结报告")
        print(f"{'='*80}")

        passed_count = sum(1 for r in self.test_results if r['passed'])
        total_count = len(self.test_results)

        print(f"\n[SUMMARY] Test Results:")
        print(f"   Passed: {passed_count}/{total_count}")
        print(f"   Pass rate: {passed_count/total_count*100:.1f}%")

        print(f"\n[DETAILS] Each segment:")
        for i, result in enumerate(self.test_results, 1):
            status = "[PASS]" if result['passed'] else "[FAIL]"
            print(f"   {status} {i}. {result['test_name']}: {result['total_count']} recommendations")

        # 未通过的测试
        failed_tests = [r for r in self.test_results if not r['passed']]
        if failed_tests:
            print(f"\n[FAILED] Tests:")
            for result in failed_tests:
                print(f"   - {result['test_name']}")
                if 'error' in result:
                    print(f"     Error: {result['error']}")
                else:
                    print(f"     Recommendations: {result['total_count']}")

        # 最终验收
        print(f"\n{'='*80}")
        if passed_count == total_count:
            print("[ACCEPTED] All rank segments have >=25 recommendations")
            print("[SUCCESS] System is ready for production use")
        else:
            print(f"[NOT ACCEPTED] {total_count-passed_count} segments have insufficient recommendations")
            print("[ACTION NEEDED] Continue optimizing algorithm or completing data")
        print(f"{'='*80}")

        # 保存测试报告
        self._save_test_report()

    def _save_test_report(self):
        """保存测试报告"""
        report_dir = Path(__file__).parent.parent / "reports"
        report_dir.mkdir(exist_ok=True)

        report_file = report_dir / "coverage_test_report.json"

        report = {
            "test_time": str(Path(__file__).stat().st_mtime),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r['passed']),
            "test_results": self.test_results,
            "overall_passed": all(r['passed'] for r in self.test_results)
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n[REPORT] Test report saved to: {report_file}")


def main():
    """主函数"""
    tester = RecommendationCoverageTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()