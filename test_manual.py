#!/usr/bin/env python3
"""
张学锋AI手动测试脚本
"""

import requests
import json
import sys

# 后端API地址
API_URL = "http://localhost:8000/api/v1/chat"

# 测试问题列表
test_questions = [
    {
        "name": "计算机专业推荐",
        "question": "老师，我理科620分，想报计算机专业，您觉得怎么样？"
    },
    {
        "name": "天坑专业劝退",
        "question": "老师，我孩子想学生物工程专业，您觉得靠谱吗？"
    },
    {
        "name": "低分考生",
        "question": "老师，我只有350分，只能上专科，有什么专业推荐吗？"
    },
    {
        "name": "师范专业",
        "question": "老师，女孩580分，想当老师，报师范大学怎么样？"
    },
    {
        "name": "专业对比",
        "question": "老师，计算机和电子信息，选哪个更好？"
    }
]

def test_ai_chat(question_text):
    """测试AI聊天"""
    print("=" * 80)
    print(f"问题：{question_text}")
    print("=" * 80)
    print()

    try:
        # 发送请求
        response = requests.post(
            API_URL,
            json={
                "message": question_text,
                "context": {},
                "conversation_history": None
            },
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                ai_answer = result.get('response', '')
                print("AI回答：")
                print(ai_answer)
                print()

                # 分析回答质量
                analyze_answer(ai_answer)
            else:
                print(f"错误：{result.get('message', '未知错误')}")
        else:
            print(f"HTTP错误：{response.status_code}")
            print(f"响应内容：{response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端API")
        print("请确保后端服务已启动：")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ 发生错误：{e}")

    print()

def analyze_answer(answer):
    """分析AI回答质量"""
    print("=" * 80)
    print("回答质量分析")
    print("=" * 80)

    # 检查数据引用
    has_2025_data = "2025年" in answer or "2025数据" in answer
    print(f"✅ 数据引用（2025年数据）：{'是' if has_2025_data else '否 ❌'}")

    # 检查明确判断
    has_judgment = any(word in answer for word in ['能报就报', '千万别报', '闭眼报', '想都别想', '必须', '一定'])
    print(f"✅ 明确判断：{'是' if has_judgment else '否 ❌'}")

    # 检查东北话
    northeast_words = ['我跟你说', '你听我说', '咱', '整', '咋了', '哎呀', '必须的', '肯定']
    found_northeast = [word for word in northeast_words if word in answer]
    print(f"✅ 东北话词汇：{len(found_northeast)}个 - {found_northeast[:3] if found_northeast else '无 ❌'}")

    # 检查绝对化表达
    absolute_words = ['能报就报', '闭眼报', '千万别报', '想都别想', '铁律', '必须', '一定', '绝对']
    found_absolute = [word for word in absolute_words if word in answer]
    print(f"✅ 绝对化表达：{len(found_absolute)}个 - {found_absolute[:3] if found_absolute else '无 ❌'}")

    # 检查反问句
    has_questions = ('?' in answer or '吗' in answer or '你想想' in answer)
    print(f"✅ 反问句：{'是' if has_questions else '否 ❌'}")

    # 检查短句
    sentences = [s.strip() for s in answer.split('。') if s.strip()]
    if sentences:
        short_sentences = [s for s in sentences if len(s) <= 20]
        short_ratio = len(short_sentences) / len(sentences)
        print(f"✅ 短句比例：{short_ratio*100:.1f}% {'✅' if short_ratio >= 0.7 else '⚠️'}")

    # 计算总分
    score = 0
    if has_2025_data: score += 20
    if has_judgment: score += 20
    score += min(len(found_northeast) * 3, 15)
    score += min(len(found_absolute) * 3, 15)
    if has_questions: score += 10
    if sentences and short_ratio >= 0.7: score += 20

    print()
    print(f"📊 总分：{score}/100 {'✅ 优秀' if score >= 80 else '⚠️  良好' if score >= 60 else '❌ 需改进'}")

    print()

def main():
    """主函数"""
    print("=" * 80)
    print("张学锋AI - 手动测试")
    print("=" * 80)
    print()
    print("后端API地址：", API_URL)
    print("测试问题数量：", len(test_questions))
    print()
    print("提示：确保后端服务已启动")
    print("  cd backend")
    print("  uvicorn app.main:app --reload")
    print()
    print("=" * 80)
    print()

    # 询问是否开始
    user_input = input("按Enter开始测试，输入q退出：")
    if user_input.lower() == 'q':
        print("测试取消")
        return

    # 测试所有问题
    for i, test in enumerate(test_questions, 1):
        print(f"\n【测试 {i}/{len(test_questions)}】{test['name']}")
        test_ai_chat(test['question'])

        # 询问是否继续
        if i < len(test_questions):
            user_input = input("\n按Enter继续下一个测试，输入q退出：")
            if user_input.lower() == 'q':
                break

    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
    print()
    print("💡 提示：")
    print("  - 如果总分 < 60分，说明需要优化SKILL.md")
    print("  - 如果数据引用缺失，检查后端是否正确加载SKILL.md")
    print("  - 如果风格分数低，考虑增强东北话和绝对化表达")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(0)
