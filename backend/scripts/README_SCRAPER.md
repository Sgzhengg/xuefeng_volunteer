# 2025广东高考本科批次投档线采集系统

## 项目概述

本系统用于采集2025年广东省高考本科批次投档线真实数据，支持多数据源采集和数据验证。

## 功能特性

✅ **多数据源采集**
  - 高考直通车
  - 掌上高考
  - 中国教育在线
  - 广东省教育考试院

✅ **优先级策略**
  - 优先使用官方JSON接口
  - 其次使用XHR接口
  - 最后才解析HTML表格

✅ **数据真实性保障**
  - 禁止使用模拟数据
  - 多源数据交叉验证
  - 生成不一致报告

✅ **标准输出格式**
  - CSV格式（带BOM UTF-8）
  - Excel格式（.xlsx）
  - 数据验证报告

## 安装依赖

```bash
cd backend/scripts
pip install -r requirements_scraper.txt
```

如果是首次使用Playwright，需要安装浏览器：

```bash
playwright install chromium
```

## 使用方法

### 方法1：API分析工具（推荐首先使用）

在开始正式采集前，建议先使用API分析工具分析目标网站：

```bash
cd backend/scripts
python api_analyzer.py
```

按照提示：
1. 选择要分析的网站（1-5）
2. 在打开的浏览器中手动导航到2025年广东投档线页面
3. 按Enter捕获API请求
4. 查看分析报告

这将帮助我们找到真实的JSON接口。

### 方法2：完整采集系统

```bash
cd backend/scripts
python guangdong_2025_admission_scraper.py
```

系统将：
1. 采集所有数据源
2. 进行数据去重
3. 数据验证
4. 导出结果到 `output/` 目录

### 方法3：单独测试某个数据源

编辑 `guangdong_2025_admission_scraper.py` 中的 `main()` 函数：

```python
async def main():
    system = Guangdong2025AdmissionSystem()

    # 只采集高考直通车
    scraper = system.scrapers['gaokao_cn']
    await scraper.create_session()
    records = await scraper.scrape('物理')
    await scraper.close_session()

    print(f"采集到 {len(records)} 条记录")
```

## 输出文件

所有输出文件保存在 `output/` 目录：

1. **guangdong_2025_admission_YYYYMMDD_HHMMSS.csv** - CSV格式数据
2. **guangdong_2025_admission_YYYYMMDD_HHMMSS.xlsx** - Excel格式数据
3. **discrepancy_report_YYYYMMDD_HHMMSS.csv** - 数据不一致报告
4. **summary_report_YYYYMMDD_HHMMSS.txt** - 汇总报告

## 数据格式说明

### 主要字段

| 字段名 | 说明 | 示例 |
|--------|------|------|
| 院校名称 | 高校全称 | 中山大学 |
| 科类 | 物理或历史 | 物理 |
| 专业组代码 | 专业组编号 | 201 |
| 最低分 | 投档最低分 | 628 |
| 最低排位 | 对应排位 | 7500 |
| 数据来源 | 数据源名称 | 高考直通车 |
| 抓取时间 | 数据采集时间 | 2025-07-20T15:30:00 |
| 验证状态 | 是否多源验证 | 已验证 |

## 数据验证规则

### 验证条件

同一学校的同一专业组：
- 至少2个数据源一致
- 分数和排位完全一致（无容忍度）
- 标记为 `verified = true`

### 不一致处理

如果数据源之间不一致：
- 优先采用官方数据
- 生成 `discrepancy_report.csv` 记录冲突
- 在汇总报告中统计不一致数量

## 去重规则

同一学校 + 同专业组 + 同科类：
- 只保留一条记录
- 按优先级：官方 > 高考直通车 > 掌上高考 > 中国教育在线

## 开发指南

### 添加新的数据源

1. 继承 `BaseScraper` 类
2. 实现 `scrape()` 方法
3. 在 `Guangdong2025AdmissionSystem` 中注册

示例：

```python
class NewScraper(BaseScraper):
    async def scrape(self, category: str = "物理") -> List[AdmissionRecord]:
        # 实现采集逻辑
        records = await self._try_json_api(category)
        if not records:
            records = await self._parse_html(category)
        return records

# 在系统中注册
system.scrapers['new_source'] = NewScraper()
```

### 自定义API端点

编辑 `scraper_config.py`：

```python
DATA_SOURCES = {
    'gaokao_cn': {
        'possible_apis': [
            '你的API地址',
        ]
    }
}
```

## 常见问题

### Q1: 为什么没有采集到数据？

A: 可能原因：
1. 2025年投档线尚未发布（通常7月中下旬发布）
2. 网站结构变化，需要重新分析接口
3. 使用API分析工具检查真实接口

### Q2: 如何确认数据是真实的？

A:
1. 查看日志中的数据来源
2. 检查 `verified` 字段
3. 查看 `discrepancy_report.csv`
4. 与官方发布的数据对比

### Q3: 浏览器窗口闪退怎么办？

A: 编辑 `scraper_config.py`：
```python
BROWSER_CONFIG = {
    'headless': False,  # 改为False
}
```

### Q4: 如何提高采集速度？

A: 编辑 `SCRAPER_CONFIG`：
```python
SCRAPER_CONFIG = {
    'delay_between_requests': 0.5,  # 减少延迟
    'timeout': 15,  # 减少超时时间
}
```

注意：太快可能被反爬虫。

## 注意事项

⚠️ **重要提醒**

1. **2025年数据发布时间**：广东省通常在7月中下旬发布本科批次投档线
2. **数据真实性**：本系统严格禁止使用模拟/AI生成的数据
3. **合法合规**：仅用于教育研究，遵守网站robots.txt
4. **频率控制**：默认有请求间隔，避免对目标网站造成压力

## 技术架构

```
guangdong_2025_admission_scraper.py  # 主程序
├── BaseScraper                       # 爬虫基类
├── GaokaoCNScraper                   # 高考直通车
├── GaokaopaiScraper                  # 掌上高考
├── EOLScraper                        # 中国教育在线
├── OfficialScraper                   # 官方数据
├── DataValidator                     # 数据验证器
└── Guangdong2025AdmissionSystem      # 系统主类

api_analyzer.py                       # API分析工具
scraper_config.py                     # 配置文件
```

## 联系方式

如有问题，请查看项目日志文件或联系开发团队。

## 更新日志

- 2025-05-10: 初始版本发布
- 支持多数据源采集
- 实现数据验证机制
- 支持CSV/Excel导出
