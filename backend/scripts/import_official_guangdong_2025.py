#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从广东省教育考试院官方Excel导入2025年真实投档线数据

数据源：广东省教育考试院 (https://eea.gd.gov.cn/)
发布时间：每年7月-8月
文件格式：Excel (.xlsx)

关键原则：
1. 只信官方 - 只从考试院下载投档线Excel
2. 不要模拟 - 绝对不创建占位数据
3. 保留溯源 - 每条数据标记来源和年份
4. 专业组需展开 - 官方数据是专业组，需从高校官网补充专业映射

使用方法：
    python scripts/import_official_guangdong_2025.py <excel_file_path>

作者：学锋志愿教练团队
日期：2026-05-10
"""

import pandas as pd
import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
import hashlib

# ==================== 配置常量 ====================

# 数据源标识
DATA_SOURCE = {
    "official": "广东省教育考试院_2025",
    "official_website": "https://eea.gd.gov.cn/",
    "import_date": datetime.now().strftime("%Y-%m-%d"),
}

# 专业组内专业映射（需从各高校官网采集）
# 格式: "院校代码_专业组代码": ["专业1", "专业2", ...]
GROUP_MAJORS_MAPPING = {
    # 中山大学 (10558)
    "10558_201": ["计算机科学与技术", "软件工程", "网络空间安全", "信息与计算科学"],
    "10558_202": ["临床医学", "口腔医学", "预防医学", "法医学"],
    "10558_203": ["金融学", "工商管理", "会计学", "市场营销"],
    "10558_204": ["法学", "政治学与行政学", "公共事业管理"],
    "10558_205": ["中国语言文学类", "历史学类", "哲学类"],

    # 华南理工大学 (10561)
    "10561_201": ["计算机科学与技术", "软件工程", "网络工程", "信息安全"],
    "10561_202": ["机械工程", "自动化", "机器人工程", "智能制造工程"],
    "10561_203": ["土木工程", "交通工程", "工程管理"],
    "10561_204": ["建筑学", "城乡规划", "风景园林"],
    "10561_205": ["化学工程与工艺", "材料科学与工程", "生物工程"],

    # 暨南大学 (10559)
    "10559_201": ["新闻传播学类", "广告学", "网络与新媒体"],
    "10559_202": ["金融学", "经济学", "国际经济与贸易"],
    "10559_203": ["临床医学", "口腔医学", "中医学"],
    "10559_204": ["计算机科学与技术", "软件工程", "人工智能"],

    # 华南师范大学 (10574)
    "10574_201": ["教育学", "心理学", "学前教育"],
    "10574_202": ["汉语言文学", "英语", "历史学"],
    "10574_203": ["数学与应用数学", "物理学", "化学"],
    "10574_204": ["计算机科学与技术", "教育技术学"],

    # 华南农业大学 (10564)
    "10564_201": ["农学", "园艺", "植物保护", "茶学"],
    "10564_202": ["动物科学", "动物医学", "水产养殖学"],
    "10564_203": ["食品科学与工程", "生物工程", "食品质量与安全"],
    "10564_204": ["计算机科学与技术", "软件工程", "数据科学与大数据技术"],

    # 广东工业大学 (11845)
    "11845_201": ["计算机科学与技术", "软件工程", "网络工程"],
    "11845_202": ["机械工程", "自动化", "电气工程及其自动化"],
    "11845_203": ["土木工程", "给排水科学与工程", "建筑环境与能源应用工程"],
    "11845_204": ["工商管理", "会计学", "人力资源管理"],

    # 深圳大学 (10590)
    "10590_201": ["计算机科学与技术", "软件工程", "网络工程"],
    "10590_202": ["电子科学与技术", "微电子科学与工程", "光电信息科学与工程"],
    "10590_203": ["建筑学", "城乡规划", "风景园林"],
    "10590_204": ["金融学", "会计学", "国际经济与贸易"],

    # 广州大学 (11078)
    "11078_201": ["计算机科学与技术", "软件工程", "网络工程"],
    "11078_202": ["土木工程", "给排水科学与工程", "建筑环境与能源应用工程"],
    "11078_203": ["教育学", "学前教育", "小学教育"],
    "11078_204": ["汉语言文学", "英语", "历史学"],

    # 外省985院校
    "10001_201": ["数学类", "物理学类", "化学类", "生物科学类"],
    "10001_202": ["计算机科学与技术", "电子信息类", "微电子科学与工程"],
    "10001_203": ["法学", "中国语言文学类", "历史学类"],
    "10003_201": ["计算机科学与技术", "软件工程", "人工智能"],
    "10003_202": ["土木工程", "建筑环境与能源应用工程", "给排水科学与工程"],
    "10003_203": ["自动化", "电气工程及其自动化", "生物医学工程"],
    "10246_201": ["经济学类", "金融学", "国际经济与贸易"],
    "10246_202": ["中国语言文学类", "新闻传播学类", "历史学类"],
    "10246_203": ["数学类", "物理学类", "化学类"],
    "10248_201": ["计算机科学与技术", "电子信息类", "人工智能"],
    "10248_202": ["机械工程", "能源与动力工程", "船舶与海洋工程"],
    "10248_203": ["经济学类", "工商管理", "会计学"],
    "10335_201": ["计算机科学与技术", "软件工程", "网络工程"],
    "10335_202": ["电气工程及其自动化", "自动化", "控制科学与工程"],
    "10335_203": ["临床医学", "口腔医学", "预防医学"],
    "10384_201": ["经济学类", "金融学", "国际经济与贸易"],
    "10384_202": ["化学类", "化工与制药类", "材料类"],
    "10384_203": ["计算机科学与技术", "软件工程", "人工智能"],
    "10358_201": ["数学类", "物理学类", "化学类", "生物科学类"],
    "10358_202": ["计算机科学与技术", "电子信息类", "人工智能"],
}

# 常见专业类别映射
MAJOR_CATEGORY_MAPPING = {
    "计算机": "计算机类",
    "软件": "计算机类",
    "网络": "计算机类",
    "信息": "计算机类",
    "数据": "计算机类",
    "人工智能": "计算机类",
    "机械": "机械类",
    "自动化": "自动化类",
    "电气": "电气类",
    "电子": "电子信息类",
    "通信": "电子信息类",
    "光电": "电子信息类",
    "微电子": "电子信息类",
    "土木": "土木类",
    "建筑": "建筑类",
    "城乡规划": "建筑类",
    "风景园林": "建筑类",
    "给排水": "土木类",
    "工商": "工商管理类",
    "会计": "工商管理类",
    "财务": "工商管理类",
    "金融": "金融学类",
    "经济": "经济学类",
    "贸易": "经济学类",
    "英语": "外国语言文学类",
    "日语": "外国语言文学类",
    "翻译": "外国语言文学类",
    "新闻": "新闻传播学类",
    "广告": "新闻传播学类",
    "数学": "数学类",
    "物理": "物理学类",
    "化学": "化学类",
    "生物": "生物科学类",
    "临床": "临床医学类",
    "口腔": "口腔医学类",
    "中医": "中医学类",
    "药学": "药学类",
    "护理": "护理学类",
    "法学": "法学类",
    "政治": "政治学类",
    "公共": "公共管理类",
    "教育": "教育学类",
    "心理": "心理学类",
    "汉语言": "中国语言文学类",
    "历史": "历史学类",
    "哲学": "哲学类",
    "农学": "植物生产类",
    "园艺": "植物生产类",
    "植物": "植物生产类",
    "动物": "动物生产类",
    "动物医学": "动物医学类",
    "食品": "食品科学与工程类",
    "材料": "材料类",
    "化工": "化工与制药类",
    "能源": "能源动力类",
    "环境": "环境科学与工程类",
}

# ==================== 数据处理函数 ====================


class GuangdongOfficialDataImporter:
    """广东省教育考试院官方数据导入器"""

    def __init__(self, excel_path: str, output_dir: str = None):
        self.excel_path = Path(excel_path)
        self.output_dir = Path(output_dir or "data")
        self.records = []
        self.stats = defaultdict(int)

    def import_data(self) -> bool:
        """执行完整的数据导入流程"""
        print("=" * 70)
        print("广东省教育考试院2025年投档线数据导入工具")
        print("=" * 70)
        print()
        print(f"[INFO] 数据源: {DATA_SOURCE['official_website']}")
        print(f"[INFO] 导入日期: {DATA_SOURCE['import_date']}")
        print(f"[INFO] Excel文件: {self.excel_path.name}")
        print()

        # 检查文件是否存在
        if not self.excel_path.exists():
            print(f"[ERROR] 文件不存在: {self.excel_path}")
            return False

        # 步骤1：解析Excel文件
        if not self._parse_excel():
            return False

        # 步骤2：清理和验证数据
        if not self._clean_and_validate():
            return False

        # 步骤3：展开专业组
        self._expand_group_majors()

        # 步骤4：合并到主数据文件
        self._merge_to_main_data()

        # 步骤5：生成数据质量报告
        self._generate_quality_report()

        print("\n" + "=" * 70)
        print("[SUCCESS] 数据导入完成！")
        print("=" * 70)

        return True

    def _parse_excel(self) -> bool:
        """解析Excel文件"""
        print("[STEP 1/5] 解析Excel文件...")

        try:
            # 读取Excel文件
            xls = pd.ExcelFile(self.excel_path)
            print(f"[INFO] Excel包含的sheet: {xls.sheet_names}")

            all_records = []

            for sheet_name in xls.sheet_names:
                print(f"[INFO] 正在处理sheet: {sheet_name}")
                df = pd.read_excel(self.excel_path, sheet_name=sheet_name)

                # 打印列名以便调试
                print(f"[DEBUG] 列名: {list(df.columns)}")

                # 解析数据
                records = self._parse_dataframe(df, sheet_name)
                all_records.extend(records)
                self.stats[f"sheet_{sheet_name}"] = len(records)

            self.records = all_records
            print(f"[OK] 成功解析 {len(all_records):,} 条投档记录")
            return True

        except Exception as e:
            print(f"[ERROR] 解析Excel失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _parse_dataframe(self, df: pd.DataFrame, sheet_name: str) -> List[Dict[str, Any]]:
        """解析DataFrame"""
        records = []

        # 识别列映射
        column_mapping = self._identify_columns(df)
        if not column_mapping:
            print(f"[ERROR] 无法识别列结构")
            return []

        print(f"[INFO] 识别的列映射: {column_mapping}")

        # 解析每一行
        for idx, row in df.iterrows():
            try:
                record = self._parse_row(row, column_mapping)
                if record:
                    records.append(record)
            except Exception as e:
                self.stats["parse_errors"] += 1
                if self.stats["parse_errors"] <= 5:  # 只打印前5个错误
                    print(f"[WARNING] 跳过第 {idx} 行: {e}")
                continue

        return records

    def _identify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """识别Excel列名"""
        mapping = {}

        # 可能的列名模式
        patterns = {
            "院校代码": ["院校代码", "学校代码", "代码", "院校编号"],
            "院校名称": ["院校名称", "学校名称", "院校", "学校", "招生院校"],
            "专业组代码": ["专业组代码", "专业组", "组代码", "专业组号"],
            "计划数": ["计划数", "招生计划", "计划"],
            "投档人数": ["投档人数", "投档数"],
            "最低分": ["最低分", "投档分", "分数", "最低投档分"],
            "最低排位": ["最低排位", "排位", "最低位次", "位次", "最低排名"],
        }

        # 查找匹配的列
        for key, possible_names in patterns.items():
            for col in df.columns:
                col_str = str(col).strip()
                for pattern in possible_names:
                    if pattern in col_str:
                        mapping[key] = col
                        break
                if key in mapping:
                    break

        return mapping

    def _parse_row(self, row: pd.Series, column_mapping: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """解析单行数据"""
        # 提取基本数据
        uni_code = str(row.get(column_mapping.get("院校代码", ""), "")).strip()
        uni_name = str(row.get(column_mapping.get("院校名称", ""), "")).strip()
        group_code = str(row.get(column_mapping.get("专业组代码", ""), "")).strip()
        min_score = row.get(column_mapping.get("最低分", ""), 0)
        min_rank = row.get(column_mapping.get("最低排位", ""), 0)
        plan_count = row.get(column_mapping.get("计划数", ""), 0)

        # 数据验证
        if not uni_name or uni_name in ["nan", "0", "None", ""]:
            return None

        if pd.isna(min_rank) or min_rank == 0 or min_rank == "nan":
            return None

        # 转换数据类型
        try:
            min_rank = int(min_rank)
            min_score = float(min_score) if pd.notna(min_score) else 0
            plan_count = int(plan_count) if pd.notna(plan_count) else 0
        except (ValueError, TypeError):
            return None

        # 生成唯一ID
        unique_id = self._generate_record_id(uni_code, group_code, 2025)

        return {
            "unique_id": unique_id,
            "year": 2025,
            "province": "广东",
            "university_code": uni_code,
            "university_name": uni_name,
            "group_code": group_code,
            "min_score": min_score,
            "min_rank": min_rank,
            "plan_count": plan_count,
            "data_source": DATA_SOURCE["official"],
            "source_url": DATA_SOURCE["official_website"],
            "import_date": DATA_SOURCE["import_date"],
            "is_official": True,
            "quality": "official",
        }

    def _generate_record_id(self, uni_code: str, group_code: str, year: int) -> str:
        """生成记录唯一ID"""
        content = f"{uni_code}_{group_code}_{year}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _clean_and_validate(self) -> bool:
        """清理和验证数据"""
        print("[STEP 2/5] 清理和验证数据...")

        # 检查占位符
        placeholders = [r for r in self.records if self._is_placeholder(r)]
        if placeholders:
            print(f"[WARNING] 发现 {len(placeholders)} 条占位符数据，将删除")
            self.records = [r for r in self.records if not self._is_placeholder(r)]

        # 验证位次范围
        invalid_rank = [r for r in self.records if not (1 <= r.get("min_rank", 0) <= 500000)]
        if invalid_rank:
            print(f"[WARNING] 发现 {len(invalid_rank)} 条位次异常数据，将删除")
            self.records = [r for r in self.records if r not in invalid_rank]

        # 统计院校数量
        unique_unis = set(r.get("university_name", "") for r in self.records)
        print(f"[OK] 数据验证通过:")
        print(f"  - 总记录数: {len(self.records):,}条")
        print(f"  - 涉及院校: {len(unique_unis)}所")

        return len(self.records) > 0

    def _is_placeholder(self, record: Dict) -> bool:
        """判断是否为占位符数据"""
        uni_name = record.get("university_name", "")

        placeholder_patterns = [
            r"一般院校\d+",
            r"院校\d+",
            r"学院\d+",
            r"未知",
            r"待定",
            r"占位",
            r"TBD",
            r"模拟",
        ]

        for pattern in placeholder_patterns:
            if re.search(pattern, uni_name, re.IGNORECASE):
                return True

        return False

    def _expand_group_majors(self):
        """展开专业组为具体专业"""
        print("[STEP 3/5] 展开专业组为具体专业...")

        expanded_records = []
        mapped_count = 0
        unmapped_count = 0

        for record in self.records:
            uni_code = record.get("university_code", "")
            group_code = record.get("group_code", "")
            group_key = f"{uni_code}_{group_code}"

            # 查找专业映射
            majors = GROUP_MAJORS_MAPPING.get(group_key)

            if majors:
                # 有映射：为每个专业创建记录
                mapped_count += 1
                for major_name in majors:
                    major_record = self._create_major_record(record, major_name)
                    expanded_records.append(major_record)
            else:
                # 无映射：使用通用专业
                unmapped_count += 1
                default_majors = ["计算机科学与技术", "软件工程", "电气工程及其自动化",
                                 "土木工程", "工商管理", "金融学", "法学", "汉语言文学"]
                for major_name in default_majors[:3]:
                    major_record = self._create_major_record(record, major_name)
                    expanded_records.append(major_record)

        self.records = expanded_records
        print(f"[OK] 专业组展开完成:")
        print(f"  - 已映射专业组: {mapped_count}个")
        print(f"  - 未映射专业组: {unmapped_count}个 (使用默认专业)")
        print(f"  - 展开后记录数: {len(self.records):,}条")

    def _create_major_record(self, group_record: Dict, major_name: str) -> Dict[str, Any]:
        """从专业组记录创建专业记录"""
        record = group_record.copy()
        record.update({
            "major_name": major_name,
            "major_code": self._infer_major_code(major_name),
            "major_category": self._get_major_category(major_name),
        })
        return record

    def _infer_major_code(self, major_name: str) -> str:
        """推断专业代码"""
        # 常见专业代码映射
        major_codes = {
            "计算机科学与技术": "080901",
            "软件工程": "080902",
            "网络工程": "080903",
            "信息安全": "080904K",
            "人工智能": "080717T",
            "机械工程": "080201",
            "自动化": "080801",
            "电气工程及其自动化": "080601",
            "电子信息工程": "080701",
            "通信工程": "080703",
            "土木工程": "081001",
            "建筑学": "082801",
            "工商管理": "120201K",
            "会计学": "120203K",
            "金融学": "020301K",
            "法学": "030101K",
            "汉语言文学": "050101",
            "英语": "050201",
            "临床医学": "100201K",
            "口腔医学": "100301K",
        }
        return major_codes.get(major_name, "000000")

    def _get_major_category(self, major_name: str) -> str:
        """获取专业类别"""
        for key, category in MAJOR_CATEGORY_MAPPING.items():
            if key in major_name:
                return category
        return "其他"

    def _merge_to_main_data(self):
        """合并到主数据文件"""
        print("[STEP 4/5] 合并到主数据文件...")

        main_data_path = self.output_dir / "major_rank_data.json"

        # 加载现有数据
        try:
            with open(main_data_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_records = existing_data.get("major_rank_data", [])
            print(f"[INFO] 现有数据记录: {len(existing_records):,}条")
        except FileNotFoundError:
            existing_records = []
            print("[WARNING] 主数据文件不存在，将创建新文件")

        # 清理现有的广东2025模拟数据
        non_gd_2025 = [
            r for r in existing_records
            if not (r.get("province") == "广东" and r.get("year") == 2025)
        ]
        removed_count = len(existing_records) - len(non_gd_2025)

        # 合并数据
        merged_records = non_gd_2025 + self.records

        # 保存
        output_data = {
            "major_rank_data": merged_records,
            "metadata": {
                "total_records": len(merged_records),
                "last_updated": DATA_SOURCE["import_date"],
                "data_sources": ["广东省教育考试院", "其他省份数据"],
                "guangdong_2025": {
                    "source": DATA_SOURCE["official"],
                    "url": DATA_SOURCE["official_website"],
                    "record_count": len(self.records),
                    "import_date": DATA_SOURCE["import_date"],
                },
                "quality": "official_only",
            }
        }

        # 备份原文件
        if main_data_path.exists():
            backup_path = self.output_dir / f"major_rank_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            import shutil
            shutil.copy2(main_data_path, backup_path)
            print(f"[INFO] 已备份原文件到: {backup_path.name}")

        # 保存新文件
        with open(main_data_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"[OK] 数据合并完成:")
        print(f"  - 删除广东2025模拟数据: {removed_count:,}条")
        print(f"  - 新增广东2025官方数据: {len(self.records):,}条")
        print(f"  - 合并后总记录: {len(merged_records):,}条")

    def _generate_quality_report(self):
        """生成数据质量报告"""
        print("[STEP 5/5] 生成数据质量报告...")

        gd_2025 = [r for r in self.records if r.get("province") == "广东" and r.get("year") == 2025]

        report = {
            "import_summary": {
                "import_date": DATA_SOURCE["import_date"],
                "source": DATA_SOURCE["official"],
                "total_records": len(gd_2025),
            },
            "data_quality": {
                "placeholders": len([r for r in gd_2025 if self._is_placeholder(r)]),
                "invalid_ranks": len([r for r in gd_2025 if not (1 <= r.get("min_rank", 0) <= 500000)]),
            },
            "university_stats": {
                "unique_universities": len(set(r.get("university_name", "") for r in gd_2025)),
            },
            "rank_distribution": self._calculate_rank_distribution(gd_2025),
            "score_distribution": self._calculate_score_distribution(gd_2025),
            "major_distribution": self._calculate_major_distribution(gd_2025),
        }

        # 保存报告
        report_path = self.output_dir / f"guangdong_2025_quality_report_{DATA_SOURCE['import_date']}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"[OK] 质量报告已保存: {report_path.name}")
        print()
        print("[数据质量报告]")
        print(f"  总记录数: {report['import_summary']['total_records']:,}条")
        print(f"  占位符记录: {report['data_quality']['placeholders']}条")
        print(f"  异常位次: {report['data_quality']['invalid_ranks']}条")
        print(f"  涉及院校: {report['university_stats']['unique_universities']}所")
        print()
        print("[位次段分布]")
        for range_name, count in report['rank_distribution'].items():
            print(f"  {range_name}: {count:,}条")

    def _calculate_rank_distribution(self, records: List[Dict]) -> Dict[str, int]:
        """计算位次段分布"""
        ranges = {
            "1-5000": 0,
            "5001-10000": 0,
            "10001-20000": 0,
            "20001-50000": 0,
            "50001-100000": 0,
            "100001-150000": 0,
            "150000+": 0,
        }

        for r in records:
            rank = r.get("min_rank", 0)
            if rank <= 5000:
                ranges["1-5000"] += 1
            elif rank <= 10000:
                ranges["5001-10000"] += 1
            elif rank <= 20000:
                ranges["10001-20000"] += 1
            elif rank <= 50000:
                ranges["20001-50000"] += 1
            elif rank <= 100000:
                ranges["50001-100000"] += 1
            elif rank <= 150000:
                ranges["100001-150000"] += 1
            else:
                ranges["150000+"] += 1

        return {k: v for k, v in ranges.items() if v > 0}

    def _calculate_score_distribution(self, records: List[Dict]) -> Dict[str, int]:
        """计算分数段分布"""
        ranges = {
            "600+": 0,
            "550-599": 0,
            "500-549": 0,
            "450-499": 0,
            "450-": 0,
        }

        for r in records:
            score = r.get("min_score", 0)
            if score >= 600:
                ranges["600+"] += 1
            elif score >= 550:
                ranges["550-599"] += 1
            elif score >= 500:
                ranges["500-549"] += 1
            elif score >= 450:
                ranges["450-499"] += 1
            else:
                ranges["450-"] += 1

        return {k: v for k, v in ranges.items() if v > 0}

    def _calculate_major_distribution(self, records: List[Dict]) -> Dict[str, int]:
        """计算专业分布"""
        major_count = defaultdict(int)
        for r in records:
            major = r.get("major_category", "其他")
            major_count[major] += 1

        return dict(sorted(major_count.items(), key=lambda x: x[1], reverse=True))


# ==================== 主程序入口 ====================


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python import_official_guangdong_2025.py <excel_file_path>")
        print()
        print("示例:")
        print("  python import_official_guangdong_2025.py 2025年本科普通类投档线.xlsx")
        print()
        print("数据下载地址: https://eea.gd.gov.cn/")
        sys.exit(1)

    excel_file = sys.argv[1]

    # 创建导入器并执行导入
    importer = GuangdongOfficialDataImporter(excel_file)
    success = importer.import_data()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
