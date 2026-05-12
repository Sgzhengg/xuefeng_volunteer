# -*- coding: utf-8 -*-
"""
志愿表与方案评估服务
评估用户的志愿填报方案是否合理，提供风险预警和建议
"""

from typing import Dict, List, Any
from datetime import datetime


class PlanEvaluatorService:
    """志愿表评估服务"""

    def __init__(self):
        pass

    def evaluate_volunteer_plan(
        self,
        volunteer_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        评估志愿填报方案

        Args:
            volunteer_plan: 志愿方案
                {
                    "user_info": {"rank": 10000, "province": "广东"},
                    "volunteers": [
                        {"university_name": "中山大学", "major": "计算机", "category": "冲刺"},
                        ...
                    ]
                }

        Returns:
            评估结果
                {
                    "overall_score": 85,
                    "risk_level": "low",
                    "warnings": [],
                    "suggestions": [],
                    "statistics": {...}
                }
        """

        volunteers = volunteer_plan.get("volunteers", [])
        user_info = volunteer_plan.get("user_info", {})

        # 统计各类数量
        stats = self._calculate_statistics(volunteers)

        # 风险检查
        warnings = self._check_risks(stats)

        # 生成建议
        suggestions = self._generate_suggestions(stats, warnings, user_info)

        # 计算总体评分
        overall_score = self._calculate_overall_score(stats, warnings)

        # 确定风险等级
        risk_level = self._determine_risk_level(overall_score, warnings)

        return {
            "overall_score": overall_score,
            "risk_level": risk_level,
            "warnings": warnings,
            "suggestions": suggestions,
            "statistics": stats,
            "evaluated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _calculate_statistics(self, volunteers: List[Dict]) -> Dict[str, Any]:
        """计算志愿表统计信息"""

        # 按类别统计
        category_counts = {"冲刺": 0, "稳妥": 0, "保底": 0}
        category_details = {"冲刺": [], "稳妥": [], "保底": []}

        for vol in volunteers:
            category = vol.get("category", "稳妥")
            if category in category_counts:
                category_counts[category] += 1
                category_details[category].append(vol)

        total = len(volunteers)

        # 计算比例
        ratios = {}
        if total > 0:
            for cat, count in category_counts.items():
                ratios[cat] = f"{count / total * 100:.1f}%"

        return {
            "total_count": total,
            "category_counts": category_counts,
            "category_ratios": ratios,
            "category_details": category_details,
        }

    def _check_risks(self, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查风险项"""

        warnings = []
        counts = stats["category_counts"]

        # 风险1: 冲刺志愿过多
        chong_count = counts.get("冲刺", 0)
        if chong_count > 6:
            warnings.append({
                "type": "high_risk",
                "category": "冲刺过多",
                "message": f"[WARN] 冲刺志愿有{chong_count}个，建议控制在6个以内",
                "current_value": chong_count,
                "recommended_value": "≤6",
                "severity": "high" if chong_count > 8 else "medium"
            })

        # 风险2: 保底志愿不足
        bao_count = counts.get("保底", 0)
        if bao_count < 3:
            warnings.append({
                "type": "high_risk",
                "category": "保底不足",
                "message": f"[WARN] 保底志愿仅{bao_count}个，建议增加1-2个保底院校",
                "current_value": bao_count,
                "recommended_value": "≥3",
                "severity": "high" if bao_count == 0 else "medium"
            })

        # 风险3: 稳妥+保底偏少
        wen_bao_count = counts.get("稳妥", 0) + bao_count
        if wen_bao_count < 10:
            warnings.append({
                "type": "medium_risk",
                "category": "稳妥保底不足",
                "message": f"[WARN] 稳妥+保底志愿仅{wen_bao_count}个，建议增加到10个以上",
                "current_value": wen_bao_count,
                "recommended_value": "≥10",
                "severity": "medium"
            })

        # 风险4: 总数不足
        total = stats["total_count"]
        if total < 15:
            warnings.append({
                "type": "medium_risk",
                "category": "总数不足",
                "message": f"[WARN] 志愿总数仅{total}个，建议填报15-20个志愿",
                "current_value": total,
                "recommended_value": "15-20",
                "severity": "medium"
            })

        return warnings

    def _generate_suggestions(
        self,
        stats: Dict[str, Any],
        warnings: List[Dict[str, Any]],
        user_info: Dict[str, Any]
    ) -> List[str]:

        """生成改进建议"""

        suggestions = []
        counts = stats["category_counts"]
        total = stats["total_count"]

        # 针对冲刺过多的建议
        if counts.get("冲刺", 0) > 6:
            suggestions.append(
                f"[IDEA] 建议：可考虑将部分冲刺志愿调整为稳妥院校，如：广东工业大学、深圳大学"
            )

        # 针对保底不足的建议
        if counts.get("保底", 0) < 3:
            province = user_info.get("province", "广东")
            suggestions.append(
                f"[IDEA] 建议：可考虑添加{province}本地院校作为保底，提高录取安全性"
            )

        # 针对总数不足的建议
        if total < 15:
            suggestions.append(
                "[IDEA] 建议：当前志愿数偏少，建议增加到15-20个以覆盖更多录取机会"
            )

        # 理想比例建议
        if total > 0:
            chong_ratio = counts.get("冲刺", 0) / total
            bao_ratio = counts.get("保底", 0) / total

            if chong_ratio > 0.4:
                suggestions.append(
                    "[IDEA] 建议：理想志愿比例为 冲刺20% | 稳妥50% | 保底30%，当前冲刺比例偏高"
                )
            elif bao_ratio < 0.2:
                suggestions.append(
                    "[IDEA] 建议：理想志愿比例为 冲刺20% | 稳妥50% | 保底30%，当前保底比例偏低"
                )

        # 如果没有风险，给出正面反馈
        if not warnings:
            suggestions.append(
                "[OK] 志愿结构合理，冲刺、稳妥、保底比例均衡，录取把握较大"
            )

        return suggestions

    def _calculate_overall_score(
        self,
        stats: Dict[str, Any],
        warnings: List[Dict[str, Any]]
    ) -> int:
        """计算总体评分（0-100）"""

        score = 100

        # 根据风险扣分
        for warning in warnings:
            severity = warning.get("severity", "low")
            if severity == "high":
                score -= 15
            elif severity == "medium":
                score -= 8
            else:
                score -= 3

        # 数量加分
        total = stats["total_count"]
        if 15 <= total <= 25:
            score += 5
        elif total > 25:
            score -= 5  # 过多也不好

        # 确保分数在0-100范围内
        return max(0, min(100, score))

    def _determine_risk_level(
        self,
        score: int,
        warnings: List[Dict[str, Any]]
    ) -> str:
        """确定风险等级"""

        if score >= 80:
            return "low"  # 低风险
        elif score >= 60:
            return "medium"  # 中等风险
        else:
            return "high"  # 高风险

    def generate_plan_summary(
        self,
        volunteer_plan: Dict[str, Any]
    ) -> str:
        """生成志愿方案摘要（用于分享）"""

        evaluation = self.evaluate_volunteer_plan(volunteer_plan)
        stats = evaluation["statistics"]
        user_info = volunteer_plan.get("user_info", {})

        summary = f"""
📋 我的志愿表评估

冲刺: {stats['category_counts']['冲刺']}个 | 稳妥: {stats['category_counts']['稳妥']}个 | 保底: {stats['category_counts']['保底']}个

总体评分: {evaluation['overall_score']}分
风险等级: {evaluation['risk_level'].upper()}
"""

        if evaluation["warnings"]:
            summary += f"\n[WARN] 发现{len(evaluation['warnings'])}个风险：\n"
            for warning in evaluation["warnings"]:
                summary += f"  - {warning['message']}\n"

        if evaluation["suggestions"]:
            summary += f"\n[IDEA] 改进建议：\n"
            for suggestion in evaluation["suggestions"][:2]:  # 只显示前2条
                summary += f"  {suggestion}\n"

        summary += f"\n[DATA] 评估时间: {evaluation['evaluated_at']}"

        return summary.strip()


# 全局实例
plan_evaluator_service = PlanEvaluatorService()