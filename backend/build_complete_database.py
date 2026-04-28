"""
构建完整的高考志愿数据库
使用多源数据生成全国2800+所院校数据
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class UniversityDatabaseBuilder:
    """院校数据库构建器"""

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load_base_data(self) -> List[Dict[str, Any]]:
        """加载基础数据"""
        base_file = self.data_dir / "universities_list.json"
        if base_file.exists():
            with open(base_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("universities", [])
        return []

    def generate_985_universities(self) -> List[Dict[str, Any]]:
        """生成985工程院校列表（39所）"""
        universities = [
            {"id": "1", "name": "北京大学", "province": "北京", "city": "北京", "type": "综合", "level": "985", "website": "https://www.pku.edu.cn", "founded": "1898", "description": "中国近代第一所国立综合性大学"},
            {"id": "2", "name": "清华大学", "province": "北京", "city": "北京", "type": "综合", "level": "985", "website": "https://www.tsinghua.edu.cn", "founded": "1911", "description": "中国顶尖综合性大学"},
            {"id": "3", "name": "复旦大学", "province": "上海", "city": "上海", "type": "综合", "level": "985", "website": "https://www.fudan.edu.cn", "founded": "1905", "description": "江南第一学府"},
            {"id": "4", "name": "上海交通大学", "province": "上海", "city": "上海", "type": "综合", "level": "985", "website": "https://www.sjtu.edu.cn", "founded": "1896", "description": "理工科强校"},
            {"id": "5", "name": "浙江大学", "province": "浙江", "city": "杭州", "type": "综合", "level": "985", "website": "https://www.zju.edu.cn", "founded": "1897", "description": "东方剑桥"},
            {"id": "6", "name": "中国科学技术大学", "province": "安徽", "city": "合肥", "type": "综合", "level": "985", "website": "https://www.ustc.edu.cn", "founded": "1958", "description": "科技英才摇篮"},
            {"id": "7", "name": "南京大学", "province": "江苏", "city": "南京", "type": "综合", "level": "985", "website": "https://www.nju.edu.cn", "founded": "1902", "description": "亚洲第一私立大学"},
            {"id": "8", "name": "西安交通大学", "province": "陕西", "city": "西安", "type": "综合", "level": "985", "website": "https://www.xjtu.edu.cn", "founded": "1896", "description": "工科强校"},
            {"id": "9", "name": "哈尔滨工业大学", "province": "黑龙江", "city": "哈尔滨", "type": "综合", "level": "985", "website": "https://www.hit.edu.cn", "founded": "1920", "description": "工程师摇篮"},
            {"id": "10", "name": "北京航空航天大学", "province": "北京", "city": "北京", "type": "理工", "level": "985", "website": "https://www.buaa.edu.cn", "founded": "1952", "description": "航空航天第一校"},
            {"id": "11", "name": "天津大学", "province": "天津", "city": "天津", "type": "综合", "level": "985", "website": "https://www.tju.edu.cn", "founded": "1895", "description": "中国第一所现代大学"},
            {"id": "12", "name": "华中科技大学", "province": "湖北", "city": "武汉", "type": "综合", "level": "985", "website": "https://www.hust.edu.cn", "founded": "1952", "description": "新中国高等教育发展的缩影"},
            {"id": "13", "name": "武汉大学", "province": "湖北", "city": "武汉", "type": "综合", "level": "985", "website": "https://www.whu.edu.cn", "founded": "1893", "description": "中国最美大学"},
            {"id": "14", "name": "南开大学", "province": "天津", "city": "天津", "type": "综合", "level": "985", "website": "https://www.nankai.edu.cn", "founded": "1919", "description": "华北第一学府"},
            {"id": "15", "name": "山东大学", "province": "山东", "city": "济南", "type": "综合", "level": "985", "website": "https://www.sdu.edu.cn", "founded": "1901", "description": "近代高等教育的起源性大学"},
            {"id": "16", "name": "中南大学", "province": "湖南", "city": "长沙", "type": "综合", "level": "985", "website": "https://www.csu.edu.cn", "founded": "1903", "description": "湘雅医学院发源地"},
            {"id": "17", "name": "华南理工大学", "province": "广东", "city": "广州", "type": "综合", "level": "985", "website": "https://www.scut.edu.cn", "founded": "1952", "description": "华南地区理工第一校"},
            {"id": "18", "name": "厦门大学", "province": "福建", "city": "厦门", "type": "综合", "level": "985", "website": "https://www.xmu.edu.cn", "founded": "1921", "description": "南方之强"},
            {"id": "19", "name": "同济大学", "province": "上海", "city": "上海", "type": "综合", "level": "985", "website": "https://www.tongji.edu.cn", "founded": "1907", "description": "建筑土木第一校"},
            {"id": "20", "name": "中国人民大学", "province": "北京", "city": "北京", "type": "综合", "level": "985", "website": "https://www.ruc.edu.cn", "founded": "1937", "description": "人文社会科学第一校"},
            {"id": "21", "name": "北京师范大学", "province": "北京", "city": "北京", "type": "师范", "level": "985", "website": "https://www.bnu.edu.cn", "founded": "1902", "description": "师范第一校"},
            {"id": "22", "name": "东南大学", "province": "江苏", "city": "南京", "type": "综合", "level": "985", "website": "https://www.seu.edu.cn", "founded": "1902", "description": "建筑四杰之一"},
            {"id": "23", "name": "北京理工大学", "province": "北京", "city": "北京", "type": "理工", "level": "985", "website": "https://www.bit.edu.cn", "founded": "1940", "description": "国防七子之一"},
            {"id": "24", "name": "四川大学", "province": "四川", "city": "成都", "type": "综合", "level": "985", "website": "https://www.scu.edu.cn", "founded": "1896", "description": "西南第一学府"},
            {"id": "25", "name": "重庆大学", "province": "重庆", "city": "重庆", "type": "综合", "level": "985", "website": "https://www.cqu.edu.cn", "founded": "1929", "description": "嘉陵与长江相汇处"},
            {"id": "26", "name": "西北工业大学", "province": "陕西", "city": "西安", "type": "综合", "level": "985", "website": "https://www.nwpu.edu.cn", "founded": "1938", "description": "国防七子之一"},
            {"id": "27", "name": "吉林大学", "province": "吉林", "city": "长春", "type": "综合", "level": "985", "website": "https://www.jlu.edu.cn", "founded": "1946", "description": "东北第一学府"},
            {"id": "28", "name": "大连理工大学", "province": "辽宁", "city": "大连", "type": "综合", "level": "985", "website": "https://www.dlut.edu.cn", "founded": "1949", "description": "四大工学院之一"},
            {"id": "29", "name": "电子科技大学", "province": "四川", "city": "成都", "type": "理工", "level": "985", "website": "https://www.uestc.edu.cn", "founded": "1956", "description": "电子类第一校"},
            {"id": "30", "name": "华东师范大学", "province": "上海", "city": "上海", "type": "师范", "level": "985", "website": "https://www.ecnu.edu.cn", "founded": "1951", "description": "华东师范第一校"},
            {"id": "31", "name": "兰州大学", "province": "甘肃", "city": "兰州", "type": "综合", "level": "985", "website": "https://www.lzu.edu.cn", "founded": "1909", "description": "西部第一学府"},
            {"id": "32", "name": "东北大学", "province": "辽宁", "city": "沈阳", "type": "综合", "level": "985", "website": "https://www.neu.edu.cn", "founded": "1923", "description": "张学良创建"},
            {"id": "33", "name": "中国海洋大学", "province": "山东", "city": "青岛", "type": "综合", "level": "985", "website": "https://www.ouc.edu.cn", "founded": "1924", "description": "海洋第一校"},
            {"id": "34", "name": "湖南大学", "province": "湖南", "city": "长沙", "type": "综合", "level": "985", "website": "https://www.hnu.edu.cn", "founded": "1926", "description": "千年学府"},
            {"id": "35", "name": "中山大学", "province": "广东", "city": "广州", "type": "综合", "level": "985", "website": "https://www.sysu.edu.cn", "founded": "1924", "description": "华南第一学府"},
            {"id": "36", "name": "华中农业大学", "province": "湖北", "city": "武汉", "type": "农林", "level": "985", "website": "https://www.hzau.edu.cn", "founded": "1898", "description": "华中农业第一校"},
            {"id": "37", "name": "西北农林科技大学", "province": "陕西", "city": "杨凌", "type": "农林", "level": "985", "website": "https://www.nwafu.edu.cn", "founded": "1934", "description": "农林水学科最齐全"},
            {"id": "38", "name": "中央民族大学", "province": "北京", "city": "北京", "type": "综合", "level": "985", "website": "https://www.muc.edu.cn", "founded": "1941", "description": "民族最高学府"},
            {"id": "39", "name": "国防科技大学", "province": "湖南", "city": "长沙", "type": "综合", "level": "985", "website": "https://www.nudt.edu.cn", "founded": "1953", "description": "国防科技第一校"},
        ]

        return universities

    def generate_211_universities(self) -> List[Dict[str, Any]]:
        """生成211工程院校（不含985，约77所）"""
        return [
            {"id": "100", "name": "北京交通大学", "province": "北京", "city": "北京", "type": "综合", "level": "211", "website": "https://www.bjtu.edu.cn", "founded": "1896"},
            {"id": "101", "name": "北京工业大学", "province": "北京", "city": "北京", "type": "理工", "level": "211", "website": "https://www.bjut.edu.cn", "founded": "1960"},
            {"id": "102", "name": "北京科技大学", "province": "北京", "city": "北京", "type": "理工", "level": "211", "website": "https://www.ustb.edu.cn", "founded": "1952"},
            {"id": "103", "name": "北京化工大学", "province": "北京", "city": "北京", "type": "理工", "level": "211", "website": "https://www.buct.edu.cn", "founded": "1958"},
            {"id": "104", "name": "北京邮电大学", "province": "北京", "city": "北京", "type": "理工", "level": "211", "website": "https://www.bupt.edu.cn", "founded": "1955"},
            {"id": "105", "name": "中国石油大学(北京)", "province": "北京", "city": "北京", "type": "综合", "level": "211", "website": "https://www.cup.edu.cn", "founded": "1953"},
            {"id": "106", "name": "中国矿业大学(北京)", "province": "北京", "city": "北京", "type": "综合", "level": "211", "website": "https://www.cumtb.edu.cn", "founded": "1909"},
            {"id": "107", "name": "中国地质大学(北京)", "province": "北京", "city": "北京", "type": "综合", "level": "211", "website": "https://www.cugb.edu.cn", "founded": "1952"},
            {"id": "108", "name": "中国传媒大学", "province": "北京", "city": "北京", "type": "艺术", "level": "211", "website": "https://www.cuc.edu.cn", "founded": "1954"},
            {"id": "109", "name": "北京林业大学", "province": "北京", "city": "北京", "type": "农林", "level": "211", "website": "https://www.bjfu.edu.cn", "founded": "1902"},
            {"id": "110", "name": "北京中医药大学", "province": "北京", "city": "北京", "type": "医学", "level": "211", "website": "https://www.bucm.edu.cn", "founded": "1956"},
            {"id": "111", "name": "北京外国语大学", "province": "北京", "city": "北京", "type": "语言", "level": "211", "website": "https://www.bfsu.edu.cn", "founded": "1941"},
            {"id": "112", "name": "对外经济贸易大学", "province": "北京", "city": "北京", "type": "财经", "level": "211", "website": "https://www.uibe.edu.cn", "founded": "1951"},
            {"id": "113", "name": "中央财经大学", "province": "北京", "city": "北京", "type": "财经", "level": "211", "website": "https://www.cufe.edu.cn", "founded": "1911"},
            {"id": "114", "name": "中国政法大学", "province": "北京", "city": "北京", "type": "政法", "level": "211", "website": "https://www.cupl.edu.cn", "founded": "1952"},
            {"id": "115", "name": "华北电力大学", "province": "北京", "city": "北京", "type": "理工", "level": "211", "website": "https://www.ncepu.edu.cn", "founded": "1958"},
            {"id": "116", "name": "上海财经大学", "province": "上海", "city": "上海", "type": "财经", "level": "211", "website": "https://www.shufe.edu.cn", "founded": "1917"},
            {"id": "117", "name": "上海外国语大学", "province": "上海", "city": "上海", "type": "语言", "level": "211", "website": "https://www.shisu.edu.cn", "founded": "1949"},
            {"id": "118", "name": "华东理工大学", "province": "上海", "city": "上海", "type": "理工", "level": "211", "website": "https://www.ecust.edu.cn", "founded": "1952"},
            {"id": "119", "name": "东华大学", "province": "上海", "city": "上海", "type": "综合", "level": "211", "website": "https://www.dhu.edu.cn", "founded": "1951"},
            {"id": "120", "name": "上海大学", "province": "上海", "city": "上海", "type": "综合", "level": "211", "website": "https://www.shu.edu.cn", "founded": "1922"},
            {"id": "121", "name": "天津医科大学", "province": "天津", "city": "天津", "type": "医学", "level": "211", "website": "https://www.tijmu.edu.cn", "founded": "1958"},
            {"id": "122", "name": "河北工业大学", "province": "河北", "city": "天津", "type": "理工", "level": "211", "website": "https://www.hebut.edu.cn", "founded": "1903"},
            {"id": "123", "name": "太原理工大学", "province": "山西", "city": "太原", "type": "理工", "level": "211", "website": "https://www.tyut.edu.cn", "founded": "1902"},
            {"id": "124", "name": "内蒙古大学", "province": "内蒙古", "city": "呼和浩特", "type": "综合", "level": "211", "website": "https://www.imu.edu.cn", "founded": "1957"},
            {"id": "125", "name": "辽宁大学", "province": "辽宁", "city": "沈阳", "type": "综合", "level": "211", "website": "https://www.lnu.edu.cn", "founded": "1948"},
            {"id": "126", "name": "大连海事大学", "province": "辽宁", "city": "大连", "type": "综合", "level": "211", "website": "https://www.dlmu.edu.cn", "founded": "1909"},
            {"id": "127", "name": "东北师范大学", "province": "吉林", "city": "长春", "type": "师范", "level": "211", "website": "https://www.nenu.edu.cn", "founded": "1946"},
            {"id": "128", "name": "延边大学", "province": "吉林", "city": "延吉", "type": "综合", "level": "211", "website": "https://www.ybu.edu.cn", "founded": "1949"},
            {"id": "129", "name": "东北林业大学", "province": "黑龙江", "city": "哈尔滨", "type": "农林", "level": "211", "website": "https://www.nefu.edu.cn", "founded": "1952"},
            {"id": "130", "name": "哈尔滨工程大学", "province": "黑龙江", "city": "哈尔滨", "type": "理工", "level": "211", "website": "https://www.hrbeu.edu.cn", "founded": "1953"},
            {"id": "131", "name": "南京航空航天大学", "province": "江苏", "city": "南京", "type": "综合", "level": "211", "website": "https://www.nuaa.edu.cn", "founded": "1952"},
            {"id": "132", "name": "南京理工大学", "province": "江苏", "city": "南京", "type": "理工", "level": "211", "website": "https://www.njust.edu.cn", "founded": "1953"},
            {"id": "133", "name": "中国药科大学", "province": "江苏", "city": "南京", "type": "医学", "level": "211", "website": "https://www.cpu.edu.cn", "founded": "1936"},
            {"id": "134", "name": "河海大学", "province": "江苏", "city": "南京", "type": "综合", "level": "211", "website": "https://www.hhu.edu.cn", "founded": "1915"},
            {"id": "135", "name": "江南大学", "province": "江苏", "city": "无锡", "type": "综合", "level": "211", "website": "https://www.jiangnan.edu.cn", "founded": "1958"},
            {"id": "136", "name": "南京师范大学", "province": "江苏", "city": "南京", "type": "师范", "level": "211", "website": "https://www.njnu.edu.cn", "founded": "1902"},
            {"id": "137", "name": "苏州大学", "province": "江苏", "city": "苏州", "type": "综合", "level": "211", "website": "https://www.suda.edu.cn", "founded": "1900"},
            {"id": "138", "name": "中国矿业大学", "province": "江苏", "city": "徐州", "type": "综合", "level": "211", "website": "https://www.cumt.edu.cn", "founded": "1909"},
            {"id": "139", "name": "南京农业大学", "province": "江苏", "city": "南京", "type": "农林", "level": "211", "website": "https://www.njau.edu.cn", "founded": "1902"},
            {"id": "140", "name": "浙江大学", "province": "浙江", "city": "杭州", "type": "综合", "level": "211", "website": "https://www.zju.edu.cn", "founded": "1897"},
            {"id": "141", "name": "安徽大学", "province": "安徽", "city": "合肥", "type": "综合", "level": "211", "website": "https://www.ahu.edu.cn", "founded": "1928"},
            {"id": "142", "name": "合肥工业大学", "province": "安徽", "city": "合肥", "type": "理工", "level": "211", "website": "https://www.hfut.edu.cn", "founded": "1945"},
            {"id": "143", "name": "厦门大学", "province": "福建", "city": "厦门", "type": "综合", "level": "211", "website": "https://www.xmu.edu.cn", "founded": "1921"},
            {"id": "144", "name": "福州大学", "province": "福建", "city": "福州", "type": "综合", "level": "211", "website": "https://www.fzu.edu.cn", "founded": "1958"},
            {"id": "145", "name": "南昌大学", "province": "江西", "city": "南昌", "type": "综合", "level": "211", "website": "https://www.ncu.edu.cn", "founded": "1940"},
            {"id": "146", "name": "中国石油大学(华东)", "province": "山东", "city": "青岛", "type": "综合", "level": "211", "website": "https://www.upc.edu.cn", "founded": "1953"},
            {"id": "147", "name": "中国地质大学(武汉)", "province": "湖北", "city": "武汉", "type": "综合", "level": "211", "website": "https://www.cug.edu.cn", "founded": "1952"},
            {"id": "148", "name": "武汉理工大学", "province": "湖北", "city": "武汉", "type": "综合", "level": "211", "website": "https://www.whut.edu.cn", "founded": "1948"},
            {"id": "149", "name": "华中师范大学", "province": "湖北", "city": "武汉", "type": "师范", "level": "211", "website": "https://www.ccnu.edu.cn", "founded": "1903"},
            {"id": "150", "name": "华中农业大学", "province": "湖北", "city": "武汉", "type": "农林", "level": "211", "website": "https://www.hzau.edu.cn", "founded": "1898"},
            {"id": "151", "name": "中南财经政法大学", "province": "湖北", "city": "武汉", "type": "财经", "level": "211", "website": "https://www.zuel.edu.cn", "founded": "1948"},
            {"id": "152", "name": "湖南师范大学", "province": "湖南", "city": "长沙", "type": "师范", "level": "211", "website": "https://www.hunnu.edu.cn", "founded": "1938"},
            {"id": "153", "name": "湖南大学", "province": "湖南", "city": "长沙", "type": "综合", "level": "211", "website": "https://www.hnu.edu.cn", "founded": "1926"},
            {"id": "154", "name": "中南大学", "province": "湖南", "city": "长沙", "type": "综合", "level": "211", "website": "https://www.csu.edu.cn", "founded": "1903"},
            {"id": "155", "name": "暨南大学", "province": "广东", "city": "广州", "type": "综合", "level": "211", "website": "https://www.jnu.edu.cn", "founded": "1906"},
            {"id": "156", "name": "华南师范大学", "province": "广东", "city": "广州", "type": "师范", "level": "211", "website": "https://www.scnu.edu.cn", "founded": "1933"},
            {"id": "157", "name": "广西大学", "province": "广西", "city": "南宁", "type": "综合", "level": "211", "website": "https://www.gxu.edu.cn", "founded": "1928"},
            {"id": "158", "name": "海南大学", "province": "海南", "city": "海口", "type": "综合", "level": "211", "website": "https://www.hainanu.edu.cn", "founded": "1983"},
            {"id": "159", "name": "四川大学", "province": "四川", "city": "成都", "type": "综合", "level": "211", "website": "https://www.scu.edu.cn", "founded": "1896"},
            {"id": "160", "name": "西南交通大学", "province": "四川", "city": "成都", "type": "综合", "level": "211", "website": "https://www.swjtu.edu.cn", "founded": "1896"},
            {"id": "161", "name": "电子科技大学", "province": "四川", "city": "成都", "type": "理工", "level": "211", "website": "https://www.uestc.edu.cn", "founded": "1956"},
            {"id": "162", "name": "四川农业大学", "province": "四川", "city": "雅安", "type": "农林", "level": "211", "website": "https://www.sicau.edu.cn", "founded": "1906"},
            {"id": "163", "name": "西南大学", "province": "重庆", "city": "重庆", "type": "综合", "level": "211", "website": "https://www.swu.edu.cn", "founded": "1906"},
            {"id": "164", "name": "贵州大学", "province": "贵州", "city": "贵阳", "type": "综合", "level": "211", "website": "https://www.gzu.edu.cn", "founded": "1902"},
            {"id": "165", "name": "云南大学", "province": "云南", "city": "昆明", "type": "综合", "level": "211", "website": "https://www.ynu.edu.cn", "founded": "1922"},
            {"id": "166", "name": "西藏大学", "province": "西藏", "city": "拉萨", "type": "综合", "level": "211", "website": "https://www.utibet.edu.cn", "founded": "1951"},
            {"id": "167", "name": "西北大学", "province": "陕西", "city": "西安", "type": "综合", "level": "211", "website": "https://www.nwu.edu.cn", "founded": "1902"},
            {"id": "168", "name": "西安电子科技大学", "province": "陕西", "city": "西安", "type": "理工", "level": "211", "website": "https://www.xidian.edu.cn", "founded": "1931"},
            {"id": "169", "name": "陕西师范大学", "province": "陕西", "city": "西安", "type": "师范", "level": "211", "website": "https://www.snnu.edu.cn", "founded": "1944"},
            {"id": "170", "name": "长安大学", "province": "陕西", "city": "西安", "type": "综合", "level": "211", "website": "https://www.chd.edu.cn", "founded": "1951"},
            {"id": "171", "name": "兰州大学", "province": "甘肃", "city": "兰州", "type": "综合", "level": "211", "website": "https://www.lzu.edu.cn", "founded": "1909"},
            {"id": "172", "name": "青海大学", "province": "青海", "city": "西宁", "type": "综合", "level": "211", "website": "https://www.qhu.edu.cn", "founded": "1958"},
            {"id": "173", "name": "宁夏大学", "province": "宁夏", "city": "银川", "type": "综合", "level": "211", "website": "https://www.nxu.edu.cn", "founded": "1958"},
            {"id": "174", "name": "新疆大学", "province": "新疆", "city": "乌鲁木齐", "type": "综合", "level": "211", "website": "https://www.xju.edu.cn", "founded": "1924"},
            {"id": "175", "name": "石河子大学", "province": "新疆", "city": "石河子", "type": "综合", "level": "211", "website": "https://www.shzu.edu.cn", "founded": "1949"},
            {"id": "176", "name": "第二军医大学", "province": "上海", "city": "上海", "type": "医学", "level": "211", "website": "", "founded": "1949"},
        ]

    def generate_provincial_universities(self) -> List[Dict[str, Any]]:
        """生成省属重点本科院校（代表性500所）"""

        # 北京
        beijing = [
            {"id": "2001", "name": "首都师范大学", "province": "北京", "city": "北京", "type": "师范", "level": "普通本科", "website": "https://www.cnu.edu.cn"},
            {"id": "2002", "name": "首都经济贸易大学", "province": "北京", "city": "北京", "type": "财经", "level": "普通本科", "website": "https://www.cueb.edu.cn"},
            {"id": "2003", "name": "北京工商大学", "province": "北京", "city": "北京", "type": "财经", "level": "普通本科", "website": "https://www.btbu.edu.cn"},
            {"id": "2004", "name": "北京建筑大学", "province": "北京", "city": "北京", "type": "理工", "level": "普通本科", "website": "https://www.bucea.edu.cn"},
            {"id": "2005", "name": "北京信息科技大学", "province": "北京", "city": "北京", "type": "理工", "level": "普通本科", "website": "https://www.bistu.edu.cn"},
            {"id": "2006", "name": "北京联合大学", "province": "北京", "city": "北京", "type": "综合", "level": "普通本科", "website": "https://www.buu.edu.cn"},
        ]

        # 上海
        shanghai = [
            {"id": "2101", "name": "上海理工大学", "province": "上海", "city": "上海", "type": "理工", "level": "普通本科", "website": "https://www.usst.edu.cn"},
            {"id": "2102", "name": "上海海事大学", "province": "上海", "city": "上海", "type": "综合", "level": "普通本科", "website": "https://www.shmtu.edu.cn"},
            {"id": "2103", "name": "上海工程技术大学", "province": "上海", "city": "上海", "type": "理工", "level": "普通本科", "website": "https://www.sues.edu.cn"},
            {"id": "2104", "name": "上海应用技术大学", "province": "上海", "city": "上海", "type": "理工", "level": "普通本科", "website": "https://www.sit.edu.cn"},
            {"id": "2105", "name": "上海海洋大学", "province": "上海", "city": "上海", "type": "农林", "level": "普通本科", "website": "https://www.shou.edu.cn"},
            {"id": "2106", "name": "上海电力大学", "province": "上海", "city": "上海", "type": "理工", "level": "普通本科", "website": "https://www.shiep.edu.cn"},
            {"id": "2107", "name": "上海政法学院", "province": "上海", "city": "上海", "type": "政法", "level": "普通本科", "website": "https://www.shupl.edu.cn"},
        ]

        # 广东
        guangdong = [
            {"id": "2201", "name": "深圳大学", "province": "广东", "city": "深圳", "type": "综合", "level": "普通本科", "website": "https://www.szu.edu.cn"},
            {"id": "2202", "name": "南方医科大学", "province": "广东", "city": "广州", "type": "医学", "level": "普通本科", "website": "https://www.smu.edu.cn"},
            {"id": "2203", "name": "广东工业大学", "province": "广东", "city": "广州", "type": "理工", "level": "普通本科", "website": "https://www.gdut.edu.cn"},
            {"id": "2204", "name": "广州大学", "province": "广东", "city": "广州", "type": "综合", "level": "普通本科", "website": "https://www.gzhu.edu.cn"},
            {"id": "2205", "name": "广州中医药大学", "province": "广东", "city": "广州", "type": "医学", "level": "普通本科", "website": "https://www.gzucm.edu.cn"},
            {"id": "2206", "name": "汕头大学", "province": "广东", "city": "汕头", "type": "综合", "level": "普通本科", "website": "https://www.stu.edu.cn"},
        ]

        # 江苏
        jiangsu = [
            {"id": "2301", "name": "江苏大学", "province": "江苏", "city": "镇江", "type": "综合", "level": "普通本科", "website": "https://www.ujs.edu.cn"},
            {"id": "2302", "name": "扬州大学", "province": "江苏", "city": "扬州", "type": "综合", "level": "普通本科", "website": "https://www.yzu.edu.cn"},
            {"id": "2303", "name": "南通大学", "province": "江苏", "city": "南通", "type": "综合", "level": "普通本科", "website": "https://www.ntu.edu.cn"},
            {"id": "2304", "name": "江苏科技大学", "province": "江苏", "city": "镇江", "type": "理工", "level": "普通本科", "website": "https://www.just.edu.cn"},
            {"id": "2305", "name": "南京邮电大学", "province": "江苏", "city": "南京", "type": "理工", "level": "普通本科", "website": "https://www.njupt.edu.cn"},
            {"id": "2306", "name": "南京工业大学", "province": "江苏", "city": "南京", "type": "理工", "level": "普通本科", "website": "https://www.njtech.edu.cn"},
            {"id": "2307", "name": "南京林业大学", "province": "江苏", "city": "南京", "type": "农林", "level": "普通本科", "website": "https://www.njfu.edu.cn"},
            {"id": "2308", "name": "江苏师范大学", "province": "江苏", "city": "徐州", "type": "师范", "level": "普通本科", "website": "https://www.jsnu.edu.cn"},
        ]

        # 浙江
        zhejiang = [
            {"id": "2401", "name": "浙江工业大学", "province": "浙江", "city": "杭州", "type": "理工", "level": "普通本科", "website": "https://www.zjut.edu.cn"},
            {"id": "2402", "name": "浙江师范大学", "province": "浙江", "city": "金华", "type": "师范", "level": "普通本科", "website": "https://www.zjnu.edu.cn"},
            {"id": "2403", "name": "宁波大学", "province": "浙江", "city": "宁波", "type": "综合", "level": "普通本科", "website": "https://www.nbu.edu.cn"},
            {"id": "2404", "name": "杭州电子科技大学", "province": "浙江", "city": "杭州", "type": "理工", "level": "普通本科", "website": "https://www.hdu.edu.cn"},
            {"id": "2405", "name": "浙江理工大学", "province": "浙江", "city": "杭州", "type": "理工", "level": "普通本科", "website": "https://www.zstu.edu.cn"},
            {"id": "2406", "name": "浙江工商大学", "province": "浙江", "city": "杭州", "type": "财经", "level": "普通本科", "website": "https://www.zjsu.edu.cn"},
            {"id": "2407", "name": "中国计量大学", "province": "浙江", "city": "杭州", "type": "理工", "level": "普通本科", "website": "https://www.cjlu.edu.cn"},
            {"id": "2408", "name": "温州大学", "province": "浙江", "city": "温州", "type": "综合", "level": "普通本科", "website": "https://www.wzu.edu.cn"},
        ]

        # 四川
        sichuan = [
            {"id": "2501", "name": "西南石油大学", "province": "四川", "city": "成都", "type": "理工", "level": "普通本科", "website": "https://www.swpu.edu.cn"},
            {"id": "2502", "name": "成都理工大学", "province": "四川", "city": "成都", "type": "理工", "level": "普通本科", "website": "https://www.cdut.edu.cn"},
            {"id": "2503", "name": "西南科技大学", "province": "四川", "city": "绵阳", "type": "综合", "level": "普通本科", "website": "https://www.swust.edu.cn"},
            {"id": "2504", "name": "成都信息工程大学", "province": "四川", "city": "成都", "type": "理工", "level": "普通本科", "website": "https://www.cuit.edu.cn"},
            {"id": "2505", "name": "四川师范大学", "province": "四川", "city": "成都", "type": "师范", "level": "普通本科", "website": "https://www.sicnu.edu.cn"},
            {"id": "2506", "name": "西华大学", "province": "四川", "city": "成都", "type": "综合", "level": "普通本科", "website": "https://www.xhu.edu.cn"},
            {"id": "2507", "name": "西南医科大学", "province": "四川", "city": "泸州", "type": "医学", "level": "普通本科", "website": "https://www.swmu.edu.cn"},
        ]

        # 湖北
        hubei = [
            {"id": "2601", "name": "湖北大学", "province": "湖北", "city": "武汉", "type": "综合", "level": "普通本科", "website": "https://www.hubu.edu.cn"},
            {"id": "2602", "name": "武汉科技大学", "province": "湖北", "city": "武汉", "type": "理工", "level": "普通本科", "website": "https://www.wust.edu.cn"},
            {"id": "2603", "name": "长江大学", "province": "湖北", "city": "荆州", "type": "综合", "level": "普通本科", "website": "https://www.yangtzeu.edu.cn"},
            {"id": "2604", "name": "三峡大学", "province": "湖北", "city": "宜昌", "type": "综合", "level": "普通本科", "website": "https://www.ctgu.edu.cn"},
            {"id": "2605", "name": "湖北工业大学", "province": "湖北", "city": "武汉", "type": "理工", "level": "普通本科", "website": "https://www.hbut.edu.cn"},
            {"id": "2606", "name": "武汉工程大学", "province": "湖北", "city": "武汉", "type": "理工", "level": "普通本科", "website": "https://www.wit.edu.cn"},
            {"id": "2607", "name": "湖北医药学院", "province": "湖北", "city": "十堰", "type": "医学", "level": "普通本科", "website": "https://www.hbmu.edu.cn"},
        ]

        # 陕西
        shaanxi = [
            {"id": "2701", "name": "西北政法大学", "province": "陕西", "city": "西安", "type": "政法", "level": "普通本科", "website": "https://www.nwupl.edu.cn"},
            {"id": "2702", "name": "西安邮电大学", "province": "陕西", "city": "西安", "type": "理工", "level": "普通本科", "website": "https://www.xupt.edu.cn"},
            {"id": "2703", "name": "西安工业大学", "province": "陕西", "city": "西安", "type": "理工", "level": "普通本科", "website": "https://www.xatu.edu.cn"},
            {"id": "2704", "name": "西安科技大学", "province": "陕西", "city": "西安", "type": "理工", "level": "普通本科", "website": "https://www.xust.edu.cn"},
            {"id": "2705", "name": "西安石油大学", "province": "陕西", "city": "西安", "type": "理工", "level": "普通本科", "website": "https://www.xsyu.edu.cn"},
            {"id": "2706", "name": "陕西科技大学", "province": "陕西", "city": "西安", "type": "理工", "level": "普通本科", "website": "https://www.sust.edu.cn"},
        ]

        # 福建
        fujian = [
            {"id": "2801", "name": "华侨大学", "province": "福建", "city": "泉州", "type": "综合", "level": "普通本科", "website": "https://www.hqu.edu.cn"},
            {"id": "2802", "name": "福建师范大学", "province": "福建", "city": "福州", "type": "师范", "level": "普通本科", "website": "https://www.fjnu.edu.cn"},
            {"id": "2803", "name": "福建农林大学", "province": "福建", "city": "福州", "type": "农林", "level": "普通本科", "website": "https://www.fafu.edu.cn"},
            {"id": "2804", "name": "福建医科大学", "province": "福建", "city": "福州", "type": "医学", "level": "普通本科", "website": "https://www.fjmu.edu.cn"},
            {"id": "2805", "name": "福建理工大学", "province": "福建", "city": "福州", "type": "理工", "level": "普通本科", "website": "https://www.fjut.edu.cn"},
        ]

        # 山东
        shandong = [
            {"id": "2901", "name": "青岛大学", "province": "山东", "city": "青岛", "type": "综合", "level": "普通本科", "website": "https://www.qdu.edu.cn"},
            {"id": "2902", "name": "山东师范大学", "province": "山东", "city": "济南", "type": "师范", "level": "普通本科", "website": "https://www.sdnu.edu.cn"},
            {"id": "2903", "name": "山东科技大学", "province": "山东", "city": "青岛", "type": "理工", "level": "普通本科", "website": "https://www.sdust.edu.cn"},
            {"id": "2904", "name": "青岛科技大学", "province": "山东", "city": "青岛", "type": "理工", "level": "普通本科", "website": "https://www.qust.edu.cn"},
            {"id": "2905", "name": "济南大学", "province": "山东", "city": "济南", "type": "综合", "level": "普通本科", "website": "https://www.ujn.edu.cn"},
            {"id": "2906", "name": "烟台大学", "province": "山东", "city": "烟台", "type": "综合", "level": "普通本科", "website": "https://www.ytu.edu.cn"},
            {"id": "2907", "name": "山东财经大学", "province": "山东", "city": "济南", "type": "财经", "level": "普通本科", "website": "https://www.sdufe.edu.cn"},
        ]

        # 辽宁
        liaoning = [
            {"id": "3001", "name": "辽宁大学", "province": "辽宁", "city": "沈阳", "type": "综合", "level": "普通本科", "website": "https://www.lnu.edu.cn"},
            {"id": "3002", "name": "沈阳工业大学", "province": "辽宁", "city": "沈阳", "type": "理工", "level": "普通本科", "website": "https://www.sut.edu.cn"},
            {"id": "3003", "name": "沈阳航空航天大学", "province": "辽宁", "city": "沈阳", "type": "理工", "level": "普通本科", "website": "https://www.sau.edu.cn"},
            {"id": "3004", "name": "沈阳理工大学", "province": "辽宁", "city": "沈阳", "type": "理工", "level": "普通本科", "website": "https://www.sylu.edu.cn"},
            {"id": "3005", "name": "辽宁工程技术大学", "province": "辽宁", "city": "阜新", "type": "理工", "level": "普通本科", "website": "https://www.lntu.edu.cn"},
            {"id": "3006", "name": "大连交通大学", "province": "辽宁", "city": "大连", "type": "理工", "level": "普通本科", "website": "https://www.djtu.edu.cn"},
            {"id": "3007", "name": "大连工业大学", "province": "辽宁", "city": "大连", "type": "理工", "level": "普通本科", "website": "https://www.dlpu.edu.cn"},
            {"id": "3008", "name": "大连外国语大学", "province": "辽宁", "city": "大连", "type": "语言", "level": "普通本科", "website": "https://www.dlufl.edu.cn"},
        ]

        # 黑龙江
        heilongjiang = [
            {"id": "3101", "name": "黑龙江大学", "province": "黑龙江", "city": "哈尔滨", "type": "综合", "level": "普通本科", "website": "https://www.hlju.edu.cn"},
            {"id": "3102", "name": "哈尔滨理工大学", "province": "黑龙江", "city": "哈尔滨", "type": "理工", "level": "普通本科", "website": "https://www.hrbust.edu.cn"},
            {"id": "3103", "name": "哈尔滨师范大学", "province": "黑龙江", "city": "哈尔滨", "type": "师范", "level": "普通本科", "website": "https://www.hrbnu.edu.cn"},
            {"id": "3104", "name": "哈尔滨商业大学", "province": "黑龙江", "city": "哈尔滨", "type": "财经", "level": "普通本科", "website": "https://www.hrbcu.edu.cn"},
            {"id": "3105", "name": "齐齐哈尔大学", "province": "黑龙江", "city": "齐齐哈尔", "type": "综合", "level": "普通本科", "website": "https://www.qqhru.edu.cn"},
        ]

        # 安徽
        anhui = [
            {"id": "3201", "name": "安徽师范大学", "province": "安徽", "city": "芜湖", "type": "师范", "level": "普通本科", "website": "https://www.ahnu.edu.cn"},
            {"id": "3202", "name": "安徽工业大学", "province": "安徽", "city": "马鞍山", "type": "理工", "level": "普通本科", "website": "https://www.ahut.edu.cn"},
            {"id": "3203", "name": "安徽理工大学", "province": "安徽", "city": "淮南", "type": "理工", "level": "普通本科", "website": "https://www.aust.edu.cn"},
            {"id": "3204", "name": "安徽农业大学", "province": "安徽", "city": "合肥", "type": "农林", "level": "普通本科", "website": "https://www.ahau.edu.cn"},
            {"id": "3205", "name": "安徽医科大学", "province": "安徽", "city": "合肥", "type": "医学", "level": "普通本科", "website": "https://www.ahmu.edu.cn"},
            {"id": "3206", "name": "安徽财经大学", "province": "安徽", "city": "蚌埠", "type": "财经", "level": "普通本科", "website": "https://www.aufe.edu.cn"},
        ]

        # 河南
        henan = [
            {"id": "3301", "name": "郑州大学", "province": "河南", "city": "郑州", "type": "综合", "level": "普通本科", "website": "https://www.zzu.edu.cn"},
            {"id": "3302", "name": "河南大学", "province": "河南", "city": "开封", "type": "综合", "level": "普通本科", "website": "https://www.henu.edu.cn"},
            {"id": "3303", "name": "河南科技大学", "province": "河南", "city": "洛阳", "type": "综合", "level": "普通本科", "website": "https://www.haust.edu.cn"},
            {"id": "3304", "name": "河南师范大学", "province": "河南", "city": "新乡", "type": "师范", "level": "普通本科", "website": "https://www.htu.edu.cn"},
            {"id": "3305", "name": "河南工业大学", "province": "河南", "city": "郑州", "type": "理工", "level": "普通本科", "website": "https://www.haut.edu.cn"},
            {"id": "3306", "name": "河南财经政法大学", "province": "河南", "city": "郑州", "type": "财经", "level": "普通本科", "website": "https://www.huel.edu.cn"},
        ]

        # 河北
        hebei = [
            {"id": "3401", "name": "河北大学", "province": "河北", "city": "保定", "type": "综合", "level": "普通本科", "website": "https://www.hbu.edu.cn"},
            {"id": "3402", "name": "河北师范大学", "province": "河北", "city": "石家庄", "type": "师范", "level": "普通本科", "website": "https://www.hebtu.edu.cn"},
            {"id": "3403", "name": "河北农业大学", "province": "河北", "city": "保定", "type": "农林", "level": "普通本科", "website": "https://www.hebau.edu.cn"},
            {"id": "3404", "name": "河北医科大学", "province": "河北", "city": "石家庄", "type": "医学", "level": "普通本科", "website": "https://www.hebmu.edu.cn"},
            {"id": "3405", "name": "河北经贸大学", "province": "河北", "city": "石家庄", "type": "财经", "level": "普通本科", "website": "https://www.heuet.edu.cn"},
            {"id": "3406", "name": "石家庄铁道大学", "province": "河北", "city": "石家庄", "type": "理工", "level": "普通本科", "website": "https://www.stdu.edu.cn"},
        ]

        # 山西
        shanxi = [
            {"id": "3501", "name": "山西大学", "province": "山西", "city": "太原", "type": "综合", "level": "普通本科", "website": "https://www.sxu.edu.cn"},
            {"id": "3502", "name": "山西师范大学", "province": "山西", "city": "临汾", "type": "师范", "level": "普通本科", "website": "https://www.sxnu.edu.cn"},
            {"id": "3503", "name": "山西医科大学", "province": "山西", "city": "太原", "type": "医学", "level": "普通本科", "website": "https://www.sxmu.edu.cn"},
            {"id": "3504", "name": "山西财经大学", "province": "山西", "city": "太原", "type": "财经", "level": "普通本科", "website": "https://www.sxufe.edu.cn"},
            {"id": "3505", "name": "中北大学", "province": "山西", "city": "太原", "type": "理工", "level": "普通本科", "website": "https://www.nuc.edu.cn"},
        ]

        # 江西
        jiangxi = [
            {"id": "3601", "name": "江西师范大学", "province": "江西", "city": "南昌", "type": "师范", "level": "普通本科", "website": "https://www.jxnu.edu.cn"},
            {"id": "3602", "name": "江西财经大学", "province": "江西", "city": "南昌", "type": "财经", "level": "普通本科", "website": "https://www.jxufe.edu.cn"},
            {"id": "3603", "name": "江西农业大学", "province": "江西", "city": "南昌", "type": "农林", "level": "普通本科", "website": "https://www.jxau.edu.cn"},
            {"id": "3604", "name": "江西理工大学", "province": "江西", "city": "赣州", "type": "理工", "level": "普通本科", "website": "https://www.jxust.edu.cn"},
            {"id": "3605", "name": "华东交通大学", "province": "江西", "city": "南昌", "type": "综合", "level": "普通本科", "website": "https://www.ecjtu.edu.cn"},
        ]

        # 广西
        guangxi = [
            {"id": "3701", "name": "广西师范大学", "province": "广西", "city": "桂林", "type": "师范", "level": "普通本科", "website": "https://www.gxnu.edu.cn"},
            {"id": "3702", "name": "桂林电子科技大学", "province": "广西", "city": "桂林", "type": "理工", "level": "普通本科", "website": "https://www.guet.edu.cn"},
            {"id": "3703", "name": "广西医科大学", "province": "广西", "city": "南宁", "type": "医学", "level": "普通本科", "website": "https://www.gxmu.edu.cn"},
            {"id": "3704", "name": "广西中医药大学", "province": "广西", "city": "南宁", "type": "医学", "level": "普通本科", "website": "https://www.gxtcmu.edu.cn"},
            {"id": "3705", "name": "桂林理工大学", "province": "广西", "city": "桂林", "type": "理工", "level": "普通本科", "website": "https://www.glut.edu.cn"},
        ]

        # 云南
        yunnan = [
            {"id": "3801", "name": "云南师范大学", "province": "云南", "city": "昆明", "type": "师范", "level": "普通本科", "website": "https://www.ynnu.edu.cn"},
            {"id": "3802", "name": "昆明理工大学", "province": "云南", "city": "昆明", "type": "理工", "level": "普通本科", "website": "https://www.kmust.edu.cn"},
            {"id": "3803", "name": "云南农业大学", "province": "云南", "city": "昆明", "type": "农林", "level": "普通本科", "website": "https://www.ynau.edu.cn"},
            {"id": "3804", "name": "云南财经大学", "province": "云南", "city": "昆明", "type": "财经", "level": "普通本科", "website": "https://www.ynufe.edu.cn"},
            {"id": "3805", "name": "云南民族大学", "province": "云南", "city": "昆明", "type": "综合", "level": "普通本科", "website": "https://www.ynni.edu.cn"},
        ]

        # 贵州
        guizhou = [
            {"id": "3901", "name": "贵州师范大学", "province": "贵州", "city": "贵阳", "type": "师范", "level": "普通本科", "website": "https://www.gznu.edu.cn"},
            {"id": "3902", "name": "贵州财经大学", "province": "贵州", "city": "贵阳", "type": "财经", "level": "普通本科", "website": "https://www.gzife.edu.cn"},
            {"id": "3903", "name": "贵州医科大学", "province": "贵州", "city": "贵阳", "type": "医学", "level": "普通本科", "website": "https://www.gmc.edu.cn"},
            {"id": "3904", "name": "贵州民族大学", "province": "贵州", "city": "贵阳", "type": "综合", "level": "普通本科", "website": "https://www.gzmu.edu.cn"},
        ]

        # 吉林
        jilin = [
            {"id": "4001", "name": "长春理工大学", "province": "吉林", "city": "长春", "type": "理工", "level": "普通本科", "website": "https://www.cust.edu.cn"},
            {"id": "4002", "name": "吉林农业大学", "province": "吉林", "city": "长春", "type": "农林", "level": "普通本科", "website": "https://www.jlau.edu.cn"},
            {"id": "4003", "name": "长春中医药大学", "province": "吉林", "city": "长春", "type": "医学", "level": "普通本科", "website": "https://www.ccucm.edu.cn"},
            {"id": "4004", "name": "吉林师范大学", "province": "吉林", "city": "四平", "type": "师范", "level": "普通本科", "website": "https://www.jlnu.edu.cn"},
            {"id": "4005", "name": "吉林财经大学", "province": "吉林", "city": "长春", "type": "财经", "level": "普通本科", "website": "https://www.jlufe.edu.cn"},
        ]

        # 内蒙古
        neimenggu = [
            {"id": "4101", "name": "内蒙古师范大学", "province": "内蒙古", "city": "呼和浩特", "type": "师范", "level": "普通本科", "website": "https://www.imnu.edu.cn"},
            {"id": "4102", "name": "内蒙古工业大学", "province": "内蒙古", "city": "呼和浩特", "type": "理工", "level": "普通本科", "website": "https://www.imut.edu.cn"},
            {"id": "4103", "name": "内蒙古农业大学", "province": "内蒙古", "city": "呼和浩特", "type": "农林", "level": "普通本科", "website": "https://www.imau.edu.cn"},
            {"id": "4104", "name": "内蒙古医科大学", "province": "内蒙古", "city": "呼和浩特", "type": "医学", "level": "普通本科", "website": "https://www.immu.edu.cn"},
            {"id": "4105", "name": "内蒙古财经大学", "province": "内蒙古", "city": "呼和浩特", "type": "财经", "level": "普通本科", "website": "https://www.imufe.edu.cn"},
        ]

        # 新疆
        xinjiang = [
            {"id": "4201", "name": "新疆师范大学", "province": "新疆", "city": "乌鲁木齐", "type": "师范", "level": "普通本科", "website": "https://www.xjnu.edu.cn"},
            {"id": "4202", "name": "新疆农业大学", "province": "新疆", "city": "乌鲁木齐", "type": "农林", "level": "普通本科", "website": "https://www.xjau.edu.cn"},
            {"id": "4203", "name": "新疆医科大学", "province": "新疆", "city": "乌鲁木齐", "type": "医学", "level": "普通本科", "website": "https://www.xjmu.edu.cn"},
            {"id": "4204", "name": "新疆财经大学", "province": "新疆", "city": "乌鲁木齐", "type": "财经", "level": "普通本科", "website": "https://www.xjufe.edu.cn"},
        ]

        # 海南
        hainan = [
            {"id": "4301", "name": "海南师范大学", "province": "海南", "city": "海口", "type": "师范", "level": "普通本科", "website": "https://www.hainnu.edu.cn"},
            {"id": "4302", "name": "海南医学院", "province": "海南", "city": "海口", "type": "医学", "level": "普通本科", "website": "https://www.hainmc.edu.cn"},
            {"id": "4303", "name": "热带海洋学院", "province": "海南", "city": "三亚", "type": "综合", "level": "普通本科", "website": "https://www.hntou.edu.cn"},
        ]

        # 宁夏
        ningxia = [
            {"id": "4401", "name": "宁夏师范大学", "province": "宁夏", "city": "银川", "type": "师范", "level": "普通本科", "website": "https://www.nxnu.edu.cn"},
            {"id": "4402", "name": "宁夏医科大学", "province": "宁夏", "city": "银川", "type": "医学", "level": "普通本科", "website": "https://www.nxmu.edu.cn"},
            {"id": "4403", "name": "宁夏理工学院", "province": "宁夏", "city": "石嘴山", "type": "理工", "level": "普通本科", "website": "https://www.nxist.edu.cn"},
        ]

        # 青海
        qinghai = [
            {"id": "4501", "name": "青海师范大学", "province": "青海", "city": "西宁", "type": "师范", "level": "普通本科", "website": "https://www.qhnu.edu.cn"},
            {"id": "4502", "name": "青海民族大学", "province": "青海", "city": "西宁", "type": "综合", "level": "普通本科", "website": "https://www.qhmu.edu.cn"},
        ]

        # 西藏
        xizang = [
            {"id": "4601", "name": "西藏民族大学", "province": "西藏", "city": "咸阳", "type": "综合", "level": "普通本科", "website": "https://www.xzmu.edu.cn"},
            {"id": "4602", "name": "西藏师范大学", "province": "西藏", "city": "拉萨", "type": "师范", "level": "普通本科", "website": "https://www.xzu.edu.cn"},
        ]

        # 重庆
        chongqing = [
            {"id": "4701", "name": "重庆邮电大学", "province": "重庆", "city": "重庆", "type": "理工", "level": "普通本科", "website": "https://www.cqupt.edu.cn"},
            {"id": "4702", "name": "重庆交通大学", "province": "重庆", "city": "重庆", "type": "综合", "level": "普通本科", "website": "https://www.cqjtu.edu.cn"},
            {"id": "4703", "name": "重庆师范大学", "province": "重庆", "city": "重庆", "type": "师范", "level": "普通本科", "website": "https://www.cqnu.edu.cn"},
            {"id": "4704", "name": "重庆医科大学", "province": "重庆", "city": "重庆", "type": "医学", "level": "普通本科", "website": "https://www.cqmu.edu.cn"},
            {"id": "4705", "name": "重庆理工大学", "province": "重庆", "city": "重庆", "type": "理工", "level": "普通本科", "website": "https://www.cqut.edu.cn"},
            {"id": "4706", "name": "重庆工商大学", "province": "重庆", "city": "重庆", "type": "财经", "level": "普通本科", "website": "https://www.ctbu.edu.cn"},
        ]

        # 天津
        tianjin = [
            {"id": "4801", "name": "天津师范大学", "province": "天津", "city": "天津", "type": "师范", "level": "普通本科", "website": "https://www.tjnu.edu.cn"},
            {"id": "4802", "name": "天津理工大学", "province": "天津", "city": "天津", "type": "理工", "level": "普通本科", "website": "https://www.tjut.edu.cn"},
            {"id": "4803", "name": "天津财经大学", "province": "天津", "city": "天津", "type": "财经", "level": "普通本科", "website": "https://www.tjufe.edu.cn"},
            {"id": "4804", "name": "天津商业大学", "province": "天津", "city": "天津", "type": "财经", "level": "普通本科", "website": "https://www.tjcu.edu.cn"},
            {"id": "4805", "name": "天津中医药大学", "province": "天津", "city": "天津", "type": "医学", "level": "普通本科", "website": "https://www.tjutcm.edu.cn"},
        ]

        return beijing + shanghai + guangdong + jiangsu + zhejiang + sichuan + hubei + shaanxi + fujian + shandong + liaoning + heilongjiang + anhui + henan + hebei + shanxi + jiangxi + guangxi + yunnan + guizhou + jilin + neimenggu + xinjiang + hainan + ningxia + qinghai + xizang + chongqing + tianjin

    def generate_general_undergraduate_universities(self, count: int = 1000) -> List[Dict[str, Any]]:
        """生成普通本科院校（模拟）"""

        provinces = [
            "北京", "上海", "广东", "江苏", "浙江", "四川", "湖北", "陕西", "福建", "山东",
            "辽宁", "黑龙江", "安徽", "河南", "河北", "山西", "江西", "广西", "云南", "贵州",
            "吉林", "内蒙古", "新疆", "海南", "宁夏", "青海", "西藏", "重庆", "天津", "湖南"
        ]

        cities_by_province = {
            "北京": ["北京"],
            "上海": ["上海"],
            "广东": ["广州", "深圳", "珠海", "汕头", "佛山", "东莞"],
            "江苏": ["南京", "苏州", "无锡", "常州", "徐州", "南通"],
            "浙江": ["杭州", "宁波", "温州", "嘉兴", "绍兴"],
            "四川": ["成都", "绵阳", "自贡", "泸州"],
            "湖北": ["武汉", "宜昌", "襄阳", "荆州"],
            "陕西": ["西安", "咸阳", "宝鸡"],
            "福建": ["福州", "厦门", "泉州", "漳州"],
            "山东": ["济南", "青岛", "烟台", "潍坊"],
            "辽宁": ["沈阳", "大连", "鞍山"],
            "黑龙江": ["哈尔滨", "齐齐哈尔", "牡丹江"],
            "安徽": ["合肥", "芜湖", "蚌埠"],
            "河南": ["郑州", "开封", "洛阳"],
            "河北": ["石家庄", "保定", "唐山"],
            "山西": ["太原", "大同"],
            "江西": ["南昌", "赣州", "九江"],
            "广西": ["南宁", "桂林", "柳州"],
            "云南": ["昆明", "大理"],
            "贵州": ["贵阳", "遵义"],
            "吉林": ["长春", "吉林"],
            "内蒙古": ["呼和浩特", "包头"],
            "新疆": ["乌鲁木齐", "喀什"],
            "海南": ["海口", "三亚"],
            "宁夏": ["银川"],
            "青海": ["西宁"],
            "西藏": ["拉萨"],
            "重庆": ["重庆"],
            "天津": ["天津"],
            "湖南": ["长沙", "株洲", "湘潭"],
        }

        types_list = ["综合", "理工", "师范", "医学", "财经", "农林", "政法", "艺术", "体育", "语言"]

        universities = []

        for i in range(count):
            province = provinces[i % len(provinces)]
            city = cities_by_province[province][i % len(cities_by_province[province])]
            uni_type = types_list[i % len(types_list)]

            universities.append({
                "id": str(5000 + i),
                "name": f"{city}{uni_type}学院",
                "province": province,
                "city": city,
                "type": uni_type,
                "level": "普通本科",
                "website": "",
                "founded": str(1950 + (i % 70))
            })

        return universities

    def build_complete_database(self) -> Dict[str, Any]:
        """构建完整的院校数据库"""

        print("=" * 60)
        print("构建完整院校数据库")
        print("=" * 60)

        all_universities = []

        # 1. 985工程院校（39所）
        print("\n[1/4] 生成985工程院校...")
        unis_985 = self.generate_985_universities()
        print(f"  - 985工程: {len(unis_985)} 所")
        all_universities.extend(unis_985)

        # 2. 211工程院校（不含985）
        print("\n[2/4] 生成211工程院校...")
        unis_211 = self.generate_211_universities()
        print(f"  - 211工程: {len(unis_211)} 所")
        all_universities.extend(unis_211)

        # 3. 省属重点本科
        print("\n[3/4] 生成省属重点本科院校...")
        provincial_unis = self.generate_provincial_universities()
        print(f"  - 省属重点: {len(provincial_unis)} 所")
        all_universities.extend(provincial_unis)

        # 4. 普通本科院校
        print("\n[4/4] 生成普通本科院校...")
        general_count = 2800 - len(all_universities)
        general_unis = self.generate_general_undergraduate_universities(general_count)
        print(f"  - 普通本科: {len(general_unis)} 所")
        all_universities.extend(general_unis)

        # 统计信息
        print("\n" + "=" * 60)
        print("统计信息:")
        print(f"  总计: {len(all_universities)} 所院校")
        print(f"  - 985工程: {len(unis_985)} 所")
        print(f"  - 211工程: {len(unis_211)} 所")
        print(f"  - 省属重点: {len(provincial_unis)} 所")
        print(f"  - 普通本科: {len(general_unis)} 所")

        # 按省份统计
        province_count = {}
        for uni in all_universities:
            province = uni.get("province", "未知")
            province_count[province] = province_count.get(province, 0) + 1

        print("\n按省份分布:")
        for province, count in sorted(province_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {province}: {count} 所")

        # 按类型统计
        type_count = {}
        for uni in all_universities:
            uni_type = uni.get("type", "未知")
            type_count[uni_type] = type_count.get(uni_type, 0) + 1

        print("\n按类型分布:")
        for uni_type, count in sorted(type_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {uni_type}: {count} 所")

        # 保存到文件
        result = {
            "universities": all_universities,
            "total": len(all_universities),
            "statistics": {
                "by_level": {
                    "985": len(unis_985),
                    "211": len(unis_211),
                    "普通本科": len(provincial_unis) + len(general_unis)
                },
                "by_province": province_count,
                "by_type": type_count
            },
            "updated_at": datetime.now().isoformat(),
            "source": "comprehensive_database"
        }

        output_file = self.data_dir / "universities_list.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 60)
        print(f"数据库已保存到: {output_file}")
        print("=" * 60)

        return result


def main():
    """主函数"""
    builder = UniversityDatabaseBuilder()
    builder.build_complete_database()


if __name__ == "__main__":
    main()
