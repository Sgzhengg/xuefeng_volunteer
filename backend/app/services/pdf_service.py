from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.schemas import ChatMessage


class PDFReportService:
    """志愿建议 PDF 报告生成服务"""

    def __init__(self):
        pass

    async def generate_volunteer_report(
        self,
        user_profile: Dict[str, Any],
        chat_history: List[ChatMessage],
        data_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        生成志愿建议 PDF 报告

        返回报告的结构化数据（实际 PDF 由前端生成）
        """

        # 提取关键信息
        report_data = {
            "title": "学锋志愿教练 - 志愿填报建议报告",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_profile": self._format_user_profile(user_profile),
            "data_summary": self._extract_data_summary(data_context),
            "key_recommendations": self._extract_key_recommendations(chat_history),
            "chat_summary": self._summarize_chat(chat_history),
            "disclaimer": self._get_disclaimer(),
        }

        return {
            "success": True,
            "data": report_data,
        }

    def _format_user_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """格式化用户档案"""
        return {
            "分数": profile.get("score", "N/A"),
            "省份": profile.get("province", "N/A"),
            "选科": profile.get("selected_subjects", "N/A"),
            "家庭背景": profile.get("family_background", "N/A"),
            "兴趣方向": profile.get("interests", "N/A"),
        }

    def _extract_data_summary(
        self,
        data_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """提取数据摘要"""
        if not data_context:
            return {"提示": "暂无数据"}

        summary = {}

        # 录取概率数据
        if "admission_probability" in data_context:
            prob_data = data_context["admission_probability"]
            summary["录取概率"] = {
                "院校": prob_data.get("university_name"),
                "专业": prob_data.get("major_name"),
                "概率": f"{prob_data.get('probability', 0)}%",
                "预测结论": prob_data.get("prediction"),
            }

        # 院校信息
        if "university_info" in data_context:
            info = data_context["university_info"]
            summary["院校详情"] = {
                "名称": info.get("name"),
                "层次": info.get("level"),
                "类型": info.get("type"),
                "2024排名": info.get("ranking2024"),
                "就业率": f"{info.get('employment_rate', 0) * 100}%",
                "平均薪资": f"{info.get('avg_salary', 0)}元/月",
            }

        # 专业就业数据
        if "major_employment" in data_context:
            employment = data_context["major_employment"]
            summary["专业就业"] = {
                "专业": employment.get("major_name"),
                "就业率": f"{employment.get('employment_rate', 0) * 100}%",
                "平均薪资": f"{employment.get('avg_salary', 0)}元/月",
                "就业趋势": employment.get("employment_trend"),
                "AI冲击": employment.get("ai_impact"),
            }

        return summary

    def _extract_key_recommendations(
        self,
        chat_history: List[ChatMessage]
    ) -> List[str]:
        """提取关键建议"""
        recommendations = []

        for msg in chat_history:
            if msg.role == "assistant":
                content = msg.content
                # 提取包含明确建议的句子
                if "建议" in content or "推荐" in content or "千万别" in content:
                    # 简单提取前几句
                    sentences = content.split("。")
                    for sentence in sentences[:3]:
                        if len(sentence) > 10:
                            recommendations.append(sentence.strip())

        return recommendations[:5]  # 最多返回5条

    def _summarize_chat(
        self,
        chat_history: List[ChatMessage]
    ) -> Dict[str, Any]:
        """总结对话内容"""
        summary = {
            "total_messages": len(chat_history),
            "user_questions": [],
            "key_topics": [],
        }

        for msg in chat_history:
            if msg.role == "user":
                summary["user_questions"].append(msg.content[:50] + "..." if len(msg.content) > 50 else msg.content)

        return summary

    def _get_disclaimer(self) -> str:
        """获取免责声明"""
        return """
免责声明：
1. 本报告基于咕咕数据2026最新预测和AI分析生成
2. 所有建议仅供参考，不代表官方立场
3. 最终志愿填报以各省教育考试院官方公布为准
4. 我们不对基于本建议做出的决策承担任何责任
5. 数据和预测可能存在误差，请谨慎参考
        """.strip()


# 全局实例
pdf_service = PDFReportService()
