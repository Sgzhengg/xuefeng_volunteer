"""
全国所有院校专业录取位次数据生成器
覆盖所有大专以上院校（2800+所）和全国31个省份
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class NationwideRankDataGenerator:
    """全国院校专业录取位次数据生成器"""

    def __init__(self):
        script_dir = Path(__file__).parent
        self.data_dir = script_dir / "data"
        self.rank_data = []
        self.statistics = {
            "total_universities": 0,
            "total_records": 0,
            "by_province": defaultdict(int),
            "by_level": defaultdict(int)
        }

    def load_data(self):
        """加载基础数据"""
        print("Loading base data...")

        # 加载院校列表
        with open(self.data_dir / "universities_list.json", 'r', encoding='utf-8') as f:
            uni_data = json.load(f)
        self.universities = uni_data["universities"]
        print(f"Loaded {len(self.universities)} universities")

        # 加载院校-专业关联表
        with open(self.data_dir / "university_majors.json", 'r', encoding='utf-8') as f:
            um_data = json.load(f)
        self.university_majors = um_data["university_majors"]
        print(f"Loaded {len(self.university_majors)} university-major records")

        # 加载现有位次数据
        with open(self.data_dir / "major_rank_data.json", 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        self.existing_rank_data = existing_data["major_rank_data"]
        print(f"Loaded {len(self.existing_rank_data)} existing rank records")

        # 按院校分组
        self.universities_by_id = {u["id"]: u for u in self.universities}

        # 按院校分组专业关联
        self.majors_by_university = defaultdict(list)
        for um in self.university_majors:
            self.majors_by_university[um['university_id']].append(um)

    def generate_nationwide_rank_data(self):
        """生成全国所有院校的专业录取位次数据"""
        print("\nGenerating nationwide rank data for all universities...")

        total_unis = len(self.universities)
        processed = 0

        for university in self.universities:
            university_id = university["id"]
            university_name = university["name"]
            university_level = university.get("level", "普通本科")
            university_province = university.get("province", "")

            # 为该院校的所有专业生成位次数据
            majors = self.majors_by_university.get(university_id, [])

            if not majors:
                continue

            # 为每个专业、每个省份生成位次数据
            for major in majors:
                for province in self._get_all_provinces():
                    # 估算录取分数和位次
                    min_score, avg_score = self._estimate_admission_scores(
                        university_name, university_level, major["major_name"],
                        university_province, province
                    )

                    if min_score == 0:
                        continue

                    # 转换为位次
                    min_rank = self._score_to_rank(province, 2024, min_score)
                    avg_rank = self._score_to_rank(province, 2024, avg_score)

                    # 判断数据来源
                    data_source = self._determine_data_source(university_level, province)

                    record = {
                        "university_major_id": major["university_major_id"],
                        "university_id": university_id,
                        "university_name": university_name,
                        "university_level": university_level,
                        "university_province": university_province,
                        "major_code": major["major_code"],
                        "major_name": major["major_name"],
                        "major_category": major["major_category"],
                        "year": 2024,
                        "province": province,
                        "min_score": min_score,
                        "avg_score": avg_score,
                        "min_rank": min_rank,
                        "avg_rank": avg_rank,
                        "data_source": data_source,
                        "accuracy": self._determine_accuracy(university_level, data_source)
                    }

                    self.rank_data.append(record)
                    self.statistics["total_records"] += 1
                    self.statistics["by_province"][province] += 1
                    self.statistics["by_level"][university_level] += 1

            processed += 1
            if processed % 100 == 0:
                print(f"Processed {processed}/{total_unis} universities...")

        print(f"\nGenerated {len(self.rank_data)} rank data records for all universities")

    def _get_all_provinces(self) -> List[str]:
        """获取全国31个省份列表"""
        return [
            "北京", "天津", "河北", "山西", "内蒙古",
            "辽宁", "吉林", "黑龙江",
            "上海", "江苏", "浙江", "安徽", "福建", "江西", "山东",
            "河南", "湖北", "湖南", "广东", "广西", "海南",
            "重庆", "四川", "贵州", "云南", "西藏",
            "陕西", "甘肃", "青海", "宁夏", "新疆"
        ]

    def _estimate_admission_scores(self, university_name: str, university_level: str,
                                   major_name: str, university_province: str,
                                   target_province: str) -> Tuple[int, int]:
        """
        估算院校专业在某省的录取分数

        改进点：
        1. 考虑院校层次的细分（985/211/普通本科/高职）
        2. 考虑本地生源优势
        3. 考虑专业热度
        """
        # 基础分数基准（按院校层次）
        base_scores = {
            "985": {"min": 620, "avg": 640},
            "211": {"min": 580, "avg": 600},
            "普通本科": {"min": 500, "avg": 520},
            "高职": {"min": 350, "avg": 370}
        }

        # 热门专业加分（细分）
        hot_majors_tier1 = {  # 最热门
            "计算机科学与技术": 25,
            "人工智能": 28,
            "软件工程": 23,
            "临床医学": 25
        }

        hot_majors_tier2 = {  # 热门
            "数学与应用数学": 18,
            "电子信息工程": 20,
            "电气工程及其自动化": 16,
            "金融学": 18,
            "口腔医学": 20
        }

        hot_majors_tier3 = {  # 较热门
            "自动化": 12,
            "数据科学与大数据技术": 15,
            "统计学": 10,
            "经济学": 12,
            "法学": 12,
            "建筑学": 14
        }

        # 计算基础分数
        base = base_scores.get(university_level, {"min": 480, "avg": 500})

        # 热门专业加分
        major_bonus = 0
        if major_name in hot_majors_tier1:
            major_bonus = hot_majors_tier1[major_name]
        elif major_name in hot_majors_tier2:
            major_bonus = hot_majors_tier2[major_name]
        elif major_name in hot_majors_tier3:
            major_bonus = hot_majors_tier3[major_name]

        # 顶尖院校额外加分
        top_universities = {
            "北京大学": 35,
            "清华大学": 35,
            "复旦大学": 25,
            "上海交通大学": 25,
            "浙江大学": 25,
            "中国科学技术大学": 23,
            "南京大学": 23,
            "中国人民大学": 20,
            "同济大学": 18,
            "哈尔滨工业大学": 18
        }

        uni_bonus = top_universities.get(university_name, 0)

        # 本地生源优势（本地考生分数略低）
        local_bonus = 0
        if target_province == university_province:
            if university_level == "985":
                local_bonus = -8
            elif university_level == "211":
                local_bonus = -10
            else:
                local_bonus = -12

        # 经济发达地区院校加分（广东、江苏、浙江、上海、北京）
        developed_provinces = ["广东", "江苏", "浙江", "上海", "北京"]
        if university_province in developed_provinces:
            developed_bonus = 5
        else:
            developed_bonus = 0

        # 计算最终分数
        min_score = base["min"] + major_bonus + uni_bonus + local_bonus + developed_bonus
        avg_score = base["avg"] + major_bonus + uni_bonus + local_bonus + developed_bonus

        # 确保分数在合理范围内
        min_score = max(300, min(750, min_score))
        avg_score = max(min_score + 5, min(750, avg_score))

        return (min_score, avg_score)

    def _score_to_rank(self, province: str, year: int, score: int) -> int:
        """分数转位次（改进版，考虑省份差异）"""
        # 不同省份的转换系数（基于考生人数和竞争激烈程度）
        province_factors = {
            # 高考大省（考生多，竞争激烈）
            "河南": 320, "山东": 270, "广东": 290, "四川": 230, "河北": 270,
            # 中等省份
            "江苏": 150, "浙江": 200, "安徽": 260, "湖南": 250, "湖北": 240,
            "广西": 240, "江西": 220, "云南": 230, "贵州": 250, "陕西": 210,
            "山西": 210, "福建": 200, "重庆": 190, "辽宁": 180, "黑龙江": 180,
            "吉林": 170, "内蒙古": 160, "甘肃": 170,
            # 考生较少的省份
            "北京": 100, "上海": 120, "天津": 140, "海南": 130,
            "新疆": 110, "宁夏": 90, "青海": 70, "西藏": 50
        }

        factor = province_factors.get(province, 200)

        # 改进的位次计算（考虑分数段）
        if score >= 650:
            # 高分段（前1%）
            rank = int((750 - score) * factor * 0.6)
        elif score >= 600:
            # 优秀段（前5%）
            rank = int((750 - score) * factor * 0.8)
        elif score >= 500:
            # 中等段
            rank = int((750 - score) * factor)
        else:
            # 低分段
            rank = int((750 - score) * factor * 1.3)

        return max(1, rank)

    def _determine_data_source(self, university_level: str, province: str) -> str:
        """判断数据来源"""
        # 优先保留官方数据（已在existing中）
        # 对于新生成的数据，标记为估算
        return f"estimated_nationwide_{university_level}"

    def _determine_accuracy(self, university_level: str, data_source: str) -> str:
        """判断数据精度"""
        if data_source.startswith("official_"):
            return "high"
        elif university_level in ["985", "211"]:
            return "medium_high"
        else:
            return "medium"

    def merge_with_existing_data(self):
        """合并现有数据和新数据"""
        print("\nMerging with existing data...")

        # 构建现有记录的键
        existing_keys = {
            (r["university_major_id"], r["province"], r["year"])
            for r in self.existing_rank_data
        }

        # 添加新记录（不重复）
        new_records = []
        for record in self.rank_data:
            key = (record["university_major_id"], record["province"], record["year"])
            if key not in existing_keys:
                new_records.append(record)

        print(f"Found {len(new_records)} new records to add")

        # 合并
        merged_records = self.existing_rank_data + new_records

        # 保存合并后的数据
        output_data = {
            "metadata": {
                "table_name": "major_rank_data",
                "description": "全国院校专业录取位次数据（全覆盖版）",
                "version": "4.0.0",
                "generated_at": "2026-05-06T15:00:00.000000",
                "total_records": len(merged_records),
                "coverage": "nationwide",
                "accuracy": "混合（官方数据+估算数据）"
            },
            "major_rank_data": merged_records
        }

        # 备份原文件
        backup_path = self.data_dir / "major_rank_data_backup_before_nationwide.json"
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {"description": "Backup before nationwide expansion"},
                "major_rank_data": self.existing_rank_data
            }, f, ensure_ascii=False, indent=2)
        print(f"Backup saved to: {backup_path}")

        # 保存合并后的数据
        with open(self.data_dir / "major_rank_data.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"Merged data saved: {len(merged_records):,} records")

        return merged_records

    def generate_coverage_report(self, merged_records: List[Dict]):
        """生成数据覆盖报告"""
        print("\n" + "=" * 80)
        print("全国数据覆盖报告")
        print("=" * 80)

        # 统计覆盖院校
        covered_uni_names = set(r["university_name"] for r in merged_records)
        total_unis = len(self.universities)

        print(f"\n总体覆盖:")
        print(f"- 覆盖院校: {len(covered_uni_names)}/{total_unis} ({len(covered_uni_names)/total_unis*100:.1f}%)")
        print(f"- 总记录数: {len(merged_records):,}")

        # 按层次统计
        print(f"\n按院校层次统计:")
        for level in ["985", "211", "普通本科", "高职"]:
            level_unis = [u for u in self.universities if u.get("level") == level]
            level_covered = [u for u in level_unis if u["name"] in covered_uni_names]
            if len(level_unis) > 0:
                print(f"- {level}: {len(level_covered)}/{len(level_unis)} ({len(level_covered)/len(level_unis)*100:.1f}%)")
            else:
                print(f"- {level}: 0/0 (N/A)")

        # 按省份统计
        print(f"\n按省份统计（前15）:")
        provinces_stats = defaultdict(int)
        for r in merged_records:
            provinces_stats[r["university_province"]] += 1

        for province, count in sorted(provinces_stats.items(), key=lambda x: x[1], reverse=True)[:15]:
            print(f"- {province}: {count:,}条记录")

        # 数据来源统计
        print(f"\n数据来源统计:")
        data_sources = defaultdict(int)
        for r in merged_records:
            ds = r.get("data_source", "unknown")
            if ds.startswith("official_"):
                data_sources["官方数据"] += 1
            else:
                data_sources["估算数据"] += 1

        for source, count in data_sources.items():
            print(f"- {source}: {count:,}条 ({count/len(merged_records)*100:.1f}%)")

        print("\n" + "=" * 80)


def main():
    """主函数"""
    print("=" * 80)
    print("全国院校专业录取位次数据生成器")
    print("目标：覆盖所有大专以上院校（2800+所）和全国31个省份")
    print("=" * 80)

    generator = NationwideRankDataGenerator()

    # 加载数据
    generator.load_data()

    # 生成全国数据
    generator.generate_nationwide_rank_data()

    # 合并现有数据
    merged_records = generator.merge_with_existing_data()

    # 生成覆盖报告
    generator.generate_coverage_report(merged_records)

    print("\n[SUCCESS] 全国数据生成完成！")


if __name__ == "__main__":
    main()
