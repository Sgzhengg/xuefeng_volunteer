# -*- coding: utf-8 -*-
"""
A/B 测试框架 - 对比 V1 (规则驱动) vs V2 (数据驱动) 推荐算法

用法:
    python tests/ab_test.py                     # 完整测试 (500样本)
    python tests/ab_test.py --quick             # 快速测试 (100样本)
    python tests/ab_test.py --sample 1000       # 自定义样本量
    python tests/ab_test.py --detail            # 详细输出

指标:
    - 院校命中率: 推荐列表中包含实际录取院校的比例
    - 专业大类命中率: 推荐专业大类与实际专业大类匹配的比例
    - 扩展后命中率: 扩展搜索范围后的命中率
    - 多样性: 独立院校数 / 总推荐数
    - 同校上限: 单校最多推荐专业数
    - 覆盖率: 测试样本中多少位次段有推荐
"""

import json, sys, io, os, random, time, argparse, math
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict, Counter
from datetime import datetime
import importlib.util

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 后端路径
BACKEND_DIR = Path(__file__).parent.parent
DATA_DIR = BACKEND_DIR / 'data'

# ============================================================
# 位次段与样本配置
# ============================================================
RANK_SEGMENTS = [
    {'name': 'elite', 'range': (1, 3000), 'ratio': 0.08, 'label': u'精英 1-3000'},
    {'name': 'high', 'range': (3001, 10000), 'ratio': 0.12, 'label': u'高分 3001-10000'},
    {'name': 'upper_mid', 'range': (10001, 30000), 'ratio': 0.18, 'label': u'中上 10001-30000'},
    {'name': 'mid', 'range': (30001, 80000), 'ratio': 0.22, 'label': u'中等 30001-80000'},
    {'name': 'lower_mid', 'range': (80001, 150000), 'ratio': 0.22, 'label': u'中下 80001-150000'},
    {'name': 'low', 'range': (150001, 350000), 'ratio': 0.18, 'label': u'低位 150001-350000'},
]

# 专业大类关键词（用于大类命中率计算）
MAJOR_CATEGORIES = {
    '计算机类': ['计算机', '软件', '人工智能', '数据', '网络', '信息安全', '物联网', '大数据', '智能', '数字媒体'],
    '电子信息类': ['电子', '通信', '信息', '微电子', '光电', '集成电路', '电气', '自动化', '测控', '仪器'],
    '医学类': ['临床', '医学', '药学', '护理', '口腔', '中医', '基础医学', '预防', '麻醉', '影像', '检验', '康复', '中药', '制药', '公共卫生', '法医'],
    '财经类': ['经济', '金融', '会计', '财务', '工商管理', '市场', '国际商务', '保险', '税收', '财政', '国贸', '贸易', '审计'],
    '法学类': ['法学', '法律', '知识产权', '政治', '社会', '公安', '侦查', '行政'],
    '机械材料类': ['机械', '车辆', '材料', '力学', '航空航天', '能源', '动力'],
    '土木建筑类': ['土木', '建筑', '城乡规划', '风景园林', '给排水', '道路', '桥梁', '工程管理', '造价', '水利', '测绘'],
    '文学传媒类': ['英语', '日语', '法语', '德语', '翻译', '汉语', '新闻', '广告', '编辑', '出版', '传播', '汉语言', '秘书', '商务英语'],
    '理学类': ['数学', '物理', '化学', '生物', '地理', '统计', '大气', '海洋', '地质', '天文', '心理'],
    '师范教育类': ['教育', '师范', '学前', '体育', '特殊教育', '小学教育'],
    '艺术类': ['美术', '音乐', '舞蹈', '设计', '动画', '表演', '书法', '播音', '编导', '摄影', '戏剧', '影视'],
}


def classify_major(major_name: str) -> str:
    """将专业名分类到大类"""
    if not major_name:
        return '其他'
    for cat, keywords in MAJOR_CATEGORIES.items():
        for kw in keywords:
            if kw in major_name:
                return cat
    return '其他'


# ============================================================
# 测试样本生成
# ============================================================
def load_test_samples(total_samples: int = 500, random_seed: int = 42) -> List[Dict]:
    """从 2025 年数据中分层抽样生成测试样本"""
    main_file = DATA_DIR / 'major_rank_data.json'
    with open(main_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    records = data.get('major_rank_data', [])

    # 只取 2025 年广东数据
    year2025 = [r for r in records
                if isinstance(r, dict) and r.get('year') == 2025
                and r.get('min_rank', 0) > 0]

    print(f'[AB] 2025 records: {len(year2025)}')

    # 按段分组
    rng = random.Random(random_seed)
    samples = []

    for seg in RANK_SEGMENTS:
        rmin, rmax = seg['range']
        pool = [r for r in year2025 if rmin <= r.get('min_rank', 0) <= rmax]
        n = max(1, int(total_samples * seg['ratio']))
        if len(pool) > n:
            chosen = rng.sample(pool, n)
        else:
            chosen = pool
        for r in chosen:
            samples.append({
                'rank': r['min_rank'],
                'university_name': r.get('university_name', ''),
                'major_name': r.get('major_name', ''),
                'group_code': str(r.get('group_code', '')),
                'university_province': r.get('university_province', ''),
                'university_level': r.get('university_level', ''),
                'subject_type': r.get('subject_type', '理科'),
                'segment': seg['name'],
            })

    print(f'[AB] Generated {len(samples)} test samples')
    for seg in RANK_SEGMENTS:
        cnt = sum(1 for s in samples if s['segment'] == seg['name'])
        print(f'  {seg["label"]}: {cnt}')

    return samples


# ============================================================
# V1 服务包装（直接调用，无需 HTTP）
# ============================================================
def load_v1_service():
    """加载 V1 推荐服务"""
    # 使用 importlib 避免 __init__.py 的依赖链
    v1_path = BACKEND_DIR / 'app' / 'services' / 'guangdong_recommendation_service.py'
    spec = importlib.util.spec_from_file_location('v1_service', str(v1_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.GuangdongRecommendationService()


# ============================================================
# V2 服务包装
# ============================================================
def load_v2_service():
    """加载 V2 推荐服务"""
    v2_path = BACKEND_DIR / 'app' / 'services' / 'recommendation_service_v2.py'
    spec = importlib.util.spec_from_file_location('v2_service', str(v2_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    svc = mod.RecommendationServiceV2(data_dir=DATA_DIR)
    return svc


# ============================================================
# 指标计算
# ============================================================
def compute_metrics(service_name: str, results: List[Tuple[Dict, Dict]],
                    samples: List[Dict]) -> Dict[str, Any]:
    """
    计算所有指标

    Returns:
        {overall_metrics, segment_metrics, details}
    """
    total = len(results)
    if total == 0:
        return {}

    # 全局计数器
    uni_hits = 0
    major_cat_hits = 0  # 大类命中
    anyone_hits = 0     # 只要有任一推荐命中实际院校
    anyone_major_hits = 0
    total_diversity = 0
    per_uni_max_counts = []
    segment_stats = defaultdict(lambda: {
        'count': 0, 'uni_hit': 0, 'major_cat_hit': 0,
        'any_hit': 0, 'any_major_hit': 0, 'diversity': 0,
        'per_uni_maxs': [], 'avg_rec_count': 0
    })

    all_details = []

    for (result, sample), orig_sample in zip(results, samples):
        rec_data = result.get('data', {})
        chongci = rec_data.get('\u51b2\u523a', [])
        wenzuo = rec_data.get('\u7a33\u59a5', [])
        baodi = rec_data.get('\u4fdd\u5e95', [])

        all_recs = chongci + wenzuo + baodi
        n_recs = len(all_recs)
        if n_recs == 0:
            continue

        actual_uni = sample.get('university_name', '')
        actual_major = sample.get('major_name', '')
        actual_group = sample.get('group_code', '')
        actual_cat = classify_major(actual_major)
        seg = sample.get('segment', '')

        # 院校命中
        rec_unis = set(r.get('university_name', '') for r in all_recs)
        uni_hit = actual_uni in rec_unis
        if uni_hit:
            uni_hits += 1

        # 无论是否命中实际院校，只要有任一推荐就算"any hit"
        if len(rec_unis) > 0:
            anyone_hits += 1

        # 大类命中
        major_cat_hit = False
        for r in all_recs:
            rec_major_name = str(r.get('major_name', ''))
            rec_cat = classify_major(rec_major_name)
            if rec_cat != '其他' and actual_cat != '其他' and rec_cat == actual_cat:
                major_cat_hit = True
                break
            # 关键词重叠（放宽匹配）
            if rec_cat != '其他' and actual_cat == '其他':
                # 检查关键词重叠
                for kw in MAJOR_CATEGORIES.get(rec_cat, []):
                    if kw in actual_major:
                        major_cat_hit = True
                        break
            if major_cat_hit:
                break
        if major_cat_hit:
            major_cat_hits += 1

        # 任意大类命中（至少有一个推荐）
        if n_recs > 0:
            anyone_major_hits += 1

        # 多样性：独立院校数 / 总推荐数
        div = len(rec_unis) / n_recs
        total_diversity += div

        # 同校上限：检查任一类中最大同校推荐数
        per_uni_max = 0
        for cat_list in [chongci, wenzuo, baodi]:
            uni_cnt = Counter(r.get('university_name', '') for r in cat_list)
            if uni_cnt:
                cat_max = max(uni_cnt.values())
                per_uni_max = max(per_uni_max, cat_max)
        per_uni_max_counts.append(per_uni_max)

        # 按段统计
        if seg:
            ss = segment_stats[seg]
            ss['count'] += 1
            ss['uni_hit'] += 1 if uni_hit else 0
            ss['major_cat_hit'] += 1 if major_cat_hit else 0
            ss['any_hit'] += 1 if len(rec_unis) > 0 else 0
            ss['any_major_hit'] += 1 if n_recs > 0 else 0
            ss['diversity'] += div
            ss['per_uni_maxs'].append(per_uni_max)
            ss['avg_rec_count'] += n_recs

        all_details.append({
            'rank': sample['rank'],
            'segment': seg,
            'actual_uni': actual_uni,
            'actual_major': actual_major,
            'uni_hit': uni_hit,
            'major_cat_hit': major_cat_hit,
            'n_recs': n_recs,
            'diversity': round(div, 3),
            'per_uni_max': per_uni_max,
        })

    # 汇总
    seg_data = {}
    all_seg_diversities = 0
    all_seg_counts = 0
    all_seg_max_per_uni = []
    all_seg_uni_hit = 0
    all_seg_major_hit = 0

    for seg_name, ss in segment_stats.items():
        cnt = ss['count']
        if cnt > 0:
            all_seg_diversities += ss['diversity']
            all_seg_counts += cnt
            all_seg_max_per_uni.extend(ss['per_uni_maxs'])
            all_seg_uni_hit += ss['uni_hit']
            all_seg_major_hit += ss['major_cat_hit']

            seg_data[seg_name] = {
                'count': cnt,
                'uni_hit_rate': round(ss['uni_hit'] / cnt * 100, 1),
                'major_cat_hit_rate': round(ss['major_cat_hit'] / cnt * 100, 1),
                'diversity': round(ss['diversity'] / cnt, 3),
                'avg_per_uni_max': round(sum(ss['per_uni_maxs']) / len(ss['per_uni_maxs']), 2) if ss['per_uni_maxs'] else 0,
                'avg_rec_count': round(ss['avg_rec_count'] / cnt, 1),
            }

    return {
        'service': service_name,
        'total_samples': total,
        'uni_hit_rate': round(uni_hits / total * 100, 1),
        'major_cat_hit_rate': round(major_cat_hits / total * 100, 1),
        'diversity': round(total_diversity / total, 3),
        'avg_per_uni_max': round(sum(per_uni_max_counts) / len(per_uni_max_counts), 2) if per_uni_max_counts else 0,
        'per_uni_violations': sum(1 for x in per_uni_max_counts if x > 3),
        'per_uni_violation_rate': round(sum(1 for x in per_uni_max_counts if x > 3) / total * 100, 1) if total > 0 else 0,
        'segments': seg_data,
        'details': all_details,
    }


# ============================================================
# A/B 测试核心
# ============================================================
def run_single_service(service, samples: List[Dict], name: str, detail: bool = False) -> List[Tuple[Dict, Dict]]:
    """对单个服务运行所有测试样本"""
    results = []
    error_count = 0
    n = len(samples)

    for i, sample in enumerate(samples):
        if detail and i % 50 == 0:
            print(f'  [{name}] {i}/{n}...')

        try:
            result = service.recommend_with_fallback(
                user_rank=sample['rank'],
                province='广东',
                subject_type=sample.get('subject_type', '理科'),
                target_majors=None
            )
            results.append((result, sample))
        except Exception as e:
            error_count += 1
            if detail:
                print(f'  [{name}] Error at rank {sample["rank"]}: {e}')

    if error_count:
        print(f'  [{name}] {error_count} errors / {n} samples')
    return results


def compare(metrics_v1: Dict, metrics_v2: Dict) -> Dict:
    """对比 V1 vs V2"""
    comparison = {}
    for key in ['uni_hit_rate', 'major_cat_hit_rate', 'diversity',
                'avg_per_uni_max', 'per_uni_violation_rate']:
        v1_val = metrics_v1.get(key, 0)
        v2_val = metrics_v2.get(key, 0)
        delta = v2_val - v1_val
        comparison[key] = {
            'v1': v1_val,
            'v2': v2_val,
            'delta': round(delta, 2),
            'better': 'V2' if delta > 0 else ('V1' if delta < 0 else 'TIE')
        }

    # 同校上限是越低越好
    for key in ['avg_per_uni_max', 'per_uni_violation_rate']:
        c = comparison.get(key, {})
        if c:
            d = c['delta']
            c['better'] = 'V2' if d < 0 else ('V1' if d > 0 else 'TIE')

    # 综合判断
    v2_wins = sum(1 for v in comparison.values() if v['better'] == 'V2')
    v1_wins = sum(1 for v in comparison.values() if v['better'] == 'V1')
    comparison['summary'] = {
        'v2_wins': v2_wins,
        'v1_wins': v1_wins,
        'ties': len(comparison) - v2_wins - v1_wins,
        'verdict': 'V2 胜出' if v2_wins >= v1_wins else 'V1 胜出' if v1_wins > v2_wins else '平局'
    }

    return comparison


# ============================================================
# HTML 报告生成
# ============================================================
def generate_html_report(metrics_v1: Dict, metrics_v2: Dict, comparison: Dict,
                         samples: List[Dict], output_path: Path, sample_count: int):
    """生成 HTML 对比报告"""

    def cell(v, cls=''):
        return f'<td class="{cls}">{v}</td>'

    def delta_viz(d):
        if d > 0:
            return f'<span class="positive">+{d}</span>'
        elif d < 0:
            return f'<span class="negative">{d}</span>'
        return f'<span class="neutral">{d}</span>'

    def better_badge(better):
        colors = {'V2': 'v2-badge', 'V1': 'v1-badge', 'TIE': 'tie-badge'}
        return f'<span class="badge {colors.get(better, "")}">{better}</span>'

    # 指标对比表
    metrics_rows = ''
    metric_labels = {
        'uni_hit_rate': '院校命中率 (%)',
        'major_cat_hit_rate': '专业大类命中率 (%)',
        'diversity': '推荐多样性',
        'avg_per_uni_max': '同校平均最多专业数',
        'per_uni_violation_rate': '同校超限率 (%)',
    }
    targets = {
        'uni_hit_rate': (65, u'\u2265 65'),
        'major_cat_hit_rate': (80, u'\u2265 80'),
        'per_uni_violation_rate': (0, u'= 0'),
        'diversity': (0.6, u'\u2265 0.6'),
    }

    for key, label in metric_labels.items():
        comp = comparison.get(key, {})
        v1 = comp.get('v1', 0)
        v2 = comp.get('v2', 0)
        d = comp.get('delta', 0)
        better = comp.get('better', 'TIE')
        target = targets.get(key)
        target_str = ''
        target_met = False
        if target:
            threshold, label_str = target
            target_str = f' (目标: {label_str})'
            if key == 'per_uni_violation_rate':
                target_met = v2 <= threshold
            else:
                target_met = v2 >= threshold

        v2_cls = 'target-met' if target_met else 'target-not-met'
        metrics_rows += f'''<tr>
            <td>{label}{target_str}</td>
            {cell(v1)}
            {cell(v2, v2_cls)}
            <td>{delta_viz(d)}</td>
            {cell(better_badge(better))}
        </tr>'''

    # 分段明细表
    seg_keys = sorted(metrics_v1.get('segments', {}).keys(),
                      key=lambda k: {'elite': 0, 'high': 1, 'upper_mid': 2,
                                     'mid': 3, 'lower_mid': 4, 'low': 5}.get(k, 99))
    seg_rows = ''
    for seg in seg_keys:
        sv1 = metrics_v1['segments'].get(seg, {})
        sv2 = metrics_v2['segments'].get(seg, {})
        label = next((s['label'] for s in RANK_SEGMENTS if s['name'] == seg), seg)

        v1_uni = sv1.get('uni_hit_rate', 0)
        v2_uni = sv2.get('uni_hit_rate', 0)
        v1_ma = sv1.get('major_cat_hit_rate', 0)
        v2_ma = sv2.get('major_cat_hit_rate', 0)
        v1_div = sv1.get('diversity', 0)
        v2_div = sv2.get('diversity', 0)

        seg_rows += f'''<tr>
            <td>{label}</td>
            <td>{sv1.get('count', 0)}</td>
            <td>{v1_uni}% / <b>{v2_uni}%</b></td>
            <td>{v1_ma}% / <b>{v2_ma}%</b></td>
            <td>{v1_div:.3f} / <b>{v2_div:.3f}</b></td>
        </tr>'''

    # 汇总
    verdict = comparison.get('summary', {}).get('verdict', 'N/A')
    v2_wins = comparison.get('summary', {}).get('v2_wins', 0)
    v1_wins = comparison.get('summary', {}).get('v1_wins', 0)
    ties = comparison.get('summary', {}).get('ties', 0)

    # 达标检查
    checks = ''
    targets_check = {
        'major_cat_hit_rate': ('专业大类命中率 >= 80%', 80),
        'per_uni_violation_rate': ('同校最多专业数 <= 3 (超限率 = 0)', 0),
    }
    for key, (desc, threshold) in targets_check.items():
        val = metrics_v2.get(key, 0)
        ok = val <= threshold if 'violation' in key else val >= threshold
        icon = 'PASS' if ok else 'FAIL'
        cls = 'pass' if ok else 'fail'
        checks += f'<tr><td class="{cls}">{icon}</td><td>{desc}</td><td>{val}</td></tr>'

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>A/B 测试报告 - 推荐算法 V1 vs V2</title>
<style>
body {{ font-family: "Microsoft YaHei", sans-serif; margin: 40px; color: #333; background: #f5f5f5; }}
.container {{ max-width: 1100px; margin: 0 auto; }}
h1 {{ color: #1a237e; border-bottom: 3px solid #1a237e; padding-bottom: 10px; }}
h2 {{ color: #283593; margin-top: 30px; }}
table {{ width: 100%; border-collapse: collapse; margin: 15px 0; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
th {{ background: #1a237e; color: white; padding: 10px 12px; text-align: left; }}
td {{ padding: 8px 12px; border-bottom: 1px solid #e0e0e0; }}
tr:hover {{ background: #f5f5f5; }}
.positive {{ color: #2e7d32; font-weight: bold; }}
.negative {{ color: #c62828; font-weight: bold; }}
.neutral {{ color: #757575; }}
.badge {{ padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
.v2-badge {{ background: #c8e6c9; color: #2e7d32; }}
.v1-badge {{ background: #ffcdd2; color: #c62828; }}
.tie-badge {{ background: #e0e0e0; color: #616161; }}
.target-met {{ background: #e8f5e9; }}
.target-not-met {{ background: #fff3e0; }}
.pass {{ color: #2e7d32; font-weight: bold; }}
.fail {{ color: #c62828; font-weight: bold; }}
.summary-box {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 20px 0; }}
.summary-box h3 {{ margin-top: 0; }}
.meta {{ color: #757575; font-size: 14px; }}
.verdict {{ font-size: 24px; font-weight: bold; text-align: center; padding: 20px; }}
</style>
</head>
<body>
<div class="container">
<h1>A/B 测试报告</h1>
<p class="meta">V1 (规则驱动) vs V2 (数据驱动) | 测试样本: {sample_count} | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<div class="summary-box">
<h3>综合判定</h3>
<div class="verdict" style="color: {'#2e7d32' if v2_wins >= v1_wins else '#c62828'}">{verdict}</div>
<p style="text-align:center">V2 胜出 {v2_wins} 项 | V1 胜出 {v1_wins} 项 | 平局 {ties} 项</p>
</div>

<h2>验收标准检查</h2>
<table>
<tr><th>标准</th><th>描述</th><th>当前值</th></tr>
{checks}
</table>

<h2>汇总指标对比</h2>
<table>
<tr><th>指标</th><th>V1</th><th>V2</th><th>Delta</th><th>胜出</th></tr>
{metrics_rows}
</table>

<h2>分段明细</h2>
<table>
<tr><th>位次段</th><th>样本数</th><th>院校命中率 V1/V2</th><th>大类命中率 V1/V2</th><th>多样性 V1/V2</th></tr>
{seg_rows}
</table>

<h2>未命中 Top 分析 (V2)</h2>
<table>
<tr><th>排名</th><th>位次段</th><th>实际院校</th><th>实际专业</th><th>推荐数</th></tr>
{generate_miss_rows(metrics_v2)}
</table>

</div>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'\n[AB] Report saved: {output_path}')


def generate_miss_rows(metrics: Dict) -> str:
    """生成未命中 top 行"""
    details = metrics.get('details', [])
    misses = [d for d in details if not d.get('uni_hit')]
    rows = ''
    for i, m in enumerate(misses[:20]):
        rows += f'''<tr>
            <td>{i + 1}</td>
            <td>{m.get('segment', '')}</td>
            <td>{m.get('actual_uni', '')}</td>
            <td>{m.get('actual_major', '')}</td>
            <td>{m.get('n_recs', 0)}</td>
        </tr>'''
    return rows


# ============================================================
# 主函数
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='A/B Test: Recommendation Algorithm V1 vs V2')
    parser.add_argument('--quick', action='store_true', help='Quick test with 100 samples')
    parser.add_argument('--sample', type=int, default=500, help='Number of test samples (default 500)')
    parser.add_argument('--detail', action='store_true', help='Detailed per-sample output')
    parser.add_argument('--v1-only', action='store_true', help='Test V1 only')
    parser.add_argument('--v2-only', action='store_true', help='Test V2 only')
    parser.add_argument('--output', type=str, default=None, help='Report output path')
    args = parser.parse_args()

    if args.quick:
        args.sample = 100

    print('=' * 60)
    print('A/B Test: Recommendation Algorithm V1 vs V2')
    print(f'Samples: {args.sample}')
    print('=' * 60)

    # 1. 生成测试样本
    print('\n[1] Generating test samples...')
    samples = load_test_samples(args.sample)
    if not samples:
        print('[ERROR] No test samples generated!')
        return

    # 2. 加载服务
    do_v1 = not args.v2_only
    do_v2 = not args.v1_only

    metrics_v1 = {}
    metrics_v2 = {}

    if do_v1:
        print('\n[2a] Loading V1 service...')
        svc1 = load_v1_service()
        print('[2a] Running V1 tests...')
        results_v1 = run_single_service(svc1, samples, 'V1', args.detail)
        metrics_v1 = compute_metrics('V1 (规则驱动)', results_v1, samples)
        print_v1_metrics(metrics_v1)

    if do_v2:
        print('\n[2b] Loading V2 service...')
        svc2 = load_v2_service()
        print('[2b] Running V2 tests...')
        results_v2 = run_single_service(svc2, samples, 'V2', args.detail)
        metrics_v2 = compute_metrics('V2 (数据驱动)', results_v2, samples)
        print_v2_metrics(metrics_v2)

    # 3. 对比
    if do_v1 and do_v2:
        print('\n[3] Comparing V1 vs V2...')
        comparison = compare(metrics_v1, metrics_v2)

        print(f'\n{"=" * 60}')
        print('Comparison Summary')
        print(f'{"=" * 60}')
        for key, comp in comparison.items():
            if key == 'summary':
                continue
            display_keys = {
                'uni_hit_rate': '院校命中率',
                'major_cat_hit_rate': '专业大类命中率',
                'diversity': '推荐多样性',
                'avg_per_uni_max': '同校平均最多专业数',
                'per_uni_violation_rate': '同校超限率',
            }
            label = display_keys.get(key, key)
            print(f'  {label}: V1={comp["v1"]}, V2={comp["v2"]}, Delta={comp["delta"]}, Better={comp["better"]}')

        summary = comparison.get('summary', {})
        print(f'\n  Verdict: {summary.get("verdict", "N/A")}')
        print(f'  V2 wins: {summary.get("v2_wins", 0)}, V1 wins: {summary.get("v1_wins", 0)}, Ties: {summary.get("ties", 0)}')

        # 4. 生成 HTML 报告
        output_path = Path(args.output) if args.output else (BACKEND_DIR / 'tests' / 'ab_test_report.html')
        generate_html_report(metrics_v1, metrics_v2, comparison, samples, output_path, len(samples))
    elif do_v1:
        print('\n[V1 Only] Skipping comparison.')
        output_path = Path(args.output) if args.output else (BACKEND_DIR / 'tests' / 'ab_test_report_v1.html')
        # Single service report
        generate_single_report(metrics_v1, samples, output_path, len(samples))
    elif do_v2:
        print('\n[V2 Only] Skipping comparison.')
        output_path = Path(args.output) if args.output else (BACKEND_DIR / 'tests' / 'ab_test_report_v2.html')
        generate_single_report(metrics_v2, samples, output_path, len(samples))


def print_v1_metrics(m: Dict):
    print(f'  Uni Hit Rate: {m.get("uni_hit_rate", 0)}%')
    print(f'  Major Cat Hit Rate: {m.get("major_cat_hit_rate", 0)}%')
    print(f'  Diversity: {m.get("diversity", 0)}')
    print(f'  Avg Per-Uni Max: {m.get("avg_per_uni_max", 0)}')
    print(f'  Per-Uni Violations: {m.get("per_uni_violations", 0)} ({m.get("per_uni_violation_rate", 0)}%)')


def print_v2_metrics(m: Dict):
    print(f'  Uni Hit Rate: {m.get("uni_hit_rate", 0)}%')
    print(f'  Major Cat Hit Rate: {m.get("major_cat_hit_rate", 0)}%')
    print(f'  Diversity: {m.get("diversity", 0)}')
    print(f'  Avg Per-Uni Max: {m.get("avg_per_uni_max", 0)}')
    print(f'  Per-Uni Violations: {m.get("per_uni_violations", 0)} ({m.get("per_uni_violation_rate", 0)}%)')


def generate_single_report(metrics: Dict, samples: List[Dict], output_path: Path, sample_count: int):
    """生成单个服务的报告"""
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>A/B Test Report - Single Service</title>
<style>
body {{ font-family: "Microsoft YaHei", sans-serif; margin: 40px; background: #f5f5f5; }}
.container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
h1 {{ color: #1a237e; }} table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
th {{ background: #1a237e; color: white; padding: 10px; text-align: left; }}
td {{ padding: 8px 10px; border-bottom: 1px solid #e0e0e0; }}
</style></head>
<body><div class="container">
<h1>{metrics.get("service", "Test")} - Test Report</h1>
<p>Samples: {sample_count} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Uni Hit Rate</td><td>{metrics.get("uni_hit_rate", 0)}%</td></tr>
<tr><td>Major Cat Hit Rate</td><td>{metrics.get("major_cat_hit_rate", 0)}%</td></tr>
<tr><td>Diversity</td><td>{metrics.get("diversity", 0)}</td></tr>
<tr><td>Avg Per-Uni Max</td><td>{metrics.get("avg_per_uni_max", 0)}</td></tr>
<tr><td>Per-Uni Violation Rate</td><td>{metrics.get("per_uni_violation_rate", 0)}%</td></tr>
</table>
</div></body></html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'\n[AB] Report saved: {output_path}')


if __name__ == '__main__':
    main()
