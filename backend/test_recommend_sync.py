# -*- coding: utf-8 -*-
"""
Simple test runner for RecommendationServiceV3 (synchronous).
This adapts the provided async snippet to the actual sync API in recommendation_service_v3.py
"""
from app.services.recommendation_service_v3 import RecommendationServiceV3


def main():
    svc = RecommendationServiceV3(load_data=True)
    # Call the sync recommend method (the module implements a synchronous recommend)
    res = svc.recommend(
        user_rank=800,
        province='广东',
        subject_type='理科',
        target_majors=[],
        verbose=True,
        min_total=30
    )

    print('\n=== 测试结果 ===')
    print('返回 top-level keys:', list(res.keys()))
    print('total_count:', res.get('total_count'))

    data = res.get('data', {})
    for cat, items in data.items():
        print(f"类别 {cat}: {len(items)} 条")

    # 打印每类前3条样例（如果存在）
    for cat, items in data.items():
        print(f"\n示例 - {cat} (最多3条):")
        for it in items[:3]:
            uni = it.get('university_name')
            grp = it.get('group_code')
            score = it.get('_score')
            print(f" - {uni} | group_code={grp} | score={score}")


if __name__ == '__main__':
    main()
