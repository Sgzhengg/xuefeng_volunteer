# 官方数据导入指南

本文档说明如何使用官方数据导入工具将教育考试院数据集成到推荐系统。

---

## 1. 准备工作

### 1.1 安装依赖（如需导入Excel文件）

```bash
pip install openpyxl
```

### 1.2 准备数据文件

支持的文件格式：
- **CSV文件**（推荐）：使用UTF-8或UTF-8-BOM编码
- **Excel文件**：.xlsx或.xls格式
- **JSON文件**：标准JSON数组格式

---

## 2. 数据格式要求

### 2.1 CSV/Excel格式

**必需列**：
- `院校名称`：院校全称（如：北京大学）
- `专业名称`：专业全称（如：计算机科学与技术）
- `最低分`：最低录取分数（整数）
- `最低位次`：最低录取位次（整数）

**可选列**：
- `平均分`：平均录取分数
- `平均位次`：平均录取位次

**示例CSV**：
```csv
院校名称,专业名称,最低分,平均分,最低位次,平均位次
北京大学,计算机科学与技术,676,681,1500,1200
清华大学,计算机科学与技术,678,683,1200,1000
```

**列名别名**（支持多种命名方式）：
- 院校名称：院校名称, 院校, 学校, university, university_name
- 专业名称：专业名称, 专业, major, major_name
- 最低分：最低分, 最低分数, min_score, score
- 最低位次：最低位次, 最低位, min_rank, rank
- 平均分：平均分, 平均分数, avg_score
- 平均位次：平均位次, 平均位, avg_rank

### 2.2 JSON格式

```json
[
  {
    "university_name": "北京大学",
    "major_name": "计算机科学与技术",
    "min_score": 676,
    "avg_score": 681,
    "min_rank": 1500,
    "avg_rank": 1200
  }
]
```

---

## 3. 使用导入工具

### 3.1 导入CSV文件

```bash
cd backend

python official_data_importer.py \
  --file data/official_data/jiangsu_2024.csv \
  --province 江苏 \
  --year 2024
```

### 3.2 导入Excel文件

```bash
python official_data_importer.py \
  --file data/official_data/jiangsu_2024.xlsx \
  --province 江苏 \
  --year 2024 \
  --sheet Sheet1
```

### 3.3 导入JSON文件

```bash
python official_data_importer.py \
  --file data/official_data/jiangsu_2024.json \
  --province 江苏 \
  --year 2024
```

---

## 4. 导入流程

### 4.1 自动化流程

导入工具会自动执行以下步骤：

1. **读取数据文件**
   - 根据文件扩展名自动选择解析器
   - 支持多种列名别名

2. **数据验证和清洗**
   - 检查必需字段是否存在
   - 验证分数和位次的合理性
   - 清理数字字符串（去除空格、逗号等）

3. **数据标准化**
   - 匹配院校ID（从universities_list.json）
   - 匹配专业代码（从majors_list.json）
   - 生成university_major_id
   - 推断专业类别（如果找不到）

4. **集成到现有数据**
   - 与major_rank_data.json合并
   - 官方数据优先级高于估算数据
   - 自动备份原文件

5. **生成导入报告**
   - 显示导入记录数
   - 统计院校层次分布
   - 显示分数和位次范围

### 4.2 数据备份

每次导入都会自动备份原文件：
```
major_rank_data_backup_20260506_143000.json
```

---

## 5. 获取官方数据的方法

### 5.1 江苏省教育考试院

**网址**：http://www.jseea.cn/

**数据路径**：
1. 访问官网
2. 进入"招考信息" > "普通高校招生"
3. 查找"录取分数线"或"投档线"
4. 下载分院校分专业录取数据

**数据格式**：
- 通常为HTML表格或PDF文件
- 可以复制到Excel或另存为CSV

**提示**：
- 如果是PDF，需要先转换为Excel/CSV
- 可以使用在线PDF转换工具或Adobe Acrobat

### 5.2 浙江省教育考试院

**网址**：http://www.zjzs.net/

**数据路径**：
1. 访问官网
2. 进入"信息公开" > "招考信息"
3. 查找"高校招生" > "录取分数线"

### 5.3 其他省份

类似流程：
- 河南省教育考试院：http://www.heao.gov.cn/
- 山东省教育招生考试院：http://www.sdzk.cn/
- 广东省教育考试院：http://eea.gd.gov.cn/

---

## 6. 常见问题

### Q1: 导入后提示"University not found in database"

**原因**：院校名称不在标准库中

**解决方法**：
1. 检查院校名称是否准确
2. 更新universities_list.json添加新院校
3. 或者暂时接受临时ID（系统会自动处理）

### Q2: 专业名称匹配不上

**原因**：专业名称不在标准库中

**解决方法**：
- 系统会自动推断专业代码和类别
- 如果推断不准确，手动更新majors_list.json

### Q3: 分数或位次显示为0

**原因**：数据格式不正确

**解决方法**：
1. 检查CSV文件编码（推荐UTF-8-BOM）
2. 确保数字列没有中文字符
3. 使用Excel打开并检查数据格式

### Q4: 导入后推荐质量没有提升

**原因**：可能是数据覆盖范围不够

**解决方法**：
1. 导入更多省份的数据
2. 导入更多年份的数据
3. 导入更多专业的数据

---

## 7. 数据质量建议

### 7.1 推荐数据优先级

1. **官方数据**（最高优先级）
   - 来源：教育考试院官网
   - 精度：高
   - 覆盖：有限

2. **估算数据**（补充）
   - 来源：基于分数转换
   - 精度：中等
   - 覆盖：广泛

### 7.2 数据更新频率

- **官方数据**：每年更新一次（8-9月录取结束后）
- **估算数据**：根据需要重新生成

---

## 8. 示例：完整导入流程

### 步骤1：获取数据

从江苏省教育考试院下载2024年专业录取数据，另存为`jiangsu_2024.csv`

### 步骤2：检查数据格式

确保CSV文件包含以下列：
```csv
院校名称,专业名称,最低分,最低位次
北京大学,计算机科学与技术,676,1500
...
```

### 步骤3：导入数据

```bash
python official_data_importer.py \
  --file data/official_data/jiangsu_2024.csv \
  --province 江苏 \
  --year 2024
```

### 步骤4：查看导入报告

```
============================================================
Data Import Report
============================================================

Source: 江苏 (2024)
Total records imported: 30

University breakdown:
- 985 universities: 30 records
- 211 universities: 0 records

Score range:
- Min: 620
- Max: 678
- Average: 650.5

Rank range:
- Min: 1,200
- Max: 9,000
- Average: 4,500

============================================================
```

### 步骤5：验证数据

```bash
python -c "
import json
with open('data/major_rank_data.json', encoding='utf-8') as f:
    data = json.load(f)
    
jiangsu_2024 = [r for r in data['major_rank_data'] 
                if r['province'] == '江苏' and r['year'] == 2024]
                
print(f'江苏2024数据: {len(jiangsu_2024)}条')
print(f'官方数据: {len([r for r in jiangsu_2024 if r.get(\"accuracy\") == \"high\"])}条')
"
```

---

## 9. 下一步

导入官方数据后，建议：

1. **测试推荐系统**
   ```bash
   python test_professional_recommendation.py
   ```

2. **对比推荐质量**
   - 对比官方数据vs估算数据的推荐结果
   - 分析推荐准确性的提升

3. **优化推荐算法**
   - 基于官方数据调整概率计算模型
   - 优化冲稳保分类阈值

---

**文档版本**：1.0.0
**创建日期**：2026-05-06
**最后更新**：2026-05-06
