"""
增强PDF报告生成服务
生成完整的志愿填报建议PDF报告
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class EnhancedPDFReportService:
    """增强PDF报告生成服务"""

    def __init__(self):
        self.data_dir = Path("data")

    async def generate_volunteer_report(
        self,
        recommendation_result: Dict[str, Any],
    ) -> bytes:
        """
        从推荐结果生成PDF报告

        Args:
            recommendation_result: 推荐结果数据

        Returns:
            PDF bytes (HTML content for now)
        """

        if not recommendation_result.get("success"):
            raise ValueError("推荐结果无效")

        data = recommendation_result["data"]

        # 构建报告结构
        report_data = {
            "meta": {
                "title": "学锋志愿教练 - 智能志愿填报建议报告",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "3.0",
                "data_source": "全国2800所院校、518个专业、92个城市完整数据库"
            },
            "user_profile": self._format_user_profile_from_data(data),
            "recommendation_summary": self._generate_recommendation_summary(data),
            "detailed_recommendations": self._generate_detailed_recommendations(data),
            "analysis": self._generate_analysis_section(data),
            "appendix": self._generate_appendix(data)
        }

        # 导出为HTML格式（简化版本）
        html_content = self.export_to_html_from_data(report_data)

        # 返回HTML内容作为bytes
        return html_content.encode('utf-8')

    async def export_to_html(
        self,
        recommendation_result: Dict[str, Any],
    ) -> str:
        """
        从推荐结果导出HTML

        Args:
            recommendation_result: 推荐结果数据

        Returns:
            HTML内容
        """

        if not recommendation_result.get("success"):
            raise ValueError("推荐结果无效")

        data = recommendation_result["data"]

        # 构建报告结构
        report_data = {
            "meta": {
                "title": "学锋志愿教练 - 智能志愿填报建议报告",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "3.0",
                "data_source": "全国2800所院校、518个专业、92个城市完整数据库"
            },
            "user_profile": self._format_user_profile_from_data(data),
            "recommendation_summary": self._generate_recommendation_summary(data),
            "detailed_recommendations": self._generate_detailed_recommendations(data),
            "analysis": self._generate_analysis_section(data),
            "appendix": self._generate_appendix(data)
        }

        return self.export_to_html_from_data(report_data)

    def export_to_html_from_data(self, report_data: Dict[str, Any]) -> str:
        """从报告数据导出HTML"""
        return self._generate_html_template(report_data)

    def _format_user_profile_from_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """从数据格式化用户档案"""
        basic_info = data.get("basicInfo", data.get("basic_info", {}))

        return {
            "province": basic_info.get("province", "未知"),
            "score": basic_info.get("score", 0),
            "rank": basic_info.get("rank", "未提供"),
            "subject_type": basic_info.get("subjectType", basic_info.get("subject_type", "未知")),
            "target_majors": basic_info.get("targetMajors", basic_info.get("target_majors", [])),
            "score_level": self._get_score_level(basic_info.get("score", 0)),
            "competition_level": self._get_competition_level(
                basic_info.get("province", ""),
                basic_info.get("score", 0)
            )
        }

    def _get_score_level(self, score: int) -> str:
        """获取分数水平"""
        if score >= 650:
            return "顶尖水平"
        elif score >= 600:
            return "优秀水平"
        elif score >= 550:
            return "良好水平"
        elif score >= 500:
            return "中等水平"
        else:
            return "基础水平"

    def _get_competition_level(self, province: str, score: int) -> str:
        """获取竞争激烈程度"""
        if score >= 650:
            return "竞争非常激烈"
        elif score >= 600:
            return "竞争激烈"
        elif score >= 550:
            return "竞争适中"
        else:
            return "竞争相对较小"

    def _generate_recommendation_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成推荐摘要"""
        analysis = data.get("analysis", {})
        total_count = analysis.get("totalCount", analysis.get("total_count", 0))

        category_counts = analysis.get("categoryCounts", analysis.get("category_counts", {}))

        return {
            "overview": f"根据您的分数和条件，我们为您推荐了{total_count}所院校。",
            "recommended_strategy": "建议按照20%冲刺、40%稳妥、30%保底、10%垫底的比例填报。",
            "key_points": [
                f"共推荐{total_count}所院校",
                f"冲刺院校{category_counts.get('冲刺', category_counts.get('chong', 0))}所",
                f"稳妥院校{category_counts.get('稳妥', category_counts.get('wen', 0))}所",
                f"保底院校{category_counts.get('保底', category_counts.get('bao', 0))}所",
            ]
        }

    def _generate_detailed_recommendations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成详细推荐"""
        categories = {
            'chong': {'name': '冲刺', 'color': '#f44336', 'icon': '🚀'},
            'wen': {'name': '稳妥', 'color': '#4caf50', 'icon': '✅'},
            'bao': {'name': '保底', 'color': '#2196f3', 'icon': '⚓'},
            'dian': {'name': '垫底', 'color': '#ff9800', 'icon': '🛡️'}
        }

        detailed = {}
        for key, config in categories.items():
            recommendations = data.get(key, [])
            if recommendations:
                detailed[key] = {
                    "category_name": config['name'],
                    "color": config['color'],
                    "universities": [self._format_university(rec) for rec in recommendations[:10]]
                }

        return detailed

    def _format_university(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """格式化单个推荐院校"""
        employment = rec.get("employmentInfo", rec.get("employment_info", {}))
        highlights = rec.get("highlights", {})

        return {
            "university_name": rec.get("universityName", rec.get("university_name", "")),
            "major": rec.get("major", ""),
            "university_level": rec.get("universityLevel", rec.get("university_level", "")),
            "university_type": rec.get("universityType", rec.get("university_type", "")),
            "province": rec.get("province", ""),
            "city": rec.get("city", ""),
            "probability": rec.get("probability", 0),
            "score_gap": rec.get("scoreGap", rec.get("score_gap", 0)),
            "suggestions": rec.get("suggestions", []),
            "highlights": {
                "university": highlights.get("university", []),
                "major": highlights.get("major", [])
            },
            "employment": {
                "employment_rate": employment.get("employmentRate", employment.get("employment_rate", "未知")),
                "average_salary": employment.get("averageSalary", employment.get("average_salary", "未知")),
                "top_employers": employment.get("topEmployers", employment.get("top_employers", []))
            }
        }

    def _generate_analysis_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析章节"""
        basic_info = data.get("basicInfo", data.get("basic_info", {}))
        analysis = data.get("analysis", {})

        return {
            "score_analysis": {
                "score": basic_info.get("score", 0),
                "score_level": self._get_score_level(basic_info.get("score", 0)),
                "score_positioning": "您的分数处于" + self._get_score_level(basic_info.get("score", 0))
            },
            "category_analysis": {
                "total_count": analysis.get("totalCount", analysis.get("total_count", 0)),
                "balance_assessment": "推荐方案较为合理，建议根据实际情况调整"
            },
            "risk_analysis": {
                "overall_risk": "中等风险",
                "specific_risks": [
                    "冲刺院校录取概率较低，请谨慎填报",
                    "建议关注保底院校，确保有学可上",
                    "注意各院校的专业录取要求"
                ]
            }
        }

    def _generate_appendix(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成附录"""
        return {
            "data_sources": {
                "title": "数据来源",
                "sources": [
                    "全国2800所高等院校官方数据",
                    "2021-2025年各省录取分数线",
                    "518个本科专业详细介绍",
                    "92个热门城市就业数据"
                ]
            },
            "methodology": {
                "title": "推荐方法",
                "methods": [
                    "基于历史录取数据的概率分析",
                    "冲稳保垫四类分类策略",
                    "就业前景综合评估",
                    "个人偏好智能匹配"
                ]
            },
            "important_notes": {
                "title": "重要提示",
                "notes": [
                    "本报告仅供参考，不构成录取承诺",
                    "实际录取以官方公布为准",
                    "建议结合学校意见和个人情况",
                    "2026年分数线预计7月公布"
                ]
            },
            "contact_info": {
                "title": "咨询联系",
                "content": "如需更多帮助，请咨询专业志愿填报老师或使用学锋志愿教练的AI对话功能"
            },
            "disclaimer": self._get_full_disclaimer()
        }

    def _get_full_disclaimer(self) -> str:
        """获取完整免责声明"""
        return """
================================================================================
免责声明
================================================================================

1. 数据来源：
   本报告基于学锋志愿教练数据库生成，数据来源于：
   - 各省市教育考试院官方公布的信息
   - 各院校招生章程和官方发布的数据
   - 权威机构发布的排名和评估报告
   - 公开出版的统计年鉴和研究报告

2. 准确性声明：
   - 我们努力确保数据的准确性和时效性
   - 数据可能存在遗漏、延迟或解读错误
   - 最终数据以官方渠道发布为准

3. 参考性质：
   - 本报告仅供参考，不构成任何形式的录取承诺
   - 高考录取受多种因素影响，存在不确定性
   - 实际录取结果可能与预测存在偏差

4. 决策责任：
   - 志愿填报是重要的人生决策，请考生和家长谨慎决策
   - 建议结合官方信息、学校意见、个人情况综合考虑
   - 我们不对基于本建议做出的决策承担任何责任

5. 更新说明：
   - 本报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
   - 如需最新数据，请重新生成报告
   - 2026年实际分数线预计7月公布

6. 使用限制：
   - 本报告仅供个人参考，不得用于商业用途
   - 未经许可，不得转载或用于其他目的

================================================================================
感谢使用学锋志愿教练！祝您金榜题名！
================================================================================
        """.strip()

    def _generate_html_template(self, report_data: Dict[str, Any]) -> str:
        """生成HTML模板"""

        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 3px solid #1976D2;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #1976D2;
            margin-bottom: 10px;
            font-size: 28px;
        }}
        .header p {{
            color: #666;
            margin: 5px 0;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 25px;
            background: #f9f9f9;
            border-radius: 8px;
            border-left: 4px solid #1976D2;
        }}
        .section h2 {{
            color: #1976D2;
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 22px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}
        .info-item {{
            background: white;
            padding: 15px;
            border-radius: 6px;
        }}
        .info-label {{
            font-weight: 600;
            color: #666;
            margin-bottom: 5px;
        }}
        .info-value {{
            color: #333;
            font-size: 16px;
        }}
        .category {{
            margin-bottom: 25px;
            padding: 20px;
            border-left: 4px solid;
            background: white;
            border-radius: 6px;
        }}
        .category-chong {{ border-left-color: #f44336; }}
        .category-wen {{ border-left-color: #4caf50; }}
        .category-bao {{ border-left-color: #2196f3; }}
        .category-dian {{ border-left-color: #ff9800; }}

        .category h3 {{
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 18px;
        }}
        .university {{
            margin-bottom: 15px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 4px;
        }}
        .university h4 {{
            margin: 0 0 10px 0;
            color: #333;
            font-size: 16px;
        }}
        .tag {{
            display: inline-block;
            padding: 4px 10px;
            margin: 3px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        .tag-985 {{ background: #E3F2FD; color: #1976D2; }}
        .tag-211 {{ background: #E8F5E9; color: #4CAF50; }}
        .tag-double {{ background: #FFF3E0; color: #FF9800; }}
        .probability {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
        }}
        .prob-high {{ background: #4caf50; }}
        .prob-medium {{ background: #2196f3; }}
        .prob-low {{ background: #ff9800; }}
        .disclaimer {{
            font-size: 12px;
            color: #666;
            margin-top: 30px;
            padding: 20px;
            background: #FFF3E0;
            border-left: 4px solid #FF9800;
            border-radius: 6px;
        }}
        .analysis-box {{
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
        }}
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
            .section {{ page-break-inside: avoid; }}
            .university {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>生成时间: {generated_at}</p>
            <p>版本: {version} | 数据源: {data_source}</p>
        </div>

        {content}

        <div class="disclaimer">
            <h3>[!] 免责声明</h3>
            <p>{disclaimer_text}</p>
        </div>
    </div>
</body>
</html>
        """

        return html_template.format(
            title=report_data["meta"]["title"],
            generated_at=report_data["meta"]["generated_at"],
            version=report_data["meta"]["version"],
            data_source=report_data["meta"]["data_source"],
            content=self._generate_html_content(report_data),
            disclaimer_text=self._get_simple_disclaimer()
        )

    def _generate_html_content(self, report_data: Dict[str, Any]) -> str:
        """生成HTML内容"""
        content = []

        # 用户信息
        content.append(self._generate_user_profile_html(report_data["user_profile"]))

        # 推荐摘要
        content.append(self._generate_summary_html(report_data["recommendation_summary"]))

        # 详细推荐
        content.append(self._generate_recommendations_html(report_data["detailed_recommendations"]))

        # 分析章节
        content.append(self._generate_analysis_html(report_data["analysis"]))

        # 附录
        content.append(self._generate_appendix_html(report_data["appendix"]))

        return "\n".join(content)

    def _generate_user_profile_html(self, profile: Dict[str, Any]) -> str:
        """生成用户信息HTML"""
        majors = profile.get('target_majors', [])
        majors_text = '、'.join(majors) if majors else '未提供'

        return f"""
        <div class="section">
            <h2>[DATA] 考生信息</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">所在省份</div>
                    <div class="info-value">{profile['province']}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">高考分数</div>
                    <div class="info-value">{profile['score']}分</div>
                </div>
                <div class="info-item">
                    <div class="info-label">全省位次</div>
                    <div class="info-value">第{profile['rank']}名</div>
                </div>
                <div class="info-item">
                    <div class="info-label">报考科类</div>
                    <div class="info-value">{profile['subject_type']}</div>
                </div>
            </div>
            <div class="info-item">
                <div class="info-label">目标专业</div>
                <div class="info-value">{majors_text}</div>
            </div>
        </div>
        """

    def _generate_summary_html(self, summary: Dict[str, Any]) -> str:
        """生成摘要HTML"""
        points = summary.get('key_points', [])

        return f"""
        <div class="section">
            <h2>[DATA] 推荐摘要</h2>
            <p>{summary['overview']}</p>
            <p><strong>填报策略：</strong>{summary['recommended_strategy']}</p>
            <h3>关键要点</h3>
            <ul>
                {''.join([f"<li>{point}</li>" for point in points])}
            </ul>
        </div>
        """

    def _generate_recommendations_html(self, recommendations: Dict[str, Any]) -> str:
        """生成推荐HTML"""
        if not recommendations:
            return """
            <div class="section">
                <h2>[TARGET] 详细推荐</h2>
                <p>暂无推荐数据，请尝试调整查询条件。</p>
            </div>
            """

        html_parts = []

        for category_key, category_data in recommendations.items():
            category_name = category_data["category_name"]
            color = category_data["color"]
            universities = category_data["universities"]

            uni_html = []
            for uni in universities:
                prob_class = "prob-high" if uni["probability"] >= 75 else "prob-medium" if uni["probability"] >= 50 else "prob-low"

                uni_html.append(f"""
                <div class="university">
                    <h4>{uni['university_name']} ({uni['major']})</h4>
                    <div>
                        <span class="tag tag-985">{uni['university_level']}</span>
                        <span class="probability {prob_class}">
                            录取概率 {uni['probability']}%
                        </span>
                    </div>
                    <p><strong>地点：</strong>{uni['province']} {uni['city']}</p>
                    <p><strong>分数差距：</strong>{uni['score_gap']:+d}分</p>
                    <p><strong>就业信息：</strong>就业率 {uni['employment']['employment_rate']}，平均薪资 {uni['employment']['average_salary']}</p>
                </div>
                """)

            html_parts.append(f"""
            <div class="category category-{category_key}">
                <h3>{category_name}（{len(universities)}所）</h3>
                {''.join(uni_html)}
            </div>
            """)

        return f'<div class="section"><h2>[TARGET] 详细推荐</h2>{"".join(html_parts)}</div>'

    def _generate_analysis_html(self, analysis: Dict[str, Any]) -> str:
        """生成分析HTML"""
        return f"""
        <div class="section">
            <h2>[CHART] 分析报告</h2>
            <div class="analysis-box">
                <h3>分数分析</h3>
                <p><strong>分数：</strong>{analysis['score_analysis']['score']}分</p>
                <p><strong>层次：</strong>{analysis['score_analysis']['score_level']}</p>
                <p><strong>定位：</strong>{analysis['score_analysis']['score_positioning']}</p>
            </div>

            <div class="analysis-box">
                <h3>类别分析</h3>
                <p><strong>总院校数：</strong>{analysis['category_analysis']['total_count']}所</p>
                <p><strong>平衡性评估：</strong>{analysis['category_analysis']['balance_assessment']}</p>
            </div>

            <div class="analysis-box">
                <h3>风险分析</h3>
                <p><strong>整体风险：</strong>{analysis['risk_analysis']['overall_risk']}</p>
                <ul>
                    {''.join([f"<li>{risk}</li>" for risk in analysis['risk_analysis']['specific_risks']])}
                </ul>
            </div>
        </div>
        """

    def _generate_appendix_html(self, appendix: Dict[str, Any]) -> str:
        """生成附录HTML"""
        return f"""
        <div class="section">
            <h2>[BOOK] 附录</h2>
            <h3>{appendix['data_sources']['title']}</h3>
            <ul>
                {''.join([f"<li>{source}</li>" for source in appendix['data_sources']['sources']])}
            </ul>

            <h3>{appendix['methodology']['title']}</h3>
            <ul>
                {''.join([f"<li>{method}</li>" for method in appendix['methodology']['methods']])}
            </ul>

            <h3>{appendix['important_notes']['title']}</h3>
            <ul>
                {''.join([f"<li>{note}</li>" for note in appendix['important_notes']['notes']])}
            </ul>
        </div>
        """

    def _get_simple_disclaimer(self) -> str:
        """获取简版免责声明"""
        return """
本报告基于学锋志愿教练数据库生成，数据来源于官方公开信息，仅供参考。
最终录取以各省教育考试院官方公布为准。我们不对基于本建议做出的决策承担任何责任。
        """.strip()


# 全局实例
enhanced_pdf_service = EnhancedPDFReportService()
