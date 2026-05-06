"""
生成院校-专业关联表（university_majors）
基于现有数据整合生成，为专业级推荐奠定基础
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class UniversityMajorsGenerator:
    """院校-专业关联表生成器"""

    def __init__(self):
        self.data_dir = Path("data")
        self.university_majors = {}  # 使用字典去重，key为university_major_id

    def load_existing_data(self):
        """加载现有数据"""
        print("正在加载现有数据...")

        # 1. 从admission_plans.json加载
        self._load_from_admission_plans()

        # 2. 从major_admission_scores.json加载
        self._load_from_major_admission_scores()

        # 3. 补充院校和专业基本信息
        self._enrich_basic_info()

        print(f"数据加载完成，共生成{len(self.university_majors)}条院校-专业关联记录")

    def _load_from_admission_plans(self):
        """从admission_plans.json加载院校-专业关联"""
        print("正在从admission_plans.json加载数据...")

        try:
            with open(self.data_dir / "admission_plans.json", 'r', encoding='utf-8') as f:
                data = json.load(f)

            universities = data.get("universities", {})

            for university_id, university_info in universities.items():
                university_name = university_info.get("name", "")
                admission_plans = university_info.get("admission_plans", {})

                for province, plan_info in admission_plans.items():
                    major_plans = plan_info.get("major_plans", [])

                    for major_plan in major_plans:
                        major_code = major_plan.get("major_code", "")
                        major_name = major_plan.get("major_name", "")

                        if not major_code or not major_name:
                            continue

                        # 生成university_major_id
                        university_major_id = f"{university_id}_{major_code}"

                        # 获取专业类别（从major_code前2位推断）
                        major_category = self._infer_major_category(major_code)

                        record = {
                            "university_major_id": university_major_id,
                            "university_id": university_id,
                            "university_name": university_name,
                            "major_code": major_code,
                            "major_name": major_name,
                            "major_category": major_category,
                            "is_active": True,
                            "year": 2024,
                            "province": province,
                            "metadata": {
                                "tuition_fee": major_plan.get("tuition_fee", ""),
                                "duration": major_plan.get("duration", ""),
                                "subject_requirements": major_plan.get("subject_requirements", ""),
                                "quota": major_plan.get("quota", 0)
                            },
                            "data_source": "admission_plans"
                        }

                        self.university_majors[university_major_id] = record

            print(f"从admission_plans.json加载了{len([r for r in self.university_majors.values() if r['data_source'] == 'admission_plans'])}条记录")

        except FileNotFoundError:
            print("警告：admission_plans.json文件不存在")
        except Exception as e:
            print(f"加载admission_plans.json出错：{str(e)}")

    def _load_from_major_admission_scores(self):
        """从major_admission_scores.json加载院校-专业关联"""
        print("正在从major_admission_scores.json加载数据...")

        try:
            with open(self.data_dir / "major_admission_scores.json", 'r', encoding='utf-8') as f:
                data = json.load(f)

            majors = data.get("majors", {})

            for major_code, major_info in majors.items():
                major_name = major_info.get("name", "")
                major_category = major_info.get("category", "")
                provinces = major_info.get("provinces", {})

                for province, province_data in provinces.items():
                    years = [k for k in province_data.keys() if k.isdigit()]

                    if not years:
                        continue

                    latest_year = max(years)
                    year_data = province_data[latest_year]
                    scores = year_data.get("scores", [])

                    for score_entry in scores:
                        if not isinstance(score_entry, dict):
                            continue

                        university_name = score_entry.get("university", "")
                        entry_major = score_entry.get("major", "")

                        # 模糊匹配专业名称
                        if major_name not in entry_major and entry_major not in major_name:
                            continue

                        # 查找院校ID
                        university_id = self._find_university_id_by_name(university_name)
                        if not university_id:
                            # 如果找不到ID，使用临时ID
                            university_id = f"TEMP_{university_name}"

                        # 生成university_major_id
                        university_major_id = f"{university_id}_{major_code}"

                        # 如果已存在，跳过
                        if university_major_id in self.university_majors:
                            continue

                        record = {
                            "university_major_id": university_major_id,
                            "university_id": university_id,
                            "university_name": university_name,
                            "major_code": major_code,
                            "major_name": major_name,
                            "major_category": major_category,
                            "is_active": True,
                            "year": int(latest_year),
                            "province": province,
                            "metadata": {
                                "min_score": score_entry.get("min_score", 0),
                                "avg_score": score_entry.get("avg_score", 0)
                            },
                            "data_source": "major_admission_scores"
                        }

                        self.university_majors[university_major_id] = record

            print(f"从major_admission_scores.json加载了{len([r for r in self.university_majors.values() if r['data_source'] == 'major_admission_scores'])}条记录")

        except FileNotFoundError:
            print("警告：major_admission_scores.json文件不存在")
        except Exception as e:
            print(f"加载major_admission_scores.json出错：{str(e)}")

    def _enrich_basic_info(self):
        """补充院校和专业基本信息"""
        print("正在补充院校和专业基本信息...")

        # 加载院校列表
        try:
            with open(self.data_dir / "universities_list.json", 'r', encoding='utf-8') as f:
                uni_data = json.load(f)
            self.universities = {u["id"]: u for u in uni_data["universities"]}
        except:
            self.universities = {}

        # 加载专业列表
        try:
            with open(self.data_dir / "majors_list.json", 'r', encoding='utf-8') as f:
                major_data = json.load(f)
            self.majors = {m["code"]: m for m in major_data["majors"]}
        except:
            self.majors = {}

        print(f"加载了{len(self.universities)}所院校，{len(self.majors)}个专业的基本信息")

    def _infer_major_category(self, major_code: str) -> str:
        """从专业代码推断专业类别"""
        # 专业代码前2位代表学科门类
        category_mapping = {
            "01": "哲学", "02": "经济学", "03": "法学", "04": "教育学",
            "05": "文学", "06": "历史学", "07": "理学", "08": "工学",
            "09": "农学", "10": "医学", "11": "军事学", "12": "管理学",
            "13": "艺术学"
        }

        prefix = major_code[:2]
        return category_mapping.get(prefix, "其他")

    def _find_university_id_by_name(self, name: str) -> str:
        """根据院校名称查找ID"""
        if not hasattr(self, 'universities'):
            return None

        for uni_id, uni_info in self.universities.items():
            if uni_info["name"] == name:
                return uni_id

        return None

    def generate_statistics(self) -> Dict:
        """生成统计信息"""
        total_records = len(self.university_majors)

        # 按院校统计
        university_counts = defaultdict(int)
        for record in self.university_majors.values():
            university_counts[record["university_name"]] += 1

        # 按专业统计
        major_counts = defaultdict(int)
        for record in self.university_majors.values():
            major_counts[record["major_name"]] += 1

        # 按类别统计
        category_counts = defaultdict(int)
        for record in self.university_majors.values():
            category_counts[record["major_category"]] += 1

        return {
            "total_records": total_records,
            "total_universities": len(university_counts),
            "total_majors": len(major_counts),
            "total_categories": len(category_counts),
            "avg_majors_per_university": total_records / len(university_counts) if university_counts else 0,
            "university_distribution": dict(sorted(university_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "major_distribution": dict(sorted(major_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "category_distribution": dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True))
        }

    def save_to_file(self, output_path: str = None):
        """保存到文件"""
        if output_path is None:
            output_path = self.data_dir / "university_majors.json"

        # 按university_major_id排序
        sorted_records = sorted(self.university_majors.values(), key=lambda x: x["university_major_id"])

        # 生成统计信息
        statistics = self.generate_statistics()

        output_data = {
            "metadata": {
                "table_name": "university_majors",
                "description": "院校-专业关联表",
                "version": "1.0.0",
                "generated_at": "2026-04-30T12:00:00.000000",
                "total_records": statistics["total_records"],
                "total_universities": statistics["total_universities"],
                "total_majors": statistics["total_majors"],
                "target_records": 84000,
                "completion_rate": f"{statistics['total_records'] / 84000:.1%}"
            },
            "statistics": statistics,
            "university_majors": sorted_records
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"\n数据已保存到：{output_path}")
        print(f"\n统计信息：")
        print(f"- 总记录数：{statistics['total_records']:,}")
        print(f"- 院校数：{statistics['total_universities']:,}")
        print(f"- 专业数：{statistics['total_majors']:,}")
        print(f"- 专业类别数：{statistics['total_categories']:,}")
        print(f"- 每校平均专业数：{statistics['avg_majors_per_university']:.1f}")
        print(f"- 目标完成率：{statistics['total_records'] / 84000:.1%}")

        print(f"\n专业分布TOP10：")
        major_dist = statistics["major_distribution"]
        if isinstance(major_dist, dict):
            for i, (major, count) in enumerate(list(major_dist.items())[:10]):
                print(f"  {i+1}. {major}: {count}所院校")

        print(f"\n院校分布TOP10：")
        uni_dist = statistics["university_distribution"]
        if isinstance(uni_dist, dict):
            for i, (university, count) in enumerate(list(uni_dist.items())[:10]):
                print(f"  {i+1}. {university}: {count}个专业")

        print(f"\n类别分布：")
        category_dist = statistics["category_distribution"]
        if isinstance(category_dist, dict):
            for category, count in category_dist.items():
                print(f"  {category}: {count}个专业")


def main():
    """主函数"""
    print("=" * 60)
    print("院校-专业关联表生成器")
    print("=" * 60)

    generator = UniversityMajorsGenerator()

    # 加载现有数据
    generator.load_existing_data()

    # 保存到文件
    generator.save_to_file()

    print("\n[SUCCESS] 院校-专业关联表生成完成！")
    print("\n下一步：")
    print("1. 审阅生成的university_majors.json文件")
    print("2. 补充缺失的院校-专业关联（阳光高考网爬虫）")
    print("3. 整合专业录取位次数据")


if __name__ == "__main__":
    main()
