# -*- coding: utf-8 -*-
"""
实际录取分布 vs 算法推荐分布 对比分析脚本

功能：
1. 从 major_rank_data.json 统计实际录取分布（985/211/本地/省外 占比）
2. 调用推荐API，记录算法推荐分布
3. 对比分析与偏差报告
4. 生成 JSON 对比报告

使用方法：
    cd backend
    python scripts/compare_distribution.py
    python scripts/compare_distribution.py --sample 200  # 自定义样本量
    python scripts/compare_distribution.py --quick        # 快速测试（50条）

作者：学锋志愿教练团队
日期：2025-05-11
"""

import json
import sys
import io
import time
import random
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime

import requests
from tqdm import tqdm

# 控制台UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ==================== 路径配置 ====================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "tests" / "results"

MAJOR_RANK_FILE = DATA_DIR / "major_rank_data.json"
UNIVERSITIES_FILE = DATA_DIR / "universities_list.json"
API_ENDPOINT = "http://localhost:8001/api/v1/recommendation/generate"
API_TIMEOUT = 30

# ==================== 位次段配置 ====================
RANK_SEGMENTS = [
    {"name": "1-10000", "min": 1, "max": 10000, "ratio": 0.10, "desc": "985/211顶尖段"},
    {"name": "10001-30000", "min": 10001, "max": 30000, "ratio": 0.15, "desc": "211/重点段"},
    {"name": "30001-70000", "min": 30001, "max": 70000, "ratio": 0.25, "desc": "一本段"},
    {"name": "70001-120000", "min": 70001, "max": 120000, "ratio": 0.25, "desc": "二本段"},
    {"name": "120001-200000", "min": 120001, "max": 200000, "ratio": 0.15, "desc": "民办/专科段"},
    {"name": "200001-350000", "min": 200001, "max": 350000, "ratio": 0.10, "desc": "专科段"},
]


# ==================== 院校层级映射 ====================
def build_university_level_map() -> Dict[str, str]:
    """从 universities_list.json 建立 院校名称 -> 层级 映射"""
    level_map = {}

    if not UNIVERSITIES_FILE.exists():
        print(f"[警告] 未找到院校列表文件: {UNIVERSITIES_FILE}")
        print("[提示] 将仅使用 major_rank_data.json 中的 university_level 字段")
        return level_map

    with open(UNIVERSITIES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    universities = data.get("universities", [])
    for uni in universities:
        name = uni.get("name", "").strip()
        level = uni.get("level", "").strip()
        if name and level:
            # 处理同名覆盖（保留985优先于211优先于其他）
            if name in level_map:
                existing = level_map[name]
                priority = {"985": 3, "211": 2, "普通本科": 1, "本科": 1, "高职": 0}
                if priority.get(level, 0) > priority.get(existing, 0):
                    level_map[name] = level
            else:
                level_map[name] = level

    level_counts = defaultdict(int)
    for level in level_map.values():
        level_counts[level] += 1
    print(f"[院校映射] 从 universities_list.json 加载了 {len(level_map)} 所院校的层级映射")
    print(f"  分布: 985={level_counts.get('985', 0)}, 211={level_counts.get('211', 0)}, "
          f"普通本科={level_counts.get('普通本科', 0)}, 高职={level_counts.get('高职', 0)}")

    return level_map


def classify_university(university_name: str,
                        university_level_from_record: str,
                        level_map: Dict[str, str]) -> Dict[str, Any]:
    """分类院校层级"""
    classification = {
        "is_985": False,
        "is_211": False,
        "is_regular": False,
        "is_vocational": False,
        "level": "unknown"
    }

    # 优先使用 mapping
    mapped_level = level_map.get(university_name, "")

    # 如果 mapping 中没有，使用记录本身的 university_level
    if not mapped_level:
        mapped_level = university_level_from_record or ""

    # 985院校关键词（对未分类院校进行启发式匹配）
    known_985 = [
        "北京大学", "清华大学", "复旦大学", "上海交通大学", "浙江大学",
        "中国科学技术大学", "南京大学", "中国人民大学", "中山大学",
        "华南理工大学", "武汉大学", "华中科技大学", "西安交通大学",
        "哈尔滨工业大学", "北京师范大学", "南开大学", "天津大学",
        "同济大学", "东南大学", "厦门大学", "四川大学", "电子科技大学",
        "吉林大学", "东北大学", "大连理工大学", "山东大学",
        "中国海洋大学", "西北工业大学", "兰州大学", "北京航空航天大学",
        "北京理工大学", "中国农业大学", "国防科技大学", "中央民族大学",
        "华东师范大学", "中南大学", "湖南大学", "重庆大学", "西北农林科技大学"
    ]
    known_211 = [
        "暨南大学", "华南师范大学", "北京邮电大学", "北京交通大学",
        "北京科技大学", "北京化工大学", "北京工业大学", "北京林业大学",
        "北京中医药大学", "北京外国语大学", "中国传媒大学",
        "中央财经大学", "对外经济贸易大学", "中国政法大学",
        "华北电力大学", "中国矿业大学", "中国石油大学",
        "中国地质大学", "东北师范大学", "东北林业大学",
        "华东理工大学", "东华大学", "上海外国语大学", "上海财经大学",
        "上海大学", "苏州大学", "南京航空航天大学", "南京理工大学",
        "中国药科大学", "河海大学", "江南大学", "南京农业大学",
        "南京师范大学", "合肥工业大学", "安徽大学", "福州大学",
        "南昌大学", "中国石油大学", "郑州大学", "武汉理工大学",
        "华中师范大学", "华中农业大学", "中南财经政法大学",
        "湖南师范大学", "西南交通大学", "四川农业大学",
        "西南大学", "西南财经大学", "贵州大学", "云南大学",
        "西藏大学", "西北大学", "西安电子科技大学", "长安大学",
        "陕西师范大学", "青海大学", "宁夏大学", "新疆大学",
        "石河子大学", "海南大学", "广西大学", "内蒙古大学",
        "延边大学", "辽宁大学", "大连海事大学", "太原理工大学",
        "华北电力大学", "河北工业大学", "哈尔滨工程大学",
        "东北农业大学", "东北师范大学", "第二军医大学", "第四军医大学"
    ]

    # 确定层级
    if mapped_level == "985" or university_name in known_985:
        classification["is_985"] = True
        classification["is_211"] = True
        classification["level"] = "985"
    elif mapped_level == "211" or university_name in known_211:
        classification["is_211"] = True
        classification["level"] = "211"
    elif mapped_level in ("普通本科", "本科") or mapped_level == "":
        # 无法识别时，按大学名判断
        name = university_name
        if any(kw in name for kw in ["大学", "学院"]) and not any(
                kw in name for kw in ["职业", "技术", "专科"]):
            classification["is_regular"] = True
            classification["level"] = "普通本科"
        elif any(kw in name for kw in ["职业", "技术", "专科"]):
            classification["is_vocational"] = True
            classification["level"] = "高职/专科"
        else:
            classification["is_regular"] = True
            classification["level"] = "普通本科"
    elif mapped_level == "高职":
        classification["is_vocational"] = True
        classification["level"] = "高职/专科"

    return classification


# ==================== 实际录取分布统计 ====================
def compute_actual_distribution(records: List[Dict],
                                level_map: Dict[str, str]) -> Dict[str, Any]:
    """统计 major_rank_data.json 中各段位的实际录取分布"""
    print("\n[统计] 正在计算实际录取分布...")

    # 先筛选广东2025有效记录
    gd_2025 = [
        r for r in records
        if isinstance(r, dict)
        and r.get("province") == "广东"
        and r.get("year") == 2025
        and r.get("min_rank") and r.get("min_rank") > 0
        and r.get("university_name")
    ]
    print(f"[统计] 广东2025有效记录: {len(gd_2025):,} 条")

    segment_stats = {}
    for seg in RANK_SEGMENTS:
        seg_records = [
            r for r in gd_2025
            if seg["min"] <= r.get("min_rank", 0) <= seg["max"]
        ]

        if not seg_records:
            segment_stats[seg["name"]] = {
                "description": seg["desc"],
                "total_records": 0,
                "ratios": None
            }
            continue

        total = len(seg_records)
        count_985 = 0
        count_211 = 0
        count_local = 0
        count_outprovince = 0
        university_set = set()
        major_set = set()

        for r in seg_records:
            uni_name = r.get("university_name", "")
            classification = classify_university(
                uni_name,
                r.get("university_level", ""),
                level_map
            )

            if classification["is_985"]:
                count_985 += 1
            if classification["is_211"]:
                count_211 += 1

            if r.get("province") == "广东":
                count_local += 1
            else:
                count_outprovince += 1

            university_set.add(uni_name)
            major_set.add((uni_name, r.get("major_name", "")))

        stats = {
            "description": seg["desc"],
            "total_records": total,
            "unique_universities": len(university_set),
            "unique_majors": len(major_set),
            "ratios": {
                "985_ratio": round(count_985 / total * 100, 2) if total else 0,
                "211_ratio": round(count_211 / total * 100, 2) if total else 0,
                "local_ratio": round(count_local / total * 100, 2) if total else 0,
                "outprovince_ratio": round(count_outprovince / total * 100, 2) if total else 0,
            },
            "counts": {
                "985_count": count_985,
                "211_count": count_211,
                "local_count": count_local,
                "outprovince_count": count_outprovince,
            }
        }
        segment_stats[seg["name"]] = stats

        print(f"  {seg['name']} ({seg['desc']}): {total} 条记录, "
              f"985={stats['ratios']['985_ratio']}%, "
              f"211={stats['ratios']['211_ratio']}%, "
              f"本地={stats['ratios']['local_ratio']}%, "
              f"省外={stats['ratios']['outprovince_ratio']}%")

    return {
        "data_source": "major_rank_data.json (广东2025)",
        "total_eligible": len(gd_2025),
        "segments": segment_stats
    }


# ==================== API推荐分布统计 ====================
def call_recommend_api(rank: int, target_major: str) -> Tuple[bool, Dict, float]:
    """调用推荐接口"""
    request_data = {
        "province": "广东",
        "score": max(300, min(750, 750 - (rank // 1000) * 10)),
        "rank": rank,
        "subject_type": "理科",
        "target_majors": [target_major]
    }

    start = time.time()
    try:
        resp = requests.post(API_ENDPOINT, json=request_data, timeout=API_TIMEOUT)
        elapsed = (time.time() - start) * 1000
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") or data.get("code") == 0:
                # 多种返回格式兼容
                inner = data.get("data", data)
                recs = []
                if inner.get("code") == 0:
                    recs = inner.get("data", {}).get("recommendations", [])
                elif inner.get("success") and isinstance(inner.get("data"), dict):
                    svc_data = inner["data"]
                    for cat in ["冲刺", "稳妥", "保底"]:
                        recs.extend(svc_data.get(cat, []))
                else:
                    recs = inner.get("recommendations", [])
                return True, recs, elapsed
            return False, {"error": data.get("message", "未知错误")}, elapsed
        return False, {"error": f"HTTP {resp.status_code}"}, elapsed
    except Exception as e:
        return False, {"error": str(e)}, (time.time() - start) * 1000


def compute_recommendation_distribution(
        test_samples: List[Dict],
        level_map: Dict[str, str]) -> Dict[str, Any]:
    """调用推荐API并统计推荐结果的分布"""
    print(f"\n[推荐分布] 正在调用API获取推荐结果，共 {len(test_samples)} 条测试...")

    segment_accumulator = {}
    for seg in RANK_SEGMENTS:
        segment_accumulator[seg["name"]] = {
            "description": seg["desc"],
            "sample_count": 0,
            "total_recommendations": 0,
            "count_985": 0,
            "count_211": 0,
            "count_local": 0,
            "count_outprovince": 0,
            "universities_seen": set(),
            "majors_seen": set(),
            "errors": 0,
        }

    # 按位次段分组测试样本
    grouped_samples = defaultdict(list)
    for s in test_samples:
        rank = s.get("min_rank", 0) if isinstance(s, dict) else s.rank if hasattr(s, 'rank') else 0
        for seg in RANK_SEGMENTS:
            if seg["min"] <= rank <= seg["max"]:
                grouped_samples[seg["name"]].append(s)
                break

    # 逐条调用API
    total_samples = len(test_samples)
    progress = tqdm(total=total_samples, desc="推荐分布采样", unit="条")

    for seg_name, samples in sorted(grouped_samples.items()):
        seg = next((s for s in RANK_SEGMENTS if s["name"] == seg_name), None)
        if not seg:
            continue

        acc = segment_accumulator[seg_name]

        for sample in samples:
            rank = sample.get("min_rank", 0) if isinstance(sample, dict) else (
                sample.rank if hasattr(sample, 'rank') else 0)
            major = sample.get("major_name", "") if isinstance(sample, dict) else (
                sample.major_name if hasattr(sample, 'major_name') else "")

            success, recs, _ = call_recommend_api(rank, major)
            progress.update(1)

            if not success:
                acc["errors"] += 1
                continue

            acc["sample_count"] += 1
            acc["total_recommendations"] += len(recs)

            for rec in recs:
                uni_name = rec.get("university_name", "")
                uni_level = rec.get("university_level", "")

                classification = classify_university(uni_name, uni_level, level_map)

                if classification["is_985"]:
                    acc["count_985"] += 1
                if classification["is_211"]:
                    acc["count_211"] += 1

                rec_province = rec.get("province", "")
                if rec_province == "广东":
                    acc["count_local"] += 1
                else:
                    # 尝试从名称推断（部分API返回不含province字段）
                    acc["count_outprovince"] += 1

                acc["universities_seen"].add(uni_name)
                acc["majors_seen"].add((uni_name, rec.get("major_name", "")))

    progress.close()

    # 计算各段比率
    segment_stats = {}
    for seg_name, acc in segment_accumulator.items():
        total = acc["total_recommendations"]
        if total == 0:
            segment_stats[seg_name] = {
                "description": acc["description"],
                "sample_count": acc["sample_count"],
                "total_recommendations": 0,
                "ratios": None,
                "errors": acc["errors"]
            }
            continue

        stats = {
            "description": acc["description"],
            "sample_count": acc["sample_count"],
            "total_recommendations": total,
            "unique_universities": len(acc["universities_seen"]),
            "unique_majors": len(acc["majors_seen"]),
            "ratios": {
                "985_ratio": round(acc["count_985"] / total * 100, 2),
                "211_ratio": round(acc["count_211"] / total * 100, 2),
                "local_ratio": round(acc["count_local"] / total * 100, 2),
                "outprovince_ratio": round(acc["count_outprovince"] / total * 100, 2),
            },
            "counts": {
                "985_count": acc["count_985"],
                "211_count": acc["count_211"],
                "local_count": acc["count_local"],
                "outprovince_count": acc["count_outprovince"],
            },
            "errors": acc["errors"]
        }
        segment_stats[seg_name] = stats

        r = stats["ratios"]
        print(f"  {seg_name}: 推荐{total}条, 985={r['985_ratio']}%, "
              f"211={r['211_ratio']}%, 本地={r['local_ratio']}%, 省外={r['outprovince_ratio']}%")

    return {
        "data_source": "API推荐结果",
        "total_samples": total_samples,
        "segments": segment_stats
    }


# ==================== 抽样 ====================
def stratified_sampling(records: List[Dict], sample_size: int) -> List[Dict]:
    """分层抽样选取测试样本"""
    gd_2025 = [
        r for r in records
        if isinstance(r, dict)
        and r.get("province") == "广东"
        and r.get("year") == 2025
        and r.get("min_rank") and r.get("min_rank") > 0
        and r.get("university_name")
        and r.get("major_name")
    ]

    rank_groups = defaultdict(list)
    for r in gd_2025:
        for seg in RANK_SEGMENTS:
            if seg["min"] <= r["min_rank"] <= seg["max"]:
                rank_groups[seg["name"]].append(r)
                break

    samples = []
    for seg in RANK_SEGMENTS:
        group = rank_groups[seg["name"]]
        target = int(sample_size * seg["ratio"])
        if len(group) <= target:
            selected = group
        else:
            selected = random.sample(group, target)
        samples.extend(selected)

    print(f"[抽样] 从 {len(gd_2025)} 条中抽取 {len(samples)} 条测试样本")
    return samples


# ==================== 偏差分析 ====================
def compute_deviation(actual: Dict, recommendation: Dict) -> Dict[str, Any]:
    """计算实际分布与推荐分布的偏差"""
    print("\n[偏差分析] 正在计算分布偏差...")

    comparison_table = []
    overall_deviation = {"985": [], "211": [], "local": [], "outprovince": []}

    for seg in RANK_SEGMENTS:
        seg_name = seg["name"]
        actual_seg = actual.get("segments", {}).get(seg_name, {})
        rec_seg = recommendation.get("segments", {}).get(seg_name, {})

        actual_ratios = actual_seg.get("ratios") or {}
        rec_ratios = rec_seg.get("ratios") or {}

        if not actual_ratios or not rec_ratios:
            comparison_table.append({
                "rank_segment": seg_name,
                "description": seg["desc"],
                "metrics": {}
            })
            continue

        metrics = {}
        for metric in ["985_ratio", "211_ratio", "local_ratio", "outprovince_ratio"]:
            actual_val = actual_ratios.get(metric, 0)
            rec_val = rec_ratios.get(metric, 0)
            deviation = round(rec_val - actual_val, 2)

            if abs(deviation) <= 5:
                grade = "正常"
                icon = "✅"
            elif abs(deviation) <= 10:
                grade = "轻微偏差"
                icon = "⚠️"
            elif abs(deviation) <= 20:
                grade = "明显偏差"
                icon = "🔶"
            else:
                grade = "严重偏差"
                icon = "❌"

            label_map = {
                "985_ratio": "985占比",
                "211_ratio": "211占比",
                "local_ratio": "本地院校占比",
                "outprovince_ratio": "省外院校占比",
            }

            metrics[metric] = {
                "label": label_map.get(metric, metric),
                "actual": actual_val,
                "recommended": rec_val,
                "deviation": deviation,
                "grade": grade,
                "icon": icon,
            }

            short_key = metric.replace("_ratio", "")
            overall_deviation[short_key].append(deviation)

        comparison_table.append({
            "rank_segment": seg_name,
            "description": seg["desc"],
            "actual_records": actual_seg.get("total_records", 0),
            "recommendation_records": rec_seg.get("total_recommendations", 0),
            "metrics": metrics,
        })

        # 打印对比结果
        seg_desc = seg["desc"]
        print(f"\n  【{seg_name} - {seg_desc}】")
        for key, m in metrics.items():
            print(f"    {m['label']}: 实际{m['actual']}% | 推荐{m['recommended']}% "
                  f"| 偏差{m['deviation']:+}% | {m['icon']} {m['grade']}")

    # 总体偏差
    avg_deviation = {}
    for key, vals in overall_deviation.items():
        if vals:
            avg_deviation[key] = round(sum(vals) / len(vals), 2)

    # 总体评估
    if avg_deviation:
        max_abs_dev = max(abs(v) for v in avg_deviation.values())
        if max_abs_dev <= 5:
            overall_grade = "优秀 - 推荐分布与实际录取高度一致"
        elif max_abs_dev <= 10:
            overall_grade = "良好 - 推荐分布有轻微偏差"
        elif max_abs_dev <= 15:
            overall_grade = "一般 - 推荐分布存在明显偏差，需要调整"
        else:
            overall_grade = "较差 - 推荐分布与实际录取偏差较大，需要修复"
    else:
        overall_grade = "无法评估"

    print(f"\n  总体平均偏差: {avg_deviation}")
    print(f"  总体评估: {overall_grade}")

    return {
        "comparison_table": comparison_table,
        "average_deviation": avg_deviation,
        "overall_assessment": overall_grade,
    }


# ==================== 主流程 ====================
def main():
    parser = argparse.ArgumentParser(description="录取分布对比分析")
    parser.add_argument("--quick", action="store_true", help="快速测试（50条样本）")
    parser.add_argument("--sample", type=int, default=200, help="样本量（默认200）")
    args = parser.parse_args()

    sample_size = 50 if args.quick else args.sample
    start_time = time.time()

    # 1. 加载数据
    print("=" * 60)
    print("实际录取分布 vs 算法推荐分布 对比分析")
    print("=" * 60)

    with open(MAJOR_RANK_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    records = data.get("major_rank_data", [])
    print(f"\n[数据] 加载了 {len(records):,} 条记录")

    # 2. 建立院校层级映射
    level_map = build_university_level_map()

    # 3. 计算实际录取分布
    actual_dist = compute_actual_distribution(records, level_map)

    # 4. 抽样
    samples = stratified_sampling(records, sample_size)

    # 5. 调用API获取推荐分布
    rec_dist = compute_recommendation_distribution(samples, level_map)

    # 6. 偏差分析
    deviation = compute_deviation(actual_dist, rec_dist)

    # 7. 生成报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "title": "算法推荐分布 vs 实际录取分布 对比报告",
        "generated_at": datetime.now().isoformat(),
        "sample_size": sample_size,
        "actual_distribution": actual_dist,
        "recommendation_distribution": rec_dist,
        "deviation_analysis": deviation,
        "summary": {
            "overall_grade": deviation["overall_assessment"],
            "average_deviation": deviation["average_deviation"],
            "analysis_time_seconds": round(time.time() - start_time, 2),
        }
    }

    # 保存报告
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = RESULTS_DIR / f"distribution_comparison_report_{timestamp}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n[报告] 已保存到: {report_path}")

    # 同时保存一份到 backend/data 目录供查看
    data_report_path = DATA_DIR / "distribution_comparison_report.json"
    with open(data_report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"[报告] 已保存到: {data_report_path}")

    # 8. 输出总体结论
    print("\n" + "=" * 60)
    print("对比分析完成")
    print("=" * 60)
    print(f"样本量: {sample_size}")
    print(f"总体评估: {deviation['overall_assessment']}")
    print(f"耗时: {round(time.time() - start_time, 2)} 秒")
    print("=" * 60)


if __name__ == "__main__":
    main()
