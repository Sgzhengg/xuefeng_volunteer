#!/usr/bin/env python3
"""
清理语音聊天功能相关代码和数据
"""
import os
import json
import shutil
from pathlib import Path
import re

def cleanup_voice_features():
    """清理语音相关功能"""
    print("=== 清理语音聊天功能 ===")

    # 1. 检查并删除语音相关文件
    voice_files = [
        "lib/features/chat/widgets/voice_input_button.dart",
    ]

    deleted_files = []
    for file_path in voice_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted_files.append(file_path)
            print(f"[DELETE] {file_path}")

    # 2. 从pubspec.yaml移除语音依赖
    pubspec_path = "pubspec.yaml"
    if os.path.exists(pubspec_path):
        with open(pubspec_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 移除speech_to_text依赖
        if "speech_to_text: ^6.6.0" in content:
            content = content.replace("  speech_to_text: ^6.6.0\n", "")
            with open(pubspec_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[UPDATE] 从 pubspec.yaml 移除 speech_to_text 依赖")

    # 3. 清理import语句
    dart_files = list(Path("lib").rglob("*.dart"))
    updated_files = []

    for file_path in dart_files:
        if file_path.name == "voice_input_button.dart":
            continue  # 已经删除的文件

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 移除语音相关的import
        original_content = content
        content = re.sub(r"import\s+['\"][^'\"]*speech_to_text[^'\"]*['\"];?\n", "", content)
        content = re.sub(r"import\s+['\"][^'\"]*flutter_sound[^'\"]*['\"];?\n", "", content)
        content = re.sub(r"import\s+['\"][^'\"]*audioplayers[^'\"]*['\"];?\n", "", content)
        content = re.sub(r"import\s+['\"][^'\"]*record[^'\"]*['\"];?\n", "", content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            updated_files.append(str(file_path))
            print(f"[UPDATE] {file_path}")

    # 4. 清理语音相关的代码
    for file_path in dart_files:
        if file_path.name == "voice_input_button.dart":
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # 移除语音按钮相关代码
        content = re.sub(r"VoiceInputButton\s*\([^)]*\)", "", content)
        content = re.sub(r"voiceInputButton\s*\([^)]*\)", "", content)
        content = re.sub(r"\.VoiceInputButton\s*\([^)]*\)", "", content)

        # 移除语音相关的状态变量
        content = re.sub(r"bool\s+\w*Listening\s*=\s*false", "", content)
        content = re.sub(r"bool\s+\w*Recording\s*=\s*false", "", content)
        content = re.sub(r"VoidCallback\s+\w*OnPressed\s*=", "", content)

        # 移除语音相关的函数调用
        content = re.sub(r"\.startListening\(\)", "", content)
        content = re.sub(r"\.stopListening\(\)", "", content)
        content = re.sub(r"\.record\(\)", "", content)
        content = re.sub(r"\.stop\(\)", "", content)

        # 清理多余的逗号和括号
        content = re.sub(r",\s*,", ",", content)
        content = re.sub(r"\(\s*,\s*\)", "()", content)
        content = re.sub(r"\[\s*,\s*\]", "[]", content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            updated_files.append(str(file_path))
            print(f"[CLEAN] {file_path}")

    print(f"\n清理完成:")
    print(f"- 删除文件: {len(deleted_files)} 个")
    print(f"- 更新文件: {len(updated_files)} 个")

    return {
        "deleted_files": deleted_files,
        "updated_files": updated_files
    }

if __name__ == "__main__":
    result = cleanup_voice_features()