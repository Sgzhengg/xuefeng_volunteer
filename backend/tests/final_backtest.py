#!/usr/bin/env python3
"""
最终回溯测试 - 验证推荐算法准确性
"""
import json
import random
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import os
import requests

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.guangdong_recommendation_service import GuangdongRecommendationService

class FinalBacktestRunner:
    def __init__(self):
        self.recommendation_service = GuangdongRecommendationService()
        self.test_results = []

    def load_data(self):
        """加载数据"""
        data_path = Path("../data/major_rank_data.json")
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("major_rank_data", [])

    def stratified_sample(self, data, sample_size=500):
        """分层抽样并构建测试用例"""
        rank_segments = {
            "1-10000": [],
            "10001-30000": [],
            "30001-70000": [],
            "70001-120000": [],
            "120001-200000": [],
            "200001-350000": []
        }

        # 将数据按位次段分组
        for record in data:
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

        # 计算每个段的样本数量
        segment_samples = {}
        for segment, records in rank_segments.items():
            if records:
                sample_count = max(1, int(sample_size * len(records) / len(data)))
                segment_samples[segment] = min(sample_count, len(records))

        # 执行抽样并构建测试用例
        test_cases = []
        for segment, count in segment_samples.items():
            sampled = random.sample(rank_segments[segment], count)
            for record in sampled:
                # 构建测试用例，包含原始数据和测试参数
                test_case = {
                    "university_name": record.get("university_name", ""),
                    "major_name": record.get("major_name", ""),
                    "category": record.get("category", ""),
                    "min_score": record.get("min_score", 0),
                    "min_rank": record.get("min_rank", 0),
                    "score": record.get("min_score", 600),  # 用于显示
                    "subject": record.get("category", ""),    # 用于显示
                    "province": "广东",  # 固定测试广东省
                    "original_data": record  # 保存原始数据用于调试
                }
                test_cases.append(test_case)

        print(f"分层抽样完成：")
        for segment, count in segment_samples.items():
            print(f"  {segment} 位次: {count} 条")

        return test_cases

    def test_recommendation(self, test_case):
        """测试单个推荐案例"""
        province = "广东"  # 固定为广东省
        score = test_case["score"]
        subject = test_case["category"]
        target_university = test_case["university_name"]

        # 将分数转换为位次（简化版本）
        # 这里使用数据中的min_rank作为用户位次
        user_rank = test_case.get("min_rank", score * 1000)  # 简化转换

        # 调用推荐算法
        try:
            recommendations = self.recommendation_service.recommend_with_fallback(
                user_rank=user_rank,
                province=province,
                target_majors=[test_case.get("major_name", "")] if test_case.get("major_name") else None
            )

            # 检查是否命中目标院校
            hit = False
            # 检查所有推荐结果中的院校名称
            for category in ["冲刺", "稳妥", "保底"]:
                for rec in recommendations.get(category, []):
                    if rec.get("university_name") == target_university:
                        hit = True
                        break
                if hit:
                    break

            return {
                "test_case": test_case,
                "hit": hit,
                "recommendations": recommendations
            }

        except Exception as e:
            print(f"测试失败: {e}")
            return {
                "test_case": test_case,
                "hit": False,
                "error": str(e)
            }

    def run_final_backtest(self, sample_size=500):
        """运行最终回溯测试"""
        print(f"=== 开始最终回溯测试（样本量：{sample_size}）===")

        # 1. 加载数据
        data = self.load_data()
        print(f"加载数据完成：{len(data):,} 条")

        # 2. 分层抽样
        test_cases = self.stratified_sample(data, sample_size)
        print(f"抽样完成：{len(test_cases)} 条测试用例")

        # 3. 执行测试
        hit_count = 0
        segment_hits = {
            "1-10000": {"total": 0, "hit": 0},
            "10001-30000": {"total": 0, "hit": 0},
            "30001-70000": {"total": 0, "hit": 0},
            "70001-120000": {"total": 0, "hit": 0},
            "120001-200000": {"total": 0, "hit": 0},
            "200001-350000": {"total": 0, "hit": 0}
        }

        # 4. 执行测试
        for i, test_case in enumerate(test_cases):
            if i % 50 == 0:
                print(f"测试进度：{i}/{len(test_cases)} ({i/len(test_cases)*100:.1f}%)")

            result = self.test_recommendation(test_case)
            self.test_results.append(result)

            # 统计命中情况
            if result["hit"]:
                hit_count += 1

            # 按位次段统计
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
            if result["hit"]:
                segment_hits[segment]["hit"] += 1

        # 5. 计算结果
        total_tests = len(test_cases)
        hit_rate = hit_count / total_tests * 100

        print(f"\n=== 测试结果 ===")
        print(f"总测试数：{total_tests}")
        print(f"命中数：{hit_count}")
        print(f"整体命中率：{hit_rate:.2f}%")

        # 各位次段命中率
        segment_hit_rates = {}
        for segment, stats in segment_hits.items():
            if stats["total"] > 0:
                rate = stats["hit"] / stats["total"] * 100
                segment_hit_rates[segment] = rate
                print(f"{segment} 位次段：{stats['hit']}/{stats['total']} ({rate:.2f}%)")

        # 6. 收集未命中案例
        unhit_cases = [r for r in self.test_results if not r["hit"]]

        # 7. 生成报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_config": {
                "sample_size": sample_size,
                "total_records": len(data),
                "test_cases_count": total_tests
            },
            "overall_results": {
                "hit_count": hit_count,
                "total_tests": total_tests,
                "hit_rate": hit_rate
            },
            "segment_results": segment_hit_rates,
            "unhit_cases_count": len(unhit_cases),
            "unhit_cases_sample": unhit_cases[:20]  # 前20个未命中案例
        }

        return report

    def save_results(self, report):
        """保存测试结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. 保存JSON报告
        report_path = Path(f"backtest_report_{timestamp}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] 测试报告已保存到: {report_path}")

        # 2. 保存未命中案例CSV
        if report["unhit_cases_count"] > 0:
            unhit_data = []
            for case in report["unhit_cases_sample"]:
                test_case = case["test_case"]
                unhit_data.append({
                    "university_name": test_case.get("university_name", ""),
                    "major_name": test_case.get("major_name", ""),
                    "category": test_case.get("category", ""),
                    "min_score": test_case.get("min_score", ""),
                    "min_rank": test_case.get("min_rank", ""),
                    "score": test_case.get("score", ""),
                    "subject": test_case.get("subject", "")
                })

            df = pd.DataFrame(unhit_data)
            csv_path = Path(f"unhit_cases_{timestamp}.csv")
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            print(f"[OK] 未命中案例已保存到: {csv_path}")

        # 3. 保存执行日志
        log_path = Path(f"test_execution_{timestamp}.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"最终回溯测试执行日志\n")
            f.write(f"时间：{datetime.now().isoformat()}\n")
            f.write(f"样本量：{report['test_config']['sample_size']}\n")
            f.write(f"整体命中率：{report['overall_results']['hit_rate']:.2f}%\n\n")

            f.write("各位次段命中率：\n")
            for segment, rate in report["segment_results"].items():
                f.write(f"{segment}: {rate:.2f}%\n")

            f.write(f"\n未命中案例数：{report['unhit_cases_count']}\n")

        print(f"[OK] 执行日志已保存到: {log_path}")

        return report_path

def main():
    runner = FinalBacktestRunner()

    # 运行回溯测试
    report = runner.run_final_backtest(sample_size=500)

    # 保存结果
    report_path = runner.save_results(report)

    # 输出总结
    print(f"\n=== 测试完成 ===")
    print(f"报告文件：{report_path}")
    print(f"整体命中率：{report['overall_results']['hit_rate']:.2f}%")

    # 评估结果
    if report['overall_results']['hit_rate'] >= 85:
        print("优秀：算法优秀，可部署上线")
    elif report['overall_results']['hit_rate'] >= 75:
        print("良好：算法良好，建议优化后部署")
    elif report['overall_results']['hit_rate'] >= 65:
        print("及格：算法基本可用，需要优化")
    else:
        print("不及格：算法需要重大调整")

if __name__ == "__main__":
    main()