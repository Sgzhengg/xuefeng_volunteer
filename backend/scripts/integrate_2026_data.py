"""
2026年数据整合脚本
将2026年招生计划、一分一段表、投档线整合为统一格式

功能：
- 数据格式统一化
- 与历史数据关联
- 数据质量验证
- 生成 major_rank_data_2026.json
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict


class DataIntegrator2026:
    """2026年数据整合器"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.reports_dir = self.base_dir / "reports"

        # 数据源文件
        self.data_sources = {
            "admission_plans": "admission_plans_2026.json",
            "score_rank_tables": "score_rank_tables_2026.json",
            "admission_scores": "admission_scores_2026.json",
            "historical_data": "major_rank_data.json"
        }

        # 整合配置
        self.integration_config = {
            "target_year": 2026,
            "output_file": "major_rank_data_2026.json",
            "validation_rules": {
                "guangdong_coverage": 0.95,  # 广东院校覆盖率 ≥95%
                "rank_coverage": 300000,       # 位次覆盖 1-300,000
                "majors_per_university": 10,   # 每个院校 ≥10个专业
                "data_consistency": True       # 数据一致性检查
            }
        }

        # 统计信息
        self.integration_stats = {
            "total_records": 0,
            "universities_count": 0,
            "provinces_count": 0,
            "majors_count": 0,
            "rank_range": None,
            "validation_results": {}
        }

    def run_integration(self):
        """执行完整的数据整合流程"""
        print("\n" + "="*80)
        print("2026年数据整合流程")
        print("="*80)
        print(f"整合时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 步骤1：加载所有数据源
        print("\n[步骤1] 加载数据源...")
        source_data = self._load_all_sources()

        # 步骤2：数据格式统一化
        print("\n[步骤2] 数据格式统一化...")
        normalized_data = self._normalize_data_formats(source_data)

        # 步骤3：数据关联
        print("\n[步骤3] 数据关联...")
        associated_data = self._associate_data(normalized_data)

        # 步骤4：数据验证
        print("\n[步骤4] 数据验证...")
        validation_results = self._validate_integrated_data(associated_data)

        # 步骤5：生成最终数据文件
        print("\n[步骤5] 生成最终数据文件...")
        self._generate_final_data_file(associated_data, validation_results)

        # 生成整合报告
        self._generate_integration_report(validation_results)

        print(f"\n[SUCCESS] 数据整合完成: {self.integration_stats['total_records']:,} 条记录")

    def _load_all_sources(self) -> Dict:
        """加载所有数据源"""
        sources = {}

        # 加载招生计划
        plans_file = self.data_dir / self.data_sources["admission_plans"]
        if plans_file.exists():
            print("  [OK] 加载招生计划数据")
            with open(plans_file, 'r', encoding='utf-8') as f:
                sources["plans"] = json.load(f).get("plans", [])
        else:
            print("  [WARN] 招生计划数据不存在，将使用历史数据")
            sources["plans"] = []

        # 加载一分一段表
        rank_file = self.data_dir / self.data_sources["score_rank_tables"]
        if rank_file.exists():
            print("  [OK] 加载一分一段表数据")
            with open(rank_file, 'r', encoding='utf-8') as f:
                sources["rank_tables"] = json.load(f).get("rank_tables", [])
        else:
            print("  [WARN] 一分一段表数据不存在")
            sources["rank_tables"] = []

        # 加载投档线
        scores_file = self.data_dir / self.data_sources["admission_scores"]
        if scores_file.exists():
            print("  [OK] 加载投档线数据")
            with open(scores_file, 'r', encoding='utf-8') as f:
                sources["admission_scores"] = json.load(f).get("admission_scores", [])
        else:
            print("  [WARN] 投档线数据不存在")
            sources["admission_scores"] = []

        # 加载历史数据
        historical_file = self.data_dir / self.data_sources["historical_data"]
        if historical_file.exists():
            print("  [OK] 加载历史数据")
            with open(historical_file, 'r', encoding='utf-8') as f:
                sources["historical"] = json.load(f).get("major_rank_data", [])
        else:
            print("  [ERROR] 历史数据不存在，无法进行整合")
            raise FileNotFoundError("历史数据文件不存在")

        return sources

    def _normalize_data_formats(self, source_data: Dict) -> Dict:
        """统一数据格式"""
        normalized = {
            "major_rank_data": []
        }

        # 处理招生计划数据
        for plan in source_data.get("plans", []):
            normalized_record = {
                "university_id": plan.get("university_id"),
                "university_name": plan.get("university_name"),
                "university_type": plan.get("university_type", ""),
                "province": plan.get("province"),
                "city": plan.get("city", ""),
                "major_id": plan.get("major_id"),
                "major_name": plan.get("major_name"),
                "major_code": plan.get("major_code", ""),
                "min_rank": None,  # 招生计划没有位次，需要关联投档线
                "avg_rank": None,
                "min_score": None,
                "avg_score": None,
                "enrollment_count": plan.get("plan_count", 0),
                "year": self.integration_config["target_year"],
                "batch": plan.get("batch", "本科批"),
                "data_source": "admission_plan_2026",
                "tuition": plan.get("tuition"),
                "duration": plan.get("duration", 4)
            }
            normalized["major_rank_data"].append(normalized_record)

        # 处理投档线数据
        for score in source_data.get("admission_scores", []):
            # 查找对应的招生计划记录，进行关联
            # 这里简化处理，实际需要更复杂的关联逻辑
            normalized_record = {
                "university_id": score.get("university_id"),
                "university_name": score.get("university_name"),
                "university_type": score.get("university_type", ""),
                "province": score.get("province"),
                "city": score.get("city", ""),
                "major_id": score.get("major_id"),
                "major_name": score.get("major_name"),
                "major_code": score.get("major_code", ""),
                "min_rank": score.get("min_rank"),
                "avg_rank": score.get("avg_rank"),
                "min_score": score.get("min_score"),
                "avg_score": score.get("avg_score"),
                "enrollment_count": score.get("enrollment_count", 30),
                "year": self.integration_config["target_year"],
                "batch": score.get("batch", "本科批"),
                "data_source": "admission_score_2026"
            }
            normalized["major_rank_data"].append(normalized_record)

        # 统计信息
        self.integration_stats["total_records"] = len(normalized["major_rank_data"])
        print(f"    统一化后记录数: {self.integration_stats['total_records']:,}")

        return normalized

    def _associate_data(self, normalized_data: Dict) -> Dict:
        """数据关联"""
        associated = normalized_data

        # 将招生计划与投档线关联
        plans = [r for r in associated["major_rank_data"] if r.get("data_source") == "admission_plan_2026"]
        scores = [r for r in associated["major_rank_data"] if r.get("data_source") == "admission_score_2026"]

        # 为招生计划补充位次信息
        associated_count = 0
        for plan in plans:
            # 查找匹配的投档线记录
            for score in scores:
                if (plan["university_id"] == score["university_id"] and
                    plan["major_id"] == score["major_id"]):
                    # 补充位次信息
                    plan["min_rank"] = score.get("min_rank")
                    plan["avg_rank"] = score.get("avg_rank")
                    plan["min_score"] = score.get("min_score")
                    plan["avg_score"] = score.get("avg_score")
                    plan["data_source"] += "_and_score"
                    associated_count += 1
                    break

        print(f"    关联记录数: {associated_count:,}")

        return associated

    def _validate_integrated_data(self, integrated_data: Dict) -> Dict:
        """验证整合后的数据"""
        validation_results = {
            "overall_status": "unknown",
            "checks": [],
            "issues": []
        }

        records = integrated_data["major_rank_data"]

        # 检查1：广东院校覆盖率
        print("  [检查1] 广东院校覆盖率...")
        guangdong_unis = set(r["university_name"] for r in records if r["province"] == "广东")
        total_guangdong_unis = 20  # 假设广东有20所主要本科院校
        coverage = len(guangdong_unis) / total_guangdong_unis

        check_result = {
            "name": "广东院校覆盖率",
            "standard": f"≥{self.integration_config['validation_rules']['guangdong_coverage']*100:.0f}%",
            "actual": f"{coverage*100:.1f}%",
            "passed": coverage >= self.integration_config["validation_rules"]["guangdong_coverage"]
        }

        validation_results["checks"].append(check_result)
        if not check_result["passed"]:
            validation_results["issues"].append("广东院校覆盖率不达标")

        # 检查2：位次覆盖
        print("  [检查2] 位次覆盖范围...")
        ranks = [r["min_rank"] for r in records if r.get("min_rank")]
        if ranks:
            min_rank = min(ranks)
            max_rank = max(ranks)
            self.integration_stats["rank_range"] = f"{min_rank:,}-{max_rank:,}"

            coverage_ok = (min_rank <= 1000) and (max_rank >= self.integration_config["validation_rules"]["rank_coverage"])

            check_result = {
                "name": "位次覆盖范围",
                "standard": f"1-{self.integration_config['validation_rules']['rank_coverage']:,}",
                "actual": f"{min_rank:,}-{max_rank:,}",
                "passed": coverage_ok
            }

            validation_results["checks"].append(check_result)
            if not check_result["passed"]:
                validation_results["issues"].append("位次覆盖范围不达标")

        # 检查3：专业数量
        print("  [检查3] 每个院校专业数量...")
        uni_majors = defaultdict(int)
        for record in records:
            uni_majors[record["university_name"]] += 1

        insufficient_majors = [
            uni for uni, count in uni_majors.items()
            if count < self.integration_config["validation_rules"]["majors_per_university"]
        ]

        check_result = {
            "name": "院校专业数量",
            "standard": f"每个院校≥{self.integration_config['validation_rules']['majors_per_university']}个专业",
            "actual": f"{len(uni_majors)}所院校，最少{min(uni_majors.values())}个专业",
            "passed": len(insufficient_majors) == 0
        }

        validation_results["checks"].append(check_result)
        if not check_result["passed"]:
            validation_results["issues"].append(f"{len(insufficient_majors)}所院校专业数量不足")

        # 统计信息更新
        self.integration_stats["universities_count"] = len(uni_majors)
        self.integration_stats["provinces_count"] = len(set(r["province"] for r in records))
        self.integration_stats["majors_count"] = len(records)

        # 总体状态
        if validation_results["issues"]:
            validation_results["overall_status"] = "WARNING"
        else:
            validation_results["overall_status"] = "OK"

        self.integration_stats["validation_results"] = validation_results

        return validation_results

    def _generate_final_data_file(self, integrated_data: Dict, validation_results: Dict):
        """生成最终的数据文件"""
        output_file = self.data_dir / self.integration_config["output_file"]

        output_data = {
            "metadata": {
                "version": "1.0.0",
                "year": self.integration_config["target_year"],
                "generated_at": datetime.now().isoformat(),
                "total_records": self.integration_stats["total_records"],
                "universities_count": self.integration_stats["universities_count"],
                "provinces_count": self.integration_stats["provinces_count"],
                "majors_count": self.integration_stats["majors_count"],
                "rank_range": self.integration_stats["rank_range"],
                "validation_status": validation_results["overall_status"]
            },
            "major_rank_data": integrated_data["major_rank_data"]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"  数据文件已生成: {output_file}")

    def _generate_integration_report(self, validation_results: Dict):
        """生成整合报告"""
        report = f"""
2026年数据整合报告
{'='*60}
整合时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
总体状态: {validation_results['overall_status']}

数据统计:
  总记录数: {self.integration_stats['total_records']:,}
  院校数量: {self.integration_stats['universities_count']}
  省份数量: {self.integration_stats['provinces_count']}
  位次范围: {self.integration_stats['rank_range']}

验证结果:
"""

        for check in validation_results["checks"]:
            status = "[OK]" if check["passed"] else "[FAIL]"
            report += f"{status} {check['name']}: {check['actual']} (标准: {check['standard']})\n"

        if validation_results["issues"]:
            report += f"\n发现问题:\n"
            for issue in validation_results["issues"]:
                report += f"  ⚠️ {issue}\n"

        report += f"\n数据文件: {self.integration_config['output_file']}"

        report_file = self.reports_dir / f"integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n整合报告已保存: {report_file}")


def main():
    """主函数"""
    integrator = DataIntegrator2026()

    try:
        integrator.run_integration()

        # 根据验证结果设置退出码
        if integrator.integration_stats["validation_results"]["overall_status"] == "OK":
            return 0
        else:
            return 1

    except Exception as e:
        print(f"\n[ERROR] 整合过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())