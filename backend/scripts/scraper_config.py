#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2025广东高考投档线采集系统配置文件
"""

# 数据源配置
DATA_SOURCES = {
    'gaokao_cn': {
        'name': '高考直通车',
        'base_url': 'https://www.gaokao.cn',
        'priority': 2,
        'enabled': True,
        'possible_apis': [
            'https://api.gaokao.cn/admission/guangdong/2025/undergraduate',
            'https://www.gaokao.cn/api/college/query',
            'https://static.gaokao.cn/wwwdata/guangdong-2025.json',
        ]
    },
    'gaokaopai': {
        'name': '掌上高考',
        'base_url': 'https://www.gaokaopai.com',
        'priority': 3,
        'enabled': True,
        'possible_apis': [
            'https://www.gaokaopai.com/api/admission',
            'https://api.gaokaopai.com/batch/query',
        ]
    },
    'eol': {
        'name': '中国教育在线',
        'base_url': 'https://www.eol.cn',
        'priority': 4,
        'enabled': True,
        'possible_apis': [
            'https://www.eol.cn/api/guangdong/2025/score',
        ]
    },
    'official': {
        'name': '广东省教育考试院',
        'base_url': 'https://eea.gd.gov.cn',
        'priority': 1,
        'enabled': True,
        'possible_apis': []
    }
}

# 采集配置
SCRAPER_CONFIG = {
    'timeout': 30,  # 请求超时时间（秒）
    'retry_times': 3,  # 重试次数
    'delay_between_requests': 1,  # 请求间隔（秒）
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

# 科类配置
CATEGORIES = {
    'physics': '物理',
    'history': '历史'
}

# 数据字段映射
FIELD_MAPPING = {
    # 通用字段
    'university': ['院校名称', '学校名称', '院校', '学校', 'college', 'university'],
    'category': ['科类', '类别', 'category', 'type'],
    'group_code': ['专业组代码', '专业组', 'group_code', 'group'],
    'min_score': ['最低分', '投档分', '分数', 'score', 'min_score'],
    'min_rank': ['最低排位', '排位', '位次', 'rank', 'min_rank', 'position'],

    # 可能的额外字段
    'university_code': ['院校代码', '学校代码', '代码'],
    'plan_count': ['计划数', '招生计划'],
    'actual_count': ['投档人数', '实际人数'],
}

# 数据验证规则
VALIDATION_RULES = {
    'score_range': (300, 750),  # 分数范围
    'rank_min': 1,  # 最小排位
    'rank_max': 500000,  # 最大排位
    'group_code_pattern': r'^\d{3}$',  # 专业组代码格式（3位数字）
}

# 输出配置
OUTPUT_CONFIG = {
    'output_dir': 'output',
    'csv_encoding': 'utf-8-sig',
    'excel_engine': 'openpyxl',
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'encoding': 'utf-8',
}

# 浏览器配置（用于Playwright）
BROWSER_CONFIG = {
    'headless': False,  # 是否无头模式
    'timeout': 30000,  # 页面加载超时（毫秒）
}

# 验证规则
VERIFICATION_CONFIG = {
    'min_sources': 2,  # 最少需要几个来源一致才标记为已验证
    'tolerance_score': 0,  # 分数容忍度（必须完全一致）
    'tolerance_rank': 0,  # 排位容忍度（必须完全一致）
}
