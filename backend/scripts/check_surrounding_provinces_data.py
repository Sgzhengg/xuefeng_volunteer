# -*- coding: utf-8 -*-
"""
广东周边省份数据完整性检查工具

功能：
1. 检查周边省份2025年录取数据总量
2. 分析关键院校覆盖情况
3. 检查位次段分布完整性
4. 评估专业覆盖度
5. 生成补全建议

使用方法：
    python check_surrounding_provinces_data.py

作者：学锋志愿教练团队
版本：1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

# ==================== 日志配置 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'surrounding_provinces_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== 配置常量 ====================

DATA_DIR = Path("../data")
MAIN_DATA_FILE = DATA_DIR / "major_rank_data.json"

# 广东周边省份配置
SURROUNDING_PROVINCES = {
    "湖南": {
        "priority": "P0",
        "target_records": 5000,
        "key_universities": [
            "中南大学",
            "湖南大学",
            "湖南师范大学",
            "湘潭大学",
            "长沙理工大学"
        ]
    },
    "江西": {
        "priority": "P0",
        "target_records": 5000,
        "key_universities": [
            "南昌大学",
            "江西财经大学",
            "江西师范大学"
        ]
    },
    "广西": {
        "priority": "P0",
        "target_records": 5000,
        "key_universities": [
            "广西大学",
            "广西医科大学",
            "广西师范大学"
        ]
    },
    "福建": {
        "priority": "P0",
        "target_records": 5000,
        "key_universities": [
            "厦门大学",
            "福州大学",
            "福建师范大学"
        ]
    },
    "湖北": {
        "priority": "P1",
        "target_records": 5000,
        "key_universities": [
            "武汉大学",
            "华中科技大学",
            "华中师范大学",
            "武汉理工大学",
            "中南财经政法大学"
        ]
    },
    "四川": {
        "priority": "P2",
        "target_records": 3000,
        "key_universities": [
            "四川大学",
            "电子科技大学",
            "西南交通大学",
            "西南财经大学"
        ]
    }
}

# 位次段定义
RANK_RANGES = {
    "1-10000": (1, 10000),
    "10001-30000": (10001, 30000),
    "30001-70000": (30001, 70000),
    "70001-120000": (70001, 120000),
    "120001-200000": (120001, 200000),
    "200001+": (200001, 999999)
}

# ==================== 数据分析函数 ====================

def check_province_data_completeness(province: str, config: Dict, records_2025: List[Dict]) -> Dict[str, Any]:
    """
    检查单个省份的数据完整性

    Args:
        province: 省份名称
        config: 省份配置
        records_2025: 2025年录取记录

    Returns:
        完整性检查结果
    """
    logger.info(f"[CHECK] 检查 {province} 省份数据完整性...")

    # 筛选该省的录取记录
    province_records = [r for r in records_2025 if r.get("province") == province]

    if not province_records:
        return {
            "province": province,
            "total_records": 0,
            "university_count": 0,
            "completeness": "NO_DATA",
            "issues": ["该省份没有任何2025年录取数据"]
        }

    # 1. 数据总量检查
    total_records = len(province_records)
    target_records = config.get("target_records", 3000)
    record_adequacy = total_records >= target_records

    # 2. 院校覆盖检查
    universities = {}
    for record in province_records:
        uni_name = record.get("university_name", "")
        if uni_name not in universities:
            universities[uni_name] = {
                "majors": set(),
                "min_rank": float('inf'),
                "max_rank": 0
            }

        universities[uni_name]["majors"].add(record.get("major_name", ""))
        universities[uni_name]["min_rank"] = min(universities[uni_name]["min_rank"], record.get("min_rank", 0))
        universities[uni_name]["max_rank"] = max(universities[uni_name]["max_rank"], record.get("min_rank", 0))

    university_count = len(universities)

    # 检查关键院校覆盖
    key_universities = config.get("key_universities", [])
    covered_key_unis = []
    missing_key_unis = []

    for key_uni in key_universities:
        found = False
        for uni_name in universities.keys():
            if key_uni in uni_name or uni_name in key_uni:
                covered_key_unis.append((key_uni, uni_name))
                found = True
                break
        if not found:
            missing_key_unis.append(key_uni)

    key_uni_coverage = len(covered_key_unis) / len(key_universities) if key_universities else 0

    # 3. 位次段分布检查
    rank_range_coverage = {}
    for range_name, (min_r, max_r) in RANK_RANGES.items():
        count = sum(1 for r in province_records if min_r <= r.get("min_rank", 0) <= max_r)
        rank_range_coverage[range_name] = count

    covered_ranges = sum(1 for count in rank_range_coverage.values() if count > 0)
    range_completeness = covered_ranges / len(RANK_RANGES)

    # 4. 专业覆盖检查
    universities_with_5plus_majors = sum(1 for uni in universities.values() if len(uni["majors"]) >= 5)
    major_coverage_adequacy = universities_with_5plus_majors / len(universities) if universities else 0

    # 5. 综合评估
    issues = []

    if not record_adequacy:
        issues.append(f"数据量不足：{total_records}条 < {target_records}条目标")

    if key_uni_coverage < 1.0:
        issues.append(f"关键院校缺失：{len(missing_key_unis)}所 - {', '.join(missing_key_unis)}")

    if range_completeness < 1.0:
        missing_ranges = [range_name for range_name, count in rank_range_coverage.items() if count == 0]
        issues.append(f"位次段缺失：{len(missing_ranges)}个 - {', '.join(missing_ranges)}")

    if major_coverage_adequacy < 0.8:
        issues.append(f"专业覆盖不足：仅{universities_with_5plus_majors}/{university_count}所院校有5个以上专业")

    # 确定完整性等级
    if record_adequacy and key_uni_coverage >= 1.0 and range_completeness >= 1.0 and major_coverage_adequacy >= 0.8:
        completeness = "优秀"
    elif record_adequacy and key_uni_coverage >= 0.8 and range_completeness >= 0.8:
        completeness = "良好"
    elif total_records > 0:
        completeness = "不足"
    else:
        completeness = "缺失"

    return {
        "province": province,
        "priority": config.get("priority", "P2"),
        "total_records": total_records,
        "target_records": target_records,
        "record_adequacy": record_adequacy,
        "university_count": university_count,
        "key_universities": {
            "total": len(key_universities),
            "covered": len(covered_key_unis),
            "missing": len(missing_key_unis),
            "covered_list": covered_key_unis,
            "missing_list": missing_key_unis,
            "coverage_rate": key_uni_coverage
        },
        "rank_ranges": rank_range_coverage,
        "range_completeness": {
            "covered": covered_ranges,
            "total": len(RANK_RANGES),
            "coverage_rate": range_completeness
        },
        "majors": {
            "universities_with_5plus": universities_with_5plus_majors,
            "total_universities": university_count,
            "coverage_rate": major_coverage_adequacy
        },
        "completeness": completeness,
        "issues": issues,
        "top_universities": sorted(universities.items(), key=lambda x: len(x[1]["majors"]), reverse=True)[:5]
    }

# ==================== 报告生成函数 ====================

def generate_completeness_report(province_results: List[Dict]) -> str:
    """
    生成数据完整性报告

    Args:
        province_results: 各省检查结果

    Returns:
        报告文件路径
    """
    logger.info("[REPORT] 生成周边省份数据完整性报告...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = Path(f"surrounding_provinces_completeness_report_{timestamp}.txt")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("广东周边省份数据完整性报告\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # 总体概览
        f.write("[总体概览]\n")
        f.write(f"检查省份数量: {len(province_results)} 个\n")

        excellent_count = sum(1 for r in province_results if r["completeness"] == "优秀")
        good_count = sum(1 for r in province_results if r["completeness"] == "良好")
        insufficient_count = sum(1 for r in province_results if r["completeness"] == "不足")
        missing_count = sum(1 for r in province_results if r["completeness"] == "缺失")

        f.write(f"优秀: {excellent_count} 个\n")
        f.write(f"良好: {good_count} 个\n")
        f.write(f"不足: {insufficient_count} 个\n")
        f.write(f"缺失: {missing_count} 个\n\n")

        # 各省数据概览表
        f.write("[各省数据概览表]\n")
        f.write(f"{'省份':<8} {'优先级':<8} {'记录数':<10} {'目标数':<10} {'院校数':<8} {'关键院校':<12} {'位次段':<12} {'完整性':<8}\n")
        f.write("-" * 100 + "\n")

        for result in sorted(province_results, key=lambda x: x["priority"]):
            province = result["province"]
            priority = result["priority"]
            records = result["total_records"]
            target = result["target_records"]
            unis = result["university_count"]
            key_uni_rate = f"{result['key_universities']['coverage_rate']*100:.0f}%"
            range_rate = f"{result['range_completeness']['coverage_rate']*100:.0f}%"
            completeness = result["completeness"]

            record_status = "✅" if records >= target else "❌"
            range_status = "✅" if result['range_completeness']['coverage_rate'] >= 1.0 else "❌"

            f.write(f"{province:<8} {priority:<8} {records:<10} {target:<10} {unis:<8} {key_uni_rate:<12} {range_rate:<12} {completeness:<8}\n")

        # 详细省份分析
        f.write("\n[详细省份分析]\n")

        for result in sorted(province_results, key=lambda x: (x["priority"], -x["total_records"])):
            f.write(f"\n{'='*60}\n")
            f.write(f"省份: {result['province']} ({result['priority']})\n")
            f.write(f"完整性评估: {result['completeness']}\n")
            f.write(f"{'='*60}\n")

            # 数据量
            f.write(f"\n1. 数据量: {result['total_records']:,} 条 (目标: {result['target_records']:,} 条)\n")
            if result['total_records'] < result['target_records']:
                f.write(f"   状态: ❌ 不足 (缺口: {result['target_records'] - result['total_records']:,} 条)\n")
            else:
                f.write(f"   状态: ✅ 达标\n")

            # 院校覆盖
            f.write(f"\n2. 院校覆盖: {result['university_count']} 所院校\n")
            key_unis = result['key_universities']
            f.write(f"   关键院校: {key_unis['covered']}/{key_unis['total']} ({key_unis['coverage_rate']*100:.0f}%)\n")

            if key_unis['covered_list']:
                f.write(f"   ✅ 已覆盖:\n")
                for original, actual in key_unis['covered_list']:
                    uni_info = next((uni for uni in result['top_universities'] if original in uni[0] or uni[0] in original), None)
                    if uni_info:
                        major_count = len(uni_info[1]['majors'])
                        f.write(f"      - {actual} ({major_count}个专业)\n")
                    else:
                        f.write(f"      - {actual}\n")

            if key_unis['missing_list']:
                f.write(f"   ❌ 缺失: {', '.join(key_unis['missing_list'])}\n")

            # 位次段覆盖
            f.write(f"\n3. 位次段覆盖: {result['range_completeness']['covered']}/{result['range_completeness']['total']} 个段位\n")
            ranges = result['rank_ranges']
            for range_name, count in ranges.items():
                status = "✅" if count > 0 else "❌"
                f.write(f"   {status} {range_name}: {count:,} 条\n")

            # 专业覆盖
            f.write(f"\n4. 专业覆盖: {result['majors']['universities_with_5plus']}/{result['majors']['total_universities']} 所院校有5个以上专业\n")
            f.write(f"   覆盖率: {result['majors']['coverage_rate']*100:.0f}%\n")

            # 顶级院校
            if result['top_universities']:
                f.write(f"\n5. 该省数据最全的院校:\n")
                for i, (uni_name, uni_data) in enumerate(result['top_universities'][:5], 1):
                    major_count = len(uni_data['majors'])
                    rank_range = f"{uni_data['min_rank']:,}-{uni_data['max_rank']:,}"
                    f.write(f"   {i}. {uni_name}\n")
                    f.write(f"      专业数: {major_count} 个 | 位次范围: {rank_range}\n")

            # 问题清单
            if result['issues']:
                f.write(f"\n6. 问题清单:\n")
                for issue in result['issues']:
                    f.write(f"   ❌ {issue}\n")

        # 补全建议
        f.write(f"\n\n{'='*80}\n")
        f.write("[补全建议]\n")
        f.write(f"{'='*80}\n\n")

        # 按优先级分组
        p0_provinces = [r for r in province_results if r["priority"] == "P0" and r["completeness"] in ["不足", "缺失"]]
        p1_provinces = [r for r in province_results if r["priority"] == "P1" and r["completeness"] in ["不足", "缺失"]]
        p2_provinces = [r for r in province_results if r["priority"] == "P2" and r["completeness"] in ["不足", "缺失"]]

        if p0_provinces:
            f.write("【P0优先级 - 立即处理】\n\n")
            for result in p0_provinces:
                f.write(f"{result['province']}:\n")
                f.write(f"  当前状态: {result['completeness']} ({result['total_records']}条记录)\n")

                # 计算需要补充的记录数
                needed_records = result['target_records'] - result['total_records']
                if needed_records > 0:
                    f.write(f"  建议补充: {needed_records:,} 条录取记录\n")

                # 建议补充的关键院校
                if result['key_universities']['missing_list']:
                    f.write(f"  优先补充院校: {', '.join(result['key_universities']['missing_list'])}\n")

                # 建议补充的位次段
                missing_ranges = [range_name for range_name, count in result['rank_ranges'].items() if count == 0]
                if missing_ranges:
                    f.write(f"  优先补充位次段: {', '.join(missing_ranges)}\n")

                f.write("\n")

        if p1_provinces:
            f.write("【P1优先级 - 近期处理】\n\n")
            for result in p1_provinces:
                f.write(f"{result['province']}: {result['completeness']} ({result['total_records']}条记录)\n")
                if result['issues']:
                    f.write(f"  主要问题: {result['issues'][0]}\n")
                f.write("\n")

        if p2_provinces:
            f.write("【P2优先级 - 后续优化】\n\n")
            for result in p2_provinces:
                f.write(f"{result['province']}: {result['completeness']} ({result['total_records']}条记录)\n")
            f.write("\n")

        # 总体建议
        f.write("【总体建议】\n\n")
        total_issues = sum(len(r['issues']) for r in province_results)
        if total_issues == 0:
            f.write("✅ 所有周边省份数据完整性良好，无需额外补全。\n")
        else:
            f.write(f"⚠️ 发现 {total_issues} 个问题，建议按优先级逐步解决。\n")
            f.write("📊 建议优先补充P0省份的关键院校和中等位次段数据。\n")
            f.write("🎯 重点目标：确保广东考生在周边省份有充足的院校选择。\n")

    logger.info(f"[OK] 完整性报告已保存: {report_file}")
    return str(report_file)

# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    print("=" * 80)
    print("广东周边省份数据完整性检查工具")
    print("=" * 80)
    print()

    # 读取数据
    logger.info("[LOAD] 读取主数据文件...")
    with open(MAIN_DATA_FILE.resolve(), 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])
    records_2025 = [r for r in records if r.get("year") == 2025]

    logger.info(f"[OK] 数据加载完成: {len(records_2025):,} 条2025年记录")

    # 检查各周边省份
    print("[CHECK] 开始检查周边省份数据完整性...")
    print()

    province_results = []

    for province, config in SURROUNDING_PROVINCES.items():
        result = check_province_data_completeness(province, config, records_2025)
        province_results.append(result)

        # 输出简略结果
        print(f"{province} ({config['priority']}): {result['completeness']} - {result['total_records']:,}条记录")

    # 生成报告
    print()
    print("[REPORT] 生成完整性报告...")
    report_file = generate_completeness_report(province_results)

    # 统计结果
    print()
    print("=" * 80)
    print("[检查完成] 周边省份数据完整性检查")
    print("=" * 80)

    excellent = sum(1 for r in province_results if r["completeness"] == "优秀")
    good = sum(1 for r in province_results if r["completeness"] == "良好")
    insufficient = sum(1 for r in province_results if r["completeness"] == "不足")
    missing = sum(1 for r in province_results if r["completeness"] == "缺失")

    print(f"优秀: {excellent} 个")
    print(f"良好: {good} 个")
    print(f"不足: {insufficient} 个")
    print(f"缺失: {missing} 个")
    print()
    print(f"详细报告: {report_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()