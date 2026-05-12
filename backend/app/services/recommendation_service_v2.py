# -*- coding: utf-8 -*-
"""
广东高考志愿推荐服务 V2 (数据驱动版)

核心改进：
1. 多模型复合评分：热度矩阵 + 城市吸引力 + 专业趋势 + 本地偏好 + 位次匹配
2. 动态位次扩展：按分数档位调整扩展比例（不再固定 ±20%→±50%→全国）
3. 动态本地偏好：按档位差异化权重（不再固定 1.15x）
4. 区域扩展策略：高分按学校层次、中分按城市吸引力、低分按历史去向
5. 后处理：同院校最多 3 个专业、最少 25 个推荐

用法:
    from app.services.recommendation_service_v2 import RecommendationServiceV2
    service = RecommendationServiceV2()
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
# 常量配置
# ============================================================

# 分数档位定义 (expand_pct 提高以增加命中率)
RANK_TIERS = [
    {'name': 'elite', 'min_rank': 1, 'max_rank': 3000, 'expand_pct': 0.25, 'local_weight': 1.25},
    {'name': 'high', 'min_rank': 3001, 'max_rank': 10000, 'expand_pct': 0.30, 'local_weight': 1.20},
    {'name': 'upper_mid', 'min_rank': 10001, 'max_rank': 30000, 'expand_pct': 0.35, 'local_weight': 1.15},
    {'name': 'mid', 'min_rank': 30001, 'max_rank': 80000, 'expand_pct': 0.40, 'local_weight': 1.10},
    {'name': 'lower_mid', 'min_rank': 80001, 'max_rank': 150000, 'expand_pct': 0.45, 'local_weight': 1.05},
    {'name': 'low', 'min_rank': 150001, 'max_rank': 350000, 'expand_pct': 0.55, 'local_weight': 1.02},
]

# 子模型权重 (降低热线知名度权重以提高多样性)
MODEL_WEIGHTS = {
    'hotness': 0.20,   # 热度矩阵 (降低: 避免过度集中热门院校)
    'city': 0.15,       # 城市吸引力
    'trend': 0.20,      # 专业趋势
    'local': 0.15,      # 本地偏好
    'rank_fit': 0.30,   # 位次匹配度 (提高: 优先匹配用户位次)
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

# 专业大类关键词（用于趋势匹配）
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

# 区域扩展路径（按档位）
# elite/high: 学校层次扩展
EXPANSION_PATHS_ELITE = ['985省内', '985省外', '211省内', '211省外', '双一流省外']
# mid: 城市吸引力扩展
EXPANSION_PATHS_MID = ['广东省内', '一线城市', '新一线城市', '省会城市', '其他']
# low: 历史实际去向扩展
EXPANSION_PATHS_LOW = ['广东省内', '周边省份', '全国']


class RecommendationServiceV2:
    """V2 推荐服务 - 数据驱动"""

    def __init__(self, data_dir: Path = None, load_data: bool = True):
        self.data_dir = data_dir or Path(__file__).parent.parent.parent / 'data'
        self.records = []
        self.hotness_matrix = {}
        self.city_attraction = {}
        self.trend_data = {}
        self.cat_trends = {}

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
            print(f'[V2] Loaded {len(self.records)} records from major_rank_data.json')

        # 2. 热度矩阵
        hotness_file = self.data_dir / 'rank_hotness_matrix.json'
        if hotness_file.exists():
            with open(hotness_file, 'r', encoding='utf-8') as f:
                self.hotness_matrix = json.load(f)
            print(f'[V2] Loaded hotness matrix ({len(self.hotness_matrix.get("segments", {}))} segments)')

        # 3. 城市吸引力
        city_file = self.data_dir / 'city_attraction_index.json'
        if city_file.exists():
            with open(city_file, 'r', encoding='utf-8') as f:
                self.city_attraction = json.load(f)
            print(f'[V2] Loaded city attraction ({len(self.city_attraction.get("provinces", {}))} provinces)')

        # 4. 专业趋势
        trend_file = self.data_dir / 'major_trend_analysis.json'
        if trend_file.exists():
            with open(trend_file, 'r', encoding='utf-8') as f:
                self.trend_data = json.load(f)
            self.cat_trends = self.trend_data.get('category_trends', {})
            print(f'[V2] Loaded major trends ({len(self.trend_data.get("trends", []))} trends)')

        # 构建快速查找索引
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
                # 按 10000 位一段建立索引
                bucket = rank // 10000
                self._records_by_rank_range[bucket].append(r)

        # 构建去重后的记录列表（每个(uni, group_code)只保留最新的）
        dedup_key_rank = {}
        for r in self.records:
            if not isinstance(r, dict):
                continue
            key = (r.get('university_name', ''), r.get('group_code', ''))
            rank = r.get('min_rank', 0)
            if key[0] and key[1] and rank > 0:
                if key not in dedup_key_rank or r.get('year', 0) > dedup_key_rank[key].get('year', 0):
                    dedup_key_rank[key] = r
        self._records_deduplicated = list(dedup_key_rank.values())
        print(f'[V2] Deduplicated: {len(self._records_deduplicated)} unique (uni, group_code) combos')

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
        # 超出范围
        if user_rank < 1:
            return RANK_TIERS[0]
        return RANK_TIERS[-1]

    def _get_rank_segment_key(self, user_rank: int) -> str:
        """获取位次段键名 (每 5000 一段)"""
        seg_start = ((user_rank - 1) // 5000) * 5000 + 1
        seg_end = seg_start + 4999
        return f"{seg_start}-{seg_end}"

    # ============================================================
    # 主推荐方法
    # ============================================================
    def recommend(self, user_rank: int, province: str = "广东",
                  subject_type: str = "理科",
                  target_majors: Optional[List[str]] = None,
                  max_per_uni: int = 3,
                  min_total: int = 25,
                  verbose: bool = False) -> Dict[str, Any]:
        """
        生成推荐方案

        Returns:
            {冲刺: [...], 稳妥: [...], 保底: [...]}
            每个推荐项: {university_name, major_name, group_code, min_rank, min_score,
                          university_level, university_province, score, roi_score, ...}
        """
        tier = self._get_tier(user_rank)
        expand_pct = tier['expand_pct']

        if verbose:
            print(f'[V2] user_rank={user_rank}, tier={tier["name"]}, expand={expand_pct}')

        # 1. 候选人筛选
        candidates = self._filter_candidates(user_rank, expand_pct, province, tier)

        if verbose:
            print(f'[V2] Filtered {len(candidates)} candidates')

        # 2. 如果不够，扩圈
        if len(candidates) < min_total * 2:
            expand_stages = self._get_expansion_stages(tier, province)
            for stage_range, stage_province in expand_stages[1:]:
                candidates = self._filter_candidates(
                    user_rank, stage_range, stage_province, tier
                )
                if verbose:
                    print(f'[V2] Expanded: range={stage_range}, candidates={len(candidates)}')
                if len(candidates) >= min_total * 2:
                    break

        # 3. 去重（按 university_name + group_code）
        candidates = self._deduplicate_candidates(candidates)

        # 4. 多模型评分
        scored = self._multi_model_score(candidates, user_rank, tier, target_majors)

        # 5. 分类
        recommendations = self._categorize(scored, user_rank, max_per_uni, min_total)

        # 6. 数量补充
        total = sum(len(v) for v in recommendations.values())
        if total < min_total:
            recommendations = self._supplement(
                recommendations, user_rank, max_per_uni, min_total, tier
            )

        total_final = sum(len(v) for v in recommendations.values())
        return {
            'success': True,
            'data': recommendations,
            'user_rank': user_rank,
            'tier': tier['name'],
            'total_count': total_final
        }

    def _get_expansion_stages(self, tier: dict, province: str) -> List[Tuple[float, str]]:
        """获取扩圈阶段"""
        expand_pct = tier['expand_pct']
        name = tier['name']

        stages = [
            (expand_pct, province),  # 第一阶段: 省内
        ]

        if name in ('elite', 'high'):
            # 高分: 按学校层次扩
            stages.append((expand_pct * 1.5, 'all'))  # 全国
            stages.append((expand_pct * 2.0, 'all'))  # 更大范围
        elif name in ('upper_mid', 'mid'):
            # 中分: 按省份扩
            nearby = ['广东', '湖南', '江西', '广西', '海南', '福建', '湖北']
            stages.append((expand_pct * 1.3, 'all'))  # 全国
            stages.append((expand_pct * 1.8, 'all'))
        else:
            # 低分: 全国扩
            stages.append((expand_pct * 1.3, 'all'))
            stages.append((expand_pct * 1.8, 'all'))
            stages.append((expand_pct * 2.5, 'all'))

        return stages

    def _filter_candidates(self, user_rank: int, expand_pct: float,
                           province: str, tier: dict) -> List[dict]:
        """按位次范围和省份筛选候选人"""
        min_rank = int(user_rank * (1 - expand_pct))
        max_rank = int(user_rank * (1 + expand_pct))
        if min_rank < 1:
            min_rank = 1

        # 快速索引查找
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
                key = (r.get('university_name', ''), r.get('group_code', ''))
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
            key = (c.get('university_name', ''), c.get('group_code', ''))
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
        # 准备
        seg_key = self._get_rank_segment_key(user_rank)
        hotness_seg = self.hotness_matrix.get('segments', {}).get(seg_key, [])
        hotness_rank = {h['university_name']: i for i, h in enumerate(hotness_seg)}

        cities = self.city_attraction.get('provinces', {})
        trend_map = self._build_trend_map()

        # 目标专业
        target_keywords = self._extract_target_keywords(target_majors or [])
        local_weight = tier.get('local_weight', 1.10)

        for c in candidates:
            uni = c.get('university_name', '')
            prov = c.get('university_province', '') or ''
            group_code = str(c.get('group_code', ''))
            c_rank = c.get('min_rank', user_rank)

            # 1. 热度分 (0-1)
            hot_idx = hotness_rank.get(uni, len(hotness_seg))
            hotness_score = 1.0 - min(hot_idx / max(1, len(hotness_seg)), 1.0)

            # 2. 城市吸引力分 (0-1)
            city_info = cities.get(prov, {})
            city_score = city_info.get('attraction_score', 0.5)

            # 3. 趋势分 (0-1)
            trend_key = f"{uni}||{group_code}"
            trend_info = trend_map.get(trend_key, {})
            trend_val = trend_info.get('trend', 'unknown')
            trend_map_score = {'warming': 1.0, 'stable': 0.7, 'cooling': 0.3, 'unknown': 0.5}
            trend_score = trend_map_score.get(trend_val, 0.5)

            # 3b. 大类趋势加成
            cat_trend_bonus = 0.0
            if target_keywords:
                major_name = c.get('major_name', '')
                cat = self._classify_major(major_name)
                if cat in self.cat_trends:
                    cat_score = self.cat_trends[cat].get('trend_score', 0.5)
                    cat_trend_bonus = (cat_score - 0.5) * 0.5  # ±0.25

            # 4. 本地偏好分 (0-1)
            local_score = 0.5  # 默认
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

            # 综合得分 (加入小随机扰动以增加多样性)
            composite = (
                MODEL_WEIGHTS['hotness'] * hotness_score +
                MODEL_WEIGHTS['city'] * city_score +
                MODEL_WEIGHTS['trend'] * (trend_score + cat_trend_bonus) +
                MODEL_WEIGHTS['local'] * (local_score * local_weight) +
                MODEL_WEIGHTS['rank_fit'] * rank_fit +
                random.uniform(-0.04, 0.04)  # ±0.04 随机扰动
            )

            # 记录子分数
            c['_hotness'] = round(hotness_score, 4)
            c['_city'] = round(city_score, 4)
            c['_trend'] = round(trend_score + cat_trend_bonus, 4)
            c['_local'] = round(local_score, 4)
            c['_rank_fit'] = round(rank_fit, 4)
            c['_score'] = round(composite, 4)

        # 按综合得分降序
        candidates.sort(key=lambda x: x.get('_score', 0), reverse=True)
        return candidates

    def _build_trend_map(self) -> Dict[str, dict]:
        """构建趋势查找映射 (uni||group_code -> trend info)"""
        trend_map = {}
        for t in self.trend_data.get('trends', []):
            if isinstance(t, dict):
                key = f"{t.get('university_name', '')}||{t.get('group_code', '')}"
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
            # 同义词扩展
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
        """分类为冲刺/稳妥/保底，并做多样性后处理"""
        chongci, wenzuo, baodi = [], [], []

        for c in scored:
            c_rank = c.get('min_rank', user_rank)
            if c_rank <= 0:
                continue

            diff = (c_rank - user_rank) / max(1, user_rank)

            if diff < -0.10:
                chongci.append(c)
            elif diff <= 0.15:
                wenzuo.append(c)
            else:
                baodi.append(c)

        # 多样性选择：优先高分院校，但每轮最多取1个避免过度集中
        def diversity_select(items: List[dict], limit: int, per_uni: int) -> List[dict]:
            if not items:
                return []

            # 按大学分组，每组按分数降序排列
            uni_groups = defaultdict(list)
            for item in items:
                uni = item.get('university_name', '')
                uni_groups[uni].append(item)

            # 计算每个大学组的"最大分数"用于排序
            uni_best_score = {
                u: max(g.get('_score', 0) for g in group)
                for u, group in uni_groups.items()
            }

            # 按最大分数降序排列大学（高分大学优先）
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

                # 如果一轮后没有新项目，退出
                if all(pointer[u] >= len(uni_groups[u]) for u in uni_keys):
                    break

            return result

        per_cat = max(10, min_total // 3)
        return {
            '\u51b2\u523a': diversity_select(chongci, per_cat, max_per_uni),
            '\u7a33\u59a5': diversity_select(wenzuo, per_cat, max_per_uni),
            '\u4fdd\u5e95': diversity_select(baodi, per_cat, max_per_uni),
        }

    def _supplement(self, recommendations: Dict, user_rank: int,
                    max_per_uni: int, min_total: int, tier: dict) -> Dict:
        """补充推荐到最小数量"""
        total = sum(len(v) for v in recommendations.values())
        if total >= min_total:
            return recommendations

        needed = min_total - total
        # 扩大范围再找
        max_rank = int(user_rank * 3.0)
        min_rank = max(1, int(user_rank * 0.3))

        existing_keys = set()
        for cat in recommendations.values():
            for c in cat:
                key = (c.get('university_name', ''), c.get('group_code', ''))
                existing_keys.add(key)

        # 从已评分候选外补
        supplements = []
        for r in self.records:
            if not isinstance(r, dict):
                continue
            rk = r.get('min_rank', 0)
            if rk < min_rank or rk > max_rank:
                continue
            key = (r.get('university_name', ''), r.get('group_code', ''))
            if key in existing_keys or not key[0]:
                continue
            existing_keys.add(key)
            supplements.append(r)
            if len(supplements) >= needed:
                break

        # 补充到保底类
        recommendations['保底'] = recommendations.get('保底', []) + supplements[:needed]

        return recommendations

    # ============================================================
    # 兼容 V1 接口（用于 A/B 测试对比）
    # ============================================================
    def recommend_with_fallback(self, user_rank: int, province: str = "广东",
                                 subject_type: str = "理科",
                                 target_majors: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        兼容 V1 的 recommend_with_fallback 接口

        Returns:
            同 V1 格式: {success, data: {冲刺, 稳妥, 保底}, user_rank, total_count}
        """
        return self.recommend(
            user_rank=user_rank,
            province=province,
            subject_type=subject_type,
            target_majors=target_majors
        )


# 不自动创建全局实例（避免在 A/B 测试中重复加载）
# 使用时请自行实例化: service = RecommendationServiceV2()
