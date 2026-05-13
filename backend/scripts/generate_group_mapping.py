#!/usr/bin/env python3
"""
生成专业组映射表
基于现有数据和常见专业分组规律
"""
import json
from pathlib import Path
from collections import defaultdict

def generate_professional_group_mapping():
    """生成专业组映射表"""
    print("=== 生成专业组映射表 ===")

    # 加载现有数据
    data_path = Path("../data/major_rank_data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])

    # 1. 基于现有数据提取专业组
    existing_groups = defaultdict(lambda: {
        "group_code": "",
        "majors": set(),
        "universities": set(),
        "count": 0
    })

    for record in records:
        university = record.get("university_name", "")
        group_code = record.get("group_code", 0)
        major = record.get("major_name", "")

        if group_code and university and major:
            key = f"{university}_{group_code}"
            existing_groups[key]["group_code"] = group_code
            existing_groups[key]["majors"].add(major)
            existing_groups[key]["universities"].add(university)
            existing_groups[key]["count"] += 1

    print(f"从现有数据中提取了 {len(existing_groups)} 个专业组")

    # 2. 补充常见专业组映射（基于教育部专业分类）
    common_major_groups = {
        "计算机类": ["计算机科学与技术", "软件工程", "网络工程", "信息安全", "物联网工程", "数字媒体技术", "智能科学与技术", "数据科学与大数据技术", "信息管理与信息系统"],
        "电子信息类": ["电子信息工程", "通信工程", "微电子科学与工程", "光电信息科学与工程", "信息工程", "电子科学与技术", "集成电路设计与集成系统"],
        "机械类": ["机械工程", "机械设计制造及其自动化", "机械电子工程", "车辆工程", "工业设计", "过程装备与控制工程", "机械工程", "汽车服务工程"],
        "电气类": ["电气工程及其自动化", "智能电网信息工程", "光源与照明", "电气工程与智能控制", "电机电器智能化"],
        "土木类": ["土木工程", "建筑环境与能源应用工程", "给排水科学与工程", "建筑电气与智能化", "城市地下空间工程", "道路桥梁与渡河工程"],
        "经济管理类": ["经济学", "金融学", "国际经济与贸易", "工商管理", "市场营销", "会计学", "财务管理", "人力资源管理", "电子商务", "旅游管理"],
        "法学类": ["法学", "知识产权", "监狱学"],
        "文学类": ["汉语言文学", "英语", "日语", "法语", "德语", "西班牙语", "阿拉伯语", "翻译", "商务英语", "新闻学", "广告学"],
        "理学类": ["数学与应用数学", "物理学", "化学", "生物科学", "地理科学", "统计学", "应用化学", "生物技术", "生态学"],
        "医学类": ["临床医学", "口腔医学", "预防医学", "药学", "中药学", "医学影像学", "医学检验技术", "护理学", "康复治疗学"],
        "教育学类": ["教育学", "学前教育", "小学教育", "特殊教育", "教育技术学", "体育教育", "运动训练"],
        "化工类": ["化学工程与工艺", "制药工程", "能源化学工程", "生物工程", "食品科学与工程", "轻化工程", "环境工程", "环境科学"],
        "材料类": ["材料科学与工程", "高分子材料与工程", "复合材料与工程", "材料物理", "材料化学", "冶金工程", "金属材料工程", "无机非金属材料工程"],
        "自动化类": ["自动化", "机器人工程", "轨道交通信号与控制", "电子信息工程", "计算机科学与技术"],
        "外语类": ["英语", "日语", "法语", "德语", "俄语", "西班牙语", "阿拉伯语", "翻译", "商务英语"]
    }

    # 3. 为每个专业组分配模拟的专业组代码
    group_mapping = {}
    group_id = 1000

    # 3.1 添加现有数据中的专业组
    for key, info in existing_groups.items():
        university = list(info["universities"])[0] if info["universities"] else ""
        majors = list(info["majors"])

        if len(majors) >= 1:
            mapping_key = f"{university}_group_{info['group_code']}"
            group_mapping[mapping_key] = {
                "group_code": info["group_code"],
                "majors": majors,
                "university": university
            }

    # 3.2 补充热门院校的常见专业组
    top_universities = [
        "中山大学", "华南理工大学", "暨南大学", "华南师范大学",
        "北京大学", "清华大学", "复旦大学", "上海交通大学",
        "浙江大学", "南京大学", "武汉大学", "华中科技大学",
        "四川大学", "重庆大学", "湖南大学", "中南大学",
        "山东大学", "吉林大学", "哈尔滨工业大学", "大连理工大学"
    ]

    for university in top_universities:
        for group_name, majors in common_major_groups.items():
            # 为每个院校的专业组分配唯一代码
            group_code = group_id
            group_id += 1

            mapping_key = f"{university}_{group_name}"
            group_mapping[mapping_key] = {
                "group_code": group_code,
                "majors": majors[:8],  # 限制专业数量
                "university": university,
                "group_name": group_name
            }

    print(f"生成了 {len(group_mapping)} 个专业组映射")

    # 4. 保存映射表
    mapping_path = Path("../data/professional_group_mapping.json")
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(group_mapping, f, ensure_ascii=False, indent=2)

    print(f"[OK] 专业组映射表已保存到: {mapping_path}")

    # 5. 统计信息
    print(f"\n=== 映射表统计 ===")
    print(f"总专业组数：{len(group_mapping)}")

    major_count = 0
    for key, info in group_mapping.items():
        major_count += len(info["majors"])

    print(f"总专业映射数：{major_count}")
    print(f"平均每组专业数：{major_count / len(group_mapping):.1f}")

    return group_mapping

if __name__ == "__main__":
    generate_professional_group_mapping()