#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import json
from pathlib import Path
import logging
from datetime import datetime
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MajorGroupExpander:
    def __init__(self):
        self.mapping_data = {}
        self.missing_mappings = []
        self.expansion_stats = {
            'input_records': 0,
            'output_records': 0,
            'expanded_groups': 0,
            'unmapped_groups': 0,
            'total_majors_added': 0,
            'mapped_universities': set()
        }

    def load_mapping(self, mapping_file):
        logger.info(f"加载专业组映射: {mapping_file}")
        with open(mapping_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.mapping_data = data.get('mappings', {})
        logger.info(f"加载了 {len(self.mapping_data)} 个专业组映射")
        return True

    def expand_data(self, input_file, output_file):
        logger.info("开始展开专业组数据...")
        df = pd.read_csv(input_file)
        logger.info(f"读取到 {len(df)} 条记录")
        
        self.expansion_stats['input_records'] = len(df)
        expanded_records = []
        unmapped_groups = defaultdict(list)

        for idx, row in df.iterrows():
            key = f"{row['university']}_{row['group_code']}"
            
            if key in self.mapping_data:
                mapping_info = self.mapping_data[key]
                majors = mapping_info.get('majors', [])
                
                if majors:
                    for major in majors:
                        new_record = row.copy()
                        new_record['major_name'] = major
                        new_record['has_major_details'] = True
                        new_record['group_name'] = mapping_info.get('group_name', '')
                        expanded_records.append(new_record)
                    
                    self.expansion_stats['expanded_groups'] += 1
                    self.expansion_stats['total_majors_added'] += len(majors)
                    self.expansion_stats['mapped_universities'].add(row['university'])
                else:
                    record = row.copy()
                    record['major_name'] = ''
                    record['has_major_details'] = False
                    expanded_records.append(record)
            else:
                record = row.copy()
                record['major_name'] = ''
                record['has_major_details'] = False
                expanded_records.append(record)
                unmapped_groups[row['university']].append(row['group_code'])
                self.expansion_stats['unmapped_groups'] += 1

        logger.info(f"展开完成: {len(df)} → {len(expanded_records)} 条记录")
        self.expansion_stats['output_records'] = len(expanded_records)

        # 保存数据
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df_expanded = pd.DataFrame(expanded_records)
        df_expanded.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"✓ 数据已保存: {output_path}")
        
        excel_file = str(output_path).replace('.csv', '.xlsx')
        df_expanded.to_excel(excel_file, index=False, engine='openpyxl')
        logger.info(f"✓ Excel已保存: {excel_file}")

        # 保存缺失映射报告
        if unmapped_groups:
            for university, groups in unmapped_groups.items():
                for group in groups:
                    self.missing_mappings.append({
                        'university': university,
                        'group_code': group,
                        'reason': '无专业组映射'
                    })
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"backend/data/missing_mapping_report_{timestamp}.csv"
            df_missing = pd.DataFrame(self.missing_mappings)
            df_missing.to_csv(report_file, index=False, encoding='utf-8-sig')
            logger.info(f"✓ 缺失映射报告: {report_file}")

        return True

    def generate_statistics(self):
        logger.info("\n" + "=" * 80)
        logger.info("专业组展开统计报告")
        logger.info("=" * 80)
        logger.info(f"展开前记录数: {self.expansion_stats['input_records']}")
        logger.info(f"展开后记录数: {self.expansion_stats['output_records']}")
        logger.info(f"记录增长: {self.expansion_stats['output_records'] - self.expansion_stats['input_records']} 条")
        
        if self.expansion_stats['input_records'] > 0:
            growth_rate = (self.expansion_stats['output_records'] / self.expansion_stats['input_records'] - 1) * 100
            logger.info(f"增长率: {growth_rate:.1f}%")
        
        logger.info(f"\n已映射专业组: {self.expansion_stats['expanded_groups']}")
        logger.info(f"未映射专业组: {self.expansion_stats['unmapped_groups']}")
        logger.info(f"已映射院校数: {len(self.expansion_stats['mapped_universities'])}")
        logger.info(f"新增专业字段总数: {self.expansion_stats['total_majors_added']}")
        logger.info("=" * 80)

def main():
    logger.info("=" * 80)
    logger.info("2025年广东高考专业组展开系统")
    logger.info("=" * 80)
    
    expander = MajorGroupExpander()
    
    # 加载映射
    expander.load_mapping("backend/data/major_group_mapping.json")
    
    # 展开数据
    input_file = "./backend/scripts/output/guangdong_2025_final_20260510_153816.csv"
    output_file = "backend/data/guangdong_2025_major_level.csv"
    
    if not Path(input_file).exists():
        logger.error(f"输入文件不存在: {input_file}")
        return False
    
    expander.expand_data(input_file, output_file)
    expander.generate_statistics()
    
    logger.info("\n✓ 专业组展开完成！")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
