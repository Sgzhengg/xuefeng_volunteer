"""
专业级推荐算法测试脚本
验证专业级推荐功能是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加backend目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.professional_recommendation_service import professional_recommendation_service


async def test_professional_recommendation():
    """测试专业级推荐"""
    print("=" * 60)
    print("专业级推荐算法测试")
    print("=" * 60)

    # 测试用例1：高分学生
    print("\n[测试1] 高分学生（680分，位次500）")
    result1 = await professional_recommendation_service.generate_professional_recommendation(
        province="江苏",
        score=680,
        rank=500,
        subject_type="物理类",
        target_majors=["计算机科学与技术"]
    )

    if result1["success"]:
        data = result1["data"]
        print(f"  推荐专业数：{len(data['专业志愿'])}")
        print(f"  冲刺：{len(data['冲刺'])}个")
        print(f"  稳妥：{len(data['稳妥'])}个")
        print(f"  保底：{len(data['保底'])}个")

        if data['专业志愿']:
            print(f"\n  TOP3推荐：")
            for i, rec in enumerate(data['专业志愿'][:3], 1):
                print(f"    {i}. {rec['university_name']} - {rec['major_name']}")
                print(f"       概率：{rec['probability']}%，位次差距：{rec['rank_gap']}")
    else:
        print("  推荐失败")

    # 测试用例2：中等分数学生
    print("\n[测试2] 中等分数学生（550分，位次20000）")
    result2 = await professional_recommendation_service.generate_professional_recommendation(
        province="江苏",
        score=550,
        rank=20000,
        subject_type="物理类",
        target_majors=["计算机科学与技术", "软件工程"]
    )

    if result2["success"]:
        data = result2["data"]
        print(f"  推荐专业数：{len(data['专业志愿'])}")
        print(f"  冲刺：{len(data['冲刺'])}个")
        print(f"  稳妥：{len(data['稳妥'])}个")
        print(f"  保底：{len(data['保底'])}个")

        print(f"\n  TOP5推荐：")
        for i, rec in enumerate(data['专业志愿'][:5], 1):
            print(f"    {i}. {rec['university_name']} - {rec['major_name']}")
            print(f"       概率：{rec['probability']}%，类别：{rec['category']}")
    else:
        print("  推荐失败")

    # 测试用例3：低分学生
    print("\n[测试3] 低分学生（420分，位次70000）")
    result3 = await professional_recommendation_service.generate_professional_recommendation(
        province="江苏",
        score=420,
        rank=70000,
        subject_type="物理类",
        target_majors=["计算机科学与技术"]
    )

    if result3["success"]:
        data = result3["data"]
        print(f"  推荐专业数：{len(data['专业志愿'])}")
        print(f"  冲刺：{len(data['冲刺'])}个")
        print(f"  稳妥：{len(data['稳妥'])}个")
        print(f"  保底：{len(data['保底'])}个")

        if data['专业志愿']:
            print(f"\n  保底专业：")
            for i, rec in enumerate(data['保底'][:3], 1):
                print(f"    {i}. {rec['university_name']} - {rec['major_name']}")
                print(f"       概率：{rec['probability']}%，位次：{rec['min_rank']}")
    else:
        print("  推荐失败")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_professional_recommendation())
