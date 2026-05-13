# -*- coding: utf-8 -*-
"""Step 3: 关联招生计划与投档线数据，生成缺失报告

1. 加载 guangdong_2025_admission_plan.json (招生计划)
2. 加载 major_rank_data.json (投档线)
3. 按 院校名称+专业组代码 关联
4. 输出 missing_admission_rank_report.csv
"""
import json
import csv
import os
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / "data"
PLAN_FILE = DATA_DIR / "guangdong_2025_admission_plan.json"
RANK_FILE = DATA_DIR / "major_rank_data.json"
OUTPUT_FILE = DATA_DIR / "missing_admission_rank_report.csv"


def clean(val):
    if val is None:
        return ""
    return str(val).replace("\n", "").replace("\r", "").strip()


def main():
    print(f"[Step 3] 加载招生计划: {PLAN_FILE}")
    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        plan_data = json.load(f)
    plan_records = plan_data.get("by_year", {}).get("2025", [])
    print(f"  招生计划记录数: {len(plan_records)}")

    # 按 院校名称_专业组代码 聚合招生计划
    plan_groups = defaultdict(list)
    for rec in plan_records:
        key = f"{rec['university_name']}_{rec['group_code']}"
        plan_groups[key].append(rec)

    print(f"  招生计划专业组数: {len(plan_groups)}")

    # 加载投档线数据
    print(f"  加载投档线: {RANK_FILE}")
    with open(RANK_FILE, "r", encoding="utf-8") as f:
        rank_data = json.load(f)

    if isinstance(rank_data, list):
        rank_records = rank_data
    else:
        rank_records = rank_data.get("major_rank_data", [])
        if not rank_records:
            rank_records = rank_data.get("records", rank_data.get("data", []))

    print(f"  投档线记录数: {len(rank_records)}")

    # 按 院校名称_专业组代码 建立索引
    rank_groups = set()
    for rec in rank_records:
        uni_name = clean(rec.get("university_name", ""))
        group_code = clean(rec.get("group_code", ""))
        year = rec.get("year", 0)
        if uni_name and group_code:
            key = f"{uni_name}_{group_code}"
            rank_groups.add(key)

    print(f"  投档线专业组数: {len(rank_groups)}")

    # 匹配：有招生计划但无投档线
    matched = 0
    missing = []

    for key, plans in plan_groups.items():
        if key in rank_groups:
            matched += 1
        else:
            sample = plans[0]
            missing.append({
                "university_name": sample["university_name"],
                "university_code": sample["university_code"],
                "group_code": sample["group_code"],
                "category": sample["category"],
                "batch": sample["batch"],
                "subjects": sample.get("subjects_requirement", ""),
                "plan_total": sum(p.get("plan_count", 0) for p in plans),
                "major_count": len(plans),
                "sample_majors": ", ".join(p["major_name"] for p in plans[:5]),
            })

    print(f"  匹配成功: {matched}")
    print(f"  缺失投档线: {len(missing)}")

    # 按院校统计
    missing_by_uni = defaultdict(int)
    for m in missing:
        missing_by_uni[m["university_name"]] += 1

    # 输出 CSV
    with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as f:
        if missing:
            writer = csv.DictWriter(f, fieldnames=missing[0].keys())
            writer.writeheader()
            writer.writerows(missing)

    print(f"  输出: {OUTPUT_FILE} ({len(missing)} rows)")

    # 输出缺失最多的院校
    print(f"\n  缺失投档线最多的前10所院校:")
    for uni, cnt in sorted(missing_by_uni.items(), key=lambda x: -x[1])[:10]:
        print(f"    {uni}: {cnt} 组")

    # 覆盖率统计
    coverage = matched / max(1, len(plan_groups)) * 100
    print(f"\n  投档线覆盖率: {coverage:.1f}% ({matched}/{len(plan_groups)})")

    print("[Step 3] Done.")


if __name__ == "__main__":
    main()
