"""
清理 major_rank_data.json 中的数字ID院校名称

问题：34条记录的 university_name 字段是纯数字院校代码（如"10558"）而非实际名称
方案：基于教育部标准院校代码建立映射表，自动修复

使用方法：
    cd backend
    python scripts/clean_data_ids.py
"""

import json
import os
import sys
import io
import shutil
from pathlib import Path
from datetime import datetime

# 设置控制台编码为UTF-8以兼容中文和特殊字符
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ==================== 教育部院校代码到名称的映射 ====================
# 来源：中华人民共和国教育部《全国高等学校名单》
# 这些代码是从 major_rank_data.json 中实际发现的数字ID

MOE_CODE_TO_NAME = {
    # 广东省重点高校
    "10558": "中山大学",
    "10561": "华南理工大学",
    "10559": "暨南大学",
    "10574": "华南师范大学",
    "10564": "华南农业大学",
    "10590": "深圳大学",
    "11078": "广州大学",
    "11845": "广东工业大学",
    "10592": "广东财经大学",
    "10586": "广州医科大学",
    "10572": "广州中医药大学",
    "10566": "广东海洋大学",
    "10571": "广东医科大学",
    "10568": "广东药科大学",
    "10579": "岭南师范学院",
    "10582": "嘉应学院",
    # 民办/独立学院
    "12575": "广州华立学院",
    "12059": "广东培正学院",
}

# ==================== 数据文件路径 ====================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "major_rank_data.json"
BACKUP_DIR = DATA_DIR / "backups"


def ensure_dirs():
    """确保必要的目录存在"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def backup_original(filepath: Path) -> Path:
    """备份原始文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"major_rank_data_backup_{timestamp}.json"
    shutil.copy2(filepath, backup_path)
    print(f"[备份] 原始数据已备份到: {backup_path}")
    return backup_path


def find_actual_mapping(records: list) -> dict:
    """
    从现有数据中尝试找出 university_code -> university_name 的映射
    作为硬编码映射的补充
    """
    additional_mapping = {}
    for record in records:
        code = str(record.get("university_code", "")).strip()
        name = str(record.get("university_name", "")).strip()
        # 只采纳有效的名称映射
        if (code and name and not name.isdigit()
                and code not in MOE_CODE_TO_NAME
                and code not in additional_mapping):
            additional_mapping[code] = name

    print(f"[发现] 从数据中自动提取了 {len(additional_mapping)} 条额外映射")
    return additional_mapping


def clean_university_ids():
    """
    主清洗流程：
    1. 加载数据
    2. 建立完整映射表
    3. 清洗所有数字ID
    4. 生成清洗报告
    5. 保存清洗后数据
    """
    ensure_dirs()

    # 1. 加载数据
    print(f"[加载] 正在读取: {INPUT_FILE}")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])
    print(f"[统计] 总记录数: {len(records):,}")

    # 2. 建立完整映射（硬编码 + 自动发现）
    auto_mapping = find_actual_mapping(records)
    complete_mapping = {**auto_mapping, **MOE_CODE_TO_NAME}  # MOE优先

    # 3. 清洗数据
    print("\n" + "=" * 60)
    print("[清洗] 开始清洗数字ID院校名称...")
    print("=" * 60)

    fixed_count = 0
    unfixed = []
    skipped_count = 0

    for record in records:
        uni_name = str(record.get("university_name", "")).strip()

        if not uni_name:
            continue

        # 检查是否为纯数字
        if uni_name.isdigit():
            if uni_name in complete_mapping:
                old_name = uni_name
                record["university_name"] = complete_mapping[uni_name]
                fixed_count += 1
                print(f"  [OK] {old_name} -> {complete_mapping[uni_name]} "
                      f"(rank={record.get('min_rank')}, major={record.get('major_name')})")
            else:
                unfixed.append(uni_name)
                print(f"  [FAIL] 未找到映射: {uni_name} "
                      f"(rank={record.get('min_rank')}, major={record.get('major_name')})")

    # 4. 统计清洗结果
    print("\n" + "=" * 60)
    print("[清洗报告]")
    print("=" * 60)
    print(f"  总记录数:       {len(records):,}")
    print(f"  修复成功:       {fixed_count}")
    print(f"  无法修复:       {len(unfixed)}")
    print(f"  跳过（已有名称）: {len(records) - fixed_count - len(unfixed):,}")

    if unfixed:
        unfixed_unique = sorted(set(unfixed))
        print(f"\n  未能修复的ID列表: {unfixed_unique}")

    # 5. 验证数据分布
    print("\n[验证] 数据分布检查...")
    gd_2025 = [r for r in records if r.get("province") == "广东" and r.get("year") == 2025]
    print(f"  广东2025总记录数: {len(gd_2025):,}")

    # 检查各种排名段分布
    rank_ranges = [
        (1, 10000, "1-10000 (顶尖)"),
        (10001, 30000, "10001-30000 (重点)"),
        (30001, 70000, "30001-70000 (一本)"),
        (70001, 120000, "70001-120000 (二本)"),
        (120001, 200000, "120001-200000 (民办)"),
        (200001, 350000, "200001-350000 (专科)"),
    ]

    numeric_after = 0
    for r in records:
        if str(r.get("university_name", "")).isdigit():
            numeric_after += 1

    for lo, hi, desc in rank_ranges:
        count = sum(1 for r in gd_2025 if lo <= r.get("min_rank", 0) <= hi)
        bar = "█" * (count // 5) if count > 0 else ""
        print(f"    {desc}: {count:>4} 条 {bar}")

    print(f"\n  残留数字ID名称: {numeric_after} 条")

    # 6. 保存清洗后数据
    output_file = DATA_DIR / "major_rank_data_cleaned.json"
    print(f"\n[保存] 写入清洗后数据: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[完成] 数据清洗完成！")
    print(f"  原始数据备份: {BACKUP_DIR}")
    print(f"  清洗后数据: {output_file}")

    return fixed_count, len(unfixed)


if __name__ == "__main__":
    clean_university_ids()
