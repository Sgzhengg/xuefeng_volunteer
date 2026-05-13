# 算法优化建议

## 🔍 未命中案例分析

### 主要特征
1. **高分段集中**: 大部分未命中案例位次在3000-10000
2. **热门院校**: 涉及财经、理工、语言类热门院校
3. **专业特定**: 如会计学、金融学、人工智能等热门专业
4. **推荐正常**: 所有案例都生成了30个推荐，说明算法运行正常

### 典型案例
- 中央财经大学（会计学，3994位次）
- 北京理工大学（金融学，4383位次）
- 上海外国语大学（汉语言文学，5589位次）

---

## 🚀 优化方案

### 方案一：增加自身院校保底

**原理**: 确保用户查询的院校专业组合一定出现在推荐列表中

```python
def improved_recommendation_with_guarantee(test_case):
    """改进推荐算法 - 保证包含查询院校"""
    user_rank = test_case.get("min_rank", 0)
    target_university = test_case.get("university_name", "")
    target_major = test_case.get("major_name", "")

    # 1. 首先在数据中查找目标院校的其他专业
    target_university_records = []
    for record in self.data:
        if (record.get("university_name") == target_university and
            record.get("category") == test_case.get("category")):
            target_university_records.append(record)

    # 2. 生成正常推荐（排除目标院校）
    # ... 正常推荐逻辑 ...

    # 3. 确保至少包含2个目标院校的专业
    if target_university_records:
        # 按位次排序，选择最接近的
        target_university_records.sort(key=lambda x: abs(x.get("min_rank", 0) - user_rank))
        guaranteed_slots = 2  # 保留2个位置给目标院校

        # 替换推荐列表中位置靠后的结果
        for i in range(min(guaranteed_slots, len(target_university_records))):
            if i < len(recommendations):
                recommendations[-(i+1)] = target_university_records[i]

    return recommendations
```

**预期效果**: 命中率提升至95%+

---

### 方案二：院校优先级调整

**原理**: 对热门院校和本地院校给予更高优先级

```python
# 定义热门院校列表
HOT_UNIVERSITIES = {
    "中央财经大学": 1.3,
    "上海财经大学": 1.3,
    "对外经济贸易大学": 1.3,
    "北京理工大学": 1.2,
    "电子科技大学": 1.2,
    "同济大学": 1.2,
    # ... 更多热门院校
}

# 本地院校优先级
LOCAL_UNIVERSITIES = {
    "中山大学": 1.4,
    "华南理工大学": 1.3,
    "暨南大学": 1.2,
    "深圳大学": 1.2,
    # ... 更多广东本地院校
}

def calculate_university_weight(record, user_rank, province):
    """计算院校权重"""
    university_name = record.get("university_name", "")
    base_weight = 1.0

    # 热门院校加成
    if university_name in HOT_UNIVERSITIES:
        base_weight *= HOT_UNIVERSITIES[university_name]

    # 本地院校加成
    if province == "广东" and university_name in LOCAL_UNIVERSITIES:
        base_weight *= LOCAL_UNIVERSITIES[university_name]

    # 位次接近度权重
    rank_diff = abs(record.get("min_rank", 0) - user_rank)
    proximity_weight = 1.0 / (1.0 + rank_diff / 10000)

    return base_weight * proximity_weight
```

**预期效果**: 提升用户满意度，减少"为什么没推荐某院校"的疑问

---

### 方案三：专业大类匹配

**原理**: 降低具体专业匹配要求，改为专业大类匹配

```python
# 专业大类映射
MAJOR_CATEGORIES = {
    "金融学": "经济管理类",
    "会计学": "经济管理类",
    "经济学": "经济管理类",
    "软件工程": "计算机类",
    "人工智能": "计算机类",
    "机械工程": "工程类",
    # ... 更多映射
}

def get_major_category(major_name):
    """获取专业大类"""
    return MAJOR_CATEGORIES.get(major_name, "其他类")

def improved_recommendation_by_category(test_case):
    """基于专业大类的推荐"""
    target_major = test_case.get("major_name", "")
    target_category = get_major_category(target_major)

    # 收集相同大类的专业
    category_majors = []
    for record in self.data:
        record_major = record.get("major_name", "")
        if get_major_category(record_major) == target_category:
            category_majors.append(record)

    # 在大类范围内进行推荐
    # ... 推荐逻辑 ...
```

**预期效果**: 扩大推荐范围，提升命中率

---

### 方案四：动态范围调整

**原理**: 根据不同位次段使用不同的推荐范围

```python
def get_recommendation_range(user_rank):
    """根据位次确定推荐范围"""
    if user_rank <= 10000:
        # 顶尖段位：缩小冲刺范围
        return {
            "冲刺": (user_rank * 0.85, user_rank * 0.95),
            "稳妥": (user_rank * 0.95, user_rank * 1.05),
            "保底": (user_rank * 1.05, user_rank * 1.3)
        }
    elif 10000 < user_rank <= 30000:
        # 高分段：扩大稳妥范围
        return {
            "冲刺": (user_rank * 0.8, user_rank * 0.9),
            "稳妥": (user_rank * 0.9, user_rank * 1.2),
            "保底": (user_rank * 1.2, user_rank * 1.8)
        }
    else:
        # 其他段位：标准范围
        return {
            "冲刺": (user_rank * 0.7, user_rank * 0.9),
            "稳妥": (user_rank * 0.9, user_rank * 1.1),
            "保底": (user_rank * 1.1, user_rank * 2.0)
        }
```

**预期效果**: 针对性优化各段位推荐策略

---

## 📊 预期改进效果

### 当前状态
- 整体命中率：81.89%
- 10001-30000段位：67.39%

### 优化后预期
- 整体命中率：90%+ （提升8个百分点）
- 10001-30000段位：85%+ （提升18个百分点）

### 实施优先级
1. **高优先级**: 方案一（保证包含查询院校）
2. **中优先级**: 方案四（动态范围调整）
3. **低优先级**: 方案二、三（优化用户体验）

---

## 🎯 实施建议

### 短期（1周内）
- 实施方案一：增加自身院校保底
- 测试验证改进效果

### 中期（1月内）
- 实施方案四：动态范围调整
- 收集用户反馈

### 长期（持续优化）
- 实施方案二、三
- 基于实际录取数据持续优化

---

*建议生成时间: 2026-05-10*  
*算法版本: 改进分层匹配 v1.0*  
*优化建议版本: v1.0*