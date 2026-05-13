#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2025年广东高考数据质量检查工具

用于检查现有数据中的问题：
- 模拟数据
- 不完整数据
- 不真实数据
- 格式错误
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime


class DataQualityChecker:
    """数据质量检查器"""

    def __init__(self, data_file: str = "../data/major_rank_data.json"):
        self.data_file = Path(data_file)
        self.data = None
        self.issues = {
            'mock_data': [],
            'incomplete_data': [],
            'unrealistic_data': [],
            'format_errors': [],
            'missing_2025_data': []
        }

    def load_data(self):
        """加载数据"""
        print(f"加载数据文件: {self.data_file}")

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"数据加载成功")
            return True
        except Exception as e:
            print(f"数据加载失败: {e}")
            return False

    def check_guangdong_2025_data(self):
        """检查2025年广东数据"""
        if not self.data:
            print("请先加载数据")
            return

        print("\n开始检查2025年广东数据...")

        records = self.data.get('major_rank_data', [])

        # 筛选2025年广东数据
        guangdong_2025 = []
        for record in records:
            if record.get('year') == 2025 and record.get('province') == '广东':
                guangdong_2025.append(record)

        print(f"找到 {len(guangdong_2025)} 条2025年广东记录")

        if not guangdong_2025:
            print("[FAIL] 严重问题: 没有2025年广东数据")
            self.issues['missing_2025_data'].append("整个2025年广东数据缺失")
            return

        # 检查各类问题
        self._check_mock_data(guangdong_2025)
        self._check_incomplete_data(guangdong_2025)
        self._check_unrealistic_data(guangdong_2025)
        self._check_format_errors(guangdong_2025)

        # 生成报告
        self._generate_report(guangdong_2025)

    def _check_mock_data(self, records: List[Dict]):
        """检查模拟数据"""
        print("\n检查模拟数据...")

        mock_patterns = [
            r'一般院校',
            r'测试',
            r'test',
            r'mock',
            r'示例',
            r'占位',
            r'placeholder'
        ]

        for record in records:
            university = record.get('university_name', '')
            major = record.get('major_name', '')

            # 检查院校名称
            for pattern in mock_patterns:
                if re.search(pattern, university, re.IGNORECASE):
                    self.issues['mock_data'].append({
                        'university': university,
                        'major': major,
                        'reason': f'院校名称包含模拟关键词: {pattern}'
                    })
                    break

            # 检查数据源标记
            data_source = record.get('data_source', '')
            if 'mock' in data_source.lower() or 'test' in data_source.lower():
                self.issues['mock_data'].append({
                    'university': university,
                    'major': major,
                    'reason': f'数据源标记为模拟数据: {data_source}'
                })

        print(f"发现 {len(self.issues['mock_data'])} 条模拟数据")

    def _check_incomplete_data(self, records: List[Dict]):
        """检查数据完整性"""
        print("\n检查数据完整性...")

        required_fields = [
            'university_name',
            'major_name',
            'min_score',
            'min_rank',
            'year',
            'province'
        ]

        for record in records:
            missing_fields = []

            for field in required_fields:
                if field not in record or record[field] is None:
                    missing_fields.append(field)

            if missing_fields:
                self.issues['incomplete_data'].append({
                    'university': record.get('university_name', 'Unknown'),
                    'major': record.get('major_name', 'Unknown'),
                    'missing_fields': missing_fields
                })

            # 检查关键字段是否为空
            if not record.get('university_name'):
                self.issues['incomplete_data'].append({
                    'university': record.get('major_name', 'Unknown'),
                    'major': record.get('major_name', 'Unknown'),
                    'missing_fields': ['university_name为空']
                })

        print(f"发现 {len(self.issues['incomplete_data'])} 条不完整数据")

    def _check_unrealistic_data(self, records: List[Dict]):
        """检查数据真实性"""
        print("\n检查数据真实性...")

        for record in records:
            score = record.get('min_score')
            rank = record.get('min_rank')

            # 检查分数范围（广东750分制）
            if score is not None:
                if not (300 <= score <= 750):
                    self.issues['unrealistic_data'].append({
                        'university': record.get('university_name', 'Unknown'),
                        'major': record.get('major_name', 'Unknown'),
                        'reason': f'分数超出合理范围: {score} (应在300-750之间)'
                    })

            # 检查排位
            if rank is not None:
                if not (1 <= rank <= 500000):
                    self.issues['unrealistic_data'].append({
                        'university': record.get('university_name', 'Unknown'),
                        'major': record.get('major_name', 'Unknown'),
                        'reason': f'排位超出合理范围: {rank} (应在1-500000之间)'
                    })

            # 检查数据源
            data_source = record.get('data_source', '')
            if not data_source or data_source == 'unknown':
                self.issues['unrealistic_data'].append({
                    'university': record.get('university_name', 'Unknown'),
                    'major': record.get('major_name', 'Unknown'),
                    'reason': '缺少数据来源信息'
                })

        print(f"发现 {len(self.issues['unrealistic_data'])} 条不真实数据")

    def _check_format_errors(self, records: List[Dict]):
        """检查格式错误"""
        print("\n检查数据格式...")

        for record in records:
            # 检查数据类型
            if not isinstance(record.get('min_score'), (int, float)):
                self.issues['format_errors'].append({
                    'university': record.get('university_name', 'Unknown'),
                    'major': record.get('major_name', 'Unknown'),
                    'reason': f'min_score类型错误: {type(record.get("min_score"))}'
                })

            if not isinstance(record.get('min_rank'), (int, float)):
                self.issues['format_errors'].append({
                    'university': record.get('university_name', 'Unknown'),
                    'major': record.get('major_name', 'Unknown'),
                    'reason': f'min_rank类型错误: {type(record.get("min_rank"))}'
                })

            # 检查年份
            year = record.get('year')
            if year != 2025:
                self.issues['format_errors'].append({
                    'university': record.get('university_name', 'Unknown'),
                    'major': record.get('major_name', 'Unknown'),
                    'reason': f'年份错误: {year} (应为2025)'
                })

        print(f"发现 {len(self.issues['format_errors'])} 条格式错误")

    def _generate_report(self, records: List[Dict]):
        """生成质量报告"""
        print("\n" + "=" * 80)
        print("2025年广东数据质量检查报告")
        print("=" * 80)

        total_issues = sum(len(issues) for issues in self.issues.values())

        print(f"\n总记录数: {len(records)}")
        print(f"问题记录数: {total_issues}")
        print(f"健康记录数: {len(records) - total_issues}")
        print(f"数据健康率: {(len(records) - total_issues) / len(records) * 100:.2f}%")

        print("\n问题分类:")

        if self.issues['mock_data']:
            print(f"\n[MOCK] 模拟数据 ({len(self.issues['mock_data'])}条):")
            for item in self.issues['mock_data'][:5]:  # 只显示前5条
                print(f"  - {item['university']} / {item.get('major', 'N/A')}: {item['reason']}")
            if len(self.issues['mock_data']) > 5:
                print(f"  ... 还有 {len(self.issues['mock_data']) - 5} 条")

        if self.issues['incomplete_data']:
            print(f"\n[INCOMPLETE] 不完整数据 ({len(self.issues['incomplete_data'])}条):")
            for item in self.issues['incomplete_data'][:5]:
                print(f"  - {item['university']}: 缺少 {', '.join(item['missing_fields'])}")
            if len(self.issues['incomplete_data']) > 5:
                print(f"  ... 还有 {len(self.issues['incomplete_data']) - 5} 条")

        if self.issues['unrealistic_data']:
            print(f"\n[UNREALISTIC] 不真实数据 ({len(self.issues['unrealistic_data'])}条):")
            for item in self.issues['unrealistic_data'][:5]:
                print(f"  - {item['university']}: {item['reason']}")
            if len(self.issues['unrealistic_data']) > 5:
                print(f"  ... 还有 {len(self.issues['unrealistic_data']) - 5} 条")

        if self.issues['format_errors']:
            print(f"\n[FORMAT] 格式错误 ({len(self.issues['format_errors'])}条):")
            for item in self.issues['format_errors'][:5]:
                print(f"  - {item['university']}: {item['reason']}")
            if len(self.issues['format_errors']) > 5:
                print(f"  ... 还有 {len(self.issues['format_errors']) - 5} 条")

        # 结论
        print("\n" + "=" * 80)
        print("结论:")

        if self.issues['mock_data']:
            print("[FAIL] 发现模拟数据，需要立即清理并重新采集真实数据")
        elif total_issues > len(records) * 0.1:  # 超过10%的问题
            print("[WARNING] 数据质量问题较多，建议重新采集")
        elif total_issues > 0:
            print("[WARNING] 存在一些数据质量问题，需要修复")
        else:
            print("[PASS] 数据质量良好")

        print("=" * 80)

        # 保存详细报告
        self._save_detailed_report(records)

    def _save_detailed_report(self, records: List[Dict]):
        """保存详细报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"data_quality_report_{timestamp}.json"

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_records': len(records),
            'issues': {
                'mock_data': {
                    'count': len(self.issues['mock_data']),
                    'items': self.issues['mock_data']
                },
                'incomplete_data': {
                    'count': len(self.issues['incomplete_data']),
                    'items': self.issues['incomplete_data']
                },
                'unrealistic_data': {
                    'count': len(self.issues['unrealistic_data']),
                    'items': self.issues['unrealistic_data']
                },
                'format_errors': {
                    'count': len(self.issues['format_errors']),
                    'items': self.issues['format_errors']
                },
                'missing_2025_data': {
                    'count': len(self.issues['missing_2025_data']),
                    'items': self.issues['missing_2025_data']
                }
            }
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n详细报告已保存: {report_file}")

    def export_problem_records(self, records: List[Dict]):
        """导出有问题的记录"""
        # 收集所有有问题的记录的university_major_id
        problem_ids = set()

        for issue_type in ['mock_data', 'incomplete_data', 'unrealistic_data', 'format_errors']:
            for item in self.issues[issue_type]:
                # 这里需要根据实际情况找到对应的记录ID
                pass

        # 导出问题记录
        if problem_ids:
            problem_records = [r for r in records if r.get('university_major_id') in problem_ids]

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"problem_records_{timestamp}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(problem_records, f, indent=2, ensure_ascii=False)

            print(f"问题记录已导出: {output_file}")


def main():
    """主函数"""
    print("2025年广东数据质量检查工具")
    print("=" * 80)

    # 创建检查器
    checker = DataQualityChecker()

    # 加载数据
    if not checker.load_data():
        return

    # 检查数据
    checker.check_guangdong_2025_data()

    print("\n检查完成！")


if __name__ == "__main__":
    main()
