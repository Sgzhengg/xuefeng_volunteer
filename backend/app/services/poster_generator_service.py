# -*- coding: utf-8 -*-
"""
可分享海报生成服务
生成包含推荐结果的精美海报，用于社交分享
"""

from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime


class PosterGeneratorService:
    """海报生成服务"""

    def __init__(self):
        self.output_dir = Path("reports/posters")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_recommendation_poster(
        self,
        recommendation_data: Dict[str, Any],
        user_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成推荐结果海报

        Args:
            recommendation_data: 推荐结果数据
            user_info: 用户信息

        Returns:
            海报信息，包含文件路径和分享文本
        """

        # 提取基本信息
        basic_info = recommendation_data.get("basic_info", {})
        user_rank = basic_info.get("rank", 0)
        province = basic_info.get("province", "")
        subject_type = basic_info.get("subject_type", "")

        # 提取推荐结果（前6个）
        recommendations = self._extract_top_recommendations(recommendation_data)

        # 生成海报内容
        poster_content = self._generate_poster_content(
            user_rank, province, subject_type, recommendations
        )

        # 生成分享文案
        share_text = self._generate_share_text(
            user_rank, province, recommendations
        )

        # 保存海报内容（在实际实现中，这里会生成图片）
        poster_file = self._save_poster(poster_content, user_rank)

        return {
            "poster_content": poster_content,
            "poster_file": str(poster_file),
            "share_text": share_text,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _extract_top_recommendations(
        self,
        recommendation_data: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """提取前6个推荐结果（冲/稳/保各2个）"""

        top_recommendations = {
            "冲刺": [],
            "稳妥": [],
            "保底": []
        }

        # 提取各类推荐的前2个
        for category in ["冲刺", "稳妥", "保底"]:
            recommendations = recommendation_data.get(category, [])
            top_recommendations[category] = recommendations[:2]

        return top_recommendations

    def _generate_poster_content(
        self,
        user_rank: int,
        province: str,
        subject_type: str,
        recommendations: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """生成海报内容结构"""

        return {
            "title": "[EDU] 雪峰志愿推荐方案",
            "user_info": {
                "rank": f"{user_rank:,}",
                "province": province,
                "subject_type": subject_type
            },
            "recommendations": recommendations,
            "brand": {
                "name": "雪峰志愿",
                "slogan": "智能志愿填报，精准录取预测",
                "qrcode": "雪峰志愿小程序码"  # 实际实现中会是图片路径
            },
            "styling": {
                "background_color": "#1976D2",
                "text_color": "#333333",
                "accent_color": "#FF9800"
            }
        }

    def _generate_share_text(
        self,
        user_rank: int,
        province: str,
        recommendations: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """生成分享文案"""

        # 统计推荐数量
        chong_count = len(recommendations.get("冲刺", []))
        wen_count = len(recommendations.get("稳妥", []))
        bao_count = len(recommendations.get("保底", []))

        share_text = f"""
[EDU] 我的雪峰志愿推荐方案

📍 {province}考生 | 位次：{user_rank:,}

✨ 推荐院校：
• 冲刺 {chong_count}所：{', '.join([r['university_name'] for r in recommendations.get('冲刺', [])])}
• 稳妥 {wen_count}所：{', '.join([r['university_name'] for r in recommendations.get('稳妥', [])])}
• 保底 {bao_count}所：{', '.join([r['university_name'] for r in recommendations.get('保底', [])])}

[DATA] 基于真实录取数据，AI智能推荐
[TARGET] 精准位次预测，科学志愿填报

扫码获取你的专属推荐方案 ↓
【雪峰志愿小程序】

#高考志愿 #志愿填报 #大学推荐
        """.strip()

        return share_text

    def _save_poster(
        self,
        poster_content: Dict[str, Any],
        user_rank: int
    ) -> Path:
        """保存海报内容"""

        # 在实际实现中，这里会生成图片文件
        # 现在我们先保存为JSON文件作为示例
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"poster_{user_rank}_{timestamp}.json"
        file_path = self.output_dir / filename

        import json
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(poster_content, f, ensure_ascii=False, indent=2)

        return file_path

    def generate_text_poster(
        self,
        poster_content: Dict[str, Any]
    ) -> str:
        """生成文本版海报（用于文本分享）"""

        user_info = poster_content["user_info"]
        recommendations = poster_content["recommendations"]

        text_poster = f"""
╔═══════════════════════════════════════╗
║        [EDU] 雪峰志愿推荐方案          ║
╚═══════════════════════════════════════╝

📍 考生信息
   省份：{user_info['province']}
   位次：{user_info['rank']}
   科类：{user_info['subject_type']}

[TARGET] 推荐方案

┌─ 冲刺院校 ─────────────────────┐
│{'📘 ' + ' | '.join([r['university_name'][:8] for r in recommendations.get('冲刺', [])])}│
└──────────────────────────────────┘

┌─ 稳妥院校 ─────────────────────┐
│{'📗 ' + ' | '.join([r['university_name'][:8] for r in recommendations.get('稳妥', [])])}│
└──────────────────────────────────┘

┌─ 保底院校 ─────────────────────┐
│{'📙 ' + ' | '.join([r['university_name'][:8] for r in recommendations.get('保底', [])])}│
└──────────────────────────────────┘

═════════════════════════════════════
  🤖 雪峰志愿  |  智能志愿填报助手
═════════════════════════════════════

[PHONE] 扫码获取你的专属推荐方案
【雪峰志愿小程序】

[HOT] 基于真实录取数据 | 精准位次预测
        """.strip()

        return text_poster

    def generate_mini_program_code(self, user_id: str = None) -> str:
        """生成小程序码（示例实现）"""

        # 在实际实现中，这里会调用微信API生成小程序码
        # 现在返回示例路径
        if user_id:
            return f"/miniprogram/code?user_id={user_id}"
        else:
            return "/miniprogram/code_default"


# 全局实例
poster_generator_service = PosterGeneratorService()