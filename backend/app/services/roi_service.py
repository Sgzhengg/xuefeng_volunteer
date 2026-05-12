# -*- coding: utf-8 -*-
"""
ROI（投资回报率）标签服务
为推荐结果添加ROI标签和值得指数计算
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class ROIService:
    """ROI标签服务"""

    def __init__(self):
        self.data_dir = Path("data")
        self._load_roi_data()
        self._load_university_data()

    def _load_university_data(self):
        """加载院校层次数据"""
        try:
            with open(self.data_dir / "universities_list.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.universities = {u['name']: u for u in data.get('universities', [])}
        except Exception as e:
            print(f"Warning: Could not load university data: {e}")
            self.universities = {}

    def _load_roi_data(self):
        """加载ROI标签数据"""
        try:
            with open(self.data_dir / "roi_tags.json", 'r', encoding='utf-8') as f:
                self.roi_data = json.load(f)
            print(f"[OK] ROI data loaded successfully: {len(self.roi_data)} categories")
        except Exception as e:
            print(f"[WARNING] ROI data loading failed: {e}")
            self.roi_data = {
                "high_return": {"majors": []},
                "low_return": {"majors": []},
                "civil_service_advantage": {"majors": []},
                "guangdong_demand": {"majors": []},
                "red_list": {"majors": []}
            }

    def get_major_roi_info(self, major_name: str) -> Dict[str, Any]:
        """
        获取专业的ROI信息

        返回格式:
        {
            "tags": ["[PROFIT]高回报", "[HOT]广东热门"],
            "hints": ["毕业起薪约15-20k，3年回本", "深圳、广州IT企业众多"],
            "is_high_return": true,
            "is_low_return": false,
            "has_civil_service_advantage": false
        }
        """
        result = {
            "tags": [],
            "hints": [],
            "is_high_return": False,
            "is_low_return": False,
            "has_civil_service_advantage": False,
            "is_guangdong_hot": False,
            "is_red_list": False
        }

        # 标准化专业名称
        major_normalized = major_name.strip()

        # 检查各个类别
        categories = [
            ("high_return", "is_high_return"),
            ("low_return", "is_low_return"),
            ("civil_service_advantage", "has_civil_service_advantage"),
            ("guangdong_demand", "is_guangdong_hot"),
            ("red_list", "is_red_list")
        ]

        for category_key, result_key in categories:
            category_data = self.roi_data.get(category_key, {})
            majors = category_data.get("majors", [])

            for major_info in majors:
                stored_major = major_info.get("name", "")
                # 模糊匹配
                if (major_normalized in stored_major or
                    stored_major in major_normalized or
                    self._is_major_alias(major_normalized, stored_major)):

                    # 添加标签
                    tag = category_data.get("tag", "")
                    if tag:
                        result["tags"].append(tag)

                    # 添加提示
                    hint = major_info.get("hint", "")
                    if hint:
                        result["hints"].append(hint)

                    # 设置标志
                    result[result_key] = True
                    break

        return result

    def _is_major_alias(self, major1: str, major2: str) -> bool:
        """检查两个专业名称是否是同一专业的不同称呼"""
        # 专业别称映射
        aliases = {
            "计算机": ["计算机科学与技术", "软件工程", "人工智能", "数据科学"],
            "软工": ["软件工程"],
            "人工智能": ["智能科学与技术"],
            "自动化": ["自动化", "机器人工程"],
            "电子": ["电子信息工程", "电子科学与技术", "通信工程"],
            "法学": ["法学", "法律"],
            "会计": ["会计学", "财务管理", "审计学"],
            "金融": ["金融学", "金融工程", "投资学"],
            "临床": ["临床医学"],
            "口腔": ["口腔医学"],
        }

        for key, values in aliases.items():
            if key in major1 and any(v in major2 for v in values):
                return True
            if key in major2 and any(v in major1 for v in values):
                return True

        return False

    def enrich_recommendation(
        self,
        recommendation_item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        为推荐结果添加ROI信息

        Args:
            recommendation_item: 单个推荐项

        Returns:
            添加了ROI信息的推荐项
        """
        major = recommendation_item.get("major", "")
        roi_info = self.get_major_roi_info(major)

        # 新增字段
        recommendation_item["roi_tags"] = roi_info["tags"]
        recommendation_item["roi_hint"] = roi_info["hints"][0] if roi_info["hints"] else None
        recommendation_item["is_high_return"] = roi_info["is_high_return"]
        recommendation_item["is_low_return"] = roi_info["is_low_return"]
        recommendation_item["has_civil_service_advantage"] = roi_info["has_civil_service_advantage"]
        recommendation_item["is_guangdong_hot"] = roi_info["is_guangdong_hot"]
        recommendation_item["is_red_list"] = roi_info["is_red_list"]

        return recommendation_item

    def get_red_list_majors(self) -> List[Dict[str, Any]]:
        """获取红牌专业列表（用于发现页面）"""
        red_list_data = self.roi_data.get("red_list", {})
        majors = red_list_data.get("majors", [])

        return [
            {
                "name": m.get("name", ""),
                "hint": m.get("hint", ""),
                "alternative": m.get("alternative", ""),
                "tag": red_list_data.get("tag", "🚫红牌专业")
            }
            for m in majors
        ]

    def get_guangdong_hot_majors(self) -> List[Dict[str, Any]]:
        """获取广东热门专业列表"""
        hot_data = self.roi_data.get("guangdong_demand", {})
        majors = hot_data.get("majors", [])

        return [
            {
                "name": m.get("name", ""),
                "hint": m.get("hint", ""),
                "tag": hot_data.get("tag", "[HOT]广东热门")
            }
            for m in majors
        ]

    def calculate_roi_score(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算推荐方案的值得指数（0-100分）

        考虑因素：
        1. 院校层次（0-30分）
        2. 专业就业前景（0-25分）
        3. 地理位置优势（0-20分）
        4. 院校特色加分（0-15分）
        5. 广东本地优势（0-10分）
        6. 红牌专业扣分（-30分）

        Args:
            recommendation: 推荐方案字典

        Returns:
            包含ROI相关字段的字典
        """
        university_name = recommendation.get('university_name', '')
        major = recommendation.get('major', '')
        province = recommendation.get('province', '')
        city = recommendation.get('city', '')
        university_type = recommendation.get('university_type', '')

        # 初始化ROI分数
        roi_score = 50  # 基础分
        reasons = []

        # 1. 院校层次评分 (0-30分)
        level_score, level_reason = self._calculate_university_level_score(university_type, university_name)
        roi_score += level_score
        reasons.append(level_reason)

        # 2. 专业就业评分 (0-25分)
        major_score, major_reason = self._calculate_major_employment_score(major)
        roi_score += major_score
        reasons.append(major_reason)

        # 3. 地理位置评分 (0-20分)
        location_score, location_reason = self._calculate_location_score(province, city)
        roi_score += location_score
        reasons.append(location_reason)

        # 4. 院校特色加分 (0-15分)
        feature_score, feature_reason = self._calculate_university_feature_score(university_name, major)
        roi_score += feature_score
        if feature_reason:
            reasons.append(feature_reason)

        # 5. 广东本地优势
        if province == '广东':
            roi_score += 5
            reasons.append("💼 广东本地就业优势")

        # 6. 红牌专业检测
        is_red_major = self._is_red_major(major)
        if is_red_major:
            roi_score = max(0, roi_score - 30)  # 红牌专业扣30分
            reasons.append("[WARN] 教育部红牌专业，就业率偏低")

        # 确保分数在0-100范围内
        roi_score = max(0, min(100, roi_score))

        # 确定等级和颜色
        roi_level, roi_color = self._get_roi_level(roi_score, is_red_major)

        return {
            'roi_score': roi_score,
            'roi_level': roi_level,
            'roi_color': roi_color,
            'roi_reason': '；'.join(reasons),
            'is_red_major': is_red_major
        }

    def _calculate_university_level_score(self, university_type: str, university_name: str) -> tuple:
        """计算院校层次分数"""
        # C9联盟院校
        c9_universities = ['北京大学', '清华大学', '复旦大学', '上海交通大学',
                          '浙江大学', '南京大学', '中国科学技术大学',
                          '西安交通大学', '哈尔滨工业大学']

        if university_name in c9_universities:
            return 30, "[TARGET] C9联盟院校，国内顶尖"

        if '985' in university_type:
            return 25, "[TOP] 985院校，国内一流"

        if '211' in university_type:
            return 20, "🎖️ 211院校，国内重点"

        if '重点' in university_type:
            return 15, "[STAR] 省属重点院校"

        if '本科' in university_type or '公办' in university_type:
            return 10, "📚 普通公办本科"

        if '高职' in university_type or '专科' in university_type:
            return 5, "[FIX] 高职专科院校"

        return 0, "📋 院校类型未知"

    def _calculate_major_employment_score(self, major: str) -> tuple:
        """计算专业就业分数"""
        # 计算机类专业（高就业率）
        if major in ['计算机科学与技术', '软件工程', '人工智能', '数据科学与大数据技术']:
            return 25, "[LAPTOP] 计算机类专业，就业前景广阔"

        # 电子信息类
        if major in ['电子信息工程', '通信工程', '微电子科学与工程']:
            return 23, "📡 电子信息类，科技行业需求大"

        # 医学类
        if major in ['临床医学', '口腔医学']:
            return 24, "[HOSPITAL] 医学类专业，就业稳定"

        # 金融类
        if major in ['金融学', '金融工程']:
            return 22, "[PROFIT] 金融类专业，高薪行业"

        # 工商管理类
        if major in ['会计学', '财务管理']:
            return 20, "[DATA] 财会类专业，就业稳定"

        # 电气工程
        if major == '电气工程及其自动化':
            return 21, "[FAST] 电气工程，电网就业机会多"

        # 普通工科
        if any(keyword in major for keyword in ['工程', '技术', '科学', '自动化']):
            return 15, "[FIX] 工科专业，技术就业面广"

        # 文科类
        if any(keyword in major for keyword in ['文学', '历史', '哲学', '社会学']):
            return 8, "📖 文科专业，就业面相对较窄"

        # 管理类
        if '管理' in major:
            return 12, "📋 管理类专业，就业一般"

        return 10, "📚 专业就业情况正常"

    def _calculate_location_score(self, province: str, city: str) -> tuple:
        """计算地理位置分数"""
        # 一线城市
        if city in ['北京', '上海', '广州', '深圳']:
            return 20, f"📍 {city}一线城市，实习就业机会多"

        # 新一线城市
        if city in ['杭州', '成都', '武汉', '西安', '南京', '重庆', '天津', '苏州']:
            return 15, f"📍 {city}新一线城市，发展潜力大"

        # 广东省内
        if province == '广东':
            return 12, "💼 广东本地，企业认可度高"

        # 经济发达省份
        if province in ['江苏', '浙江', '福建', '山东']:
            return 10, f"📍 {province}经济发达，就业环境好"

        return 5, "📍 地理位置一般"

    def _calculate_university_feature_score(self, university_name: str, major: str) -> tuple:
        """计算院校特色分数"""
        # 华为/腾讯目标院校
        target_universities = [
            '华南理工大学', '广东工业大学', '深圳大学',
            '中山大学', '暨南大学', '广州大学'
        ]

        if university_name in target_universities and '计算机' in major:
            return 15, "[DEPLOY] 华为/腾讯校招目标院校"

        # 行业特色院校
        features = {
            '两电一邮': ['电子科技大学', '西安电子科技大学', '北京邮电大学'],
            '建筑老八校': ['清华大学', '东南大学', '天津大学', '同济大学',
                          '华南理工大学', '哈尔滨工业大学', '重庆大学', '西安建筑科技大学'],
            '财经强校': ['上海财经大学', '中央财经大学', '西南财经大学', '中南财经政法大学']
        }

        for feature, unis in features.items():
            if university_name in unis:
                return 10, f"[TOP] {feature}，行业认可度高"

        return 0, ""

    def _is_red_major(self, major: str) -> bool:
        """判断是否为红牌专业"""
        red_majors = [
            '应用心理学', '公共事业管理', '法学', '汉语言文学', '英语',
            '历史学', '化学', '生物技术', '生物科学', '环境工程',
            '材料化学', '材料科学与工程', '旅游管理', '市场营销'
        ]

        # 精确匹配
        if major in red_majors:
            return True

        # 模糊匹配
        for red_major in red_majors:
            if red_major in major or major in red_major:
                return True

        return False

    def _get_roi_level(self, score: int, is_red_major: bool) -> tuple:
        """获取ROI等级和颜色"""
        if is_red_major:
            return '[WARN] 红牌专业', 'red'

        if score >= 80:
            return 'A级', 'green'
        elif score >= 60:
            return 'B级', 'blue'
        else:
            return 'C级', 'orange'

    def enrich_recommendation_with_roi_score(
        self,
        recommendation_item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        为推荐结果同时添加ROI标签和值得指数

        Args:
            recommendation_item: 单个推荐项

        Returns:
            添加了ROI信息的推荐项
        """
        # 添加ROI标签
        major = recommendation_item.get("major", "")
        roi_info = self.get_major_roi_info(major)

        recommendation_item["roi_tags"] = roi_info["tags"]
        recommendation_item["roi_hint"] = roi_info["hints"][0] if roi_info["hints"] else None
        recommendation_item["is_high_return"] = roi_info["is_high_return"]
        recommendation_item["is_low_return"] = roi_info["is_low_return"]
        recommendation_item["has_civil_service_advantage"] = roi_info["has_civil_service_advantage"]
        recommendation_item["is_guangdong_hot"] = roi_info["is_guangdong_hot"]
        recommendation_item["is_red_list"] = roi_info["is_red_list"]

        # 添加值得指数
        roi_score_data = self.calculate_roi_score(recommendation_item)
        recommendation_item.update(roi_score_data)

        return recommendation_item


# 全局实例
roi_service = ROIService()
