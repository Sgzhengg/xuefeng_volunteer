# -*- coding: utf-8 -*-
"""
将专业组数据展开为专业级数据

功能：
1. 读取专业组投档线数据
2. 根据专业组映射表展开为专业级数据
3. 智能处理缺失的映射关系
4. 生成展开后的专业级录取数据

使用方法：
    python expand_major_groups.py <input_json> <mapping_json> <output_json>

作者：学锋志愿教练团队
版本：1.0.0
"""

import json
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict

# ==================== 日志配置 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'expand_major_groups_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== 默认专业映射 ====================

# 当专业组映射表缺失时，使用常见专业组合作为默认映射
DEFAULT_MAJOR_COMBINATIONS = {
    "计算机类": ["计算机科学与技术", "软件工程", "网络工程", "信息安全", "物联网工程"],
    "电子信息类": ["电子信息工程", "通信工程", "电子科学与技术", "微电子科学与工程"],
    "机械类": ["机械工程", "机械设计制造及其自动化", "机械电子工程", "车辆工程"],
    "土木类": ["土木工程", "建筑环境与能源应用工程", "给排水科学与工程", "建筑电气与智能化"],
    "材料类": ["材料科学与工程", "材料物理", "材料化学", "冶金工程"],
    "化工与制药类": ["化学工程与工艺", "制药工程", "资源循环科学与工程"],
    "工商管理类": ["工商管理", "市场营销", "会计学", "财务管理", "人力资源管理"],
    "公共管理类": ["行政管理", "公共事业管理", "劳动与社会保障", "土地资源管理"],
    "外国语言文学类": ["英语", "商务英语", "翻译", "日语", "法语"],
    "新闻传播学类": ["新闻学", "传播学", "广告学", "网络与新媒体"],
    "经济学类": ["经济学", "经济统计学", "国民经济管理", "资源与环境经济学"],
    "金融学类": ["金融学", "金融工程", "投资学", "保险学"],
    "法学类": ["法学", "知识产权", "监狱学"],
    "数学类": ["数学与应用数学", "信息与计算科学", "统计学"],
    "物理类": ["物理学", "应用物理学", "核物理"],
    "化学类": ["化学", "应用化学", "化学生物学"],
    "生物科学类": ["生物科学", "生物技术", "生态学"],
    "电气类": ["电气工程及其自动化", "智能电网信息工程", "光源与照明"],
    "自动化类": ["自动化", "机器人工程", "轨道交通信号与控制"],
    "航空航天类": ["航空航天工程", "飞行器设计与工程", "飞行器制造工程"],
    "水利类": ["水利水电工程", "水文与水资源工程", "港口航道与海岸工程"],
    "测绘类": ["测绘工程", "遥感科学与技术", "导航工程"],
    "交通运输类": ["交通运输", "交通工程", "航海技术"],
    "海洋工程类": ["船舶与海洋工程", "海洋工程", "海洋资源开发技术"],
    "环境科学与工程类": ["环境科学与工程", "环境工程", "环境科学"],
    "食品科学与工程类": ["食品科学与工程", "食品质量与安全", "粮食工程"],
    "建筑类": ["建筑学", "城乡规划", "风景园林", "历史建筑保护工程"],
    "生物工程类": ["生物工程", "生物医学工程", "制药工程"],
    "农业工程类": ["农业工程", "农业机械化及其自动化", "农业电气化"],
    "林业工程类": ["林业工程", "森林工程", "木材科学与工程"],
    "基础医学类": ["基础医学", "生物医学", "生物信息学"],
    "临床医学类": ["临床医学", "麻醉学", "医学影像学", "精神医学"],
    "口腔医学类": ["口腔医学"],
    "公共卫生与预防医学类": ["预防医学", "食品卫生与营养学", "全球健康学"],
    "中医学类": ["中医学", "针灸推拿学", "藏医学"],
    "药学类": ["药学", "药物制剂", "中药学"],
    "中药学类": ["中药学", "中药制药", "中草药栽培与鉴定"],
    "法医学类": ["法医学"],
    "护理学类": ["护理学", "助产学"],
    "管理科学与工程类": ["管理科学", "信息管理与信息系统", "工程管理", "房地产开发与管理"],
    "图书情报与档案管理类": ["图书馆学", "档案学", "信息资源管理"],
    "音乐与舞蹈学类": ["音乐表演", "音乐学", "作曲与作曲技术理论", "舞蹈表演", "舞蹈学"],
    "戏剧与影视学类": ["表演", "戏剧影视文学", "广播电视编导", "戏剧影视导演", "戏剧影视美术设计"],
    "美术学类": ["美术学", "绘画", "雕塑", "摄影"],
    "设计学类": ["视觉传达设计", "环境设计", "产品设计", "服装与服饰设计", "数字媒体艺术"],
    "体育学类": ["体育教育", "运动训练", "社会体育指导与管理", "运动人体科学"],
    "教育学类": ["教育学", "科学教育", "人文教育", "小学教育"],
    "中国语言文学类": ["汉语言文学", "汉语言", "汉语国际教育", "中国少数民族语言文学"],
    "历史学类": ["历史学", "世界史", "考古学", "文物与博物馆学", "文物保护技术"],
    "哲学类": ["哲学", "逻辑学", "宗教学", "伦理学"],
    "社会学类": ["社会学", "社会工作", "人类学", "女性学"],
    "心理学类": ["心理学", "应用心理学"]
}

# ==================== 专业组展开函数 ====================

def expand_major_groups(raw_data_path: str, mapping_path: str, output_path: str):
    """
    将专业组数据展开为专业级录取数据

    Args:
        raw_data_path: 原始投档线数据路径
        mapping_path: 专业组映射表路径
        output_path: 输出路径
    """
    logger.info("[START] 开始展开专业组数据")
    logger.info(f"[INPUT] 原始数据: {raw_data_path}")
    logger.info(f"[MAPPING] 映射文件: {mapping_path}")

    try:
        # 1. 加载原始数据
        logger.info("[READ] 正在读取原始投档线数据...")
        with open(raw_data_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        logger.info(f"[OK] 原始数据加载完成: {len(raw_data)} 条记录")

        # 2. 加载或生成映射表
        if mapping_path and Path(mapping_path).exists():
            logger.info("[READ] 正在读取专业组映射表...")
            with open(mapping_path, 'r', encoding='utf-8') as f:
                group_mapping = json.load(f)
            logger.info(f"[OK] 映射表加载完成: {len(group_mapping)} 个专业组")
        else:
            logger.info("[INFO] 映射表文件不存在，使用默认专业组合")
            group_mapping = generate_default_mapping(raw_data)

        # 3. 展开数据
        logger.info("[EXPAND] 正在展开专业组数据...")
        expanded_records = []
        statistics = {
            "total_groups": 0,
            "expanded_count": 0,
            "kept_as_group": 0,
            "mapping_missing": 0
        }

        for record in raw_data:
            statistics["total_groups"] += 1

            # 提取专业组信息
            group_code = record.get("major_code", "")
            university_name = record.get("university_name", "")

            # 查找映射关系
            majors = find_major_mapping(group_code, university_name, group_mapping, record)

            if majors:
                # 展开为专业级数据
                for major in majors:
                    expanded_record = {
                        **record,
                        "major_name": major["major_name"],
                        "major_code": major.get("major_code", f"{group_code}_{major['major_name'][:2]}"),
                        "expanded": True,
                        "original_group_code": group_code
                    }
                    expanded_records.append(expanded_record)
                statistics["expanded_count"] += len(majors)
            else:
                # 没有找到映射，保留专业组级别数据
                record["expanded"] = False
                record["expansion_note"] = "专业组映射缺失，保留原始数据"
                expanded_records.append(record)
                statistics["kept_as_group"] += 1
                statistics["mapping_missing"] += 1

        # 4. 保存展开后的数据
        logger.info("[SAVE] 正在保存展开后的数据...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(expanded_records, f, ensure_ascii=False, indent=2)

        # 5. 输出统计信息
        logger.info("=" * 50)
        logger.info("[SUCCESS] 专业组展开完成！")
        logger.info(f"[STATS] 原始专业组数: {statistics['total_groups']}")
        logger.info(f"[STATS] 展开为专业级: {statistics['expanded_count']} 条")
        logger.info(f"[STATS] 保留专业组级: {statistics['kept_as_group']} 条")
        logger.info(f"[STATS] 映射关系缺失: {statistics['mapping_missing']} 条")
        logger.info(f"[STATS] 展开率: {statistics['expanded_count'] / statistics['total_groups'] * 100:.1f}%")
        logger.info(f"[OUTPUT] 输出文件: {output_path}")
        logger.info("=" * 50)

        return expanded_records

    except Exception as e:
        logger.error(f"[ERROR] 展开失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def generate_default_mapping(raw_data: List[Dict]) -> Dict:
    """
    基于原始数据生成默认映射表

    Args:
        raw_data: 原始投档线数据

    Returns:
        生成的映射表
    """
    logger.info("[GEN] 正在生成默认专业映射表...")

    mapping = {}
    statistics = defaultdict(int)

    for record in raw_data:
        university_name = record.get("university_name", "")
        major_name = record.get("major_name", "")

        if "未分专业" in major_name or "专业组" in major_name:
            # 尝试从专业组代码推断专业类型
            group_code = record.get("major_code", "")

            # 根据专业组代码中的关键词推断专业类别
            for category, majors in DEFAULT_MAJOR_COMBINATIONS.items():
                if category in group_code or category in major_name:
                    # 为该专业组创建映射
                    if group_code not in mapping:
                        mapping[group_code] = []
                        statistics["auto_detected"] += 1

                    for major in majors:
                        mapping[group_code].append({
                            "major_name": major,
                            "major_code": f"{group_code}_{major[:2]}",
                            "source": "auto_detected"
                        })
                    break

    logger.info(f"[OK] 自动生成映射: {len(mapping)} 个专业组")
    logger.info(f"[STATS] 映射关系: {statistics['auto_detected']} 个自动检测")

    return mapping

def find_major_mapping(group_code: str, university_name: str,
                      group_mapping: Dict, record: Dict) -> List[Dict]:
    """
    查找专业组的专业映射

    Args:
        group_code: 专业组代码
        university_name: 院校名称
        group_mapping: 专业组映射表
        record: 原始记录

    Returns:
        专业列表
    """
    # 1. 直接使用专业组代码查找
    if group_code in group_mapping:
        return group_mapping[group_code]

    # 2. 使用院校名称+专业组代码查找
    key = f"{university_name}_{group_code}"
    if key in group_mapping:
        return group_mapping[key]

    # 3. 从专业名称推断
    major_name = record.get("major_name", "")
    for category, majors in DEFAULT_MAJOR_COMBINATIONS.items():
        if category in major_name or category in group_code:
            return [
                {
                    "major_name": major,
                    "major_code": f"{group_code}_{major[:2]}",
                    "source": "default_combination"
                }
                for major in majors
            ]

    return []

# ==================== 主程序入口 ====================

def main():
    """主程序入口"""
    if len(sys.argv) < 3:
        print("=" * 60)
        print("专业组数据展开工具")
        print("=" * 60)
        print()
        print("使用方法:")
        print("  python expand_major_groups.py <input_json> <mapping_json> <output_json>")
        print()
        print("参数说明:")
        print("  input_json: 输入的原始投档线JSON文件")
        print("  mapping_json: 专业组映射表JSON文件（可选，使用'auto'自动生成）")
        print("  output_json: 输出的展开后JSON文件")
        print()
        print("示例:")
        print("  python expand_major_groups.py guangdong_2025_本科_raw.json mapping.json expanded.json")
        print("  python expand_major_groups.py guangdong_2025_本科_raw.json auto expanded.json")
        print()
        return

    input_json = sys.argv[1]
    mapping_json = sys.argv[2] if sys.argv[2] != "auto" else None
    output_json = sys.argv[3]

    # 验证文件路径
    if not Path(input_json).exists():
        logger.error(f"[ERROR] 输入文件不存在: {input_json}")
        return

    # 执行展开
    expand_major_groups(input_json, mapping_json, output_json)

if __name__ == "__main__":
    main()