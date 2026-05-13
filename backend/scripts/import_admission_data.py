"""
广东省高考录取数据导入脚本
支持手动录入、CSV导入、数据验证
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class AdmissionDataImporter:
    """录取数据导入器"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.scripts_dir = self.base_dir / "scripts"
        self.output_file = self.data_dir / "guangdong_admission_2024.json"

        # 确保目录存在
        self.data_dir.mkdir(exist_ok=True)
        self.scripts_dir.mkdir(exist_ok=True)

    def import_from_manual_input(self):
        """手动录入数据"""
        print("\n" + "="*60)
        print("手动录入广东录取数据")
        print("="*60)

        admission_data = []

        while True:
            print("\n录入院校专业信息（留空跳过）：")
            university_name = input("院校名称: ").strip()
            if not university_name:
                break

            university_type = self._select_university_type()
            city = input("城市（如：广州、深圳）: ").strip()
            major_name = input("专业名称: ").strip()
            major_code = input("专业代码（如：080901）: ").strip()

            min_rank = self._input_rank("最低录取位次")
            min_score = self._input_score("最低录取分数")

            enrollment = self._input_int("招生计划数", default=60)

            record = {
                "university_id": self._generate_id(),
                "university_name": university_name,
                "university_type": university_type,
                "city": city,
                "major_id": self._generate_id(prefix="major"),
                "major_name": major_name,
                "major_code": major_code,
                "min_rank": min_rank,
                "min_score": min_score,
                "enrollment_count": enrollment,
                "data_source": "manual_input",
                "imported_at": datetime.now().isoformat()
            }

            admission_data.append(record)
            print(f"\n[ADDED] {university_name} - {major_name} (rank:{min_rank})")

            if input("\n继续录入？(y/n): ").lower() != 'y':
                break

        self._save_data(admission_data)
        self._show_summary(admission_data)

    def import_from_csv(self, csv_file_path: str):
        """从CSV文件导入"""
        print(f"\n从CSV导入: {csv_file_path}")

        csv_path = Path(csv_file_path)
        if not csv_path.exists():
            print(f"[ERROR] File not found: {csv_file_path}")
            return

        admission_data = []

        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    # 验证必要字段
                    if not row.get('university_name'):
                        continue

                    record = {
                        "university_id": self._generate_id(),
                        "university_name": row['university_name'].strip(),
                        "university_type": self._normalize_type(row.get('university_type', '')),
                        "city": row.get('city', '').strip() or '未知',
                        "major_id": self._generate_id(prefix="major"),
                        "major_name": row.get('major_name', '').strip(),
                        "major_code": row.get('major_code', '').strip(),
                        "min_rank": self._parse_rank(row.get('min_rank')),
                        "min_score": self._parse_score(row.get('min_score')),
                        "enrollment_count": int(row.get('enrollment_count', 60)) if row.get('enrollment_count') else 60,
                        "data_source": "csv_import",
                        "imported_at": datetime.now().isoformat()
                    }

                    # 验证数据合理性
                    if self._validate_record(record):
                        admission_data.append(record)

            self._save_data(admission_data)
            self._show_summary(admission_data)

        except Exception as e:
            print(f"[ERROR] Import failed: {e}")

    def import_from_template(self):
        """使用模板数据快速导入"""
        print("\n生成模板数据（用于测试）...")

        admission_data = self._generate_template_data()

        self._save_data(admission_data)
        self._show_summary(admission_data)

    def _generate_template_data(self) -> List[Dict[str, Any]]:
        """生成模板数据"""
        return [
            # 985院校
            {
                "university_id": "10001",
                "university_name": "中山大学",
                "university_type": "985",
                "city": "广州",
                "major_id": "20001",
                "major_name": "计算机科学与技术",
                "major_code": "080901",
                "min_rank": 1500,
                "min_score": 650,
                "enrollment_count": 120,
                "year": 2024,
                "batch": "本科批"
            },
            {
                "university_id": "10002",
                "university_name": "华南理工大学",
                "university_type": "985",
                "city": "广州",
                "major_id": "20002",
                "major_name": "计算机科学与技术",
                "major_code": "080901",
                "min_rank": 3500,
                "min_score": 635,
                "enrollment_count": 150,
                "year": 2024,
                "batch": "本科批"
            },
            # 211院校
            {
                "university_id": "10003",
                "university_name": "暨南大学",
                "university_type": "211",
                "city": "广州",
                "major_id": "20003",
                "major_name": "金融学",
                "major_code": "020301",
                "min_rank": 12000,
                "min_score": 580,
                "enrollment_count": 80,
                "year": 2024,
                "batch": "本科批"
            },
            {
                "university_id": "10004",
                "university_name": "华南师范大学",
                "university_type": "211",
                "city": "广州",
                "major_id": "20004",
                "major_name": "汉语言文学",
                "major_code": "050101",
                "min_rank": 15000,
                "min_score": 565,
                "enrollment_count": 100,
                "year": 2024,
                "batch": "本科批"
            },
            # 省属重点
            {
                "university_id": "10005",
                "university_name": "深圳大学",
                "university_type": "省属重点",
                "city": "深圳",
                "major_id": "20005",
                "major_name": "计算机科学与技术",
                "major_code": "080901",
                "min_rank": 22000,
                "min_score": 550,
                "enrollment_count": 200,
                "year": 2024,
                "batch": "本科批"
            },
            {
                "university_id": "10006",
                "university_name": "广州大学",
                "university_type": "省属重点",
                "city": "广州",
                "major_id": "20006",
                "major_name": "机械工程",
                "major_code": "080202",
                "min_rank": 35000,
                "min_score": 530,
                "enrollment_count": 150,
                "year": 2024,
                "batch": "本科批"
            },
            # 独立学院
            {
                "university_id": "10007",
                "university_name": "北京师范大学珠海分校",
                "university_type": "独立学院",
                "city": "珠海",
                "major_id": "20007",
                "major_name": "计算机科学与技术",
                "major_code": "080901",
                "min_rank": 55000,
                "min_score": 510,
                "enrollment_count": 80,
                "year": 2024,
                "batch": "本科批"
            },
            # 民办本科
            {
                "university_id": "10008",
                "university_name": "广州南方学院",
                "university_type": "民办本科",
                "city": "广州",
                "major_id": "20008",
                "major_name": "会计学",
                "major_code": "120203",
                "min_rank": 100000,
                "min_score": 480,
                "enrollment_count": 100,
                "year": 2024,
                "batch": "本科批"
            },
            # 高职专科
            {
                "university_id": "10009",
                "university_name": "深圳职业技术学院",
                "university_type": "公办高职",
                "city": "深圳",
                "major_id": "20009",
                "major_name": "计算机应用技术",
                "major_code": "510201",
                "min_rank": 150000,
                "min_score": 420,
                "enrollment_count": 200,
                "year": 2024,
                "batch": "专科批"
            },
            {
                "university_id": "10010",
                "university_name": "顺德职业技术学院",
                "university_type": "公办高职",
                "city": "佛山",
                "major_id": "20010",
                "major_name": "机电一体化技术",
                "major_code": "560301",
                "min_rank": 200000,
                "min_score": 380,
                "enrollment_count": 150,
                "year": 2024,
                "batch": "专科批"
            },
        ]

    def _select_university_type(self) -> str:
        """选择院校类型"""
        types = [
            ("1", "985"),
            ("2", "211"),
            ("3", "双一流"),
            ("4", "省属重点"),
            ("5", "普通公办"),
            ("6", "独立学院"),
            ("7", "民办本科"),
            ("8", "公办高职"),
            ("9", "民办高职"),
        ]

        print("\n院校类型:")
        for code, name in types:
            print(f"  {code}. {name}")

        while True:
            choice = input("\n请选择类型 (1-9): ").strip()
            if choice in [str(i) for i in range(1, 10)]:
                return types[int(choice)-1][1]

    def _input_rank(self, prompt: str) -> int:
        """输入位次"""
        while True:
            value = input(f"{prompt}: ").strip()
            rank = self._parse_rank(value)
            if rank is not None:
                return rank
            print("[ERROR] Please enter a valid rank (1-500000)")

    def _input_score(self, prompt: str) -> int:
        """输入分数"""
        while True:
            value = input(f"{prompt}: ").strip()
            score = self._parse_score(value)
            if score is not None:
                return score
            print("[ERROR] Please enter a valid score (0-750)")

    def _input_int(self, prompt: str, default: int = 0) -> int:
        """输入整数"""
        value = input(f"{prompt} (默认{default}): ").strip()
        if not value:
            return default
        try:
            return int(value)
        except:
            return default

    def _parse_rank(self, value: str) -> Optional[int]:
        """解析位次"""
        try:
            rank = int(value)
            if 1 <= rank <= 500000:
                return rank
        except:
            pass
        return None

    def _parse_score(self, value: str) -> Optional[int]:
        """解析分数"""
        try:
            score = int(value)
            if 0 <= score <= 750:
                return score
        except:
            pass
        return None

    def _normalize_type(self, type_str: str) -> str:
        """规范化院校类型"""
        mapping = {
            "985": "985",
            "211": "211",
            "双一流": "双一流",
            "省属重点": "省属重点",
            "普通公办": "普通公办",
            "独立学院": "独立学院",
            "民办本科": "民办本科",
            "公办高职": "公办高职",
            "民办高职": "民办高职",
            "高职": "公办高职",
        }
        return mapping.get(type_str.strip(), "普通公办")

    def _validate_record(self, record: Dict[str, Any]) -> bool:
        """验证单条记录"""
        # 验证位次范围
        min_rank = record.get('min_rank', 0)
        if not (1 <= min_rank <= 500000):
            print(f"[WARNING] Skipping invalid record: {record['university_name']} rank{min_rank}")
            return False

        # 验证分数范围
        min_score = record.get('min_score', 0)
        if not (0 <= min_score <= 750):
            print(f"[WARNING] Skipping invalid record: {record['university_name']} score{min_score}")
            return False

        return True

    def _generate_id(self, prefix: str = "uni") -> str:
        """生成ID"""
        import time
        return f"{prefix}_{int(time.time() * 1000)}"

    def _save_data(self, data: List[Dict[str, Any]]):
        """保存数据到JSON文件"""
        output_data = {
            "metadata": {
                "version": "1.0.0",
                "year": 2024,
                "province": "广东",
                "generated_at": datetime.now().isoformat(),
                "total_records": len(data)
            },
            "data": data
        }

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"\n[SUCCESS] Data saved to: {self.output_file}")

    def _show_summary(self, data: List[Dict[str, Any]]):
        """显示数据摘要"""
        print("\n" + "="*60)
        print("数据导入完成")
        print("="*60)

        # 按类型统计
        type_count = {}
        for record in data:
            utype = record['university_type']
            type_count[utype] = type_count.get(utype, 0) + 1

        print(f"\n导入统计:")
        print(f"  总记录数: {len(data)} 条")

        print(f"\n院校类型分布:")
        for utype, count in sorted(type_count.items()):
            print(f"  {utype}: {count} 条")

        # 位次范围
        ranks = [r['min_rank'] for r in data]
        if ranks:
            print(f"\n位次范围:")
            print(f"  最低位次: {min(ranks):,}")
            print(f"  最高位次: {max(ranks):,}")


def main():
    """主函数"""
    print("="*60)
    print("广东高考录取数据导入工具")
    print("="*60)

    importer = AdmissionDataImporter()

    print("\n请选择导入方式:")
    print("  1. 手动录入")
    print("  2. CSV文件导入")
    print("  3. 生成模板数据（测试用）")

    choice = input("\n请选择 (1-3): ").strip()

    if choice == "1":
        importer.import_from_manual_input()
    elif choice == "2":
        csv_file = input("请输入CSV文件路径: ").strip()
        importer.import_from_csv(csv_file)
    elif choice == "3":
        importer.import_from_template()
    else:
        print("[ERROR] Invalid choice")


if __name__ == "__main__":
    main()
