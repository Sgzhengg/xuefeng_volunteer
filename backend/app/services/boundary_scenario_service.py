"""
边界场景处理服务
处理特殊类型考生、边界分数段、特殊录取规则等场景
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path


class BoundaryScenarioService:
    """边界场景处理服务"""

    def __init__(self):
        self.data_dir = Path("data")
        self._load_boundary_data()

    def _load_boundary_data(self):
        """加载边界场景数据"""
        print("Loading boundary scenario data...")

        # 加载学科评估数据
        try:
            with open(self.data_dir / "discipline_evaluation.json", 'r', encoding='utf-8') as f:
                self.discipline_evaluation = json.load(f)
        except:
            self.discipline_evaluation = {}

        # 加载专业级差数据
        try:
            with open(self.data_dir / "major_step_rules.json", 'r', encoding='utf-8') as f:
                self.major_step_rules = json.load(f)
        except:
            self.major_step_rules = {}

        # 加载同分排序规则
        try:
            with open(self.data_dir / "same_score_rules.json", 'r', encoding='utf-8') as f:
                self.same_score_rules = json.load(f)
        except:
            self.same_score_rules = {}

        # 加载专本贯通项目数据
        try:
            with open(self.data_dir / "college_transfer_programs.json", 'r', encoding='utf-8') as f:
                self.transfer_programs = json.load(f)
        except:
            self.transfer_programs = {}

        print("Boundary scenario data loaded!")

    # ==================== 超高分段精细推荐 ====================

    def generate_top_tier_recommendation(
        self,
        province: str,
        score: int,
        rank: int,
        target_majors: List[str]
    ) -> Dict[str, Any]:
        """
        超高分段(680+)专项推荐

        策略：
        - 全省前100：重点推荐清北
        - 全省前500：推荐华五人
        - 全省前2000：推荐其他顶尖985
        """

        result = {
            "冲刺": [],
            "稳妥": [],
            "保底": []
        }

        # 根据位次分段推荐
        if rank <= 100:
            # 全省前100：清北为主
            result = self._recommend_tsinghua_peking(rank, target_majors)

        elif rank <= 500:
            # 全省前500：华五人
            result = self._recommend_c9_union(rank, target_majors)

        elif rank <= 2000:
            # 全省前2000：其他顶尖985
            result = self._recommend_top_985(rank, target_majors)

        else:
            # 680+但位次较低：正常推荐逻辑
            pass

        return result

    def _recommend_tsinghua_peking(
        self,
        rank: int,
        target_majors: List[str]
    ) -> Dict[str, Any]:
        """推荐清华北大"""

        result = {
            "冲刺": [],
            "稳妥": [],
            "保底": []
        }

        # 清北顶尖专业（按学科评估A+排序）
        top_majors_by_discipline = self._sort_majors_by_discipline_evaluation(
            ["清华大学", "北京大学"],
            target_majors
        )

        # 前50名：冲刺清北任何专业
        if rank <= 50:
            for major in top_majors_by_discipline[:3]:
                result["冲刺"].append({
                    "university_name": "清华大学" if major.get("university") == "清华大学" else "北京大学",
                    "major": major["name"],
                    "probability": 85 if rank <= 30 else 75,
                    "category": "冲刺",
                    "note": "全省前50，冲刺清北顶尖专业",
                    "discipline_grade": major.get("grade", "A+")
                })

        # 50-100名：稳妥清北普通专业
        for major in top_majors_by_discipline[3:6]:
            result["稳妥"].append({
                "university_name": major.get("university"),
                "major": major["name"],
                "probability": 80,
                "category": "稳妥",
                "note": "全省前100，稳妥选择",
                "discipline_grade": major.get("grade", "A")
            })

        return result

    def _recommend_c9_union(
        self,
        rank: int,
        target_majors: List[str]
    ) -> Dict[str, Any]:
        """推荐华五人（复旦、上交、浙大、南大、中科大）+ 人大"""

        c9_universities = [
            "复旦大学", "上海交通大学", "浙江大学",
            "南京大学", "中国科学技术大学", "中国人民大学"
        ]

        result = {
            "冲刺": [],
            "稳妥": [],
            "保底": []
        }

        # 按学科评估排序
        top_majors = self._sort_majors_by_discipline_evaluation(
            c9_universities,
            target_majors
        )

        # 前200名：冲刺华五热门专业
        if rank <= 200:
            for major in top_majors[:3]:
                result["冲刺"].append({
                    "university_name": major.get("university"),
                    "major": major["name"],
                    "probability": 70,
                    "category": "冲刺",
                    "note": "华五人热门专业，冲刺",
                    "discipline_grade": major.get("grade", "A+")
                })

        # 稳妥华五普通专业
        for major in top_majors[3:6]:
            result["稳妥"].append({
                "university_name": major.get("university"),
                "major": major["name"],
                "probability": 80,
                "category": "稳妥",
                "note": "华五人普通专业，稳妥",
                "discipline_grade": major.get("grade", "A")
            })

        # 保底：其他985
        result["保底"].append({
            "university_name": "武汉大学",
            "major": target_majors[0] if target_majors else "计算机科学与技术",
            "probability": 85,
            "category": "保底",
            "note": "中坚985保底"
        })

        return result

    def _recommend_top_985(
        self,
        rank: int,
        target_majors: List[str]
    ) -> Dict[str, Any]:
        """推荐其他顶尖985"""

        top_985 = [
            "武汉大学", "华中科技大学", "中山大学", "厦门大学",
            "天津大学", "南开大学", "四川大学", "山东大学"
        ]

        result = {
            "冲刺": [],
            "稳妥": [],
            "保底": []
        }

        # 冲刺：华五人冷门专业
        result["冲刺"].append({
            "university_name": "浙江大学",
            "major": target_majors[0] if target_majors else "计算机科学与技术",
            "probability": 65,
            "category": "冲刺",
            "note": "冲刺华五人冷门专业"
        })

        # 稳妥：中坚985优势专业
        for uni in top_985[:4]:
            result["稳妥"].append({
                "university_name": uni,
                "major": target_majors[0] if target_majors else "计算机科学与技术",
                "probability": 75,
                "category": "稳妥",
                "note": f"{uni}优势专业"
            })

        # 保底：其他985
        result["保底"].append({
            "university_name": "吉林大学",
            "major": target_majors[0] if target_majors else "计算机科学与技术",
            "probability": 85,
            "category": "保底",
            "note": "保底985"
        })

        return result

    def _sort_majors_by_discipline_evaluation(
        self,
        universities: List[str],
        target_majors: List[str]
    ) -> List[Dict[str, Any]]:
        """
        按学科评估排序专业

        优先级：A+ > A > A- > B+
        """
        major_scores = []

        for uni in universities:
            for major in target_majors:
                # 获取学科评估等级
                grade = self._get_discipline_grade(uni, major)

                # 评分
                grade_score = {
                    "A+": 100, "A": 90, "A-": 85,
                    "B+": 80, "B": 75, "B-": 70
                }.get(grade, 60)

                major_scores.append({
                    "university": uni,
                    "name": major,
                    "grade": grade,
                    "score": grade_score
                })

        # 按评分降序排序
        major_scores.sort(key=lambda x: x["score"], reverse=True)

        return major_scores

    def _get_discipline_grade(self, university: str, major: str) -> str:
        """获取学科评估等级"""
        # 从学科评估数据中查询
        if major in self.discipline_evaluation:
            uni_grades = self.discipline_evaluation[major]
            if university in uni_grades:
                return uni_grades[university]

        # 默认返回A（顶尖985默认A）
        if "清华" in university or "北大" in university:
            return "A+"
        elif any(x in university for x in ["复旦", "上交", "浙大", "南大", "中科大"]):
            return "A"

        return "A-"  # 默认

    # ==================== 边缘分数专项策略 ====================

    def generate_edge_score_recommendation(
        self,
        province: str,
        score: int,
        control_line: int,
        is_undergraduate: bool,
        target_majors: List[str]
    ) -> Dict[str, Any]:
        """
        边缘分数专项推荐

        策略：
        - 本科压线生：民办本科 + 偏远公办 + 专本贯通
        - 专科压线生：优质专科 + 专本贯通项目
        """

        result = {
            "冲刺": [],
            "稳妥": [],
            "保底": [],
            "special_programs": []  # 特殊项目（专本贯通等）
        }

        if is_undergraduate:
            # 本科压线生
            gap = score - control_line

            if gap < 0:
                # 低于本科线：重点推荐专科+专本贯通
                result = self._recommend_below_undergraduate_line(
                    province, score, target_majors
                )

            elif gap < 10:
                # 压线0-10分：民办本科+偏远公办
                result = self._recommend_on_undergraduate_line(
                    province, score, target_majors
                )

            else:
                # 正常推荐
                pass

        else:
            # 专科压线生
            result = self._recommend_vocational_with_transfer(
                province, score, target_majors
            )

        return result

    def _recommend_below_undergraduate_line(
        self,
        province: str,
        score: int,
        target_majors: List[str]
    ) -> Dict[str, Any]:
        """低于本科线：推荐专科+专本贯通"""

        result = {
            "冲刺": [],
            "稳妥": [],
            "保底": [],
            "special_programs": []
        }

        # 查找专本贯通项目
        if province in self.transfer_programs:
            programs = self.transfer_programs[province].get("programs", [])

            for program in programs[:3]:
                result["special_programs"].append({
                    "type": "专本贯通(3+2)",
                    "vocational_college": program["vocational_college"],
                    "partner_university": program["partner_university"],
                    "major": program["majors"][0] if program["majors"] else target_majors[0],
                    "transfer_rate": program.get("transfer_rate", "50%"),
                    "note": "3年专科+2年本科，获得全日制本科文凭",
                    "probability": 80
                })

        # 优质专科作为保底
        result["保底"].append({
            "university_name": f"{province}职业技术学院",
            "major": target_majors[0] if target_majors else "计算机应用技术",
            "probability": 90,
            "category": "保底",
            "note": "省内优质专科，就业率高"
        })

        return result

    def _recommend_on_undergraduate_line(
        self,
        province: str,
        score: int,
        target_majors: List[str]
    ) -> Dict[str, Any]:
        """本科压线0-10分：民办本科+偏远公办"""

        result = {
            "冲刺": [],
            "稳妥": [],
            "保底": []
        }

        # 冲刺：偏远地区公办本科（分数相对较低）
        remote_universities = [
            "新疆大学", "西藏大学", "青海大学", "宁夏大学",
            "石河子大学", "内蒙古大学"
        ]

        for uni in remote_universities[:2]:
            result["冲刺"].append({
                "university_name": uni,
                "major": target_majors[0] if target_majors else "计算机科学与技术",
                "probability": 60,
                "category": "冲刺",
                "note": "偏远地区211，分数相对较低"
            })

        # 稳妥：省内民办本科
        result["稳妥"].append({
            "university_name": f"{province}XX学院（民办）",
            "major": target_majors[0] if target_majors else "计算机科学与技术",
            "probability": 75,
            "category": "稳妥",
            "note": "省内民办本科，学费较高但录取机会大"
        })

        # 保底：专本贯通项目
        if province in self.transfer_programs:
            programs = self.transfer_programs[province].get("programs", [])
            if programs:
                result["保底"].append({
                    "university_name": programs[0]["vocational_college"],
                    "major": programs[0]["majors"][0] if programs[0]["majors"] else target_majors[0],
                    "probability": 85,
                    "category": "保底",
                    "note": f"专本贯通，对接{programs[0]['partner_university']}"
                })

        return result

    def _recommend_vocational_with_transfer(
        self,
        province: str,
        score: int,
        target_majors: List[str]
    ) -> Dict[str, Any]:
        """专科压线生：优质专科+专本贯通"""

        result = {
            "冲刺": [],
            "稳妥": [],
            "保底": []
        }

        # 冲刺：专本贯通项目
        if province in self.transfer_programs:
            programs = self.transfer_programs[province].get("programs", [])

            for program in programs[:2]:
                result["冲刺"].append({
                    "university_name": program["vocational_college"],
                    "major": program["majors"][0] if program["majors"] else target_majors[0],
                    "probability": 70,
                    "category": "冲刺",
                    "note": f"专本贯通，对接{program['partner_university']}"
                })

        # 稳妥：省内优质专科
        top_vocational = [
            f"{province}工业职业技术学院",
            f"{province}信息职业技术学院",
            f"{province}交通职业技术学院"
        ]

        for college in top_vocational[:2]:
            result["稳妥"].append({
                "university_name": college,
                "major": target_majors[0] if target_majors else "计算机应用技术",
                "probability": 85,
                "category": "稳妥",
                "note": "省内优质专科，就业率高"
            })

        # 保底：普通专科
        result["保底"].append({
            "university_name": f"{province}XX职业技术学院",
            "major": target_majors[0] if target_majors else "计算机应用技术",
            "probability": 95,
            "category": "保底",
            "note": "保底专科"
        })

        return result

    # ==================== 专业级差处理 ====================

    def apply_major_step_adjustment(
        self,
        original_score: int,
        major_position: int,
        university_id: str
    ) -> int:
        """
        应用专业级差调整

        Args:
            original_score: 原始分数
            major_position: 第几志愿专业（从1开始）
            university_id: 院校ID

        Returns:
            调整后的分数
        """
        # 获取院校专业级差规则
        step_rule = self._get_major_step_rule(university_id)

        if not step_rule or not step_rule.get("has_step"):
            return original_score

        # 获取级差分数
        step_scores = step_rule.get("step_scores", [])

        if major_position <= len(step_scores):
            adjustment = step_scores[major_position - 1]
            return original_score - adjustment

        return original_score

    def _get_major_step_rule(self, university_id: str) -> Optional[Dict[str, Any]]:
        """获取院校专业级差规则"""
        if university_id in self.major_step_rules:
            return self.major_step_rules[university_id]

        # 默认规则：无级差
        return {
            "has_step": False,
            "note": "该院校不设专业级差"
        }

    # ==================== 同分排序规则 ====================

    def calculate_rank_with_same_score_rules(
        self,
        province: str,
        score: int,
        subject_type: str,
        subject_scores: Dict[str, int]
    ) -> int:
        """
        使用同分排序规则计算精确位次

        Args:
            province: 省份
            score: 总分
            subject_type: 科类（文科/理科/综合）
            subject_scores: 各科成绩 {"语文": 120, "数学": 130, "外语": 140}

        Returns:
            精确位次
        """
        # 获取该省份同分排序规则
        rules = self._get_same_score_rules(province, subject_type)

        if not rules:
            # 如果没有规则，返回估算位次
            return self._estimate_rank_by_score(province, score)

        # 模拟同分排序（实际应用中需要查询数据库）
        # 这里简化实现
        base_rank = self._estimate_rank_by_score(province, score)

        # 按规则调整位次
        adjusted_rank = self._adjust_rank_by_rules(
            base_rank,
            subject_scores,
            rules
        )

        return adjusted_rank

    def _get_same_score_rules(
        self,
        province: str,
        subject_type: str
    ) -> Optional[List[Dict[str, Any]]]:
        """获取同分排序规则"""
        if province in self.same_score_rules:
            return self.same_score_rules[province].get(subject_type)

        # 默认规则（理科）
        return [
            {"priority": 1, "field": "数学", "direction": "desc"},
            {"priority": 2, "field": "语文", "direction": "desc"},
            {"priority": 3, "field": "外语", "direction": "desc"}
        ]

    def _estimate_rank_by_score(self, province: str, score: int) -> int:
        """根据分数估算位次（简化版本）"""
        # 这里应该查询一分一段表
        # 简化实现
        if score >= 680:
            return 500
        elif score >= 650:
            return 2000
        elif score >= 600:
            return 8000
        else:
            return 20000

    def _adjust_rank_by_rules(
        self,
        base_rank: int,
        subject_scores: Dict[str, int],
        rules: List[Dict[str, Any]]
    ) -> int:
        """
        按同分规则调整位次

        同分考生中，单科成绩高的排在前
        """
        # 简化实现：根据单科成绩微调位次
        # 实际应用中需要查询所有同分考生数据

        math_score = subject_scores.get("数学", 0)
        chinese_score = subject_scores.get("语文", 0)
        english_score = subject_scores.get("外语", 0)

        # 单科成绩优秀，位次略微提前
        adjustment = 0
        if math_score >= 130:
            adjustment -= 5
        if chinese_score >= 125:
            adjustment -= 3
        if english_score >= 140:
            adjustment -= 2

        return base_rank + adjustment

    # ==================== 艺术类考生支持 ====================

    def calculate_art_comprehensive_score(
        self,
        cultural_score: int,
        art_score: int,
        province: str,
        major_type: str  # "美术", "音乐", "编导", "播音"
    ) -> float:
        """
        计算艺术类综合分

        各省公式不同：
        - 江苏：文化70% + 专业30%
        - 浙江：文化50% + 专业50%
        - 安徽：文化40% + 专业60%（美术）
        """
        # 省份权重映射
        weight_map = {
            "江苏": {
                "美术": (0.7, 0.3),
                "音乐": (0.6, 0.4),
                "编导": (0.7, 0.3),
                "播音": (0.6, 0.4)
            },
            "浙江": {
                "美术": (0.5, 0.5),
                "音乐": (0.5, 0.5),
                "编导": (0.5, 0.5),
                "播音": (0.5, 0.5)
            },
            "安徽": {
                "美术": (0.4, 0.6),
                "音乐": (0.4, 0.6),
                "编导": (0.5, 0.5),
                "播音": (0.5, 0.5)
            }
        }

        # 获取权重
        if province in weight_map and major_type in weight_map[province]:
            cultural_weight, art_weight = weight_map[province][major_type]
        else:
            # 默认5:5
            cultural_weight, art_weight = 0.5, 0.5

        # 计算综合分
        comprehensive_score = cultural_score * cultural_weight + art_score * art_weight

        return comprehensive_score

    # ==================== 体育类考生支持 ====================

    def calculate_pe_comprehensive_score(
        self,
        cultural_score: int,
        pe_score: int,
        province: str
    ) -> float:
        """
        计算体育类综合分

        大部分省份：文化分 + 体育分
        """
        # 各省体育综合分计算
        if province == "江苏":
            # 江苏：文化分 + 体育分
            return cultural_score + pe_score

        elif province == "浙江":
            # 浙江：文化分/2 + 体育分
            return cultural_score / 2 + pe_score

        else:
            # 默认：直接相加
            return cultural_score + pe_score


# 全局实例
boundary_scenario_service = BoundaryScenarioService()
