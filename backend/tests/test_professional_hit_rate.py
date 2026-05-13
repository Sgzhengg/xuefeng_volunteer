# -*- coding: utf-8 -*-
"""
专业命中率测试
验证推荐结果中是否包含目标专业，三类命中判定：
  - 精确命中 (exact_hit)：推荐的 major_name 或 group_code 映射中包含目标专业名称
  - 宽松命中 (lenient_hit)：推荐的专业/专业组与目标专业属于同一大类
  - 院校命中 (uni_hit)：推荐的院校历史上录取了目标专业

用法:
    python test_professional_hit_rate.py
    python test_professional_hit_rate.py --quick     # 快速模式
    python test_professional_hit_rate.py --v2-only   # 仅测试V2
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple, Set

_PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

# ---------------------------------------------------------------------------
# 专业大类映射 (来自 recommendation_service_v2.py - MAJOR_CATEGORIES)
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# 测试用例 - 8 个，覆盖不同位次段
# ---------------------------------------------------------------------------
TEST_CASES: List[Dict[str, Any]] = [
    {"rank": 5000, "expected_major": "计算机科学与技术"},
    {"rank": 10000, "expected_major": "临床医学"},
    {"rank": 20000, "expected_major": "软件工程"},
    {"rank": 35000, "expected_major": "自动化"},
    {"rank": 50000, "expected_major": "会计学"},
    {"rank": 70000, "expected_major": "土木工程"},
    {"rank": 100000, "expected_major": "护理学"},
    {"rank": 150000, "expected_major": "电子商务"},
]


def _classify_major(major_name: str) -> str:
    """从专业名推断大类"""
    if not major_name:
        return '其他'
    mn = str(major_name)
    for cat, keywords in MAJOR_CATEGORIES.items():
        for kw in keywords:
            if kw in mn:
                return cat
    return '其他'


# =====================================================================
# ProfessionalHitRateTest
# =====================================================================

class ProfessionalHitRateTest:
    """专业命中率测试"""

    def __init__(self, quick: bool = False):
        self.data_dir = _PROJECT_ROOT / 'data'
        self.quick = quick
        self.records: List[Dict] = []
        self.group_major_map: Dict[Tuple[str, str], List[str]] = {}
        self.major_to_groups: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
        self.group_records: Dict[Tuple[str, str], List[Dict]] = defaultdict(list)
        self._load_all()

    def _load_all(self) -> None:
        t0 = datetime.now()
        self._load_main_data()
        self._load_group_mapping()
        self._build_reverse_index()
        self._build_group_records()
        elapsed = (datetime.now() - t0).total_seconds()
        print(f"[Init] 加载完成, 耗时 {elapsed:.1f}s, "
              f"记录数={len(self.records)}, "
              f"映射组数={len(self.group_major_map)}, "
              f"反向索引专业数={len(self.major_to_groups)}")

    def _load_main_data(self) -> None:
        main_file = self.data_dir / 'major_rank_data.json'
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            records = data.get('major_rank_data', [])
            if self.quick and len(records) > 5000:
                records = records[:5000]
                print(f"[Data] 快速模式: 使用前 5000 条记录")
            self.records = records
            print(f"[Data] 加载 {len(self.records)} 条录取记录")

    def _load_group_mapping(self) -> None:
        # 优先使用 group_code_mapping.json，回退到 major_group_mapping.json
        for fname in ['group_code_mapping.json', 'major_group_mapping.json']:
            mf = self.data_dir / fname
            if not mf.exists():
                continue
            with open(mf, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'mappings' in data:
                data = data['mappings']
            for key, info in data.items():
                if isinstance(key, str) and '_' in key:
                    parts = key.rsplit('_', 1)
                    if len(parts) == 2:
                        uni, code = parts[0], parts[1].replace('\n', '').strip()
                        majors = info.get('majors', []) if isinstance(info, dict) else []
                        if uni and code and majors:
                            self.group_major_map[(uni, code)] = majors
            print(f"[Data] 加载 {len(self.group_major_map)} 条专业组映射 (from {fname})")
            return
        print(f"[Data] WARNING: 未找到专业组映射文件")

    def _build_reverse_index(self) -> None:
        for (uni, code), majors in self.group_major_map.items():
            for major in majors:
                self.major_to_groups[major].append((uni, code))

    def _build_group_records(self) -> None:
        for rec in self.records:
            if not isinstance(rec, dict):
                continue
            uni = rec.get('university_name', '')
            code = str(rec.get('group_code', '') or '').replace('\n', '').strip()
            if uni and code:
                self.group_records[(uni, code)].append(rec)

    def _get_expected_unis(self, target_major: str, rank_min: int, rank_max: int) -> Set[str]:
        """获取指定位次范围内录取了目标专业的所有院校"""
        expected = set()
        target_groups = self.major_to_groups.get(target_major, [])
        if target_groups:
            for uni, code in target_groups:
                recs = self.group_records.get((uni, code), [])
                for rec in recs:
                    rk = rec.get('min_rank', 0)
                    if rk and rank_min <= rk <= rank_max:
                        expected.add(uni)
                        break
        else:
            keywords = [target_major]
            for kw in ['计算机', '软件', '临床', '医学', '自动化', '会计', '土木', '护理', '电子商务']:
                if kw in target_major and kw not in keywords:
                    keywords.append(kw)
            for rec in self.records:
                if not isinstance(rec, dict):
                    continue
                rk = rec.get('min_rank', 0)
                if not rk or rk < rank_min or rk > rank_max:
                    continue
                mn = rec.get('major_name', '')
                uni = rec.get('university_name', '')
                if any(kw in str(mn) for kw in keywords):
                    expected.add(uni)
        return expected

    def _rank_range_for(self, rank: int) -> Tuple[int, int]:
        """返回位次对应的搜索范围"""
        # 使用动态位次范围
        if rank <= 10000:
            pct = 0.10
        elif rank <= 30000:
            pct = 0.15
        elif rank <= 70000:
            pct = 0.20
        elif rank <= 120000:
            pct = 0.25
        else:
            pct = 0.30
        return (max(1, int(rank * 0.7)), int(rank * (1 + pct)))

    def _is_exact_match(self, major_name: str, uni_name: str,
                        group_code: str, target_major: str) -> bool:
        target = str(target_major).strip()
        if not target:
            return False
        code = str(group_code or '').replace('\n', '').strip()
        mapped = self.group_major_map.get((uni_name, code), [])
        if target in mapped:
            return True
        if target in str(major_name or ''):
            return True
        return False

    def _is_category_match(self, major_name: str, uni_name: str,
                           group_code: str, target_major: str) -> bool:
        target_cat = _classify_major(target_major)
        if target_cat == '其他':
            return False
        code = str(group_code or '').replace('\n', '').strip()
        mapped = self.group_major_map.get((uni_name, code), [])
        if mapped:
            for major in mapped:
                if _classify_major(major) == target_cat:
                    return True
        if _classify_major(str(major_name or '')) == target_cat:
            return True
        return False

    def _is_uni_hit(self, uni_name: str, expected_unis: Set[str]) -> bool:
        return uni_name in expected_unis

    def _check_hits(self, recommendations: List[Dict], target_major: str,
                    expected_unis: Set[str]) -> Dict[str, Any]:
        exact = False
        lenient_hit = False
        uni = False
        total = len(recommendations)
        for rec in recommendations:
            if not isinstance(rec, dict):
                continue
            uni_name = rec.get('university_name', '')
            major_name = rec.get('major_name', '')
            group_code = str(rec.get('group_code', '') or '')
            if not exact:
                exact = self._is_exact_match(major_name, uni_name, group_code, target_major)
            if not lenient_hit:
                lenient_hit = self._is_category_match(major_name, uni_name, group_code, target_major)
            if not uni:
                uni = self._is_uni_hit(uni_name, expected_unis)
            if exact and lenient_hit and uni:
                break
        return {'exact': exact, 'lenient': lenient_hit, 'uni': uni, 'total_count': total}

    def _run_service_test(self, label: str, get_recs_fn) -> Optional[List[Dict]]:
        results = []
        for tc in TEST_CASES:
            rank = tc['rank']
            major = tc['expected_major']
            rank_min, rank_max = self._rank_range_for(rank)
            expected_unis = self._get_expected_unis(major, rank_min, rank_max)
            try:
                recs = get_recs_fn(rank, major)
            except Exception as e:
                print(f"  [{label}] 位次={rank} 目标={major} 调用失败: {e}")
                results.append({'rank': rank, 'target_major': major,
                               'exact': False, 'lenient': False, 'uni': False,
                               'total_count': 0, 'expected_unis': expected_unis, 'error': str(e)})
                continue
            hits = self._check_hits(recs, major, expected_unis)
            hits['rank'] = rank
            hits['target_major'] = major
            hits['expected_unis'] = expected_unis
            results.append(hits)
            print(f"  [{label}] 位次={rank:>6}  {major:<14s} "
                  f"推荐={hits['total_count']:>3}  "
                  f"精确={'是' if hits['exact'] else '否'}  "
                  f"宽松={'是' if hits['lenient'] else '否'}  "
                  f"院校={'是' if hits['uni'] else '否'}  "
                  f"GT={len(expected_unis):>3}")
        return results

    def run_v2_test(self) -> Optional[List[Dict]]:
        try:
            from app.services.recommendation_service_v2 import RecommendationServiceV2
            service = RecommendationServiceV2(data_dir=self.data_dir, load_data=True)
            def get_recs(user_rank, target_major):
                result = service.recommend(user_rank=user_rank, province='广东',
                                          subject_type='理科', target_majors=[target_major],
                                          max_per_uni=3, min_total=25, verbose=False)
                if not result.get('success'):
                    return []
                all_recs = []
                for cat_recs in result.get('data', {}).values():
                    all_recs.extend(cat_recs)
                return all_recs
            return self._run_service_test('V2', get_recs)
        except Exception as e:
            import traceback
            print(f"\n[ERROR] V2 测试初始化失败: {e}")
            traceback.print_exc()
            return None

    def run_v3_test(self) -> Optional[List[Dict]]:
        try:
            from app.services.recommendation_service_v3 import RecommendationServiceV3
        except ImportError:
            print(f"\n[V3] 待测试(文件不存在: recommendation_service_v3.py)")
            return None
        try:
            service = RecommendationServiceV3(data_dir=self.data_dir, load_data=True)
            def get_recs(user_rank, target_major):
                result = service.recommend(user_rank=user_rank, province='广东',
                                          subject_type='理科', target_majors=[target_major])
                if not result.get('success'):
                    return []
                all_recs = []
                for cat_recs in result.get('data', {}).values():
                    all_recs.extend(cat_recs)
                return all_recs
            return self._run_service_test('V3', get_recs)
        except Exception as e:
            import traceback
            print(f"\n[V3] 测试失败: {e}")
            traceback.print_exc()
            return None

    def _fmt_table(self, label: str, results: List[Dict]) -> Tuple[str, tuple]:
        lines = []
        lines.append(f"")
        lines.append(f"------------------------------------------------------------")
        lines.append(f"{label} 算法")
        lines.append(f"------------------------------------------------------------")
        header = (f"{'位次':>6} | {'目标专业':<20s} | {'推荐数':>6} | "
                  f"{'精确':>4} | {'宽松':>4} | {'院校':>4} | {'GT院校':>6}")
        lines.append(header)
        lines.append("-" * len(header))

        exact_c = lenient_c = uni_c = total_recs = 0
        n = len(results)
        if n == 0:
            lines.append("  (无测试结果)")
            return "\n".join(lines), (0, 0, 0, 0)

        for r in results:
            exact_c += 1 if r['exact'] else 0
            lenient_c += 1 if r['lenient'] else 0
            uni_c += 1 if r['uni'] else 0
            total_recs += r['total_count']
            lines.append(
                f"{r['rank']:>6} | {r['target_major']:<20s} | {r['total_count']:>6} | "
                f"{'是' if r['exact'] else '否':>4} | {'是' if r['lenient'] else '否':>4} | "
                f"{'是' if r['uni'] else '否':>4} | {len(r.get('expected_unis', set())):>6}"
            )
        lines.append(f"------------------------------------------------------------")
        lines.append(f"精确命中率: {exact_c / n * 100:.1f}% ({exact_c}/{n})")
        lines.append(f"宽松命中率: {lenient_c / n * 100:.1f}% ({lenient_c}/{n})")
        lines.append(f"院校命中率: {uni_c / n * 100:.1f}% ({uni_c}/{n})")
        avg = total_recs / n if n > 0 else 0
        lines.append(f"平均推荐数: {avg:.1f}")
        return "\n".join(lines), (exact_c / n * 100, lenient_c / n * 100, uni_c / n * 100, avg)

    def _print_report(self, v2_results, v3_results) -> None:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(f"\n{'='*60}")
        print(f"专业命中率测试报告")
        print(f"{'='*60}")
        print(f"\n测试时间: {now}")
        print(f"数据记录数: {len(self.records)}")
        print(f"测试用例数: {len(TEST_CASES)}")
        print(f"模式: {'快速(前5000条)' if self.quick else '完整数据'}")
        print(f"数据映射组数: {len(self.group_major_map)}")
        print(f"反向索引专业数: {len(self.major_to_groups)}")

        v2_stats = None
        if v2_results is not None:
            tbl, v2_stats = self._fmt_table('V2', v2_results)
            print(tbl)
        else:
            print(f"\nV2: 测试未执行")

        v3_stats = None
        if v3_results is not None:
            tbl, v3_stats = self._fmt_table('V3', v3_results)
            print(tbl)
        else:
            print(f"\nV3: 待测试(文件不存在)")

        # 对比总结
        print(f"\n{'='*60}")
        print(f"对比总结")
        print(f"{'='*60}")
        header = f"{'指标':<16s} | {'V2':>8s} | {'V3':>8s} | {'改进':>8s}"
        print(header)
        print("-" * len(header))
        metrics = ['精确命中率', '宽松命中率', '院校命中率', '平均推荐数']
        for idx, metric in enumerate(metrics):
            v2s = f"{v2_stats[idx]:.1f}{'%' if idx < 3 else ''}" if v2_stats else 'N/A'
            v3s = f"{v3_stats[idx]:.1f}{'%' if idx < 3 else ''}" if v3_stats else 'N/A'
            if v2_stats and v3_stats:
                imp = v3_stats[idx] - v2_stats[idx]
                fmt = '.1f' if idx < 3 else '.1f'
                imp_s = f"{imp:+{fmt}}{'' if idx < 3 else ''}"
            else:
                imp_s = '--'
            print(f"{metric:<16s} | {v2s:>8s} | {v3s:>8s} | {imp_s:>8s}")

        # 验收标准
        print(f"\n{'='*60}")
        print(f"验收标准")
        print(f"{'='*60}")
        stats = v3_stats if v3_stats else (v2_stats if v2_stats else None)
        if stats:
            def pf(cond):
                return "PASS" if cond else "FAIL"
            print(f"  {pf(stats[0] >= 60.0)} 专业命中率 >= 60% (精确)  -> {stats[0]:.1f}%")
            print(f"  {pf(stats[2] >= 25.0)} 院校命中率 >= 25%           -> {stats[2]:.1f}%")
            print(f"  {pf(stats[3] >= 45.0)} 推荐数量 >= 45条            -> {stats[3]:.1f}")

    def run_all(self, v2_only: bool = False) -> None:
        print(f"\n{'='*60}")
        print(f"开始专业命中率测试")
        print(f"{'='*60}")

        print(f"\n>>> 运行 V2 测试 <<<")
        v2_results = self.run_v2_test()

        v3_results = None
        if not v2_only:
            print(f"\n>>> 运行 V3 测试 <<<")
            v3_results = self.run_v3_test()

        self._print_report(v2_results, v3_results)


def main():
    parser = argparse.ArgumentParser(description='专业命中率测试')
    parser.add_argument('--quick', action='store_true', help='快速模式 (前5000条)')
    parser.add_argument('--v2-only', action='store_true', help='仅测试V2')
    args = parser.parse_args()

    test = ProfessionalHitRateTest(quick=args.quick)
    test.run_all(v2_only=args.v2_only)


if __name__ == '__main__':
    main()
