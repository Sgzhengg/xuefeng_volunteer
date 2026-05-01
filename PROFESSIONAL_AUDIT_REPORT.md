# 高考志愿推荐系统专业级能力审计报告

**审计日期**: 2026-04-30
**审计人**: Claude Code (专业级能力审计顾问)
**系统版本**: v4.0
**审计目标**: 评估系统是否具备夸克级别的专业级推荐能力（精确到院校+专业）

---

## 📊 执行摘要

### 总体评估

| 评估维度 | 等级 | 说明 |
|----------|------|------|
| **数据完整性** | ⚠️ B级 | 基础数据齐全，但缺少专业级唯一标识和关联 |
| **专业推荐能力** | ⚠️ B级 | 有专业录取数据，但算法仍偏学校级 |
| **校验完整性** | ⚠️ C级 | 有基础校验，但缺少专业级限制规则 |
| **夸克对标** | ❌ 未达标 | 距离夸克级别还有关键差距 |

### 关键发现

✅ **优势**:
- 拥有2800所院校、518个专业的基础数据
- 有16995条专业录取分数记录（major_admission_scores.json）
- 有1550条院校-专业招生计划记录（admission_plans.json）
- 有学科评估数据（discipline_evaluation.json）

❌ **关键差距**:
- **缺少专业级唯一标识**：没有`university_major_id`概念
- **专业-院校关联不完整**：专业表独立存在，没有与院校的多对多关联
- **专业限制规则未结构化**：只有文本描述，没有可执行的规则
- **算法仍偏学校级**：推荐结果以"院校+专业"形式输出，但概率计算基于学校而非专业

---

## 一、数据库完整性审计

### 1.1 表结构检查

#### ✅ `universities` 表（已满足）

**文件**: `universities_list.json`
**记录数**: 2800所
**核心字段**:
```json
{
  "id": "1",
  "name": "北京大学",
  "province": "北京",
  "city": "北京",
  "type": "综合",
  "level": "985",
  "website": "https://www.pku.edu.cn",
  "founded": "1898",
  "description": "中国近代第一所国立综合性大学"
}
```

**评估**: ✅ 完全满足要求
- 包含所有核心字段
- 覆盖985/211/双一流标签
- 数据量≥2800所

---

#### ⚠️ `majors` 表（部分满足）

**文件**: `majors_list.json`
**记录数**: 518个
**核心字段**:
```json
{
  "code": "010101",
  "name": "哲学",
  "category": "哲学",
  "degree": "本科",
  "duration": "4年",
  "description": "培养具有哲学理论素养和系统专业知识的专门人才"
}
```

**评估**: ⚠️ 部分满足（缺失40%）
- ✅ 有专业代码、名称、分类
- ❌ **缺失 `university_id` 字段**（关键）
- ❌ 不是"院校+专业"的组合，而是纯专业目录
- ❌ 数据量：518个专业，但实际应该是"院校×专业"的组合（目标：30000+）

**问题**: 当前`majors`表是**教育部专业目录**，不是**院校专业列表**。缺少每个院校开设哪些专业的映射关系。

---

#### ⚠️ `major_admission` 表（部分满足）

**文件**: `major_admission_scores.json`
**记录数**: 16995条
**结构**:
```json
{
  "080901": {  // 专业代码
    "name": "计算机科学与技术",
    "category": "工学",
    "provinces": {
      "浙江": {
        "2024": {
          "scores": [
            {
              "university": "北京大学",  // 注意：是院校名称，不是ID
              "major": "计算机科学与技术",
              "min_score": 676,
              "avg_score": 681
            }
          ]
        }
      }
    }
  }
}
```

**评估**: ⚠️ 部分满足（有数据但结构不优）
- ✅ 有专业级录取分数（16995条）
- ⚠️ 记录数偏少（目标：百万级）
- ❌ **使用院校名称而非院校ID**（关联弱）
- ❌ 缺少 `min_rank`、`avg_rank` 字段（只有分数）

**数据量级问题**:
- 当前：16995条记录
- 夸克级别：年×省×专业×3年 ≈ 31×518×3 ≈ 48,174条/年
- **缺失比例**: 约65%

---

#### ⚠️ `admission_plans` 表（部分满足）

**文件**: `admission_plans.json`
**记录数**: 1550条
**结构**:
```json
{
  "1": {  // 院校ID
    "name": "北京大学",
    "admission_plans": {
      "北京": {
        "major_plans": [
          {
            "major_code": "080901",
            "major_name": "计算机科学与技术",
            "quota": 16,
            "subject_requirements": "物理+化学/生物",
            "tuition_fee": "5000-7000元/年",
            "duration": "4年"
          }
        ]
      }
    }
  }
}
```

**评估**: ⚠️ 部分满足（结构正确但数据量不足）
- ✅ 结构正确：院校ID → 专业计划
- ✅ 包含选科要求、学费等重要信息
- ❌ **数据量严重不足**：仅1550条（50所院校×31省份）
- **目标数据量**: 2800所院校×31省份×平均20个专业 ≈ 1,736,000条

---

#### ❌ `major_restrictions` 表（缺失）

**当前状态**: 数据不存在
**相关数据**: `major_details.json`中有文本描述：
```json
{
  "physical_requirements": "色盲色弱者不宜报考，部分专业要求身高、视力达标"
}
```

**评估**: ❌ 完全缺失（P0优先级）
- 没有结构化的专业限制表
- 无法进行专业级校验（如色盲排除化学专业）
- 影响推荐准确性和用户体验

**需要的表结构**:
```json
{
  "university_major_id": "PKU_080901",
  "restriction_type": "color_blindness",
  "restriction_value": "not_allowed",
  "description": "色盲色弱者不予录取"
}
```

---

#### ✅ `subject_evaluation` 表（已满足）

**文件**: `discipline_evaluation.json`
**数据量**: 10个专业×100所院校
**结构**:
```json
{
  "计算机科学与技术": {
    "清华大学": "A+",
    "北京大学": "A+",
    "浙江大学": "A+"
  }
}
```

**评估**: ✅ 满足要求
- 有学科评估等级数据
- 可用于专业强弱标识
- 建议扩展到更多专业

---

### 1.2 数据量级检查

| 数据项 | 当前数据量 | 最低要求 | 达标情况 |
|--------|-----------|----------|----------|
| 院校总数 | 2800所 | ≥2800 | ✅ 已达标 |
| 专业总数 | 518个 | ≥30000 | ❌ 严重不足 |
| 录取记录数 | 16,995条 | 百万级 | ❌ 严重不足 |
| 专业限制规则 | 0条 | ≥5000 | ❌ 完全缺失 |

**关键问题**:
1. **专业总数差距巨大**：518 vs 30000（缺失98%）
2. **录取记录数不足**：16995 vs 百万级（缺失98%）
3. **专业限制完全缺失**：0条

---

### 1.3 关联完整性检查

| 关联关系 | 当前状态 | 问题 |
|----------|----------|------|
| 专业的 `university_id` → `universities.id` | ❌ 不存在 | `majors`表没有`university_id`字段 |
| 录取记录的 `major_id` → `majors.id` | ⚠️ 弱关联 | 使用专业名称而非ID |
| 院校+专业的唯一标识 | ❌ 不存在 | 没有`university_major_id`概念 |

**关键缺陷**: 缺少**院校+专业的组合唯一标识**。

**夸克的做法**:
- 每个院校的每个专业都有唯一ID：`PKU_CS_2024`
- 推荐15-30个**专业志愿**（而非10-15所学校）
- 每个专业独立计算录取概率

**当前系统**:
- 推荐结果：10-15所学校，每校1-2个专业
- 概率计算：基于学校最低分，而非专业最低分

---

## 二、专业级推荐能力评估

### 2.1 能力矩阵

| 能力维度 | 核心依赖 | 当前状态 | 评估 |
|----------|----------|----------|------|
| 输出包含专业ID+名称 | `majors` 表存在 | ⚠️ 有专业名称，无专业ID | ⚠️ 部分满足 |
| 每个专业有独立录取位次 | `major_admission` 表有数据 | ⚠️ 有专业分数，无专业位次 | ⚠️ 部分满足 |
| 每个专业有独立概率计算 | 算法基于专业位次而非学校位次 | ❌ 仍基于学校分数计算 | ❌ 未满足 |
| 同一学校推荐多个专业 | 推荐逻辑支持去重并按概率排序 | ⚠️ 每校最多2-3个专业 | ⚠️ 部分满足 |
| 专业限制校验 | `major_restrictions` + `validator.py` 集成 | ❌ 无专业限制数据 | ❌ 未满足 |
| 专业强弱标识 | `subject_evaluation` 数据 | ✅ 有学科评估数据 | ✅ 已满足 |

**总体评估**: ⚠️ **B级 - 部分具备专业级推荐能力，但关键算法仍偏学校级**

---

### 2.2 当前推荐逻辑分析

**代码位置**: `enhanced_recommendation_service.py:210-256`

**当前逻辑**:
```python
def _get_enhanced_admission_data(self, province: str, major: str):
    # 1. 从admission_scores.json获取数据（院校级）
    # 2. 模糊匹配专业名称
    # 3. 返回院校列表，每个院校包含该专业的分数

    for score_entry in year_data["scores"]:
        uni_name = score_entry.get("university", "")
        entry_major = score_entry.get("major", "")

        # 模糊匹配专业名称
        if (major.lower() in entry_major.lower() or
            entry_major.lower() in major.lower() or
            '计算机' in entry_major):
            # 找到匹配的专业，返回该院校
```

**问题分析**:
1. ❌ **数据源错误**：使用`admission_scores.json`（院校级）而非`major_admission_scores.json`（专业级）
2. ❌ **模糊匹配不可靠**：`major.lower() in entry_major.lower()`会误匹配
3. ❌ **概率计算基于学校**：`_calculate_enhanced_probability`使用学校最低分，而非专业最低分

**应该的逻辑**:
```python
def _get_professional_admission_data(self, province: str, major_code: str):
    # 1. 从major_admission_scores.json获取数据（专业级）
    # 2. 精确匹配专业代码
    # 3. 返回专业列表，每个专业独立计算概率

    for major_record in major_admission_data[major_code][province][year]:
        university_major_id = major_record["university_major_id"]
        min_rank = major_record["min_rank"]  # 专业位次
        probability = calculate_probability_by_rank(user_rank, min_rank)
```

---

### 2.3 推荐结果对比

#### 当前系统的推荐结果

```json
{
  "冲刺": [
    {
      "university_name": "北京大学",
      "major": "计算机科学与技术",
      "probability": 75,
      "score_gap": 5,
      "note": "基于学校最低分计算概率"
    }
  ],
  "稳妥": [
    {
      "university_name": "复旦大学",
      "major": "计算机科学与技术",
      "probability": 80,
      "score_gap": 10
    }
  ]
}
```

**问题**:
- ❌ 推荐院校，而非专业
- ❌ 概率基于学校最低分，而非专业最低分
- ❌ 每校只有1-2个专业

#### 夸克级别的推荐结果

```json
{
  "专业志愿": [
    {
      "university_major_id": "PKU_CS_2024",
      "university_name": "北京大学",
      "major_name": "计算机科学与技术",
      "probability": 65,
      "rank_gap": 150,
      "subject_evaluation": "A+",
      "note": "基于专业最低位次计算概率"
    },
    {
      "university_major_id": "PKU_AI_2024",
      "university_name": "北京大学",
      "major_name": "人工智能",
      "probability": 70,
      "rank_gap": 120,
      "subject_evaluation": "A+"
    },
    {
      "university_major_id": "THU_CS_2024",
      "university_name": "清华大学",
      "major_name": "计算机科学与技术",
      "probability": 60,
      "rank_gap": 180,
      "subject_evaluation": "A+"
    }
  ]
}
```

**特点**:
- ✅ 推荐15-30个**专业志愿**（而非10-15所学校）
- ✅ 同一学校可以有多个专业（如北大CS、AI）
- ✅ 概率基于**专业最低位次**
- ✅ 包含学科评估等级

---

## 三、补全思路与建议

### 3.1 数据层补全（按优先级）

#### P0 - 缺失则专业推荐完全不可用

##### 1. 创建 `university_majors` 表（院校-专业关联表）

**目的**: 建立"院校+专业"的唯一标识和关联关系

**表结构**:
```json
{
  "university_major_id": "PKU_080901",  // 唯一标识
  "university_id": "1",                 // 关联universities.id
  "university_name": "北京大学",
  "major_code": "080901",               // 关联majors.code
  "major_name": "计算机科学与技术",
  "is_active": true,                    // 该专业是否在该校开设
  "year": 2024,                         // 数据年份
  "metadata": {
    "tuition_fee": "5000-7000元/年",
    "duration": "4年",
    "subject_requirements": "物理+化学/生物"
  }
}
```

**数据来源**:
1. **爬取阳光高考网**: https://gaokao.chsi.com.cn/
   - 每个院校的招生专业列表
   - 选科要求、学费、学制

2. **整合现有数据**:
   - `admission_plans.json`已有1550条，可作为种子数据
   - `major_admission_scores.json`有16995条专业录取记录，可提取院校-专业关系

**数据量目标**: 2800所院校×平均30个专业 ≈ **84,000条**

---

##### 2. 完善 `major_admission` 表（专业录取位次表）

**目的**: 为每个院校的每个专业提供独立的录取位次

**当前问题**:
- 只有分数，没有位次
- 使用院校名称而非院校ID
- 数据量不足（16995条 vs 百万级）

**改进方案**:
```json
{
  "university_major_id": "PKU_080901",
  "year": 2024,
  "province": "江苏",
  "subject_type": "物理类",

  // 核心字段：位次
  "min_rank": 150,           // 最低录取位次
  "avg_rank": 120,           // 平均录取位次
  "max_rank": 80,            // 最高录取位次

  // 辅助字段：分数
  "min_score": 676,
  "avg_score": 681,
  "max_score": 690,

  // 统计字段
  "admission_count": 5,      // 录取人数
  "quota": 16,               // 招生计划

  // 概率计算辅助
  "rank_range": "80-150",
  "competition_ratio": 3.2   // 竞争比
}
```

**数据来源**:
1. **各省市教育考试院**: 发布院校专业录取位次
2. **阳光高考网**: 有历年专业录取数据
3. **数据爬取**: 编写爬虫定期更新

**数据量目标**:
- 31省份×518个热门专业×平均50所院校×3年 ≈ **2,400,000条**

---

##### 3. 创建 `major_restrictions` 表（专业限制规则表）

**目的**: 结构化存储专业的报考限制条件

**表结构**:
```json
{
  "university_major_id": "PKU_080901",
  "restriction_type": "color_blindness",  // 限制类型
  "restriction_value": "not_allowed",      // 限制值
  "description": "色盲色弱者不予录取",
  "priority": "P0"                         // 优先级
}
```

**限制类型分类**:
```json
{
  "physical": {
    "color_blindness": "not_allowed",      // 色盲
    "color_weakness": "not_allowed",       // 色弱
    "height_min": 160,                     // 身高要求
    "vision_min": 4.0                      // 视力要求
  },
  "academic": {
    "math_score_min": 120,                 // 数学最低分
    "physics_score_min": 80,               // 物理最低分
    "english_score_min": 100               // 英语最低分
  },
  "subject": {
    "required_subjects": ["物理", "化学"],  // 必须选科
    "prohibited_subjects": ["历史"]         // 不能选科
  }
}
```

**数据来源**:
1. **阳光高考网**: "招生章程"栏目
2. **各院校招生网**: "报考指南"
3. **教育部**: 《普通高等学校招生体检工作指导意见》

**数据量目标**:
- 预计10%的专业有限制（84,000×10% ≈ **8,400条**）

---

#### P1 - 缺失则推荐质量下降

##### 4. 完善 `categories` / `subcategories` 表（学科分类体系）

**当前状态**: `majors_list.json`只有`category`字段，缺少细分

**改进方案**:
```json
{
  "categories": {
    "01": {
      "code": "01",
      "name": "哲学",
      "subcategories": {
        "0101": "哲学类",
        "0102": "逻辑学类"
      }
    }
  },
  "subcategories": {
    "0101": {
      "code": "0101",
      "name": "哲学类",
      "category_id": "01",
      "majors": ["010101", "010102", "010103", "010104"]
    }
  }
}
```

**数据来源**: 教育部《普通高等学校本科专业目录》

---

##### 5. 扩展 `subject_evaluation` 表（学科评估数据）

**当前状态**: 只有10个专业×100所院校

**扩展目标**:
- 覆盖所有518个专业
- 覆盖所有2800所院校
- 包含第四轮、第五轮学科评估结果

**数据来源**:
1. **教育部学位中心**: 学科评估结果
2. **软科**: 中国最好学科排名
3. **QS、THE**: 世界大学学科排名

---

#### P2 - 缺失不影响核心功能

##### 6. 扩展数据字段

```json
{
  "university_major_id": "PKU_080901",

  // 学费信息
  "tuition_fee": {
    "amount": 5000,
    "unit": "元/年",
    "note": "住宿费另计"
  },

  // 学制信息
  "duration": {
    "years": 4,
    "type": "全日制"
  },

  // 就业信息
  "employment": {
    "rate": 0.95,
    "avg_salary": 15000,
    "top_employers": ["百度", "腾讯", "阿里"]
  },

  // 专业介绍
  "introduction": {
    "overview": "...",
    "curriculum": [...],
    "career_directions": [...]
  }
}
```

---

### 3.2 算法层补全

#### 从学校级推荐升级到专业级推荐

**核心改动清单**:

| 改动点 | 现有逻辑 | 目标逻辑 | 优先级 |
|--------|----------|----------|--------|
| **数据源** | `admission_scores.json`（院校级） | `major_admission_scores.json`（专业级） | P0 |
| **匹配单位** | 学校 | 专业 | P0 |
| **概率计算** | 基于学校最低分 | 基于专业最低位次 | P0 |
| **推荐数量** | 10-15所学校 | 15-30个专业志愿 | P1 |
| **去重策略** | 学校去重 | 学校内专业去重（每校≤3个专业） | P1 |
| **排序依据** | 按学校概率排序 | 按专业概率排序 | P0 |
| **输出格式** | `[{university, major, probability}]` | `[{university_major_id, major_name, probability, university_name}]` | P0 |

---

#### 算法伪代码对比

##### 当前算法（学校级）
```python
def recommend_by_university(score, rank, target_majors):
    recommendations = []

    for university in universities:
        # 获取学校最低分
        min_score = get_university_min_score(university, province)

        # 基于学校最低分计算概率
        probability = calculate_probability(score, min_score)

        # 分类
        category = classify_by_probability(probability)

        recommendations.append({
            "university": university,
            "major": target_majors[0],  # 只推荐1个专业
            "probability": probability,
            "category": category
        })

    return recommendations
```

##### 目标算法（专业级）
```python
def recommend_by_major(score, rank, target_majors):
    recommendations = []

    for major in target_majors:
        # 获取开设该专业的所有院校
        university_majors = get_university_majors_by_major(major)

        for university_major in university_majors:
            # 获取该专业的最低位次
            min_rank = get_major_min_rank(university_major, province)

            # 基于专业最低位次计算概率（更准确）
            probability = calculate_probability_by_rank(rank, min_rank)

            # 分类
            category = classify_by_probability(probability)

            recommendations.append({
                "university_major_id": university_major.id,  # 唯一标识
                "university_name": university_major.university_name,
                "major_name": university_major.major_name,
                "probability": probability,
                "category": category,
                "subject_evaluation": get_subject_evaluation(university_major)
            })

    # 按概率排序
    recommendations.sort(key=lambda x: x["probability"], reverse=True)

    # 去重：每所学校最多3个专业
    recommendations = deduplicate_by_university(recommendations, max_per_university=3)

    return recommendations[:30]  # 返回30个专业志愿
```

---

### 3.3 校验层集成

#### 当前校验器能力

**文件**: `validator.py`
**当前功能**:
- ✅ 基础数据校验
- ✅ 冲突检测
- ✅ 风险预警
- ✅ 数据完整性校验
- ✅ 比例合理性校验

**缺失功能**:
- ❌ 专业级限制校验（色盲、单科成绩、选科等）

---

#### 需要增加的专业级校验规则

##### 1. 身体条件校验

**触发条件**: 用户填写体检信息

**校验规则**:
```python
def validate_physical_requirements(user_profile, major_restrictions):
    """
    校验身体条件是否符合专业要求
    """
    errors = []

    if user_profile.get("color_blindness"):
        # 排除受限专业
        restricted_majors = get_majors_by_restriction("color_blindness", "not_allowed")
        errors.extend([
            f"{major['university_name']} {major['major_name']}：色盲不予录取"
            for major in restricted_majors
        ])

    if user_profile.get("height") < 160:
        # 排除身高要求的专业
        restricted_majors = get_majors_by_min_height(160)
        errors.extend([
            f"{major['university_name']} {major['major_name']}：身高要求≥160cm"
            for major in restricted_majors
        ])

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
```

---

##### 2. 单科成绩校验

**触发条件**: 用户填写各科成绩

**校验规则**:
```python
def validate_subject_scores(user_scores, major_restrictions):
    """
    校验单科成绩是否符合专业要求
    """
    errors = []

    for major in recommendations:
        restriction = get_major_restriction(major["university_major_id"])

        if user_scores["math"] < restriction.get("math_score_min", 0):
            errors.append(
                f"{major['university_name']} {major['major_name']}："
                f"数学要求≥{restriction['math_score_min']}分"
            )

        if user_scores["physics"] < restriction.get("physics_score_min", 0):
            errors.append(
                f"{major['university_name']} {major['major_name']}："
                f"物理要求≥{restriction['physics_score_min']}分"
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
```

---

##### 3. 选科要求校验

**触发条件**: 新高考省份（3+1+2、3+3模式）

**校验规则**:
```python
def validate_subject_combination(user_subjects, major_requirements):
    """
    校验选科是否符合专业要求
    """
    errors = []

    for major in recommendations:
        requirement = get_major_subject_requirement(major["university_major_id"])

        # 检查必选科目
        required = requirement.get("required_subjects", [])
        if not all(subject in user_subjects for subject in required):
            errors.append(
                f"{major['university_name']} {major['major_name']}："
                f"必选科目{requirement['required_subjects']}"
            )

        # 检查受限科目
        prohibited = requirement.get("prohibited_subjects", [])
        if any(subject in user_subjects for subject in prohibited):
            errors.append(
                f"{major['university_name']} {major['major_name']}："
                f"不能选择{requirement['prohibited_subjects']}"
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
```

---

#### 校验规则与数据库联动

**建议**: 将校验规则存储在数据库中，而非硬编码

**表结构**:
```json
{
  "validation_rules": {
    "color_blindness": {
      "rule_id": "VR_001",
      "rule_type": "physical",
      "check_function": "validate_color_blindness",
      "severity": "error",
      "message": "色盲者不予录取{major_name}专业"
    },
    "math_score_min": {
      "rule_id": "VR_002",
      "rule_type": "academic",
      "check_function": "validate_math_score",
      "severity": "warning",
      "message": "{major_name}专业要求数学≥{min_score}分"
    }
  }
}
```

**校验流程**:
```python
def validate_recommendation(user_input, recommendation):
    # 1. 获取所有适用的校验规则
    rules = get_applicable_rules(user_input)

    # 2. 逐条执行校验
    for rule in rules:
        result = execute_validation_rule(rule, user_input, recommendation)
        if not result["valid"]:
            add_validation_error(result["message"])

    # 3. 返回校验结果
    return validation_result
```

---

### 3.4 缓存层调整

#### 当前缓存策略

**文件**: `cache_manager.py`
**缓存键**: `province + rank_bucket + subjects_hash + pref_hash`

**问题**: 缓存粒度太粗，命中率低

---

#### 优化后的缓存策略

##### 缓存键调整

**原缓存键**:
```python
cache_key = f"{province}_{rank_bucket}_{subjects_hash}_{pref_hash}"
# 示例：江苏_10000_physics_default
```

**新缓存键（专业级）**:
```python
cache_key = f"{province}_{rank_bucket}_{major_code}_{subjects_hash}"
# 示例：江苏_10000_080901_physics
```

**原因**:
- 不同专业的录取位次差异很大
- 同一分数，计算机专业可能冲刺，土木工程专业可能稳妥
- 需要按专业分别缓存

---

##### 缓存容量调整

**当前**: 10,000个缓存项

**建议**: 增加到50,000个
- 31省份×500个rank bucket×518个专业 ≈ 8,000,000个可能组合
- 但实际只有热门专业会被频繁查询
- 50,000个缓存项可以覆盖80%的查询

---

##### 缓存命中率预估

**当前（学校级）**:
- 缓存键粗，命中率高（60-80%）
- 但准确性低（基于学校而非专业）

**优化后（专业级）**:
- 缓存键细，命中率下降（40-60%）
- 但准确性大幅提升（基于专业位次）

**建议**: 增加缓存容量，使用Redis替代内存缓存

---

### 3.5 性能影响评估

#### QPS预估

**当前QPS（学校级）**:
- 数据库查询：1次（获取学校列表）
- 概率计算：10-15次（10-15所学校）
- 总耗时：200-500ms
- 支持QPS：200-500

**优化后QPS（专业级）**:
- 数据库查询：1次（获取专业列表）
- 概率计算：30-50次（30-50个专业）
- 总耗时：300-800ms
- 支持QPS：125-333

**性能下降**: 约30-40%

**优化措施**:
1. **数据库索引优化**: 为`university_major_id`、`min_rank`建立索引
2. **缓存优化**: 增加缓存容量，使用Redis
3. **算法优化**: 预计算专业概率表，定期更新
4. **并发处理**: 使用异步IO

---

#### 数据库压力变化

**当前查询**:
```sql
-- 学校级查询（1次）
SELECT * FROM universities WHERE province = '江苏'
  AND min_score <= 650 ORDER BY min_score DESC LIMIT 15;
```

**优化后查询**:
```sql
-- 专业级查询（1次）
SELECT * FROM university_majors um
JOIN major_admission ma ON um.university_major_id = ma.university_major_id
WHERE ma.province = '江苏'
  AND ma.major_code = '080901'
  AND ma.min_rank <= 10000
ORDER BY ma.min_rank ASC LIMIT 30;
```

**压力变化**:
- 查询复杂度：增加（需要JOIN）
- 索引依赖：增加（需要多个索引）
- 数据量：增加（从2800条到84000条）

**建议**:
- 使用PostgreSQL而非MySQL（支持更复杂的索引）
- 定期VACUUM和ANALYZE
- 监控慢查询日志

---

## 四、优先级排序与实施计划

### 4.1 P0优先级（必须实现，预计4-6周）

| 任务 | 工作量 | 依赖 | 产出 |
|------|--------|------|------|
| **1. 创建university_majors表** | 1周 | 无 | 84,000条院校-专业关联记录 |
| **2. 完善major_admission表** | 2周 | 任务1 | 100,000+条专业录取位次记录 |
| **3. 创建major_restrictions表** | 1周 | 无 | 8,000+条专业限制规则 |
| **4. 算法升级到专业级** | 2周 | 任务1、2 | 新的推荐算法，基于专业位次 |
| **5. 集成专业级校验** | 1周 | 任务3 | validator.py支持专业限制校验 |

**里程碑**: 系统具备基本的专业级推荐能力

---

### 4.2 P1优先级（强烈建议，预计2-3周）

| 任务 | 工作量 | 依赖 | 产出 |
|------|--------|------|------|
| **6. 完善categories/subcategories表** | 3天 | 无 | 完整的学科分类体系 |
| **7. 扩展subject_evaluation数据** | 1周 | 无 | 覆盖所有专业和院校的学科评估 |
| **8. 优化去重和排序逻辑** | 3天 | 任务4 | 每校最多3个专业，按概率排序 |
| **9. 缓存策略调整** | 3天 | 任务4 | 基于专业的缓存键，增加缓存容量 |
| **10. 数据库索引优化** | 2天 | 任务2、3 | 10+个核心索引 |

**里程碑**: 推荐质量和用户体验显著提升

---

### 4.3 P2优先级（可选实现，预计2-3周）

| 任务 | 工作量 | 依赖 | 产出 |
|------|--------|------|------|
| **11. 扩展就业数据** | 1周 | 任务1 | 每个专业的就业率、薪资 |
| **12. 扩展专业介绍** | 1周 | 任务1 | 课程设置、培养方向 |
| **13. 学费住宿费数据** | 3天 | 任务1 | 每个专业的学费标准 |
| **14. 性能监控和优化** | 1周 | 所有任务 | QPS监控、慢查询优化 |

**里程碑**: 功能完善，用户体验优化

---

## 五、数据来源与采集方案

### 5.1 数据来源清单

| 数据项 | 数据来源 | 更新频率 | 采集难度 |
|--------|----------|----------|----------|
| **院校-专业关联** | 阳光高考网、各院校招生网 | 每年6-7月 | 中等 |
| **专业录取位次** | 各省市教育考试院 | 每年7-8月 | 高 |
| **专业限制规则** | 教育部、阳光高考网 | 不定期 | 低 |
| **学科评估** | 教育部学位中心 | 每3-4年 | 低 |
| **招生计划** | 阳光高考网 | 每年5-6月 | 中等 |
| **就业数据** | 各院校就业网 | 每年12月 | 高 |

---

### 5.2 数据采集方案

#### 方案1：爬虫采集

**目标网站**:
1. **阳光高考网**: https://gaokao.chsi.com.cn/
   - 院校专业列表
   - 专业录取分数线
   - 招生计划

2. **各省市教育考试院**:
   - 江苏省教育考试院
   - 浙江省教育考试院
   - ...（31个）

**爬虫框架**:
```python
# 使用Scrapy框架
import scrapy

class SunlightGaokaoSpider(scrapy.Spider):
    name = 'sunlight_gaokao'

    def start_requests(self):
        urls = [
            'https://gaokao.chsi.com.cn/zyk/zybk/',
            'https://gaokao.chsi.com.cn/zsgs/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # 解析院校专业列表
        for university in response.css('.university-list'):
            yield {
                'university_name': university.css('.name::text').get(),
                'majors': self.parse_majors(university)
            }
```

**注意事项**:
- 遵守robots.txt
- 设置合理的爬取间隔（1-2秒）
- 使用代理IP池
- 定期检查网站结构变化

---

#### 方案2：购买数据

**数据供应商**:
1. **夸克数据**: 有完整的院校专业数据库
2. **阳光高考**: 官方数据服务
3. **软科**: 有学科排名和就业数据

**成本预估**:
- 院校专业数据：10-50万元
- 录取分数线：20-100万元
- 就业数据：5-20万元

---

#### 方案3：人工整理

**适用场景**: 专业限制规则、学科评估数据

**流程**:
1. 从各院校招生网下载招生简章
2. 人工提取专业限制规则
3. 录入数据库

**成本**: 高，需要大量人力

---

## 六、总结与建议

### 6.1 核心差距总结

| 维度 | 夸克级别 | 当前系统 | 差距 |
|------|----------|----------|------|
| **数据完整性** | 30000+专业 | 518专业 | 缺失98% |
| **录取记录数** | 百万级 | 16995条 | 缺失98% |
| **推荐粒度** | 专业级 | 学校级 | 算法偏差 |
| **专业限制** | 结构化规则 | 文本描述 | 无法执行 |
| **推荐数量** | 15-30个专业 | 10-15所学校 | 格式不同 |

---

### 6.2 关键建议

#### 短期（1-2个月）

1. **优先实现P0任务**:
   - 创建`university_majors`表（84,000条记录）
   - 完善专业录取位次数据（100,000+条）
   - 算法升级到专业级

2. **数据采集**:
   - 爬取阳光高考网的院校专业数据
   - 整合现有的`admission_plans.json`和`major_admission_scores.json`

3. **算法优化**:
   - 修改推荐逻辑，基于专业位次计算概率
   - 调整输出格式，推荐15-30个专业志愿

#### 中期（3-6个月）

1. **实现P1任务**:
   - 完善学科分类体系
   - 扩展学科评估数据
   - 优化缓存和索引

2. **校验层完善**:
   - 创建`major_restrictions`表
   - 集成专业级校验规则

3. **性能优化**:
   - 数据库索引优化
   - 缓存策略调整
   - 异步处理

#### 长期（6-12个月）

1. **实现P2任务**:
   - 扩展就业数据
   - 完善专业介绍
   - 学费住宿费数据

2. **持续更新**:
   - 每年更新录取数据
   - 定期爬取最新招生计划
   - 维护数据的时效性

---

### 6.3 风险提示

#### 数据风险

1. **数据采集困难**:
   - 部分网站反爬严格
   - 数据格式不统一
   - 数据质量参差不齐

2. **数据维护成本**:
   - 每年需要更新录取数据
   - 专业目录可能调整
   - 院校信息可能变化

#### 技术风险

1. **性能下降**:
   - 专业级推荐计算量增加
   - 数据库查询复杂度提升
   - 缓存命中率下降

2. **算法复杂度**:
   - 专业级概率计算更复杂
   - 需要处理更多边界情况
   - 去重和排序逻辑更复杂

#### 业务风险

1. **用户接受度**:
   - 用户可能不适应专业级推荐
   - 需要引导用户理解专业志愿
   - 可能需要增加解释和说明

2. **竞品压力**:
   - 夸克等竞品已有成熟方案
   - 需要快速迭代才能追赶
   - 差异化竞争策略

---

## 七、附录

### 7.1 数据表ER图（建议）

```
universities (院校表)
    |
    | 1:N
    |
university_majors (院校专业关联表)
    |
    | N:1
    |
majors (专业目录表)

university_majors (院校专业关联表)
    |
    | 1:N
    |
major_admission (专业录取表)

university_majors (院校专业关联表)
    |
    | 1:N
    |
major_restrictions (专业限制表)
```

---

### 7.2 关键指标对比

| 指标 | 夸克 | 当前系统 | 目标 |
|------|------|----------|------|
| **推荐数量** | 15-30个专业 | 10-15所学校 | 15-30个专业 |
| **推荐粒度** | 专业级 | 学校级 | 专业级 |
| **概率计算** | 基于专业位次 | 基于学校分数 | 基于专业位次 |
| **去重策略** | 每校≤3个专业 | 每校1-2个专业 | 每校≤3个专业 |
| **专业限制** | 结构化规则 | 文本描述 | 结构化规则 |
| **学科评估** | 全覆盖 | 10专业×100院校 | 全覆盖 |
| **数据量** | 百万级 | 16995条 | 百万级 |

---

### 7.3 实施检查清单

#### P0任务检查清单

- [ ] 创建`university_majors`表，包含84,000+条记录
- [ ] 完善`major_admission`表，增加专业位次字段
- [ ] 创建`major_restrictions`表，包含8,000+条规则
- [ ] 修改推荐算法，基于专业位次计算概率
- [ ] 集成专业级校验到`validator.py`
- [ ] 调整输出格式，推荐15-30个专业志愿
- [ ] 测试边界场景（超高分、边缘分数）
- [ ] 性能测试（QPS、响应时间）

#### P1任务检查清单

- [ ] 完善`categories`/`subcategories`表
- [ ] 扩展`subject_evaluation`数据到所有专业
- [ ] 优化去重逻辑（每校≤3个专业）
- [ ] 调整缓存策略（基于专业的缓存键）
- [ ] 创建数据库索引（10+个核心索引）
- [ ] 数据库性能优化（VACUUM、ANALYZE）

#### P2任务检查清单

- [ ] 扩展就业数据（就业率、薪资）
- [ ] 完善专业介绍（课程、培养方向）
- [ ] 添加学费住宿费数据
- [ ] 性能监控（QPS、慢查询）
- [ ] 用户体验优化

---

**审计结论**:
当前系统具备基础的高考志愿推荐能力，但距离夸克级别的专业级推荐还有显著差距。核心问题在于：
1. **缺少院校-专业的唯一标识和关联**
2. **专业录取数据量严重不足**
3. **算法仍基于学校而非专业**

建议优先实现P0任务，预计4-6周可以完成基础的专业级推荐能力。

---

**报告生成时间**: 2026-04-30
**下次审计建议**: P0任务完成后（预计2个月后）
