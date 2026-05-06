"""
专业级智能志愿推荐服务
基于专业位次计算概率，推荐15-30个专业志愿
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict


class ProfessionalRecommendationService:
    """专业级推荐服务"""

    def __init__(self):
        self.data_dir = Path("data")
        self._load_professional_data()

    def _load_professional_data(self):
        """加载专业级数据"""
        print("Loading professional database...")

        # 加载院校-专业关联表
        try:
            with open(self.data_dir / "university_majors.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.university_majors = data["university_majors"]
            print(f"Loaded {len(self.university_majors)} university-major records")
        except Exception as e:
            print(f"Error loading university_majors.json: {e}")
            self.university_majors = []

        # 加载专业录取位次数据
        try:
            with open(self.data_dir / "major_rank_data.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.major_rank_data = data["major_rank_data"]
            print(f"Loaded {len(self.major_rank_data)} major rank records")
        except Exception as e:
            print(f"Error loading major_rank_data.json: {e}")
            self.major_rank_data = []

        # 加载院校基本信息
        try:
            with open(self.data_dir / "universities_list.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.universities = {u["id"]: u for u in data["universities"]}
        except:
            self.universities = {}

        print("Professional database loaded successfully!")

    async def generate_professional_recommendation(
        self,
        province: str,
        score: int,
        rank: int,
        subject_type: str = "理科",
        target_majors: Optional[List[str]] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        生成专业级智能推荐方案

        Returns:
            推荐结果，包含15-30个专业志愿
        """

        # 规范化输入
        if not target_majors:
            target_majors = ["计算机科学与技术"]

        if rank is None:
            rank = self._calculate_rank_from_score(province, score, subject_type)

        print(f"\n生成专业级推荐：{province}, {score}分, 位次{rank}")
        print(f"目标专业：{target_majors}")

        # 生成推荐
        recommendation = {
            "basic_info": {
                "province": province,
                "score": score,
                "rank": rank,
                "subject_type": subject_type,
                "target_majors": target_majors,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "recommendation_type": "professional"  # 标识为专业级推荐
            },
            "专业志愿": []
        }

        # 为每个目标专业生成推荐
        professional_recommendations = []

        for major in target_majors:
            major_recs = self._generate_major_recommendations(
                province, rank, major, subject_type
            )
            professional_recommendations.extend(major_recs)

        # 按概率排序
        professional_recommendations.sort(
            key=lambda x: x["probability"],
            reverse=True
        )

        # 去重：每所学校最多3个专业
        professional_recommendations = self._deduplicate_by_university(
            professional_recommendations,
            max_per_university=3
        )

        # 取前30个专业志愿
        recommendation["专业志愿"] = professional_recommendations[:30]

        # 分类（按概率）
        recommendation["冲刺"] = [r for r in recommendation["专业志愿"] if r["category"] == "冲刺"]
        recommendation["稳妥"] = [r for r in recommendation["专业志愿"] if r["category"] == "稳妥"]
        recommendation["保底"] = [r for r in recommendation["专业志愿"] if r["category"] == "保底"]

        # 生成分析报告
        recommendation["analysis"] = self._generate_analysis(recommendation)

        # 生成建议
        recommendation["advice"] = self._generate_advice(recommendation)

        return {
            "success": True,
            "data": recommendation
        }

    def _generate_major_recommendations(
        self,
        province: str,
        rank: int,
        major: str,
        subject_type: str
    ) -> List[Dict[str, Any]]:
        """为某个专业生成推荐"""

        recommendations = []

        # 查找开设该专业的所有院校
        major_offered_universities = self._get_universities_by_major(major)

        print(f"为{major}专业找到{len(major_offered_universities)}所院校")

        for university_major in major_offered_universities:
            # 获取该专业的录取位次
            rank_data = self._get_major_rank_data(
                university_major["university_major_id"],
                province
            )

            if not rank_data:
                continue

            # 计算录取概率
            probability = self._calculate_probability_by_rank(
                rank, rank_data["min_rank"]
            )

            # 确定类别
            category = self._determine_category(probability)

            rec = {
                "university_major_id": university_major["university_major_id"],
                "university_id": university_major["university_id"],
                "university_name": university_major["university_name"],
                "university_level": university_major.get("university_level", ""),
                "major_code": university_major["major_code"],
                "major_name": university_major["major_name"],
                "major_category": university_major["major_category"],
                "probability": probability,
                "rank_gap": rank - rank_data["min_rank"],
                "category": category,
                "min_rank": rank_data["min_rank"],
                "avg_rank": rank_data.get("avg_rank", 0),
                "min_score": rank_data.get("min_score", 0),
                "avg_score": rank_data.get("avg_score", 0)
            }

            recommendations.append(rec)

        return recommendations

    def _get_universities_by_major(self, major: str) -> List[Dict[str, Any]]:
        """获取开设某个专业的所有院校"""
        # 从university_majors中查找
        universities = []

        for record in self.university_majors:
            # 模糊匹配专业名称
            if (major in record["major_name"] or
                record["major_name"] in major or
                record["major_code"].startswith(major[:3])):

                universities.append(record)

        return universities

    def _get_major_rank_data(self, university_major_id: str, province: str) -> Optional[Dict[str, Any]]:
        """获取专业的录取位次数据"""
        for record in self.major_rank_data:
            if (record["university_major_id"] == university_major_id and
                record["province"] == province):
                return {
                    "min_rank": record["min_rank"],
                    "avg_rank": record.get("avg_rank", 0),
                    "min_score": record["min_score"],
                    "avg_score": record["avg_score"]
                }

        # 如果没有找到位次数据，尝试用分数估算
        return None

    def _calculate_probability_by_rank(self, user_rank: int, major_min_rank: int) -> int:
        """
        基于位次计算录取概率（位次波动率模型）

        Args:
            user_rank: 用户位次
            major_min_rank: 专业最低录取位次

        Returns:
            录取概率（0-100）
        """
        if major_min_rank == 0:
            return 50  # 没有数据时返回中等概率

        rank_gap = user_rank - major_min_rank

        # 基于位差距计算概率
        if user_rank <= major_min_rank:
            # 位次高于最低要求，概率很高
            if rank_gap >= -100:
                return 90
            elif rank_gap >= -50:
                return 85
            else:
                return 75
        elif user_rank <= major_min_rank * 1.1:
            # 位次在最低要求附近（+10%以内）
            gap_ratio = abs(rank_gap) / (major_min_rank * 0.1)
            return int(75 - gap_ratio * 40)  # 35%-75%
        else:
            # 位次低于最低要求（冲刺）
            if rank_gap >= -500:
                return 30
            elif rank_gap >= -1000:
                return 20
            elif rank_gap >= -2000:
                return 10
            else:
                return 5

    def _determine_category(self, probability: int) -> str:
        """根据概率确定类别"""
        if probability >= 70:
            return "保底"
        elif probability >= 30:
            return "稳妥"
        else:
            return "冲刺"

    def _deduplicate_by_university(
        self,
        recommendations: List[Dict[str, Any]],
        max_per_university: int = 3
    ) -> List[Dict[str, Any]]:
        """
        去重：每所学校最多保留max_per_university个专业

        Args:
            recommendations: 推荐列表
            max_per_university: 每校最多保留的专业数

        Returns:
            去重后的推荐列表
        """
        university_counts = defaultdict(int)
        filtered_recommendations = []

        for rec in recommendations:
            university_name = rec["university_name"]

            # 检查该院校的专业数量
            if university_counts[university_name] < max_per_university:
                filtered_recommendations.append(rec)
                university_counts[university_name] += 1
            else:
                # 该院校已有足够多的专业，检查是否需要替换
                # 找到该院校概率最低的专业，如果当前专业概率更高，则替换
                existing_indices = [
                    i for i, r in enumerate(filtered_recommendations)
                    if r["university_name"] == university_name
                ]

                if existing_indices:
                    # 找到概率最低的专业
                    min_prob_index = min(
                        existing_indices,
                        key=lambda i: filtered_recommendations[i]["probability"]
                    )

                    # 如果当前专业概率更高，替换
                    if rec["probability"] > filtered_recommendations[min_prob_index]["probability"]:
                        filtered_recommendations[min_prob_index] = rec

        return filtered_recommendations

    def _calculate_rank_from_score(self, province: str, score: int, subject_type: str) -> int:
        """根据分数计算位次（简化版本）"""
        # 简化实现：基于固定系数
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

    def _generate_analysis(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析报告"""
        professional_volunteer = recommendation.get("专业志愿", [])

        return {
            "total_count": len(professional_volunteer),
            "category_counts": {
                "冲刺": len(recommendation.get("冲刺", [])),
                "稳妥": len(recommendation.get("稳妥", [])),
                "保底": len(recommendation.get("保底", []))
            },
            "university_count": len(set(r["university_name"] for r in professional_volunteer)),
            "avg_probability": sum(r["probability"] for r in professional_volunteer) / len(professional_volunteer) if professional_volunteer else 0
        }

    def _generate_advice(self, recommendation: Dict[str, Any]) -> List[str]:
        """生成建议"""
        advice = []

        analysis = recommendation.get("analysis", {})
        total_count = analysis.get("total_count", 0)
        avg_probability = analysis.get("avg_probability", 0)

        if total_count == 0:
            advice.append("建议调整筛选条件或专业")
        else:
            advice.append(f"基于专业级推荐算法生成{total_count}个专业志愿")
            advice.append(f"平均录取概率：{avg_probability:.1f}%")

            # 冲稳保建议
            category_counts = analysis.get("category_counts", {})
            冲刺 = category_counts.get("冲刺", 0)
            稳妥 = category_counts.get("稳妥", 0)
            保底 = category_counts.get("保底", 0)

            if 冲刺 > total_count * 0.3:
                advice.append(f"冲刺专业较多（{冲刺}/{total_count}），注意风险")
            if 保底 == 0:
                advice.append("建议增加保底专业")
            if 保底 < total_count * 0.2:
                advice.append("保底专业偏少，建议补充")

        return advice


# 全局实例
professional_recommendation_service = ProfessionalRecommendationService()
