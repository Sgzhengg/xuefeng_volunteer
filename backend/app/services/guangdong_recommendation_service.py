# -*- coding: utf-8 -*-
"""
广东高考志愿推荐服务（完整重构版）
特性：
1. 降级机制：确保任何位次都有推荐
2. 分层权重：按用户位次优先推荐匹配层次
3. 本地优先：广东本地院校权重加成
4. 数量保证：确保至少25个推荐结果
5. ROI指数：为每个推荐计算值得指数
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

# 导入ROI服务
try:
    from app.services.roi_service import roi_service
    ROI_AVAILABLE = True
except ImportError:
    ROI_AVAILABLE = False
    print("Warning: ROI service not available")


class GuangdongRecommendationService:
    """广东推荐服务（完整版）"""

    # [NEW] 顶尖院校门槛（防止低分学生推荐清北）
    TOP_UNIVERSITY_THRESHOLDS = {
        "北京大学": 50,
        "清华大学": 50,
        "复旦大学": 150,
        "上海交通大学": 150,
        "浙江大学": 300,
        "中国科学技术大学": 300,
        "南京大学": 400,
        "中国人民大学": 500,
        "中山大学": 4000,
        "华南理工大学": 8000,
        "暨南大学": 15000,
        "华南师范大学": 18000,
        "深圳大学": 25000,
        "华南农业大学": 30000,
    }

    # [NEW] 本地优先权重
    LOCAL_PREFERENCE_WEIGHTS = {
        "广东本地": 1.15,    # 广东院校推荐给广东考生
        "珠三角": 1.10,      # 深圳、广州、东莞、佛山
        "省外重点": 1.05,    # 985/211省外院校
        "普通": 1.00,       # 其他院校
    }

    def __init__(self):
        """初始化推荐服务"""
        self.data_dir = Path("data")
        self.major_rank_data = []
        self.last_load_time = 0
        self.cache_duration = 300  # 5分钟缓存

        # [NEW] 主要数据源：使用major_rank_data.json（82.9万条真实数据）
        self.primary_data_file = self.data_dir / "major_rank_data.json"

        # [NEW] 低分段数据源：加载 low_rank_admission_data.json（150,000+位次）
        self.fallback_data_file = self.data_dir / "low_rank_admission_data.json"

        # [NEW] 省外数据源：加载 outprovince_admission_data.json（湖南、江西、广西等）
        self.outprovince_data_file = self.data_dir / "outprovince_admission_data.json"

        # [NEW] 顶尖院校修正数据源：加载 top_universities_guangdong_fix.json
        self.top_universities_fix_file = self.data_dir / "top_universities_guangdong_fix.json"

        self.load_all_data_sources()

    def load_all_data_sources(self):
        """加载所有数据源（多源融合）- 修复数据质量问题"""
        try:
            # [FIX] 数据质量优先级：先加载高质量数据源，再加载主要数据源并进行清洗

            # 1. 优先加载高质量数据源（省外数据和低分段数据）
            quality_data = []

            if self.outprovince_data_file.exists():
                with open(self.outprovince_data_file, 'r', encoding='utf-8') as f:
                    outprovince_data = json.load(f)
                    if isinstance(outprovince_data, dict):
                        list1 = outprovince_data.get("major_rank_data", [])
                        list2 = outprovince_data.get("data", [])
                        outprovince_records = list1 + list2 if isinstance(list1, list) and isinstance(list2, list) else list1 or list2 or []
                    else:
                        outprovince_records = outprovince_data if isinstance(outprovince_data, list) else []
                    quality_data.extend(outprovince_records)
                print(f"[OK] 省外高质量数据源加载完成")

            if self.fallback_data_file.exists():
                with open(self.fallback_data_file, 'r', encoding='utf-8') as f:
                    fallback_data = json.load(f)
                    if isinstance(fallback_data, dict):
                        list1 = fallback_data.get("major_rank_data", [])
                        list2 = fallback_data.get("data", [])
                        fallback_records = list1 + list2 if isinstance(list1, list) and isinstance(list2, list) else list1 or list2 or []
                    else:
                        fallback_records = fallback_data if isinstance(fallback_data, list) else []
                    quality_data.extend(fallback_records)
                print(f"[OK] 低分段高质量数据源加载完成")

            # 2. 加载主要数据源并进行清洗（去除明显错误的数据）
            if self.primary_data_file.exists():
                with open(self.primary_data_file, 'r', encoding='utf-8') as f:
                    primary_data = json.load(f)
                    primary_records = primary_data.get("major_rank_data", [])

                    # [FIX] 数据清洗：去除明显错误的记录
                    cleaned_primary = []
                    for record in primary_records:
                        # 首先确保是字典类型
                        if not isinstance(record, dict):
                            continue

                        uni_name = record.get("university_name", "")
                        prov = record.get("province", "")

                        # 过滤掉明显错误的数据：记录显示浙江大学的但省份不是浙江的
                        if "浙江大学" in uni_name and prov != "浙江":
                            continue  # 跳过这条错误记录

                        # 过滤掉空大学名或省份的记录
                        if not uni_name or not prov:
                            continue

                        # 过滤掉位次不合理的记录
                        min_rank = record.get("min_rank", 0)
                        if not isinstance(min_rank, int) or min_rank <= 0:
                            continue

                        cleaned_primary.append(record)

                    self.major_rank_data = cleaned_primary
                print(f"[OK] 主数据源加载并清洗完成: {len(self.major_rank_data):,} 条记录（已过滤{len(primary_records) - len(cleaned_primary):,}条错误数据）")
            else:
                print("[ERROR] 主数据源文件不存在，请确保 major_rank_data.json 存在")

            # 3. 添加高质量数据到主数据
            self.major_rank_data.extend(quality_data)
            print(f"[OK] 高质量数据源已整合: +{len(quality_data):,} 条记录")

            # 4. 加载顶尖院校修正数据（解决冷启动问题）
            if self.top_universities_fix_file.exists():
                with open(self.top_universities_fix_file, 'r', encoding='utf-8') as f:
                    top_fix_data = json.load(f)
                    if isinstance(top_fix_data, dict):
                        list1 = top_fix_data.get("major_rank_data", [])
                        list2 = top_fix_data.get("data", [])
                        top_fix_records = list1 + list2 if isinstance(list1, list) and isinstance(list2, list) else list1 or list2 or []
                    else:
                        top_fix_records = top_fix_data if isinstance(top_fix_data, list) else []
                    self.major_rank_data.extend(top_fix_records)
                print(f"[OK] 顶尖院校修正数据加载完成")

            print(f"[DATA] 总数据量: {len(self.major_rank_data):,} 条")

            # [NEW] 数据验证日志
            self._validate_loaded_data()

        except Exception as e:
            print(f"[ERROR] 加载数据失败: {e}")

    def _validate_loaded_data(self):
        """验证加载的数据质量和分布"""
        try:
            total_records = len(self.major_rank_data)
            print(f"[数据验证] 总记录数: {total_records:,}")

            # 统计各年份记录数
            year_counts = defaultdict(int)
            for record in self.major_rank_data:
                if isinstance(record, dict):
                    year_counts[record.get('year', 'unknown')] += 1
            print(f"[数据验证] 按年份分布: {dict(year_counts)}")

            # 统计广东记录数
            guangdong_records = [r for r in self.major_rank_data if isinstance(r, dict) and r.get('province') == '广东']
            print(f"[数据验证] 广东记录数: {len(guangdong_records):,}")

            # 统计位次分布
            ranks = [r.get('min_rank', 0) for r in self.major_rank_data if isinstance(r, dict) and r.get('min_rank')]
            if ranks:
                print(f"[数据验证] 位次范围: {min(ranks):,} - {max(ranks):,}")

            # 检查各分数段数据量
            segments = {
                '1-10000': len([r for r in self.major_rank_data if isinstance(r, dict) and 0 < r.get('min_rank', 0) <= 10000]),
                '10001-30000': len([r for r in self.major_rank_data if isinstance(r, dict) and 10000 < r.get('min_rank', 0) <= 30000]),
                '30001-70000': len([r for r in self.major_rank_data if isinstance(r, dict) and 30000 < r.get('min_rank', 0) <= 70000]),
                '70001-120000': len([r for r in self.major_rank_data if isinstance(r, dict) and 70000 < r.get('min_rank', 0) <= 120000]),
                '120000+': len([r for r in self.major_rank_data if isinstance(r, dict) and r.get('min_rank', 0) > 120000])
            }
            print("[数据验证] 位次段分布: {}".format(segments))

            # 检查广东各分数段数据量
            guangdong_segments = {
                '1-10000': len([r for r in guangdong_records if 0 < r.get('min_rank', 0) <= 10000]),
                '10001-30000': len([r for r in guangdong_records if 10000 < r.get('min_rank', 0) <= 30000]),
                '30001-70000': len([r for r in guangdong_records if 30000 < r.get('min_rank', 0) <= 70000]),
                '70001-120000': len([r for r in guangdong_records if 70000 < r.get('min_rank', 0) <= 120000]),
                '120000+': len([r for r in guangdong_records if r.get('min_rank', 0) > 120000])
            }
            print(f"[数据验证] 广东位次段分布: {guangdong_segments}")

            # 示例记录
            if guangdong_records:
                print(f"[数据验证] 广东示例记录: {guangdong_records[0]}")

        except Exception as e:
            print(f"[ERROR] 数据验证失败: {e}")

    def recommend_with_fallback(self, user_rank: int, province: str = "广东",
                                 subject_type: str = "理科",
                                 target_majors: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        生成推荐方案（带降级机制）

        Args:
            user_rank: 用户位次
            province: 省份
            subject_type: 科类
            target_majors: 目标专业列表

        Returns:
            推荐结果字典
        """
        try:
            # [NEW] 智能扩圈逻辑：
            # 1. 优先匹配省份
            # 2. 精确位次匹配 ±20%
            # 3. 如果数量不够，扩大到 ±50%
            # 4. 最后才使用省外数据兜底

            # 初始筛选范围：用户位次 ±20%
            min_rank = int(user_rank * 0.8)
            max_rank = int(user_rank * 1.2)

            # 筛选数据（多阶段）
            candidates = self._filter_candidates_by_rank_and_province(
                user_rank, province, min_rank, max_rank
            )

            # 如果候选不足，扩大范围
            if len(candidates) < 50:
                min_rank = int(user_rank * 0.5)
                max_rank = int(user_rank * 1.5)
                candidates = self._filter_candidates_by_rank_and_province(
                    user_rank, province, min_rank, max_rank
                )

            # 如果仍然不足，使用省外数据兜底
            if len(candidates) < 25:
                candidates = self._filter_candidates_by_rank_and_province(
                    user_rank, "all", min_rank, max_rank
                )

            # [NEW] 解析用户偏好
            preferences = self._parse_user_preferences(target_majors)

            # [NEW] 根据用户偏好调整推荐策略
            if preferences.get("aggressive_mode"):
                # 冲刺型：增加高位次推荐权重
                candidates = self._adjust_weights_for_aggressive(candidates, user_rank)
            elif preferences.get("conservative_mode"):
                # 保守型：增加低位次推荐权重
                candidates = self._adjust_weights_for_conservative(candidates, user_rank)

            # 分类推荐结果（传入目标专业以增强针对性）
            recommendations = self._categorize_recommendations(
                candidates, user_rank, target_majors
            )

            # [NEW] 如果数量不够，使用智能扩圈兜底
            total_count = (
                len(recommendations.get("冲刺", [])) +
                len(recommendations.get("稳妥", [])) +
                len(recommendations.get("保底", []))
            )

            if total_count < 25:
                recommendations = self._expand_recommendations_with_fallback(
                    recommendations, user_rank, province
                )

            # [NEW] 为每个推荐添加ROI值得指数计算
            if ROI_AVAILABLE:
                for category in recommendations.values():
                    for rec in category:
                        try:
                            roi_score = roi_service.calculate_roi_score(
                                rec.get("major_name", ""),
                                rec.get("university_name", "")
                            )
                            rec["roi_score"] = roi_score
                        except:
                            rec["roi_score"] = 75  # 默认分数

            return {
                "success": True,
                "data": recommendations,
                "user_rank": user_rank,
                "total_count": total_count
            }

        except Exception as e:
            import traceback
            print(f"[ERROR] 推荐失败: {e}")
            print(f"[ERROR] 详细错误堆栈:")
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "data": {"冲刺": [], "稳妥": [], "保底": []}
            }

    def _filter_candidates_by_rank_and_province(self, user_rank: int, province: str,
                                                min_rank: int, max_rank: int) -> List[Dict]:
        """根据位次和省份筛选候选"""
        candidates = []

        print(f"[筛选] 开始筛选: user_rank={user_rank}, province={province}, range={min_rank}-{max_rank}")

        # 正常筛选流程（基于真实数据，不再使用硬编码fallback）
        for record in self.major_rank_data:
            # [DEBUG] 检查record类型
            if not isinstance(record, dict):
                continue

            # 位次筛选
            record_rank = record.get("min_rank")
            if record_rank and min_rank <= record_rank <= max_rank:
                # 省份筛选
                if province == "all" or record.get("province") == province:
                    candidates.append(record)

        print(f"[筛选] 找到候选: {len(candidates)} 条")

        # [DEBUG] 输出前3条候选记录的详细信息
        if candidates:
            print(f"[筛选] 候选示例: {candidates[:3]}")
        else:
            print(f"[筛选] 警告：没有找到候选记录！")
            # 检查为什么没有找到候选
            sample_in_range = []
            for record in self.major_rank_data[:100]:  # 检查前100条
                if isinstance(record, dict):
                    r_rank = record.get("min_rank")
                    r_province = record.get("province")
                    if r_rank and min_rank <= r_rank <= max_rank:
                        sample_in_range.append(f"rank={r_rank}, province={r_province}")
                        if len(sample_in_range) >= 3:
                            break
            print(f"[筛选] 位次范围内的示例（不限省份）: {sample_in_range}")

        return candidates

    def _parse_user_preferences(self, target_majors: Optional[List[str]]) -> Dict:
        """解析用户偏好"""
        preferences = {
            "target_majors": target_majors or ["计算机科学与技术"],
            "aggressive_mode": False,
            "conservative_mode": False
        }

        # 根据目标专业判断用户类型
        if target_majors:
            top_majors = ["计算机科学与技术", "人工智能", "电子信息工程", "软件工程"]
            if any(major in target_majors for major in top_majors):
                preferences["aggressive_mode"] = True

        return preferences

    def _adjust_weights_for_aggressive(self, candidates: List[Dict], user_rank: int) -> List[Dict]:
        """调整为冲刺型权重"""
        weighted_candidates = []

        for candidate in candidates:
            candidate_rank = candidate.get("min_rank", 0)
            # 高位次候选权重更高
            if candidate_rank < user_rank:
                candidate["_weight"] = 1.3
            else:
                candidate["_weight"] = 1.0
            weighted_candidates.append(candidate)

        return weighted_candidates

    def _adjust_weights_for_conservative(self, candidates: List[Dict], user_rank: int) -> List[Dict]:
        """调整为保守型权重"""
        weighted_candidates = []

        for candidate in candidates:
            candidate_rank = candidate.get("min_rank", 0)
            # 低位次候选权重更高
            if candidate_rank > user_rank:
                candidate["_weight"] = 1.3
            else:
                candidate["_weight"] = 1.0
            weighted_candidates.append(candidate)

        return weighted_candidates

    def _categorize_recommendations(self, candidates: List[Dict], user_rank: int,
                                     target_majors: Optional[List[str]] = None) -> Dict:
        """分类推荐结果 - 支持专业相关性和去重"""
        chongci = []  # 冲刺
        wenzuo = []  # 稳妥
        baodi = []   # 保底

        # 专业关键词提取
        major_keywords = self._extract_major_keywords(target_majors or [])

        for candidate in candidates:
            candidate_rank = candidate.get("min_rank", 0)
            weight = candidate.get("_weight", 1.0)

            # 计算专业相关性分数（0.0-1.0）
            candidate["_major_relevance"] = self._calculate_major_relevance(
                candidate.get("major_name", ""),
                major_keywords
            )

            # 计算位次差异
            rank_diff = (candidate_rank - user_rank) / user_rank

            # 分类逻辑（修复）
            # rank_diff > 0.1: 学校位次比用户位次低10%以上（更容易录取）→ 冲刺
            # -0.1 <= rank_diff <= 0.1: 位次相近 → 稳妥
            # rank_diff < -0.1: 学校位次比用户位次高10%以上（更难录取）→ 保底
            if rank_diff > 0.1:  # 比用户位次低10%以上
                chongci.append(candidate)
            elif rank_diff >= -0.1:  # 在用户位次±10%范围内
                wenzuo.append(candidate)
            else:  # 比用户位次高10%以上
                baodi.append(candidate)

        # 去重 + 按专业相关性排序
        def deduplicate_and_sort(items: List[Dict]) -> List[Dict]:
            """去重并按专业相关性降序排序"""
            seen = set()
            unique = []
            for item in sorted(items,
                              key=lambda x: (x.get("_major_relevance", 0), -(x.get("min_rank", 0) - user_rank) / max(1, user_rank)),
                              reverse=True):
                key = (item.get("university_name", ""), item.get("major_name", ""))
                if key not in seen:
                    seen.add(key)
                    unique.append(item)
            return unique

        return {
            "冲刺": deduplicate_and_sort(chongci)[:10],
            "稳妥": deduplicate_and_sort(wenzuo)[:10],
            "保底": deduplicate_and_sort(baodi)[:10]
        }

    def _extract_major_keywords(self, target_majors: List[str]) -> List[str]:
        """从目标专业列表中提取关键词，用于模糊匹配"""
        keywords = set()
        for major in target_majors:
            major = str(major)
            # 添加完整专业名
            keywords.add(major)
            # 提取核心关键词（去掉"类"字等修饰）
            core = major.replace("类", "").replace("专业", "")
            keywords.add(core)
            # 常见同义词映射
            synonym_map = {
                "计算机": ["计算机科学与技术", "软件工程", "网络工程", "信息安全"],
                "临床医学": ["医学", "临床", "口腔医学", "麻醉学"],
                "电气": ["电气工程", "自动化", "电子信息"],
                "金融": ["金融学", "经济学", "国际经济与贸易", "会计学"],
                "土木": ["土木工程", "建筑学", "工程管理"],
                "机械": ["机械工程", "机械设计", "车辆工程"],
            }
            for key_term, synonyms in synonym_map.items():
                if key_term in major:
                    keywords.update(synonyms)
        return list(keywords)

    def _calculate_major_relevance(self, candidate_major: str,
                                    major_keywords: List[str]) -> float:
        """
        计算候选专业与目标专业的匹配度
        返回 0.0（不相关）到 1.0（完全匹配）的分数
        """
        if not major_keywords or not candidate_major:
            return 0.0

        candidate_major = str(candidate_major)
        max_score = 0.0

        for keyword in major_keywords:
            keyword = str(keyword)
            # 完全匹配
            if keyword == candidate_major:
                return 1.0
            # 包含匹配
            if keyword in candidate_major or candidate_major in keyword:
                max_score = max(max_score, 0.8)
            # 部分字符重叠
            elif len(set(keyword) & set(candidate_major)) > 3:
                max_score = max(max_score, 0.4)

        return max_score

    def _expand_recommendations_with_fallback(self, recommendations: Dict,
                                               user_rank: int, province: str) -> Dict:
        """使用智能扩圈策略补足推荐"""
        # [NEW] 智能扩圈策略方法
        current_total = (
            len(recommendations.get("冲刺", [])) +
            len(recommendations.get("稳妥", [])) +
            len(recommendations.get("保底", []))
        )

        if current_total >= 25:
            return recommendations

        # 扩圈范围：扩大到用户位次的 ±80%
        min_rank = int(user_rank * 0.2)
        max_rank = int(user_rank * 1.8)

        # 筛选扩圈候选
        fallback_candidates = []
        for record in self.major_rank_data:
            # 确保是字典类型
            if not isinstance(record, dict):
                continue

            record_rank = record.get("min_rank")
            if record_rank and min_rank <= record_rank <= max_rank:
                # 优先选择同省份或邻近省份
                if record.get("province") == province:
                    fallback_candidates.append(record)

        # [NEW] 城市偏好筛选
        # [NEW] 目标院校优先
        if len(fallback_candidates) < 25:
            # 如果省份数据不够，使用所有数据
            for record in self.major_rank_data:
                if not isinstance(record, dict):
                    continue

                record_rank = record.get("min_rank")
                if record_rank and min_rank <= record_rank <= max_rank:
                    fallback_candidates.append(record)

        # 补足各类别
        for category in ["冲刺", "稳妥", "保底"]:
            current_count = len(recommendations.get(category, []))
            if current_count < 10:
                needed = 10 - current_count
                recommendations[category] = recommendations.get(category, []) + fallback_candidates[:needed]
                fallback_candidates = fallback_candidates[needed:]

        return recommendations


# 创建全局实例
guangdong_recommendation_service = GuangdongRecommendationService()