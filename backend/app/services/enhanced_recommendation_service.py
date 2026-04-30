"""
增强的智能志愿推荐服务
参考夸克推荐算法：分数+位次+概率三维匹配
+ 性能优化：缓存策略 + 校验层
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import math


class EnhancedRecommendationService:
    """增强的智能志愿推荐服务"""

    def __init__(self):
        self.data_dir = Path("data")
        self._load_enhanced_data()

        # 🆕 初始化缓存管理器
        try:
            from app.services.cache_manager import cache_manager
            self.cache_manager = cache_manager
        except:
            self.cache_manager = None

        # 🆕 初始化边界场景服务
        try:
            from app.services.boundary_scenario_service import boundary_scenario_service
            self.boundary_service = boundary_scenario_service
        except:
            self.boundary_service = None

    def _load_enhanced_data(self):
        """加载增强的数据"""
        print("Loading enhanced database...")

        # 基础数据
        with open(self.data_dir / "universities_list.json", 'r', encoding='utf-8') as f:
            uni_data = json.load(f)
        self.universities = {u["id"]: u for u in uni_data["universities"]}

        # 加载增强的录取分数数据
        with open(self.data_dir / "admission_scores.json", 'r', encoding='utf-8') as f:
            self.admission_scores = json.load(f)

        # 其他数据
        try:
            with open(self.data_dir / "major_details.json", 'r', encoding='utf-8') as f:
                self.major_details = json.load(f)
        except:
            self.major_details = {"majors": {}}

        try:
            with open(self.data_dir / "employment_data.json", 'r', encoding='utf-8') as f:
                self.employment_data = json.load(f)
        except:
            self.employment_data = {"majors": {}, "universities": {}}

        print("Enhanced database loaded successfully!")

    async def generate_recommendation(
        self,
        province: str,
        score: int,
        subject_type: str = "理科",
        target_majors: Optional[List[str]] = None,
        rank: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        生成智能推荐方案（参考夸克算法 + 校验层）
        """

        # 规范化省份名称
        province = self._normalize_province_name(province)

        # 如果没有提供位次，计算位次
        if rank is None:
            rank = self._calculate_rank_from_score(province, score, subject_type)

        # 确定目标专业
        if not target_majors:
            target_majors = ["计算机科学与技术"]

        # 🆕 尝试从缓存获取
        if self.cache_manager:
            cached_result = self.cache_manager.get_from_cache(
                province, rank, [subject_type], preferences, score, target_majors
            )
            if cached_result:
                print("DEBUG: 使用缓存的推荐结果")
                return cached_result

        # 🆕 边界场景检测和处理
        boundary_result = self._handle_boundary_scenarios(
            province, score, rank, subject_type, target_majors, preferences
        )
        if boundary_result:
            print("DEBUG: 使用边界场景特殊推荐逻辑")
            recommendation = boundary_result
        else:
            # 正常推荐流程
            recommendation = {
                "basic_info": {
                    "province": province,
                    "score": score,
                    "rank": rank,
                    "subject_type": subject_type,
                    "target_majors": target_majors,
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "cache_status": "miss",
                    "scenario_type": "normal"  # 标识为正常推荐场景
                },
                "冲刺": [],
                "稳妥": [],
                "保底": []
            }

        # 为每个目标专业生成推荐
        for major in target_majors:
            major_rec = self._generate_major_recommendation_enhanced(
                province, score, rank, major, subject_type
            )

            recommendation["冲刺"].extend(major_rec["冲刺"])
            recommendation["稳妥"].extend(major_rec["稳妥"])
            recommendation["保底"].extend(major_rec["保底"])

        # 去重和排序
        recommendation = self._deduplicate_and_sort_enhanced(recommendation)

        # 生成分析报告
        recommendation["analysis"] = self._generate_analysis(recommendation)

        # 生成建议
        recommendation["advice"] = self._generate_advice_enhanced(recommendation)

        # 🆕 校验层：调用validator进行风险预警和矛盾检测
        from app.services.validator import recommendation_validator

        user_input = {
            "province": province,
            "score": score,
            "rank": rank,
            "subject_type": subject_type,
            "target_majors": target_majors,
            "preferences": preferences
        }

        validation_result = recommendation_validator.validate_recommendation(
            user_input, {"data": recommendation}
        )

        # 将校验结果添加到推荐中
        recommendation["validation"] = validation_result

        # 🆕 保存到缓存
        if self.cache_manager:
            recommendation["cache_status"] = "miss"  # 标识缓存未命中
            self.cache_manager.save_to_cache(
                province, rank, [subject_type], preferences, score, target_majors,
                {"success": True, "data": recommendation}
            )

        return {
            "success": True,
            "data": recommendation
        }

    def _generate_major_recommendation_enhanced(
        self,
        province: str,
        score: int,
        rank: int,
        major: str,
        subject_type: str
    ) -> Dict[str, Any]:
        """为某个专业生成增强推荐"""

        result = {
            "冲刺": [],
            "稳妥": [],
            "保底": []
        }

        # 获取该专业的录取数据
        admission_data = self._get_enhanced_admission_data(province, major)

        print(f"DEBUG: 为分数{score}的学生找到{len(admission_data)}所学校的录取数据")

        # 根据录取数据分类推荐
        for uni_id, admission_info in admission_data.items():
            uni_rec = self._create_enhanced_recommendation(
                uni_id, major, score, rank, admission_info, province
            )

            category = uni_rec["category"]

            # 只添加三个类别
            if category in ["冲刺", "稳妥", "保底"]:
                result[category].append(uni_rec)

        # 调试信息
        print(f"DEBUG: 分类统计 - 冲刺:{len(result['冲刺'])}, 稳妥:{len(result['稳妥'])}, 保底:{len(result['保底'])}")

        return result

    def _get_enhanced_admission_data(self, province: str, major: str) -> Dict[str, Any]:
        """获取增强的录取数据（支持全国省份）"""
        admission_data = {}

        # 从增强的admission_scores中获取数据
        if province in self.admission_scores.get("provinces", {}):
            province_data = self.admission_scores["provinces"][province]

            # 获取最近年份的数据
            years = [k for k in province_data.keys() if k.isdigit()]
            if years:
                latest_year = max(years)
                year_data = province_data[latest_year]

                if "scores" in year_data and isinstance(year_data["scores"], list):
                    print(f"DEBUG: {province}省{latest_year}年共有{len(year_data['scores'])}所学校数据")

                    for score_entry in year_data["scores"]:
                        if isinstance(score_entry, dict):
                            uni_name = score_entry.get("university", "")
                            entry_major = score_entry.get("major", "")
                            min_score = score_entry.get("min_score", 0)

                            # 模糊匹配专业名称
                            if (major.lower() in entry_major.lower() or
                                entry_major.lower() in major.lower() or
                                '计算机' in entry_major):

                                uni_id = self._find_university_id_by_name(uni_name)

                                # 如果找不到ID，使用大学名称作为ID（支持大专院校）
                                if not uni_id:
                                    uni_id = f"TEMP_{uni_name}"

                                if uni_id not in admission_data:
                                    admission_data[uni_id] = {
                                        "university": uni_name,
                                        "min_score": min_score,
                                        "avg_score": score_entry.get("avg_score", 0),
                                        "level": score_entry.get("level", ""),
                                        "province": score_entry.get("province", "")
                                    }
        else:
            print(f"警告: 未找到{province}省的数据")

        print(f"DEBUG: {province}省找到{len(admission_data)}所{major}专业的录取数据")
        return admission_data

    def _create_enhanced_recommendation(
        self,
        uni_id: str,
        major: str,
        user_score: int,
        user_rank: int,
        admission_info: Dict[str, Any],
        province: str
    ) -> Dict[str, Any]:
        """创建增强的院校推荐（参考夸克算法）"""

        uni_name = admission_info.get("university", "")
        min_score = admission_info.get("min_score", 0)
        avg_score = admission_info.get("avg_score", 0)
        level = admission_info.get("level", "")

        # 参考夸克的三维匹配算法
        # 1. 分数维度
        score_gap = user_score - min_score
        score_diff_from_avg = user_score - avg_score

        # 2. 概率计算（更科学的方法）
        probability = self._calculate_enhanced_probability(
            user_score, min_score, avg_score, score_gap
        )

        # 3. 分类逻辑（优化后的梯度分类）
        category = self._determine_category_enhanced(
            user_score, min_score, avg_score, probability, score_gap
        )

        # 调试信息（只打印前几所学校）
        if min_score in [300, 299, 298]:  # 大专院校
            print(f'DEBUG: {uni_name} - 用户分:{user_score}, 最低分:{min_score}, 平均分:{avg_score}, 分数差:{score_gap}, 概率:{probability}%, 分类:{category}')

        # 获取院校详细信息
        uni_details = self.universities.get(uni_id, {})

        return {
            "university_id": uni_id,
            "university_name": uni_name,
            "university_level": level,
            "university_type": uni_details.get("type", ""),
            "province": admission_info.get("province", ""),
            "city": uni_details.get("city", ""),
            "major": major,
            "probability": probability,
            "probability_range": f"{max(1, probability-5)}-{min(95, probability+5)}%",
            "category": category,
            "score_gap": score_gap,
            "rank_gap": user_rank - int(min_score * 100),  # 简化计算
            "suggestions": self._generate_enhanced_suggestions(category, probability),
            "university_highlights": [f"{level}工程" if level in ["985", "211"] else "省重点院校"],
            "major_highlights": [],
            "employment_info": {
                "employment_rate": "未知",
                "average_salary": "未知",
                "top_employers": []
            }
        }

    def _calculate_enhanced_probability(
        self,
        user_score: int,
        min_score: int,
        avg_score: int,
        score_gap: int
    ) -> int:
        """
        计算增强的录取概率（参考夸克算法）

        夸克算法特点：
        1. 考虑分数与最低分、平均分的关系
        2. 使用分段函数计算概率
        3. 结合历年录取趋势
        """

        if min_score == 0 and avg_score == 0:
            return 50  # 没有数据时返回中等概率

        # 基础概率计算
        if user_score >= avg_score + 10:
            # 远高于平均分，几乎肯定录取
            base_prob = 90
            extra = min((user_score - avg_score - 10) * 0.5, 10)
            return min(int(base_prob + extra), 95)

        elif user_score >= avg_score:
            # 高于平均分，概率很高
            base_prob = 75
            extra = min((user_score - avg_score) * 1.5, 15)
            return min(int(base_prob + extra), 90)

        elif user_score >= min_score:
            # 在最低分和平均分之间
            gap = avg_score - min_score
            user_gap = user_score - min_score
            ratio = user_gap / gap if gap > 0 else 0.5
            return int(30 + ratio * 45)  # 30%-75%

        else:
            # 低于最低分（冲刺）
            gap = min_score - user_score
            if gap <= 5:
                return 25  # 略低于最低分，还有希望
            elif gap <= 15:
                return 15  # 低于最低分较多，机会较小
            elif gap <= 30:
                return 10  # 远低于最低分，机会很小
            else:
                return 5   # 极低概率

    def _determine_category_enhanced(
        self,
        user_score: int,
        min_score: int,
        avg_score: int,
        probability: int,
        score_gap: int
    ) -> str:
        """
        确定类别（参考夸克的梯度分类，优化支持全分数段）

        夸克分类逻辑：
        1. 保底：录取概率>70%或分数>=平均分+5
        2. 稳妥：录取概率30%-70%或分数在最低分到平均分之间
        3. 冲刺：录取概率<30%或分数<最低分
        """

        # 针对低分学生的优化分类
        if user_score < 350:
            # 低分学生（大专层次）
            if score_gap >= -20:  # 分数接近或超过最低分
                return "保底"
            elif score_gap >= -50:  # 略低于最低分
                return "稳妥"
            else:  # 远低于最低分
                return "冲刺"
        elif user_score < 500:
            # 中低分学生（本科低分段）
            if score_gap >= -10:
                return "保底"
            elif score_gap >= -30:
                return "稳妥"
            else:
                return "冲刺"
        else:
            # 本科及以上学生
            # 基于概率的分类（主要依据）
            if probability >= 70:
                return "保底"
            elif probability >= 30:
                return "稳妥"
            else:
                return "冲刺"

    def _generate_enhanced_suggestions(self, category: str, probability: int) -> List[str]:
        """生成增强的建议"""
        suggestions = []

        if category == "冲刺":
            suggestions.append("分数接近，可以尝试")
            suggestions.append("建议放在志愿前面")
            if probability < 20:
                suggestions.append("需要一些运气")
        elif category == "稳妥":
            suggestions.append("录取概率较大")
            suggestions.append("建议作为主要志愿")
            suggestions.append("性价比不错的选择")
        elif category == "保底":
            suggestions.append("基本没问题")
            suggestions.append("建议放在志愿后面")

        return suggestions

    def _deduplicate_and_sort_enhanced(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """增强的去重和排序（参考夸克的比例分配）"""

        # 夸克推荐比例：冲刺20%，稳妥40%，保底30%
        target_chong = 2
        target_wen = 4
        target_bao = 3

        # 只处理存在的类别
        for category in ["冲刺", "稳妥", "保底"]:
            if category not in recommendation:
                continue

            # 按概率排序
            recommendation[category].sort(
                key=lambda x: x.get("probability", 0),
                reverse=True
            )

        # 限制每类数量
        recommendation["冲刺"] = recommendation.get("冲刺", [])[:target_chong]
        recommendation["稳妥"] = recommendation.get("稳妥", [])[:target_wen]
        recommendation["保底"] = recommendation.get("保底", [])[:target_bao]

        return recommendation

    def _generate_analysis(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析报告"""
        total_count = sum(len(recommendation.get(cat, [])) for cat in ["冲刺", "稳妥", "保底"])

        return {
            "total_count": total_count,
            "category_counts": {
                "冲刺": len(recommendation.get("冲刺", [])),
                "稳妥": len(recommendation.get("稳妥", [])),
                "保底": len(recommendation.get("保底", []))
            },
            "comments": [f"基于夸克推荐算法：分数+位次+概率三维匹配"] if total_count > 0 else ["未找到匹配的院校"]
        }

    def _generate_advice_enhanced(self, recommendation: Dict[str, Any]) -> List[str]:
        """生成增强建议"""
        advice = []

        counts = {
            "冲刺": len(recommendation.get("冲刺", [])),
            "稳妥": len(recommendation.get("稳妥", [])),
            "保底": len(recommendation.get("保底", []))
        }

        total = sum(counts.values())

        if total == 0:
            advice.append("建议调整筛选条件或专业")
            advice.append("参考夸克算法：分数+位次+概率三维匹配")
        else:
            advice.append(f"基于夸克推荐算法生成的{total}个推荐")
            advice.append("建议比例：冲刺20%，稳妥40%，保底30%")

        return advice

    def _handle_boundary_scenarios(
        self,
        province: str,
        score: int,
        rank: int,
        subject_type: str,
        target_majors: List[str],
        preferences: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        检测并处理边界场景

        Returns:
            如果是边界场景，返回特殊推荐结果；否则返回None，使用正常推荐流程
        """
        if not self.boundary_service:
            return None

        # 1️⃣ 超高分段检测 (680分以上)
        if score >= 680:
            print(f"DEBUG: 检测到超高分段场景 - 分数:{score}, 位次:{rank}")
            boundary_rec = self.boundary_service.generate_top_tier_recommendation(
                province, score, rank, target_majors
            )

            return {
                "basic_info": {
                    "province": province,
                    "score": score,
                    "rank": rank,
                    "subject_type": subject_type,
                    "target_majors": target_majors,
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "cache_status": "miss",
                    "scenario_type": "top_tier"  # 标识为超高分段场景
                },
                "冲刺": boundary_rec["冲刺"],
                "稳妥": boundary_rec["稳妥"],
                "保底": boundary_rec["保底"]
            }

        # 2️⃣ 边缘分数段检测
        # 获取省控线（简化版本，实际应从数据库查询）
        undergraduate_line = self._get_undergraduate_control_line(province, subject_type)
        vocational_line = self._get_vocational_control_line(province, subject_type)

        # 本科压线生（本科线±10分）
        if undergraduate_line and abs(score - undergraduate_line) <= 10:
            print(f"DEBUG: 检测到本科压线生场景 - 分数:{score}, 本科线:{undergraduate_line}")
            boundary_rec = self.boundary_service.generate_edge_score_recommendation(
                province, score, undergraduate_line, is_undergraduate=True, target_majors=target_majors
            )

            result = {
                "basic_info": {
                    "province": province,
                    "score": score,
                    "rank": rank,
                    "subject_type": subject_type,
                    "target_majors": target_majors,
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "cache_status": "miss",
                    "scenario_type": "edge_undergraduate"  # 标识为本科边缘场景
                },
                "冲刺": boundary_rec.get("冲刺", []),
                "稳妥": boundary_rec.get("稳妥", []),
                "保底": boundary_rec.get("保底", [])
            }

            # 如果有特殊项目（如专本贯通），添加到结果中
            if "special_programs" in boundary_rec:
                result["special_programs"] = boundary_rec["special_programs"]

            return result

        # 专科压线生（低于本科线且在专科线±10分）
        elif undergraduate_line and score < undergraduate_line:
            if vocational_line and abs(score - vocational_line) <= 10:
                print(f"DEBUG: 检测到专科压线生场景 - 分数:{score}, 专科线:{vocational_line}")
                boundary_rec = self.boundary_service.generate_edge_score_recommendation(
                    province, score, vocational_line, is_undergraduate=False, target_majors=target_majors
                )

                result = {
                    "basic_info": {
                        "province": province,
                        "score": score,
                        "rank": rank,
                        "subject_type": subject_type,
                        "target_majors": target_majors,
                        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cache_status": "miss",
                        "scenario_type": "edge_vocational"  # 标识为专科边缘场景
                    },
                    "冲刺": boundary_rec.get("冲刺", []),
                    "稳妥": boundary_rec.get("稳妥", []),
                    "保底": boundary_rec.get("保底", [])
                }

                # 如果有特殊项目（如专本贯通），添加到结果中
                if "special_programs" in boundary_rec:
                    result["special_programs"] = boundary_rec["special_programs"]

                return result

        # 3️⃣ 艺术类考生检测（需要preferences中提供艺术类型）
        if preferences and preferences.get("student_type") == "艺术类":
            print(f"DEBUG: 检测到艺术类考生场景")
            # 艺术类考生需要特殊处理
            # 这里可以调用艺术类专门的推荐逻辑
            # TODO: 实现艺术类推荐逻辑

        # 4️⃣ 体育类考生检测
        if preferences and preferences.get("student_type") == "体育类":
            print(f"DEBUG: 检测到体育类考生场景")
            # TODO: 实现体育类推荐逻辑

        # 不是边界场景，返回None使用正常推荐流程
        return None

    def _get_undergraduate_control_line(self, province: str, subject_type: str) -> Optional[int]:
        """
        获取本科省控线（简化版本）

        实际应用中应该从数据库查询最新的省控线数据
        """
        # 简化的省控线数据（仅作示例）
        control_lines = {
            "江苏": {"理科": 415, "文科": 472, "物理类": 415, "历史类": 472},
            "浙江": {"理科": 488, "文科": 543, "综合": 488},
            "北京": {"理科": 425, "文科": 465, "综合": 425},
            "上海": {"理科": 400, "文科": 440, "综合": 400},
            "广东": {"理科": 445, "文科": 490, "物理类": 445, "历史类": 490},
            "山东": {"理科": 443, "文科": 518, "综合": 443},
            "湖北": {"理科": 435, "文科": 475, "物理类": 435, "历史类": 475},
            "湖南": {"理科": 439, "文科": 485, "物理类": 439, "历史类": 485},
            "四川": {"理科": 445, "文科": 510},
            "河南": {"理科": 440, "文科": 495},
            "安徽": {"理科": 435, "文科": 480},
            "福建": {"理科": 440, "文科": 490, "物理类": 440, "历史类": 490},
            "江西": {"理科": 445, "文科": 500},
            "重庆": {"理科": 430, "文科": 480, "物理类": 430, "历史类": 480},
        }

        if province in control_lines:
            province_lines = control_lines[province]
            # 优先使用新高考名称
            if subject_type in ["物理类", "历史类"]:
                return province_lines.get(subject_type)
            # 使用传统文理科名称
            elif subject_type in ["理科", "文科"]:
                return province_lines.get(subject_type)
            # 默认使用理科线
            else:
                return province_lines.get("理科")

        # 如果省份不在列表中，返回默认值
        return 430  # 默认本科线

    def _get_vocational_control_line(self, province: str, subject_type: str) -> Optional[int]:
        """
        获取专科省控线（简化版本）

        实际应用中应该从数据库查询最新的省控线数据
        """
        # 简化的专科省控线数据
        control_lines = {
            "江苏": {"理科": 220, "文科": 220},
            "浙江": {"理科": 274, "文科": 274},
            "北京": {"理科": 120, "文科": 120},
            "上海": {"理科": 150, "文科": 150},
            "广东": {"理科": 180, "文科": 180},
            "山东": {"理科": 150, "文科": 150},
            "湖北": {"理科": 200, "文科": 200},
            "湖南": {"理科": 200, "文科": 200},
            "四川": {"理科": 150, "文科": 150},
            "河南": {"理科": 185, "文科": 185},
            "安徽": {"理科": 200, "文科": 200},
            "福建": {"理科": 220, "文科": 220},
            "江西": {"理科": 200, "文科": 200},
            "重庆": {"理科": 180, "文科": 180},
        }

        if province in control_lines:
            province_lines = control_lines[province]
            return province_lines.get("理科", 200)  # 默认返回理科线

        # 如果省份不在列表中，返回默认值
        return 200  # 默认专科线

    def _normalize_province_name(self, province: str) -> str:
        """规范化省份名称"""
        # 简化的省份映射
        mapping = {
            "江苏省": "江苏",
            "浙江省": "浙江",
            "北京市": "北京",
            "上海市": "上海",
        }

        if province in mapping:
            return mapping[province]

        # 移除常见后缀
        for suffix in ["省", "市", "自治区"]:
            if province.endswith(suffix):
                return province[:-len(suffix)]

        return province

    def _calculate_rank_from_score(self, province: str, score: int, subject_type: str) -> int:
        """根据分数计算位次（简化版本）"""
        # 基于江苏省理科的简化位次计算
        # 实际应用中应该使用一分一段表
        if score >= 680:
            return 500
        elif score >= 650:
            return 2000
        elif score >= 600:
            return 8000
        elif score >= 550:
            return 20000
        elif score >= 500:
            return 40000
        elif score >= 450:
            return 70000
        else:
            return 100000

    def _find_university_id_by_name(self, name: str) -> Optional[str]:
        """根据院校名称查找ID"""
        for uni_id, uni_info in self.universities.items():
            if uni_info["name"] == name:
                return uni_id
        return None


# 全局实例
enhanced_recommendation_service = EnhancedRecommendationService()
