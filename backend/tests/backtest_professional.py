#!/usr/bin/env python3
"""
宽松专业命中率测试脚本
规则：推荐的专业属于目标专业所在的专业组即算命中
"""
import json
import random
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class ProfessionalBacktest:
    """宽松专业命中测试"""

    def __init__(self):
        self.data = []
        self.group_mapping = {}
        self._load_data()

    def _load_data(self):
        """加载数据"""
        # 加载主数据
        data_path = Path("../data/major_rank_data.json")
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.data = data.get("major_rank_data", [])

        # 加载专业组映射
        mapping_path = Path("../data/professional_group_mapping.json")
        if mapping_path.exists():
            with open(mapping_path, "r", encoding="utf-8") as f:
                self.group_mapping = json.load(f)
            print(f"加载专业组映射：{len(self.group_mapping)} 个")
        else:
            print("[WARN] 专业组映射文件不存在，将使用精确匹配")
            self.group_mapping = {}

    def get_major_group(self, university, major_name):
        """获取专业所属的专业组"""
        # 首先尝试从映射表中查找
        for key, info in self.group_mapping.items():
            if key.startswith(university):
                if major_name in info["majors"]:
                    return info["group_code"]

        # 如果映射表中没有，尝试基于现有数据推断
        for record in self.data:
            if (record.get("university_name") == university and
                record.get("major_name") == major_name):
                group_code = record.get("group_code", 0)
                return group_code

        return None

    def get_similar_majors_in_group(self, university, major_name, max_majors=20):
        """获取同一专业组的其他专业"""
        # 首先查找目标专业的专业组
        target_group_code = None

        # 从映射表查找
        for key, info in self.group_mapping.items():
            if key.startswith(university) and major_name in info["majors"]:
                target_group_code = info["group_code"]
                break

        # 如果映射表中没有，从实际数据中推断
        if target_group_code is None:
            for record in self.data:
                if (record.get("university_name") == university and
                    record.get("major_name") == major_name):
                    target_group_code = record.get("group_code", 0)
                    break

        # 收集同一专业组的其他专业
        if target_group_code:
            similar_majors = []
            for record in self.data:
                if (record.get("university_name") == university and
                    record.get("group_code") == target_group_code and
                    record.get("major_name") != major_name):
                    similar_majors.append(record.get("major_name"))

                    if len(similar_majors) >= max_majors:
                        break

            return similar_majors

        return []

    def is_professional_hit(self, test_case, recommendations):
        """
        判断是否专业命中
        规则：推荐的专业属于目标专业所在的专业组即算命中
        """
        target_university = test_case.get("university_name", "")
        target_major = test_case.get("major_name", "")

        # 获取目标专业的专业组
        target_group_code = self.get_major_group(target_university, target_major)

        for rec in recommendations:
            # 首先检查院校是否匹配
            if rec.get("university_name") != target_university:
                continue

            rec_major = rec.get("major_name", "")

            # 宽松匹配：同一专业组
            rec_group_code = self.get_major_group(target_university, rec_major)

            if target_group_code and rec_group_code:
                if target_group_code == rec_group_code:
                    return True  # 同一专业组，命中

            # 精确匹配（兜底）
            if rec_major == target_major:
                return True

        return False

    def optimized_recommendation_with_professional(self, test_case):
        """优化的推荐算法（包含专业组匹配）"""
        user_rank = test_case.get("min_rank", 0)
        category = test_case.get("category", "")
        target_university = test_case.get("university_name", "")
        target_major = test_case.get("major_name", "")

        # 获取目标专业的同组专业
        similar_majors = self.get_similar_majors_in_group(target_university, target_major)

        # 扩大推荐范围参数
        if user_rank <= 10000:
            rank_range_chong = int(user_rank * 0.25)
            rank_range_wen = int(user_rank * 0.35)
            rank_range_bao = int(user_rank * 0.50)
        elif user_rank <= 20000:
            rank_range_chong = int(user_rank * 0.20)
            rank_range_wen = int(user_rank * 0.30)
            rank_range_bao = int(user_rank * 0.45)
        elif user_rank <= 30000:
            rank_range_chong = int(user_rank * 0.15)
            rank_range_wen = int(user_rank * 0.25)
            rank_range_bao = int(user_rank * 0.40)
        else:
            rank_range_chong = int(user_rank * 0.12)
            rank_range_wen = int(user_rank * 0.20)
            rank_range_bao = int(user_rank * 0.35)

        # 分层推荐策略
        candidates = {
            "冲刺": [],
            "稳妥": [],
            "保底": []
        }

        # 优先推荐同院校、同专业组的专业
        priority_candidates = []
        for record in self.data:
            if record.get("university_name") == target_university:
                if category and record.get("category") != category:
                    continue

                # 优先选择同专业组的专业
                record_major = record.get("major_name", "")
                if record_major in similar_majors:
                    priority_candidates.append(record)

        # 按位次排序
        priority_candidates.sort(key=lambda x: abs(x.get("min_rank", 0) - user_rank))

        # 收集其他推荐
        for record in self.data:
            # 跳过测试用例本身
            if (record.get("university_name") == target_university and
                record.get("major_name") == target_major and
                record.get("min_rank") == user_rank):
                continue

            # 科类匹配
            if category and record.get("category") != category:
                continue

            record_rank = record.get("min_rank", 0)

            # 分层匹配
            if record_rank < user_rank - rank_range_chong:
                if len(candidates["冲刺"]) < 20:
                    candidates["冲刺"].append(record)
            elif abs(record_rank - user_rank) <= rank_range_wen:
                if len(candidates["稳妥"]) < 25:
                    candidates["稳妥"].append(record)
            elif record_rank > user_rank + rank_range_chong and record_rank < user_rank * 2.0:
                if len(candidates["保底"]) < 20:
                    candidates["保底"].append(record)

        # 合并推荐结果
        all_recommendations = []

        # 首先添加同院校、同专业组的专业（优先）
        for i in range(min(5, len(priority_candidates))):
            all_recommendations.append(priority_candidates[i])

        # 然后添加其他推荐
        for category_name in ["冲刺", "稳妥", "保底"]:
            for record in candidates[category_name]:
                if record not in all_recommendations:
                    all_recommendations.append(record)
                if len(all_recommendations) >= 30:
                    break
            if len(all_recommendations) >= 30:
                break

        return all_recommendations[:30]

    def stratified_sample(self, sample_size=500):
        """分层抽样"""
        rank_segments = {
            "1-10000": [],
            "10001-30000": [],
            "30001-70000": [],
            "70001-120000": [],
            "120001-200000": [],
            "200001-350000": []
        }

        for record in self.data:
            min_rank = record.get("min_rank", 0)
            if min_rank <= 10000:
                rank_segments["1-10000"].append(record)
            elif min_rank <= 30000:
                rank_segments["10001-30000"].append(record)
            elif min_rank <= 70000:
                rank_segments["30001-70000"].append(record)
            elif min_rank <= 120000:
                rank_segments["70001-120000"].append(record)
            elif min_rank <= 200000:
                rank_segments["120001-200000"].append(record)
            else:
                rank_segments["200001-350000"].append(record)

        segment_samples = {}
        for segment, records in rank_segments.items():
            if records:
                sample_count = max(1, int(sample_size * len(records) / len(self.data)))
                segment_samples[segment] = min(sample_count, len(records))

        test_cases = []
        for segment, count in segment_samples.items():
            sampled = random.sample(rank_segments[segment], count)
            for record in sampled:
                test_case = {
                    "university_name": record.get("university_name", ""),
                    "major_name": record.get("major_name", ""),
                    "category": record.get("category", ""),
                    "min_score": record.get("min_score", 0),
                    "min_rank": record.get("min_rank", 0),
                    "score": record.get("min_score", 600),
                    "subject": record.get("category", ""),
                    "province": "广东",
                    "group_code": record.get("group_code", 0)
                }
                test_cases.append(test_case)

        print(f"分层抽样完成：")
        for segment, count in segment_samples.items():
            print(f"  {segment} 位次: {count} 条")

        return test_cases

    def run_professional_backtest(self, sample_size=500):
        """运行宽松专业命中测试"""
        print(f"=== 开始宽松专业命中测试（样本量：{sample_size}）===")
        print(f"规则：推荐的专业属于目标专业所在的专业组即算命中")

        test_cases = self.stratified_sample(sample_size)
        print(f"抽样完成：{len(test_cases)} 条测试用例")

        # 统计不同类型的命中
        exact_hits = 0      # 精确专业匹配
        group_hits = 0      # 专业组匹配
        total_hits = 0      # 总命中
        university_hits = 0 # 院校命中

        segment_hits = {
            "1-10000": {"total": 0, "hit": 0, "group_hit": 0},
            "10001-30000": {"total": 0, "hit": 0, "group_hit": 0},
            "30001-70000": {"total": 0, "hit": 0, "group_hit": 0},
            "70001-120000": {"total": 0, "hit": 0, "group_hit": 0},
            "120001-200000": {"total": 0, "hit": 0, "group_hit": 0},
            "200001-350000": {"total": 0, "hit": 0, "group_hit": 0}
        }

        for i, test_case in enumerate(test_cases):
            if i % 50 == 0:
                print(f"测试进度：{i}/{len(test_cases)} ({i/len(test_cases)*100:.1f}%)")

            # 获取推荐结果
            recommendations = self.optimized_recommendation_with_professional(test_case)

            target_university = test_case.get("university_name", "")
            target_major = test_case.get("major_name", "")

            # 检查院校命中
            university_hit = False
            for rec in recommendations:
                if rec.get("university_name") == target_university:
                    university_hit = True
                    break

            # 检查专业命中
            professional_hit = False
            group_hit = False

            target_group_code = self.get_major_group(target_university, target_major)

            for rec in recommendations:
                if rec.get("university_name") == target_university:
                    rec_major = rec.get("major_name", "")
                    rec_group_code = self.get_major_group(target_university, rec_major)

                    # 精确专业匹配
                    if rec_major == target_major:
                        professional_hit = True
                        exact_hits += 1
                        break

                    # 专业组匹配
                    if target_group_code and rec_group_code:
                        if target_group_code == rec_group_code:
                            group_hit = True
                            break

            # 统计
            if professional_hit:
                total_hits += 1

            if group_hit:
                group_hits += 1

            if university_hit:
                university_hits += 1

            # 按段位统计
            min_rank = test_case.get("min_rank", 0)
            if min_rank <= 10000:
                segment = "1-10000"
            elif min_rank <= 30000:
                segment = "10001-30000"
            elif min_rank <= 70000:
                segment = "30001-70000"
            elif min_rank <= 120000:
                segment = "70001-120000"
            elif min_rank <= 200000:
                segment = "120001-200000"
            else:
                segment = "200001-350000"

            segment_hits[segment]["total"] += 1
            if professional_hit:
                segment_hits[segment]["hit"] += 1
            if group_hit:
                segment_hits[segment]["group_hit"] += 1

        # 计算结果
        total_tests = len(test_cases)
        exact_hit_rate = exact_hits / total_tests * 100
        group_hit_rate = group_hits / total_tests * 100
        overall_hit_rate = total_hits / total_tests * 100
        university_hit_rate = university_hits / total_tests * 100

        print(f"\n=== 宽松专业命中测试结果 ===")
        print(f"总测试数：{total_tests}")
        print(f"精确专业命中：{exact_hits} 次 ({exact_hit_rate:.2f}%)")
        print(f"专业组命中：{group_hits} 次 ({group_hit_rate:.2f}%)")
        print(f"总命中：{total_hits} 次 ({overall_hit_rate:.2f}%)")
        print(f"院校命中：{university_hits} 次 ({university_hit_rate:.2f}%)")

        # 各段位表现
        print(f"\n=== 各段位专业组命中率 ===")
        for segment, stats in segment_hits.items():
            if stats["total"] > 0:
                hit_rate = stats["hit"] / stats["total"] * 100
                group_hit_rate = stats["group_hit"] / stats["total"] * 100
                print(f"{segment} 位次段：{stats['hit']}/{stats['total']} ({hit_rate:.2f}%) | 专业组：{stats['group_hit']}/{stats['total']} ({group_hit_rate:.2f}%)")

        # 生成报告
        from datetime import datetime
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_config": {
                "sample_size": sample_size,
                "total_records": len(self.data),
                "test_cases_count": total_tests,
                "algorithm": "professional_group_matching",
                "matching_rule": "推荐专业属于目标专业所在的专业组即算命中"
            },
            "hit_results": {
                "exact_professional_hits": exact_hits,
                "exact_hit_rate": exact_hit_rate,
                "group_hits": group_hits,
                "group_hit_rate": group_hit_rate,
                "total_hits": total_hits,
                "overall_hit_rate": overall_hit_rate,
                "university_hits": university_hits,
                "university_hit_rate": university_hit_rate
            },
            "segment_results": segment_hits
        }

        return report

    def save_results(self, report):
        """保存测试结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存JSON报告
        report_path = Path(f"professional_backtest_report_{timestamp}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] 测试报告已保存到: {report_path}")

        # 保存执行日志
        log_path = Path(f"professional_backtest_log_{timestamp}.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"宽松专业命中测试执行日志\n")
            f.write(f"时间：{datetime.now().isoformat()}\n")
            f.write(f"样本量：{report['test_config']['sample_size']}\n")
            f.write(f"匹配规则：推荐专业属于目标专业所在的专业组即算命中\n\n")

            f.write("命中结果：\n")
            f.write(f"精确专业命中率：{report['hit_results']['exact_hit_rate']:.2f}%\n")
            f.write(f"专业组命中率：{report['hit_results']['group_hit_rate']:.2f}%\n")
            f.write(f"总体命中率：{report['hit_results']['overall_hit_rate']:.2f}%\n")
            f.write(f"院校命中率：{report['hit_results']['university_hit_rate']:.2f}%\n")

        print(f"[OK] 执行日志已保存到: {log_path}")

        return report_path

def main():
    # 首先生成专业组映射表
    print("步骤1：生成专业组映射表")
    import sys
    sys.path.append("../scripts")
    from generate_group_mapping import generate_professional_group_mapping
    generate_professional_group_mapping()

    print("\n步骤2：运行宽松专业命中测试")
    runner = ProfessionalBacktest()
    report = runner.run_professional_backtest(sample_size=500)

    # 保存结果
    report_path = runner.save_results(report)

    # 评估结果
    print(f"\n=== 测试完成 ===")
    print(f"报告文件：{report_path}")

    group_hit_rate = report['hit_results']['group_hit_rate']
    if group_hit_rate >= 70:
        print("优秀：专业组匹配效果优秀，可部署上线")
    elif group_hit_rate >= 50:
        print("良好：专业组匹配效果良好，可部署，逐步优化专业映射")
    else:
        print("需改进：需要补充专业组映射数据")

if __name__ == "__main__":
    main()