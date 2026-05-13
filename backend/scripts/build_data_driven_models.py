# -*- coding: utf-8 -*-
"""
构建数据驱动模型：位次段-院校热度矩阵、城市吸引力指数、专业热度趋势

基于 18,325 条 2023-2025 全批次投档数据，输出 3 个 JSON 模型文件。

用法: python scripts/build_data_driven_models.py
"""
import json, os, sys, io, math
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = Path(__file__).parent.parent / 'data'
MAIN_FILE = DATA_DIR / 'major_rank_data.json'
UNI_DETAILS_FILE = DATA_DIR / 'university_details.json'
OUT_HOTNESS = DATA_DIR / 'rank_hotness_matrix.json'
OUT_CITY = DATA_DIR / 'city_attraction_index.json'
OUT_TREND = DATA_DIR / 'major_trend_analysis.json'

# ============================================================
# 0. 高校名称→所在省映射（985/211/省属重点 + heuristics）
# ============================================================
UNI_PROVINCE_MAP = {
    # ---- 北京 ----
    '北京大学': '北京', '清华大学': '北京', '中国人民大学': '北京',
    '北京师范大学': '北京', '北京航空航天大学': '北京', '北京理工大学': '北京',
    '中国农业大学': '北京', '中央民族大学': '北京',
    '北京邮电大学': '北京', '北京交通大学': '北京', '北京科技大学': '北京',
    '北京化工大学': '北京', '北京工业大学': '北京', '北京林业大学': '北京',
    '北京中医药大学': '北京', '北京外国语大学': '北京', '中国传媒大学': '北京',
    '中央财经大学': '北京', '对外经济贸易大学': '北京', '中国政法大学': '北京',
    '华北电力大学': '北京', '中国矿业大学(北京)': '北京', '中国石油大学(北京)': '北京',
    '中国地质大学(北京)': '北京', '北京体育大学': '北京', '中央音乐学院': '北京',
    '中央戏剧学院': '北京', '中央美术学院': '北京', '外交学院': '北京',
    '中国人民公安大学': '北京', '国际关系学院': '北京', '北京协和医学院': '北京',
    '中国音乐学院': '北京', '中国科学院大学': '北京', '北京语言大学': '北京',
    '首都师范大学': '北京', '首都医科大学': '北京', '首都经济贸易大学': '北京',
    '北京工商大学': '北京', '北京第二外国语学院': '北京', '北京建筑大学': '北京',
    '北京信息科技大学': '北京', '北京联合大学': '北京', '北方工业大学': '北京',
    '北京印刷学院': '北京', '北京石油化工学院': '北京', '北京农学院': '北京',
    '北京物资学院': '北京', '北京服装学院': '北京', '中国劳动关系学院': '北京',
    '中华女子学院': '北京', '中国消防救援学院': '北京', '北京城市学院': '北京',
    '中国社会科学院大学': '北京', '北京体育大学(中外合作办学)': '北京',
    # ---- 上海 ----
    '复旦大学': '上海', '上海交通大学': '上海', '同济大学': '上海',
    '华东师范大学': '上海', '上海财经大学': '上海', '上海外国语大学': '上海',
    '华东理工大学': '上海', '东华大学': '上海', '上海大学': '上海',
    '华东政法大学': '上海', '上海理工大学': '上海', '上海海事大学': '上海',
    '上海海洋大学': '上海', '上海中医药大学': '上海', '上海师范大学': '上海',
    '上海对外经贸大学': '上海', '上海电力大学': '上海', '上海应用技术大学': '上海',
    '上海工程技术大学': '上海', '上海立信会计金融学院': '上海', '上海电机学院': '上海',
    '上海商学院': '上海', '上海政法学院': '上海', '上海海关学院': '上海',
    '上海健康医学院': '上海', '上海第二工业大学': '上海', '上海科技大学': '上海',
    # ---- 江苏 ----
    '南京大学': '江苏', '东南大学': '江苏', '南京航空航天大学': '江苏',
    '南京理工大学': '江苏', '河海大学': '江苏', '苏州大学': '江苏',
    '中国药科大学': '江苏', '江南大学': '江苏', '南京农业大学': '江苏',
    '南京师范大学': '江苏', '中国矿业大学': '江苏', '南京信息工程大学': '江苏',
    '南京工业大学': '江苏', '南京邮电大学': '江苏', '南京林业大学': '江苏',
    '江苏大学': '江苏', '扬州大学': '江苏', '南京医科大学': '江苏',
    '南京中医药大学': '江苏', '南京财经大学': '江苏', '南京审计大学': '江苏',
    '南京艺术学院': '江苏', '常州大学': '江苏', '南通大学': '江苏',
    '江苏科技大学': '江苏', '徐州医科大学': '江苏', '江苏师范大学': '江苏',
    '苏州科技大学': '江苏', '盐城工学院': '江苏', '淮阴工学院': '江苏',
    # ---- 浙江 ----
    '浙江大学': '浙江', '浙江工业大学': '浙江', '宁波大学': '浙江',
    '浙江师范大学': '浙江', '杭州电子科技大学': '浙江', '浙江工商大学': '浙江',
    '浙江理工大学': '浙江', '中国美术学院': '浙江', '温州医科大学': '浙江',
    '浙江财经大学': '浙江', '浙江海洋大学': '浙江', '中国计量大学': '浙江',
    '浙江农林大学': '浙江', '杭州师范大学': '浙江', '温州大学': '浙江',
    '浙江传媒学院': '浙江', '浙江外国语学院': '浙江', '湖州师范学院': '浙江',
    '绍兴文理学院': '浙江', '嘉兴大学': '浙江', '台州学院': '浙江',
    # ---- 安徽 ----
    '中国科学技术大学': '安徽', '合肥工业大学': '安徽', '安徽大学': '安徽',
    '安徽师范大学': '安徽', '安徽医科大学': '安徽', '安徽农业大学': '安徽',
    '安徽工业大学': '安徽', '安徽理工大学': '安徽', '安徽财经大学': '安徽',
    '安徽建筑大学': '安徽', '安徽工程大学': '安徽', '皖南医学院': '安徽',
    # ---- 湖北 ----
    '武汉大学': '湖北', '华中科技大学': '湖北', '武汉理工大学': '湖北',
    '华中师范大学': '湖北', '华中农业大学': '湖北', '中南财经政法大学': '湖北',
    '中国地质大学(武汉)': '湖北', '湖北大学': '湖北', '武汉科技大学': '湖北',
    '中南民族大学': '湖北', '湖北工业大学': '湖北', '武汉工程大学': '湖北',
    '武汉纺织大学': '湖北', '长江大学': '湖北', '三峡大学': '湖北',
    '江汉大学': '湖北', '湖北经济学院': '湖北', '湖北中医药大学': '湖北',
    '武汉轻工大学': '湖北',
    # ---- 湖南 ----
    '湖南大学': '湖南', '中南大学': '湖南', '国防科技大学': '湖南',
    '湖南师范大学': '湖南', '湘潭大学': '湖南', '长沙理工大学': '湖南',
    '湖南农业大学': '湖南', '中南林业科技大学': '湖南', '南华大学': '湖南',
    '湖南科技大学': '湖南', '湖南工业大学': '湖南', '吉首大学': '湖南',
    '湖南工商大学': '湖南', '湖南理工学院': '湖南', '湖南中医药大学': '湖南',
    # ---- 广东 ----
    '中山大学': '广东', '华南理工大学': '广东', '暨南大学': '广东',
    '华南师范大学': '广东', '深圳大学': '广东', '南方医科大学': '广东',
    '广东外语外贸大学': '广东', '广东工业大学': '广东', '广州大学': '广东',
    '广州医科大学': '广东', '华南农业大学': '广东', '广东财经大学': '广东',
    '广州中医药大学': '广东', '汕头大学': '广东', '东莞理工学院': '广东',
    '北京师范大学-香港浸会大学联合国际学院': '广东', '香港中文大学(深圳)': '广东',
    '广东海洋大学': '广东', '广东技术师范大学': '广东', '广东药科大学': '广东',
    '广东医科大学': '广东', '仲恺农业工程学院': '广东', '广东石油化工学院': '广东',
    '五邑大学': '广东', '佛山科学技术学院': '广东', '嘉应学院': '广东',
    '岭南师范学院': '广东', '惠州学院': '广东', '肇庆学院': '广东',
    '韶关学院': '广东', '韩山师范学院': '广东', '广东金融学院': '广东',
    '北京理工大学珠海学院': '广东', '广州航海学院': '广东', '深圳技术大学': '广东',
    '广东第二师范学院': '广东', '电子科技大学中山学院': '广东',
    '华南农业大学珠江学院': '广东', '广州新华学院': '广东', '广州南方学院': '广东',
    '广州商学院': '广东', '珠海科技学院': '广东', '广东科技学院': '广东',
    '广州城市理工学院': '广东', '东莞城市学院': '广东', '广东白云学院': '广东',
    '广州理工学院': '广东', '广州工商学院': '广东', '广州软件学院': '广东',
    '广东理工学院': '广东', '广州华商学院': '广东', '广东东软学院': '广东',
    '广东工商职业技术大学': '广东', '广东外语外贸大学南国商学院': '广东',
    '广州应用科技学院': '广东', '湛江科技学院': '广东', '广州华立学院': '广东',
    '广东培正学院': '广东', '广州理工学院(筹)': '广东', '广东轻工职业技术大学': '广东',
    '广州科技职业技术大学': '广东', '深圳职业技术大学': '广东',
    '广东水利电力职业技术学院': '广东', '深圳信息职业技术学院': '广东',
    '广东农工商职业技术学院': '广东', '广东交通职业技术学院': '广东',
    '广东科贸职业学院': '广东', '广州番禺职业技术学院': '广东',
    '广东工程职业技术学院': '广东', '广东邮电职业技术学院': '广东',
    '广东建设职业技术学院': '广东', '广东机电职业技术学院': '广东',
    '广东食品药品职业学院': '广东', '广东司法警官职业学院': '广东',
    '广东职业技术学院': '广东', '广东文艺职业学院': '广东',
    '广东行政职业学院': '广东', '广东女子职业技术学院': '广东',
    '广州民航职业技术学院': '广东', '广东松山职业技术学院': '广东',
    '广州铁路职业技术学院': '广东', '广州科技贸易职业学院': '广东',
    '广东工贸职业技术学院': '广东', '广东南华工商职业学院': '广东',
    '广东岭南职业技术学院': '广东', '广州城建职业学院': '广东',
    '广州涉外经济职业技术学院': '广东', '广州华夏职业学院': '广东',
    '广州南洋理工职业学院': '广东', '广东环境保护工程职业学院': '广东',
    '广东文理职业学院': '广东', '广东酒店管理职业技术学院': '广东',
    '广东亚视演艺职业学院': '广东', '广东新安职业技术学院': '广东',
    '广东肇庆航空职业学院': '广东', '潮汕职业技术学院': '广东',
    '珠海艺术职业学院': '广东', '私立华联学院': '广东',
    '惠州经济职业技术学院': '广东', '广东碧桂园职业学院': '广东',
    '广东信息工程职业学院': '广东', '广东创新科技职业学院': '广东',
    '广州现代信息工程职业技术学院': '广东', '广州华南商贸职业学院': '广东',
    '广州珠江职业技术学院': '广东', '广州松田职业学院': '广东',
    '广东华南职业技术学院': '广东', '广州东华职业学院': '广东',
    '广州华立科技职业学院': '广东', '广东南方职业学院': '广东',
    '广东茂名健康职业学院': '广东', '广东茂名幼儿师范专科学校': '广东',
    '广东茂名农林科技职业学院': '广东', '江门职业技术学院': '广东',
    '河源职业技术学院': '广东', '汕头职业技术学院': '广东',
    '汕尾职业技术学院': '广东', '揭阳职业技术学院': '广东',
    '阳江职业技术学院': '广东', '罗定职业技术学院': '广东',
    '清远职业技术学院': '广东', '肇庆医学高等专科学校': '广东',
    '顺德职业技术学院': '广东', '佛山职业技术学院': '广东',
    '中山职业技术学院': '广东', '中山火炬职业技术学院': '广东',
    '东莞职业技术学院': '广东', '珠海城市职业技术学院': '广东',
    '惠州卫生职业技术学院': '广东', '广东江门中医药职业学院': '广东',
    '广东江门幼儿师范高等专科学校': '广东', '湛江幼儿师范专科学校': '广东',
    '广东生态工程职业学院': '广东', '广东体育职业技术学院': '广东',
    '广州体育职业技术学院': '广东', '广东舞蹈戏剧职业学院': '广东',
    '广东财贸职业学院': '广东', '广州工程技术职业学院': '广东',
    '广州城市职业学院': '广东', '广州卫生职业技术学院': '广东',
    '深圳城市职业学院': '广东', '南方科技大学': '广东',
    '哈尔滨工业大学(深圳)': '广东', '北京师范大学(珠海校区)': '广东',
    '北京师范大学(珠海)': '广东', '北京师范大学珠海分校': '广东',
    '遵义医科大学(珠海校区)': '广东',
    # ---- 广西 ----
    '广西大学': '广西', '广西师范大学': '广西', '广西医科大学': '广西',
    '桂林电子科技大学': '广西', '桂林理工大学': '广西', '广西民族大学': '广西',
    '广西中医药大学': '广西', '广西科技大学': '广西', '南宁师范大学': '广西',
    '广西艺术学院': '广西', '北部湾大学': '广西', '广西财经学院': '广西',
    '广西警察学院': '广西', '河池学院': '广西', '贺州学院': '广西',
    # ---- 海南 ----
    '海南大学': '海南', '海南师范大学': '海南', '海南医科大学': '海南',
    '海南热带海洋学院': '海南', '琼台师范学院': '海南',
    # ---- 福建 ----
    '厦门大学': '福建', '福州大学': '福建', '福建师范大学': '福建',
    '华侨大学': '福建', '福建农林大学': '福建', '福建医科大学': '福建',
    '集美大学': '福建', '厦门理工学院': '福建', '闽南师范大学': '福建',
    '福建中医药大学': '福建', '仰恩大学': '福建', '闽江学院': '福建',
    '泉州师范学院': '福建', '莆田学院': '福建', '龙岩学院': '福建',
    '三明学院': '福建', '武夷学院': '福建', '福建理工大学': '福建',
    # ---- 江西 ----
    '南昌大学': '江西', '江西师范大学': '江西', '江西财经大学': '江西',
    '江西农业大学': '江西', '华东交通大学': '江西', '南昌航空大学': '江西',
    '东华理工大学': '江西', '江西理工大学': '江西', '景德镇陶瓷大学': '江西',
    '江西中医药大学': '江西', '赣南医科大学': '江西', '赣南师范大学': '江西',
    '江西科技师范大学': '江西', '宜春学院': '江西', '井冈山大学': '江西',
    '九江学院': '江西', '南昌工程学院': '江西', '新余学院': '江西',
    # ---- 山东 ----
    '山东大学': '山东', '中国海洋大学': '山东', '中国石油大学(华东)': '山东',
    '山东师范大学': '山东', '青岛大学': '山东', '山东科技大学': '山东',
    '山东农业大学': '山东', '青岛科技大学': '山东', '青岛理工大学': '山东',
    '济南大学': '山东', '山东财经大学': '山东', '曲阜师范大学': '山东',
    '烟台大学': '山东', '聊城大学': '山东', '鲁东大学': '山东',
    '山东理工大学': '山东', '山东建筑大学': '山东', '山东第一医科大学': '山东',
    '山东中医药大学': '山东', '潍坊医学院': '山东', '滨州医学院': '山东',
    '潍坊学院': '山东', '泰山学院': '山东', '菏泽学院': '山东',
    '枣庄学院': '山东', '德州学院': '山东', '临沂大学': '山东',
    # ---- 河南 ----
    '郑州大学': '河南', '河南大学': '河南', '河南师范大学': '河南',
    '河南科技大学': '河南', '河南理工大学': '河南', '河南工业大学': '河南',
    '河南农业大学': '河南', '河南财经政法大学': '河南', '郑州轻工业大学': '河南',
    '华北水利水电大学': '河南', '中原工学院': '河南', '南阳理工学院': '河南',
    '新乡医学院': '河南', '信阳师范大学': '河南', '河南中医药大学': '河南',
    '河南科技学院': '河南', '洛阳师范学院': '河南', '安阳师范学院': '河南',
    '商丘师范学院': '河南', '平顶山学院': '河南', '黄淮学院': '河南',
    '许昌学院': '河南', '南阳师范学院': '河南', '新乡学院': '河南',
    '河南工程学院': '河南', '河南城建学院': '河南', '周口师范学院': '河南',
    # ---- 河北 ----
    '河北工业大学': '河北', '燕山大学': '河北', '河北大学': '河北',
    '河北师范大学': '河北', '河北医科大学': '河北', '河北农业大学': '河北',
    '河北科技大学': '河北', '华北理工大学': '河北', '石家庄铁道大学': '河北',
    '河北经贸大学': '河北', '河北工程大学': '河北', '河北地质大学': '河北',
    '河北科技师范学院': '河北', '承德医学院': '河北', '北华航天工业学院': '河北',
    '廊坊师范学院': '河北', '唐山师范学院': '河北', '保定学院': '河北',
    '衡水学院': '河北', '邯郸学院': '河北', '邢台学院': '河北',
    # ---- 山西 ----
    '太原理工大学': '山西', '山西大学': '山西', '中北大学': '山西',
    '山西医科大学': '山西', '山西财经大学': '山西', '山西农业大学': '山西',
    '山西师范大学': '山西', '太原科技大学': '山西', '山西大同大学': '山西',
    '长治医学院': '山西', '山西中医药大学': '山西', '太原师范学院': '山西',
    '运城学院': '山西', '忻州师范学院': '山西', '吕梁学院': '山西',
    # ---- 天津 ----
    '南开大学': '天津', '天津大学': '天津', '天津医科大学': '天津',
    '天津师范大学': '天津', '天津工业大学': '天津', '天津科技大学': '天津',
    '天津理工大学': '天津', '天津财经大学': '天津', '天津中医药大学': '天津',
    '天津外国语大学': '天津', '天津商业大学': '天津', '天津城建大学': '天津',
    '中国民航大学': '天津', '天津农学院': '天津', '天津体育学院': '天津',
    # ---- 辽宁 ----
    '大连理工大学': '辽宁', '东北大学': '辽宁', '大连海事大学': '辽宁',
    '辽宁大学': '辽宁', '中国医科大学': '辽宁', '东北财经大学': '辽宁',
    '大连医科大学': '辽宁', '沈阳药科大学': '辽宁', '沈阳农业大学': '辽宁',
    '辽宁师范大学': '辽宁', '大连大学': '辽宁', '沈阳工业大学': '辽宁',
    '沈阳航空航天大学': '辽宁', '沈阳建筑大学': '辽宁', '大连交通大学': '辽宁',
    '辽宁科技大学': '辽宁', '大连工业大学': '辽宁', '沈阳化工大学': '辽宁',
    '渤海大学': '辽宁', '锦州医科大学': '辽宁', '沈阳师范大学': '辽宁',
    # ---- 吉林 ----
    '吉林大学': '吉林', '东北师范大学': '吉林', '延边大学': '吉林',
    '东北电力大学': '吉林', '长春理工大学': '吉林', '吉林农业大学': '吉林',
    '长春工业大学': '吉林', '北华大学': '吉林', '吉林师范大学': '吉林',
    '吉林财经大学': '吉林', '吉林化工学院': '吉林',
    # ---- 黑龙江 ----
    '哈尔滨工业大学': '黑龙江', '哈尔滨工程大学': '黑龙江', '东北林业大学': '黑龙江',
    '东北农业大学': '黑龙江', '黑龙江大学': '黑龙江', '哈尔滨理工大学': '黑龙江',
    '哈尔滨医科大学': '黑龙江', '哈尔滨师范大学': '黑龙江', '黑龙江中医药大学': '黑龙江',
    '齐齐哈尔大学': '黑龙江', '黑龙江八一农垦大学': '黑龙江', '佳木斯大学': '黑龙江',
    '哈尔滨商业大学': '黑龙江',
    # ---- 重庆 ----
    '重庆大学': '重庆', '西南大学': '重庆', '西南政法大学': '重庆',
    '重庆医科大学': '重庆', '重庆邮电大学': '重庆', '重庆交通大学': '重庆',
    '重庆工商大学': '重庆', '四川外国语大学': '重庆', '重庆师范大学': '重庆',
    '重庆理工大学': '重庆', '四川美术学院': '重庆', '重庆科技大学': '重庆',
    '重庆三峡学院': '重庆', '长江师范学院': '重庆', '重庆文理学院': '重庆',
    # ---- 四川 ----
    '四川大学': '四川', '电子科技大学': '四川', '西南交通大学': '四川',
    '西南财经大学': '四川', '四川农业大学': '四川', '西南石油大学': '四川',
    '成都理工大学': '四川', '西南科技大学': '四川', '西华大学': '四川',
    '成都信息工程大学': '四川', '四川师范大学': '四川', '成都大学': '四川',
    '西华师范大学': '四川', '西南医科大学': '四川', '川北医学院': '四川',
    '成都中医药大学': '四川', '成都体育学院': '四川', '四川轻化工大学': '四川',
    '西南民族大学': '四川', '中国民用航空飞行学院': '四川',
    # ---- 陕西 ----
    '西安交通大学': '陕西', '西北工业大学': '陕西', '西北大学': '陕西',
    '西安电子科技大学': '陕西', '陕西师范大学': '陕西', '长安大学': '陕西',
    '西北农林科技大学': '陕西', '西安建筑科技大学': '陕西', '西安理工大学': '陕西',
    '陕西科技大学': '陕西', '西安科技大学': '陕西', '西安石油大学': '陕西',
    '西安工业大学': '陕西', '西安工程大学': '陕西', '西安外国语大学': '陕西',
    '西北政法大学': '陕西', '西安邮电大学': '陕西', '延安大学': '陕西',
    # ---- 甘肃 ----
    '兰州大学': '甘肃', '西北师范大学': '甘肃', '兰州交通大学': '甘肃',
    '兰州理工大学': '甘肃', '甘肃农业大学': '甘肃', '西北民族大学': '甘肃',
    '甘肃政法大学': '甘肃', '兰州财经大学': '甘肃', '天水师范学院': '甘肃',
    # ---- 贵州 ----
    '贵州大学': '贵州', '贵州师范大学': '贵州', '贵州医科大学': '贵州',
    '贵州财经大学': '贵州', '贵州民族大学': '贵州', '贵州中医药大学': '贵州',
    '遵义医科大学': '贵州', '贵阳学院': '贵州', '黔南民族师范学院': '贵州',
    '贵州理工学院': '贵州',
    # ---- 云南 ----
    '云南大学': '云南', '昆明理工大学': '云南', '云南师范大学': '云南',
    '云南农业大学': '云南', '云南财经大学': '云南', '昆明医科大学': '云南',
    '西南林业大学': '云南', '云南民族大学': '云南', '大理大学': '云南',
    '云南艺术学院': '云南', '曲靖师范学院': '云南', '红河学院': '云南',
    # ---- 宁夏 ----
    '宁夏大学': '宁夏', '宁夏医科大学': '宁夏', '北方民族大学': '宁夏',
    # ---- 青海 ----
    '青海大学': '青海', '青海师范大学': '青海', '青海民族大学': '青海',
    # ---- 新疆 ----
    '新疆大学': '新疆', '石河子大学': '新疆', '新疆师范大学': '新疆',
    '新疆医科大学': '新疆', '新疆农业大学': '新疆', '塔里木大学': '新疆',
    '喀什大学': '新疆', '昌吉学院': '新疆',
    # ---- 西藏 ----
    '西藏大学': '西藏', '西藏民族大学': '西藏', '西藏藏医药大学': '西藏',
    # ---- 内蒙古 ----
    '内蒙古大学': '内蒙古', '内蒙古师范大学': '内蒙古', '内蒙古工业大学': '内蒙古',
    '内蒙古科技大学': '内蒙古', '内蒙古农业大学': '内蒙古', '内蒙古医科大学': '内蒙古',
    '内蒙古民族大学': '内蒙古', '内蒙古财经大学': '内蒙古',
    # ---- 香港/澳门 ----
    '香港大学': '香港', '香港中文大学': '香港', '香港科技大学': '香港',
    '香港理工大学': '香港', '香港城市大学': '香港', '香港浸会大学': '香港',
    '澳门大学': '澳门', '澳门科技大学': '澳门',
    # ---- 中外合作/独立学院 ----
    '西交利物浦大学': '江苏', '宁波诺丁汉大学': '浙江', '温州肯恩大学': '浙江',
    '昆山杜克大学': '江苏', '广东以色列理工学院': '广东',
    '上海纽约大学': '上海', '深圳北理莫斯科大学': '广东',
}

# 已知的高=位次(难考)关键词 --> 能推断省份的
# 这里主要通过名称中的地名推断
PROVINCE_KEYWORDS = {
    '北京': ['北京', '首都', '中国', '中华', '中央', '外交', '清华', '北大'],
    '上海': ['上海', '同济', '复旦', '华东', '东华'],
    '广东': ['广东', '广州', '深圳', '华南', '暨南', '岭南', '南方', '汕头',
            '东莞', '佛山', '珠海', '惠州', '中山', '肇庆', '韶关', '湛江',
            '嘉应', '韩山', '五邑', '仲恺', '番禺', '顺德', '河源', '江门',
            '清远', '阳江', '揭阳', '汕尾', '罗定', '潮汕', '茂名'],
    '江苏': ['江苏', '南京', '苏州', '江南', '河海', '中国药科', '东南',
            '扬州', '常州', '南通', '徐州', '盐城', '淮阴'],
    '浙江': ['浙江', '杭州', '宁波', '温州', '湖州', '绍兴', '嘉兴', '台州',
            '中国美术', '中国计量'],
    '湖北': ['湖北', '武汉', '华中', '中南', '三峡', '长江大学', '江汉'],
    '湖南': ['湖南', '中南大学', '长沙', '湘潭', '南华', '吉首', '衡阳'],
    '四川': ['四川', '成都', '西南交通', '西南财经', '电子科技', '西南石油',
            '西华', '川北'],
    '重庆': ['重庆', '西南政法', '西南大学', '四川外国语', '四川美术'],
    '山东': ['山东', '济南', '青岛', '烟台', '鲁东', '曲阜', '聊城',
            '潍坊', '滨州', '菏泽', '枣庄', '德州', '临沂', '泰山', '中国海洋',
            '中国石油(华东)'],
    '福建': ['福建', '厦门', '福州', '华侨', '泉州', '闽南', '闽江',
            '龙岩', '莆田', '三明', '武夷'],
    '安徽': ['安徽', '合肥', '中国科学技术', '皖南'],
    '江西': ['江西', '南昌', '赣南', '井冈山', '九江', '宜春', '新余',
            '景德镇', '华东交通', '东华理工'],
    '河南': ['河南', '郑州', '华北水利', '中原', '南阳', '洛阳',
            '安阳', '商丘', '新乡', '平顶山', '信阳', '许昌', '周口'],
    '河北': ['河北', '燕山', '石家庄', '华北理工', '廊坊', '唐山',
            '保定', '衡水', '邯郸', '邢台', '承德', '北华航天'],
    '天津': ['天津', '南开', '中国民航'],
    '辽宁': ['辽宁', '大连', '沈阳', '东北大学', '东北财经', '渤海', '锦州'],
    '吉林': ['吉林', '长春', '延边', '东北师范', '东北电力', '北华大学'],
    '黑龙江': ['黑龙江', '哈尔滨', '齐齐哈尔', '佳木斯', '东北林业', '东北农业'],
    '陕西': ['陕西', '西安', '西北', '长安', '延安'],
    '甘肃': ['甘肃', '兰州', '天水'],
    '贵州': ['贵州', '贵阳', '遵义', '黔南'],
    '云南': ['云南', '昆明', '大理', '曲靖', '红河'],
    '广西': ['广西', '桂林', '南宁', '北部湾', '河池', '贺州'],
    '海南': ['海南', '琼台'],
    '新疆': ['新疆', '石河子', '塔里木', '喀什', '昌吉'],
    '西藏': ['西藏'],
    '宁夏': ['宁夏'],
    '青海': ['青海'],
    '内蒙古': ['内蒙古'],
    '山西': ['山西', '太原', '大同', '运城', '忻州', '吕梁', '长治', '中北大学'],
}

# 按全名匹配优先级排序 (长关键词优先)
SORTED_PROVINCE_ITEMS = sorted(
    [(k, v) for k, v in PROVINCE_KEYWORDS.items()],
    key=lambda x: -len(x[0])
)


def infer_province(uname):
    """推断高校所在省份"""
    if uname in UNI_PROVINCE_MAP:
        return UNI_PROVINCE_MAP[uname]
    # 从 university_details 查
    details_uni = _UNI_DETAILS_MAP.get(uname)
    if details_uni:
        p = details_uni.get('basic_info', {}).get('province', '')
        if p and p != '':
            return p
    # 关键词推断
    for pname, keywords in SORTED_PROVINCE_ITEMS:
        for kw in keywords:
            if kw in uname:
                return pname
    # 特殊处理带括号的名称
    base = uname.split('(')[0]
    if base != uname and base in UNI_PROVINCE_MAP:
        return UNI_PROVINCE_MAP[base]
    return ''


_UNI_DETAILS_MAP = {}


def load_university_details():
    """加载 university_details.json 构建名称映射"""
    global _UNI_DETAILS_MAP
    if UNI_DETAILS_FILE.exists():
        with open(UNI_DETAILS_FILE, 'r', encoding='utf-8') as f:
            details = json.load(f)
        unis = details.get('universities', {})
        for uid, info in unis.items():
            name = info.get('name', '') or info.get('basic_info', {}).get('name', '')
            if name:
                _UNI_DETAILS_MAP[name] = info
        print(f'  Loaded {len(_UNI_DETAILS_MAP)} university detail records')
    else:
        print(f'  Warning: {UNI_DETAILS_FILE} not found')


# ============================================================
# 1. 加载与清洗数据
# ============================================================
def load_and_clean_data():
    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    records = data.get('major_rank_data', [])
    print(f'Loaded {len(records)} records from {MAIN_FILE}')

    # 统计年份
    year_counts = Counter(r['year'] for r in records)
    print(f'  By year: {dict(year_counts)}')

    # 修复 university_province
    fixed = 0
    inferred = 0
    unknown = 0
    for r in records:
        if not r.get('university_province') or r['university_province'] == '':
            uni = r['university_name']
            if uni in UNI_PROVINCE_MAP:
                r['university_province'] = UNI_PROVINCE_MAP[uni]
                fixed += 1
            else:
                prov = infer_province(uni)
                if prov:
                    r['university_province'] = prov
                    inferred += 1
                else:
                    unknown += 1
    print(f'  Province: {fixed} fixed from known map, {inferred} inferred, {unknown} still unknown')

    # 按年份分组
    by_year = defaultdict(list)
    for r in records:
        by_year[r['year']].append(r)
    return records, by_year


# ============================================================
# 2. 位次段-院校热度矩阵
# ============================================================
def build_rank_hotness_matrix(records):
    """
    将 1-350000 位次按 5000 分段 (70 段)
    统计各位次段录取记录数最多的前 50 所院校
    """
    SEG_SIZE = 5000
    MAX_RANK = 350000
    TOP_N = 50

    segments = {}
    for seg_start in range(1, MAX_RANK + 1, SEG_SIZE):
        seg_end = seg_start + SEG_SIZE - 1
        seg_key = f"{seg_start}-{seg_end}"
        counter = Counter()
        for r in records:
            rank = r.get('min_rank', 0)
            if seg_start <= rank <= seg_end:
                counter[r['university_name']] += 1
        top_unis = counter.most_common(TOP_N)
        # 存储: [{university_name, count, level}]
        unis_list = []
        for uni_name, cnt in top_unis:
            # 查院校层次
            level = '普通本科'
            for rec in records:
                if rec['university_name'] == uni_name:
                    level = rec.get('university_level', '普通本科')
                    break
            unis_list.append({
                'university_name': uni_name,
                'count': cnt,
                'university_level': level
            })
        segments[seg_key] = unis_list

    # 插值填充空段
    seg_keys_sorted = sorted(segments.keys(), key=lambda k: int(k.split('-')[0]))
    for i, seg_key in enumerate(seg_keys_sorted):
        if not segments[seg_key] and i == 0:
            # 第一段为空: 用第一非空段
            for j in range(i + 1, len(seg_keys_sorted)):
                if segments[seg_keys_sorted[j]]:
                    segments[seg_key] = segments[seg_keys_sorted[j]]
                    break

    filled = 0
    for i, seg_key in enumerate(seg_keys_sorted):
        if not segments[seg_key]:
            # 找最近的上下非空段
            prev_val = None
            for j in range(i - 1, -1, -1):
                if segments[seg_keys_sorted[j]]:
                    prev_val = segments[seg_keys_sorted[j]]
                    break
            next_val = None
            for j in range(i + 1, len(seg_keys_sorted)):
                if segments[seg_keys_sorted[j]]:
                    next_val = segments[seg_keys_sorted[j]]
                    break
            if prev_val:
                segments[seg_key] = prev_val
                filled += 1
            elif next_val:
                segments[seg_key] = next_val
                filled += 1

    total_segs = len(seg_keys_sorted)
    empty_segs = sum(1 for k in seg_keys_sorted if not segments[k])
    print(f'  Rank hotness: {total_segs- empty_segs}/{total_segs} segments populated, {filled} interpolated')

    return {
        'metadata': {
            'total_records': len(records),
            'segment_size': SEG_SIZE,
            'max_rank': MAX_RANK,
            'top_n_per_segment': TOP_N,
            'generated_at': datetime.now().isoformat()
        },
        'segments': segments
    }


# ============================================================
# 3. 城市吸引力指数
# ============================================================
def build_city_attraction_index(records):
    """
    按省份(城市)分组，计算 2025 年投档位次均值
    位次越低 = 越难考上 = 吸引力越高
    标准化为 0-1 分数
    """
    by_province = defaultdict(list)
    for r in records:
        if r['year'] == 2025:
            prov = r.get('university_province', '')
            rank = r.get('min_rank', 0)
            if prov and rank > 0:
                by_province[prov].append(rank)

    province_scores = {}
    for prov, ranks in by_province.items():
        if len(ranks) < 5:
            continue  # 样本太少跳过
        avg_rank = sum(ranks) / len(ranks)
        median_rank = sorted(ranks)[len(ranks) // 2]
        province_scores[prov] = {
            'avg_rank': round(avg_rank, 1),
            'median_rank': median_rank,
            'sample_count': len(ranks),
            'min_rank': min(ranks),
            'max_rank': max(ranks)
        }

    # 标准化为 0-1 (越低越好 → 反转)
    if province_scores:
        max_avg = max(v['avg_rank'] for v in province_scores.values())
        min_avg = min(v['avg_rank'] for v in province_scores.values())
        rng = max_avg - min_avg
        if rng > 0:
            for prov in province_scores:
                raw = province_scores[prov]['avg_rank']
                # 反转: 低排名→高吸引力分
                province_scores[prov]['attraction_score'] = round(
                    1.0 - (raw - min_avg) / rng, 4
                )

    # 排序
    sorted_provinces = sorted(
        province_scores.items(),
        key=lambda x: x[1].get('attraction_score', 0),
        reverse=True
    )
    ranked_provinces = {}
    for rank, (prov, info) in enumerate(sorted_provinces, 1):
        info['attraction_rank'] = rank
        ranked_provinces[prov] = info

    print(f'  City attraction: {len(ranked_provinces)} provinces')
    top5 = list(ranked_provinces.keys())[:5]
    print(f'    Top 5: {", ".join(top5)}')

    return {
        'metadata': {
            'year': 2025,
            'total_provinces': len(ranked_provinces),
            'generated_at': datetime.now().isoformat()
        },
        'provinces': ranked_provinces
    }


# ============================================================
# 4. 专业热度趋势
# ============================================================
# 专业大类关键词映射
MAJOR_CATEGORIES = {
    '计算机类': ['计算机', '软件', '人工智能', '数据', '网络工程', '信息安全',
               '物联网', '大数据', '智能科学', '数字媒体技术', '区块链'],
    '电子信息类': ['电子', '通信', '信息', '微电子', '光电', '集成电路', '电气', '自动化'],
    '医学类': ['临床', '医学', '药学', '护理', '口腔', '中医', '基础医学', '预防医学',
             '麻醉', '影像', '检验', '康复', '中药', '制药', '公共卫生', '法医'],
    '财经类': ['经济', '金融', '会计', '财务', '工商管理', '市场营销', '国际商务',
             '财务管理', '审计', '保险', '税收', '财政', '国贸', '贸易'],
    '法学类': ['法学', '法律', '知识产权', '政治', '社会工作', '公安', '侦查'],
    '机械类': ['机械', '车辆', '材料', '测控', '仪器', '能源', '力学', '航空航天'],
    '土木建筑类': ['土木', '建筑', '城乡规划', '风景园林', '给排水', '道路', '桥梁',
                '工程管理', '工程造价', '水利', '测绘'],
    '文学类': ['英语', '日语', '法语', '德语', '翻译', '汉语', '新闻', '广告',
             '编辑', '出版', '传播', '汉语言', '秘书', '商务英语'],
    '理学类': ['数学', '物理', '化学', '生物', '地理', '统计', '应用物理', '大气',
             '海洋', '地质', '天文', '心理'],
    '师范教育类': ['教育', '师范', '学前', '体育', '特殊教育', '小学教育'],
    '艺术类': ['美术', '音乐', '舞蹈', '设计', '动画', '表演', '书法', '播音',
             '编导', '摄影', '戏剧', '影视', '产品设计', '视觉', '环境设计'],
}

# 从 major_name 推断专业大类
def classify_major(major_name):
    if not major_name:
        return '其他'
    mn = str(major_name)
    for cat_name, keywords in MAJOR_CATEGORIES.items():
        for kw in keywords:
            if kw in mn:
                return cat_name
    return '其他'


def build_major_trend_analysis(by_year):
    """
    对每个 (大学+专业组) 追踪 2023→2024→2025 位次变化
    同时计算大类趋势
    """
    # 按 (大学, 专业组编号) 追踪
    by_uni_major = defaultdict(dict)

    for year in [2023, 2024, 2025]:
        if year not in by_year:
            continue
        for r in by_year[year]:
            uni = r['university_name']
            major = r.get('major_name', '')
            group_code = r.get('group_code', '')
            key = f"{uni}||{group_code}"
            if year not in by_uni_major[key]:
                by_uni_major[key][year] = r['min_rank']

    # 分析趋势
    trends = []
    for key, year_ranks in by_uni_major.items():
        uni, group_code = key.split('||', 1)
        ranks = {y: year_ranks.get(y) for y in [2023, 2024, 2025]}
        has_2023 = 2023 in ranks and ranks[2023] is not None and ranks[2023] > 0
        has_2024 = 2024 in ranks and ranks[2024] is not None and ranks[2024] > 0
        has_2025 = 2025 in ranks and ranks[2025] is not None and ranks[2025] > 0

        # 确定趋势类型
        if has_2023 and has_2025:
            r2023, r2025 = ranks[2023], ranks[2025]
            if r2023 > 0 and r2025 > 0:
                change_pct = (r2023 - r2025) / r2023
                if change_pct > 0.05:
                    trend = 'warming'
                elif change_pct < -0.05:
                    trend = 'cooling'
                else:
                    trend = 'stable'
            else:
                trend = 'unknown'
        elif has_2023 and has_2024:
            r2023, r2024 = ranks[2023], ranks[2024]
            if r2023 > 0 and r2024 > 0:
                change_pct = (r2023 - r2024) / r2023
                if change_pct > 0.05:
                    trend = 'warming'
                elif change_pct < -0.05:
                    trend = 'cooling'
                else:
                    trend = 'stable'
            else:
                trend = 'unknown'
        elif has_2024 and has_2025:
            r2024, r2025 = ranks[2024], ranks[2025]
            if r2024 > 0 and r2025 > 0:
                change_pct = (r2024 - r2025) / r2024
                if change_pct > 0.05:
                    trend = 'warming'
                elif change_pct < -0.05:
                    trend = 'cooling'
                else:
                    trend = 'stable'
            else:
                trend = 'unknown'
        else:
            trend = 'unknown'

        # 计算变化率
        if has_2023 and has_2025 and ranks[2023] > 0:
            pct_23_25 = round((ranks[2023] - ranks[2025]) / ranks[2023] * 100, 2)
        else:
            pct_23_25 = None

        trends.append({
            'university_name': uni,
            'group_code': group_code,
            'rank_2023': ranks.get(2023, 0),
            'rank_2024': ranks.get(2024, 0),
            'rank_2025': ranks.get(2025, 0),
            'trend': trend,
            'change_pct_2023_2025': pct_23_25
        })

    # 统计
    trend_counts = Counter(t['trend'] for t in trends)
    print(f'  Major trends: {len(trends)} (uni,group) combinations')
    print(f'    warming={trend_counts.get("warming",0)}, stable={trend_counts.get("stable",0)}, cooling={trend_counts.get("cooling",0)}, unknown={trend_counts.get("unknown",0)}')

    # 按大类聚合趋势
    # 需要获取每个组合的 major_name 来分类
    # 从 records 中获取
    major_categories_lookup = {}
    for r in by_year.get(2025, []) + by_year.get(2024, []) + by_year.get(2023, []):
        key = f"{r['university_name']}||{r.get('group_code', '')}"
        major_categories_lookup[key] = r.get('major_name', '')

    cat_trends = defaultdict(lambda: {'warming': 0, 'stable': 0, 'cooling': 0, 'unknown': 0, 'total': 0})
    for t in trends:
        key = f"{t['university_name']}||{t['group_code']}"
        mn = major_categories_lookup.get(key, '')
        cat = classify_major(mn)
        cat_trends[cat][t['trend']] += 1
        cat_trends[cat]['total'] += 1

    # 计算热度分数: warming=1.0, stable=0.7, cooling=0.3, unknown=0.5
    cat_scores = {}
    for cat, counts in cat_trends.items():
        total = counts['total']
        if total > 0:
            score = (
                counts['warming'] * 1.0 +
                counts['stable'] * 0.7 +
                counts['cooling'] * 0.3 +
                counts['unknown'] * 0.5
            ) / total
            cat_scores[cat] = {
                'trend_score': round(score, 4),
                'warming_pct': round(counts['warming'] / total * 100, 1),
                'stable_pct': round(counts['stable'] / total * 100, 1),
                'cooling_pct': round(counts['cooling'] / total * 100, 1),
                'total_combinations': total
            }
    print(f'  Category trends: {len(cat_scores)} categories')
    for cat in sorted(cat_scores.keys()):
        sc = cat_scores[cat]
        print(f'    {cat}: score={sc["trend_score"]}, warming={sc["warming_pct"]}%')

    return {
        'metadata': {
            'total_combinations': len(trends),
            'trend_counts': dict(trend_counts),
            'generated_at': datetime.now().isoformat()
        },
        'trends': trends,
        'category_trends': {k: dict(v) for k, v in cat_scores.items()},
        'trend_score_map': {'warming': 1.0, 'stable': 0.7, 'cooling': 0.3, 'unknown': 0.5}
    }


# ============================================================
# 5. 主函数
# ============================================================
def main():
    print('=' * 60)
    print('Building Data-Driven Models')
    print('=' * 60)

    load_university_details()
    records, by_year = load_and_clean_data()

    # 2. 位次段-院校热度矩阵
    print('\n--- Rank Segment Hotness Matrix ---')
    hotness = build_rank_hotness_matrix(records)
    with open(OUT_HOTNESS, 'w', encoding='utf-8') as f:
        json.dump(hotness, f, ensure_ascii=False, indent=2)
    print(f'  Saved: {OUT_HOTNESS}')

    # 3. 城市吸引力指数
    print('\n--- City Attraction Index ---')
    city = build_city_attraction_index(records)
    with open(OUT_CITY, 'w', encoding='utf-8') as f:
        json.dump(city, f, ensure_ascii=False, indent=2)
    print(f'  Saved: {OUT_CITY}')

    # 4. 专业热度趋势
    print('\n--- Major Trend Analysis ---')
    trend = build_major_trend_analysis(by_year)
    with open(OUT_TREND, 'w', encoding='utf-8') as f:
        json.dump(trend, f, ensure_ascii=False, indent=2)
    print(f'  Saved: {OUT_TREND}')

    print('\n' + '=' * 60)
    print('All models built successfully!')
    print(f'  {OUT_HOTNESS}')
    print(f'  {OUT_CITY}')
    print(f'  {OUT_TREND}')
    print('=' * 60)


if __name__ == '__main__':
    main()
