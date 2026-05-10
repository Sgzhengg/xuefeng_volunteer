#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理所有模拟/占位符数据，只保留真实录取数据

功能：
1. 删除 major_rank_data.json 中的占位符记录
2. 删除标记为 mock_data 的记录
3. 删除模拟数据文件
4. 生成清理报告

使用方法：
    python scripts/clean_mock_data.py [--dry-run]

作者：学锋志愿教练团队
日期：2026-05-10
"""

import json
import sys
import re
import shutil
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict


class MockDataCleaner:
    """模拟数据清理器"""

    def __init__(self, data_dir: str = "data", dry_run: bool = False):
        self.data_dir = Path(data_dir)
        self.dry_run = dry_run
        self.stats = defaultdict(int)

        # 占位符模式
        self.placeholder_patterns = [
            r"一般院校\d+",
            r"院校\d+",
            r"学院\d+",
            r"未知",
            r"待定",
            r"占位",
            r"TBD",
            r"模拟",
            r"mock",
        ]

    def clean_all(self) -> bool:
        """执行完整的清理流程"""
        print("=" * 70)
        print("模拟数据清理工具")
        print("=" * 70)
        print()
        if self.dry_run:
            print("[DRY RUN] 预演模式，不会实际修改文件")
        print()

        # 步骤1：清理主数据文件中的占位符
        self._clean_main_data_file()

        # 步骤2：删除模拟数据文件
        self._delete_mock_files()

        # 步骤3：生成清理报告
        self._generate_report()

        print("\n" + "=" * 70)
        if self.dry_run:
            print("[DRY RUN] 预演完成")
        else:
            print("[SUCCESS] 清理完成！")
        print("=" * 70)

        return True

    def _clean_main_data_file(self):
        """清理主数据文件中的占位符"""
        print("[STEP 1/3] 清理主数据文件...")

        main_data_path = self.data_dir / "major_rank_data.json"

        if not main_data_path.exists():
            print("[WARNING] 主数据文件不存在: {main_data_path}")
            return

        # 加载数据
        with open(main_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            records = data.get("major_rank_data", [])

        print(f"[INFO] 原始记录数: {len(records):,}条")

        # 分类记录
        cleaned_records = []
        removed_records = []

        for record in records:
            if self._is_mock_record(record):
                removed_records.append(record)
            else:
                cleaned_records.append(record)

        # 统计
        self.stats["original_records"] = len(records)
        self.stats["removed_records"] = len(removed_records)
        self.stats["cleaned_records"] = len(cleaned_records)

        # 分析删除原因
        removal_reasons = self._analyze_removal_reasons(removed_records)

        print(f"[OK] 清理分析完成:")
        print(f"  - 保留真实记录: {len(cleaned_records):,}条")
        print(f"  - 删除模拟记录: {len(removed_records):,}条")
        print()
        print("[删除原因统计]")
        for reason, count in removal_reasons.items():
            print(f"  - {reason}: {count:,}条")

        # 保存清理后的数据
        if not self.dry_run:
            # 备份
            backup_path = self.data_dir / f"major_rank_data_before_cleaning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy2(main_data_path, backup_path)
            print(f"[INFO] 已备份原文件: {backup_path.name}")

            # 保存清理后的数据
            data["major_rank_data"] = cleaned_records
            data["metadata"] = data.get("metadata", {})
            data["metadata"]["last_cleaned"] = datetime.now().strftime("%Y-%m-%d")
            data["metadata"]["mock_data_removed"] = len(removed_records)

            with open(main_data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"[OK] 清理后的数据已保存")

    def _is_mock_record(self, record: Dict) -> bool:
        """判断是否为模拟记录"""
        # 检查 mock_data 标记
        if record.get("mock_data") is True:
            return True

        # 检查数据源
        data_source = record.get("data_source", "")
        if "mock" in str(data_source).lower():
            return True

        # 检查院校名称是否为占位符
        uni_name = record.get("university_name", "")
        if self._is_placeholder_name(uni_name):
            return True

        return False

    def _is_placeholder_name(self, name: str) -> bool:
        """判断是否为占位符名称"""
        for pattern in self.placeholder_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                return True
        return False

    def _analyze_removal_reasons(self, records: List[Dict]) -> Dict[str, int]:
        """分析删除原因"""
        reasons = defaultdict(int)

        for record in records:
            if record.get("mock_data") is True:
                reasons["标记为mock_data"] += 1
            elif "mock" in str(record.get("data_source", "")).lower():
                reasons["数据源包含mock"] += 1
            elif self._is_placeholder_name(record.get("university_name", "")):
                reasons["占位符院校名称"] += 1
            else:
                reasons["其他"] += 1

        return dict(reasons)

    def _delete_mock_files(self):
        """删除模拟数据文件"""
        print("\n[STEP 2/3] 删除模拟数据文件...")

        # 模拟数据文件模式
        mock_patterns = [
            "*mock*.json",
            "*_mock.json",
            "province_data_2025/*.json",  # 2025年数据都是模拟的
        ]

        deleted_files = []

        for pattern in mock_patterns:
            for file_path in self.data_dir.glob(pattern):
                if file_path.is_file():
                    # 检查是否确实是模拟文件
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            is_mock = (
                                isinstance(data, dict) and (
                                    data.get("mock_data") is True or
                                    data.get("generation_time", "").startswith("202")  # 模拟时间戳
                                )
                            )
                    except:
                        is_mock = False

                    if is_mock or "mock" in file_path.name.lower():
                        deleted_files.append(file_path)

        print(f"[INFO] 发现 {len(deleted_files)} 个模拟数据文件:")
        for f in deleted_files:
            print(f"  - {f.relative_to(self.data_dir)}")

        if not self.dry_run:
            # 创建备份目录
            backup_dir = self.data_dir / "deleted_mock_files" / datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir.mkdir(parents=True, exist_ok=True)

            # 移动文件而不是删除
            for f in deleted_files:
                shutil.move(str(f), str(backup_dir / f.name))

            print(f"[OK] 已移动到: {backup_dir.relative_to(self.data_dir)}")

        self.stats["deleted_files"] = len(deleted_files)

    def _generate_report(self):
        """生成清理报告"""
        print("\n[STEP 3/3] 生成清理报告...")

        report = {
            "clean_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dry_run": self.dry_run,
            "statistics": dict(self.stats),
        }

        report_path = self.data_dir / f"cleaning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        if not self.dry_run:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"[OK] 清理报告已保存: {report_path.name}")
        else:
            print("[DRY RUN] 报告内容（预览）:")
            print(json.dumps(report, ensure_ascii=False, indent=2))


# ==================== 主程序入口 ====================


def main():
    """主函数"""
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("[DRY RUN] 预演模式，不会实际修改文件")
        print()

    cleaner = MockDataCleaner(dry_run=dry_run)
    cleaner.clean_all()


if __name__ == "__main__":
    main()
