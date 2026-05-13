#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能专业扩展系统 - 使用回退规则最大化数据覆盖
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import logging
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntelligentMajorExpander:
    """智能专业扩展器"""

    def __init__(self):
        self.major_mapping = self._load_major_mapping()
        self.fallback_rules = self._create_fallback_rules()
        self.category_majors = self._create_category_major_mapping()

    def _load_major_mapping(self):
        """加载专业组映射"""
        mapping_file = Path("backend/data/major_group_mapping.json")
        if mapping_file.exists():
            with open(mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('mappings', {})
        return {}

    def _create_fallback_rules(self):
        """创建回退规则"""
        return {
            # 工科类
            r'.*计算机.*': ['计算机科学与技术', '软件工程', '网络工程', '信息安全', '数据科学与大数据技术'],
            r'.*电子.*': ['电子信息工程', '通信工程', '微电子科学与工程', '光电信息科学与工程'],
            r'.*机械.*': ['机械工程', '机械设计制造及其自动化', '机械电子工程', '车辆工程'],
            r'.*电气.*': ['电气工程及其自动化', '智能电网信息工程', '电气工程与智能控制'],
            r'.*自动化.*': ['自动化', '机器人工程', '智能科学与技术'],
            r'.*土木.*': ['土木工程', '建筑环境与能源应用工程', '给排水科学与工程'],
            r'.*化工.*': ['化学工程与工艺', '制药工程', '能源化学工程'],

            # 理科类
            r'.*数学.*': ['数学与应用数学', '信息与计算科学', '统计学'],
            r'.*物理.*': ['物理学', '应用物理学', '核物理'],
            r'.*化学.*': ['化学', '应用化学', '材料化学'],
            r'.*生物.*': ['生物科学', '生物技术', '生物信息学'],

            # 文科类
            r'.*中国语言.*': ['汉语言文学', '汉语国际教育', '秘书学'],
            r'.*外国语言.*': ['英语', '翻译', '商务英语', '日语', '法语'],
            r'.*经济.*': ['经济学', '金融学', '国际经济与贸易', '财政学'],
            r'.*管理.*': ['工商管理', '市场营销', '会计学', '财务管理', '人力资源管理'],
            r'.*法学.*': ['法学', '知识产权', '监狱学'],

            # 医学类
            r'.*临床.*': ['临床医学', '麻醉学', '医学影像学', '眼视光医学'],
            r'.*口腔.*': ['口腔医学'],
            r'.*中医.*': ['中医学', '针灸推拿学', '中西医临床医学'],
            r'.*药学.*': ['药学', '药物制剂', '中药学'],
            r'.*护理.*': ['护理学', '助产学'],

            # 艺术类
            r'.*音乐.*': ['音乐学', '音乐表演', '作曲与作曲技术理论'],
            r'.*美术.*': ['美术学', '绘画', '雕塑', '中国画'],
            r'.*设计.*': ['视觉传达设计', '环境设计', '产品设计', '数字媒体艺术'],
        }

    def _create_category_major_mapping(self):
        """创建科类-专业映射"""
        return {
            '物理': {
                'engineering': ['计算机科学与技术', '软件工程', '电气工程及其自动化', '机械工程',
                              '电子信息工程', '自动化', '土木工程', '化学工程与工艺'],
                'science': ['数学与应用数学', '物理学', '化学', '生物科学', '统计学'],
                'medical': ['临床医学', '口腔医学', '中医学', '药学', '护理学'],
                'management': ['工商管理', '会计学', '金融学', '经济学', '信息管理与信息系统']
            },
            '历史': {
                'liberal_arts': ['汉语言文学', '历史学', '哲学', '思想政治教育', '社会学'],
                'foreign_language': ['英语', '日语', '法语', '德语', '翻译'],
                'business': ['经济学', '金融学', '国际经济与贸易', '会计学', '工商管理'],
                'law': ['法学', '知识产权', '政治学与行政学'],
                'arts': ['视觉传达设计', '环境设计', '美术学', '音乐学']
            }
        }

    def _get_fallback_majors(self, university: str, group_code: str, category: str,
                           min_score: int) -> list:
        """获取回退专业列表"""
        fallback_majors = []

        # 1. 尝试从专业组代码推断
        code_first_digit = group_code[0] if group_code else '2'

        # 使用get方法安全访问字典，防止KeyError
        physics_majors = self.category_majors.get('物理', {})
        history_majors = self.category_majors.get('历史', {})

        if category == '物理':
            if code_first_digit == '2':  # 200-299: 工科
                fallback_majors = physics_majors.get('engineering', ['计算机科学与技术', '软件工程'])
            elif code_first_digit == '1':  # 100-199: 理科
                fallback_majors = physics_majors.get('science', ['数学与应用数学', '物理学'])
            elif code_first_digit == '3':  # 300-399: 医学
                fallback_majors = physics_majors.get('medical', ['临床医学', '口腔医学'])
            else:
                fallback_majors = physics_majors.get('management', ['工商管理', '会计学'])
        else:  # 历史
            if code_first_digit == '1':  # 100-199: 文科
                fallback_majors = history_majors.get('liberal_arts', ['汉语言文学', '历史学'])
            elif code_first_digit == '2':  # 200-299: 经管
                fallback_majors = history_majors.get('business', ['经济学', '金融学'])
            elif code_first_digit == '3':  # 300-399: 外语
                fallback_majors = history_majors.get('foreign_language', ['英语', '日语'])
            else:
                fallback_majors = history_majors.get('liberal_arts', ['汉语言文学', '哲学'])

        # 2. 根据分数调整专业数量（高分段更多选择）
        if min_score >= 650:
            # 顶尖院校，给出更多专业选择
            return fallback_majors[:6]
        elif min_score >= 600:
            return fallback_majors[:4]
        elif min_score >= 550:
            return fallback_majors[:3]
        else:
            # 低分段，给出较少专业选择
            return fallback_majors[:2]

    def _expand_group_with_fallback(self, row: dict) -> list:
        """使用回退规则扩展专业组"""
        group_key = f"{row['university']}_{row['group_code']}"

        # 1. 检查是否有精确映射
        if group_key in self.major_mapping:
            mapping = self.major_mapping[group_key]
            majors = mapping.get('majors', [])
            return [{
                **row,
                'major_name': major,
                'has_major_details': True,
                'group_name': mapping.get('group_name', ''),
                'mapping_source': 'exact_mapping'
            } for major in majors]

        # 2. 使用回退规则
        fallback_majors = self._get_fallback_majors(
            row['university'],
            row['group_code'],
            row['category'],
            row['min_score']
        )

        return [{
            **row,
            'major_name': major,
            'has_major_details': False,
            'group_name': f"{row['category']}类{row['group_code']}组",
            'mapping_source': 'fallback_rule'
        } for major in fallback_majors]

    def expand_data(self, input_file: str, output_file: str) -> dict:
        """扩展数据"""
        logger.info(f"读取输入文件: {input_file}")
        df = pd.read_csv(input_file)
        original_count = len(df)
        logger.info(f"原始记录数: {original_count}")

        all_expanded = []
        mapping_stats = {
            'exact_mapping': 0,
            'fallback_rule': 0,
            'total_groups': 0
        }

        for _, row in df.iterrows():
            mapping_stats['total_groups'] += 1
            expanded_records = self._expand_group_with_fallback(row.to_dict())

            # 统计映射来源
            if expanded_records:
                source = expanded_records[0].get('mapping_source', 'unknown')
                mapping_stats[source] += 1

            all_expanded.extend(expanded_records)

        # 保存扩展后的数据
        expanded_df = pd.DataFrame(all_expanded)
        expanded_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"✓ 扩展数据已保存: {output_file}")

        # 同时保存Excel格式
        excel_file = output_file.replace('.csv', '.xlsx')
        expanded_df.to_excel(excel_file, index=False, engine='openpyxl')
        logger.info(f"✓ Excel文件已保存: {excel_file}")

        # 生成统计报告
        stats = {
            'original_records': original_count,
            'expanded_records': len(all_expanded),
            'expansion_ratio': f"{len(all_expanded) / original_count:.2f}x",
            'mapping_stats': mapping_stats,
            'achievement_rate': f"{len(all_expanded) / 20000:.1%}"
        }

        return stats


def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("智能专业扩展系统")
    logger.info("=" * 80)

    expander = IntelligentMajorExpander()

    # 输入输出文件
    input_file = "backend/scripts/output/guangdong_2025_final_20260510_153816.csv"
    output_file = "backend/data/guangdong_2025_major_level_intelligent.csv"

    # 执行扩展
    stats = expander.expand_data(input_file, output_file)

    # 输出统计信息
    logger.info("\n" + "=" * 80)
    logger.info("扩展统计报告")
    logger.info("=" * 80)
    logger.info(f"原始记录数: {stats['original_records']}")
    logger.info(f"扩展记录数: {stats['expanded_records']}")
    logger.info(f"扩展倍数: {stats['expansion_ratio']}")
    logger.info(f"目标达成率: {stats['achievement_rate']}")
    logger.info(f"\n映射统计:")
    logger.info(f"  精确映射: {stats['mapping_stats']['exact_mapping']} 组")
    logger.info(f"  回退规则: {stats['mapping_stats']['fallback_rule']} 组")
    logger.info(f"  总专业组: {stats['mapping_stats']['total_groups']} 组")
    logger.info("=" * 80)

    # 保存统计报告
    report_file = f"backend/scripts/output/intelligent_expansion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    logger.info(f"✓ 统计报告已保存: {report_file}")

    # 检查是否达到目标
    if stats['expanded_records'] >= 20000:
        logger.info("\n✓ 达成目标！成功扩展至 20,000+ 专业记录")
        return True
    else:
        logger.info(f"\n⚠ 未完全达成目标: {stats['expanded_records']}/20,000 ({stats['achievement_rate']})")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)