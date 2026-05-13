"""
广东录取数据完整性验证脚本
验证数据覆盖率和质量
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class DataCoverageValidator:
    """数据覆盖率验证器"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.admission_file = self.data_dir / "guangdong_admission_2024.json"
        self.majors_file = self.data_dir / "university_majors.json"
        self.universities_file = self.data_dir / "universities_list.json"

    def validate_all(self):
        """执行所有验证"""
        print("\n" + "="*70)
        print("广东录取数据完整性验证")
        print("="*70)

        # 加载数据
        admission_data = self._load_data()

        # 验证各项指标
        results = {}

        results["university_count"] = self._validate_university_count(admission_data)
        results["batch_coverage"] = self._validate_batch_coverage(admission_data)
        results["rank_coverage"] = self._validate_rank_coverage(admission_data)
        results["major_coverage"] = self._validate_major_coverage(admission_data)
        results["data_consistency"] = self._validate_data_consistency(admission_data)

        # 生成报告
        self._generate_report(results, admission_data)

        # 检查是否通过
        all_passed = all(r["passed"] for r in results.values())

        if all_passed:
            print("\n" + "="*70)
            print("✅ 验证通过！数据完整性满足要求。")
            print("="*70)
        else:
            print("\n" " + "="*70)
            print("⚠️ 验证未通过！存在数据缺口，需要继续补全。")
            print("="*70)

        return all_passed

    def _load_data(self) -> List[Dict[str, Any]]:
        """加载数据"""
        if not self.admission_file.exists():
            print(f"❌ 数据文件不存在: {self.admission_file}")
            print("请先运行数据导入脚本: python scripts/import_admission_data.py")
            return []

        with open(self.admission_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data.get("data", [])

    def _validate_university_count(self, data: List[Dict[str, Any]]) -> Dict:
        """验证院校数量"""
        print("\n【验证1】院校数量")

        # 统计唯一院校
        universities = set()
        for record in data:
            universities.add(record.get("university_name", ""))

        total_count = len(universities)

        # 按类型统计
        type_count = defaultdict(int)
        for record in data:
            utype = record.get("university_type", "未知")
            type_count[utype] += 1

        print(f"  总院校数: {total_count}所")
        print(f"\n  按类型分布:")
        for utype, count in sorted(type_count.items()):
            print(f"    {utype}: {count}所")

        # 验证标准
        passed = total_count >= 250

        print(f"\n  验收标准: ≥250所")
        print(f"  状态: {'✅ 通过' if passed else '❌ 未通过'}")

        return {"passed": passed, "count": total_count, "detail": dict(type_count)}

    def _validate_batch_coverage(self, data: List[Dict[str, Any]]) -> Dict:
        """验证批次覆盖"""
        print("\n【验证2】批次覆盖")

        batches = set()
        for record in data:
            batch = record.get("batch", "")
            if batch:
                batches.add(batch)

        print(f"  覆盖批次: {', '.join(sorted(batches))}")

        passed = "本科批" in batches and "专科批" in batches

        print(f"\n  验收标准: 必须包含本科批和专科批")
        print(f"  状态: {'✅ 通过' if passed else '❌ 未通过'}")

        return {"passed": passed, "batches": list(batches)}

    def _validate_rank_coverage(self, data: List[Dict[str, Any]]) -> Dict:
        """验证位次覆盖范围"""
        print("\n【验证3】位次覆盖范围")

        ranks = [r.get("min_rank", 0) for r in data if r.get("min_rank")]

        if not ranks:
            print("  ❌ 没有位次数据")
            return {"passed": False, "min_rank": 0, "max_rank": 0}

        min_rank = min(ranks)
        max_rank = max(ranks)

        print(f"  位次范围: {min_rank:,} - {max_rank:,}")

        # 检查连续性
        gaps = self._find_rank_gaps(sorted(ranks))

        if gaps:
            print(f"\n  ⚠️ 发现位次缺口:")
            for gap in gaps[:5]:  # 只显示前5个
                print(f"    {gap['start']:,} - {gap['end']:,}: 缺失 {gap['count']} 条")
        else:
            print(f"  ✅ 位次覆盖连续（1-{max_rank:,}）")

        passed = max_rank >= 300000

        print(f"\n  验收标准: 最高位次 ≥ 300000")
        print(f"  状态: {'✅ 通过' if passed else '❌ 未通过'}")

        return {"passed": passed, "min_rank": min_rank, "max_rank": max_rank, "gaps": gaps}

    def _validate_major_coverage(self, data: List[Dict[str, Any]]) -> Dict:
        """验证专业覆盖"""
        print("\n【验证4】专业覆盖")

        # 统计每个院校的专业数
        uni_majors = defaultdict(int)
        for record in data:
            uni = record.get("university_name", "")
            uni_majors[uni] += 1

        # 计算平均专业数
        if uni_majors:
            avg_majors = sum(uni_majors.values()) / len(uni_majors)
        else:
            avg_majors = 0

        print(f"  平均每校专业数: {avg_majors:.1f}")

        # 检查专业数少于10的院校
        low_majors = [uni for uni, count in uni_majors.items() if count < 10]

        if low_majors:
            print(f"\n  ⚠️ 以下院校专业数 < 10:")
            for uni, count in low_majors[:10]:
                print(f"    {uni}: {count}个专业")

        # 统计热门专业覆盖
        popular_majors = [
            "计算机科学与技术", "软件工程", "电子信息工程",
            "电气工程", "自动化", "临床医学", "口腔医学",
            "金融学", "会计学", "工商管理"
        ]

        major_coverage = defaultdict(int)
        for record in data:
            major = record.get("major_name", "")
            if major in popular_majors:
                major_coverage[major] += 1

        print(f"\n  热门专业覆盖:")
        for major, count in sorted(major_coverage.items(), key=lambda x: -x[1])[:5]:
            print(f"    {major}: {count}个院校")

        passed = avg_majors >= 10

        print(f"\n  验收标准: 平均每校 ≥ 10个专业")
        print(f"  状态: {'✅ 通过' if passed else '❌ 未通过'}")

        return {"passed": passed, "avg_majors": avg_majors}

    def _validate_data_consistency(self, data: List[Dict[str, Any]]) -> Dict:
        """验证数据一致性"""
        print("\n【验证5】数据一致性")

        issues = []

        # 检查不合理数据
        for record in data:
            rank = record.get("min_rank", 0)
            score = record.get("min_score", 0)

            # 位次和分数的关系检查（粗略）
            if score > 0 and rank > 0:
                # 分数625对应位次大约在10000-20000
                if score > 650 and rank > 50000:
                    issues.append(f"{record['university_name']} {record['major_name']}: 高分低排名次异常")
                elif score < 500 and rank < 10000:
                    issues.append(f"{record['university_name']} {record['major_name']}: 低分高排名次异常")

        if issues:
            print(f"  ⚠️ 发现 {len(issues)} 个数据异常:")
            for issue in issues[:5]:
                print(f"    - {issue}")
        else:
            print("  ✅ 数据一致性良好")

        passed = len(issues) == 0

        print(f"\n  验收标准: 无严重数据异常")
        print(f"  状态: {'✅ 通过' if passed else '❌ 未通过'}")

        return {"passed": passed, "issues": issues}

    def _find_rank_gaps(self, sorted_ranks: List[int]) -> List[Dict]:
        """发现位次缺口"""
        gaps = []

        for i in range(len(sorted_ranks) - 1):
            gap = sorted_ranks[i+1] - sorted_ranks[i]

            # 缺口超过1000认为是真正缺口
            if gap > 1000:
                gaps.append({
                    "start": sorted_ranks[i],
                    "end": sorted_ranks[i+1],
                    "count": (sorted_ranks[i+1] - sorted_ranks[i]) // 100  # 估算
                })

        return gaps

    def _generate_report(self, results: Dict, data: List[Dict[str, Any]]):
        """生成验证报告"""
        report = {
            "validation_time": datetime.now().isoformat(),
            "overall_status": "PASS" if all(r["passed"] for r in results.values()) else "FAIL",
            "results": results,
            "recommendations": self._generate_recommendations(results)
        }

        # 保存报告
        report_file = self.base_dir / "scripts" / "validation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n📄 验证报告已保存到: {report_file}")

    def _generate_recommendations(self, results: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 院校数量
        uni_count = results.get("university_count", {})
        if not uni_count.get("passed"):
            recommendations.append(
                "❌ 院校数量不足250所，需继续补全各层次院校数据"
            )

        # 批次覆盖
        batch = results.get("batch_coverage", {})
        if not batch.get("passed"):
            recommendations.append(
                "❌ 批次覆盖不全，需补充专科批数据"
            )

        # 位次覆盖
        rank = results.get("rank_coverage", {})
        if not rank.get("passed"):
            recommendations.append(
                f"❌ 位次覆盖不足，当前范围{rank['min_rank']:,}-{rank['max_rank']:,}，需扩展到300000位次"
            )

        # 专业覆盖
        major = results.get("major_coverage", {})
        if not major.get("passed"):
            recommendations.append(
                f"❌ 专业覆盖不足，平均每校{major['avg_majors']:.1f}个专业，需增加到≥10个"
            )

        return recommendations


def main():
    """主函数"""
    validator = DataCoverageValidator()
    validator.validate_all()


if __name__ == "__main__":
    main()
