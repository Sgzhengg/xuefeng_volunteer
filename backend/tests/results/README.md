# 测试结果存储目录

此目录用于存储推荐系统回溯测试的结果文件。

## 📁 文件说明

### JSON报告文件
- `backtest_report_YYYYMMDD_HHMMSS.json` - 完整测试报告，包含所有统计数据
- `backtest_unhit_details_YYYYMMDD_HHMMSS.json` - 未命中案例详情

### CSV数据文件
- `backtest_hit_rate_by_rank_YYYYMMDD_HHMMSS.csv` - 按位次段分组的命中率数据

### HTML可视化报告
- `backtest_report_YYYYMMDD_HHMMSS.html` - 可在浏览器中查看的可视化报告

### 日志文件
- `backtest_YYYYMMDD_HHMMSS.log` - 测试运行日志

## 📊 使用建议

1. **定期清理**: 建议定期清理旧的测试结果文件
2. **版本对比**: 保留不同版本的测试结果用于对比分析
3. **趋势分析**: 通过多次测试结果分析系统性能变化

## 🔍 查看报告

1. **JSON报告**: 使用任何文本编辑器或JSON查看器
2. **CSV数据**: 使用Excel或其他表格软件
3. **HTML报告**: 直接在浏览器中打开