# -*- coding: utf-8 -*-
"""
多年度广东高考投档数据导入管道

功能：
1. 支持从PDF解析、Excel导入、CSV导入多种方式
2. 支持2023/2024/2025多年数据
3. 自动去重、院校层级分类、省份推断
4. 合并到 major_rank_data.json

使用方法：
    # 从已下载的PDF导入（需要先下载PDF到 data/ 目录）
    python scripts/import_multi_year.py --pdf data/2024_物理.pdf --year 2024

    # 从Excel导入
    python scripts/import_multi_year.py --excel data/2024_data.xlsx --year 2024

    # 从CSV导入
    python scripts/import_multi_year.py --csv data/2023_data.csv --year 2023

    # 导入所有已有的Excel/CSV文件
    python scripts/import_multi_year.py --auto

作者：学锋志愿教练团队
日期：2026-05-11
"""

import sys
import io
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional

# UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ==================== 配置 ====================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MAIN_DATA_FILE = DATA_DIR / "major_rank_data.json"
BACKUP_DIR = DATA_DIR / "backups"

# 985院校
KNOWN_985 = {
    "北京大学", "清华大学", "复旦大学", "上海交通大学", "浙江大学",
    "中国科学技术大学", "南京大学", "中国人民大学", "中山大学",
    "华南理工大学", "武汉大学", "华中科技大学", "西安交通大学",
    "哈尔滨工业大学", "北京师范大学", "南开大学", "天津大学",
    "同济大学", "东南大学", "厦门大学", "四川大学", "电子科技大学",
    "吉林大学", "东北大学", "大连理工大学", "山东大学",
    "中国海洋大学", "西北工业大学", "兰州大学", "北京航空航天大学",
    "北京理工大学", "中国农业大学", "国防科技大学", "中央民族大学",
    "华东师范大学", "中南大学", "湖南大学", "重庆大学", "西北农林科技大学",
}

# 211院校（不含985）
KNOWN_211 = {
    "暨南大学", "华南师范大学", "北京邮电大学", "北京交通大学",
    "北京科技大学", "北京化工大学", "北京工业大学", "北京林业大学",
    "北京中医药大学", "北京外国语大学", "中国传媒大学",
    "中央财经大学", "对外经济贸易大学", "中国政法大学",
    "华北电力大学", "中国矿业大学", "中国石油大学",
    "中国地质大学", "东北师范大学", "东北林业大学",
    "华东理工大学", "东华大学", "上海外国语大学", "上海财经大学",
    "上海大学", "苏州大学", "南京航空航天大学", "南京理工大学",
    "中国药科大学", "河海大学", "江南大学", "南京农业大学",
    "南京师范大学", "合肥工业大学", "安徽大学", "福州大学",
    "南昌大学", "郑州大学", "武汉理工大学",
    "华中师范大学", "华中农业大学", "中南财经政法大学",
    "湖南师范大学", "西南交通大学", "四川农业大学",
    "西南大学", "西南财经大学", "贵州大学", "云南大学",
    "西藏大学", "西北大学", "西安电子科技大学", "长安大学",
    "陕西师范大学", "青海大学", "宁夏大学", "新疆大学",
    "石河子大学", "海南大学", "广西大学", "内蒙古大学",
    "延边大学", "辽宁大学", "大连海事大学", "太原理工大学",
    "河北工业大学", "哈尔滨工程大学", "东北农业大学",
}

# 省份关键词映射
PROVINCE_KEYWORDS = {
    "北京": "北京", "清华": "北京", "北大": "北京",
    "上海": "上海", "复旦": "上海", "同济": "上海",
    "天津": "天津", "南开": "天津",
    "重庆": "重庆",
    "广东": "广东", "广州": "广东", "深圳": "广东", "华南": "广东",
    "暨南": "广东", "中山": "广东", "东莞": "广东", "佛山": "广东",
    "汕头": "广东", "韶关": "广东", "惠州": "广东", "肇庆": "广东",
    "嘉应": "广东", "岭南": "广东", "五邑": "广东", "韩山": "广东",
    "广东": "广东",
    "浙江": "浙江",
    "江苏": "江苏", "南京": "江苏", "苏州": "江苏", "东南": "江苏", "河海": "江苏", "江南": "江苏",
    "湖北": "湖北", "武汉": "湖北", "华中": "湖北",
    "湖南": "湖南", "中南": "湖南",
    "四川": "四川", "电子科技": "四川", "西南交通": "四川",
    "山东": "山东", "中国海洋": "山东",
    "福建": "福建", "厦门": "福建",
    "陕西": "陕西", "西安": "陕西", "西北": "陕西", "长安": "陕西",
    "辽宁": "辽宁", "大连": "辽宁", "东北": "辽宁",
    "吉林": "吉林",
    "黑龙江": "黑龙江", "哈尔滨": "黑龙江",
    "安徽": "安徽", "中国科学技术": "安徽",
    "江西": "江西",
    "河南": "河南",
    "河北": "河北",
    "广西": "广西",
    "云南": "云南",
    "贵州": "贵州",
    "海南": "海南",
    "甘肃": "甘肃", "兰州": "甘肃",
}


def get_university_level(uni_name):
    if uni_name in KNOWN_985:
        return "985"
    if uni_name in KNOWN_211:
        return "211"
    if any(kw in uni_name for kw in ["大学"]) and not any(
            kw in uni_name for kw in ["职业", "技术"]):
        return "普通本科"
    if any(kw in uni_name for kw in ["职业", "技术", "专科"]):
        return "高职"
    return "普通本科"


def get_province_from_name(uni_name):
    for keyword, province in PROVINCE_KEYWORDS.items():
        if keyword in uni_name:
            return province
    return ""


def import_from_pdf(pdf_path, year, category="物理"):
    """从PDF导入（需要pdfplumber）"""
    try:
        import pdfplumber
    except ImportError:
        print("[ERROR] 需要安装pdfplumber: pip install pdfplumber")
        return []

    print(f"[PDF] 解析: {pdf_path} ({year}, {category})")
    records = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 5:
                        continue
                    try:
                        uni_name = str(row[1] if len(row) > 1 else "").strip()  # 院校名称
                        group_code = str(row[2] if len(row) > 2 else "").strip()  # 专业组
                        min_score = int(float(str(row[4]).strip())) if len(row) > 4 and row[4] else 0
                        min_rank = int(str(row[5]).strip().replace(",", "")) if len(row) > 5 and row[5] else 0

                        if not uni_name or min_rank <= 0:
                            continue
                        if uni_name in ("院校名称", "院校代码", ""):
                            continue

                        record = {
                            "year": year,
                            "province": "广东",
                            "university_name": uni_name,
                            "major_name": f"专业组{group_code}" if group_code else "未分类",
                            "min_rank": min_rank,
                            "min_score": min_score,
                            "university_level": get_university_level(uni_name),
                            "university_province": get_province_from_name(uni_name),
                            "subject_type": "理科" if category == "物理" else "文科",
                            "data_source": f"广东省教育考试院_{year}_官方PDF",
                            "is_official": True,
                            "verified": True,
                            "group_code": group_code,
                        }
                        records.append(record)
                    except (ValueError, IndexError):
                        continue

    print(f"[PDF] 提取了 {len(records)} 条记录")
    return records


def import_from_excel(excel_path, year):
    """从Excel导入"""
    import pandas as pd

    print(f"[Excel] 读取: {excel_path}")
    df = pd.read_excel(excel_path)
    print(f"  列名: {list(df.columns)}, 行数: {len(df)}")

    records = []
    seen = set()

    # 列名映射
    col_map = {}
    for col in df.columns:
        col_str = str(col)
        if "院校" in col_str and "代码" in col_str:
            col_map["uni_code"] = col
        elif "院校" in col_str or "大学" in col_str or "学校" in col_str:
            col_map["uni_name"] = col
        elif "专业" in col_str and "代码" in col_str:
            col_map["group_code"] = col
        elif "分数" in col_str or "最低分" in col_str:
            col_map["min_score"] = col
        elif "排位" in col_str or "位次" in col_str:
            col_map["min_rank"] = col
        elif "计划" in col_str:
            col_map["plan_count"] = col
        elif "科类" in col_str or "类别" in col_str:
            col_map["category"] = col
        elif "专业" in col_str and "名称" in col_str:
            col_map["major_name"] = col

    # 通用映射（适用于已处理过的文件）
    if not col_map.get("uni_name"):
        for col in df.columns:
            if col in ("university", "院校名称", "大学名称"):
                col_map["uni_name"] = col
    if not col_map.get("min_score"):
        for col in df.columns:
            if col in ("min_score", "最低分", "投档最低分"):
                col_map["min_score"] = col
    if not col_map.get("min_rank"):
        for col in df.columns:
            if col in ("min_rank", "最低排位", "投档最低排位"):
                col_map["min_rank"] = col

    print(f"  列映射: {col_map}")

    for idx, row in df.iterrows():
        try:
            uni_name = str(row.get(col_map.get("uni_name", ""), "")).strip()
            if not uni_name or uni_name == "nan":
                continue

            min_score = int(row.get(col_map.get("min_score", 0), 0)) if col_map.get("min_score") else 0
            min_rank = int(row.get(col_map.get("min_rank", 0), 0)) if col_map.get("min_rank") else 0
            if min_rank <= 0:
                continue

            group_code = str(row.get(col_map.get("group_code", ""), "")).strip()
            category = str(row.get(col_map.get("category", ""), "")).strip() if col_map.get("category") else "物理"
            major_name = str(row.get(col_map.get("major_name", "")), "").strip() if col_map.get("major_name") else ""

            if not major_name or major_name == "nan":
                major_name = f"专业组{group_code}" if group_code else "未分类"

            dedup = (uni_name, major_name, min_rank, year)
            if dedup in seen:
                continue
            seen.add(dedup)

            subject_type = "理科" if "物理" in category or "理科" in category else "文科"

            record = {
                "year": year,
                "province": "广东",
                "university_name": uni_name,
                "major_name": major_name,
                "min_rank": min_rank,
                "min_score": min_score,
                "university_level": get_university_level(uni_name),
                "university_province": get_province_from_name(uni_name),
                "subject_type": subject_type,
                "data_source": f"广东省教育考试院_{year}_官方数据",
                "is_official": True,
                "verified": True,
                "group_code": group_code if group_code != "nan" else "",
            }
            records.append(record)
        except Exception as e:
            if idx < 5:
                print(f"  [WARN] 行{idx}: {e}")

    print(f"[Excel] 提取了 {len(records)} 条记录")
    return records


def import_from_csv(csv_path, year):
    """从CSV导入 - 尝试自动识别列"""
    import pandas as pd

    print(f"[CSV] 读取: {csv_path}")
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    records = []
    seen = set()

    for idx, row in df.iterrows():
        try:
            # 尝试不同列名
            for name_col in ["院校名称", "university", "学校名称", "大学", "院校"]:
                uni_name = str(row.get(name_col, "")).strip()
                if uni_name and uni_name != "nan":
                    break

            if not uni_name:
                continue

            for rank_col in ["最低排位", "min_rank", "投档最低排位", "排位", "位次"]:
                min_rank = int(row.get(rank_col, 0))
                if min_rank > 0:
                    break

            if min_rank <= 0:
                continue

            major_name = str(row.get("major_name", row.get("专业名称", row.get("专业组", "")))).strip()
            if not major_name or major_name == "nan":
                major_name = "未分类"

            dedup = (uni_name, major_name, min_rank, year)
            if dedup in seen:
                continue
            seen.add(dedup)

            record = {
                "year": year,
                "province": "广东",
                "university_name": uni_name,
                "major_name": major_name,
                "min_rank": min_rank,
                "min_score": int(row.get("min_score", row.get("最低分", 0)) or 0),
                "university_level": get_university_level(uni_name),
                "university_province": get_province_from_name(uni_name),
                "subject_type": "理科",
                "data_source": f"广东省教育考试院_{year}_CSV",
                "is_official": True,
                "verified": True,
            }
            records.append(record)
        except Exception:
            pass

    print(f"[CSV] 提取了 {len(records)} 条记录")
    return records


def merge_to_main(records: List[Dict], year: int):
    """合并到主数据文件"""
    print(f"\n[合并] 合并 {len(records):,} 条{year}年记录到 major_rank_data.json...")

    # 备份
    BACKUP_DIR.mkdir(exist_ok=True)
    if MAIN_DATA_FILE.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"major_rank_data_backup_{timestamp}.json"
        shutil.copy2(MAIN_DATA_FILE, backup_path)
        print(f"  已备份到: {backup_path}")

    # 加载现有数据
    with open(MAIN_DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    existing = data.get("major_rank_data", [])
    print(f"  现有记录: {len(existing):,}")

    # 移除同一年份的旧数据
    kept = [r for r in existing if isinstance(r, dict) and r.get("year") != year]
    removed = len(existing) - len(kept)
    print(f"  移除旧{year}年数据: {removed:,}")

    # 合并
    merged = kept + records
    print(f"  合并后总记录: {len(merged):,}")

    # 保存
    output = {
        "major_rank_data": merged,
        "metadata": {
            "total_records": len(merged),
            "last_updated": datetime.now().isoformat(),
            f"guangdong_{year}_source": f"广东省教育考试院官方数据",
        },
    }
    with open(MAIN_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 统计
    print(f"\n[统计] {year}年广东数据:")
    gd = [r for r in records if r.get("province") == "广东"]
    print(f"  总记录: {len(gd):,}")
    print(f"  院校数: {len(set(r['university_name'] for r in gd)):,}")
    ranks = [r["min_rank"] for r in gd if r.get("min_rank")]
    print(f"  位次范围: {min(ranks):,} - {max(ranks):,}")

    levels = defaultdict(int)
    for r in gd:
        levels[r.get("university_level", "?")] += 1
    print(f"  层级分布: {dict(levels)}")

    provs = defaultdict(int)
    for r in gd:
        provs[r.get("university_province", "?")] += 1
    local = provs.get("广东", 0)
    out = sum(v for k, v in provs.items() if k != "广东" and k != "?")
    print(f"  广东本地: {local:,}, 省外: {out:,}")

    return len(merged)


def auto_import():
    """自动导入 data/ 目录下的所有Excel和CSV文件"""
    print("=" * 60)
    print("自动导入模式 - 扫描 data/ 目录")
    print("=" * 60)

    for f in sorted(DATA_DIR.glob("*.xlsx")):
        name = f.name.lower()
        if "2024" in name or "2023" in name:
            year = 2024 if "2024" in name else 2023
            print(f"\n发现 {year} 年Excel: {f.name}")
            records = import_from_excel(str(f), year)
            if records:
                merge_to_main(records, year)

    for f in sorted(DATA_DIR.glob("*.csv")):
        name = f.name.lower()
        if "2024" in name and ("物理" in name or "历史" in name or "投档" in name):
            year = 2024
        elif "2023" in name and ("物理" in name or "历史" in name or "投档" in name):
            year = 2023
        else:
            continue
        print(f"\n发现 {year} 年CSV: {f.name}")
        records = import_from_csv(str(f), year)
        if records:
            merge_to_main(records, year)


def main():
    parser = argparse.ArgumentParser(description="多年度广东高考数据导入")
    parser.add_argument("--pdf", type=str, help="PDF文件路径")
    parser.add_argument("--excel", type=str, help="Excel文件路径")
    parser.add_argument("--csv", type=str, help="CSV文件路径")
    parser.add_argument("--year", type=int, required=True, help="数据年份 (2023/2024/2025)")
    parser.add_argument("--category", type=str, default="物理", help="科类 (物理/历史)")
    parser.add_argument("--auto", action="store_true", help="自动扫描data目录")
    args = parser.parse_args()

    if args.auto:
        auto_import()
        return

    records = []
    if args.pdf:
        records = import_from_pdf(args.pdf, args.year, args.category)
    elif args.excel:
        records = import_from_excel(args.excel, args.year)
    elif args.csv:
        records = import_from_csv(args.csv, args.year)
    else:
        print("[ERROR] 请指定 --pdf, --excel, --csv 或 --auto")
        return

    if records:
        merge_to_main(records, args.year)
    else:
        print("[ERROR] 未提取到任何数据")


if __name__ == "__main__":
    main()
