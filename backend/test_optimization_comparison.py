"""
推荐算法优化对比测试
对比优化前后的推荐质量差异
"""

import asyncio
import sys
from pathlib import Path

# 添加backend目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.professional_recommendation_service import professional_recommendation_service
from app.services.optimized_recommendation_service import optimized_recommendation_service


async def compare_recommendations():
    """对比优化前后的推荐结果"""
    print("=" * 80)
    print("推荐算法优化对比测试")
    print("=" * 80)

    # 测试用例
    test_cases = [
        {
            "name": "高分学生（680分，位次500）",
            "params": {
                "province": "江苏",
                "score": 680,
                "rank": 500,
                "subject_type": "物理类",
                "target_majors": ["计算机科学与技术"]
            }
        },
        {
            "name": "中等分数学生（580分，位次15000）",
            "params": {
                "province": "江苏",
                "score": 580,
                "rank": 15000,
                "subject_type": "物理类",
                "target_majors": ["计算机科学与技术", "软件工程"]
            }
        },
        {
            "name": "低分学生（480分，位次50000）",
            "params": {
                "province": "江苏",
                "score": 480,
                "rank": 50000,
                "subject_type": "物理类",
                "target_majors": ["计算机科学与技术"]
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"[测试用例 {i}] {test_case['name']}")
        print(f"{'=' * 80}")

        params = test_case["params"]

        # 使用旧算法生成推荐
        print("\n[旧算法]")
        result_old = await professional_recommendation_service.generate_professional_recommendation(
            **params
        )

        if result_old["success"]:
            data_old = result_old["data"]
            print(f"  推荐专业数：{len(data_old['专业志愿'])}")
            print(f"  冲刺：{len(data_old['冲刺'])}个，稳妥：{len(data_old['稳妥'])}个，保底：{len(data_old['保底'])}个")
            print(f"  平均概率：{data_old['analysis']['avg_probability']:.1f}%")

            if data_old['专业志愿']:
                print(f"\n  TOP5推荐：")
                for j, rec in enumerate(data_old['专业志愿'][:5], 1):
                    print(f"    {j}. {rec['university_name']} - {rec['major_name']}")
                    print(f"       概率：{rec['probability']}%，类别：{rec['category']}")

        # 使用新算法生成推荐
        print("\n[新算法]")
        result_new = await optimized_recommendation_service.generate_professional_recommendation(
            **params
        )

        if result_new["success"]:
            data_new = result_new["data"]
            print(f"  推荐专业数：{len(data_new['专业志愿'])}")
            print(f"  冲刺：{len(data_new['冲刺'])}个，稳妥：{len(data_new['稳妥'])}个，保底：{len(data_new['保底'])}个")
            print(f"  平均概率：{data_new['analysis']['avg_probability']:.1f}%")

            # 数据来源统计
            data_sources = data_new['analysis'].get('data_sources', {})
            print(f"  数据来源：官方数据{data_sources.get('official', 0)}条，估算数据{data_sources.get('estimated', 0)}条")

            if data_new['专业志愿']:
                print(f"\n  TOP5推荐：")
                for j, rec in enumerate(data_new['专业志愿'][:5], 1):
                    print(f"    {j}. {rec['university_name']} - {rec['major_name']}")
                    print(f"       概率：{rec['probability']}%，类别：{rec['category']}，来源：{rec.get('data_source', '')}")

        # 对比分析
        if result_old["success"] and result_new["success"]:
            print(f"\n[对比分析]")
            data_old = result_old["data"]
            data_new = result_new["data"]

            # 概率分布对比
            old_probs = [r["probability"] for r in data_old["专业志愿"]]
            new_probs = [r["probability"] for r in data_new["专业志愿"]]

            print(f"  概率范围：")
            print(f"    旧算法：{min(old_probs)}% - {max(old_probs)}%")
            print(f"    新算法：{min(new_probs)}% - {max(new_probs)}%")

            # 冲稳保分布对比
            old_categories = data_old["analysis"]["category_counts"]
            new_categories = data_new["analysis"]["category_counts"]

            print(f"\n  冲稳保分布：")
            print(f"    旧算法 - 冲刺:{old_categories['冲刺']}, 稳妥:{old_categories['稳妥']}, 保底:{old_categories['保底']}")
            print(f"    新算法 - 冲刺:{new_categories['冲刺']}, 稳妥:{new_categories['稳妥']}, 保底:{new_categories['保底']}")

            # 数据质量对比
            if "data_sources" in data_new["analysis"]:
                print(f"\n  数据质量提升：")
                print(f"    新算法使用{data_new['analysis']['data_sources'].get('official', 0)}条官方数据")

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(compare_recommendations())
