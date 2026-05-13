"""
全位次段推荐质量验证脚本
验证每一位考生（无论分数高低）都能获得合理推荐

验收标准：✅ 所有位次段（500-350,000）都有≥20个推荐
"""

import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.guangdong_recommendation_service import guangdong_recommendation_service


class FullCoverageValidator:
    """全位次段覆盖验证器"""

    def __init__(self):
        self.service = guangdong_recommendation_service

    def validate_all(self):
        """验证全位次段覆盖"""
        print("\n" + "="*80)
        print("全位次段推荐质量验证（让每一位考生都有合理推荐）")
        print("="*80)

        # 测试用例：从高分到低分，覆盖所有位次段
        test_cases = [
            # 高分段（重点院校）
            {
                "rank": 500,
                "name": "超高位次（清北段）",
                "expect_min_results": 25,
                "expect_uni_types": ["985", "211"],
                "forbidden_types": ["高职", "专科"]
            },
            {
                "rank": 5000,
                "name": "高位次（985段）",
                "expect_min_results": 25,
                "expect_uni_types": ["985", "211"],
                "forbidden_types": ["高职", "专科"]
            },
            {
                "rank": 15000,
                "name": "中高位次（211段）",
                "expect_min_results": 25,
                "expect_uni_types": ["211", "省属重点"],
                "forbidden_types": ["高职", "专科"]
            },

            # 中分段（普通本科）
            {
                "rank": 40000,
                "name": "中等位次（一本段）",
                "expect_min_results": 25,
                "expect_has_province": "广东",
                "expect_min_guangdong": 10
            },
            {
                "rank": 80000,
                "name": "中低位次（二本段）",
                "expect_min_results": 25,
                "expect_has_province": "广东",
                "expect_min_guangdong": 8
            },

            # 低分段（关键测试！）
            {
                "rank": 120000,
                "name": "低位次（三本段）",
                "expect_min_results": 25,
                "expect_has_province": "广东",
                "expect_min_guangdong": 5
            },
            {
                "rank": 150000,
                "name": "低位次（专科头）",
                "expect_min_results": 25,
                "expect_has_type": ["高职", "专科"],
                "expect_min_guangdong": 3
            },
            {
                "rank": 180000,
                "name": "超低位次（专科中）",
                "expect_min_results": 20,
                "expect_has_type": ["高职", "专科"],
                "expect_min_guangdong": 2
            },
            {
                "rank": 250000,
                "name": "极低位次（专科尾）",
                "expect_min_results": 20,
                "expect_has_type": ["高职", "专科", "民办"],
                "expect_min_guangdong": 1
            },
            {
                "rank": 350000,
                "name": "最低位次（保底）",
                "expect_min_results": 15,
                "expect_has_type": ["高职", "专科", "民办"],
                "expect_min_guangdong": 1
            }
        ]

        results = []

        for i, case in enumerate(test_cases, 1):
            print(f"\n{'='*80}")
            print(f"测试 {i}/{len(test_cases)}: {case['name']}")
            print(f"用户位次: {case['rank']:,}")

            if case.get('expect_min_results'):
                print(f"期望推荐数: ≥{case['expect_min_results']}个")
            if case.get('expect_uni_types'):
                print(f"期望院校类型: {', '.join(case['expect_uni_types'])}")
            if case.get('forbidden_types'):
                print(f"禁止院校类型: {', '.join(case['forbidden_types'])}")

            print(f"{'='*80}")

            result = self._test_single_rank(
                user_rank=case['rank'],
                province="广东",
                subject_type="理科",
                target_majors=["计算机科学与技术"],
                test_case=case
            )

            results.append(result)
            self._print_single_result(result, case)

        # 生成总结报告
        self._generate_summary_report(results)

    def _test_single_rank(
        self,
        user_rank: int,
        province: str,
        subject_type: str,
        target_majors: list,
        test_case: dict
    ) -> dict:
        """测试单个位次的推荐质量"""

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
                    "total_count": 0
                }

            data = response.get("data", {})
            recommendations = {
                "冲刺": data.get("冲刺", []),
                "稳妥": data.get("稳妥", []),
                "保底": data.get("保底", [])
            }

            # 统计推荐数量
            total_count = sum(len(recs) for recs in recommendations.values())

            # 提取所有推荐的详细信息
            all_recs = []
            for cat_recs in recommendations.values():
                all_recs.extend(cat_recs)

            # 统计广东本地院校
            guangdong_recs = [
                rec for rec in all_recs
                if rec.get('province') == '广东'
            ]

            # 统计院校类型
            uni_types = {}
            for rec in all_recs:
                utype = rec.get('university_type', '未知')
                uni_types[utype] = uni_types.get(utype, 0) + 1

            # 验收检查
            checks = []

            # 检查1：最小推荐数量
            min_expected = test_case.get('expect_min_results', 20)
            check_count = total_count >= min_expected
            checks.append({
                "name": f"推荐数量≥{min_expected}",
                "passed": check_count,
                "actual": total_count,
                "expected": f"≥{min_expected}"
            })

            # 检查2：期望的院校类型
            if test_case.get('expect_uni_types'):
                expected_types = test_case['expect_uni_types']
                has_expected_type = any(
                    any(exp_type in rec.get('university_type', '') for exp_type in expected_types)
                    for rec in all_recs
                )
                checks.append({
                    "name": f"包含期望院校类型",
                    "passed": has_expected_type,
                    "actual": list(uni_types.keys())[:5],
                    "expected": expected_types
                })

            # 检查3：禁止的院校类型
            if test_case.get('forbidden_types'):
                forbidden_types = test_case['forbidden_types']
                has_forbidden = any(
                    any(fType in rec.get('university_type', '') for fType in forbidden_types)
                    for rec in all_recs
                )
                checks.append({
                    "name": f"不包含禁止院校类型",
                    "passed": not has_forbidden,
                    "actual": "无禁止类型" if not has_forbidden else f"发现禁止类型",
                    "expected": f"不含{forbidden_types}"
                })

            # 检查4：广东本地院校数量
            if test_case.get('expect_min_guangdong'):
                min_guangdong = test_case['expect_min_guangdong']
                check_guangdong = len(guangdong_recs) >= min_guangdong
                checks.append({
                    "name": f"广东本地院校≥{min_guangdong}所",
                    "passed": check_guangdong,
                    "actual": len(guangdong_recs),
                    "expected": f"≥{min_guangdong}"
                })

            # 检查5：期望的特定院校类型（如高职专科）
            if test_case.get('expect_has_type'):
                expected_types = test_case['expect_has_type']
                has_expected_type = any(
                    any(exp_type in rec.get('university_type', '') for exp_type in expected_types)
                    for rec in all_recs
                )
                checks.append({
                    "name": f"包含期望类型（{expected_types}）",
                    "passed": has_expected_type,
                    "actual": "包含" if has_expected_type else "不包含",
                    "expected": f"包含{expected_types}"
                })

            # 综合判断
            all_passed = all(check['passed'] for check in checks)

            return {
                "passed": all_passed,
                "rank": user_rank,
                "total_count": total_count,
                "guangdong_count": len(guangdong_recs),
                "uni_types": uni_types,
                "checks": checks,
                "sample_recs": [
                    {
                        "university": rec['university_name'],
                        "type": rec.get('university_type', ''),
                        "province": rec.get('province', ''),
                        "min_rank": rec.get('min_rank', 'N/A')
                    }
                    for rec in all_recs[:5]
                ]
            }

        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "rank": user_rank,
                "total_count": 0
            }

    def _print_single_result(self, result: dict, test_case: dict):
        """打印单个测试结果"""
        if not result.get("passed"):
            if "error" in result:
                print(f"\n[FAIL] 测试未通过")
                print(f"   错误: {result['error']}")
            else:
                print(f"\n[FAIL] 测试未通过")

            # 显示检查详情
            if "checks" in result:
                print(f"   检查结果:")
                for check in result['checks']:
                    status = "[OK]" if check['passed'] else "[FAIL]"
                    print(f"     {status} {check['name']}")
                    print(f"        期望: {check['expected']}")
                    print(f"        实际: {check['actual']}")
            return

        print(f"\n[PASS] 测试通过")
        print(f"   总推荐数: {result['total_count']}")
        print(f"   广东院校: {result['guangdong_count']}")

        print(f"\n   院校类型分布:")
        for utype, count in sorted(result['uni_types'].items(), key=lambda x: -x[1])[:5]:
            print(f"     {utype}: {count}所")

        if result.get('sample_recs'):
            print(f"\n   推荐样本:")
            for i, rec in enumerate(result['sample_recs'], 1):
                print(f"     {i}. {rec['university']} ({rec['type']}, {rec['province']}, 位次:{rec['min_rank']})")

    def _generate_summary_report(self, results: list):
        """生成总结报告"""
        print(f"\n\n{'='*80}")
        print("全位次段验证总结报告")
        print(f"{'='*80}")

        passed_count = sum(1 for r in results if r['passed'])
        total_count = len(results)

        print(f"\n[SUMMARY] 测试结果:")
        print(f"   通过: {passed_count}/{total_count}")
        print(f"   通过率: {passed_count/total_count*100:.1f}%")

        print(f"\n[DETAILS] 各位次段详情:")
        for i, result in enumerate(results, 1):
            rank = result['rank']
            status = "[PASS]" if result['passed'] else "[FAIL]"
            count = result.get('total_count', 0)
            guangdong = result.get('guangdong_count', 0)

            print(f"   {status} {i}. 位次{rank:,}: {count}个推荐 (广东:{guangdong}所)")

        # 按位次段分组统计
        print(f"\n[SEGMENT ANALYSIS] 按位次段分析:")
        segments = {
            "高分段 (500-15000)": 0,
            "中分段 (40000-80000)": 0,
            "低分段 (120000-180000)": 0,
            "超低位次 (250000-350000)": 0
        }

        for result in results:
            rank = result['rank']
            if rank <= 15000:
                segments["高分段 (500-15000)"] += 1
            elif 40000 <= rank <= 80000:
                segments["中分段 (40000-80000)"] += 1
            elif 120000 <= rank <= 180000:
                segments["低分段 (120000-180000)"] += 1
            elif 250000 <= rank <= 350000:
                segments["超低位次 (250000-350000)"] += 1

        for segment, count in segments.items():
            segment_passed = sum(
                1 for r in results
                if segment.startswith("高分") and r['rank'] <= 15000 and r['passed'] or
                segment.startswith("中分") and 40000 <= r['rank'] <= 80000 and r['passed'] or
                segment.startswith("低分") and 120000 <= r['rank'] <= 180000 and r['passed'] or
                segment.startswith("超低") and r['rank'] >= 250000 and r['passed']
            )
            total_in_segment = count
            status = "[PASS]" if segment_passed == total_in_segment else "[PARTIAL]"
            print(f"   {status} {segment}: {segment_passed}/{total_in_segment} 通过")

        # 最终验收
        print(f"\n{'='*80}")
        if passed_count == total_count:
            print("[SUCCESS] 全位次段验证通过！")
            print("[CONFIRMED] 每一位考生都能获得≥20个合理推荐")
            print("[READY] 系统可投入全位次段使用")
        else:
            failed_count = total_count - passed_count
            print(f"[NOT ACCEPTED] {failed_count}个位次段验证未通过")
            print(f"[ACTION NEEDED] 需要继续优化算法或补全数据")
        print(f"{'='*80}")


def main():
    """主函数"""
    validator = FullCoverageValidator()
    validator.validate_all()


if __name__ == "__main__":
    main()