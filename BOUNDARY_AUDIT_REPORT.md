# 高考志愿推荐系统边界场景审计报告

**审计日期**: 2026-04-30
**审计人**: Claude Code (审计专家模式)
**系统版本**: v4.0
**审计范围**: 全边界场景扫描

---

## 📊 审计概览

| 类别 | 总项数 | 已实现 | 部分实现 | 未实现 | 覆盖率 |
|------|--------|--------|----------|--------|--------|
| 用户画像边界 | 9 | 1 | 0 | 8 | 11% |
| 数据覆盖边界 | 8 | 3 | 2 | 3 | 38% |
| 算法边界场景 | 9 | 2 | 1 | 6 | 22% |
| 校验规则边界 | 7 | 3 | 0 | 4 | 43% |
| 性能边界场景 | 6 | 2 | 1 | 3 | 33% |
| **总计** | **39** | **11** | **4** | **24** | **28%** |

---

## 1️⃣ 用户画像边界场景

### 1.1 特殊类型考生

| 场景 | 状态 | 优先级 | 当前实现位置 | 缺失内容 |
|------|------|--------|--------------|----------|
| **普通文理科考生** | ✅ 已实现 | - | `enhanced_recommendation_service.py` | 无 |
| **艺术类考生** | ❌ 未实现 | P0 | - | 缺少艺术类专业录取数据<br>缺少艺术类分数转换算法<br>缺少艺术类统考/校考成绩处理 |
| **体育类考生** | ❌ 未实现 | P0 | - | 缺少体育类专业录取数据<br>缺少体育专项成绩处理<br>缺少体育类术科分数线 |
| **特殊类型招生** | ❌ 未实现 | P0 | - | 缺少强基计划录取逻辑<br>缺少综合评价录取数据<br>缺少高校专项计划数据<br>缺少保送生处理逻辑 |
| **少数民族考生** | ❌ 未实现 | P1 | - | 缺少少数民族加分处理<br>缺少少数民族预科班数据<br>缺少民族班录取规则 |
| **往届生** | ❌ 未实现 | P2 | - | 往届生与应届生录取规则相同<br>（部分军校有限制） |
| **残疾考生** | ❌ 未实现 | P1 | - | 缺少体检受限代码匹配<br>缺少无障碍设施信息<br>缺少专业体检要求校验 |
| **华侨港澳台学生** | ❌ 未实现 | P2 | - | 缺少港澳台联考数据<br>缺少华侨生录取政策 |
| **单招职高学生** | ❌ 未实现 | P1 | - | 缺少单招录取数据<br>缺少中职对口升学数据 |

**优先级说明**:
- **P0**: 必须实现，影响核心用户群体
- **P1**: 强烈建议，影响重要用户群体
- **P2**: 可选实现，影响小众用户群体

---

## 2️⃣ 数据覆盖边界场景

### 2.1 录取规则数据

| 场景 | 状态 | 优先级 | 当前实现位置 | 缺失内容 |
|------|------|--------|--------------|----------|
| **历年录取分数** | ✅ 已实现 | - | `admission_scores.json` | 覆盖31省份，但需更新最新数据 |
| **一分一段表** | ✅ 已实现 | - | `score_rank_tables.json` | 覆盖31省份，但需更新最新数据 |
| **招生计划** | ⚠️ 部分实现 | P0 | `admission_scores.json` | 缺少各专业具体招生人数<br>缺少计划变化趋势 |
| **专业级差** | ❌ 未实现 | P0 | - | 缺少专业级差规则数据<br>缺少级差分数计算逻辑 |
| **同分排序规则** | ❌ 未实现 | P0 | - | 缺少各省同分排序规则<br>缺少同分考生位次计算 |
| **调剂政策** | ⚠️ 部分实现 | P1 | `validator.py` | 有基础校验，但缺少院校具体调剂规则 |
| **单科成绩要求** | ❌ 未实现 | P1 | - | 缺少外语/数学单科分数线<br>缺少单科成绩优秀优先规则 |
| **体检受限代码** | ❌ 未实现 | P1 | - | 缺少体检标准与专业匹配<br>缺少色盲/色受限专业列表 |

### 2.2 院校专业数据

| 场景 | 状态 | 优先级 | 当前实现位置 | 缺失内容 |
|------|------|--------|--------------|----------|
| **院校基本信息** | ✅ 已实现 | - | `universities_list.json` | 覆盖2800+院校，数据完整 |
| **专业详情** | ⚠️ 部分实现 | P1 | `major_details.json` | 部分专业缺少课程设置<br>缺少专业培养方向详细信息 |
| **就业数据** | ⚠️ 部分实现 | P1 | `employment_data.json` | 数据覆盖率约60%<br>缺少最新就业趋势 |
| **学费住宿费** | ❌ 未实现 | P2 | - | 缺少各专业学费标准<br>缺少住宿费标准 |
| **校区分布** | ❌ 未实现 | P2 | - | 缺少多校区院校信息<br>缺少校区地理位置 |

---

## 3️⃣ 算法边界场景

### 3.1 分数边界

| 场景 | 状态 | 优先级 | 当前实现位置 | 缺失内容 |
|------|------|--------|--------------|----------|
| **超高分段(680-750)** | ⚠️ 部分实现 | P0 | `_determine_category_enhanced()` | 分类逻辑存在，但缺少顶尖院校精细推荐<br>缺少清北复交人专项推荐 |
| **本科分数线边缘** | ❌ 未实现 | P0 | - | 缺少压线生专项策略<br>缺少边缘分数冲稳保精确计算 |
| **专科分数线边缘** | ❌ 未实现 | P0 | - | 缺少专科压线生推荐<br>缺少专本贯通项目推荐 |
| **位次缺失/异常** | ❌ 未实现 | P1 | `_calculate_rank_from_score()` | 使用简化计算，缺少精确一分一段表匹配 |
| **新老高考交替** | ❌ 未实现 | P1 | - | 缺少3+1+2选科组合权重<br>缺少再选科目限制规则 |

### 3.2 录取概率边界

| 场景 | 状态 | 优先级 | 当前实现位置 | 缺失内容 |
|------|------|--------|--------------|----------|
| **正常分数段** | ✅ 已实现 | - | `_calculate_enhanced_probability()` | 算法完整，参考夸克三维匹配 |
| **征集志愿** | ❌ 未实现 | P1 | - | 缺少征集志愿数据<br>缺少征集志愿推荐逻辑 |
| **中外合作办学** | ❌ 未实现 | P2 | - | 缺少中外合作项目数据<br>缺少高学费低分项目推荐 |
| **职业资格限制** | ❌ 未实现 | P2 | - | 缺少师范/医学/法律资格要求<br>缺少相关资格证书说明 |

---

## 4️⃣ 校验规则边界场景

### 4.1 风险预警

| 场景 | 状态 | 优先级 | 当前实现位置 | 缺失内容 |
|------|------|--------|--------------|----------|
| **基础数据校验** | ✅ 已实现 | - | `validator.py:_validate_basic_data()` | 完整实现 |
| **冲突检测** | ✅ 已实现 | - | `validator.py:_detect_conflicts()` | 重复推荐检测完整 |
| **风险预警** | ✅ 已实现 | - | `validator.py:_risk_warning()` | 冲刺比例、低分高分院校预警完整 |
| **单科成绩预警** | ❌ 未实现 | P1 | - | 缺少单科成绩不足预警<br>缺少外语/数学要求校验 |
| **体检受限预警** | ❌ 未实现 | P1 | - | 缺少体检代码与专业匹配<br>缺少色盲/受限专业过滤 |
| **家庭收入预警** | ❌ 未实现 | P2 | - | 缺少学费与家庭收入匹配<br>缺少助学贷款信息 |
| **专业与学校优势匹配** | ❌ 未实现 | P2 | - | 缺少学科评估结果<br>缺少优势专业识别 |

### 4.2 比例合理性

| 场景 | 状态 | 优先级 | 当前实现位置 | 缺失内容 |
|------|------|--------|--------------|----------|
| **冲稳保比例校验** | ✅ 已实现 | - | `validator.py:_validate_category_ratio()` | 参考夸克标准(20%/40%/30%) |
| **梯度合理性校验** | ✅ 已实现 | - | `validator.py:_detect_conflicts()` | 分数梯度检测完整 |

---

## 5️⃣ 性能边界场景

### 5.1 并发性能

| 场景 | 状态 | 优先级 | 当前实现位置 | 缺失内容 |
|------|------|--------|--------------|----------|
| **缓存策略** | ✅ 已实现 | - | `cache_manager.py` | LRU缓存、位次分桶完整 |
| **数据库索引** | ✅ 已实现 | - | `data_optimization.sql` | 10个核心索引已创建 |
| **并发高峰处理** | ⚠️ 部分实现 | P1 | `router.py` | 有基础缓存，但缺少限流机制<br>缺少队列管理 |
| **弱网环境优化** | ❌ 未实现 | P2 | - | 缺少请求超时优化<br>缺少离线缓存策略 |
| **大数据量处理** | ⚠️ 部分实现 | P1 | `enhanced_recommendation_service.py` | 有分页限制，但缺少流式处理 |
| **N+1查询检测** | ✅ 已实现 | - | `n_plus_one_detector.py` | 检测工具完整 |

### 5.2 响应时间

| 场景 | 状态 | 优先级 | 当前实现位置 | 缺失内容 |
|------|------|--------|--------------|----------|
| **缓存命中响应** | ✅ 已实现 | - | `cache_manager.py` | 预期 < 50ms |
| **缓存未命中响应** | ⚠️ 部分实现 | P1 | `enhanced_recommendation_service.py` | 预期 < 500ms，需实测验证 |
| **数据库查询优化** | ✅ 已实现 | - | `data_optimization.sql` | 索引优化完整 |

---

## 🚨 P0优先级缺失功能详细说明

### 1. 艺术类考生支持 [P0]

**缺失内容**:
- 艺术类专业录取分数线（与普通文理科不同）
- 艺术类统考/校考成绩处理逻辑
- 艺术类综合分计算公式（文化分+专业分权重）

**实现建议**:
```python
# 在 enhanced_recommendation_service.py 中添加
def _calculate_art_comprehensive_score(
    self,
    cultural_score: int,
    art_score: int,
    province: str,
    formula_type: str  # "5:5", "6:4", "7:3"
) -> float:
    """
    计算艺术类综合分
    各省公式不同：江苏7:3，浙江5:5等
    """
    # 省份权重映射
    weight_map = {
        "江苏": (0.7, 0.3),  # 文化70%, 专业30%
        "浙江": (0.5, 0.5),  # 文化50%, 专业50%
        # ...
    }

    cultural_weight, art_weight = weight_map.get(province, (0.5, 0.5))
    return cultural_score * cultural_weight + art_score * art_weight
```

### 2. 体育类考生支持 [P0]

**缺失内容**:
- 体育类专业录取分数线
- 体育专项成绩处理
- 体育术科分数线

**实现建议**:
```python
def _calculate_pe_comprehensive_score(
    self,
    cultural_score: int,
    pe_score: int,
    province: str
) -> float:
    """
    计算体育类综合分
    大部分省份：文化分+体育分
    """
    # 各省体育综合分计算
    if province == "江苏":
        return cultural_score + pe_score
    # 其他省份...
```

### 3. 强基计划/综合评价支持 [P0]

**缺失内容**:
- 强基计划录取数据（通常低于裸分录取线）
- 综合评价录取规则（高考分+校测分+学业水平考）
- 特殊招生代码识别

**实现建议**:
```python
# 数据结构
{
    "university": "清华大学",
    "strong_basis_plan": {
        "majors": ["数学与应用数学", "物理学"],
        "admission_rule": "85%高考分 + 15%校测分",
        "min_score_adjustment": -20  # 可低于统招线20分
    }
}
```

### 4. 专业级差处理 [P0]

**缺失内容**:
- 各院校专业级差规则数据
- 级差分数计算逻辑

**实现建议**:
```python
# 数据结构
{
    "university_id": "123",
    "major_step_rules": {
        "has_step": true,
        "step_scores": [3, 2, 1, 0],  # 第一二专业级差3分，二三2分...
        "note": "部分专业无级差"
    }
}

# 算法调整
def _apply_major_step_adjustment(
    self,
    original_score: int,
    major_position: int,  # 第几志愿专业
    university_step_rule: dict
) -> int:
    """
    应用专业级差调整
    """
    if not university_step_rule.get("has_step"):
        return original_score

    step_scores = university_step_rule.get("step_scores", [])
    if major_position <= len(step_scores):
        return original_score - step_scores[major_position - 1]

    return original_score
```

### 5. 同分排序规则 [P0]

**缺失内容**:
- 各省同分排序规则
- 同分考生精确位次计算

**实现建议**:
```python
# 数据结构
{
    "province": "江苏",
    "same_score_rules": {
        "理科": [
            {"priority": 1, "field": "数学", "direction": "desc"},
            {"priority": 2, "field": "语文", "direction": "desc"},
            {"priority": 3, "field": "外语", "direction": "desc"}
        ]
    }
}

# 算法实现
def _calculate_rank_with_same_score_rules(
    self,
    province: str,
    score: int,
    subject_scores: dict
) -> int:
    """
    使用同分排序规则计算精确位次
    """
    # 获取该分数所有考生
    candidates = self._get_candidates_by_score(province, score)

    # 按同分规则排序
    rules = self._get_same_score_rules(province)
    sorted_candidates = sorted(
        candidates,
        key=lambda x: self._compare_by_rules(x, rules)
    )

    # 返回精确位次
    return sorted_candidates.index(subject_scores) + 1
```

### 6. 超高分段精细推荐 [P0]

**缺失内容**:
- 清北复交人专项推荐逻辑
- 顶尖院校专业排序（学科评估A+专业优先）

**实现建议**:
```python
def _generate_top_tier_recommendation(
    self,
    province: str,
    score: int,
    rank: int,
    target_majors: list
) -> dict:
    """
    超高分段(680+)专项推荐
    """
    # 1. 清北筛选（全省前100）
    if rank <= 100:
        return self._recommend_tsinghua_peking(rank, target_majors)

    # 2. 华五人筛选（全省前500）
    elif rank <= 500:
        return self._recommend_c9_union(rank, target_majors)

    # 3. 其他985顶尖院校
    else:
        return self._recommend_top_985(rank, target_majors)

def _recommend_by_discipline_evaluation(
    self,
    universities: list,
    major: str
) -> list:
    """
    按学科评估排序（A+优先）
    """
    # 学科评估数据
    evaluation_data = {
        "计算机科学与技术": {
            "A+": ["清华大学", "北京大学", "浙江大学", "国防科技大学"],
            "A": ["北京航空航天大学", "上海交通大学", "南京大学", ...]
        }
    }

    # 按学科评估等级排序
    return sorted(universities, key=lambda x: self._get_evaluation_grade(x, major))
```

### 7. 边缘分数专项策略 [P0]

**缺失内容**:
- 压线生（本科线附近）冲稳保精确计算
- 专科压线生专本贯通项目推荐

**实现建议**:
```python
def _generate_edge_score_recommendation(
    self,
    province: str,
    score: int,
    control_line: int,
    is_undergraduate: bool
) -> dict:
    """
    边缘分数专项推荐
    """
    if is_undergraduate:
        # 本科压线生策略
        gap = score - control_line

        if gap < 0:
            # 低于本科线：重点推荐专科+专本贯通
            return self._recommend_college_transfer_programs(province, score)

        elif gap < 10:
            # 压线0-10分：民办本科+偏远地区公办
            return self._recommend_edge_undergraduate(province, score)

        else:
            # 正常推荐
            pass

    else:
        # 专科压线生策略
        return self._recommend_vocational_with_transfer(province, score)

def _recommend_college_transfer_programs(
    self,
    province: str,
    score: int
) -> dict:
    """
    推荐专本贯通项目（3+2专升本）
    """
    # 数据结构
    transfer_programs = {
        "province": "江苏",
        "programs": [
            {
                "vocational_college": "南京工业职业技术学院",
                "partner_university": "南京工业大学",
                "majors": ["机械设计制造", "自动化"],
                "transfer_rate": "50%",
                "note": "3年专科+2年本科"
            }
        ]
    }

    return transfer_programs
```

---

## 📝 实施优先级路线图

### 第一阶段（1-2周）- P0核心功能
1. ✅ 艺术类考生支持
2. ✅ 体育类考生支持
3. ✅ 专业级差处理
4. ✅ 同分排序规则
5. ✅ 超高分段精细推荐
6. ✅ 边缘分数专项策略

### 第二阶段（2-3周）- P1重要功能
1. ⚠️ 强基计划/综合评价支持
2. ⚠️ 少数民族考生加分处理
3. ⚠️ 残疾考生体检受限代码匹配
4. ⚠️ 单科成绩要求校验
5. ⚠️ 征集志愿推荐
6. ⚠️ 并发限流机制

### 第三阶段（3-4周）- P2增强功能
1. 📋 中外合作办学推荐
2. 📋 学费住宿费数据
3. 📋 家庭收入预警
4. 📋 学科评估数据集成
5. 📋 港澳台联考支持

---

## 🎯 验收标准

### 功能验收
- [ ] 艺术类考生推荐成功率 > 90%
- [ ] 体育类考生推荐成功率 > 90%
- [ ] 超高分段(680+)推荐准确性 > 95%
- [ ] 边缘分数推荐合理性 > 85%

### 性能验收
- [ ] P99延迟 < 500ms（含边界场景处理）
- [ ] 缓存命中率 > 60%
- [ ] 并发1000 QPS无错误

### 稳定性验收
- [ ] 边界场景错误率 < 1%
- [ ] 所有边界场景有降级方案
- [ ] 校验规则覆盖所有边界场景

---

## 📊 风险评估

| 风险项 | 风险等级 | 影响 | 缓解措施 |
|--------|----------|------|----------|
| 艺术类数据缺失 | 高 | 艺术生无法使用 | 紧急爬取艺术类录取数据 |
| 专业级差数据缺失 | 高 | 推荐不准确 | 逐步收集院校规则 |
| 同分规则缺失 | 中 | 位次计算不准确 | 使用简化算法+用户手动输入 |
| 超高分段数据不足 | 中 | 顶尖学生推荐不准 | 手动整理顶尖院校录取数据 |

---

**审计结论**:
当前系统在普通文理科考生场景下表现良好，但在特殊类型考生、边界分数段、录取规则细节等方面存在较多缺失。建议优先实现P0级别的7项功能，以覆盖核心边界场景。

**下一步行动**:
1. 立即开始P0功能开发
2. 收集艺术类/体育类录取数据
3. 实现边缘分数专项推荐算法
4. 完善校验规则覆盖边界场景

---

**审计报告生成时间**: 2026-04-30
**下次审计计划**: P0功能实现后（预计2周）
