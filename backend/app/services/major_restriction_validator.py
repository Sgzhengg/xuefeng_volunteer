"""
专业限制规则校验器
检查学生是否符合专业的报考条件
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum


class RestrictionType(Enum):
    """限制类型"""
    SUBJECT_REQUIREMENT = "subject_requirement"  # 选科要求
    SCORE_REQUIREMENT = "score_requirement"  # 单科成绩要求
    GENDER_REQUIREMENT = "gender_requirement"  # 性别要求
    PHYSICAL_REQUIREMENT = "physical_requirement"  # 身体条件要求
    OTHER_REQUIREMENT = "other_requirement"  # 其他要求


class ValidationResult:
    """验证结果"""

    def __init__(self, is_valid: bool, restriction_type: RestrictionType = None,
                 reason: str = "", suggestion: str = ""):
        self.is_valid = is_valid
        self.restriction_type = restriction_type
        self.reason = reason
        self.suggestion = suggestion

    def to_dict(self) -> Dict:
        return {
            "is_valid": self.is_valid,
            "restriction_type": self.restriction_type.value if self.restriction_type else None,
            "reason": self.reason,
            "suggestion": self.suggestion
        }


class MajorRestrictionValidator:
    """专业限制规则校验器"""

    def __init__(self):
        self.data_dir = Path("data")
        self._load_restriction_rules()

    def _load_restriction_rules(self):
        """加载专业限制规则"""
        print("Loading major restriction rules...")

        try:
            with open(self.data_dir / "major_restriction_rules.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.restriction_rules = data.get("rules", [])
            print(f"Loaded {len(self.restriction_rules)} restriction rules")
        except FileNotFoundError:
            print("Warning: major_restriction_rules.json not found, using default rules")
            self.restriction_rules = self._get_default_rules()
            self._save_default_rules()

    def _get_default_rules(self) -> List[Dict]:
        """获取默认限制规则"""
        return [
            # 选科要求
            {
                "rule_id": "SUBJ_001",
                "rule_type": "subject_requirement",
                "major_keywords": ["计算机科学与技术", "软件工程", "人工智能", "电子信息工程"],
                "subject_requirements": {
                    "physics": "required",  # 必选物理
                    "chemistry": "optional"
                },
                "description": "理工科专业通常要求必选物理"
            },
            {
                "rule_id": "SUBJ_002",
                "rule_type": "subject_requirement",
                "major_keywords": ["临床医学", "口腔医学", "中医学"],
                "subject_requirements": {
                    "physics": "required",
                    "chemistry": "required",
                    "biology": "required"
                },
                "description": "医学专业通常要求物理、化学、生物"
            },
            {
                "rule_id": "SUBJ_003",
                "rule_type": "subject_requirement",
                "major_keywords": ["数学与应用数学", "统计学", "物理学"],
                "subject_requirements": {
                    "physics": "required",
                    "math": "strongly_recommended"
                },
                "description": "数学、物理类专业要求必选物理"
            },
            {
                "rule_id": "SUBJ_004",
                "rule_type": "subject_requirement",
                "major_keywords": ["化学", "生物科学", "材料科学"],
                "subject_requirements": {
                    "chemistry": "required",
                    "physics": "optional"
                },
                "description": "化学、生物类专业通常要求必选化学"
            },
            {
                "rule_id": "SUBJ_005",
                "rule_type": "subject_requirement",
                "major_keywords": ["汉语言文学", "历史学", "哲学"],
                "subject_requirements": {
                    "history": "preferred",
                    "politics": "preferred"
                },
                "description": "文史类专业偏好历史、政治"
            },
            # 单科成绩要求
            {
                "rule_id": "SCORE_001",
                "rule_type": "score_requirement",
                "major_keywords": ["英语", "翻译", "商务英语"],
                "score_requirements": {
                    "english": {
                        "min_score": 100,
                        "min_percentile": 80
                    }
                },
                "description": "英语专业要求英语成绩较好"
            },
            {
                "rule_id": "SCORE_002",
                "rule_type": "score_requirement",
                "major_keywords": ["数学与应用数学", "统计学"],
                "score_requirements": {
                    "math": {
                        "min_score": 110,
                        "min_percentile": 85
                    }
                },
                "description": "数学专业要求数学成绩优秀"
            },
            {
                "rule_id": "SCORE_003",
                "rule_type": "score_requirement",
                "major_keywords": ["建筑学", "城市规划", "工业设计"],
                "score_requirements": {
                    "art_foundation": "required",  # 需要美术基础
                    "drawing_test": "required"  # 需要加试绘画
                },
                "description": "建筑学、城市规划专业通常需要美术基础"
            },
            # 身体条件要求
            {
                "rule_id": "PHYS_001",
                "rule_type": "physical_requirement",
                "major_keywords": ["临床医学", "护理学", "医学影像学"],
                "physical_requirements": {
                    "vision": {
                        "corrected": ">4.8",  # 矫正视力要求
                        "color_blindness": "not_allowed"
                    },
                    "other": "无传染性疾病"
                },
                "description": "医学专业对身体条件有严格要求"
            },
            {
                "rule_id": "PHYS_002",
                "rule_type": "physical_requirement",
                "major_keywords": ["航海技术", "轮机工程"],
                "physical_requirements": {
                    "vision": {
                        "uncorrected": ">5.0",
                        "color_blindness": "not_allowed"
                    },
                    "height": {
                        "min": 165
                    }
                },
                "description": "航海类专业对身体条件有特殊要求"
            },
            # 其他要求
            {
                "rule_id": "OTHER_001",
                "rule_type": "other_requirement",
                "major_keywords": ["法学", "哲学"],
                "other_requirements": {
                    "oral_communication": "strongly_recommended"  # 口头表达能力
                },
                "description": "法学、哲学专业对语言表达能力要求较高"
            }
        ]

    def _save_default_rules(self):
        """保存默认规则到文件"""
        output_data = {
            "metadata": {
                "version": "1.0.0",
                "total_rules": len(self.restriction_rules),
                "description": "专业报考限制规则库"
            },
            "rules": self.restriction_rules
        }

        with open(self.data_dir / "major_restriction_rules.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(self.restriction_rules)} default rules to major_restriction_rules.json")

    def validate_major(self, major_name: str, student_profile: Dict) -> ValidationResult:
        """
        验证学生是否符合某个专业的报考条件

        Args:
            major_name: 专业名称
            student_profile: 学生档案
                {
                    "subjects": {"physics": true, "chemistry": false, ...},
                    "subject_scores": {"english": 120, "math": 130, ...},
                    "gender": "male/female",
                    "vision": {"corrected": "5.0", "color_blindness": false},
                    "height": 175
                }

        Returns:
            ValidationResult: 验证结果
        """
        # 查找适用的规则
        applicable_rules = self._find_applicable_rules(major_name)

        if not applicable_rules:
            # 没有适用规则，默认允许
            return ValidationResult(is_valid=True)

        # 逐个验证规则
        for rule in applicable_rules:
            result = self._validate_rule(rule, student_profile)
            if not result.is_valid:
                return result

        # 所有规则都通过
        return ValidationResult(is_valid=True)

    def _find_applicable_rules(self, major_name: str) -> List[Dict]:
        """查找适用于某个专业的规则"""
        applicable_rules = []

        for rule in self.restriction_rules:
            # 检查专业关键词是否匹配
            major_keywords = rule.get("major_keywords", [])
            if any(keyword in major_name for keyword in major_keywords):
                applicable_rules.append(rule)

        return applicable_rules

    def _validate_rule(self, rule: Dict, student_profile: Dict) -> ValidationResult:
        """验证单个规则"""
        rule_type = rule.get("rule_type")

        if rule_type == "subject_requirement":
            return self._validate_subject_requirement(rule, student_profile)
        elif rule_type == "score_requirement":
            return self._validate_score_requirement(rule, student_profile)
        elif rule_type == "physical_requirement":
            return self._validate_physical_requirement(rule, student_profile)
        elif rule_type == "other_requirement":
            return self._validate_other_requirement(rule, student_profile)
        else:
            return ValidationResult(is_valid=True)

    def _validate_subject_requirement(self, rule: Dict, student_profile: Dict) -> ValidationResult:
        """验证选科要求"""
        subject_requirements = rule.get("subject_requirements", {})
        student_subjects = student_profile.get("subjects", {})

        for subject, requirement in subject_requirements.items():
            student_selected = student_subjects.get(subject, False)

            if requirement == "required" and not student_selected:
                return ValidationResult(
                    is_valid=False,
                    restriction_type=RestrictionType.SUBJECT_REQUIREMENT,
                    reason=f"该专业要求必选{self._translate_subject(subject)}",
                    suggestion=f"建议选修{self._translate_subject(subject)}课程"
                )
            elif requirement == "strongly_recommended" and not student_selected:
                return ValidationResult(
                    is_valid=True,  # 不强制，但给出警告
                    restriction_type=RestrictionType.SUBJECT_REQUIREMENT,
                    reason=f"该专业建议选修{self._translate_subject(subject)}",
                    suggestion=f"推荐选修{self._translate_subject(subject)}课程以提高录取概率"
                )

        return ValidationResult(is_valid=True)

    def _validate_score_requirement(self, rule: Dict, student_profile: Dict) -> ValidationResult:
        """验证单科成绩要求"""
        score_requirements = rule.get("score_requirements", {})
        student_scores = student_profile.get("subject_scores", {})

        for subject, requirement in score_requirements.items():
            if isinstance(requirement, dict):
                student_score = student_scores.get(subject, 0)

                # 检查最低分要求
                min_score = requirement.get("min_score")
                if min_score and student_score < min_score:
                    return ValidationResult(
                        is_valid=False,
                        restriction_type=RestrictionType.SCORE_REQUIREMENT,
                        reason=f"该专业要求{self._translate_subject(subject)}成绩≥{min_score}分",
                        suggestion=f"当前{self._translate_subject(subject)}成绩为{student_score}分，建议选择其他专业"
                    )

                # 检查百分位要求
                min_percentile = requirement.get("min_percentile")
                if min_percentile:
                    # 这里需要更复杂的逻辑来计算百分位
                    # 简化实现：假设学生成绩已经足够
                    pass

            elif requirement == "required":
                # 特殊要求（如美术基础）
                art_foundation = student_profile.get("art_foundation", False)
                if not art_foundation:
                    return ValidationResult(
                        is_valid=False,
                        restriction_type=RestrictionType.SCORE_REQUIREMENT,
                        reason="该专业需要美术基础或参加绘画加试",
                        suggestion="建议选择其他专业，或提前准备美术基础"
                    )

        return ValidationResult(is_valid=True)

    def _validate_physical_requirement(self, rule: Dict, student_profile: Dict) -> ValidationResult:
        """验证身体条件要求"""
        physical_requirements = rule.get("physical_requirements", {})
        student_physical = student_profile.get("physical", {})

        # 视力要求
        vision_requirements = physical_requirements.get("vision", {})
        if vision_requirements:
            student_vision = student_physical.get("vision", {})

            # 检查矫正视力
            corrected_min = vision_requirements.get("corrected")
            if corrected_min and student_vision.get("corrected"):
                # 简化比较，实际需要更复杂的逻辑
                pass

            # 检查色盲
            color_blindness = vision_requirements.get("color_blindness")
            if color_blindness == "not_allowed" and student_vision.get("color_blindness"):
                return ValidationResult(
                    is_valid=False,
                    restriction_type=RestrictionType.PHYSICAL_REQUIREMENT,
                    reason="该专业不允许色盲/色弱",
                    suggestion="建议选择其他专业"
                )

        # 身高要求
        height_requirements = physical_requirements.get("height")
        if height_requirements:
            min_height = height_requirements.get("min")
            student_height = student_physical.get("height")
            if min_height and student_height and student_height < min_height:
                return ValidationResult(
                    is_valid=False,
                    restriction_type=RestrictionType.PHYSICAL_REQUIREMENT,
                    reason=f"该专业要求身高≥{min_height}cm",
                    suggestion=f"当前身高{student_height}cm不满足要求，建议选择其他专业"
                )

        return ValidationResult(is_valid=True)

    def _validate_other_requirement(self, rule: Dict, student_profile: Dict) -> ValidationResult:
        """验证其他要求"""
        # 简化实现：其他要求通常不强制限制
        return ValidationResult(is_valid=True)

    def _translate_subject(self, subject: str) -> str:
        """翻译科目名称"""
        translations = {
            "physics": "物理",
            "chemistry": "化学",
            "biology": "生物",
            "history": "历史",
            "politics": "政治",
            "geography": "地理",
            "english": "英语",
            "math": "数学"
        }
        return translations.get(subject, subject)

    def batch_validate_majors(self, major_list: List[str],
                             student_profile: Dict) -> Dict[str, ValidationResult]:
        """
        批量验证多个专业

        Args:
            major_list: 专业列表
            student_profile: 学生档案

        Returns:
            Dict[str, ValidationResult]: 专业名 -> 验证结果
        """
        results = {}

        for major in major_list:
            results[major] = self.validate_major(major, student_profile)

        return results


# 全局实例
major_restriction_validator = MajorRestrictionValidator()


def main():
    """主函数"""
    print("=" * 60)
    print("专业限制规则校验器")
    print("=" * 60)

    # 创建校验器实例
    validator = MajorRestrictionValidator()

    # 测试用例1：理工科专业
    print("\n[测试1] 验证计算机科学与技术专业")
    student_profile_1 = {
        "subjects": {"physics": True, "chemistry": False},
        "subject_scores": {"math": 130, "english": 120}
    }
    result_1 = validator.validate_major("计算机科学与技术", student_profile_1)
    print(f"结果: {'通过' if result_1.is_valid else '不通过'}")
    if not result_1.is_valid:
        print(f"原因: {result_1.reason}")
        print(f"建议: {result_1.suggestion}")

    # 测试用例2：医学专业
    print("\n[测试2] 验证临床医学专业")
    student_profile_2 = {
        "subjects": {"physics": True, "chemistry": True, "biology": False},
        "physical": {
            "vision": {"color_blindness": False}
        }
    }
    result_2 = validator.validate_major("临床医学", student_profile_2)
    print(f"结果: {'通过' if result_2.is_valid else '不通过'}")
    if not result_2.is_valid:
        print(f"原因: {result_2.reason}")
        print(f"建议: {result_2.suggestion}")

    # 测试用例3：英语专业
    print("\n[测试3] 验证英语专业")
    student_profile_3 = {
        "subjects": {"physics": False, "history": True},
        "subject_scores": {"english": 95, "math": 110}
    }
    result_3 = validator.validate_major("英语", student_profile_3)
    print(f"结果: {'通过' if result_3.is_valid else '不通过'}")
    if not result_3.is_valid:
        print(f"原因: {result_3.reason}")
        print(f"建议: {result_3.suggestion}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
