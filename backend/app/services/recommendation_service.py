"""
智能志愿推荐服务
基于完整数据库实现推荐算法
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import random


class RecommendationService:
    """智能志愿推荐服务"""

    def __init__(self):
        self.data_dir = Path("data")

        # 加载数据
        self._load_data()

    def _load_data(self):
        """加载所有数据"""

        print("Loading database...")

        # 基础数据
        with open(self.data_dir / "universities_list.json", 'r', encoding='utf-8') as f:
            uni_data = json.load(f)
        self.universities = {u["id"]: u for u in uni_data["universities"]}

        with open(self.data_dir / "majors_list.json", 'r', encoding='utf-8') as f:
            major_data = json.load(f)
        self.majors = {m["code"]: m for m in major_data["majors"]}

        # 分数线数据
        with open(self.data_dir / "admission_scores.json", 'r', encoding='utf-8') as f:
            self.admission_scores = json.load(f)

        with open(self.data_dir / "major_admission_scores.json", 'r', encoding='utf-8') as f:
            self.major_scores = json.load(f)

        with open(self.data_dir / "score_rank_tables.json", 'r', encoding='utf-8') as f:
            self.score_rank_tables = json.load(f)

        # 其他数据
        with open(self.data_dir / "employment_data.json", 'r', encoding='utf-8') as f:
            self.employment_data = json.load(f)

        with open(self.data_dir / "university_details.json", 'r', encoding='utf-8') as f:
            self.university_details = json.load(f)

        with open(self.data_dir / "major_details.json", 'r', encoding='utf-8') as f:
            self.major_details = json.load(f)

        with open(self.data_dir / "rankings.json", 'r', encoding='utf-8') as f:
            self.rankings = json.load(f)

        with open(self.data_dir / "city_data.json", 'r', encoding='utf-8') as f:
            self.city_data = json.load(f)

        print("Database loaded successfully!")

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
        生成智能推荐方案

        Args:
            province: 省份
            score: 高考分数
            subject_type: 科类（理科/文科/综合）
            target_majors: 目标专业列表
            rank: 位次（可选）
            preferences: 偏好设置

        Returns:
            推荐方案
        """

        # 规范化省份名称（移除"省"、"市"、"自治区"等后缀）
        province = self._normalize_province_name(province)

        # 如果没有提供位次，计算位次
        if rank is None:
            rank = self._calculate_rank_from_score(province, score)

        # 确定目标专业
        if not target_majors:
            target_majors = self._recommend_majors_by_score(score, subject_type)

        # 生成推荐
        recommendation = {
            "basic_info": {
                "province": province,
                "score": score,
                "rank": rank,
                "subject_type": subject_type,
                "target_majors": target_majors,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "冲刺": [],
            "稳妥": [],
            "保底": []
        }

        # 为每个目标专业生成推荐
        for major in target_majors:
            major_rec = await self._generate_major_recommendation(
                province, score, rank, major, subject_type
            )

            recommendation["冲刺"].extend(major_rec["冲刺"])
            recommendation["稳妥"].extend(major_rec["稳妥"])
            recommendation["保底"].extend(major_rec["保底"])
            # 不再添加"垫底"类别
            # recommendation["垫底"].extend(major_rec["垫底"])

        # 去重和排序
        recommendation = self._deduplicate_and_sort(recommendation)

        # 生成分析报告
        recommendation["analysis"] = self._generate_analysis(recommendation)

        # 生成建议
        recommendation["advice"] = self._generate_advice(recommendation)

        return {
            "success": True,
            "data": recommendation
        }

    def _normalize_province_name(self, province: str) -> str:
        """规范化省份名称，匹配数据库中的格式"""

        # 常见省份名称映射
        province_mapping = {
            "浙江省": "浙江",
            "江苏省": "江苏",
            "北京市": "北京",
            "上海市": "上海",
            "广东": "广东",
            "山东省": "山东",
            "河南省": "河南",
            "四川省": "四川",
            "湖北省": "湖北",
            "湖南省": "湖南",
        }

        # 直接映射
        if province in province_mapping:
            return province_mapping[province]

        # 移除常见的行政后缀
        suffixes_to_remove = ["省", "市", "自治区", "特别行政区"]

        for suffix in suffixes_to_remove:
            if province.endswith(suffix):
                normalized = province[:-len(suffix)]
                # 检查是否在映射表中
                if normalized in province_mapping:
                    return province_mapping[normalized]
                return normalized

        # 如果没有匹配，返回原始值
        return province

    def _calculate_rank_from_score(self, province: str, score: int) -> int:
        """根据分数计算位次"""

        # 从一分一段表中查找
        if province in self.score_rank_tables.get("provinces", {}):
            province_data = self.score_rank_tables["provinces"][province]

            # 查找最近一年的数据
            years = [k for k in province_data.keys() if k.isdigit()]
            if years:
                latest_year = max(years)
                year_data = province_data[latest_year]

                if "table" in year_data:
                    for entry in year_data["table"]:
                        if entry["score"] == score:
                            return entry["rank"]

        # 如果找不到，使用估算
        return int(50000 / (score / 750))

    def _recommend_majors_by_score(self, score: int, subject_type: str) -> List[str]:
        """根据分数推荐专业"""

        # 高分段推荐热门专业
        if score >= 680:
            hot_majors = [
                "计算机科学与技术", "人工智能", "临床医学", "口腔医学",
                "金融学", "经济学", "法学", "电气工程及其自动化"
            ]
        elif score >= 650:
            hot_majors = [
                "计算机科学与技术", "软件工程", "电子信息工程", "自动化",
                "临床医学", "金融学", "会计学", "电气工程及其自动化"
            ]
        elif score >= 600:
            hot_majors = [
                "计算机科学与技术", "软件工程", "电子信息工程",
                "会计学", "金融学", "自动化", "临床医学"
            ]
        else:
            hot_majors = [
                "计算机科学与技术", "会计学", "金融学",
                "自动化", "电子信息工程", "机械设计制造及其自动化"
            ]

        return hot_majors[:5]

    async def _generate_major_recommendation(
        self,
        province: str,
        score: int,
        rank: int,
        major: str,
        subject_type: str
    ) -> Dict[str, Any]:
        """为某个专业生成推荐"""

        result = {
            "冲刺": [],
            "稳妥": [],
            "保底": []
        }  # 删除"垫底"类别

        # 获取该专业在目标省份的录取数据
        major_data = self._get_major_admission_data(province, major)

        # 根据录取数据分类推荐
        for uni_id, admission_info in major_data.items():
            uni_rec = self._create_university_recommendation(
                uni_id, major, score, rank, admission_info, province
            )

            category = uni_rec["category"]

            # 添加到对应类别（所有学校都已分类为冲刺、稳妥或保底）
            result[category].append(uni_rec)

        return result

    def _get_major_admission_data(self, province: str, major: str) -> Dict[str, Any]:
        """获取专业在某省的录取数据"""

        admission_data = {}

        # 从专业分数线数据中查找（使用模糊匹配）
        if "majors" in self.major_scores:
            for major_code, major_info in self.major_scores["majors"].items():
                # 使用模糊匹配专业名称
                major_name = major_info.get("name", "")
                if (major.lower() in major_name.lower() or
                    major_name.lower() in major.lower() or
                    major == major_name):

                    if province in major_info.get("provinces", {}):
                        province_data = major_info["provinces"][province]

                        # 提取各院校的录取分数（使用最近年份）
                        years = [k for k in province_data.keys() if k.isdigit()]
                        if years:
                            latest_year = max(years)
                            year_data = province_data[latest_year]

                            if "scores" in year_data and isinstance(year_data["scores"], list):
                                for score_entry in year_data["scores"]:
                                    if isinstance(score_entry, dict):
                                        uni_name = score_entry.get("university", "")

                                        # 找到对应的院校ID
                                        uni_id = self._find_university_id_by_name(uni_name)

                                        if uni_id and uni_id not in admission_data:
                                            admission_data[uni_id] = {
                                                "university": uni_name,
                                                "min_score": score_entry.get("min_score", 0),
                                                "avg_score": score_entry.get("avg_score", 0)
                                            }

        # 如果专业数据不足（少于10所），使用院校整体分数线数据补充
        if len(admission_data) < 10:
            print(f"专业数据只有{len(admission_data)}所，使用院校整体分数线补充")
            admission_data.update(self._get_university_admission_fallback(province, major))

        return admission_data

    def _find_university_id_by_name(self, name: str) -> Optional[str]:
        """根据院校名称查找ID"""

        for uni_id, uni_info in self.universities.items():
            if uni_info["name"] == name:
                return uni_id
        return None

    def _get_university_admission_fallback(self, province: str, major: str) -> Dict[str, Any]:
        """获取院校录取数据的后备方案"""

        admission_data = {}

        # 从院校分数线数据中查找
        if province in self.admission_scores.get("provinces", {}):
            province_data = self.admission_scores["provinces"][province]

            # 获取最近一年的数据
            years = [k for k in province_data.keys() if k.isdigit()]
            if years:
                latest_year = max(years)
                year_data = province_data[latest_year]

                if "scores" in year_data and isinstance(year_data["scores"], list):
                    # 遍历所有分数线数据，查找相关专业
                    for score_entry in year_data["scores"]:
                        if isinstance(score_entry, dict):
                            uni_name = score_entry.get("university", "")
                            entry_major = score_entry.get("major", "")

                            # 模糊匹配专业名称
                            if (major.lower() in entry_major.lower() or
                                entry_major.lower() in major.lower() or
                                '计算机' in entry_major):

                                uni_id = self._find_university_id_by_name(uni_name)

                                if uni_id and uni_id not in admission_data:
                                    admission_data[uni_id] = {
                                        "university": uni_name,
                                        "min_score": score_entry.get("min_score", 0),
                                        "avg_score": score_entry.get("avg_score", 0)
                                    }

        print(f"Fallback found {len(admission_data)} schools from admission scores")
        return admission_data

    def _create_university_recommendation(
        self,
        uni_id: str,
        major: str,
        user_score: int,
        user_rank: int,
        admission_info: Dict[str, Any],
        province: str
    ) -> Dict[str, Any]:
        """创建院校推荐"""

        uni_name = admission_info.get("university", "")
        min_score = admission_info.get("min_score", 0)
        avg_score = admission_info.get("avg_score", 0)

        print(f"DEBUG: 处理院校 {uni_name} - 用户分数:{user_score}, 最低分:{min_score}, 平均分:{avg_score}")

        # 计算录取概率
        probability = self._calculate_admission_probability(
            user_score, min_score, avg_score
        )

        print(f"DEBUG: 计算概率:{probability}%, 分数差:{user_score - min_score}")

        # 确定类别（基于分数差和概率）
        score_gap = user_score - min_score

        # 重新设计的分类逻辑 - 只使用冲刺、稳妥、保底三个类别
        if user_score < 500:
            # 低分学生（<500分）：非常宽松的标准
            if score_gap >= -100:
                category = "保底"
                category_cn = "保底"
            elif score_gap >= -200:
                category = "稳妥"
                category_cn = "稳妥"
            else:
                category = "冲刺"
                category_cn = "冲刺"
        elif user_score < 600:
            # 中低分学生（500-600分）：宽松标准
            if score_gap >= -50:
                category = "保底"
                category_cn = "保底"
            elif score_gap >= -100:
                category = "稳妥"
                category_cn = "稳妥"
            else:
                category = "冲刺"
                category_cn = "冲刺"
        elif user_score < 650:
            # 中高分学生（600-650分）：中等标准
            if score_gap >= -10:
                category = "保底"
                category_cn = "保底"
            elif score_gap >= -50:
                category = "稳妥"
                category_cn = "稳妥"
            else:
                category = "冲刺"
                category_cn = "冲刺"
        else:
            # 高分学生（>=650分）：严格标准 - 不再使用"垫底"分类
            if score_gap >= 10:
                category = "保底"
                category_cn = "保底"
            elif score_gap >= 0:
                category = "稳妥"
                category_cn = "稳妥"
            else:
                # 所有低于最低分的情况都归类为"冲刺"
                category = "冲刺"
                category_cn = "冲刺"

        print(f"DEBUG: {uni_name} - 分数差:{score_gap}, 用户分数:{user_score}, 分类:{category_cn}")

        # 获取院校详细信息
        uni_details = self.universities.get(uni_id, {})
        uni_extra = self.university_details.get("universities", {}).get(uni_id, {}).get("details", {})

        # 获取专业详细信息
        major_code = self._find_major_code_by_name(major)
        major_details = self.major_details.get("majors", {}).get(major_code, {}).get("details", {})

        # 获取就业数据
        employment_info = self.employment_data.get("majors", {}).get(major_code, {}).get("employment", {})
        uni_employment = self.employment_data.get("universities", {}).get(uni_id, {}).get("employment", {})

        return {
            "university_id": uni_id,
            "university_name": uni_name,
            "university_level": uni_details.get("level", ""),
            "university_type": uni_details.get("type", ""),
            "province": uni_details.get("province", ""),
            "city": uni_details.get("city", ""),
            "major": major,
            "probability": probability,
            "probability_range": f"{probability-5}-{probability+5}%",
            "category": category_cn,
            "score_gap": user_score - min_score,
            "rank_gap": user_rank - int(min_score * 100),  # 简化计算
            "suggestions": self._generate_university_suggestions(
                uni_id, major, probability, category
            ),
            "university_highlights": self._get_university_highlights(uni_extra),
            "major_highlights": self._get_major_highlights(major_details),
            "employment_info": {
                "employment_rate": employment_info.get("employment_rate", "未知"),
                "average_salary": employment_info.get("average_salary", "未知"),
                "top_employers": employment_info.get("top_employers", [])[:3]
            },
            "university_employment": {
                "employment_rate": uni_employment.get("employment_rate", "未知"),
                "graduate_school_rate": uni_employment.get("graduate_school_rate", "未知")
            }
        }

    def _calculate_admission_probability(
        self,
        user_score: int,
        min_score: int,
        avg_score: int
    ) -> int:
        """计算录取概率"""

        # 确保分数有效
        if min_score == 0 and avg_score == 0:
            return 50  # 没有数据时返回中等概率

        if user_score >= avg_score:
            # 高于平均分，概率很高
            base_prob = 75
            extra = min((user_score - avg_score) * 1.5, 20)
            return min(int(base_prob + extra), 95)
        elif user_score >= min_score:
            # 在最低分和平均分之间
            gap = avg_score - min_score
            user_gap = user_score - min_score
            ratio = user_gap / gap if gap > 0 else 0.5
            return int(40 + ratio * 35)
        else:
            # 低于最低分
            gap = min_score - user_score
            if gap <= 3:
                return 30
            elif gap <= 8:
                return 20
            elif gap <= 15:
                return 10
            else:
                return 5

    def _find_major_code_by_name(self, name: str) -> Optional[str]:
        """根据专业名称查找代码"""

        for code, info in self.majors.items():
            if info["name"] == name:
                return code
        return None

    def _generate_university_suggestions(
        self,
        uni_id: str,
        major: str,
        probability: int,
        category: str
    ) -> List[str]:
        """生成院校建议"""

        suggestions = []

        if category == "冲刺":
            suggestions.append("分数接近，可以尝试")
            suggestions.append("建议放在志愿前面")
            if probability < 40:
                suggestions.append("需要一些运气")
        elif category == "稳妥":
            suggestions.append("录取概率较大")
            suggestions.append("建议作为主要志愿")
            suggestions.append("性价比不错的选择")
        elif category == "保底":
            suggestions.append("基本没问题")
            suggestions.append("建议放在志愿后面")

        return suggestions

    def _get_university_highlights(self, details: Dict) -> List[str]:
        """获取院校亮点"""

        highlights = []

        if "rankings" in details:
            rankings = details["rankings"]
            if rankings.get("national_rank"):
                highlights.append(f"全国排名#{rankings['national_rank']}")

            if rankings.get("soft_ranking"):
                highlights.append(f"软科排名#{rankings['soft_ranking']}")

        if "key_subjects" in details:
            key_subjects = details["key_subjects"]
            if key_subjects.get("national_key_subjects", 0) > 0:
                highlights.append(f"{key_subjects['national_key_subjects']}个国家重点学科")

        if "employment" in details:
            emp = details["employment"]
            if emp.get("employment_rate", 0) >= 0.95:
                highlights.append("就业率超高")

        return highlights[:3]

    def _get_major_highlights(self, details: Dict) -> List[str]:
        """获取专业亮点"""

        highlights = []

        if "career_directions" in details:
            career = details["career_directions"]
            if career.get("employment_prospects"):
                highlights.append(f"就业前景：{career['employment_prospects']}")

        if "curriculum" in details:
            curriculum = details["curriculum"]
            if curriculum.get("core_courses"):
                highlights.append(f"核心课程丰富")

        if "development_prospects" in details:
            prospects = details["development_prospects"]
            if prospects.get("salary_outlook"):
                highlights.append(f"薪资前景：{prospects['salary_outlook']}")

        return highlights[:3]

    def _deduplicate_and_sort(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """去重和排序，按照20%冲刺、40%稳妥、30%保底的比例分配"""

        # 1. 大幅放宽过滤条件以适应数据库局限性
        max_score_gap = -400 # 增加到-400，允许更大的分数差距
        min_probability = 1     # 最低录取概率：1%以上

        print(f"DEBUG: 使用过滤条件 max_score_gap={max_score_gap}, min_probability={min_probability}")

        # 只处理存在的类别（冲刺、稳妥、保底）
        for category in ["冲刺", "稳妥", "保底"]:
            if category not in recommendation:
                continue

            filtered_items = []
            for item in recommendation[category]:
                score_gap = item.get("score_gap", 0)
                probability = item.get("probability", 0)

                # 放宽条件：允许更大的分数差距
                if score_gap >= max_score_gap and probability >= min_probability:
                    filtered_items.append(item)

            # 如果某类别没有学校了，至少保留2个概率最高的
            if len(filtered_items) == 0 and len(recommendation[category]) > 0:
                # 按概率排序，保留前2个
                sorted_items = sorted(recommendation[category], key=lambda x: x.get("probability", 0), reverse=True)
                filtered_items = sorted_items[:2]
                print(f"DEBUG: {category}类别过滤后为空，保留前2个概率最高的")

            print(f"DEBUG: {category}类别过滤后保留{len(filtered_items)}所学校")
            recommendation[category] = filtered_items

        # 2. 去重
        seen = set()
        for category in ["冲刺", "稳妥", "保底"]:
            if category not in recommendation:
                continue

            unique_items = []
            for item in recommendation[category]:
                key = f"{item.get('university_name', '')}-{item.get('major', '')}"
                if key not in seen:
                    seen.add(key)
                    unique_items.append(item)
            recommendation[category] = unique_items

        # 3. 排序（按概率降序）
        for category in ["冲刺", "稳妥", "保底"]:
            if category in recommendation:
                recommendation[category].sort(
                    key=lambda x: x.get("probability", 0),
                    reverse=True
                )

        # 4. 按照20%冲刺、40%稳妥、30%保底的比例分配
        # 目标总数量：10所学校（2冲刺、4稳妥、3保底、1剩余）
        target_chong = 2
        target_wen = 4
        target_bao = 3

        # 5. 限制每类数量，按照目标比例
        recommendation["冲刺"] = recommendation.get("冲刺", [])[:target_chong]
        recommendation["稳妥"] = recommendation.get("稳妥", [])[:target_wen]
        recommendation["保底"] = recommendation.get("保底", [])[:target_bao]

        return recommendation

    def _generate_analysis(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析报告"""

        analysis = {
            "total_count": 0,
            "category_counts": {},
            "score_distribution": {},
            "university_levels": {},
            "major_distribution": {}
        }

        total = 0
        for category in ["冲刺", "稳妥", "保底"]:  # 删除"垫底"
            count = len(recommendation[category])
            analysis["category_counts"][category] = count
            total += count

            # 统计院校层次
            levels = {}
            for item in recommendation[category]:
                level = item.get("university_level", "未知")
                levels[level] = levels.get(level, 0) + 1

            analysis["university_levels"][category] = levels

        analysis["total_count"] = total

        # 生成评论
        analysis["comments"] = []
        if total == 0:
            analysis["comments"].append("未找到匹配的院校，请调整分数或专业")
        elif total < 10:
            analysis["comments"].append("匹配院校较少，建议扩大专业范围")
        else:
            analysis["comments"].append(f"共找到{total}所院校，方案完整")

        return analysis

    def _generate_advice(self, recommendation: Dict[str, Any]) -> List[str]:
        """生成建议"""

        advice = []

        counts = recommendation.get("analysis", {}).get("category_counts", {})

        # 冲刺建议
        chong_count = counts.get("冲刺", 0)
        if chong_count > 0:
            advice.append(f"有{chong_count}个冲刺院校，建议选择1-2个最有希望的")
        else:
            advice.append("建议增加1-2个冲刺院校")

        # 稳妥建议
        wen_count = counts.get("稳妥", 0)
        if wen_count >= 3:
            advice.append(f"有{wen_count}个稳妥院校，这是重点，建议选3-4个")
        else:
            advice.append("稳妥院校不足，建议补充")

        # 保底建议
        bao_count = counts.get("保底", 0)
        if bao_count >= 2:
            advice.append(f"有{bao_count}个保底院校，建议选2-3个")
        else:
            advice.append("保底院校不足，建议补充")

        # 总体建议
        advice.append("建议比例：冲刺20%，稳妥40%，保底30%")

        return advice


# 全局实例
recommendation_service = RecommendationService()
