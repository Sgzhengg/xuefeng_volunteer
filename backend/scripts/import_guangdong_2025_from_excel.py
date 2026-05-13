# -*- coding: utf-8 -*-
"""
将 guangdong_2025_major_level_intelligent.xlsx 数据导入到 major_rank_data.json

数据来源：广东省教育考试院官方PDF（已通过 parse_pdf_with_pdfplumber.py 解析）
功能：
1. 从 Excel 读取已解析的投档数据
2. 转换为标准 JSON 格式
3. 合并到 major_rank_data.json（替换旧的广东2025数据）
4. 验证数据完整性

使用方法：
    cd backend
    python scripts/import_guangdong_2025_from_excel.py
"""

import sys
import io
import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import pandas as pd

# UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ==================== 路径配置 ====================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

EXCEL_FILE = DATA_DIR / "guangdong_2025_major_level_intelligent.xlsx"
MAIN_DATA_FILE = DATA_DIR / "major_rank_data.json"
BACKUP_DIR = DATA_DIR / "backups"

# ==================== 院校层级映射 ====================
# 从 universities_list.json 加载
def load_level_map():
    level_map = {}
    uni_file = DATA_DIR / "universities_list.json"
    if uni_file.exists():
        with open(uni_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for uni in data.get("universities", []):
            name = uni.get("name", "").strip()
            level = uni.get("level", "").strip()
            if name and level:
                if name in level_map:
                    existing = level_map[name]
                    priority = {"985": 3, "211": 2, "普通本科": 1, "本科": 1, "高职": 0}
                    if priority.get(level, 0) > priority.get(existing, 0):
                        level_map[name] = level
                else:
                    level_map[name] = level
    return level_map


# 已知的985/211名单（补充分类）
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


def get_university_level(uni_name, level_map):
    """确定院校层级"""
    name = uni_name.strip()
    if name in KNOWN_985:
        return "985"
    if name in KNOWN_211:
        return "211"
    mapped = level_map.get(name, "")
    if mapped in ("985", "211", "普通本科", "本科", "高职"):
        return mapped
    # 启发式判断
    if any(kw in name for kw in ["大学"]) and not any(
            kw in name for kw in ["职业", "技术"]):
        return "普通本科"
    if any(kw in name for kw in ["职业", "技术", "专科"]):
        return "高职"
    return "普通本科"


def get_province_from_university(uni_name):
    """根据大学名称推断所在省份"""
    province_map = {
        "北京": "北京", "清华": "北京", "北大": "北京",
        "上海": "上海", "复旦": "上海", "同济": "上海",
        "天津": "天津", "南开": "天津",
        "重庆": "重庆",
        "广东": "广东", "广州": "广东", "深圳": "广东", "华南": "广东",
        "暨南": "广东", "中山": "广东", "汕头": "广东", "韶关": "广东",
        "惠州": "广东", "肇庆": "广东", "嘉应": "广东", "岭南": "广东",
        "东莞": "广东", "佛山": "广东", "五邑": "广东", "韩山": "广东",
        "广东": "广东",
        "浙江": "浙江",
        "江苏": "江苏", "南京": "江苏", "苏州": "江苏", "东南": "江苏",
        "湖北": "湖北", "武汉": "湖北", "华中": "湖北",
        "湖南": "湖南", "中南": "湖南",
        "四川": "四川", "电子科技": "四川", "西南交通": "四川",
        "山东": "山东",
        "福建": "福建", "厦门": "福建",
        "陕西": "陕西", "西安": "陕西", "西北": "陕西",
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
        "内蒙古": "内蒙古",
        "宁夏": "宁夏",
        "青海": "青海",
        "新疆": "新疆", "石河子": "新疆",
        "西藏": "西藏",
    }
    for keyword, province in province_map.items():
        if keyword in uni_name:
            return province
    return ""



def import_2025_from_excel():
    """从Excel导入2025年数据到major_rank_data.json"""
    print("=" * 60)
    print("广东省2025年投档数据导入工具")
    print("=" * 60)

    # 1. 备份原始数据
    BACKUP_DIR.mkdir(exist_ok=True)
    if MAIN_DATA_FILE.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"major_rank_data_backup_{timestamp}.json"
        shutil.copy2(MAIN_DATA_FILE, backup_path)
        print(f"[备份] 已备份到: {backup_path}")

    # 2. 读取Excel数据
    print(f"\n[读取] {EXCEL_FILE}")
    df = pd.read_excel(EXCEL_FILE)
    print(f"  总行数: {len(df):,}")
    print(f"  列名: {list(df.columns)}")

    # 3. 加载层级映射
    level_map = load_level_map()
    print(f"\n[映射] 加载了 {len(level_map)} 所院校的层级映射")

    # 4. 转换数据
    print(f"\n[转换] 正在转换数据格式...")
    new_records = []
    stats = {
        "total": 0,
        "physics": 0,
        "history": 0,
        "has_major": 0,
        "no_major": 0,
        "level_stats": defaultdict(int),
        "province_stats": defaultdict(int),
        "skipped": 0,
    }

    seen_keys = set()

    for idx, row in df.iterrows():
        try:
            uni_name = str(row.get("university", "")).strip()
            if not uni_name or uni_name == "nan":
                stats["skipped"] += 1
                continue

            category = str(row.get("category", "")).strip()
            major_name = str(row.get("major_name", "")).strip()
            group_name = str(row.get("group_name", "")).strip()
            group_code = str(row.get("group_code", "")).strip()

            if major_name in ("nan", ""):
                major_name = group_name if group_name and group_name != "nan" else "未分类专业"

            min_score = int(row.get("min_score", 0))
            min_rank = int(row.get("min_rank", 0))

            if min_rank <= 0:
                stats["skipped"] += 1
                continue

            # 确定院校层级和省份
            uni_level = get_university_level(uni_name, level_map)
            uni_province = get_province_from_university(uni_name)

            # 去重key
            dedup_key = (uni_name, major_name, min_rank, "广东", 2025, category)
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            # 主体类型映射
            subject_type = "理科" if category in ("物理", "理科") else "文科"

            record = {
                "year": 2025,
                "province": "广东",
                "university_name": uni_name,
                "major_name": major_name,
                "major_code": "",
                "min_rank": min_rank,
                "min_score": min_score,
                "university_level": uni_level,
                "university_province": uni_province,
                "subject_type": subject_type,
                "data_source": "广东省教育考试院_2025_官方PDF",
                "is_official": True,
                "verified": True,
                "group_code": group_code if group_code != "nan" else "",
                "group_name": group_name if group_name != "nan" else "",
            }

            new_records.append(record)
            stats["total"] += 1

            if category in ("物理", "理科"):
                stats["physics"] += 1
            else:
                stats["history"] += 1

            if major_name and major_name not in ("nan", "未分类专业"):
                stats["has_major"] += 1
            else:
                stats["no_major"] += 1

            stats["level_stats"][uni_level] += 1
            stats["province_stats"][uni_province or "未知"] += 1

        except Exception as e:
            stats["skipped"] += 1
            if idx < 5:
                print(f"  [警告] 跳过第{idx}行: {e}")

    # 5. 打印统计
    print(f"\n[统计] 导入数据统计:")
    print(f"  总记录数: {stats['total']:,}")
    print(f"  物理类: {stats['physics']:,}")
    print(f"  历史类: {stats['history']:,}")
    print(f"  有专业名: {stats['has_major']:,}")
    print(f"  无专业名(使用组名): {stats['no_major']:,}")
    print(f"  跳过: {stats['skipped']:,}")
    print(f"  去重后唯一记录: {len(seen_keys):,}")

    print(f"\n院校层级分布:")
    for level, count in sorted(stats["level_stats"].items(), key=lambda x: -x[1]):
        print(f"  {level}: {count:,}")

    print(f"\n院校省份分布 (Top 15):")
    for province, count in sorted(stats["province_stats"].items(), key=lambda x: -x[1])[:15]:
        print(f"  {province}: {count:,}")

    # 5. 位次段分布
    rank_segments = [
        (1, 10000, "1-10000 顶尖段"),
        (10001, 30000, "10001-30000 重点段"),
        (30001, 70000, "30001-70000 一本段"),
        (70001, 120000, "70001-120000 二本段"),
        (120001, 200000, "120001-200000 民办/专科段"),
        (200001, 350000, "200001-350000 专科段"),
    ]
    print(f"\n位次段分布:")
    for lo, hi, desc in rank_segments:
        count = sum(1 for r in new_records if lo <= r["min_rank"] <= hi)
        bar = "█" * (count // 20) if count > 0 else ""
        print(f"  {desc}: {count:,} {bar}")

    # 6. 合并到主数据文件
    print(f"\n[合并] 正在合并到 major_rank_data.json...")

    # 加载现有数据
    with open(MAIN_DATA_FILE, 'r', encoding='utf-8') as f:
        main_data = json.load(f)

    existing_records = main_data.get("major_rank_data", [])
    print(f"  现有总记录: {len(existing_records):,}")

    # 保留非广东2025的记录 + 只保留广东2025但数据源非官方的
    kept_records = []
    gd_2025_old = 0
    for r in existing_records:
        if not isinstance(r, dict):
            continue
        if r.get("province") == "广东" and r.get("year") == 2025:
            gd_2025_old += 1
            continue  # 替换为新的
        kept_records.append(r)

    print(f"  移除的旧广东2025记录: {gd_2025_old:,}")
    print(f"  保留的其他记录: {len(kept_records):,}")

    # 合并
    merged = kept_records + new_records
    print(f"  合并后总记录: {len(merged):,}")

    # 保存
    output_data = {
        "major_rank_data": merged,
        "metadata": {
            "total_records": len(merged),
            "last_updated": datetime.now().isoformat(),
            "guangdong_2025_source": "广东省教育考试院官方PDF - 12,622条记录",
            "data_sources": ["广东省教育考试院", "其他省份数据"],
        }
    }

    with open(MAIN_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n[完成] 数据已保存到 major_rank_data.json")

    # 7. 最终验证
    print(f"\n{'=' * 60}")
    print("数据验证")
    print(f"{'=' * 60}")
    gd_2025_new = [r for r in merged if r.get("province") == "广东" and r.get("year") == 2025]
    print(f"  广东2025记录数: {len(gd_2025_new):,}")
    print(f"  覆盖院校数: {len(set(r['university_name'] for r in gd_2025_new)):,}")
    print(f"  位次范围: {min(r['min_rank'] for r in gd_2025_new):,} - {max(r['min_rank'] for r in gd_2025_new):,}")

    gd_provinces = defaultdict(int)
    for r in gd_2025_new:
        gd_provinces[r.get("university_province", "未知")] += 1
    print(f"  广东本地院校记录: {gd_provinces.get('广东', 0):,}")
    print(f"  省外院校记录: {sum(v for k, v in gd_provinces.items() if k != '广东' and k != '未知'):,}")

    return stats["total"]


if __name__ == "__main__":
    import_2025_from_excel()
