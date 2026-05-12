# -*- coding: utf-8 -*-
"""
留粤VS出省对比服务
为广东考生提供留粤和出省的院校对比推荐
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class CompareService:
    """留粤VS出省对比服务"""

    def __init__(self):
        self.data_dir = Path("data")
        self._load_data()

    def _load_data(self):
        """加载数据"""
        # 加载院校列表
        with open(self.data_dir / "universities_list.json", 'r', encoding='utf-8') as f:
            uni_data = json.load(f)
        self.universities = {u["id"]: u for u in uni_data["universities"]}

        # 加载录取分数数据
        with open(self.data_dir / "admission_scores.json", 'r', encoding='utf-8') as f:
            self.admission_scores = json.load(f)

        # 加载ROI数据
        try:
            with open(self.data_dir / "roi_tags.json", 'r', encoding='utf-8') as f:
                self.roi_data = json.load(f)
        except:
            self.roi_data = {}

    def compare_guangdong_vs_outprovince(
        self,
        province: str,
        score: int,
        rank: int,
        subject_type: str = "理科",
        target_majors: Optional[List[str]] = None,
        prefer_city: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        对比留粤和出省的最优选择

        Args:
            province: 考生省份
            score: 高考分数
            rank: 全省位次
            subject_type: 科目类型
            target_majors: 目标专业列表
            prefer_city: 偏好城市

        Returns:
            对比结果
        """

        if not target_majors:
            target_majors = ["计算机科学与技术"]

        # 获取广东省内院校推荐
        guangdong_recommendations = self._get_guangdong_recommendations(
            score, rank, subject_type, target_majors
        )

        # 获取省外院校推荐
        outprovince_recommendations = self._get_outprovince_recommendations(
            province, score, rank, subject_type, target_majors
        )

        # 选择最优的（录取概率最高的）
        guangdong_best = self._select_best_recommendation(guangdong_recommendations)
        outprovince_best = self._select_best_recommendation(outprovince_recommendations)

        # 生成建议文案
        suggestion = self._generate_suggestion(
            guangdong_best, outprovince_best, score, rank
        )

        return {
            "success": True,
            "data": {
                "user_info": {
                    "province": province,
                    "score": score,
                    "rank": rank,
                    "subject_type": subject_type
                },
                "guangdong_best": guangdong_best,
                "outprovince_best": outprovince_best,
                "suggestion": suggestion,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

    def _get_guangdong_recommendations(
        self,
        score: int,
        rank: int,
        subject_type: str,
        target_majors: List[str]
    ) -> List[Dict[str, Any]]:
        """获取广东省内院校推荐"""

        recommendations = []

        # 广东省重点院校列表
        guangdong_unis = [
            {"id": "中山大学", "name": "中山大学", "level": "985", "city": "广州"},
            {"id": "华南理工大学", "name": "华南理工大学", "level": "985", "city": "广州"},
            {"id": "暨南大学", "name": "暨南大学", "level": "211", "city": "广州"},
            {"id": "华南师范大学", "name": "华南师范大学", "level": "211", "city": "广州"},
            {"id": "汕头大学", "name": "汕头大学", "level": "一本", "city": "汕头"},
            {"id": "深圳大学", "name": "深圳大学", "level": "一本", "city": "深圳"},
            {"id": "南方科技大学", "name": "南方科技大学", "level": "双一流", "city": "深圳"},
            {"id": "广州大学", "name": "广州大学", "level": "一本", "city": "广州"},
            {"id": "广东工业大学", "name": "广东工业大学", "level": "一本", "city": "广州"},
            {"id": "华南农业大学", "name": "华南农业大学", "level": "双一流", "city": "广州"},
        ]

        for major in target_majors:
            for uni in guangdong_unis:
                # 估算录取概率
                probability, score_gap, tag = self._estimate_probability(
                    uni["level"], score, major
                )

                recommendations.append({
                    "university": uni["name"],
                    "university_id": uni["id"],
                    "university_level": uni["level"],
                    "city": uni["city"],
                    "province": "广东",
                    "major": major,
                    "probability": probability,
                    "score_gap": score_gap,
                    "tag": tag
                })

        return recommendations

    def _get_outprovince_recommendations(
        self,
        user_province: str,
        score: int,
        rank: int,
        subject_type: str,
        target_majors: List[str]
    ) -> List[Dict[str, Any]]:
        """获取省外院校推荐"""

        recommendations = []

        # 全国知名院校（排除广东）
        national_unis = [
            {"id": "北京大学", "name": "北京大学", "level": "985", "city": "北京", "province": "北京"},
            {"id": "清华大学", "name": "清华大学", "level": "985", "city": "北京", "province": "北京"},
            {"id": "复旦大学", "name": "复旦大学", "level": "985", "city": "上海", "province": "上海"},
            {"id": "上海交通大学", "name": "上海交通大学", "level": "985", "city": "上海", "province": "上海"},
            {"id": "浙江大学", "name": "浙江大学", "level": "985", "city": "杭州", "province": "浙江"},
            {"id": "南京大学", "name": "南京大学", "level": "985", "city": "南京", "province": "江苏"},
            {"id": "中国科学技术大学", "name": "中国科学技术大学", "level": "985", "city": "合肥", "province": "安徽"},
            {"id": "华中科技大学", "name": "华中科技大学", "level": "985", "city": "武汉", "province": "湖北"},
            {"id": "武汉大学", "name": "武汉大学", "level": "985", "city": "武汉", "province": "湖北"},
            {"id": "西安交通大学", "name": "西安交通大学", "level": "985", "city": "西安", "province": "陕西"},
        ]

        for major in target_majors:
            for uni in national_unis:
                # 跳过考生所在省份的院校
                if uni["province"] == user_province:
                    continue

                # 估算录取概率（省外院校通常需要更高分数）
                probability, score_gap, tag = self._estimate_probability(
                    uni["level"], score, major, is_outprovince=True
                )

                recommendations.append({
                    "university": uni["name"],
                    "university_id": uni["id"],
                    "university_level": uni["level"],
                    "city": uni["city"],
                    "province": uni["province"],
                    "major": major,
                    "probability": probability,
                    "score_gap": score_gap,
                    "tag": tag
                })

        return recommendations

    def _estimate_probability(
        self,
        university_level: str,
        score: int,
        major: str,
        is_outprovince: bool = False
    ) -> tuple:
        """
        估算录取概率

        Returns:
            (概率, 分数差, 类别)
        """

        # 基础分数线估算
        base_scores = {
            "985": 620,
            "211": 560,
            "双一流": 540,
            "一本": 500
        }

        base_score = base_scores.get(university_level, 500)

        # 省外院校通常需要更高分数
        if is_outprovince:
            base_score += 10

        # 热门专业加分
        hot_majors = ["计算机科学与技术", "软件工程", "人工智能", "临床医学"]
        if any(hot in major for hot in hot_majors):
            base_score += 5

        score_gap = score - base_score

        # 计算概率
        if score >= base_score + 30:
            probability = 90
            tag = "保底"
        elif score >= base_score + 10:
            probability = 70
            tag = "稳妥"
        elif score >= base_score - 10:
            probability = 50
            tag = "稳妥"
        elif score >= base_score - 30:
            probability = 30
            tag = "冲刺"
        else:
            probability = 15
            tag = "冲刺"

        return probability, score_gap, tag

    def _select_best_recommendation(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """选择最优推荐（录取概率最高的稳妥或保底院校）"""

        if not recommendations:
            return None

        # 优先选择稳妥或保底的院校
        valid_recs = [r for r in recommendations if r["tag"] in ["稳妥", "保底"]]

        if not valid_recs:
            # 如果没有稳妥保底，选择概率最高的冲刺
            valid_recs = recommendations

        # 按概率排序，取最高的
        valid_recs.sort(key=lambda x: x["probability"], reverse=True)
        best = valid_recs[0]

        # 添加ROI信息
        major = best["major"]
        roi_info = self._get_roi_info(major)

        best["roi_tags"] = roi_info.get("tags", [])
        best["roi_hint"] = roi_info.get("hints", [""])[0]

        return best

    def _get_roi_info(self, major: str) -> Dict[str, Any]:
        """获取专业的ROI信息"""
        result = {"tags": [], "hints": []}

        if not self.roi_data:
            return result

        categories = ["high_return", "low_return", "civil_service_advantage", "guangdong_demand"]

        for category in categories:
            category_data = self.roi_data.get(category, {})
            tag = category_data.get("tag", "")
            majors = category_data.get("majors", [])

            for major_info in majors:
                stored_major = major_info.get("name", "")
                if major in stored_major or stored_major in major:
                    if tag:
                        result["tags"].append(tag)
                    hint = major_info.get("hint", "")
                    if hint:
                        result["hints"].append(hint)
                    break

        return result

    def _generate_suggestion(
        self,
        guangdong_best: Optional[Dict[str, Any]],
        outprovince_best: Optional[Dict[str, Any]],
        score: int,
        rank: int
    ) -> str:
        """生成学锋老师的建议文案"""

        if not guangdong_best and not outprovince_best:
            return "抱歉，暂无足够的推荐数据。建议您提高分数或扩大专业选择范围。"

        if not guangdong_best:
            g_name = "无推荐"
        else:
            g_name = f"{guangdong_best['university']}（{guangdong_best['university_level']}，录取概率{guangdong_best['probability']}%）"

        if not outprovince_best:
            o_name = "无推荐"
        else:
            o_name = f"{outprovince_best['university']}（{outprovince_best['university_level']}，录取概率{outprovince_best['probability']}%）"

        # 根据分数段生成不同建议
        if score >= 620:
            return f"""**学锋老师的建议：**

你这个分数{score}分，位次{rank}名，很不错！

[DATA] **对比结果：**
- 留粤最优：{g_name}
- 出省最优：{o_name}

[TARGET] **我的看法：**
{outprovince_best['university'] if outprovince_best else '省外院校'}全国排名更高，校友资源更丰富，如果你不介意离家远，强烈推荐出省！

{guangdong_best['university'] if guangdong_best else '省内院校'}在广东就业有地理优势，深圳、广州的机会多，如果你打算在广东发展，留粤也是不错的选择。

[IDEA] **一句话建议：**想进大厂/深造选出省，想在广东就业选留粤。"""

        elif score >= 540:
            return f"""**学锋老师的建议：**

你这个分数{score}分，位次{rank}名，在广东选择不少！

[DATA] **对比结果：**
- 留粤最优：{g_name}
- 出省最优：{o_name}

[TARGET] **我的看法：**
你这个分数段，留粤性价比很高！{guangdong_best['university'] if guangdong_best else '省内院校'}虽然排名不如{outprovince_best['university'] if outprovince_best else '省外院校'}，但在广东就业市场认可度不错。

而且省内离家近，生活成本低，实习机会多。

[IDEA] **一句话建议：**优先留粤，除非你想去特定城市或专业。

[WARN] **注意：**如果你想冲985/211，可以考虑出省的{outprovince_best['university'] if outprovince_best else '院校'}，但录取概率会低一些。"""

        else:
            return f"""**学锋老师的建议：**

你这个分数{score}分，位次{rank}名，要务实一点！

[DATA] **对比结果：**
- 留粤最优：{g_name}
- 出省最优：{o_name}

[TARGET] **我的看法：**
老实说，你这个分数出省只能去一般院校，但在省内还有不错的选择。

{guangdong_best['university'] if guangdong_best else '省内院校'}在广东就业市场认可度不错，而且省内人脉资源方便积累。

[IDEA] **一句话建议：**安心留粤，选个好专业比选学校更重要！

[EDU] **专业建议：**优先选就业前景好的专业，比如计算机、电气、自动化等。"""


# 全局实例
compare_service = CompareService()
