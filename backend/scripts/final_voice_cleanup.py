#!/usr/bin/env python3
"""
最终清理语音相关代码
"""
import re
from pathlib import Path

def clean_speech_imports():
    """清理SpeechToText导入"""
    dart_files = list(Path("lib").rglob("*.dart"))

    for file_path in dart_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # 移除SpeechToText导入和实例化
        content = re.sub(r"import\s+['\"][^'\"]*speech_to_text[^'\"]*['\"];?\n", "", content)
        content = re.sub(r"final SpeechToText _speechToText = SpeechToText\(\)\s*;", "", content)
        content = re.sub(r"final\s+SpeechToText\s+\w*\s*=\s*SpeechToText\(\)\s*;", "", content)

        # 移除语音相关的变量
        content = re.sub(r"bool\s+\w*Listening\s*=\s*false", "", content)
        content = re.sub(r"bool\s+\w*isListening\s*=\s*false", "", content)

        # 移除语音初始化函数
        content = re.sub(r"void _initSpeechRecognition\(\).*?\n\s*\}", "", content, flags=re.DOTALL)

        # 移除语音处理函数
        content = re.sub(r"void _toggleVoiceInput\(\).*?\n\s*\}", "", content, flags=re.DOTALL)

        # 移除语音相关的函数调用
        content = re.sub(r"_toggleVoiceInput\(\)", "", content)
        content = re.sub(r"_speechToText\.initialize\([^)]*\)", "", content)
        content = re.sub(r"_speechToText\.listen\([^)]*\)", "", content)
        content = re.sub(r"_speechToText\.stop\(\)", "", content)

        # 清理语音相关的UI代码
        content = re.sub(r"VoiceInputButton\s*\([^)]*\)", "", content)
        content = re.sub(r"\.VoiceInputButton\s*\([^)]*\)", "", content)
        content = re.sub(r"\.value\s*\?\s*VoiceInputButton[^:]*:\s*Container", "Container", content)

        # 清理多余的空行和逗号
        content = re.sub(r",\s*,", ",", content)
        content = re.sub(r"\(\s*,\s*\)", "()", content)
        content = re.sub(r"\[\s*,\s*\]", "[]", content)
        content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[CLEAN] {file_path}")

def check_remaining_speech_code():
    """检查剩余的语音代码"""
    dart_files = list(Path("lib").rglob("*.dart"))
    issues = []

    for file_path in dart_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().lower()

        # 检查是否还有语音相关的代码
        if any(keyword in content for keyword in ["speech", "voice", "speech_to_text", "listen", "microphone"]):
            issues.append(str(file_path))

    return issues

if __name__ == "__main__":
    print("=== 最终语音代码清理 ===")

    # 执行清理
    clean_speech_imports()

    # 检查剩余问题
    remaining_issues = check_remaining_speech_code()

    print(f"\n清理完成！")
    if remaining_issues:
        print(f"\n[WARN] 以下文件仍可能包含语音代码:")
        for file in remaining_issues:
            print(f"  - {file}")
    else:
        print("\n[OK] 所有语音代码已清理干净")