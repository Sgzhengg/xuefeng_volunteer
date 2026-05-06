"""
为全国所有院校生成专业关联数据
将university_majors从298所扩展到全部2800所院校
"""

import json
from pathlib import Path
from typing import List, Dict
from collections import defaultdict


class AllUniversitiesMajorsExpander:
    """全国所有院校专业关联扩展器"""

    def __init__(self):
        script_dir = Path(__file__).parent
        self.data_dir = script_dir / "data"
        self.all_university_majors = []

    def load_data(self):
        """加载基础数据"""
        print("Loading base data...")

        # 加载院校列表
        with open(self.data_dir / "universities_list.json", 'r', encoding='utf-8') as f:
            uni_data = json.load(f)
        self.universities = uni_data["universities"]
        print(f"Loaded {len(self.universities)} universities")

        # 加载现有的院校-专业关联
        with open(self.data_dir / "university_majors.json", 'r', encoding='utf-8') as f:
            um_data = json.load(f)
        self.existing_university_majors = um_data["university_majors"]
        print(f"Loaded {len(self.existing_university_majors)} existing university-major records")

        # 加载专业列表
        with open(self.data_dir / "majors_list.json", 'r', encoding='utf-8') as f:
            majors_data = json.load(f)
        self.majors = majors_data["majors"]
        print(f"Loaded {len(self.majors)} majors")

        # 按院校ID分组现有记录
        self.existing_by_university = defaultdict(list)
        for um in self.existing_university_majors:
            self.existing_by_university[um['university_id']].append(um)

    def generate_all_universities_majors(self):
        """为全国所有院校生成专业关联数据"""
        print("\nGenerating majors for all universities...")

        total = len(self.universities)
        processed = 0

        for university in self.universities:
            university_id = university["id"]
            university_name = university["name"]
            university_level = university.get("level", "普通本科")
            university_type = university.get("type", "综合")
            university_province = university.get("province", "")

            # 检查是否已有专业关联
            if university_id in self.existing_by_university:
                # 保留现有数据
                self.all_university_majors.extend(self.existing_by_university[university_id])
            else:
                # 为该院校生成专业关联
                majors = self._generate_majors_for_university(
                    university_id, university_name, university_level,
                    university_type, university_province
                )
                self.all_university_majors.extend(majors)

            processed += 1
            if processed % 100 == 0:
                print(f"Processed {processed}/{total} universities...")

        print(f"\nGenerated {len(self.all_university_majors)} university-major records")

    def _generate_majors_for_university(self, university_id: str, university_name: str,
                                       university_level: str, university_type: str,
                                       university_province: str) -> List[Dict]:
        """为某个院校生成专业关联数据"""
        majors = []

        # 根据院校类型和层次确定专业列表
        major_list = self._get_major_list(university_level, university_type)

        # 为每个专业生成关联记录
        for major_code, major_name, major_category in major_list:
            record = {
                "university_major_id": f"{university_id}_{major_code}",
                "university_id": university_id,
                "university_name": university_name,
                "university_level": university_level,
                "university_type": university_type,
                "university_province": university_province,
                "major_code": major_code,
                "major_name": major_name,
                "major_category": major_category,
                "is_active": True,
                "year": 2024,
                "metadata": {
                    "tuition_fee": self._estimate_tuition_fee(major_category, university_level),
                    "duration": self._estimate_duration(major_category),
                    "subject_requirements": self._estimate_subject_requirements(major_category)
                },
                "data_source": "generated_for_all_universities"
            }
            majors.append(record)

        return majors

    def _get_major_list(self, university_level: str, university_type: str) -> List[tuple]:
        """
        根据院校层次和类型获取专业列表

        Returns:
            List of (major_code, major_name, major_category) tuples
        """
        # 从majors_list.json读取所有专业，按类别分组
        majors_by_category = defaultdict(list)
        for major in self.majors:
            category = major.get("category", "其他")
            majors_by_category[category].append(
                (major["code"], major["name"], category)
            )

        # 根据院校层次和类型确定专业数量和类别
        if university_level == "985":
            # 985院校：专业最齐全
            categories = list(majors_by_category.keys())
            majors_per_category = 30
        elif university_level == "211":
            # 211院校：专业较齐全
            categories = list(majors_by_category.keys())
            majors_per_category = 25
        elif university_type == "综合":
            # 综合类普通本科
            categories = ["工学", "理学", "经济学", "管理学", "文学", "法学", "教育学", "历史学"]
            majors_per_category = 20
        elif university_type == "理工":
            # 理工类院校
            categories = ["工学", "理学", "管理学", "经济学"]
            majors_per_category = 25
        elif university_type == "师范":
            # 师范类院校
            categories = ["教育学", "文学", "理学", "管理学", "法学"]
            majors_per_category = 20
        elif university_type == "医学":
            # 医学类院校
            categories = ["医学", "理学", "工学", "管理学"]
            majors_per_category = 20
        elif university_type == "财经":
            # 财经类院校
            categories = ["经济学", "管理学", "法学", "文学"]
            majors_per_category = 25
        elif university_type == "政法":
            # 政法类院校
            categories = ["法学", "管理学", "文学", "工学"]
            majors_per_category = 20
        elif university_type == "艺术":
            # 艺术类院校
            categories = ["文学", "管理学", "工学"]
            majors_per_category = 15
        elif university_type == "农林":
            # 农林类院校
            categories = ["农学", "工学", "理学", "管理学"]
            majors_per_category = 20
        else:
            # 其他类型（默认更多专业）
            categories = ["工学", "管理学", "文学", "理学", "经济学"]
            majors_per_category = 15

        # 生成专业列表
        major_list = []
        for category in categories:
            if category in majors_by_category:
                majors = majors_by_category[category][:majors_per_category]
                major_list.extend(majors)

        return major_list

    def _estimate_tuition_fee(self, major_category: str, university_level: str) -> str:
        """估算学费"""
        base_fees = {
            "工学": "5000-6000元/年",
            "理学": "5000-6000元/年",
            "经济学": "5500-6500元/年",
            "管理学": "5000-6000元/年",
            "文学": "4500-5500元/年",
            "法学": "5000-6000元/年",
            "医学": "6000-8000元/年",
            "教育学": "4500-5500元/年",
            "历史学": "4500-5500元/年",
            "农学": "3000-4000元/年"
        }
        return base_fees.get(major_category, "5000-6000元/年")

    def _estimate_duration(self, major_category: str) -> str:
        """估算学制"""
        if major_category == "医学":
            return "5年"
        else:
            return "4年"

    def _estimate_subject_requirements(self, major_category: str) -> str:
        """估算选科要求"""
        requirements = {
            "工学": "物理必选",
            "理学": "物理/化学必选",
            "经济学": "物理/历史均可",
            "管理学": "物理/历史均可",
            "文学": "历史/政治优先",
            "法学": "政治优先",
            "医学": "物理+化学+生物",
            "教育学": "物理/历史均可",
            "历史学": "历史必选",
            "农学": "化学/生物必选"
        }
        return requirements.get(major_category, "无特殊要求")

    def save_expanded_data(self):
        """保存扩展后的数据"""
        print("\nSaving expanded university-majors data...")

        # 统计信息
        total_records = len(self.all_university_majors)
        covered_universities = len(set(r['university_id'] for r in self.all_university_majors))
        categories = len(set(r['major_category'] for r in self.all_university_majors))

        output_data = {
            "metadata": {
                "table_name": "university_majors",
                "description": "院校-专业关联表（全国全覆盖版）",
                "version": "2.0.0",
                "generated_at": "2026-05-06T16:00:00.000000",
                "total_records": total_records,
                "total_universities": covered_universities,
                "total_categories": categories,
                "coverage": "nationwide"
            },
            "statistics": {
                "total_records": total_records,
                "total_universities": covered_universities,
                "total_majors": len(set(r['major_code'] for r in self.all_university_majors)),
                "total_categories": categories,
                "avg_majors_per_university": total_records / covered_universities
            },
            "university_majors": self.all_university_majors
        }

        # 备份原文件
        backup_path = self.data_dir / "university_majors_backup_before_expansion.json"
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {"description": "Backup before nationwide expansion"},
                "university_majors": self.existing_university_majors
            }, f, ensure_ascii=False, indent=2)
        print(f"Backup saved to: {backup_path}")

        # 保存扩展后的数据
        with open(self.data_dir / "university_majors.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"Expanded data saved: {total_records:,} records")
        print(f"Covered universities: {covered_universities}")

        return output_data


def main():
    """主函数"""
    print("=" * 80)
    print("全国所有院校专业关联扩展器")
    print("目标：将院校-专业关联从298所扩展到全部2800所院校")
    print("=" * 80)

    expander = AllUniversitiesMajorsExpander()

    # 加载数据
    expander.load_data()

    # 生成所有院校的专业关联
    expander.generate_all_universities_majors()

    # 保存扩展后的数据
    expander.save_expanded_data()

    print("\n[SUCCESS] 全国所有院校专业关联扩展完成！")


if __name__ == "__main__":
    main()
