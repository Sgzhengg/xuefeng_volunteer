# -*- coding: utf-8 -*-
"""
数据覆盖审计工具 - 验证是否满足推荐算法需求

功能：
1. 位次连续性检查 - 每5000位次区间的记录数
2. 地域覆盖检查 - 广东省数据分层分析
3. 省外覆盖检查 - 全国院校覆盖情况
4. 专业覆盖检查 - 专业级推荐数据完整性
5. 降级机制检查 - 各扩圈层级数据可用性

使用方法：
    python data_coverage_audit.py

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
        logging.FileHandler(f'data_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== 配置常量 ====================

DATA_DIR = Path("../data")
MAIN_DATA_FILE = DATA_DIR / "major_rank_data.json"

# 位次区间定义
RANK_INTERVALS = []
for i in range(0, 350000, 5000):
    rank_range = f"{i+1}-{i+5000}"
    RANK_INTERVALS.append((i+1, i+5000, rank_range))

# 主要位次段
MAIN_RANK_SEGMENTS = {
    "1-10000": (1, 10000),
    "10001-30000": (10001, 30000),
    "30001-70000": (30001, 70000),
    "70001-120000": (70001, 120000),
    "120001-200000": (120001, 200000),
    "200001-350000": (200001, 350000)
}

# 985和211院校清单
TOP_985_UNIVERSITIES = [
    '北京大学', '清华大学', '复旦大学', '上海交通大学', '浙江大学',
    '中国科学技术大学', '南京大学', '西安交通大学', '哈尔滨工业大学',
    '中山大学', '华中科技大学', '武汉大学', '四川大学', '吉林大学',
    '南开大学', '天津大学', '山东大学', '中南大学', '华南理工大学',
    '厦门大学', '同济大学', '东南大学', '重庆大学', '大连理工大学',
    '华东师范大学', '北京师范大学', '中国人民大学', '兰州大学',
    '西北工业大学', '湖南大学', '东北大学', '电子科技大学',
    '北京航空航天大学', '北京理工大学', '中国农业大学', '中央民族大学',
    '西北农林科技大学', '中国海洋大学', '国防科技大学'
]

TOP_211_UNIVERSITIES = [
    '上海财经大学', '中央财经大学', '对外经济贸易大学',
    '北京外国语大学', '上海外国语大学',
    '中国政法大学', '西南政法大学',
    '北京邮电大学', '西安电子科技大学',
    '华中师范大学', '华南师范大学', '南京师范大学',
    '西南交通大学', '苏州大学', '上海大学',
    '暨南大学', '华南师范大学', '南昌大学', '湖南师范大学',
    '武汉理工大学', '中南财经政法大学', '华中农业大学',
    '西南财经大学', '四川农业大学', '东北师范大学',
    '西北大学', '长安大学', '陕西师范大学',
    '湖南师范大学', '福州大学', '福建师范大学', '华侨大学',
    '广西大学', '广西医科大学', '广西师范大学', '桂林电子科技大学'
]

# ==================== 数据加载函数 ====================

def load_data() -> List[Dict]:
    """加载主数据文件"""
    logger.info("[LOAD] 加载主数据文件...")

    with open(MAIN_DATA_FILE.resolve(), 'r', encoding='utf-8') as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])
    records_2025 = [r for r in records if r.get("year") == 2025]

    logger.info(f"[OK] 数据加载完成: {len(records_2025):,} 条2025年记录")
    return records_2025

# ==================== 位次连续性检查 ====================

def check_rank_continuity(records: List[Dict]) -> Dict[str, Any]:
    """
    检查位次连续性 - 每5000位次区间的记录数

    Returns:
        位次连续性检查结果
    """
    logger.info("[CHECK] 检查位次连续性...")

    interval_stats = {}
    insufficient_intervals = []

    for min_rank, max_rank, range_name in RANK_INTERVALS:
        # 统计该区间的记录数
        interval_records = [
            r for r in records
            if min_rank <= r.get("min_rank", 0) <= max_rank
        ]

        count = len(interval_records)
        is_sufficient = count >= 50  # 最低标准：每区间至少50条记录

        interval_stats[range_name] = {
            "count": count,
            "sufficient": is_sufficient,
            "sample_universities": list(set(r.get("university_name", "") for r in interval_records[:3])) if interval_records else []
        }

        if not is_sufficient:
            insufficient_intervals.append({
                "range": range_name,
                "count": count,
                "gap": 50 - count
            })

    # 统计总体情况
    total_intervals = len(RANK_INTERVALS)
    sufficient_intervals = sum(1 for stat in interval_stats.values() if stat["sufficient"])

    logger.info(f"[OK] 位次连续性检查完成: {sufficient_intervals}/{total_intervals} 区间达标")

    return {
        "total_intervals": total_intervals,
        "sufficient_intervals": sufficient_intervals,
        "insufficient_rate": (total_intervals - sufficient_intervals) / total_intervals,
        "interval_stats": interval_stats,
        "insufficient_intervals": insufficient_intervals
    }

# ==================== 地域覆盖检查 ====================

def check_guangdong_coverage(records: List[Dict]) -> Dict[str, Any]:
    """
    检查广东省数据覆盖情况

    Returns:
        广东省数据覆盖检查结果
    """
    logger.info("[CHECK] 检查广东省数据覆盖...")

    guangdong_records = [r for r in records if r.get("province") == "广东"]

    # 按位次段统计
    segment_stats = {}
    insufficient_segments = []

    for segment_name, (min_rank, max_rank) in MAIN_RANK_SEGMENTS.items():
        segment_records = [
            r for r in guangdong_records
            if min_rank <= r.get("min_rank", 0) <= max_rank
        ]

        count = len(segment_records)
        is_sufficient = count >= 500  # 每个位次段至少500条记录

        segment_stats[segment_name] = {
            "count": count,
            "sufficient": is_sufficient,
            "percentage": (count / len(guangdong_records) * 100) if guangdong_records else 0,
            "sample_universities": list(set(r.get("university_name", "") for r in segment_records[:5])) if segment_records else []
        }

        if not is_sufficient:
            insufficient_segments.append({
                "segment": segment_name,
                "count": count,
                "gap": 500 - count
            })

    total_gd_records = len(guangdong_records)
    sufficient_segments = sum(1 for stat in segment_stats.values() if stat["sufficient"])

    logger.info(f"[OK] 广东省覆盖检查完成: {sufficient_segments}/6 位次段达标")

    return {
        "total_gd_records": total_gd_records,
        "sufficient_segments": sufficient_segments,
        "segment_stats": segment_stats,
        "insufficient_segments": insufficient_segments
    }

# ==================== 省外覆盖检查 ====================

def check_national_coverage(records: List[Dict]) -> Dict[str, Any]:
    """
    检查全国院校覆盖情况

    Returns:
        全国院校覆盖检查结果
    """
    logger.info("[CHECK] 检查全国院校覆盖...")

    # 检查985院校覆盖
    covered_985 = set()
    missing_985 = []

    for record in records:
        university = record.get("university_name", "")
        for top_uni in TOP_985_UNIVERSITIES:
            if top_uni in university or university in top_uni:
                covered_985.add(top_uni)
                break

    for uni in TOP_985_UNIVERSITIES:
        if uni not in covered_985:
            missing_985.append(uni)

    # 检查211院校覆盖
    covered_211 = set()
    missing_211 = []

    for record in records:
        university = record.get("university_name", "")
        for top_uni in TOP_211_UNIVERSITIES:
            if top_uni in university or university in top_uni:
                covered_211.add(top_uni)
                break

    for uni in TOP_211_UNIVERSITIES:
        if uni not in covered_211:
            missing_211.append(uni)

    # 检查普通本科覆盖（抽样检查）
    sample_normal_universities = [
        '深圳大学', '广州大学', '汕头大学', '广州医科大学',
        '广州中医药大学', '南方医科大学', '广东工业大学',
        '江苏大学', '扬州大学', '宁波大学'
    ]

    covered_normal = []
    missing_normal = []

    for uni in sample_normal_universities:
        found = any(uni in r.get("university_name", "") or r.get("university_name", "") in uni for r in records)
        if found:
            covered_normal.append(uni)
        else:
            missing_normal.append(uni)

    logger.info(f"[OK] 全国院校覆盖检查完成: 985-{len(covered_985)}/39, 211-{len(covered_211)}/77")

    return {
        "985": {
            "total": len(TOP_985_UNIVERSITIES),
            "covered": len(covered_985),
            "covered_list": list(covered_985),
            "missing_list": missing_985,
            "coverage_rate": len(covered_985) / len(TOP_985_UNIVERSITIES)
        },
        "211": {
            "total": len(TOP_211_UNIVERSITIES),
            "covered": len(covered_211),
            "covered_list": list(covered_211),
            "missing_list": missing_211,
            "coverage_rate": len(covered_211) / len(TOP_211_UNIVERSITIES)
        },
        "normal": {
            "sample_total": len(sample_normal_universities),
            "covered": len(covered_normal),
            "covered_list": covered_normal,
            "missing_list": missing_normal
        }
    }

# ==================== 专业覆盖检查 ====================

def check_major_coverage(records: List[Dict]) -> Dict[str, Any]:
    """
    检查专业级推荐数据完整性

    Returns:
        专业覆盖检查结果
    """
    logger.info("[CHECK] 检查专业覆盖...")

    # 检查专业名称覆盖率
    records_with_major_name = [r for r in records if r.get("major_name") and r.get("major_name") not in ["未分专业", ""]]
    major_name_coverage = len(records_with_major_name) / len(records) if records else 0

    # 检查专业代码覆盖率
    records_with_major_code = [r for r in records if r.get("major_code") and r.get("major_code") not in ["000000", ""]]
    major_code_coverage = len(records_with_major_code) / len(records) if records else 0

    # 检查每个院校的专业数
    university_majors = defaultdict(set)
    for record in records:
        university = record.get("university_name", "")
        major = record.get("major_name", "")
        if major and major not in ["未分专业", ""]:
            university_majors[university].add(major)

    # 统计专业数充足的院校
    universities_with_5plus_majors = sum(1 for majors in university_majors.values() if len(majors) >= 5)
    universities_with_insufficient_majors = [
        (uni, len(majors)) for uni, majors in university_majors.items() if len(majors) < 5
    ]

    major_coverage_rate = universities_with_5plus_majors / len(university_majors) if university_majors else 0

    logger.info(f"[OK] 专业覆盖检查完成: 专业名{major_name_coverage*100:.1f}%, 专业数充足{major_coverage_rate*100:.1f}%")

    return {
        "major_name_coverage": major_name_coverage,
        "major_code_coverage": major_code_coverage,
        "total_universities": len(university_majors),
        "universities_with_5plus_majors": universities_with_5plus_majors,
        "major_coverage_rate": major_coverage_rate,
        "universities_insufficient": universities_with_insufficient_majors[:20]  # 只列出前20个
    }

# ==================== 降级机制检查 ====================

def check_fallback_mechanism(records: List[Dict]) -> Dict[str, Any]:
    """
    检查各扩圈层级的数据可用性

    Returns:
        降级机制检查结果
    """
    logger.info("[CHECK] 检查降级机制数据可用性...")

    # 第1层：本省±15000
    guangdong_records = [r for r in records if r.get("province") == "广东"]
    layer1_count = len(guangdong_records)
    layer1_sufficient = layer1_count >= 1000  # 至少1000条广东记录

    # 第2层：周边省份±20000
    surrounding_provinces = ["湖南", "江西", "广西", "福建"]
    surrounding_records = [r for r in records if r.get("province") in surrounding_provinces]
    layer2_count = len(surrounding_records)
    layer2_sufficient = layer2_count >= 2000  # 至少2000条周边记录

    # 第3层：全国985/211±30000
    tier3_universities = TOP_985_UNIVERSITIES + TOP_211_UNIVERSITIES
    tier3_records = []
    for record in records:
        university = record.get("university_name", "")
        if any(top_uni in university or university in top_uni for top_uni in tier3_universities):
            tier3_records.append(record)

    layer3_count = len(tier3_records)
    layer3_sufficient = layer3_count >= 5000  # 至少5000条985/211记录

    # 第4层：全国宽范围±50000
    layer4_count = len(records)
    layer4_sufficient = layer4_count >= 10000  # 至少10000条总记录

    logger.info(f"[OK] 降级机制检查完成: 第1层{'✅' if layer1_sufficient else '❌'}, 第2层{'✅' if layer2_sufficient else '❌'}, 第3层{'✅' if layer3_sufficient else '❌'}, 第4层{'✅' if layer4_sufficient else '❌'}")

    return {
        "layer1": {
            "name": "本省±15000",
            "count": layer1_count,
            "sufficient": layer1_sufficient,
            "gap": 1000 - layer1_count if not layer1_sufficient else 0
        },
        "layer2": {
            "name": "周边省份±20000",
            "count": layer2_count,
            "sufficient": layer2_sufficient,
            "gap": 2000 - layer2_count if not layer2_sufficient else 0
        },
        "layer3": {
            "name": "全国985/211±30000",
            "count": layer3_count,
            "sufficient": layer3_sufficient,
            "gap": 5000 - layer3_count if not layer3_sufficient else 0
        },
        "layer4": {
            "name": "全国宽范围±50000",
            "count": layer4_count,
            "sufficient": layer4_sufficient,
            "gap": 10000 - layer4_count if not layer4_sufficient else 0
        }
    }

# ==================== 报告生成函数 ====================

def generate_audit_report(
    rank_result: Dict,
    guangdong_result: Dict,
    national_result: Dict,
    major_result: Dict,
    fallback_result: Dict
) -> str:
    """
    生成数据覆盖审计报告

    Returns:
        报告文件路径
    """
    logger.info("[REPORT] 生成数据覆盖审计报告...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = Path(f"data_coverage_audit_report_{timestamp}.txt")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("数据覆盖审计报告 - 验证是否满足推荐算法需求\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # 总体评估
        f.write("[总体评估]\n\n")

        total_checks = 5
        passed_checks = 0

        if rank_result["sufficient_intervals"] >= 60:  # 70个区间中至少60个达标
            passed_checks += 1
            f.write("✅ 位次连续性: 通过\n")
        else:
            f.write("❌ 位次连续性: 未通过\n")

        if guangdong_result["sufficient_segments"] >= 5:
            passed_checks += 1
            f.write("✅ 广东覆盖: 通过\n")
        else:
            f.write("❌ 广东覆盖: 未通过\n")

        if national_result["985"]["coverage_rate"] >= 0.95 and national_result["211"]["coverage_rate"] >= 0.95:
            passed_checks += 1
            f.write("✅ 全国院校覆盖: 通过\n")
        else:
            f.write("❌ 全国院校覆盖: 未通过\n")

        if major_result["major_name_coverage"] >= 0.95 and major_result["major_coverage_rate"] >= 0.70:
            passed_checks += 1
            f.write("✅ 专业覆盖: 通过\n")
        else:
            f.write("❌ 专业覆盖: 未通过\n")

        if all(layer["sufficient"] for layer in fallback_result.values()):
            passed_checks += 1
            f.write("✅ 降级机制: 通过\n")
        else:
            f.write("❌ 降级机制: 未通过\n")

        f.write(f"\n总体通过率: {passed_checks}/{total_checks} ({passed_checks*100//total_checks}%)\n\n")

        # 1. 位次连续性矩阵
        f.write("[1. 位次连续性矩阵]\n\n")
        f.write(f"{'位次区间':<15} {'记录数':<10} {'状态':<8} {'样例院校'}\n")
        f.write("-" * 80 + "\n")

        for range_name, stats in rank_result["interval_stats"].items():
            count = stats["count"]
            status = "✅充足" if stats["sufficient"] else "❌不足"
            sample = ", ".join(stats["sample_universities"][:2])
            f.write(f"{range_name:<15} {count:<10} {status:<8} {sample}\n")

        # 不充足区间清单
        if rank_result["insufficient_intervals"]:
            f.write(f"\n⚠️ 不充足区间 ({len(rank_result['insufficient_intervals'])}个):\n")
            for interval in rank_result["insufficient_intervals"]:
                f.write(f"  {interval['range']}: {interval['count']}条 (缺{interval['gap']}条)\n")

        # 2. 广东省数据分层表
        f.write(f"\n[2. 广东省数据分层表]\n\n")
        f.write(f"{'位次段':<20} {'记录数':<12} {'占比':<10} {'状态':<8} {'样例院校'}\n")
        f.write("-" * 80 + "\n")

        total_gd = guangdong_result["total_gd_records"]
        for segment_name, stats in guangdong_result["segment_stats"].items():
            count = stats["count"]
            percentage = stats["percentage"]
            status = "✅充足" if stats["sufficient"] else "❌不足"
            sample = ", ".join(stats["sample_universities"][:3])
            f.write(f"{segment_name:<20} {count:<12} {percentage:>6.1f}% {status:<8} {sample}\n")

        # 3. 全国院校覆盖清单
        f.write(f"\n[3. 全国院校覆盖清单]\n\n")

        f.write("985院校:\n")
        if national_result["985"]["missing_list"]:
            f.write(f"  ❌ 缺失 ({len(national_result['985']['missing_list'])}所): {', '.join(national_result['985']['missing_list'][:5])}")
            if len(national_result['985']['missing_list']) > 5:
                f.write(f" 等{len(national_result['985']['missing_list'])}所")
            f.write("\n")
        else:
            f.write(f"  ✅ 完全覆盖 {national_result['985']['covered']}/{national_result['985']['total']}所\n")

        f.write("\n211院校:\n")
        if national_result["211"]["missing_list"]:
            f.write(f"  ❌ 缺失 ({len(national_result['211']['missing_list'])}所): {', '.join(national_result['211']['missing_list'][:5])}")
            if len(national_result['211']['missing_list']) > 5:
                f.write(f" 等{len(national_result['211']['missing_list'])}所")
            f.write("\n")
        else:
            f.write(f"  ✅ 完全覆盖 {national_result['211']['covered']}/{national_result['211']['total']}所\n")

        f.write("\n普通本科 (抽样10所):\n")
        normal = national_result["normal"]
        f.write(f"  覆盖: {normal['covered']}/{normal['sample_total']}所\n")
        if normal["missing_list"]:
            f.write(f"  缺失: {', '.join(normal['missing_list'])}\n")

        # 4. 专业覆盖统计
        f.write(f"\n[4. 专业覆盖统计]\n\n")
        f.write(f"有专业名称记录: {major_result['major_name_coverage']*100:.1f}%\n")
        f.write(f"有专业代码记录: {major_result['major_code_coverage']*100:.1f}%\n")
        f.write(f"院校总数: {major_result['total_universities']}所\n")
        f.write(f"专业数≥5的院校: {major_result['universities_with_5plus_majors']}所 ({major_result['major_coverage_rate']*100:.1f}%)\n")

        if major_result["universities_insufficient"]:
            f.write(f"\n⚠️ 专业数不足的院校 (前20所):\n")
            for uni, major_count in major_result["universities_insufficient"]:
                f.write(f"  {uni}: {major_count}个专业\n")

        # 5. 降级机制检查
        f.write(f"\n[5. 降级机制兜底检查]\n\n")
        for layer_name, layer_data in fallback_result.items():
            status = "✅充足" if layer_data["sufficient"] else "❌不足"
            gap_info = f" (缺{layer_data['gap']}条)" if not layer_data["sufficient"] else ""
            f.write(f"{layer_data['name']}: {layer_data['count']:,}条 - {status}{gap_info}\n")

        # 6. 缺口分析
        f.write(f"\n[6. 缺口分析]\n\n")

        all_gaps = []

        # 位次连续性缺口
        if rank_result["insufficient_intervals"]:
            all_gaps.append({
                "category": "位次连续性",
                "priority": "P0",
                "count": len(rank_result["insufficient_intervals"]),
                "description": f"{len(rank_result['insufficient_intervals'])}个位次区间数据不足"
            })

        # 广东覆盖缺口
        if guangdong_result["insufficient_segments"]:
            all_gaps.append({
                "category": "广东覆盖",
                "priority": "P0",
                "count": len(guangdong_result["insufficient_segments"]),
                "description": f"{len(guangdong_result['insufficient_segments'])}个位次段数据不足"
            })

        # 院校覆盖缺口
        if national_result["985"]["missing_list"]:
            all_gaps.append({
                "category": "985院校",
                "priority": "P0",
                "count": len(national_result["985"]["missing_list"]),
                "description": f"缺失{len(national_result['985']['missing_list'])}所985院校"
            })

        if national_result["211"]["missing_list"]:
            all_gaps.append({
                "category": "211院校",
                "priority": "P0",
                "count": len(national_result["211"]["missing_list"]),
                "description": f"缺失{len(national_result['211']['missing_list'])}所211院校"
            })

        # 专业覆盖缺口
        if major_result["major_coverage_rate"] < 0.70:
            all_gaps.append({
                "category": "专业覆盖",
                "priority": "P1",
                "count": int(major_result["total_universities"] * (1 - major_result["major_coverage_rate"])),
                "description": f"{major_result['major_coverage_rate']*100:.0f}%院校专业数不足"
            })

        # 降级机制缺口
        insufficient_layers = [(name, data) for name, data in fallback_result.items() if not data["sufficient"]]
        if insufficient_layers:
            for layer_name, layer_data in insufficient_layers:
                all_gaps.append({
                    "category": f"降级机制-{layer_name}",
                    "priority": "P0",
                    "count": layer_data["gap"],
                    "description": f"{layer_data['name']}数据不足"
                })

        # 按优先级排序
        all_gaps.sort(key=lambda x: (x["priority"], x["count"]), reverse=True)

        if all_gaps:
            f.write(f"发现 {len(all_gaps)} 个缺口，按优先级排序:\n\n")
            for i, gap in enumerate(all_gaps, 1):
                f.write(f"{i}. [{gap['priority']}] {gap['category']}: {gap['description']}\n")
        else:
            f.write("✅ 未发现缺口，数据覆盖完整！\n")

        # 7. 补全建议
        f.write(f"\n[7. 补全建议]\n\n")

        if all_gaps:
            f.write("针对发现的问题，建议按以下优先级进行补全:\n\n")

            p0_gaps = [gap for gap in all_gaps if gap["priority"] == "P0"]
            p1_gaps = [gap for gap in all_gaps if gap["priority"] == "P1"]

            if p0_gaps:
                f.write("【P0优先级 - 立即处理】\n\n")
                for gap in p0_gaps:
                    f.write(f"• {gap['category']}: {gap['description']}\n")
                    if "位次" in gap['category']:
                        f.write("  建议: 补充相关位次段的录取数据，优先补充广东和周边省份院校\n")
                    elif "院校" in gap['category']:
                        f.write("  建议: 采集缺失院校的录取数据，优先补充985/211院校\n")
                    elif "广东" in gap['category']:
                        f.write("  建议: 重点补充广东省各分数段的录取数据\n")
                    f.write("\n")

            if p1_gaps:
                f.write("【P1优先级 - 近期处理】\n\n")
                for gap in p1_gaps:
                    f.write(f"• {gap['category']}: {gap['description']}\n")
                    f.write("  建议: 逐步提升院校专业覆盖率，确保每所院校至少5个专业\n\n")
        else:
            f.write("✅ 当前数据覆盖完整，满足算法运行需求！\n")

        # 验收标准检查
        f.write(f"\n[8. 验收标准检查]\n\n")

        acceptance_checks = [
            ("位次连续性", "每5000区间至少50条记录", rank_result["sufficient_intervals"] >= 60),
            ("广东覆盖", "每位次段至少500条记录", guangdong_result["sufficient_segments"] >= 5),
            ("985/211", "100%覆盖", national_result["985"]["coverage_rate"] >= 1.0 and national_result["211"]["coverage_rate"] >= 1.0),
            ("专业覆盖", "95%记录有专业名，70%院校有5+专业",
             major_result["major_name_coverage"] >= 0.95 and major_result["major_coverage_rate"] >= 0.70)
        ]

        f.write(f"{'检查项':<15} {'通过标准':<40} {'状态'}\n")
        f.write("-" * 80 + "\n")

        for check_name, standard, passed in acceptance_checks:
            status = "✅ 通过" if passed else "❌ 未通过"
            f.write(f"{check_name:<15} {standard:<40} {status}\n")

        passed_count = sum(1 for _, _, passed in acceptance_checks if passed)
        f.write(f"\n验收通过率: {passed_count}/{len(acceptance_checks)} ({passed_count*100//len(acceptance_checks)}%)\n")

    logger.info(f"[OK] 审计报告已保存: {report_file}")
    return str(report_file)

# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    print("=" * 80)
    print("数据覆盖审计工具 - 验证是否满足推荐算法需求")
    print("=" * 80)
    print()

    # 加载数据
    records = load_data()

    if not records:
        logger.error("[ERROR] 没有可用的2025年数据")
        return

    # 执行各项检查
    print("[CHECK] 开始执行数据覆盖审计...")
    print()

    print("[1/5] 检查位次连续性...")
    rank_result = check_rank_continuity(records)

    print("[2/5] 检查广东省数据覆盖...")
    guangdong_result = check_guangdong_coverage(records)

    print("[3/5] 检查全国院校覆盖...")
    national_result = check_national_coverage(records)

    print("[4/5] 检查专业覆盖...")
    major_result = check_major_coverage(records)

    print("[5/5] 检查降级机制...")
    fallback_result = check_fallback_mechanism(records)

    # 生成报告
    print()
    print("[REPORT] 生成数据覆盖审计报告...")
    audit_report = generate_audit_report(
        rank_result, guangdong_result, national_result,
        major_result, fallback_result
    )

    # 输出结果摘要
    print()
    print("=" * 80)
    print("[审计完成] 数据覆盖审计报告")
    print("=" * 80)

    print(f"位次连续性: {rank_result['sufficient_intervals']}/{rank_result['total_intervals']} 区间达标")
    print(f"广东覆盖: {guangdong_result['sufficient_segments']}/6 位次段达标")
    print(f"985院校: {national_result['985']['covered']}/{national_result['985']['total']} 所")
    print(f"211院校: {national_result['211']['covered']}/{national_result['211']['total']} 所")
    print(f"专业覆盖: {major_result['major_name_coverage']*100:.1f}% 记录有专业名")
    print()
    print(f"详细报告: {audit_report}")
    print("=" * 80)

if __name__ == "__main__":
    main()