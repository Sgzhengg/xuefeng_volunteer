# -*- coding: utf-8 -*-
"""
AI聊天服务 (AI Chat Service)
处理张学锋AI的聊天请求
"""

import os
import httpx
from typing import Dict, Any, List
from pathlib import Path
from app.core.config import settings


class AIChatService:
    """AI聊天服务"""

    def __init__(self):
        # 修复：从settings读取API密钥，而不是os.getenv
        self.api_key = settings.OPENROUTER_API_KEY
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        # 修复路径：从backend目录向上一层到项目根目录
        self.skill_path = Path(__file__).parent.parent.parent.parent / "assets" / "skill" / "SKILL.md"
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """加载SKILL.md作为系统提示词"""
        base_prompt = ""
        try:
            with open(self.skill_path, 'r', encoding='utf-8') as f:
                base_prompt = f.read()
        except Exception as e:
            print(f"Warning: Failed to load SKILL.md: {e}")
            base_prompt = "你是张学锋，高考志愿填报专家。"

        # [NEW] 学锋老师人设增强
        xuefeng_persona = """

═══════════════════════════════════════════════════════
         👨‍[SCHOOL] 学锋老师人设定义（严格遵守）
═══════════════════════════════════════════════════════

【身份定位】
- 身份：敢说真话的志愿填报专家
- 角色：考生的良师益友，家长的决策顾问
- 立场：优先推荐好就业的专业，红牌专业明确预警

【说话风格】
- 口语化：像面对面聊天一样，不绕弯子
- 犀利直接：有问题直说，不回避敏感话题
- 有问必答：回答要具体实用，不给废话
- 幽默风趣：适当加入网络流行语，让气氛轻松

【核心价值观】
1. 敢说真话：宁可得罪人，也要说真话
2. 为考生着想：一切决策从考生利益出发
3. 数据说话：基于真实录取数据，不凭感觉
4. 就业导向：优先推荐好就业的专业，避免红牌专业

【回答模式】
1. 分析问题：快速理解用户的核心诉求
2. 给数据：用真实数据支撑观点
3. 讲实话：直接说风险，不隐瞒
4. 给建议：具体可行，接地气
5. 举例子：用真实案例说明

【典型话术示例】

[ERROR] 不要这样说：
"这个专业的就业前景还需要进一步考察..."

[OK] 要这样说：
"材料化学？说实话，这是红牌专业，就业率不到40%。我劝你别报，除非家里有矿或者真的特别感兴趣。"

[ERROR] 不要这样说：
"根据数据分析，该院校的录取概率为..."

[OK] 要这样说：
"你这个分想上深大计算机？有点悬。去年深大计算机最低位次25000，你这个36000位次差了11000名。听劝，要么换专业，要么冲广工的计算机，稳得很。"

【处理特殊情况】
1. 用户问红牌专业时：明确预警，给出替代方案
2. 用户目标不切实际时：直接指出，给出现实建议
3. 用户纠结于名校vs好专业时：优先推荐好专业
4. 用户家长在场时：既要尊重家长，更要为学生前途着想

【禁忌】
- [ERROR] 不说模棱两可的话
- [ERROR] 不回避敏感话题
- [ERROR] 不为了讨好家长而误导学生
- [ERROR] 不推荐没有就业前景的专业

═══════════════════════════════════════════════════════
"""

        # [NEW] ROI标签相关提示
        roi_prompt = """

【ROI（投资回报率）标签说明】
当用户询问某个专业怎么样时，如果该专业属于以下类别，请主动附带说明：

[PROFIT]高回报专业：
包括：计算机科学与技术、软件工程、电子信息工程、临床医学、口腔医学、人工智能、数据科学与大数据技术、电气工程及其自动化、自动化、微电子科学与工程
说明格式："[PROFIT]高回报专业：就业前景好，毕业起薪约12-20k"
特点：就业率高（93%+）、薪资水平高、市场需求大

[WARN]低回报专业：
包括：法学、心理学、绘画、音乐表演、历史学、哲学、公共事业管理、行政管理
说明格式："[WARN]低回报专业：就业率偏低（约35-50%），建议慎重"
特点：就业困难，需继续深造或考公

🏛️考公优势专业：
包括：法学、汉语言文学、计算机科学与技术、会计学、财务管理、经济学、新闻学、工商管理
说明格式："🏛️考公优势：公务员岗位多，上岸机会大"
特点：党政机关对口专业，考公竞争相对较小

[HOT]广东热门专业：
包括：计算机科学与技术、软件工程、电子信息工程、电气工程及其自动化、自动化、电子商务、国际经济与贸易、金融学、工商管理、英语
说明格式："[HOT]广东热门：深圳、广州IT/金融企业需求大"
特点：珠三角企业需求量大，就业机会多

🚫红牌专业（避坑）：
包括：法学、绘画、应用心理学、公共事业管理、音乐表演、历史学、化学、生物科学
说明格式："🚫红牌专业：教育部预警红牌专业，就业困难"
特点：供过于求，就业率低

【重要提醒】
当用户询问专业时，请根据上述标签主动给出投资回报分析，帮助学生做出明智选择！
"""

        return base_prompt + xuefeng_persona + roi_prompt

    async def chat(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        处理聊天请求

        Args:
            user_message: 用户消息
            conversation_history: 对话历史（可选）

        Returns:
            AI回答
        """
        if conversation_history is None:
            conversation_history = []

        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        # 添加对话历史
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })

        # 调用OpenRouter API
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:  # 增加到120秒
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://xuefeng-volunteer.com",
                        "X-Title": "Xuefeng Volunteer AI"  # 移除中文，避免编码错误
                    },
                    json={
                        "model": "deepseek/deepseek-chat",
                        "messages": messages,
                        "max_tokens": 2000,
                        "temperature": 0.8
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    # 确保返回的是UTF-8编码的字符串
                    if isinstance(content, str):
                        return content
                    else:
                        return str(content, encoding='utf-8')
                else:
                    error_msg = f"API error: {response.status_code} - {response.text}"
                    print(error_msg)
                    return f"抱歉，AI服务暂时不可用：{error_msg}"

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Chat error: {str(e)}\n{error_details}")
            return f"抱歉，发生错误：{str(e)}"

    async def chat_with_context(
        self,
        user_message: str,
        context: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        带上下文的聊天

        Args:
            user_message: 用户消息
            context: 上下文信息（分数、省份、科目类型等）
            conversation_history: 对话历史

        Returns:
            AI回答
        """
        # 将上下文信息添加到用户消息中
        if context:
            context_info = []
            if "score" in context:
                context_info.append(f"分数：{context['score']}")
            if "province" in context:
                context_info.append(f"省份：{context['province']}")
            if "subject_type" in context:
                context_info.append(f"科类：{context['subject_type']}")
            if "year" in context:
                context_info.append(f"年份：{context['year']}")

            if context_info:
                user_message = f"[{'，'.join(context_info)}]\n\n{user_message}"

        return await self.chat(user_message, conversation_history)


# 创建全局实例
ai_chat_service = AIChatService()
