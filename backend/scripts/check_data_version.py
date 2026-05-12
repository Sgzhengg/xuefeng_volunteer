"""
数据版本检查脚本
检查各年份数据的完整性和就绪状态
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.collection_service import get_collection_service


def check_university_data(year: int) -> dict:
    """检查院校数据"""
    data_file = project_root / "data" / "universities_list.json"

    if not data_file.exists():
        return {
            "exists": False,
            "count": 0,
            "status": "missing"
        }

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    universities = data.get("universities", [])

    return {
        "exists": True,
        "count": len(universities),
        "status": "ok" if len(universities) > 0 else "empty",
        "sample": universities[:3] if universities else []
    }


def check_admission_data(year: int) -> dict:
    """检查录取数据"""
    data_file = project_root / "data" / "major_rank_data.json"

    if not data_file.exists():
        return {
            "exists": False,
            "count": 0,
            "by_year": {},
            "by_province": {},
            "status": "missing"
        }

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])

    # 按年份统计
    by_year = {}
    by_province = {}

    for record in records:
        record_year = record.get("year")
        province = record.get("province", "")

        if record_year:
            by_year[record_year] = by_year.get(record_year, 0) + 1

        if province:
            by_province[province] = by_province.get(province, 0) + 1

    year_count = by_year.get(year, 0)

    return {
        "exists": True,
        "count": year_count,
        "total_count": len(records),
        "by_year": by_year,
        "by_province": by_province,
        "status": "ok" if year_count > 1000 else "insufficient"
    }


def check_majors_data(year: int) -> dict:
    """检查专业数据"""
    data_file = project_root / "data" / "majors_list.json"

    if not data_file.exists():
        return {
            "exists": False,
            "count": 0,
            "status": "missing"
        }

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    majors = data.get("majors", [])

    return {
        "exists": True,
        "count": len(majors),
        "status": "ok" if len(majors) > 0 else "empty"
    }


def calculate_completeness(year: int) -> int:
    """计算数据完整度百分比"""
    scores = []

    # 院校数据 (权重30%)
    uni_data = check_university_data(year)
    if uni_data["exists"] and uni_data["count"] > 2000:
        scores.append(30)
    elif uni_data["exists"]:
        scores.append(int(30 * uni_data["count"] / 2000))
    else:
        scores.append(0)

    # 录取数据 (权重50%)
    admission_data = check_admission_data(year)
    if admission_data["exists"] and admission_data["count"] > 40000:
        scores.append(50)
    elif admission_data["exists"]:
        scores.append(int(50 * admission_data["count"] / 40000))
    else:
        scores.append(0)

    # 专业数据 (权重20%)
    majors_data = check_majors_data(year)
    if majors_data["exists"] and majors_data["count"] > 1000:
        scores.append(20)
    elif majors_data["exists"]:
        scores.append(int(20 * majors_data["count"] / 1000))
    else:
        scores.append(0)

    return sum(scores)


def check_year_data(year: int) -> dict:
    """检查指定年份的数据状态"""
    print(f"\n{'='*50}")
    print(f"检查 {year} 年数据状态")
    print(f"{'='*50}")

    result = {
        "year": year,
        "checked_at": datetime.now().isoformat(),
        "data": {},
        "completeness": 0,
        "overall_status": "unknown"
    }

    # 检查各类数据
    print("\n[1/3] 检查院校数据...")
    uni_data = check_university_data(year)
    result["data"]["universities"] = uni_data
    print(f"  状态: {uni_data['status']}, 数量: {uni_data['count']}")

    print("\n[2/3] 检查录取数据...")
    admission_data = check_admission_data(year)
    result["data"]["admission"] = admission_data
    print(f"  状态: {admission_data['status']}, 数量: {admission_data['count']}")
    if admission_data["by_year"]:
        print(f"  年份分布: {admission_data['by_year']}")

    print("\n[3/3] 检查专业数据...")
    majors_data = check_majors_data(year)
    result["data"]["majors"] = majors_data
    print(f"  状态: {majors_data['status']}, 数量: {majors_data['count']}")

    # 计算完整度
    print("\n计算数据完整度...")
    completeness = calculate_completeness(year)
    result["completeness"] = completeness
    print(f"  完整度: {completeness}%")

    # 确定整体状态
    if completeness >= 95:
        result["overall_status"] = "ready"
    elif completeness >= 50:
        result["overall_status"] = "preparing"
    else:
        result["overall_status"] = "insufficient"

    print(f"\n整体状态: {result['overall_status']}")

    return result


def update_version_status(year: int, check_result: dict):
    """更新数据库中的版本状态"""
    service = get_collection_service()

    version = service.get_version(year)

    # 省份覆盖情况
    province_coverage = {}
    if "admission" in check_result["data"]:
        by_province = check_result["data"]["admission"].get("by_province", {})
        total_count = sum(by_province.values())
        for province, count in by_province.items():
            province_coverage[province] = {
                "count": count,
                "percentage": round(count / total_count * 100, 2) if total_count > 0 else 0
            }

    # 元数据
    metadata = {
        "last_checked": check_result["checked_at"],
        "data_sources": {
            "universities": check_result["data"]["universities"]["status"],
            "admission": check_result["data"]["admission"]["status"],
            "majors": check_result["data"]["majors"]["status"]
        },
        "counts": {
            "universities": check_result["data"]["universities"]["count"],
            "admission": check_result["data"]["admission"]["count"],
            "majors": check_result["data"]["majors"]["count"]
        }
    }

    # 更新版本信息
    service.update_version(
        year=year,
        status=check_result["overall_status"],
        data_completeness=check_result["completeness"],
        university_count=check_result["data"]["universities"]["count"],
        major_count=check_result["data"]["admission"]["count"],
        province_coverage=province_coverage,
        metadata=metadata
    )

    print(f"\n已更新 {year} 年版本状态到数据库")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="检查数据版本状态")
    parser.add_argument("--year", type=int, default=2026, help="检查的年份（默认：2026）")
    parser.add_argument("--all", action="store_true", help="检查所有年份")
    parser.add_argument("--update", action="store_true", help="更新数据库状态")

    args = parser.parse_args()

    if args.all:
        years = [2025, 2026]
    else:
        years = [args.year]

    for year in years:
        result = check_year_data(year)

        if args.update:
            update_version_status(year, result)

    print("\n" + "="*50)
    print("检查完成！")


if __name__ == "__main__":
    main()
