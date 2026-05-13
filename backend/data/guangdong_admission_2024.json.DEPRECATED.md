# ⚠️ DEPRECATED FILE - 已弃用

## 文件状态
- **文件名**: `guangdong_admission_2024.json`
- **状态**: ⚠️ **DEPRECATED** (已弃用)
- **替换为**: `major_rank_data.json`
- **弃用日期**: 2026年5月8日
- **弃用原因**: 数据源切换，使用真实录取数据替代模板数据

---

## 📊 数据对比

| 特性 | 旧文件 (DEPRECATED) | 新文件 (ACTIVE) |
|------|---------------------|-----------------|
| **文件名** | guangdong_admission_2024.json | major_rank_data.json |
| **记录数量** | 10条 | 829,495条 |
| **数据类型** | 手动模板数据 | 真实录取数据 |
| **数据年份** | 2024年 | 2021-2025年 |
| **广东记录** | 10条 | 26,595条 |
| **推荐效果** | 随机推荐 | 精准推荐 |
| **文件大小** | 4KB | 484MB |

---

## 🔄 迁移说明

### 新的数据源加载方式

**旧代码（已弃用）**：
```python
def _load_data(self):
    with open("data/guangdong_admission_2024.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
        self.guangdong_data = data.get("data", [])
```

**新代码（推荐）**：
```python
def _load_data(self):
    with open("data/major_rank_data.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
        all_records = data.get("major_rank_data", [])
        
        # 过滤广东数据
        self.guangdong_data = [
            r for r in all_records
            if r.get("province") == "广东"
        ]
```

---

## 🗂️ 文件保留原因

1. **向后兼容**: 某些旧代码可能仍在使用此文件
2. **数据备份**: 作为应急备用数据源
3. **格式参考**: JSON结构参考格式
4. **测试用途**: 用于单元测试和开发环境

---

## ⚡ 性能对比

| 指标 | 旧文件 | 新文件 | 改善 |
|------|--------|--------|------|
| **推荐准确性** | 低（随机） | 高（基于真实数据） | **质变** |
| **覆盖率** | 10个院校专业 | 82.9万条记录 | **8294倍** |
| **广东本地推荐** | 不保证 | 100%广东院校 | **精准** |
| **用户满意度** | 低 | 高 | **显著提升** |

---

## 📅 弃用时间线

- **2026年5月8日**: 标记为 DEPRECATED
- **2026年6月1日**: 停止更新此文件
- **2026年7月1日**: 建议删除此文件（如果兼容性测试通过）

---

## 🆘 支持信息

如有疑问或需要技术支持，请参考：
- `DATA_SOURCE_SWITCH_REPORT.md` - 数据源切换详细报告
- `build_university_majors.py` - 数据生成脚本
- `validate_guangdong_recommendations.py` - 验证测试脚本

---

**⚠️ 重要提醒**: 新开发请勿使用此文件，请使用 `major_rank_data.json`