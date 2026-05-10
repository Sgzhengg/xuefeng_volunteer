#!/usr/bin/env python3
"""
生成缺失院校清单并建议补充数据优先级
"""
import json
from pathlib import Path
from datetime import datetime

# 广东本地院校完整清单（应补充的院校）
GUANGDONG_UNIVERSITIES = {
    "广东重点本科": [
        {"name": "广东工业大学", "priority": "high", "reason": "省内理工重点院校，录取量大"},
        {"name": "深圳大学", "priority": "high", "reason": "快速发展高校，报考热门"},
        {"name": "广州大学", "priority": "high", "reason": "省会城市综合大学"},
        {"name": "汕头大学", "priority": "medium", "reason": "粤东地区重点院校"},
        {"name": "广东外语外贸大学", "priority": "high", "reason": "外语外贸特色，录取量大"},
        {"name": "华南农业大学", "priority": "medium", "reason": "农业类重点院校"},
        {"name": "广州医科大学", "priority": "medium", "reason": "医学类院校"},
        {"name": "南方医科大学", "priority": "medium", "reason": "医学类重点院校"}
    ],
    "广东普通本科": [
        {"name": "东莞理工学院", "priority": "high", "reason": "东莞地区主要本科院校"},
        {"name": "佛山科学技术学院", "priority": "high", "reason": "佛山地区主要本科院校"},
        {"name": "五邑大学", "priority": "medium", "reason": "江门地区本科院校"},
        {"name": "惠州学院", "priority": "medium", "reason": "惠州地区本科院校"},
        {"name": "肇庆学院", "priority": "medium", "reason": "肇庆地区本科院校"},
        {"name": "广东石油化工学院", "priority": "medium", "reason": "化工特色院校"},
        {"name": "韶关学院", "priority": "low", "reason": "粤北地区本科院校"},
        {"name": "嘉应学院", "priority": "low", "reason": "梅州地区本科院校"},
        {"name": "韩山师范学院", "priority": "medium", "reason": "潮汕地区师范院校"},
        {"name": "岭南师范学院", "priority": "medium", "reason": "湛江地区师范院校"},
        {"name": "广东技术师范大学", "priority": "high", "reason": "技术师范特色院校"},
        {"name": "广东第二师范学院", "priority": "medium", "reason": "师范类院校"}
    ],
    "广东独立学院": [
        {"name": "珠海科技学院", "priority": "high", "reason": "独立学院排名靠前，报考热门"},
        {"name": "广州南方学院", "priority": "high", "reason": "广州地区热门独立学院"},
        {"name": "广州华商学院", "priority": "medium", "reason": "财经类独立学院"},
        {"name": "广东白云学院", "priority": "medium", "reason": "工科类独立学院"},
        {"name": "广东理工学院", "priority": "medium", "reason": "理工类独立学院"},
        {"name": "广州理工学院", "priority": "medium", "reason": "广州地区理工类独立学院"},
        {"name": "东莞城市学院", "priority": "medium", "reason": "东莞地区独立学院"},
        {"name": "广州新华学院", "priority": "medium", "reason": "广州地区独立学院"},
        {"name": "电子科技大学中山学院", "priority": "high", "reason": "名校举办独立学院"},
        {"name": "北京理工大学珠海学院", "priority": "high", "reason": "名校举办独立学院"}
    ],
    "广东民办本科": [
        {"name": "广东科技学院", "priority": "medium", "reason": "理工类民办本科"},
        {"name": "广州软件学院", "priority": "medium", "reason": "软件特色民办本科"},
        {"name": "广州工商学院", "priority": "medium", "reason": "工商类民办本科"},
        {"name": "广东东软学院", "priority": "medium", "reason": "IT类民办本科"},
        {"name": "广东培正学院", "priority": "low", "reason": "综合类民办本科"},
        {"name": "广州商学院", "priority": "medium", "reason": "财经类民办本科"}
    ],
    "广东高职专科": [
        {"name": "深圳职业技术大学", "priority": "high", "reason": "高职专科排名第一，升格为大学"},
        {"name": "广东轻工职业技术学院", "priority": "high", "reason": "轻工类高职专科龙头"},
        {"name": "广州番禺职业技术学院", "priority": "high", "reason": "广州地区高职专科"},
        {"name": "广东机电职业技术学院", "priority": "medium", "reason": "机电类高职专科"},
        {"name": "广东交通职业技术学院", "priority": "medium", "reason": "交通类高职专科"},
        {"name": "广东工贸职业技术学院", "priority": "medium", "reason": "工贸类高职专科"},
        {"name": "广东水利电力职业技术学院", "priority": "medium", "reason": "水利电力类高职专科"},
        {"name": "广东科学技术职业学院", "priority": "medium", "reason": "科技类高职专科"},
        {"name": "广东职业技术学院", "priority": "medium", "reason": "综合类高职专科"},
        {"name": "广东邮电职业技术学院", "priority": "medium", "reason": "邮电类高职专科"},
        {"name": "广东司法警官职业学院", "priority": "low", "reason": "司法类高职专科"},
        {"name": "广东体育职业技术学院", "priority": "low", "reason": "体育类高职专科"},
        {"name": "广东建设职业技术学院", "priority": "medium", "reason": "建设类高职专科"},
        {"name": "广东食品药品职业技术学院", "priority": "medium", "reason": "食品药品类高职专科"},
        {"name": "广东环境保护工程职业学院", "priority": "low", "reason": "环保类高职专科"},
        {"name": "广东松山职业技术学院", "priority": "low", "reason": "粤北地区高职专科"},
        {"name": "广东农工商职业技术学院", "priority": "medium", "reason": "农工商类高职专科"},
        {"name": "广东女子职业技术学院", "priority": "low", "reason": "女子类高职专科"}
    ]
}

def generate_missing_report():
    """生成缺失院校清单报告"""
    print("=== 生成缺失院校清单报告 ===")

    # 加载现有数据
    data_path = Path("../data/major_rank_data.json")
    if not data_path.exists():
        data_path = Path("backend/data/major_rank_data.json")

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("major_rank_data", [])

    # 提取现有院校名称
    existing_universities = set()
    for record in records:
        university = record.get("university_name", "")
        if university:
            existing_universities.add(university)

    print(f"现有院校总数：{len(existing_universities)}")

    # 分析各类型缺失院校
    missing_report = {}
    priority_summary = {"high": [], "medium": [], "low": []}

    for category, universities in GUANGDONG_UNIVERSITIES.items():
        missing = []
        covered = []

        for uni_info in universities:
            uni_name = uni_info["name"]
            if uni_name in existing_universities:
                covered.append(uni_info)
            else:
                missing.append(uni_info)

        missing_report[category] = {
            "total": len(universities),
            "covered": len(covered),
            "missing": len(missing),
            "covered_list": covered,
            "missing_list": missing
        }

        # 按优先级汇总
        for uni_info in missing:
            priority = uni_info["priority"]
            priority_summary[priority].append({
                "name": uni_info["name"],
                "category": category,
                "reason": uni_info["reason"]
            })

    # 生成文本报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = Path(f"missing_universities_report_{timestamp}.txt")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("广东本地院校数据覆盖情况报告\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"现有院校总数：{len(existing_universities)}\n\n")

        f.write("=" * 80 + "\n")
        f.write("一、各类院校覆盖情况\n")
        f.write("=" * 80 + "\n\n")

        for category, stats in missing_report.items():
            coverage_rate = stats["covered"] / stats["total"] * 100 if stats["total"] > 0 else 0

            status = "[OK]" if coverage_rate >= 80 else "[WARN]" if coverage_rate >= 50 else "[MISS]"

            f.write(f"{status} {category}\n")
            f.write(f"    覆盖率：{stats['covered']}/{stats['total']} ({coverage_rate:.1f}%)\n")

            if stats["covered_list"]:
                f.write(f"    已覆盖：{', '.join([u['name'] for u in stats['covered_list']])}\n")

            if stats["missing_list"]:
                f.write(f"    缺失院校：\n")
                for uni_info in stats["missing_list"]:
                    f.write(f"      - {uni_info['name']} (优先级：{uni_info['priority']}, {uni_info['reason']})\n")

            f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("二、补充数据优先级建议\n")
        f.write("=" * 80 + "\n\n")

        for priority in ["high", "medium", "low"]:
            priority_name = {"high": "高优先级", "medium": "中优先级", "low": "低优先级"}[priority]
            items = priority_summary[priority]

            f.write(f"{priority_name}（共{len(items)}所）：\n")

            for item in items:
                f.write(f"  1. {item['name']} ({item['category']})\n")
                f.write(f"     原因：{item['reason']}\n")

            f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("三、数据补充建议\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 高优先级院校（建议立即补充）：\n")
        f.write("   - 这些院校报考人数多，录取数据对用户价值大\n")
        f.write("   - 建议优先补充广东工业大学、深圳大学、广州大学等重点院校\n")
        f.write("   - 独立学院中的热门院校（如珠海科技学院）也应优先补充\n\n")

        f.write("2. 中优先级院校（建议逐步补充）：\n")
        f.write("   - 地方性本科院校，对当地考生重要\n")
        f.write("   - 具有专业特色的院校（如师范、理工类）\n")
        f.write("   - 建议按地区逐步补充\n\n")

        f.write("3. 低优先级院校（可延后补充）：\n")
        f.write("   - 报考人数相对较少\n")
        f.write("   - 可作为后续优化项目\n\n")

        f.write("4. 补充数据要求：\n")
        f.write("   - 专业名称\n")
        f.write("   - 最低录取分数\n")
        f.write("   - 最低录取位次\n")
        f.write("   - 专业组代码（如有）\n")
        f.write("   - 科类（物理/历史）\n")
        f.write("   - 选科要求\n\n")

        f.write("=" * 80 + "\n")
        f.write("四、数据来源建议\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. 官方渠道：\n")
        f.write("   - 广东省教育考试院官方公布数据\n")
        f.write("   - 各院校招生官网\n")
        f.write("   - 广东省2025年普通高校招生专业目录\n\n")

        f.write("2. 第三方渠道：\n")
        f.write("   - 阳光高考网\n")
        f.write("   - 夸克高考\n")
        f.write("   - 各大教育类APP\n\n")

        f.write("3. 数据收集优先级：\n")
        f.write("   - 优先收集2025年最新数据\n")
        f.write("   - 确保数据准确性\n")
        f.write("   - 交叉验证多个数据源\n\n")

    print(f"\n[OK] 缺失院校报告已保存到：{report_path}")

    # 显示汇总信息
    print(f"\n=== 缺失院校汇总 ===")
    total_universities = sum(len(unis) for unis in GUANGDONG_UNIVERSITIES.values())
    total_covered = sum(stats["covered"] for stats in missing_report.values())
    total_missing = sum(stats["missing"] for stats in missing_report.values())

    print(f"应补充院校总数：{total_universities}")
    print(f"已覆盖：{total_covered} ({total_covered/total_universities*100:.1f}%)")
    print(f"缺失：{total_missing} ({total_missing/total_universities*100:.1f}%)")

    print(f"\n优先级分布：")
    print(f"  高优先级：{len(priority_summary['high'])} 所")
    print(f"  中优先级：{len(priority_summary['medium'])} 所")
    print(f"  低优先级：{len(priority_summary['low'])} 所")

    return missing_report, priority_summary

if __name__ == "__main__":
    generate_missing_report()
