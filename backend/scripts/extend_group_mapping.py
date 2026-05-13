# -*- coding: utf-8 -*-
"""Extend group_code_mapping.json with 20 new universities"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data'

# Load existing group_code_mapping.json
with open(DATA_DIR / 'group_code_mapping.json', 'r', encoding='utf-8') as f:
    result = json.load(f)

print(f'Starting with {len(result)} entries')

# Load major_group_mapping.json
with open(DATA_DIR / 'major_group_mapping.json', 'r', encoding='utf-8') as f:
    mgm_data = json.load(f)
mgm = mgm_data.get('mappings', {})

# New universities and their core group mappings
new_unis_map = {
    '广东药科大学': {
        '201': {'majors': ['药学', '药物制剂', '临床药学', '药学(国际班)'], 'category': '物理'},
        '202': {'majors': ['中药学', '中药制药', '中药资源与开发'], 'category': '物理'},
        '203': {'majors': ['预防医学', '卫生检验与检疫'], 'category': '物理'},
        '204': {'majors': ['护理学', '康复治疗学'], 'category': '物理'},
        '205': {'majors': ['生物技术', '生物信息学', '海洋药学'], 'category': '物理'},
        '207': {'majors': ['食品质量与安全', '食品科学与工程'], 'category': '物理'},
        '208': {'majors': ['健康服务与管理', '公共事业管理'], 'category': '历史'},
        '215': {'majors': ['化妆品科学与技术', '化学工程与工艺'], 'category': '物理'},
    },
    '广东医科大学': {
        '201': {'majors': ['临床医学', '口腔医学'], 'category': '物理'},
        '202': {'majors': ['麻醉学', '医学影像学'], 'category': '物理'},
        '203': {'majors': ['药学', '中药学', '药物分析'], 'category': '物理'},
        '204': {'majors': ['护理学', '助产学'], 'category': '物理'},
        '205': {'majors': ['医学检验技术', '医学实验技术'], 'category': '物理'},
        '206': {'majors': ['预防医学', '卫生检验与检疫'], 'category': '物理'},
        '207': {'majors': ['生物医学工程', '生物技术'], 'category': '物理'},
        '208': {'majors': ['公共事业管理', '健康服务与管理'], 'category': '历史'},
    },
    '广州体育学院': {
        '201': {'majors': ['体育教育', '运动训练', '社会体育指导与管理'], 'category': '物理'},
        '202': {'majors': ['运动康复', '运动人体科学'], 'category': '物理'},
        '203': {'majors': ['休闲体育', '电子竞技运动与管理'], 'category': '历史'},
    },
    '广州美术学院': {
        '201': {'majors': ['美术学', '绘画', '雕塑', '中国画'], 'category': '物理'},
        '202': {'majors': ['视觉传达设计', '环境设计', '产品设计'], 'category': '物理'},
        '203': {'majors': ['数字媒体艺术', '动画', '摄影'], 'category': '历史'},
    },
    '星海音乐学院': {
        '201': {'majors': ['音乐表演', '音乐学', '作曲与作曲技术理论'], 'category': '物理'},
        '202': {'majors': ['舞蹈表演', '舞蹈学', '舞蹈编导'], 'category': '物理'},
        '203': {'majors': ['艺术管理', '录音艺术'], 'category': '历史'},
    },
    '广东海洋大学': {
        '201': {'majors': ['水产养殖学', '海洋渔业科学与技术', '水生动物医学'], 'category': '物理'},
        '202': {'majors': ['海洋科学', '海洋技术', '海洋资源与环境'], 'category': '物理'},
        '203': {'majors': ['计算机科学与技术', '软件工程', '物联网工程'], 'category': '物理'},
        '204': {'majors': ['机械设计制造及其自动化', '能源与动力工程'], 'category': '物理'},
        '205': {'majors': ['食品科学与工程', '食品质量与安全'], 'category': '物理'},
        '206': {'majors': ['会计学', '财务管理', '工商管理'], 'category': '历史'},
        '207': {'majors': ['法学', '政治学与行政学'], 'category': '历史'},
        '208': {'majors': ['英语', '日语', '汉语言文学'], 'category': '历史'},
    },
    '仲恺农业工程学院': {
        '201': {'majors': ['农学', '园艺', '植物保护'], 'category': '物理'},
        '202': {'majors': ['动物科学', '动物医学', '水产养殖学'], 'category': '物理'},
        '203': {'majors': ['计算机科学与技术', '电子信息工程'], 'category': '物理'},
        '204': {'majors': ['食品科学与工程', '食品质量与安全'], 'category': '物理'},
        '205': {'majors': ['园林', '环境设计', '城乡规划'], 'category': '物理'},
        '206': {'majors': ['会计学', '国际经济与贸易'], 'category': '历史'},
    },
    '广东金融学院': {
        '201': {'majors': ['金融学', '金融工程', '投资学'], 'category': '物理'},
        '202': {'majors': ['会计学', '审计学', '财务管理'], 'category': '物理'},
        '203': {'majors': ['计算机科学与技术', '数据科学与大数据技术'], 'category': '物理'},
        '204': {'majors': ['法学', '知识产权'], 'category': '历史'},
        '205': {'majors': ['国际经济与贸易', '商务英语'], 'category': '历史'},
        '206': {'majors': ['市场营销', '人力资源管理'], 'category': '历史'},
    },
    '广州航海学院': {
        '201': {'majors': ['航海技术', '轮机工程', '船舶电子电气工程'], 'category': '物理'},
        '202': {'majors': ['交通运输', '物流工程', '港口航道与海岸工程'], 'category': '物理'},
        '203': {'majors': ['计算机科学与技术', '通信工程'], 'category': '物理'},
    },
    '深圳技术大学': {
        '201': {'majors': ['计算机科学与技术', '软件工程', '物联网工程'], 'category': '物理'},
        '202': {'majors': ['机械设计制造及其自动化', '车辆工程'], 'category': '物理'},
        '203': {'majors': ['新能源科学与工程', '光电信息科学与工程'], 'category': '物理'},
        '204': {'majors': ['生物医学工程', '医疗器械工程'], 'category': '物理'},
        '205': {'majors': ['城市轨道交通运营管理', '交通设备与控制'], 'category': '物理'},
    },
    '广东石油化工学院': {
        '201': {'majors': ['化学工程与工艺', '应用化学', '高分子材料与工程'], 'category': '物理'},
        '202': {'majors': ['石油工程', '油气储运工程'], 'category': '物理'},
        '203': {'majors': ['机械设计制造及其自动化', '过程装备与控制工程'], 'category': '物理'},
        '204': {'majors': ['计算机科学与技术', '电子信息工程'], 'category': '物理'},
        '205': {'majors': ['环境工程', '安全工程'], 'category': '物理'},
        '206': {'majors': ['会计学', '市场营销'], 'category': '历史'},
    },
    '韶关学院': {
        '201': {'majors': ['计算机科学与技术', '软件工程', '通信工程'], 'category': '物理'},
        '202': {'majors': ['机械设计制造及其自动化', '汽车服务工程'], 'category': '物理'},
        '203': {'majors': ['汉语言文学', '新闻学'], 'category': '历史'},
        '204': {'majors': ['数学与应用数学', '物理学'], 'category': '物理'},
        '205': {'majors': ['化学', '应用化学', '食品科学与工程'], 'category': '物理'},
        '206': {'majors': ['小学教育', '学前教育'], 'category': '历史'},
    },
    '嘉应学院': {
        '201': {'majors': ['汉语言文学', '小学教育'], 'category': '历史'},
        '202': {'majors': ['计算机科学与技术', '数学与应用数学'], 'category': '物理'},
        '203': {'majors': ['英语', '商务英语'], 'category': '历史'},
        '204': {'majors': ['财务管理', '市场营销'], 'category': '历史'},
    },
    '韩山师范学院': {
        '201': {'majors': ['汉语言文学', '历史学', '思想政治教育'], 'category': '历史'},
        '202': {'majors': ['数学与应用数学', '物理学', '化学'], 'category': '物理'},
        '203': {'majors': ['英语', '日语'], 'category': '历史'},
        '204': {'majors': ['计算机科学与技术', '电子信息工程'], 'category': '物理'},
    },
    '岭南师范学院': {
        '201': {'majors': ['小学教育', '学前教育', '心理学'], 'category': '历史'},
        '202': {'majors': ['数学与应用数学', '物理学'], 'category': '物理'},
        '203': {'majors': ['汉语言文学', '英语'], 'category': '历史'},
        '204': {'majors': ['计算机科学与技术', '电子信息工程'], 'category': '物理'},
    },
    '广东科技学院': {
        '201': {'majors': ['计算机科学与技术', '软件工程', '数据科学与大数据技术'], 'category': '物理'},
        '202': {'majors': ['电子信息工程', '机械设计制造及其自动化'], 'category': '物理'},
        '203': {'majors': ['英语', '商务英语', '日语'], 'category': '历史'},
        '204': {'majors': ['会计学', '财务管理', '市场营销'], 'category': '历史'},
        '205': {'majors': ['工商管理', '电子商务', '物流管理'], 'category': '历史'},
        '206': {'majors': ['视觉传达设计', '环境设计'], 'category': '物理'},
    },
    '广东理工学院': {
        '201': {'majors': ['计算机科学与技术', '软件工程'], 'category': '物理'},
        '202': {'majors': ['电气工程及其自动化', '机械电子工程'], 'category': '物理'},
        '203': {'majors': ['土木工程', '工程管理', '工程造价'], 'category': '物理'},
        '204': {'majors': ['会计学', '财务管理'], 'category': '历史'},
        '205': {'majors': ['英语', '商务英语'], 'category': '历史'},
        '206': {'majors': ['国际经济与贸易', '市场营销'], 'category': '历史'},
    },
    '广州理工学院': {
        '201': {'majors': ['计算机科学与技术', '软件工程', '数据科学与大数据技术'], 'category': '物理'},
        '202': {'majors': ['电气工程及其自动化', '电子信息工程'], 'category': '物理'},
        '203': {'majors': ['土木工程', '工程造价'], 'category': '物理'},
        '204': {'majors': ['会计学', '财务管理', '市场营销'], 'category': '历史'},
        '205': {'majors': ['英语', '日语'], 'category': '历史'},
    },
    '广东东软学院': {
        '201': {'majors': ['计算机科学与技术', '软件工程', '网络工程'], 'category': '物理'},
        '202': {'majors': ['数字媒体技术', '电子信息工程'], 'category': '物理'},
        '203': {'majors': ['电子商务', '工商管理', '市场营销'], 'category': '历史'},
    },
    '广州软件学院': {
        '201': {'majors': ['软件工程', '网络工程', '数据科学与大数据技术'], 'category': '物理'},
        '202': {'majors': ['数字媒体技术', '动画'], 'category': '物理'},
        '203': {'majors': ['电子商务', '物流管理', '市场营销'], 'category': '历史'},
    },
}

# Step 1: Add existing major_group_mapping entries for new universities
added_from_mgm = 0
for key, info in mgm.items():
    for uni in new_unis_map:
        if key.startswith(uni + '_'):
            code = key[len(uni)+1:].replace('\n', '').strip()
            if not code:
                continue
            mapped_key = f'{uni}_{code}'
            if mapped_key not in result:
                result[mapped_key] = {
                    'group_code': code,
                    'majors': info.get('majors', []),
                    'category': info.get('category', '物理')
                }
                added_from_mgm += 1
            break

print(f'Added {added_from_mgm} from major_group_mapping.json')

# Step 2: Add new curated mappings
added_new = 0
for uni, groups in new_unis_map.items():
    for code, info in groups.items():
        key = f'{uni}_{code}'
        if key not in result:
            result[key] = {
                'group_code': code,
                'majors': info['majors'],
                'category': info['category']
            }
            added_new += 1

print(f'Added {added_new} new curated entries')

# Step 3: Count total
uni_set = set()
for k in result:
    if '_' in k:
        uni_set.add(k.rsplit('_', 1)[0])

print(f'Total entries: {len(result)}')
print(f'Universities covered: {len(uni_set)}')

# Save
with open(DATA_DIR / 'group_code_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('Saved to group_code_mapping.json')
