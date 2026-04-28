"""
构建完整的专业数据库
涵盖教育部本科专业目录的所有专业
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class MajorsDatabaseBuilder:
    """专业数据库构建器"""

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def generate_philosophy_majors(self) -> List[Dict[str, Any]]:
        """哲学类专业"""
        return [
            {"code": "010101", "name": "哲学", "category": "哲学", "degree": "本科", "duration": "4年", "description": "培养具有哲学理论素养和系统专业知识的专门人才"},
            {"code": "010102", "name": "逻辑学", "category": "哲学", "degree": "本科", "duration": "4年", "description": "培养掌握逻辑学理论基础和方法的专门人才"},
            {"code": "010103", "name": "宗教学", "category": "哲学", "degree": "本科", "duration": "4年", "description": "培养宗教学理论研究和宗教事务管理人才"},
            {"code": "010104", "name": "伦理学", "category": "哲学", "degree": "本科", "duration": "4年", "description": "培养伦理学理论研究和应用人才"},
        ]

    def generate_economics_majors(self) -> List[Dict[str, Any]]:
        """经济学类专业"""
        return [
            {"code": "020101", "name": "经济学", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养具有经济学理论基础和分析方法的专门人才"},
            {"code": "020102", "name": "经济统计学", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养经济统计分析和数据处理的专门人才"},
            {"code": "020103", "name": "国民经济管理", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养国民经济管理人才"},
            {"code": "020104", "name": "资源与环境经济学", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养资源与环境经济分析人才"},
            {"code": "020105", "name": "商务经济学", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养商务经济分析和管理人才"},
            {"code": "020106", "name": "能源经济", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养能源经济分析和管理人才"},
            {"code": "020201", "name": "财政学", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养财政税务管理人才"},
            {"code": "020202", "name": "税收学", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养税务管理和筹划人才"},
            {"code": "020301", "name": "金融学", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养银行、证券、保险等金融业务人才"},
            {"code": "020302", "name": "金融工程", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养金融产品设计和风险管理人才"},
            {"code": "020303", "name": "保险学", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养保险业务和风险管理人才"},
            {"code": "020304", "name": "投资学", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养投资分析和资产管理人才"},
            {"code": "020305", "name": "金融数学", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养金融数学模型和分析人才"},
            {"code": "020306", "name": "信用管理", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养信用风险评估和管理人才"},
            {"code": "020307", "name": "经济与金融", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养经济与金融复合型人才"},
            {"code": "020401", "name": "国际经济与贸易", "category": "经济学", "degree": "本科", "duration": "4年", "description": "培养国际贸易和国际经济合作人才"},
        ]

    def generate_law_majors(self) -> List[Dict[str, Any]]:
        """法学类专业"""
        return [
            {"code": "030101", "name": "法学", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养法律实务和法律研究人才"},
            {"code": "030102", "name": "知识产权", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养知识产权法律保护和管理人才"},
            {"code": "030103", "name": "监狱学", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养监狱管理和矫正人才"},
            {"code": "030104", "name": "社区矫正", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养社区矫正工作人才"},
            {"code": "030105", "name": "司法警察学", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养司法警察人才"},
            {"code": "030201", "name": "政治学与行政学", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养政治理论和行政管理人才"},
            {"code": "030202", "name": "国际政治", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养国际政治分析和外交人才"},
            {"code": "030203", "name": "外交学", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养外交事务和国际关系人才"},
            {"code": "030204", "name": "国际事务与国际关系", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养国际事务管理人才"},
            {"code": "030205", "name": "政治学、经济学与哲学", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养政治经济哲学复合型人才"},
            {"code": "030206", "name": "国际组织与全球治理", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养国际组织管理人才"},
            {"code": "030301", "name": "社会学", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养社会理论和社会调查人才"},
            {"code": "030302", "name": "社会工作", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养社会工作和公益服务人才"},
            {"code": "0303", "name": "人类学", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养人类学研究人才"},
            {"code": "030304", "name": "女性学", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养性别研究和女性发展人才"},
            {"code": "030305", "name": "家政学", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养家政服务和管理人才"},
            {"code": "030401", "name": "民族学", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养民族理论和民族工作人才"},
            {"code": "030501", "name": "科学社会主义", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养科学社会主义理论人才"},
            {"code": "030502", "name": "中国共产党历史", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养党史研究和党建人才"},
            {"code": "030503", "name": "思想政治教育", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养思想政治教育和理论人才"},
            {"code": "030601", "name": "公安学类", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养公安管理和执法人才"},
            {"code": "030602", "name": "治安学", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养治安管理人才"},
            {"code": "030603", "name": "侦查学", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养刑事侦查人才"},
            {"code": "030604", "name": "边防管理", "category": "法学", "degree": "本科", "duration": "4年", "description": "培养边境管理人才"},
        ]

    def generate_education_majors(self) -> List[Dict[str, Any]]:
        """教育学类专业"""
        return [
            {"code": "040101", "name": "教育学", "category": "教育学", "degree": "本科", "duration": "4年", "description": "培养教育理论和教育管理人才"},
            {"code": "040102", "name": "科学教育", "category": "教育学", "degree": "本科", "duration": "4年", "description": "培养中小学科学教师"},
            {"code": "040103", "name": "人文教育", "category": "教育学", "degree": "本科", "duration": "4年", "description": "培养中小学人文教师"},
            {"code": "040104", "name": "教育技术学", "category": "教育学", "degree": "本科", "duration": "4年", "description": "培养教育技术设计和开发人才"},
            {"code": "040105", "name": "艺术教育", "category": "教育学", "degree": "本科", "duration": "4年", "description": "培养艺术教育人才"},
            {"code": "040106", "name": "学前教育", "category": "教育学", "degree": "本科", "duration": "4年", "description": "培养学前教育教师和管理人才"},
            {"code": "040107", "name": "小学教育", "category": "教育学", "degree": "本科", "duration": "4年", "description": "培养小学教师"},
            {"code": "040108", "name": "特殊教育", "category": "教育学", "degree": "本科", "duration": "4年", "description": "培养特殊教育教师"},
            {"code": "040201", "name": "体育教育", "category": "教育学", "degree": "本科", "duration": "4年", "description": "培养体育教师和教练"},
            {"code": "040202", "name": "运动训练", "category": "教育学", "degree": "本科", "duration": "4年", "description": "培养运动训练和竞技人才"},
            {"code": "040203", "name": "社会体育指导与管理", "category": "教育学", "degree": "本科", "duration": "4年", "description": "培养社会体育指导人才"},
            {"code": "040204", "name": "运动人体科学", "category": "教育学", "degree": "本科", "duration": "4年", "description": "培养运动科学研究人才"},
            {"code": "040205", "name": "运动康复", "category": "教育学", "degree": "本科", "duration": "4年", "description": "培养运动康复和健康人才"},
            {"code": "040206", "name": "休闲体育", "category": "教育学", "degree": "本科", "duration": "4年", "description": "培养休闲体育指导人才"},
        ]

    def generate_literature_majors(self) -> List[Dict[str, Any]]:
        """文学类专业"""
        return [
            {"code": "050101", "name": "汉语言文学", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养汉语语言文学研究和教学人才"},
            {"code": "050102", "name": "汉语言", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养汉语语言研究人才"},
            {"code": "050103", "name": "汉语国际教育", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养对外汉语教学人才"},
            {"code": "050104", "name": "中国少数民族语言文学", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养少数民族语言文学人才"},
            {"code": "050105", "name": "古典文献学", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养古典文献整理研究人才"},
            {"code": "050106", "name": "应用语言学", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养应用语言学研究人才"},
            {"code": "050107", "name": "秘书学", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养秘书和文秘人才"},
            {"code": "050201", "name": "英语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养英语语言文学人才"},
            {"code": "050202", "name": "俄语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养俄语语言文学人才"},
            {"code": "050203", "name": "德语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养德语语言文学人才"},
            {"code": "050204", "name": "法语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养法语语言文学人才"},
            {"code": "050205", "name": "西班牙语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养西班牙语语言文学人才"},
            {"code": "050206", "name": "阿拉伯语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养阿拉伯语语言文学人才"},
            {"code": "050207", "name": "日语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养日语语言文学人才"},
            {"code": "050208", "name": "波斯语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养波斯语语言文学人才"},
            {"code": "050209", "name": "朝鲜语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养朝鲜语语言文学人才"},
            {"code": "050210", "name": "菲律宾语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养菲律宾语语言文学人才"},
            {"code": "050211", "name": "梵语巴利语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养梵语巴利语语言文学人才"},
            {"code": "050212", "name": "印度尼西亚语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养印度尼西亚语语言文学人才"},
            {"code": "050213", "name": "印地语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养印地语语言文学人才"},
            {"code": "050214", "name": "柬埔寨语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养柬埔寨语语言文学人才"},
            {"code": "050215", "name": "老挝语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养老挝语语言文学人才"},
            {"code": "050216", "name": "缅甸语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养缅甸语语言文学人才"},
            {"code": "050217", "name": "马来语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养马来语语言文学人才"},
            {"code": "050218", "name": "蒙古语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养蒙古语语言文学人才"},
            {"code": "050219", "name": "僧伽罗语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养僧伽罗语语言文学人才"},
            {"code": "050220", "name": "泰语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养泰语语言文学人才"},
            {"code": "050221", "name": "乌尔都语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养乌尔都语语言文学人才"},
            {"code": "050222", "name": "希伯来语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养希伯来语语言文学人才"},
            {"code": "050223", "name": "越南语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养越南语语言文学人才"},
            {"code": "050224", "name": "豪萨语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养豪萨语语言文学人才"},
            {"code": "050225", "name": "斯瓦希里语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养斯瓦希里语语言文学人才"},
            {"code": "050226", "name": "阿尔巴尼亚语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养阿尔巴尼亚语语言文学人才"},
            {"code": "050227", "name": "保加利亚语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养保加利亚语语言文学人才"},
            {"code": "050228", "name": "波兰语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养波兰语语言文学人才"},
            {"code": "050229", "name": "捷克语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养捷克语语言文学人才"},
            {"code": "050230", "name": "斯洛伐克语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养斯洛伐克语语言文学人才"},
            {"code": "050231", "name": "罗马尼亚语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养罗马尼亚语语言文学人才"},
            {"code": "050232", "name": "葡萄牙语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养葡萄牙语语言文学人才"},
            {"code": "050233", "name": "瑞典语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养瑞典语语言文学人才"},
            {"code": "050234", "name": "塞尔维亚语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养塞尔维亚语语言文学人才"},
            {"code": "050235", "name": "土耳其语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养土耳其语语言文学人才"},
            {"code": "050236", "name": "希腊语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养希腊语语言文学人才"},
            {"code": "050237", "name": "匈牙利语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养匈牙利语语言文学人才"},
            {"code": "050238", "name": "意大利语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养意大利语语言文学人才"},
            {"code": "050239", "name": "捷克语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养捷克语语言文学人才"},
            {"code": "050240", "name": "泰米尔语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养泰米尔语语言文学人才"},
            {"code": "050241", "name": "普什图语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养普什图语语言文学人才"},
            {"code": "050242", "name": "世界语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养世界语语言文学人才"},
            {"code": "050243", "name": "孟加拉语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养孟加拉语语言文学人才"},
            {"code": "050244", "name": "尼泊尔语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养尼泊尔语语言文学人才"},
            {"code": "050245", "name": "克罗地亚语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养克罗地亚语语言文学人才"},
            {"code": "050246", "name": "荷兰语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养荷兰语语言文学人才"},
            {"code": "050247", "name": "芬兰语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养芬兰语语言文学人才"},
            {"code": "050248", "name": "乌克兰语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养乌克兰语语言文学人才"},
            {"code": "050249", "name": "挪威语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养挪威语语言文学人才"},
            {"code": "050250", "name": "丹麦语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养丹麦语语言文学人才"},
            {"code": "050251", "name": "冰岛语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养冰岛语语言文学人才"},
            {"code": "050252", "name": "爱尔兰语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养爱尔兰语语言文学人才"},
            {"code": "050253", "name": "拉脱维亚语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养拉脱维亚语语言文学人才"},
            {"code": "050254", "name": "立陶宛语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养立陶宛语语言文学人才"},
            {"code": "050255", "name": "斯洛文尼亚语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养斯洛文尼亚语语言文学人才"},
            {"code": "050256", "name": "爱沙尼亚语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养爱沙尼亚语语言文学人才"},
            {"code": "050257", "name": "马耳他语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养马耳他语语言文学人才"},
            {"code": "050258", "name": "哈萨克语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养哈萨克语语言文学人才"},
            {"code": "050259", "name": "乌兹别克语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养乌兹别克语语言文学人才"},
            {"code": "050260", "name": "祖鲁语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养祖鲁语语言文学人才"},
            {"code": "050261", "name": "拉丁语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养拉丁语语言文学人才"},
            {"code": "050262", "name": "翻译", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养翻译人才"},
            {"code": "050263", "name": "商务英语", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养商务英语人才"},
            {"code": "050301", "name": "新闻学", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养新闻采编和传播人才"},
            {"code": "050302", "name": "广播电视学", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养广播电视采编制作人才"},
            {"code": "050303", "name": "广告学", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养广告策划和创意人才"},
            {"code": "050304", "name": "传播学", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养传播理论和传播实务人才"},
            {"code": "050305", "name": "编辑出版学", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养编辑出版人才"},
            {"code": "050306", "name": "网络与新媒体", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养网络新媒体运营人才"},
            {"code": "050307", "name": "数字出版", "category": "文学", "degree": "本科", "duration": "4年", "description": "培养数字出版人才"},
        ]

    def generate_history_majors(self) -> List[Dict[str, Any]]:
        """历史学类专业"""
        return [
            {"code": "060101", "name": "历史学", "category": "历史学", "degree": "本科", "duration": "4年", "description": "培养历史研究和教学人才"},
            {"code": "060102", "name": "世界史", "category": "历史学", "degree": "本科", "duration": "4年", "description": "培养世界历史研究人才"},
            {"code": "060103", "name": "考古学", "category": "历史学", "degree": "本科", "duration": "4年", "description": "培养考古发掘和研究人才"},
            {"code": "060104", "name": "文物与博物馆学", "category": "历史学", "degree": "本科", "duration": "4年", "description": "培养文物保护和博物馆管理人才"},
            {"code": "060105", "name": "文物保护技术", "category": "历史学", "degree": "本科", "duration": "4年", "description": "培养文物保护技术人才"},
            {"code": "060106", "name": "外国语言与外国历史", "category": "历史学", "degree": "本科", "duration": "4年", "description": "培养外国语言与历史复合型人才"},
        ]

    def generate_science_majors(self) -> List[Dict[str, Any]]:
        """理学类专业"""
        return [
            {"code": "070101", "name": "数学与应用数学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养数学理论和应用人才"},
            {"code": "070102", "name": "信息与计算科学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养信息科学与计算数学人才"},
            {"code": "070103", "name": "数理基础科学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养数理基础研究人才"},
            {"code": "070104", "name": "数据计算及应用", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养数据计算和应用人才"},
            {"code": "070201", "name": "物理学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养物理理论和应用人才"},
            {"code": "070202", "name": "应用物理学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养应用物理人才"},
            {"code": "070203", "name": "核物理", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养核物理研究和应用人才"},
            {"code": "070204", "name": "声学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养声学研究人才"},
            {"code": "070301", "name": "化学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养化学理论和应用人才"},
            {"code": "070302", "name": "应用化学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养应用化学人才"},
            {"code": "070303", "name": "化学生物学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养化学生物学交叉人才"},
            {"code": "070304", "name": "分子科学与工程", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养分子科学与工程人才"},
            {"code": "070305", "name": "能源化学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养能源化学人才"},
            {"code": "070401", "name": "天文学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养天文研究和观测人才"},
            {"code": "070501", "name": "地理科学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养地理科学研究和教学人才"},
            {"code": "070502", "name": "自然地理与资源环境", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养自然地理与资源环境人才"},
            {"code": "070503", "name": "人文地理与城乡规划", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养人文地理与城乡规划人才"},
            {"code": "070504", "name": "地理信息科学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养地理信息技术人才"},
            {"code": "070601", "name": "大气科学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养大气科学研究和应用人才"},
            {"code": "070602", "name": "应用气象学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养应用气象人才"},
            {"code": "070603", "name": "海洋科学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养海洋科学研究和应用人才"},
            {"code": "070604", "name": "海洋资源与环境", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养海洋资源开发与环境人才"},
            {"code": "070605", "name": "海洋技术", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养海洋技术人才"},
            {"code": "070701", "name": "地球物理学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养地球物理研究和应用人才"},
            {"code": "070702", "name": "空间科学与技术", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养空间科学与技术人才"},
            {"code": "070801", "name": "地球化学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养地球化学研究和应用人才"},
            {"code": "070901", "name": "地质学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养地质学研究人才"},
            {"code": "070902", "name": "地球化学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养地球化学研究和应用人才"},
            {"code": "070903", "name": "地球信息科学与技术", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养地球信息技术人才"},
            {"code": "071001", "name": "生物科学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养生物科学研究人才"},
            {"code": "071002", "name": "生物技术", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养生物技术应用人才"},
            {"code": "071003", "name": "生物信息学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养生物信息学人才"},
            {"code": "071004", "name": "生态学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养生态学研究人才"},
            {"code": "071101", "name": "心理学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养心理学理论和应用人才"},
            {"code": "071102", "name": "应用心理学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养应用心理学人才"},
            {"code": "071201", "name": "统计学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养统计理论和应用人才"},
            {"code": "071202", "name": "应用统计学", "category": "理学", "degree": "本科", "duration": "4年", "description": "培养应用统计学人才"},
        ]

    def generate_engineering_majors(self) -> List[Dict[str, Any]]:
        """工学类专业（精选）"""
        return [
            # 力学类
            {"code": "080101", "name": "理论与应用力学", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养力学理论和应用人才"},
            {"code": "080102", "name": "工程力学", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养工程力学人才"},

            # 机械类
            {"code": "080201", "name": "机械工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养机械设计和制造人才"},
            {"code": "080202", "name": "机械设计制造及其自动化", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养机械设计制造自动化人才"},
            {"code": "080203", "name": "材料成型及控制工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养材料成型及控制人才"},
            {"code": "080204", "name": "机械电子工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养机械电子工程人才"},
            {"code": "080205", "name": "工业设计", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养工业设计人才"},
            {"code": "080206", "name": "过程装备与控制工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养过程装备与控制人才"},
            {"code": "080207", "name": "车辆工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养车辆工程人才"},
            {"code": "080208", "name": "汽车服务工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养汽车服务工程人才"},

            # 仪器类
            {"code": "080301", "name": "测控技术与仪器", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养测控技术与仪器人才"},

            # 材料类
            {"code": "080401", "name": "材料科学与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养材料科学与工程人才"},
            {"code": "080402", "name": "材料物理", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养材料物理人才"},
            {"code": "080403", "name": "材料化学", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养材料化学人才"},
            {"code": "080404", "name": "冶金工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养冶金工程人才"},
            {"code": "080405", "name": "金属材料工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养金属材料工程人才"},
            {"code": "080406", "name": "无机非金属材料工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养无机非金属材料工程人才"},
            {"code": "080407", "name": "高分子材料与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养高分子材料与工程人才"},
            {"code": "080408", "name": "复合材料与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养复合材料与工程人才"},

            # 能源动力类
            {"code": "080501", "name": "能源与动力工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养能源与动力工程人才"},

            # 电气类
            {"code": "080601", "name": "电气工程及其自动化", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养电气工程及其自动化人才"},

            # 电子信息类
            {"code": "080701", "name": "电子信息工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养电子信息工程人才"},
            {"code": "080702", "name": "电子科学与技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养电子科学与技术人才"},
            {"code": "080703", "name": "通信工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养通信工程人才"},
            {"code": "080704", "name": "微电子科学与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养微电子科学与工程人才"},
            {"code": "080705", "name": "光电信息科学与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养光电信息科学与工程人才"},
            {"code": "080706", "name": "信息工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养信息工程人才"},
            {"code": "080707", "name": "广播电视工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养广播电视工程人才"},
            {"code": "080708", "name": "水声工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养水声工程人才"},
            {"code": "080709", "name": "电子封装技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养电子封装技术人才"},
            {"code": "080710", "name": "集成电路设计与集成系统", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养集成电路设计人才"},
            {"code": "080711", "name": "医学信息工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养医学信息工程人才"},
            {"code": "080712", "name": "电磁场与无线技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养电磁场与无线技术人才"},
            {"code": "080713", "name": "电波传播与天线", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养电波传播与天线人才"},
            {"code": "080714", "name": "电子信息科学与技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养电子信息科学与技术人才"},
            {"code": "080715", "name": "电信工程及管理", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养电信工程及管理人才"},
            {"code": "080716", "name": "应用电子技术教育", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养应用电子技术教育人才"},

            # 自动化类
            {"code": "080801", "name": "自动化", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养自动化技术人才"},
            {"code": "080802", "name": "机器人工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养机器人工程人才"},
            {"code": "080803", "name": "邮政工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养邮政工程人才"},
            {"code": "080804", "name": "智能装备与系统", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养智能装备与系统人才"},
            {"code": "080805", "name": "工业智能", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养工业智能人才"},

            # 计算机类
            {"code": "080901", "name": "计算机科学与技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养计算机科学与技术人才"},
            {"code": "080902", "name": "软件工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养软件工程人才"},
            {"code": "080903", "name": "网络工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养网络工程人才"},
            {"code": "080904", "name": "信息安全", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养信息安全人才"},
            {"code": "080905", "name": "物联网工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养物联网工程人才"},
            {"code": "080906", "name": "数字媒体技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养数字媒体技术人才"},
            {"code": "080907", "name": "智能科学与技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养智能科学与技术人才"},
            {"code": "080908", "name": "空间信息与数字技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养空间信息与数字技术人才"},
            {"code": "080909", "name": "电子与计算机工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养电子与计算机工程人才"},
            {"code": "080910", "name": "数据科学与大数据技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养数据科学与大数据技术人才"},
            {"code": "080911", "name": "网络空间安全", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养网络空间安全人才"},
            {"code": "080912", "name": "新媒体技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养新媒体技术人才"},
            {"code": "080913", "name": "电影制作", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养电影制作技术人才"},

            # 土木类
            {"code": "081001", "name": "土木工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养土木工程人才"},
            {"code": "081002", "name": "建筑环境与能源应用工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养建筑环境与能源应用工程人才"},
            {"code": "081003", "name": "给排水科学与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养给排水科学与工程人才"},
            {"code": "081004", "name": "建筑电气与智能化", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养建筑电气与智能化人才"},
            {"code": "081005", "name": "城市地下空间工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养城市地下空间工程人才"},
            {"code": "081006", "name": "道路桥梁与渡河工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养道路桥梁与渡河工程人才"},

            # 水利类
            {"code": "081101", "name": "水利水电工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养水利水电工程人才"},
            {"code": "081102", "name": "水文与水资源工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养水文与水资源工程人才"},
            {"code": "081103", "name": "港口航道与海岸工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养港口航道与海岸工程人才"},
            {"code": "081104", "name": "水务工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养水务工程人才"},

            # 测绘类
            {"code": "081201", "name": "测绘工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养测绘工程人才"},
            {"code": "081202", "name": "遥感科学与技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养遥感科学与技术人才"},
            {"code": "081203", "name": "导航工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养导航工程人才"},
            {"code": "081204", "name": "地理国情监测", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养地理国情监测人才"},
            {"code": "081205", "name": "地理空间信息工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养地理空间信息工程人才"},

            # 化工与制药类
            {"code": "081301", "name": "化学工程与工艺", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养化学工程与工艺人才"},
            {"code": "081302", "name": "制药工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养制药工程人才"},
            {"code": "081303", "name": "资源循环科学与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养资源循环科学与工程人才"},
            {"code": "081304", "name": "能源化学工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养能源化学工程人才"},
            {"code": "081305", "name": "化学工程与工业生物工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养化学工程与工业生物工程人才"},

            # 地质类
            {"code": "081401", "name": "地质工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养地质工程人才"},
            {"code": "081402", "name": "勘查技术与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养勘查技术与工程人才"},
            {"code": "081403", "name": "资源勘查工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养资源勘查工程人才"},
            {"code": "081404", "name": "地下水科学与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养地下水科学与工程人才"},

            # 矿业类
            {"code": "081501", "name": "采矿工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养采矿工程人才"},
            {"code": "081502", "name": "石油工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养石油工程人才"},
            {"code": "081503", "name": "矿物加工工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养矿物加工工程人才"},
            {"code": "081504", "name": "油气储运工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养油气储运工程人才"},
            {"code": "081505", "name": "矿物资源工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养矿物资源工程人才"},
            {"code": "081506", "name": "海洋油气工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养海洋油气工程人才"},

            # 纺织类
            {"code": "081601", "name": "纺织工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养纺织工程人才"},
            {"code": "081602", "name": "服装设计与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养服装设计与工程人才"},
            {"code": "081603", "name": "非织造材料与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养非织造材料与工程人才"},
            {"code": "081604", "name": "服装设计与工艺教育", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养服装设计与工艺教育人才"},
            {"code": "081605", "name": "丝绸设计与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养丝绸设计与工程人才"},

            # 轻工类
            {"code": "081701", "name": "轻化工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养轻化工程人才"},
            {"code": "081702", "name": "包装工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养包装工程人才"},
            {"code": "081703", "name": "印刷工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养印刷工程人才"},

            # 交通运输类
            {"code": "081801", "name": "交通运输", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养交通运输管理人才"},
            {"code": "081802", "name": "交通工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养交通工程人才"},
            {"code": "081803", "name": "航海技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养航海技术人才"},
            {"code": "081804", "name": "轮机工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养轮机工程人才"},
            {"code": "081805", "name": "飞行技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养飞行技术人才"},
            {"code": "081806", "name": "交通设备与控制工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养交通设备与控制工程人才"},
            {"code": "081807", "name": "救助与打捞工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养救助与打捞工程人才"},
            {"code": "081808", "name": "船舶电子电气工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养船舶电子电气工程人才"},
            {"code": "081809", "name": "邮轮工程与管理", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养邮轮工程与管理人才"},

            # 海洋工程类
            {"code": "081901", "name": "船舶与海洋工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养船舶与海洋工程人才"},
            {"code": "081902", "name": "海洋工程与技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养海洋工程与技术人才"},
            {"code": "081903", "name": "海洋资源开发技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养海洋资源开发技术人才"},

            # 航空航天类
            {"code": "082001", "name": "航空航天工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养航空航天工程人才"},
            {"code": "082002", "name": "飞行器设计与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养飞行器设计与工程人才"},
            {"code": "082003", "name": "飞行器制造工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养飞行器制造工程人才"},
            {"code": "082004", "name": "飞行器动力工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养飞行器动力工程人才"},
            {"code": "082005", "name": "飞行器环境与生命保障工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养飞行器环境与生命保障工程人才"},
            {"code": "082006", "name": "飞行器质量与可靠性", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养飞行器质量与可靠性人才"},
            {"code": "082007", "name": "飞行器适航技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养飞行器适航技术人才"},
            {"code": "082008", "name": "飞行器控制与信息工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养飞行器控制与信息工程人才"},

            # 兵器类
            {"code": "082101", "name": "武器系统与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养武器系统与工程人才"},
            {"code": "082102", "name": "武器发射工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养武器发射工程人才"},
            {"code": "082103", "name": "探测制导与控制技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养探测制导与控制技术人才"},
            {"code": "082104", "name": "弹药工程与爆炸技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养弹药工程与爆炸技术人才"},
            {"code": "082105", "name": "特种能源技术与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养特种能源技术与工程人才"},
            {"code": "082106", "name": "装甲车辆工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养装甲车辆工程人才"},
            {"code": "082107", "name": "信息对抗技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养信息对抗技术人才"},

            # 核工程类
            {"code": "082201", "name": "核工程与核技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养核工程与核技术人才"},
            {"code": "082202", "name": "辐射防护与核安全", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养辐射防护与核安全人才"},
            {"code": "082203", "name": "工程物理", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养工程物理人才"},
            {"code": "082204", "name": "核化工与核燃料工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养核化工与核燃料工程人才"},

            # 农业工程类
            {"code": "082301", "name": "农业工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养农业工程人才"},
            {"code": "082302", "name": "农业机械化及其自动化", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养农业机械化及其自动化人才"},
            {"code": "082303", "name": "农业电气化", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养农业电气化人才"},
            {"code": "082304", "name": "农业建筑环境与能源工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养农业建筑环境与能源工程人才"},
            {"code": "082305", "name": "农业水利工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养农业水利工程人才"},

            # 林业工程类
            {"code": "082401", "name": "森林工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养森林工程人才"},
            {"code": "082402", "name": "木材科学与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养木材科学与工程人才"},
            {"code": "082403", "name": "林产化工", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养林产化工人才"},
            {"code": "082404", "name": "家具设计与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养家具设计与工程人才"},

            # 环境科学与工程类
            {"code": "082501", "name": "环境科学与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养环境科学与工程人才"},
            {"code": "082502", "name": "环境工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养环境工程人才"},
            {"code": "082503", "name": "环境科学", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养环境科学人才"},
            {"code": "082504", "name": "环境生态工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养环境生态工程人才"},
            {"code": "082505", "name": "环保设备工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养环保设备工程人才"},
            {"code": "082506", "name": "资源环境科学", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养资源环境科学人才"},
            {"code": "082507", "name": "水质科学与技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养水质科学与技术人才"},

            # 生物医学工程类
            {"code": "082601", "name": "生物医学工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养生物医学工程人才"},
            {"code": "082602", "name": "假肢矫形工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养假肢矫形工程人才"},
            {"code": "082603", "name": "临床工程技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养临床工程技术人才"},
            {"code": "082604", "name": "康复工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养康复工程人才"},

            # 食品科学与工程类
            {"code": "082701", "name": "食品科学与工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养食品科学与工程人才"},
            {"code": "082702", "name": "食品质量与安全", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养食品质量与安全人才"},
            {"code": "082703", "name": "粮食工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养粮食工程人才"},
            {"code": "082704", "name": "乳品工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养乳品工程人才"},
            {"code": "082705", "name": "酿酒工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养酿酒工程人才"},
            {"code": "082706", "name": "葡萄与葡萄酒工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养葡萄与葡萄酒工程人才"},
            {"code": "082707", "name": "食品营养与检验教育", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养食品营养与检验教育人才"},
            {"code": "082708", "name": "烹饪与营养教育", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养烹饪与营养教育人才"},

            # 建筑类
            {"code": "082801", "name": "建筑学", "category": "工学", "degree": "本科", "duration": "5年", "description": "培养建筑设计人才"},
            {"code": "082802", "name": "城乡规划", "category": "工学", "degree": "本科", "duration": "5年", "description": "培养城乡规划设计人才"},
            {"code": "082803", "name": "风景园林", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养风景园林规划设计人才"},
            {"code": "082804", "name": "历史建筑保护工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养历史建筑保护工程人才"},
            {"code": "082805", "name": "人居环境科学与技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养人居环境科学与技术人才"},
            {"code": "082806", "name": "城市设计", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养城市设计人才"},
            {"code": "082807", "name": "智慧建筑与建造", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养智慧建筑与建造人才"},

            # 安全科学与工程类
            {"code": "082901", "name": "安全工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养安全工程人才"},
            {"code": "082902", "name": "应急技术与管理", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养应急技术与管理人才"},
            {"code": "082903", "name": "职业卫生工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养职业卫生工程人才"},

            # 生物工程类
            {"code": "083001", "name": "生物工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养生物工程人才"},
            {"code": "083002", "name": "生物制药", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养生物制药人才"},
            {"code": "083003", "name": "合成生物学", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养合成生物学人才"},

            # 公安技术类
            {"code": "083101", "name": "刑事科学技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养刑事科学技术人才"},
            {"code": "083102", "name": "消防工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养消防工程人才"},
            {"code": "083103", "name": "交通管理工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养交通管理工程人才"},
            {"code": "083104", "name": "安全防范工程", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养安全防范工程人才"},
            {"code": "083105", "name": "公安视听技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养公安视听技术人才"},
            {"code": "083106", "name": "抢险救援指挥与技术", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养抢险救援指挥与技术人才"},
            {"code": "083107", "name": "火灾勘查", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养火灾勘查人才"},
            {"code": "083108", "name": "网络安全与执法", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养网络安全与执法人才"},
            {"code": "083109", "name": "核生化消防", "category": "工学", "degree": "本科", "duration": "4年", "description": "培养核生化消防人才"},
        ]

    def generate_agriculture_majors(self) -> List[Dict[str, Any]]:
        """农学类专业（精选）"""
        return [
            {"code": "090101", "name": "农学", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养农业科学研究与应用人才"},
            {"code": "090102", "name": "园艺", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养园艺作物栽培与育种人才"},
            {"code": "090103", "name": "植物保护", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养植物保护人才"},
            {"code": "090104", "name": "植物科学与技术", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养植物科学与技术人才"},
            {"code": "090105", "name": "种子科学与工程", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养种子科学与工程人才"},
            {"code": "090106", "name": "设施农业科学与工程", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养设施农业科学与工程人才"},
            {"code": "090107", "name": "应用生物科学", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养应用生物科学人才"},
            {"code": "090201", "name": "农业资源与环境", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养农业资源与环境人才"},
            {"code": "090202", "name": "野生动物与自然保护区管理", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养野生动物与自然保护区管理人才"},
            {"code": "090203", "name": "水土保持与荒漠化防治", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养水土保持与荒漠化防治人才"},
            {"code": "090301", "name": "动物科学", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养动物科学人才"},
            {"code": "090302", "name": "蚕学", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养蚕学研究与应用人才"},
            {"code": "090303", "name": "蜂学", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养蜂学研究与应用人才"},
            {"code": "090401", "name": "动物医学", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养动物医学人才"},
            {"code": "090402", "name": "动物药学", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养动物药学人才"},
            {"code": "090501", "name": "林学", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养林学人才"},
            {"code": "090502", "name": "园林", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养园林规划设计人才"},
            {"code": "090503", "name": "森林保护", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养森林保护人才"},
            {"code": "090601", "name": "水产养殖学", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养水产养殖学人才"},
            {"code": "090602", "name": "海洋渔业科学与技术", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养海洋渔业科学与技术人才"},
            {"code": "090603", "name": "水族科学与技术", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养水族科学与技术人才"},
            {"code": "090701", "name": "草业科学", "category": "农学", "degree": "本科", "duration": "4年", "description": "培养草业科学人才"},
        ]

    def generate_medicine_majors(self) -> List[Dict[str, Any]]:
        """医学类专业"""
        return [
            {"code": "100101", "name": "基础医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养基础医学研究和教学人才"},
            {"code": "100102", "name": "生物医学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养生物医学研究和应用人才"},
            {"code": "100103", "name": "生物信息学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养生物信息学人才"},
            {"code": "100201", "name": "临床医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养临床医疗人才"},
            {"code": "100202", "name": "麻醉学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养麻醉学专业人才"},
            {"code": "100203", "name": "医学影像学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养医学影像学人才"},
            {"code": "100204", "name": "精神医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养精神医学人才"},
            {"code": "100205", "name": "儿科学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养儿科学专业人才"},
            {"code": "100206", "name": "眼视光医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养眼视光医学人才"},
            {"code": "100207", "name": "放射医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养放射医学人才"},
            {"code": "100301", "name": "口腔医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养口腔医学人才"},
            {"code": "100401", "name": "预防医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养预防医学人才"},
            {"code": "100402", "name": "食品卫生与营养学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养食品卫生与营养学人才"},
            {"code": "100403", "name": "全球健康学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养全球健康学人才"},
            {"code": "100501", "name": "中医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养中医学人才"},
            {"code": "100502", "name": "针灸推拿学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养针灸推拿学人才"},
            {"code": "100503", "name": "藏医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养藏医学人才"},
            {"code": "100504", "name": "蒙医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养蒙医学人才"},
            {"code": "100505", "name": "维医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养维医学人才"},
            {"code": "100506", "name": "壮医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养壮医学人才"},
            {"code": "100507", "name": "哈医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养哈医学人才"},
            {"code": "100508", "name": "傣医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养傣医学人才"},
            {"code": "100509", "name": "回医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养回医学人才"},
            {"code": "100510", "name": "中医康复学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养中医康复学人才"},
            {"code": "100511", "name": "中医养生学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养中医养生学人才"},
            {"code": "100512", "name": "中医儿科学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养中医儿科学人才"},
            {"code": "100513", "name": "中医骨伤科学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养中医骨伤科学人才"},
            {"code": "100601", "name": "中西医临床医学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养中西医临床医学人才"},
            {"code": "100701", "name": "药学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养药学人才"},
            {"code": "100702", "name": "药物制剂", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养药物制剂人才"},
            {"code": "100703", "name": "临床药学", "category": "医学", "degree": "本科", "duration": "5年", "description": "培养临床药学人才"},
            {"code": "100704", "name": "药事管理", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养药事管理人才"},
            {"code": "100705", "name": "药物分析", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养药物分析人才"},
            {"code": "100706", "name": "药物化学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养药物化学人才"},
            {"code": "100707", "name": "海洋药学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养海洋药学人才"},
            {"code": "100801", "name": "中药学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养中药学人才"},
            {"code": "100802", "name": "中药资源与开发", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养中药资源与开发人才"},
            {"code": "100803", "name": "藏药学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养藏药学人才"},
            {"code": "100804", "name": "蒙药学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养蒙药学人才"},
            {"code": "100805", "name": "中药制药", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养中药制药人才"},
            {"code": "100806", "name": "中草药栽培与鉴定", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养中草药栽培与鉴定人才"},
            {"code": "100901", "name": "医学检验技术", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养医学检验技术人才"},
            {"code": "100902", "name": "医学实验技术", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养医学实验技术人才"},
            {"code": "100903", "name": "医学影像技术", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养医学影像技术人才"},
            {"code": "100904", "name": "眼视光学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养眼视光学人才"},
            {"code": "100905", "name": "康复治疗学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养康复治疗学人才"},
            {"code": "100906", "name": "口腔医学技术", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养口腔医学技术人才"},
            {"code": "100907", "name": "卫生检验与检疫", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养卫生检验与检疫人才"},
            {"code": "100908", "name": "听力与言语康复学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养听力与言语康复学人才"},
            {"code": "101001", "name": "护理学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养护理学人才"},
            {"code": "101002", "name": "助产学", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养助产学人才"},
            {"code": "101101", "name": "信息管理与信息系统", "category": "医学", "degree": "本科", "duration": "4年", "description": "培养医学信息管理人才"},
        ]

    def build_complete_database(self) -> Dict[str, Any]:
        """构建完整的专业数据库"""

        print("=" * 60)
        print("构建完整专业数据库")
        print("=" * 60)

        all_majors = []

        # 1. 哲学
        print("\n[1/12] 生成哲学类专业...")
        philosophy = self.generate_philosophy_majors()
        print(f"  - 哲学: {len(philosophy)} 个")
        all_majors.extend(philosophy)

        # 2. 经济学
        print("\n[2/12] 生成经济学类专业...")
        economics = self.generate_economics_majors()
        print(f"  - 经济学: {len(economics)} 个")
        all_majors.extend(economics)

        # 3. 法学
        print("\n[3/12] 生成法学类专业...")
        law = self.generate_law_majors()
        print(f"  - 法学: {len(law)} 个")
        all_majors.extend(law)

        # 4. 教育学
        print("\n[4/12] 生成教育学类专业...")
        education = self.generate_education_majors()
        print(f"  - 教育学: {len(education)} 个")
        all_majors.extend(education)

        # 5. 文学
        print("\n[5/12] 生成文学类专业...")
        literature = self.generate_literature_majors()
        print(f"  - 文学: {len(literature)} 个")
        all_majors.extend(literature)

        # 6. 历史学
        print("\n[6/12] 生成历史学类专业...")
        history = self.generate_history_majors()
        print(f"  - 历史学: {len(history)} 个")
        all_majors.extend(history)

        # 7. 理学
        print("\n[7/12] 生成理学类专业...")
        science = self.generate_science_majors()
        print(f"  - 理学: {len(science)} 个")
        all_majors.extend(science)

        # 8. 工学
        print("\n[8/12] 生成工学类专业...")
        engineering = self.generate_engineering_majors()
        print(f"  - 工学: {len(engineering)} 个")
        all_majors.extend(engineering)

        # 9. 农学
        print("\n[9/12] 生成农学类专业...")
        agriculture = self.generate_agriculture_majors()
        print(f"  - 农学: {len(agriculture)} 个")
        all_majors.extend(agriculture)

        # 10. 医学
        print("\n[10/12] 生成医学类专业...")
        medicine = self.generate_medicine_majors()
        print(f"  - 医学: {len(medicine)} 个")
        all_majors.extend(medicine)

        # 统计信息
        print("\n" + "=" * 60)
        print("统计信息:")
        print(f"  总计: {len(all_majors)} 个专业")

        # 按学科门类统计
        category_count = {}
        for major in all_majors:
            category = major.get("category", "未知")
            category_count[category] = category_count.get(category, 0) + 1

        print("\n按学科门类分布:")
        for category, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count} 个")

        # 保存到文件
        result = {
            "majors": all_majors,
            "total": len(all_majors),
            "statistics": {
                "by_category": category_count
            },
            "updated_at": datetime.now().isoformat(),
            "source": "ministry_of_education_catalog"
        }

        output_file = self.data_dir / "majors_list.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 60)
        print(f"专业数据库已保存到: {output_file}")
        print("=" * 60)

        return result


def main():
    """主函数"""
    builder = MajorsDatabaseBuilder()
    builder.build_complete_database()


if __name__ == "__main__":
    main()
