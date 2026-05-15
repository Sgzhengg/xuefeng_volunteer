# -*- coding: utf-8 -*-
"""
广东高考志愿推荐服务 V3 (候选池优化版)

核心改进（对比 V2）：
1. 动态位次范围：替换固定 expand_pct，按 rank 段差异化 (±10%~±30%)
2. 扩大候选池：CANDIDATE_POOL_SIZE 500 (原 200)
3. 提前触发扩圈：EXPANSION_TRIGGER 50 (原 30)
4. 增加推荐数量：min_total=45, max_per_uni=4 (原 25/3)
5. 集成专业组映射：加载 group_code_mapping.json，将 group_code 解析为实际专业名
6. 分类策略调整：冲刺(diff<-0.15) / 稳妥(±0.15) / 保底(diff>0.15)

用法:
    from app.services.recommendation_service_v3 import RecommendationServiceV3
    service = RecommendationServiceV3()
    result = service.recommend(user_rank=15000, subject_type="理科")
    # result: {冲刺: [...], 稳妥: [...], 保底: [...]}
"""

import json
import os
import random
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime


# ============================================================
# 动态位次范围
# ============================================================

def get_dynamic_rank_range(user_rank: int) -> float:
    """根据用户位次返回动态位次范围比例

    关键修复：对于高分考生（前1000名），需要更大的范围才能找到合适的冲刺和保底学校
    """
    if user_rank <= 1000:
        return 0.80  # 精英考生 ±80%（位次800 → 160-1440，能覆盖清北到普通一本）
    elif user_rank <= 3000:
        return 0.60  # 顶尖考生 ±60%
    elif user_rank <= 10000:
        return 0.40  # 高分考生 ±40%
    elif user_rank <= 30000:
        return 0.25  # 中高分 ±25%
    elif user_rank <= 70000:
        return 0.20  # 中分段 ±20%
    elif user_rank <= 120000:
        return 0.25  # 中低分 ±25%
    else:
        return 0.30  # 低分 ±30%


# ============================================================
# 常量配置
# ============================================================

# V3 优化参数
CANDIDATE_POOL_SIZE = 500   # 候选池大小 (原 200)
EXPANSION_TRIGGER = 50      # 扩圈触发阈值 (原 30)
MAX_RECOMMENDATIONS = 45    # 最少推荐数 (原 25)

# 分数档位定义 (保留用于本地权重)
RANK_TIERS = [
    {'name': 'elite', 'min_rank': 1, 'max_rank': 3000, 'expand_pct': 0.25, 'local_weight': 1.25},
    {'name': 'high', 'min_rank': 3001, 'max_rank': 10000, 'expand_pct': 0.30, 'local_weight': 1.20},
    {'name': 'upper_mid', 'min_rank': 10001, 'max_rank': 30000, 'expand_pct': 0.35, 'local_weight': 1.15},
    {'name': 'mid', 'min_rank': 30001, 'max_rank': 80000, 'expand_pct': 0.40, 'local_weight': 1.10},
    {'name': 'lower_mid', 'min_rank': 80001, 'max_rank': 150000, 'expand_pct': 0.45, 'local_weight': 1.05},
    {'name': 'low', 'min_rank': 150001, 'max_rank': 350000, 'expand_pct': 0.55, 'local_weight': 1.02},
]

# 子模型权重
MODEL_WEIGHTS = {
    'hotness': 0.20,
    'city': 0.15,
    'trend': 0.20,
    'local': 0.15,
    'rank_fit': 0.30,
}

# 985/211 名单
KNOWN_985 = {
    '北京大学', '清华大学', '复旦大学', '上海交通大学', '浙江大学',
    '中国科学技术大学', '南京大学', '中国人民大学', '中山大学',
    '华南理工大学', '武汉大学', '华中科技大学', '西安交通大学',
    '哈尔滨工业大学', '北京师范大学', '南开大学', '天津大学',
    '同济大学', '东南大学', '厦门大学', '四川大学', '电子科技大学',
    '吉林大学', '东北大学', '大连理工大学', '山东大学',
    '中国海洋大学', '西北工业大学', '兰州大学', '北京航空航天大学',
    '北京理工大学', '中国农业大学', '国防科技大学', '中央民族大学',
    '华东师范大学', '中南大学', '湖南大学', '重庆大学', '西北农林科技大学',
}
KNOWN_211 = {
    '暨南大学', '华南师范大学', '北京邮电大学', '北京交通大学',
    '北京科技大学', '北京化工大学', '北京工业大学', '北京林业大学',
    '北京中医药大学', '北京外国语大学', '中国传媒大学',
    '中央财经大学', '对外经济贸易大学', '中国政法大学',
    '华北电力大学', '中国矿业大学', '中国石油大学',
    '中国地质大学', '东北师范大学', '东北林业大学',
    '华东理工大学', '东华大学', '上海外国语大学', '上海财经大学',
    '上海大学', '苏州大学', '南京航空航天大学', '南京理工大学',
    '中国药科大学', '河海大学', '江南大学', '南京农业大学',
    '南京师范大学', '合肥工业大学', '安徽大学', '福州大学',
    '南昌大学', '郑州大学', '武汉理工大学',
    '华中师范大学', '华中农业大学', '中南财经政法大学',
    '湖南师范大学', '西南交通大学', '四川农业大学',
    '西南大学', '西南财经大学', '贵州大学', '云南大学',
    '西藏大学', '西北大学', '西安电子科技大学', '长安大学',
    '陕西师范大学', '青海大学', '宁夏大学', '新疆大学',
    '石河子大学', '海南大学', '广西大学', '内蒙古大学',
    '延边大学', '辽宁大学', '大连海事大学', '太原理工大学',
    '河北工业大学', '哈尔滨工程大学', '东北农业大学',
}

# 广东省内院校
GUANGDONG_UNIS = {
    '中山大学', '华南理工大学', '暨南大学', '华南师范大学',
    '深圳大学', '南方医科大学', '广东外语外贸大学', '广东工业大学',
    '广州大学', '广州医科大学', '华南农业大学', '广东财经大学',
    '广州中医药大学', '汕头大学', '东莞理工学院', '广东海洋大学',
    '广东技术师范大学', '广东药科大学', '广东医科大学',
    '仲恺农业工程学院', '广东石油化工学院', '五邑大学',
    '广州航海学院', '深圳技术大学', '广东金融学院',
    '南方科技大学', '哈尔滨工业大学(深圳)', '北京师范大学(珠海校区)',
    '北京师范大学(珠海)', '北京师范大学珠海分校',
    '北京师范大学-香港浸会大学联合国际学院', '香港中文大学(深圳)',
    '广东以色列理工学院', '深圳北理莫斯科大学',
    '遵义医科大学(珠海校区)',
}

# 专业大类关键词
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

# 区域扩展路径
EXPANSION_PATHS_ELITE = ['985省内', '985省外', '211省内', '211省外', '双一流省外']
EXPANSION_PATHS_MID = ['广东省内', '一线城市', '新一线城市', '省会城市', '其他']
EXPANSION_PATHS_LOW = ['广东省内', '周边省份', '全国']


class RecommendationServiceV3:
    """V3 推荐服务 - 候选池优化版"""

    def __init__(self, data_dir: Path = None, load_data: bool = True,
                 candidate_pool_size: int = CANDIDATE_POOL_SIZE,
                 expansion_trigger: int = EXPANSION_TRIGGER,
                 min_total: int = MAX_RECOMMENDATIONS):
        self.data_dir = data_dir or Path(__file__).parent.parent.parent / 'data'
        self.candidate_pool_size = candidate_pool_size
        self.expansion_trigger = expansion_trigger
        self.min_total = min_total

        self.records = []
        self.hotness_matrix = {}
        self.city_attraction = {}
        self.trend_data = {}
        self.cat_trends = {}
        self.group_code_mapping = {}  # (uni, group_code) -> [major names]
        self.detailed_group_mapping = {}  # (uni, group_code) -> {tuition, duration, subjects, majors...}

        # 内部索引
        self._records_by_year = defaultdict(list)
        self._records_by_rank_range = defaultdict(list)
        self._uni_city_map = {}
        self._uni_level_map = {}
        self._records_deduplicated = []

        if load_data:
            self._load_all()

    def _load_all(self):
        """加载所有数据源和模型"""
        # 1. 主数据
        main_file = self.data_dir / 'major_rank_data.json'
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.records = data.get('major_rank_data', [])
            print(f'[V3] Loaded {len(self.records)} records from major_rank_data.json')

        # 2. 专业组映射 (V3 新增)
        mapping_file = self.data_dir / 'group_code_mapping.json'
        if mapping_file.exists():
            with open(mapping_file, 'r', encoding='utf-8') as f:
                raw_mapping = json.load(f)
            # 转换键格式: "中山大学_201" -> ("中山大学", "201") -> [majors]
            for key, info in raw_mapping.items():
                if isinstance(key, str) and '_' in key:
                    parts = key.rsplit('_', 1)
                    if len(parts) == 2:
                        uni, code = parts[0], parts[1]
                        clean_code = code.replace('\n', '').strip()
                        self.group_code_mapping[(uni, clean_code)] = info.get('majors', [])
            print(f'[V3] Loaded {len(self.group_code_mapping)} group code mappings')

        # 2b. 官方招生计划专业组映射 (2025) - 包含学费、学制等详细信息
        detailed_file = self.data_dir / 'group_code_to_majors.json'
        if detailed_file.exists():
            with open(detailed_file, 'r', encoding='utf-8') as f:
                raw_detailed = json.load(f)
            for key, info in raw_detailed.items():
                if isinstance(key, str) and '_' in key:
                    parts = key.rsplit('_', 1)
                    if len(parts) == 2:
                        uni, code = parts[0], parts[1]
                        clean_code = code.replace('\n', '').strip()
                        self.detailed_group_mapping[(uni, clean_code)] = {
                            'majors': [m.get('major_name', m) if isinstance(m, dict) else m
                                       for m in info.get('majors', [])],
                            'major_details': info.get('majors', []),
                            'tuition': info.get('tuition'),
                            'duration': info.get('duration'),
                            'subjects': info.get('subjects', ''),
                            'plan_count': info.get('plan_count', 0),
                            'category': info.get('category', ''),
                            'university_code': info.get('university_code', ''),
                        }
            print(f'[V3] Loaded {len(self.detailed_group_mapping)} detailed group mappings (2025 official)')

        # 3. 热度矩阵
        hotness_file = self.data_dir / 'rank_hotness_matrix.json'
        if hotness_file.exists():
            with open(hotness_file, 'r', encoding='utf-8') as f:
                self.hotness_matrix = json.load(f)
            print(f'[V3] Loaded hotness matrix ({len(self.hotness_matrix.get("segments", {}))} segments)')

        # 4. 城市吸引力
        city_file = self.data_dir / 'city_attraction_index.json'
        if city_file.exists():
            with open(city_file, 'r', encoding='utf-8') as f:
                self.city_attraction = json.load(f)
            print(f'[V3] Loaded city attraction ({len(self.city_attraction.get("provinces", {}))} provinces)')

        # 5. 专业趋势
        trend_file = self.data_dir / 'major_trend_analysis.json'
        if trend_file.exists():
            with open(trend_file, 'r', encoding='utf-8') as f:
                self.trend_data = json.load(f)
            self.cat_trends = self.trend_data.get('category_trends', {})
            print(f'[V3] Loaded major trends ({len(self.trend_data.get("trends", []))} trends)')

        # 构建索引
        self._build_indices()
        self._build_uni_info()

    def _build_indices(self):
        """构建快速查找索引"""
        self._records_by_year = defaultdict(list)
        self._records_by_rank_range = defaultdict(list)

        for r in self.records:
            if not isinstance(r, dict):
                continue
            yr = r.get('year', 0)
            self._records_by_year[yr].append(r)

            rank = r.get('min_rank', 0)
            if rank > 0:
                bucket = rank // 10000
                self._records_by_rank_range[bucket].append(r)

        # 构建去重记录列表
        dedup_key_rank = {}
        for r in self.records:
            if not isinstance(r, dict):
                continue
            code = str(r.get('group_code', '')).replace('\n', '').strip()
            key = (r.get('university_name', ''), code)
            rank = r.get('min_rank', 0)
            if key[0] and key[1] and rank > 0:
                if key not in dedup_key_rank or r.get('year', 0) > dedup_key_rank[key].get('year', 0):
                    dedup_key_rank[key] = r
        self._records_deduplicated = list(dedup_key_rank.values())
        print(f'[V3] Deduplicated: {len(self._records_deduplicated)} unique (uni, group_code) combos')

    def _build_uni_info(self):
        """构建高校信息映射"""
        for r in self.records:
            if not isinstance(r, dict):
                continue
            uni = r.get('university_name', '')
            prov = r.get('university_province', '')
            level = r.get('university_level', '')
            if uni and not self._uni_city_map.get(uni):
                self._uni_city_map[uni] = prov
            if uni and not self._uni_level_map.get(uni):
                self._uni_level_map[uni] = level

    def _get_tier(self, user_rank: int) -> dict:
        """获取用户所在档位"""
        for tier in RANK_TIERS:
            if tier['min_rank'] <= user_rank <= tier['max_rank']:
                return tier
        if user_rank < 1:
            return RANK_TIERS[0]
        return RANK_TIERS[-1]

    def _get_rank_segment_key(self, user_rank: int) -> str:
        """获取位次段键名 (每 5000 一段)"""
        seg_start = ((user_rank - 1) // 5000) * 5000 + 1
        seg_end = seg_start + 4999
        return f"{seg_start}-{seg_end}"

    # ============================================================
    # 专业组映射 (V3 新增)
    # ============================================================

    def _resolve_major_name(self, university_name: str, group_code) -> List[str]:
        """从 group_code_mapping 中获取实际专业列表"""
        code = str(group_code or '').replace('\n', '').strip()
        if not code:
            return []
        return self.group_code_mapping.get((university_name, code), [])

    def _clean_code(self, code) -> str:
        """清洗 group_code 中的异常字符"""
        return str(code or '').replace('\n', '').strip()

    def _normalize_group_code(self, group_code) -> str:
        """标准化专业组代码，去除前导零和空格"""
        if not group_code:
            return ""
        code = str(group_code).strip()
        if code.isdigit():
            return str(int(code))
        return code

    # ============================================================
    # 主推荐方法
    # ============================================================
    def recommend(self, user_rank: int, province: str = "广东",
                  subject_type: str = "理科",
                  target_majors: Optional[List[str]] = None,
                  max_per_uni: int = 4,
                  min_total: int = None,
                  verbose: bool = False) -> Dict[str, Any]:
        """
        生成推荐方案

        Returns:
            {冲刺: [...], 稳妥: [...], 保底: [...]}
        """
        if min_total is None:
            min_total = self.min_total

        tier = self._get_tier(user_rank)
        # V3: 使用动态位次范围替代固定 expand_pct
        rank_range_pct = get_dynamic_rank_range(user_rank)

        if verbose:
            print(f'[V3] user_rank={user_rank}, tier={tier["name"]}, range={rank_range_pct:.0%}')
            print(f'[V3] 候选池范围: {int(user_rank * (1 - rank_range_pct))} - {int(user_rank * (1 + rank_range_pct))}')

        # 1. 候选人筛选 (使用动态位次范围)
        candidates = self._filter_candidates(user_rank, rank_range_pct, province)

        if verbose:
            print(f'[V3] 初始筛选 {len(candidates)} 个候选 (province={province})')
            if len(candidates) > 0:
                ranks = [c.get('min_rank', 0) for c in candidates]
                print(f'[V3] 候选位次范围: {min(ranks)} - {max(ranks)}')

        # 2. 扩圈 (V3: 关键修复)
        # 修复说明：无论初始候选数量是否达到触发阈值，都应尝试所有扩圈层级，
        # 直到收集到足够的候选（以去重后的数量为准）或耗尽所有层级。
        expand_stages = self._get_expansion_stages(tier, rank_range_pct, province)
        # 从第二层开始对外扩（第一层即为基准范围）
        for idx, (stage_range, stage_province) in enumerate(expand_stages[1:], start=2):
            # 在每层入口处打印诊断日志，便于追踪扩圈过程
            current_results = self._deduplicate_candidates(candidates)
            print(f"[DEBUG 扩圈] 当前层: 第 {idx-1} 层, 当前结果数: {len(current_results)}, 目标数量: {min_total}")

            new_candidates = self._filter_candidates(user_rank, stage_range, stage_province)
            before_add = len(candidates)
            candidates.extend(new_candidates)
            added = len(candidates) - before_add

            if verbose:
                print(f'[V3] 扩圈 第{idx-1}层: range={stage_range:.0%}, province={stage_province}, 新增={added}, 总计={len(candidates)}')

            # 使用去重后的数量判断是否已收集到足够的候选
            deduped_now = self._deduplicate_candidates(candidates)
            # 停止条件：去重后数量达到候选池上限或达到最小目标数量
            if len(deduped_now) >= max(self.candidate_pool_size, min_total):
                candidates = deduped_now
                break
            else:
                # 保留累积（未达到则继续下一层），但 keep deduped for next iteration to avoid explosion
                candidates = deduped_now

        # 3. 去重
        candidates = self._deduplicate_candidates(candidates)
        if verbose:
            print(f'[V3] 去重后: {len(candidates)} 个候选')

        # 4. 多模型评分
        scored = self._multi_model_score(candidates, user_rank, tier, target_majors)

        # 5. 分类 (V3: 使用新的分类阈值)
        recommendations = self._categorize(scored, user_rank, max_per_uni, min_total)

        if verbose:
            for cat, items in recommendations.items():
                print(f'[V3] {cat}: {len(items)} 个')

        # 6. 数量补充
        total = sum(len(v) for v in recommendations.values())
        if total < min_total:
            if verbose:
                print(f'[V3] ⚠️ 总数不足 ({total} < {min_total})，触发补充')
            recommendations = self._supplement(
                recommendations, user_rank, max_per_uni, min_total, tier
            )
            if verbose:
                total_after = sum(len(v) for v in recommendations.values())
                print(f'[V3] 补充后: {total_after} 个')
                for cat, items in recommendations.items():
                    print(f'[V3] {cat}: {len(items)} 个')

        # 7. 解析专业名 (V3 新增: 为返回结果附加实际专业名称)
        recommendations = self._enrich_major_names(recommendations)

        # 8. 计算录取概率 (V3 新增)
        recommendations = self._add_admission_probability(recommendations, user_rank)

        total_final = sum(len(v) for v in recommendations.values())
        return {
            'success': True,
            'data': recommendations,
            'user_rank': user_rank,
            'tier': tier['name'],
            'total_count': total_final,
            'algorithm': 'v3'
        }

    def _get_expansion_stages(self, tier: dict, base_range: float, province: str) -> List[Tuple[float, str]]:
        """获取扩圈阶段 (V3: 基于动态位次范围)

        关键修复：对于精英考生，需要更激进的扩圈策略以确保有足够的冲刺和保底选择
        """
        name = tier['name']
        stages = [(base_range, province)]

        if name == 'elite':  # 位次1-3000
            # 精英考生需要全国范围内的学校，扩圈到3-5倍
            stages.append((min(base_range * 2.0, 1.5), province))  # 2倍或150%
            stages.append((min(base_range * 3.0, 2.0), 'all'))     # 3倍或200%，全国
            stages.append((min(base_range * 5.0, 3.0), 'all'))     # 5倍或300%，全国
        elif name == 'high':  # 位次3001-10000
            stages.append((base_range * 1.5, province))
            stages.append((base_range * 2.0, 'all'))
            stages.append((base_range * 3.0, 'all'))
        elif name in ('upper_mid', 'mid'):
            stages.append((base_range * 1.5, 'all'))
            stages.append((base_range * 2.0, 'all'))
        else:
            stages.append((base_range * 1.3, 'all'))
            stages.append((base_range * 1.8, 'all'))
            stages.append((base_range * 2.5, 'all'))

        return stages

    def _filter_candidates(self, user_rank: int, expand_pct: float,
                           province: str) -> List[dict]:
        """按位次范围和省份筛选候选人（修复：确保所有分数段的合理覆盖）"""

        # 关键修复：确保所有分数段都有足够的冲刺和保底选择
        if user_rank <= 1000:
            # 精英考生：从清北到普通一本的广泛范围
            min_rank = 1
            max_rank = user_rank * 10
        elif user_rank <= 5000:
            # 高分考生：从清北到优秀211
            min_rank = 1
            max_rank = user_rank * 5
        elif user_rank <= 10000:
            # 中高分考生：从C9到211
            min_rank = int(user_rank * 0.05)  # 向上小范围冲刺
            max_rank = user_rank * 4           # 向下大幅扩保底
        elif user_rank <= 30000:
            # 中上分考生：从部分985到普通一本
            min_rank = int(user_rank * 0.1)   # 向上冲刺
            max_rank = user_rank * 3           # 向下保底
        elif user_rank <= 80000:
            # 中分考生：从211到二本
            min_rank = int(user_rank * 0.2)   # 向上冲刺
            max_rank = user_rank * 2.5         # 向下保底
        elif user_rank <= 150000:
            # 中低分考生：从普通一本到民办
            min_rank = int(user_rank * 0.3)   # 向上冲刺
            max_rank = user_rank * 2.0         # 向下保底
        else:
            # 低分考生：从二本到专科
            min_rank = int(user_rank * 0.4)   # 向上冲刺
            max_rank = user_rank * 1.8         # 向下保底

        if min_rank < 1:
            min_rank = 1

        min_bucket = min_rank // 10000
        max_bucket = max_rank // 10000

        candidates = []
        seen_keys = set()

        for bucket in range(max(0, min_bucket), max_bucket + 1):
            for r in self._records_by_rank_range.get(bucket, []):
                rank = r.get('min_rank', 0)
                if rank < min_rank or rank > max_rank:
                    continue
                if province != 'all':
                    rec_prov = r.get('province', '') or r.get('university_province', '')
                    if rec_prov != province:
                        continue
                code = self._clean_code(r.get('group_code', ''))
                key = (r.get('university_name', ''), code)
                if key not in seen_keys and key[0] and key[1]:
                    seen_keys.add(key)
                    candidates.append(r)

        return candidates

    def _deduplicate_candidates(self, candidates: List[dict]) -> List[dict]:
        """去重并保留最新年份的数据"""
        best = {}
        for c in candidates:
            if not isinstance(c, dict):
                continue
            code = self._clean_code(c.get('group_code', ''))
            key = (c.get('university_name', ''), code)
            if not key[0] or not key[1]:
                continue
            if key not in best or c.get('year', 0) > best[key].get('year', 0):
                best[key] = c
        return list(best.values())

    # ============================================================
    # 多模型评分
    # ============================================================
    def _multi_model_score(self, candidates: List[dict], user_rank: int,
                           tier: dict, target_majors: Optional[List[str]]) -> List[dict]:
        """对每个候选人计算复合得分"""
        seg_key = self._get_rank_segment_key(user_rank)
        hotness_seg = self.hotness_matrix.get('segments', {}).get(seg_key, [])
        hotness_rank = {h['university_name']: i for i, h in enumerate(hotness_seg)}

        cities = self.city_attraction.get('provinces', {})
        trend_map = self._build_trend_map()
        target_keywords = self._extract_target_keywords(target_majors or [])
        local_weight = tier.get('local_weight', 1.10)

        for c in candidates:
            uni = c.get('university_name', '')
            prov = c.get('university_province', '') or ''
            group_code = self._clean_code(c.get('group_code', ''))
            c_rank = c.get('min_rank', user_rank)

            # 1. 热度分 (0-1)
            hot_idx = hotness_rank.get(uni, len(hotness_seg))
            hotness_score = 1.0 - min(hot_idx / max(1, len(hotness_seg)), 1.0)

            # 2. 城市吸引力分 (0-1)
            city_info = cities.get(prov, {})
            city_score = city_info.get('attraction_score', 0.5)

            # 3. 趋势分 (0-1) -- V3: 优先使用映射后的专业名
            trend_key = f"{uni}||{group_code}"
            trend_info = trend_map.get(trend_key, {})
            trend_val = trend_info.get('trend', 'unknown')
            trend_map_score = {'warming': 1.0, 'stable': 0.7, 'cooling': 0.3, 'unknown': 0.5}
            trend_score = trend_map_score.get(trend_val, 0.5)

            # 3b. 大类趋势加成 (V3: 优先用映射专业名判断)
            cat_trend_bonus = 0.0
            if target_keywords:
                resolved_majors = self._resolve_major_name(uni, group_code)
                if resolved_majors:
                    # 使用映射后的专业名进行分类
                    for rm in resolved_majors:
                        cat = self._classify_major(rm)
                        if cat in self.cat_trends:
                            cs = self.cat_trends[cat].get('trend_score', 0.5)
                            bonus = (cs - 0.5) * 0.5
                            cat_trend_bonus = max(cat_trend_bonus, bonus)
                else:
                    major_name = c.get('major_name', '')
                    cat = self._classify_major(major_name)
                    if cat in self.cat_trends:
                        cat_score = self.cat_trends[cat].get('trend_score', 0.5)
                        cat_trend_bonus = (cat_score - 0.5) * 0.5

            # 4. 本地偏好分 (0-1)
            local_score = 0.5
            if uni in GUANGDONG_UNIS or prov == '广东':
                local_score = 1.0
            elif prov in ('北京', '上海', '浙江', '江苏'):
                local_score = 0.6
            elif prov in ('湖南', '江西', '广西', '福建', '海南', '湖北'):
                local_score = 0.4

            # 5. 位次匹配度 (0-1)
            if c_rank > 0:
                ratio = c_rank / max(1, user_rank)
                if 0.8 <= ratio <= 1.2:
                    rank_fit = 1.0
                elif 0.5 <= ratio <= 1.5:
                    rank_fit = 0.7
                elif 0.3 <= ratio <= 2.0:
                    rank_fit = 0.4
                else:
                    rank_fit = 0.2
            else:
                rank_fit = 0.5

            # 综合得分
            composite = (
                MODEL_WEIGHTS['hotness'] * hotness_score +
                MODEL_WEIGHTS['city'] * city_score +
                MODEL_WEIGHTS['trend'] * (trend_score + cat_trend_bonus) +
                MODEL_WEIGHTS['local'] * (local_score * local_weight) +
                MODEL_WEIGHTS['rank_fit'] * rank_fit +
                random.uniform(-0.04, 0.04)
            )

            c['_hotness'] = round(hotness_score, 4)
            c['_city'] = round(city_score, 4)
            c['_trend'] = round(trend_score + cat_trend_bonus, 4)
            c['_local'] = round(local_score, 4)
            c['_rank_fit'] = round(rank_fit, 4)
            c['_score'] = round(composite, 4)

        candidates.sort(key=lambda x: x.get('_score', 0), reverse=True)
        return candidates

    def _build_trend_map(self) -> Dict[str, dict]:
        """构建趋势查找映射"""
        trend_map = {}
        for t in self.trend_data.get('trends', []):
            if isinstance(t, dict):
                code = self._clean_code(t.get('group_code', ''))
                key = f"{t.get('university_name', '')}||{code}"
                trend_map[key] = t
        return trend_map

    def _classify_major(self, major_name: str) -> str:
        """从专业名推断大类"""
        if not major_name:
            return '其他'
        mn = str(major_name)
        for cat, keywords in MAJOR_CATEGORIES.items():
            for kw in keywords:
                if kw in mn:
                    return cat
        return '其他'

    def _extract_target_keywords(self, target_majors: List[str]) -> List[str]:
        """提取目标专业关键词"""
        keywords = set()
        for m in target_majors:
            m = str(m)
            keywords.add(m)
            syn_map = {
                '计算机': ['计算机科学与技术', '软件工程', '网络工程', '信息安全', '人工智能', '大数据', '数据科学'],
                '临床': ['临床医学', '口腔医学', '麻醉学', '医学影像学', '中医学', '中西医临床医学'],
                '电气': ['电气工程', '自动化', '电子信息', '通信工程', '集成电路'],
                '金融': ['金融学', '经济学', '会计学', '财务管理', '国际经济与贸易'],
                '土木': ['土木工程', '建筑学', '工程管理', '给排水', '城乡规划'],
                '机械': ['机械工程', '车辆工程', '机械设计', '智能制造', '机器人工程'],
                '法学': ['法学', '知识产权', '政治学', '社会工作'],
            }
            for key_term, syns in syn_map.items():
                if key_term in m:
                    keywords.update(syns)
        return list(keywords)

    # ============================================================
    # 分类与后处理
    # ============================================================
    def _categorize(self, scored: List[dict], user_rank: int,
                    max_per_uni: int, min_total: int) -> Dict[str, List[dict]]:
        """分类为冲刺/稳妥/保底 (V3: 精确阈值)"""
        chongci, wenzuo, baodi = [], [], []

        for c in scored:
            c_rank = c.get('min_rank', user_rank)
            if c_rank <= 0:
                continue

            diff = (c_rank - user_rank) / max(1, user_rank)

            # 修复分类逻辑：
            # diff > 0.15: 学校位次 > 用户位次×1.15 → 学校要求更低 → 冲刺
            # -0.15 <= diff <= 0.15: 位次相近 → 稳妥
            # diff < -0.15: 学校位次 < 用户位次×0.85 → 学校要求更高 → 保底
            if diff > 0.15:
                chongci.append(c)
            elif diff >= -0.15:
                wenzuo.append(c)
            else:
                baodi.append(c)

        def diversity_select(items: List[dict], limit: int, per_uni: int) -> List[dict]:
            """多样性选择：每轮每校最多取1个"""
            if not items:
                return []

            uni_groups = defaultdict(list)
            for item in items:
                uni = item.get('university_name', '')
                uni_groups[uni].append(item)

            uni_best_score = {
                u: max(g.get('_score', 0) for g in group)
                for u, group in uni_groups.items()
            }
            uni_keys = sorted(uni_groups.keys(),
                             key=lambda u: uni_best_score[u],
                             reverse=True)

            result = []
            pointer = {u: 0 for u in uni_keys}
            round_num = 0
            while len(result) < limit and round_num < per_uni:
                for uni in uni_keys:
                    if len(result) >= limit:
                        break
                    groups = uni_groups[uni]
                    idx = pointer[uni]
                    if idx < len(groups):
                        result.append(groups[idx])
                        pointer[uni] += 1
                round_num += 1
                if all(pointer[u] >= len(uni_groups[u]) for u in uni_keys):
                    break

            return result

        # V3: 每类至少 min_total // 3 个，但使用动态限制以增加总数
        per_cat = max(15, min_total // 3)
        return {
            '\u51b2\u523a': diversity_select(chongci, per_cat, max_per_uni),
            '\u7a33\u59a5': diversity_select(wenzuo, per_cat, max_per_uni),
            '\u4fdd\u5e95': diversity_select(baodi, per_cat, max_per_uni),
        }

    def _supplement(self, recommendations: Dict, user_rank: int,
                    max_per_uni: int, min_total: int, tier: dict) -> Dict:
        """补充推荐到最小数量（修复：正确分类补充的学校）"""
        total = sum(len(v) for v in recommendations.values())
        if total >= min_total:
            return recommendations

        needed = min_total - total
        # 扩大补充范围，确保能找到足够的学校
        max_rank = int(user_rank * 5.0)  # 扩大到5倍
        min_rank = max(1, int(user_rank * 0.1))  # 扩大到0.1倍

        existing_keys = set()
        for cat in recommendations.values():
            for c in cat:
                code = self._clean_code(c.get('group_code', ''))
                key = (c.get('university_name', ''), code)
                existing_keys.add(key)

        supplements = []
        for r in self.records:
            if not isinstance(r, dict):
                continue
            rk = r.get('min_rank', 0)
            if rk < min_rank or rk > max_rank:
                continue
            code = self._clean_code(r.get('group_code', ''))
            key = (r.get('university_name', ''), code)
            if key in existing_keys or not key[0]:
                continue
            existing_keys.add(key)
            supplements.append(r)
            if len(supplements) >= needed * 2:  # 多找一些，然后筛选
                break

        # 对补充的学校进行评分和分类
        if supplements:
            scored_supplements = self._multi_model_score(supplements, user_rank, tier, None)
            # 重新分类所有推荐（包括原有的和补充的）
            all_items = []
            for cat_items in recommendations.values():
                all_items.extend(cat_items)
            all_items.extend(scored_supplements)

            # 重新分类
            recommendations = self._categorize(all_items, user_rank, max_per_uni, min_total)

        return recommendations

    # ============================================================
    # 专业名增强 (V3 新增)
    # ============================================================
    def _enrich_major_names(self, recommendations: Dict[str, List[dict]]) -> Dict[str, List[dict]]:
        """为推荐结果附加实际专业名称列表及详细信息（2025官方招生计划）"""
        for cat_name, items in recommendations.items():
            for item in items:
                uni = item.get('university_name', '')
                # 标准化 group_code，兼容不同来源的格式
                raw_code = item.get('group_code', '')
                code = self._normalize_group_code(raw_code)

                # 1. 从旧映射获取基础专业名
                resolved = self._resolve_major_name(uni, code)
                if resolved:
                    item['resolved_majors'] = resolved
                    if not item.get('major_name') or '专业组' in str(item.get('major_name', '')):
                        item['major_display'] = ', '.join(resolved[:3])
                        # 🔧 修复：直接替换major_name字段
                        item['major_name'] = resolved[0]
                else:
                    # 打印警告便于定位数据缺失
                    print(f"[WARN 映射缺失] 未在 simple mapping 中找到: {uni}_{code}")

                # 2. 从2025官方招生计划获取详细信息
                detail = self.detailed_group_mapping.get((uni, code))
                if detail:
                    # 专业列表
                    if detail.get('majors'):
                        item['resolved_majors'] = detail['majors']
                        item['major_display'] = ', '.join(detail['majors'][:3])
                        # 🔧 修复：确保用第一个专业名替换"专业组XXX"
                        if '专业组' in str(item.get('major_name', '')):
                            item['major_name'] = detail['majors'][0]

                    # 附加字段
                    item['tuition'] = detail.get('tuition')
                    item['duration'] = detail.get('duration')
                    item['plan_count'] = detail.get('plan_count', 0)
                    item['subjects_requirement'] = detail.get('subjects', '')

                    # 专业详细信息（含专业代码和备注）
                    item['major_details'] = detail.get('major_details', [])

        return recommendations

    # ============================================================
    # 录取概率计算 (V3 新增)
    # ============================================================
    def _add_admission_probability(self, recommendations: Dict[str, List[dict]],
                                   user_rank: int) -> Dict[str, List[dict]]:
        """基于位次差计算录取概率"""
        for cat_name, items in recommendations.items():
            for item in items:
                c_rank = item.get('min_rank', user_rank)
                if c_rank > 0:
                    diff = (c_rank - user_rank) / max(1, user_rank)
                    if cat_name == '冲刺':
                        # diff in [0.15, 0.40] -> prob in [20, 45]
                        # 学校位次越高，录取概率越低
                        prob = max(20, min(45, int(25 + (diff - 0.15) * 100)))
                    elif cat_name == '稳妥':
                        # diff in [-0.15, 0.15] -> prob in [50, 75]
                        # 位次接近，录取概率较高
                        prob = max(50, min(75, int(60 + diff * 83)))
                    else:  # 保底
                        # diff in [-0.40, -0.15] -> prob in [75, 95]
                        # 学校位次越低，录取概率越高
                        prob = max(75, min(95, int(85 + (diff + 0.15) * 80)))
                else:
                    prob = 50  # fallback
                item['admission_probability'] = prob
                item['admission_probability_pct'] = f'{prob}%'
        return recommendations

    # ============================================================
    # 兼容 V1 接口
    # ============================================================
    def recommend_with_fallback(self, user_rank: int, province: str = "广东",
                                 subject_type: str = "理科",
                                 target_majors: Optional[List[str]] = None) -> Dict[str, Any]:
        """兼容 V1 的 recommend_with_fallback 接口"""
        return self.recommend(
            user_rank=user_rank,
            province=province,
            subject_type=subject_type,
            target_majors=target_majors
        )


# 不自动创建全局实例
# 使用时请自行实例化: service = RecommendationServiceV3()
