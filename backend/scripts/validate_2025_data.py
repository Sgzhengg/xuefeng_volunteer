"""
2025年数据验证脚本
检查系统中2025年数据的完整性，为缺失数据制定采集计划

验收标准：
- 广东：必须有完整的投档线和位次数据
- 主要省份（湖南、江西、广西、湖北）：至少要有投档线数据
- 其他省份：至少要有核心院校数据
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import sys


class DataValidator2025:
    """2025年数据验证器"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "provinces": {},
            "recommendations": []
        }

    def validate_all(self):
        """执行所有验证检查"""
        print("\n" + "="*80)
        print("2025年数据完整性验证")
        print("="*80)

        # 检查1：数据文件存在性
        print("\n[检查1] 数据文件存在性检查...")
        self._check_file_existence()

        # 检查2：广东数据完整性（P0）
        print("\n[检查2] 广东数据完整性检查（P0）...")
        self._validate_guangdong_data()

        # 检查3：主要省份数据检查
        print("\n[检查3] 主要省份数据检查...")
        self._validate_key_provinces()

        # 检查4：其他省份核心数据检查
        print("\n[检查4] 其他省份核心数据检查...")
        self._validate_other_provinces()

        # 检查5：数据年份一致性
        print("\n[检查5] 数据年份一致性检查...")
        self._validate_year_consistency()

        # 生成报告
        self._generate_report()

    def _check_file_existence(self):
        """检查必要的数据文件是否存在"""
        required_files = [
            "major_rank_data.json",
            "universities_list.json",
            "low_rank_admission_data.json",
            "outprovince_admission_data.json"
        ]

        for filename in required_files:
            file_path = self.data_dir / filename
            exists = file_path.exists()
            status = "[OK]" if exists else "[MISSING]"
            print(f"  {status} {filename}")

            if not exists:
                self.validation_results["recommendations"].append({
                    "priority": "P0",
                    "issue": f"缺少必要数据文件: {filename}",
                    "action": "立即采集或生成该文件"
                })

    def _validate_guangdong_data(self):
        """验证广东数据完整性（P0优先级）"""
        guangdong_status = {
            "status": "unknown",
            "admission_scores": False,
            "rank_tables": False,
            "universities": 0,
            "majors": 0,
            "score_range": None,
            "rank_range": None,
            "issues": []
        }

        # 检查major_rank_data.json中的广东数据
        try:
            with open(self.data_dir / "major_rank_data.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_records = data.get("major_rank_data", [])

            # 提取广东数据
            guangdong_records = [r for r in all_records if r.get("province") == "广东"]

            if not guangdong_records:
                guangdong_status["issues"].append("未找到广东省录取数据")
                guangdong_status["status"] = "FAIL"
            else:
                guangdong_status["admission_scores"] = True
                guangdong_status["universities"] = len(set(r.get("university_name") for r in guangdong_records))
                guangdong_status["majors"] = len(guangdong_records)

                # 检查位次范围
                ranks = [r.get("min_rank", 0) for r in guangdong_records if r.get("min_rank")]
                if ranks:
                    guangdong_status["rank_range"] = f"{min(ranks):,}-{max(ranks):,}"
                    guangdong_status["rank_tables"] = True

                # 检查数据年份
                years = set(r.get("year", 0) for r in guangdong_records if r.get("year"))
                if 2025 in years:
                    guangdong_status["status"] = "OK"
                    print(f"  [OK] 广东数据完整：{guangdong_status['universities']}所院校，{guangdong_status['majors']}条专业记录")
                else:
                    guangdong_status["issues"].append("广东数据缺少2025年记录")
                    guangdong_status["status"] = "WARNING"

        except Exception as e:
            guangdong_status["status"] = "ERROR"
            guangdong_status["issues"].append(f"数据读取失败: {str(e)}")

        self.validation_results["provinces"]["广东"] = guangdong_status

        # 生成广东数据检查报告
        if guangdong_status["status"] != "OK":
            print(f"  [{guangdong_status['status']}] 广东数据检查未通过")
            for issue in guangdong_status["issues"]:
                print(f"    ⚠️ {issue}")
                self.validation_results["recommendations"].append({
                    "priority": "P0",
                    "issue": f"广东数据问题: {issue}",
                    "action": "从广东省教育考试院采集2025年投档线和位次数据"
                })
        else:
            print(f"  [OK] 广东位次范围: {guangdong_status['rank_range']}")

    def _validate_key_provinces(self):
        """验证主要省份数据"""
        key_provinces = ["湖南", "江西", "广西", "湖北", "福建", "四川", "重庆", "云南", "贵州", "海南"]

        try:
            with open(self.data_dir / "major_rank_data.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_records = data.get("major_rank_data", [])

            for province in key_provinces:
                province_records = [r for r in all_records if r.get("province") == province]

                if not province_records:
                    print(f"  [MISSING] {province}: 无数据")
                    self.validation_results["recommendations"].append({
                        "priority": "P1",
                        "issue": f"{province}省缺少数据",
                        "action": f"从{province}省教育考试院采集2025年投档线数据"
                    })
                else:
                    universities = len(set(r.get("university_name") for r in province_records))
                    years = set(r.get("year", 0) for r in province_records if r.get("year"))
                    has_2025 = 2025 in years

                    status = "OK" if has_2025 else "WARNING"
                    year_info = f"含2025年数据" if has_2025 else f"缺少2025年数据"
                    print(f"  [{status}] {province}: {universities}所院校，{year_info}")

                    if not has_2025:
                        self.validation_results["recommendations"].append({
                            "priority": "P1",
                            "issue": f"{province}省缺少2025年数据",
                            "action": f"从{province}省教育考试院采集2025年投档线"
                        })

                self.validation_results["provinces"][province] = {
                    "universities": len(province_records) if province_records else 0,
                    "has_2025_data": 2025 in set(r.get("year", 0) for r in province_records if r.get("year"))
                }

        except Exception as e:
            print(f"  [ERROR] 主要省份检查失败: {str(e)}")

    def _validate_other_provinces(self):
        """验证其他省份核心数据"""
        print("  检查全国31省份覆盖率...")

        try:
            with open(self.data_dir / "major_rank_data.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_records = data.get("major_rank_data", [])

            provinces = set(r.get("province") for r in all_records if r.get("province"))
            coverage = len(provinces)

            print(f"    当前覆盖: {coverage}/31个省份")

            if coverage < 20:
                print(f"    [WARNING] 覆盖率偏低，建议补充更多省份数据")
                self.validation_results["recommendations"].append({
                    "priority": "P2",
                    "issue": f"全国省份数据覆盖不足: {coverage}/31",
                    "action": "从阳光高考网采集其他省份核心院校2025年数据"
                })

            # 检查核心985/211院校覆盖
            top_universities = [
                "北京大学", "清华大学", "复旦大学", "上海交通大学", "浙江大学",
                "南京大学", "中国科学技术大学", "中山大学", "华南理工大学"
            ]

            missing_top = []
            for uni in top_universities:
                uni_records = [r for r in all_records if r.get("university_name") == uni]
                if not uni_records:
                    missing_top.append(uni)

            if missing_top:
                print(f"    [WARNING] 缺少顶尖院校数据: {', '.join(missing_top)}")
                self.validation_results["recommendations"].append({
                    "priority": "P1",
                    "issue": f"缺少顶尖院校数据: {len(missing_top)}所",
                    "action": "从阳光高考网补全顶尖院校2025年录取数据"
                })

        except Exception as e:
            print(f"    [ERROR] 其他省份检查失败: {str(e)}")

    def _validate_year_consistency(self):
        """验证数据年份一致性"""
        try:
            with open(self.data_dir / "major_rank_data.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_records = data.get("major_rank_data", [])

            # 统计各年份数据量
            year_distribution = defaultdict(int)
            for record in all_records:
                year = record.get("year", 0)
                if year:
                    year_distribution[year] += 1

            print("  数据年份分布:")
            for year in sorted(year_distribution.keys()):
                count = year_distribution[year]
                print(f"    {year}年: {count:,}条记录")

            # 检查是否有2025年数据
            if 2025 not in year_distribution:
                print("    [WARNING] 系统中缺少2025年数据")
                self.validation_results["recommendations"].append({
                    "priority": "P0",
                    "issue": "系统中缺少2025年录取数据",
                    "action": "立即启动2025年数据采集工作"
                })
            else:
                count_2025 = year_distribution[2025]
                print(f"    [OK] 2025年数据: {count_2025:,}条记录")

        except Exception as e:
            print(f"    [ERROR] 年份一致性检查失败: {str(e)}")

    def _generate_report(self):
        """生成验证报告"""
        print("\n" + "="*80)
        print("验证报告总结")
        print("="*80)

        # 统计问题数量
        p0_count = sum(1 for r in self.validation_results["recommendations"] if r.get("priority") == "P0")
        p1_count = sum(1 for r in self.validation_results["recommendations"] if r.get("priority") == "P1")
        p2_count = sum(1 for r in self.validation_results["recommendations"] if r.get("priority") == "P2")

        print(f"\n发现问题统计:")
        print(f"  P0（紧急）: {p0_count}个")
        print(f"  P1（重要）: {p1_count}个")
        print(f"  P2（一般）: {p2_count}个")

        # 优先处理P0问题
        if p0_count > 0:
            print(f"\n[紧急] 需要立即处理的P0问题:")
            for rec in self.validation_results["recommendations"]:
                if rec.get("priority") == "P0":
                    print(f"  ⚠️ {rec['issue']}")
                    print(f"     行动: {rec['action']}")

        # 保存报告
        report_file = self.base_dir / "reports" / f"validation_2025_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, ensure_ascii=False, indent=2)

        print(f"\n验证报告已保存: {report_file}")

        # 设置总体状态
        if p0_count == 0 and p1_count == 0:
            self.validation_results["overall_status"] = "OK"
            print("\n[SUCCESS] 2025年数据验证通过，可以投入使用")
        elif p0_count == 0:
            self.validation_results["overall_status"] = "ACCEPTABLE"
            print("\n[WARNING] 2025年数据基本可用，建议尽快处理P1问题")
        else:
            self.validation_results["overall_status"] "NOT_ACCEPTABLE"
            print("\n[ALERT] 2025年数据不完整，必须立即处理P0问题")

        print("="*80)


def main():
    """主函数"""
    validator = DataValidator2025()

    try:
        validator.validate_all()

        # 根据验证结果设置退出码
        if validator.validation_results["overall_status"] == "NOT_ACCEPTABLE":
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"\n[ERROR] 验证过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()