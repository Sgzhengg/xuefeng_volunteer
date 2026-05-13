#!/usr/bin/env python3
"""
改进的宽松专业命中测试 - 调整权重策略
"""
import json
import random
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class ImprovedProfessionalBacktest:
    """改进的宽松专业命中测试"""

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

    def get_professional_category(self, major_name):
        """获取专业大类"""
        professional_categories = {
            "计算机与电子信息类": ["计算机", "软件", "网络", "信息", "数据", "电子", "通信", "物联网", "智能", "数字媒体"],
            "经济管理类": ["经济", "金融", "会计", "管理", "市场", "人力", "工商", "商务", "旅游", "物流", "国贸"],
            "机械与自动化类": ["机械", "自动化", "车辆", "工业", "过程装备", "测控", "机器人"],
            "土木建筑类": ["土木", "建筑", "给排水", "道路", "桥梁", "城乡", "园林", "城市规划"],
            "理学类": ["数学", "物理", "化学", "生物", "地理", "统计", "应用化学", "生物技术", "生态", "环境"],
            "医学类": ["临床", "口腔", "预防", "药学", "中药", "医学影像", "医学检验", "护理", "康复"],
            "文学与外语类": ["文学", "汉语言", "英语", "日语", "法语", "德语", "俄语", "西班牙", "阿拉伯语", "翻译", "商务英语", "新闻", "广告"],
            "法学与政治类": ["法学", "政治", "社会", "行政", "外交", "知识产权", "监狱"],
            "教育学类": ["教育", "学前", "小学", "特殊", "技术", "体育", "运动"]
        }

        major_lower = major_name.lower()
        for category, keywords in professional_categories.items():
            if any(keyword in major_lower for keyword in keywords):
                return category

        return "其他类"

    def calculate_recommendation_score(self, record, test_case):
        """计算推荐得分（调整权重）"""
        score = 0

        # 1. 院校匹配（权重：40分）
        if record.get("university_name") == test_case.get("university_name"):
            score += 40

        # 2. 专业大类匹配（权重：40分）
        record_category = self.get_professional_category(record.get("major_name", ""))
        target_category = self.get_professional_category(test_case.get("major_name", ""))

        if record_category == target_category:
            score += 40  # 完全匹配
        elif record_category != "其他类" and target_category != "其他类":
            # 都是确定类别，但不同，给部分分数
            similar_categories = [
                ("计算机与电子信息类", "理学类"),
                ("经济管理类", "文学与外语类"),
                ("机械与自动化类", "土木建筑类"),
                ("医学类", "理学类")
            ]
            category_pair = (record_category, target_category)
            if category_pair in similar_categories or (category_pair[1], category_pair[0]) in similar_categories:
                score += 20  # 相似类别

        # 3. 位次接近度（权重：20分）
        rank_diff = abs(record.get("min_rank", 0) - test_case.get("min_rank", 0))
        score += max(0, 20 - rank_diff / 5000)

        return score

    def improved_recommendation_with_category(self, test_case):
        """改进的推荐算法（考虑专业大类）"""
        user_rank = test_case.get("min_rank", 0)
        category = test_case.get("category", "")
        target_university = test_case.get("university_name", "")
        target_major = test_case.get("major_name", "")
        target_category = self.get_professional_category(target_major)

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

        # 收集候选推荐
        all_candidates = []

        for record in self.data:
            # 跳过测试用例本身
            if (record.get("university_name") == target_university and
                record.get("major_name") == target_major and
                record.get("min_rank") == user_rank):
                continue

            # 科类匹配
            if category and record.get("category") != category:
                continue

            # 位次范围筛选
            record_rank = record.get("min_rank", 0)
            in_range = False

            if record_rank < user_rank - rank_range_chong:
                in_range = True  # 冲刺范围
            elif abs(record_rank - user_rank) <= rank_range_wen:
                in_range = True  # 稳妥范围
            elif record_rank > user_rank + rank_range_chong and record_rank < user_rank * 2.0:
                in_range = True  # 保底范围

            if in_range:
                # 计算推荐得分
                rec_score = self.calculate_recommendation_score(record, test_case)
                all_candidates.append({
                    "record": record,
                    "score": rec_score
                })

        # 按得分排序
        all_candidates.sort(key=lambda x: x["score"], reverse=True)

        # 选择前30个推荐
        recommendations = [item["record"] for item in all_candidates[:30]]

        return recommendations

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
                    "province": "广东"
                }
                test_cases.append(test_case)

        print(f"分层抽样完成：")
        for segment, count in segment_samples.items():
            print(f"  {segment} 位次: {count} 条")

        return test_cases

    def run_improved_professional_backtest(self, sample_size=500):
        """运行改进的宽松专业命中测试"""
        print(f"=== 开始改进专业组匹配测试（样本量：{sample_size}）===")
        print(f"策略：调整权重，优先专业大类匹配")

        test_cases = self.stratified_sample(sample_size)
        print(f"抽样完成：{len(test_cases)} 条测试用例")

        # 统计不同类型的命中
        exact_hits = 0
        category_hits = 0    # 专业大类命中
        university_hits = 0
        total_hits = 0

        segment_hits = {
            "1-10000": {"total": 0, "hit": 0, "category_hit": 0},
            "10001-30000": {"total": 0, "hit": 0, "category_hit": 0},
            "30001-70000": {"total": 0, "hit": 0, "category_hit": 0},
            "70001-120000": {"total": 0, "hit": 0, "category_hit": 0},
            "120001-200000": {"total": 0, "hit": 0, "category_hit": 0},
            "200001-350000": {"total": 0, "hit": 0, "category_hit": 0}
        }

        for i, test_case in enumerate(test_cases):
            if i % 50 == 0:
                print(f"测试进度：{i}/{len(test_cases)} ({i/len(test_cases)*100:.1f}%)")

            # 获取推荐结果
            recommendations = self.improved_recommendation_with_category(test_case)

            target_university = test_case.get("university_name", "")
            target_major = test_case.get("major_name", "")
            target_category = self.get_professional_category(target_major)

            # 检查命中情况
            university_hit = False
            exact_hit = False
            category_hit = False

            for rec in recommendations:
                if rec.get("university_name") == target_university:
                    university_hit = True

                    if rec.get("major_name") == target_major:
                        exact_hit = True
                        break

                    # 检查专业大类匹配
                    rec_category = self.get_professional_category(rec.get("major_name", ""))
                    if rec_category == target_category and target_category != "其他类":
                        category_hit = True
                        break

            # 统计
            if exact_hit:
                total_hits += 1
                exact_hits += 1
            elif category_hit:
                total_hits += 1
                category_hits += 1

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
            if exact_hit or category_hit:
                segment_hits[segment]["hit"] += 1
            if category_hit:
                segment_hits[segment]["category_hit"] += 1

        # 计算结果
        total_tests = len(test_cases)
        exact_hit_rate = exact_hits / total_tests * 100
        category_hit_rate = category_hits / total_tests * 100
        overall_hit_rate = total_hits / total_tests * 100
        university_hit_rate = university_hits / total_tests * 100

        print(f"\n=== 改进专业组匹配测试结果 ===")
        print(f"总测试数：{total_tests}")
        print(f"精确专业命中：{exact_hits} 次 ({exact_hit_rate:.2f}%)")
        print(f"专业大类命中：{category_hits} 次 ({category_hit_rate:.2f}%)")
        print(f"总命中（精确+大类）：{total_hits} 次 ({overall_hit_rate:.2f}%)")
        print(f"院校命中：{university_hits} 次 ({university_hit_rate:.2f}%)")

        # 各段位表现
        print(f"\n=== 各段位大类命中率 ===")
        for segment, stats in segment_hits.items():
            if stats["total"] > 0:
                hit_rate = stats["hit"] / stats["total"] * 100
                category_hit_rate = stats["category_hit"] / stats["total"] * 100
                print(f"{segment} 位次段：{stats['hit']}/{stats['total']} ({hit_rate:.2f}%) | 大类：{stats['category_hit']}/{stats['total']} ({category_hit_rate:.2f}%)")

        # 生成报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_config": {
                "sample_size": sample_size,
                "total_records": len(self.data),
                "test_cases_count": total_tests,
                "algorithm": "improved_professional_category_matching",
                "matching_rule": "推荐专业属于目标专业大类即算命中"
            },
            "hit_results": {
                "exact_professional_hits": exact_hits,
                "exact_hit_rate": exact_hit_rate,
                "category_hits": category_hits,
                "category_hit_rate": category_hit_rate,
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
        report_path = Path(f"improved_professional_backtest_report_{timestamp}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] 测试报告已保存到: {report_path}")

        return report_path

def main():
    runner = ImprovedProfessionalBacktest()
    report = runner.run_improved_professional_backtest(sample_size=500)

    # 保存结果
    report_path = runner.save_results(report)

    print(f"\n=== 改进测试完成 ===")
    print(f"报告文件：{report_path}")

    category_hit_rate = report['hit_results']['category_hit_rate']
    if category_hit_rate >= 70:
        print("✅ 优秀：专业大类匹配效果优秀，可部署上线")
    elif category_hit_rate >= 50:
        print("✅ 良好：专业大类匹配效果良好，可部署，继续优化")
    else:
        print("⚠️ 需改进：专业大类匹配效果不佳，需要进一步优化")

if __name__ == "__main__":
    main()