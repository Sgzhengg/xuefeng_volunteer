"""
推荐结果校验模块
实现夸克算法的校验与反思层，提供风险预警和矛盾检测
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import os

class RecommendationValidator:
    """推荐结果校验器"""

    def __init__(self):
        # 功能开关
        self.validator_enabled = os.getenv("VALIDATOR_ENABLED", "true").lower() == "true"

    def validate_recommendation(
        self,
        user_input: Dict[str, Any],
        recommendation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        校验推荐结果

        Args:
            user_input: 用户输入信息
            recommendation: 推荐结果

        Returns:
            校验结果，包含warnings和errors
        """
        if not self.validator_enabled:
            return {"valid": True, "warnings": [], "errors": []}

        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "validated_at": datetime.now().isoformat()
        }

        # 1. 基础数据校验
        self._validate_basic_data(user_input, recommendation, validation_result)

        # 2. 冲突检测
        self._detect_conflicts(user_input, recommendation, validation_result)

        # 3. 风险预警
        self._risk_warning(user_input, recommendation, validation_result)

        # 4. 数据完整性校验
        self._validate_data_integrity(user_input, recommendation, validation_result)

        # 5. 比例合理性校验
        self._validate_category_ratio(recommendation, validation_result)

        return validation_result

    def _validate_basic_data(
        self,
        user_input: Dict[str, Any],
        recommendation: Dict[str, Any],
        validation_result: Dict[str, Any]
    ):
        """基础数据校验"""
        data = recommendation.get("data", recommendation)

        # 检查推荐数量
        total_count = 0
        for category in ["冲刺", "稳妥", "保底"]:
            schools = data.get(category, [])
            total_count += len(schools)

        if total_count == 0:
            validation_result["errors"].append("推荐结果为空，请检查数据完整性")
            validation_result["valid"] = False
        elif total_count < 3:
            validation_result["warnings"].append(f"推荐数量过少({total_count}所)，建议至少3-5所")

        # 检查用户输入的合理性
        score = user_input.get("score", 0)
        if score < 200 or score > 750:
            validation_result["errors"].append(f"用户分数异常: {score}，请检查输入")
            validation_result["valid"] = False

        province = user_input.get("province", "")
        if not province:
            validation_result["errors"].append("缺少省份信息")
            validation_result["valid"] = False

    def _detect_conflicts(
        self,
        user_input: Dict[str, Any],
        recommendation: Dict[str, Any],
        validation_result: Dict[str, Any]
    ):
        """冲突检测"""
        data = recommendation.get("data", recommendation)

        # 检查是否有重复推荐的院校
        all_schools = []
        for category in ["冲刺", "稳妥", "保底"]:
            schools = data.get(category, [])
            for school in schools:
                uni_name = school.get("university_name", "")
                major = school.get("major", "")
                key = f"{uni_name}-{major}"

                if key in all_schools:
                    validation_result["warnings"].append(f"重复推荐: {uni_name} {major}")
                else:
                    all_schools.append(key)

        # 检查分数梯度是否合理
        if len(all_schools) > 1:
            scores = []
            for category in ["冲刺", "稳妥", "保底"]:
                for school in data.get(category, []):
                    score_gap = school.get("score_gap", 0)
                    scores.append(score_gap)

            if scores and (max(scores) - min(scores)) < 10:
                validation_result["warnings"].append("推荐学校分数梯度过小，建议拉开差距")

    def _risk_warning(
        self,
        user_input: Dict[str, Any],
        recommendation: Dict[str, Any],
        validation_result: Dict[str, Any]
    ):
        """风险预警"""
        data = recommendation.get("data", recommendation)
        score = user_input.get("score", 0)

        # 检查冲刺比例过高
        chong_schools = len(data.get("冲刺", []))
        total_schools = sum(len(data.get(cat, [])) for cat in ["冲刺", "稳妥", "保底"])

        if total_schools > 0:
            chong_ratio = chong_schools / total_schools
            if chong_ratio > 0.4:
                validation_result["warnings"].append(
                    f"冲刺比例过高({chong_ratio:.1%})，建议控制在20%-30%"
                )

        # 检查低分学生推荐高分院校的风险
        if score < 400:
            high_level_count = 0
            for category in ["冲刺", "稳妥", "保底"]:
                for school in data.get(category, []):
                    level = school.get("university_level", "")
                    if level in ["985", "211"]:
                        high_level_count += 1

            if high_level_count > 2:
                validation_result["warnings"].append(
                    f"低分学生({score}分)推荐了{high_level_count}所985/211院校，风险较大"
                )

        # 检查保底不足
        bao_schools = len(data.get("保底", []))
        if bao_schools == 0 and total_schools > 0:
            validation_result["warnings"].append("缺少保底院校，建议增加1-2所保底学校")

    def _validate_data_integrity(
        self,
        user_input: Dict[str, Any],
        recommendation: Dict[str, Any],
        validation_result: Dict[str, Any]
    ):
        """数据完整性校验"""
        data = recommendation.get("data", recommendation)

        # 检查每个推荐学校是否包含必需字段
        required_fields = [
            "university_name", "university_level", "major",
            "probability", "score_gap", "category"
        ]

        for category in ["冲刺", "稳妥", "保底"]:
            schools = data.get(category, [])
            for i, school in enumerate(schools):
                missing_fields = []
                for field in required_fields:
                    if field not in school or school[field] is None:
                        missing_fields.append(field)

                if missing_fields:
                    validation_result["errors"].append(
                        f"第{i+1}个{category}推荐缺少字段: {', '.join(missing_fields)}"
                    )
                    validation_result["valid"] = False

        # 检查概率值是否在合理范围
        for category in ["冲刺", "稳妥", "保底"]:
            schools = data.get(category, [])
            for school in schools:
                probability = school.get("probability", 0)
                if not (0 <= probability <= 100):
                    validation_result["errors"].append(
                        f"{school.get('university_name', '')}的概率值异常: {probability}%"
                    )
                    validation_result["valid"] = False

    def _validate_category_ratio(
        self,
        recommendation: Dict[str, Any],
        validation_result: Dict[str, Any]
    ):
        """比例合理性校验（参考夸克标准）"""
        data = recommendation.get("data", recommendation)

        counts = {
            "冲刺": len(data.get("冲刺", [])),
            "稳妥": len(data.get("稳妥", [])),
            "保底": len(data.get("保底", []))
        }

        total = sum(counts.values())

        if total > 0:
            ratios = {cat: count / total for cat, count in counts.items()}

            # 夸克推荐比例参考：冲刺20%，稳妥40%，保底30%
            if abs(ratios.get("冲刺", 0) - 0.2) > 0.2:
                validation_result["warnings"].append(
                    f"冲刺比例({ratios.get('冲刺', 0):.1%})偏离夸克推荐标准(20%)较多"
                )

            if abs(ratios.get("稳妥", 0) - 0.4) > 0.3:
                validation_result["warnings"].append(
                    f"稳妥比例({ratios.get('稳妥', 0):.1%})偏离夸克推荐标准(40%)较多"
                )

            if abs(ratios.get("保底", 0) - 0.3) > 0.2:
                validation_result["warnings"].append(
                    f"保底比例({ratios.get('保底', 0):.1%})偏离夸克推荐标准(30%)较多"
                )

    def generate_validation_report(
        self,
        validation_result: Dict[str, Any]
    ) -> str:
        """生成校验报告"""
        if not validation_result.get("warnings") and not validation_result.get("errors"):
            return "✅ 推荐结果校验通过，无警告无错误"

        report = ["📋 推荐结果校验报告", ""]

        if validation_result.get("errors"):
            report.append("❌ 错误（必须修复）:")
            for error in validation_result["errors"]:
                report.append(f"  - {error}")
            report.append("")

        if validation_result.get("warnings"):
            report.append("⚠️  警告（建议关注）:")
            for warning in validation_result["warnings"]:
                report.append(f"  - {warning}")

        return "\n".join(report)


# 全局实例
recommendation_validator = RecommendationValidator()