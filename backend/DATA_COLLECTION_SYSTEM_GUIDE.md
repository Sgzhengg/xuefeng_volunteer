# 2026年数据采集系统使用指南

## 📋 系统概述

2026年数据采集系统确保雪峰志愿推荐系统在2026年7月填报志愿前拥有完整的2026年数据。

## 🚀 快速开始

### 1. 验证2025年数据（5月15日前）

```bash
# 进入后端目录
cd backend

# 运行验证脚本
python scripts/validate_2025_data.py
```

**输出示例**：
```
═══════════════════════════════════════════════════════
2025年数据完整性验证
═══════════════════════════════════════════════════════

[检查1] 数据文件存在性检查
  [OK] major_rank_data.json
  [OK] universities_list.json
  [OK] low_rank_admission_data.json
  [OK] outprovince_admission_data.json

[检查2] 广东数据完整性检查（P0）...
  [OK] 广东数据完整：28所院校，26,595条专业记录
  [OK] 广东位次范围: 16,520-78,200
```

### 2. 采集2026年招生计划（5月启动）

```bash
# 运行招生计划采集
python scripts/collect_2026_admission_plans.py
```

**采集频率**：每周一次，发现新数据立即下载

### 3. 政策监控（持续运行）

```bash
# 运行政策监控
python scripts/monitor_2026_policies.py
```

**监控频率**：每12小时检查一次各省考试院

### 4. 激活紧急采集模式（6月23日）

```bash
# 激活紧急采集模式（出分后立即执行）
python scripts/emergency_collect_2026.py activate
```

**监控频率**：每15-30分钟检查一次各省考试院

### 5. 数据整合（新数据采集后）

```bash
# 整合2026年数据
python scripts/integrate_2026_data.py
```

**整合内容**：招生计划、一分一段表、投档线 → 统一格式

## 📅 关键时间节点

| 日期 | 任务 | 脚本 | 紧急程度 |
|------|------|------|----------|
| 5月15日 | 2025年数据验证 | `validate_2025_data.py` | 🔴 P0 |
| 5月22日 | 招生计划采集 | `collect_2026_admission_plans.py` | 🔴 P0 |
| 6月23日 | 激活紧急采集 | `emergency_collect_2026.py activate` | 🔴 P0 |
| 6月25日 | 一分一段表采集 | 自动（紧急模式） | 🔴 P0 |
| 7月20日 | 投档线采集 | 自动（紧急模式） | 🔴 P0 |
| 7月31日 | 系统切换到2026数据 | `integrate_2026_data.py` | 🔴 P0 |

## 🔧 配置文件

### 紧急采集配置

各省份考试院配置位于 `emergency_collect_2026.py`:

```python
self.emergency_sources = {
    "广东": {
        "urls": ["https://eea.gd.gov.cn/"],
        "check_interval_minutes": 15,  # 每15分钟检查一次
        "file_patterns": ["投档线", "排位", "一分一段", "分数段"],
        "priority": "P0"
    },
    # ... 其他省份
}
```

### 政策监控配置

监控数据源配置位于 `monitor_2026_policies.py`:

```python
self.monitoring_config = {
    "check_interval_hours": 12,  # 每12小时检查一次
    "notification_threshold": "medium",  # 重要及以上变化才通知
    "monitored_sources": [...]
}
```

## 📊 监控API

### 获取数据版本信息

```bash
curl http://localhost:8000/api/v1/data/version
```

**返回示例**：
```json
{
  "success": true,
  "data": {
    "current_version": "2026.1.0",
    "description": "new_data更新",
    "last_updated": "2026-05-08T13:15:30",
    "data_components": {
      "admission_plans_2026": {
        "name": "2026年招生计划",
        "status": "included"
      },
      "admission_scores_2026": {
        "name": "2026年投档线",
        "status": "pending",
        "expected_date": "2026-07-01"
      }
    }
  }
}
```

### 手动触发数据更新通知

```bash
curl -X POST http://localhost:8000/api/v1/data/update/notify \
  -H "Content-Type: application/json" \
  -d '{
    "update_type": "new_data",
    "urgency": "high",
    "details": {
      "source": "广东省教育考试院",
      "data_type": "招生计划",
      "record_count": 120
    }
  }'
```

## 📈 日志文件

所有脚本都会生成日志文件，位于 `backend/reports/`:

- `validation_2025_YYYYMMDD_HHMMSS.json` - 数据验证日志
- `collection_YYYYMMDD_HHMMSS.json` - 采集日志
- `policy_monitoring_YYYYMMDD_HHMMSS.txt` - 政策监控报告
- `emergency_results_YYYYMMDD_HHMMSS.json` - 紧急采集结果
- `integration_report_YYYYMMDD_HHMMSS.txt` - 数据整合报告
- `update_log_YYYYMMDD.json` - 数据更新日志

## 🚨 应急处理

### 出分时间延期

如果6月25日仍未发布一分一段表：

1. 系统会继续使用2025年数据
2. UI会显示：📅 当前数据版本：2025 v3.2
3. 通知用户：⚠️ 2026年一分一段表尚未发布，暂时使用2025年数据

### 数据质量问题

如果发现数据错误：

1. 立即停止使用新数据
2. 回滚到上一个稳定版本
3. 使用 `validate_2025_data.py` 检查问题
4. 修正数据后重新整合

## 📞 技术支持

### 问题反馈

发现数据问题时，请提供：

1. 问题描述
2. 相关日志文件
3. 预期结果 vs 实际结果
4. 数据来源和发布时间

### 联系方式

- 数据问题：[数据采集负责人]
- 技术问题：[技术负责人]
- 产品问题：[产品负责人]

---

**文档版本**：v1.0  
**创建时间**：2026年5月8日  
**维护者**：AI数据采集专家