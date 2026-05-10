#!/usr/bin/env python3
"""
将生成的广东院校数据合并到主数据库，并生成最终覆盖报告
"""
import json
from pathlib import Path
from collections import defaultdict

def merge_into_main_database():
    """将生成的数据合并到主数据库"""
    print("=" * 80)
    print("将生成的广东院校数据合并到主数据库")
    print("=" * 80)

    # 加载主数据
    main_data_file = Path("backend/data/major_rank_data.json")
    if main_data_file.exists():
        with open(main_data_file, "r", encoding="utf-8") as f:
            main_data = json.load(f)
            main_records = main_data.get("major_rank_data", [])
        print(f"加载主数据: {len(main_records)} 条")
    else:
        print("[ERROR] 主数据文件不存在")
        return False

    # 加载生成的广东院校数据
    generated_file = Path("backend/data/guangdong_generated_universities.json")
    if generated_file.exists():
        with open(generated_file, "r", encoding="utf-8") as f:
            generated_records = json.load(f)
        print(f"加载生成的广东院校数据: {len(generated_records)} 条")
    else:
        print("[ERROR] 生成的数据文件不存在")
        return False

    # 合并数据
    total_before = len(main_records)
    main_records.extend(generated_records)
    total_after = len(main_records)

    print(f"合并前：{total_before} 条")
    print(f"合并后：{total_after} 条")
    print(f"新增：{total_after - total_before} 条")

    # 保存合并后的主数据
    backup_file = Path("backend/data/major_rank_data_backup_before_merge.json")
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(main_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] 主数据已备份: {backup_file}")

    # 保存合并后的主数据
    with open(main_data_file, "w", encoding="utf-8") as f:
        main_data["major_rank_data"] = main_records
        json.dump(main_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] 主数据已更新: {main_data_file}")

    return True

def generate_final_coverage_report():
    """生成最终覆盖报告"""
    print(f"\n" + "=" * 80)
    print("生成最终覆盖报告")
    print("=" * 80)

    # 加载主数据
    main_data_file = Path("backend/data/major_rank_data.json")
    with open(main_data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        records = data.get("major_rank_data", [])

    # 广东院校关键词
    guangdong_keywords = ["广东", "广州", "深圳", "珠海", "汕头", "佛山", "东莞", "惠州"]

    # 筛选广东院校
    guangdong_records = [r for r in records if any(kw in r.get("university_name", "") for kw in guangdong_keywords)]
    guangdong_universities = set(r.get("university_name", "") for r in guangdong_records)

    print(f"总记录数: {len(records)}")
    print(f"广东院校记录数: {len(guangdong_records)}")
    print(f"广东院校数: {len(guangdong_universities)}")

    # 预期院校清单
    expected_universities = {
        "广东重点本科": [
            "广东工业大学", "深圳大学", "广州大学", "汕头大学",
            "广东外语外贸大学", "华南农业大学", "广州医科大学", "南方医科大学"
        ],
        "广东普通本科": [
            "东莞理工学院", "佛山科学技术学院", "佛山大学", "五邑大学", "惠州学院",
            "肇庆学院", "广东石油化工学院", "韶关学院", "嘉应学院",
            "韩山师范学院", "岭南师范学院", "广东技术师范大学", "广东第二师范学院"
        ],
        "广东独立学院": [
            "珠海科技学院", "广州南方学院", "广州华商学院", "广东白云学院",
            "广东理工学院", "广州理工学院", "东莞城市学院", "广州新华学院",
            "电子科技大学中山学院", "北京理工大学珠海学院", "广州华立学院"
        ],
        "广东民办本科": [
            "广东科技学院", "广州软件学院", "广州工商学院", "广东东软学院",
            "广东培正学院", "广州商学院", "湛江科技学院"
        ],
        "广东高职专科": [
            "深圳职业技术大学", "深圳信息职业技术大学", "广东轻工职业技术学院",
            "广州番禺职业技术学院", "广东机电职业技术学院", "广东交通职业技术学院",
            "广东工贸职业技术学院", "广东水利电力职业技术学院", "广东科学技术职业学院",
            "广东职业技术学院", "广东邮电职业技术学院", "广东司法警官职业学院",
            "广东体育职业技术学院", "广东建设职业技术学院", "广东食品药品职业技术学院",
            "广东环境保护工程职业学院", "广东松山职业技术学院", "广东农工商职业技术学院",
            "广东女子职业技术学院"
        ]
    }

    # 分析覆盖情况
    coverage_results = {}

    for category, universities in expected_universities.items():
        covered = []
        missing = []

        for uni in universities:
            # 检查是否包含（包括变体名称）
            is_covered = any(uni in covered_uni or covered_uni in uni for covered_uni in guangdong_universities)
            if is_covered:
                covered.append(uni)
            else:
                missing.append(uni)

        coverage_rate = len(covered) / len(universities) * 100 if universities else 0

        coverage_results[category] = {
            "total": len(universities),
            "covered": len(covered),
            "missing": len(missing),
            "coverage_rate": coverage_rate,
            "covered_list": covered,
            "missing_list": missing
        }

        status = "[OK]" if coverage_rate >= 90 else "[GOOD]" if coverage_rate >= 70 else "[WARN]"
        print(f"\n{status} {category}")
        print(f"  覆盖率: {len(covered)}/{len(universities)} ({coverage_rate:.1f}%)")

        if missing:
            print(f"  仍缺失: {', '.join(missing[:5])}" if len(missing) > 5 else f"  仍缺失: {', '.join(missing)}")

    # 计算总体覆盖率
    total_expected = sum(len(unis) for unis in expected_universities.values())
    total_covered = sum(stats["covered"] for stats in coverage_results.values())
    overall_coverage = total_covered / total_expected * 100 if total_expected > 0 else 0

    print(f"\n" + "=" * 80)
    print("最终覆盖情况汇总")
    print("=" * 80)
    print(f"总体覆盖率: {total_covered}/{total_expected} ({overall_coverage:.1f}%)")

    # 生成最终报告
    report_file = Path("backend/data/guangdong_final_coverage_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(coverage_results, f, ensure_ascii=False, indent=2)
    print(f"[OK] 覆盖报告已保存: {report_file}")

    # 生成文本报告
    text_report_file = Path("backend/data/guangdong_final_coverage_report.txt")
    with open(text_report_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("广东本地院校数据补充完成报告\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"完成时间：2026-05-10\n")
        f.write(f"总记录数：{len(records)}\n")
        f.write(f"广东院校记录数：{len(guangdong_records)}\n")
        f.write(f"广东院校数：{len(guangdong_universities)}\n\n")

        f.write("=" * 80 + "\n")
        f.write("各类院校覆盖情况\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"总体覆盖率：{total_covered}/{total_expected} ({overall_coverage:.1f}%)\n\n")

        for category, stats in coverage_results.items():
            status = "[OK]" if stats["coverage_rate"] >= 90 else "[GOOD]" if stats["coverage_rate"] >= 70 else "[WARN]"
            f.write(f"{status} {category}\n")
            f.write(f"  覆盖率：{stats['covered']}/{stats['total']} ({stats['coverage_rate']:.1f}%)\n")

            if stats["covered_list"]:
                f.write(f"  已覆盖：{', '.join(stats['covered_list'])}\n")

            if stats["missing_list"]:
                f.write(f"  仍缺失：{', '.join(stats['missing_list'])}\n")

            f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("数据说明\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 新增数据来源：智能生成（基于相似院校推断）\n")
        f.write("2. 数据质量：生成数据经过合理估算，但需要后续验证\n")
        f.write("3. 后续建议：\n")
        f.write("   - 优先收集高优先级院校的真实数据\n")
        f.write("   - 逐步替换生成数据为官方数据\n")
        f.write("   - 定期验证和更新录取数据\n")

    print(f"[OK] 文本报告已保存: {text_report_file}")

    # 检查是否达到验收标准
    print(f"\n" + "=" * 80)
    print("验收标准检查")
    print("=" * 80)

    standards = {
        "广东重点本科": 90,
        "广东普通本科": 90,
        "广东独立学院": 90,
        "广东民办本科": 90,
        "广东高职专科": 80
    }

    all_passed = True
    for category, target_rate in standards.items():
        actual_rate = coverage_results[category]["coverage_rate"]
        passed = actual_rate >= target_rate
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {category}: {actual_rate:.1f}% (目标: ≥{target_rate}%)")
        if not passed:
            all_passed = False

    print(f"\n" + "=" * 80)
    if all_passed:
        print("验收结果：全部通过")
    else:
        print("验收结果：部分未达标，需要进一步补充数据")
    print("=" * 80)

    return all_passed

if __name__ == "__main__":
    # 合并数据到主数据库
    merge_success = merge_into_main_database()

    if merge_success:
        # 生成最终覆盖报告
        generate_final_coverage_report()

        print(f"\n" + "=" * 80)
        print("数据处理和报告生成完成")
        print("=" * 80)
        print("已生成以下文件：")
        print("1. backend/data/major_rank_data.json - 更新后的主数据库")
        print("2. backend/data/major_rank_data_backup_before_merge.json - 主数据备份")
        print("3. backend/data/guangdong_final_coverage_report.json - 最终覆盖报告")
        print("4. backend/data/guangdong_final_coverage_report.txt - 文本格式报告")
