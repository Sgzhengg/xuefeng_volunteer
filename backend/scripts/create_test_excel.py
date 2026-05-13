#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试用Excel文件（仅用于验证系统功能）

注意：这是测试文件，包含少量示例数据，仅用于验证系统解析功能
实际使用时请使用广东省教育考试院发布的官方Excel文件
"""

import pandas as pd
from datetime import datetime

# 创建测试数据（仅用于验证系统功能）
test_data = {
    '院校代码': ['10561', '10561', '10558', '10558', '10559'],
    '院校名称': ['华南理工大学', '华南理工大学', '中山大学', '中山大学', '暨南大学'],
    '专业组代码': ['202', '203', '201', '202', '101'],
    '计划数': [60, 40, 100, 80, 120],
    '投档人数': [60, 40, 100, 80, 120],
    '最低分': [625, 618, 628, 620, 603],
    '最低排位': [8500, 10200, 7500, 9800, 15000]
}

# 创建DataFrame
df = pd.DataFrame(test_data)

# 保存为Excel
filename = f"test_guangdong_2025_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
df.to_excel(filename, index=False, engine='openpyxl')

print(f"测试Excel文件已创建: {filename}")
print("\n注意：这是测试文件，包含少量示例数据，仅用于验证系统解析功能")
print("实际使用时请使用广东省教育考试院发布的官方Excel文件")
print("\n使用方法：")
print(f"python fetch_real_guangdong_2025.py manual {filename}")
print("\n预期结果：")
print("由于测试文件只有5条记录，系统应该返回：")
print("INCOMPLETE_DATA: 只有 5 条记录，要求至少 3000 条")
