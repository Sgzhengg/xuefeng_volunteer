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
        try:
            with open(self.skill_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Failed to load SKILL.md: {e}")
            return "你是张学锋，高考志愿填报专家。"

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
