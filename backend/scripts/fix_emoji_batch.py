# -*- coding: utf-8 -*-
"""
批量移除后端代码中的emoji字符

功能：
1. 扫描backend/app目录下所有.py文件
2. 将emoji字符替换为纯文本标记
3. 添加UTF-8编码声明
4. 生成修复报告

使用方法：
    python fix_emoji_batch.py

作者：学锋志愿教练团队
版本：1.0.0
"""

import os
import re
from pathlib import Path
from typing import Dict, List

# ==================== emoji替换映射 ====================

EMOJI_REPLACEMENTS = {
    '✅': '[OK]',
    '❌': '[ERROR]',
    '⚠️': '[WARN]',
    '🔥': '[HOT]',
    '💰': '[PROFIT]',
    '🎉': '[SUCCESS]',
    '📊': '[DATA]',
    '🔧': '[FIX]',
    '🚀': '[DEPLOY]',
    '🟢': '[ON]',
    '🔴': '[OFF]',
    '📁': '[FILE]',
    '🐛': '[BUG]',
    '🆕': '[NEW]',
    '🎯': '[TARGET]',
    '📈': '[UP]',
    '🔍': '[SEARCH]',
    '🎓': '[EDU]',
    '📝': '[NOTE]',
    '⚡': '[FAST]',
    '💡': '[IDEA]',
    '🏆': '[TOP]',
    '⭐': '[STAR]',
    '👍': '[GOOD]',
    '👎': '[BAD]',
    '🔔': '[NOTIFY]',
    '📱': '[PHONE]',
    '💻': '[LAPTOP]',
    '🌟': '[SHINE]',
    '🎨': '[ART]',
    '🎪': '[CIRCUS]',
    '🎭': '[MASK]',
    '🎢': '[MOVIE]',
    '🎮': '[GAME]',
    '🏃': '[RUN]',
    '🚶': '[WALK]',
    '🛒': '[CART]',
    '🚌': '[BUS]',
    '🚗': '[CAR]',
    '🚕': '[TAXI]',
    '🚙': '[TRUCK]',
    '✈️': '[PLANE]',
    '🚂': '[TRAIN]',
    '🚃': '[TRAM]',
    '🚢': '[SHIP]',
    '⛵': '[BOAT]',
    '⛽': '[GAS]',
    '🚁': '[HOUSE]',
    '🏢': '[BUILDING]',
    '🏠': '[HOME]',
    '🏥': '[HOSPITAL]',
    '🏫': '[SCHOOL]',
    '🏭': '[FACTORY]',
    '⛪': '[CHURCH]',
    '🕌': '[MOSQUE]',
    '🗼': '[SHRINE]',
    '🕍': '[SYNAGOGUE]',
    '⛲': '[FOUNTAIN]',
    '⛺': '[MOUNTAIN]',
    '🏰': '[CASTLE]',
    '🗼': '[MUSEUM]'
}

# ==================== 批量修复函数 ====================

def scan_py_files(directory: Path) -> List[Path]:
    """
    扫描目录中的所有.py文件

    Args:
        directory: 要扫描的目录

    Returns:
        Python文件列表
    """
    py_files = []

    for root, dirs, files in os.walk(directory):
        # 排除虚拟环境目录
        if 'venv' in root or '__pycache__' in root:
            continue

        for file in files:
            if file.endswith('.py'):
                py_files.append(Path(root) / file)

    return py_files

def fix_emoji_in_file(file_path: Path) -> Dict:
    """
    修复单个文件中的emoji字符

    Args:
        file_path: 文件路径

    Returns:
        修复统计信息
    """
    stats = {
        "file": str(file_path),
        "original_size": 0,
        "modified": False,
        "emoji_found": {},
        "errors": []
    }

    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        stats["original_size"] = len(content)

        # 检查是否已有编码声明
        has_encoding = content.startswith('# -*- coding:') or content.startswith('# coding:')

        # 查找并替换emoji
        modified_content = content
        emoji_counts = {}

        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            count = modified_content.count(emoji)
            if count > 0:
                emoji_counts[emoji] = count
                modified_content = modified_content.replace(emoji, replacement)

        if emoji_counts:
            stats["emoji_found"] = emoji_counts
            stats["modified"] = True

        # 添加编码声明（如果需要）
        if not has_encoding and (stats["modified"] or stats["emoji_found"]):
            # 在第一行添加编码声明
            if content.startswith('#!'):
                # 如果有shebang，在第二行添加
                lines = modified_content.split('\n')
                lines.insert(1, '# -*- coding: utf-8 -*-')
                modified_content = '\n'.join(lines)
            else:
                # 否则在第一行添加
                modified_content = '# -*- coding: utf-8 -*-\n' + modified_content

        # 如果有修改，写回文件
        if stats["modified"]:
            # 创建备份
            backup_path = file_path.with_suffix('.py.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # 写入修复后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)

            stats["backup_created"] = str(backup_path)
            print(f"[FIXED] {file_path.name}: {sum(emoji_counts.values())} emoji替换")

        return stats

    except Exception as e:
        stats["errors"].append(str(e))
        print(f"[ERROR] 处理文件失败 {file_path.name}: {e}")
        return stats

def batch_fix_emoji(target_directory: Path):
    """
    批量修复目录中的emoji字符

    Args:
        target_directory: 目标目录
    """
    print("=" * 60)
    print("批量emoji字符修复工具")
    print("=" * 60)
    print(f"[TARGET] 目标目录: {target_directory}")

    # 扫描Python文件
    print("[SCAN] 正在扫描Python文件...")
    py_files = scan_py_files(target_directory)
    print(f"[OK] 找到 {len(py_files)} 个Python文件")

    # 修复每个文件
    print("[FIX] 开始修复emoji字符...")
    results = []
    total_emoji_fixed = 0

    for file_path in py_files:
        result = fix_emoji_in_file(file_path)
        results.append(result)
        total_emoji_fixed += sum(result["emoji_found"].values())

    # 生成报告
    modified_files = [r for r in results if r["modified"]]
    files_with_errors = [r for r in results if r["errors"]]

    print("=" * 60)
    print("[SUCCESS] 批量修复完成！")
    print(f"[STATS] 扫描文件: {len(py_files)}")
    print(f"[STATS] 修复文件: {len(modified_files)}")
    print(f"[STATS] emoji替换总数: {total_emoji_fixed}")
    print(f"[STATS] 错误文件: {len(files_with_errors)}")
    print("=" * 60)

    if modified_files:
        print("[DETAIL] 修复的文件:")
        for result in modified_files:
            print(f"  - {result['file']}: {result['emoji_found']}")

    if files_with_errors:
        print("[ERROR] 处理失败的文件:")
        for result in files_with_errors:
            print(f"  - {result['file']}: {result['errors']}")

    # 保存修复报告
    report_file = "emoji_fix_report.json"
    import json
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "target_directory": str(target_directory),
            "total_files_scanned": len(py_files),
            "files_modified": len(modified_files),
            "total_emoji_fixed": total_emoji_fixed,
            "files_with_errors": len(files_with_errors),
            "details": results
        }, f, ensure_ascii=False, indent=2)

    print(f"[REPORT] 详细报告已保存: {report_file}")

# ==================== 主程序入口 ====================

if __name__ == "__main__":
    # 目标目录
    target_dir = Path("../app")

    if not target_dir.exists():
        print(f"[ERROR] 目标目录不存在: {target_dir}")
        print("[INFO] 请从backend/scripts目录运行此脚本")
        exit(1)

    try:
        batch_fix_emoji(target_dir)
    except Exception as e:
        print(f"[ERROR] 批量修复失败: {e}")
        import traceback
        print(traceback.format_exc())
        exit(1)