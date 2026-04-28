import 'package:flutter/material.dart';
import '../../../shared/theme/app_theme.dart';

/// 院校分布柱状图
class UniversityDistributionChart extends StatelessWidget {
  final Map<String, int> distribution;
  final String? title;

  const UniversityDistributionChart({
    super.key,
    required this.distribution,
    this.title,
  });

  @override
  Widget build(BuildContext context) {
    final totalCount = distribution.values.fold(0, (sum, count) => sum + count);

    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingLg),
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        boxShadow: AppTheme.shadowLight,
        border: Border.all(
          color: AppTheme.surfaceContainerHighest,
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (title != null) ...[
            Row(
              children: [
                Icon(Icons.bar_chart_rounded, color: AppTheme.primaryBlue, size: 20),
                const SizedBox(width: AppTheme.spacingSm),
                Text(
                  title!,
                  style: AppTheme.titleSmall,
                ),
              ],
            ),
            const SizedBox(height: AppTheme.spacingMd),
          ],

          // 图表
          ...distribution.entries.map((entry) {
            return _buildBar(
              category: entry.key,
              count: entry.value,
              totalCount: totalCount,
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildBar({
    required String category,
    required int count,
    required int totalCount,
  }) {
    final color = _getCategoryColor(category);
    final percentage = totalCount > 0 ? (count / totalCount * 100) : 0.0;

    return Padding(
      padding: const EdgeInsets.only(bottom: AppTheme.spacingMd),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 类别和数量
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    width: 12,
                    height: 12,
                    decoration: BoxDecoration(
                      color: color,
                      borderRadius: BorderRadius.circular(3),
                    ),
                  ),
                  const SizedBox(width: AppTheme.spacingSm),
                  Text(
                    category,
                    style: AppTheme.bodyMedium,
                  ),
                ],
              ),
              Text(
                '$count所',
                style: AppTheme.bodyMedium.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppTheme.spacingSm),

          // 进度条
          Stack(
            children: [
              Container(
                height: 24,
                decoration: BoxDecoration(
                  color: AppTheme.lightGray,
                  borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                ),
              ),
              FractionallySizedBox(
                widthFactor: percentage / 100,
                child: Container(
                  height: 24,
                  decoration: BoxDecoration(
                    color: color,
                    borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                  ),
                  child: Center(
                    child: Text(
                      '${percentage.toStringAsFixed(0)}%',
                      style: AppTheme.labelSmall.copyWith(
                        color: AppTheme.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Color _getCategoryColor(String category) {
    switch (category) {
      case '冲刺':
        return AppTheme.red;
      case '稳妥':
        return AppTheme.green;
      case '保底':
        return AppTheme.primaryBlue;
      case '垫底':
        return AppTheme.orange;
      default:
        return AppTheme.mediumGray;
    }
  }
}

/// 院校层次分布饼图（简化版）
class UniversityLevelPieChart extends StatelessWidget {
  final Map<String, int> levelDistribution;
  final String? title;

  const UniversityLevelPieChart({
    super.key,
    required this.levelDistribution,
    this.title,
  });

  @override
  Widget build(BuildContext context) {
    final totalCount = levelDistribution.values.fold(0, (sum, count) => sum + count);

    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingLg),
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        boxShadow: AppTheme.shadowLight,
        border: Border.all(
          color: AppTheme.surfaceContainerHighest,
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (title != null) ...[
            Row(
              children: [
                Icon(Icons.pie_chart_rounded, color: AppTheme.primaryBlue, size: 20),
                const SizedBox(width: AppTheme.spacingSm),
                Text(
                  title!,
                  style: AppTheme.titleSmall,
                ),
              ],
            ),
            const SizedBox(height: AppTheme.spacingMd),
          ],

          // 饼图（简化版：使用水平条形图）
          ...levelDistribution.entries.map((entry) {
            return _buildPieSlice(
              level: entry.key,
              count: entry.value,
              totalCount: totalCount,
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildPieSlice({
    required String level,
    required int count,
    required int totalCount,
  }) {
    final color = _getLevelColor(level);
    final percentage = totalCount > 0 ? (count / totalCount * 100) : 0.0;

    return Padding(
      padding: const EdgeInsets.only(bottom: AppTheme.spacingSm),
      child: Row(
        children: [
          // 图例
          Container(
            width: 16,
            height: 16,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          const SizedBox(width: AppTheme.spacingSm),

          // 层次名称
          SizedBox(
            width: 60,
            child: Text(
              level,
              style: AppTheme.bodySmall,
            ),
          ),

          // 数量
          Text(
            '$count所',
            style: AppTheme.bodySmall.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(width: AppTheme.spacingSm),

          // 进度条
          Expanded(
            child: Stack(
              children: [
                Container(
                  height: 8,
                  decoration: BoxDecoration(
                    color: AppTheme.lightGray,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                FractionallySizedBox(
                  widthFactor: percentage / 100,
                  child: Container(
                    height: 8,
                    decoration: BoxDecoration(
                      color: color,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                ),
              ],
            ),
          ),

          // 百分比
          SizedBox(
            width: 45,
            child: Text(
              '${percentage.toStringAsFixed(0)}%',
              style: AppTheme.labelSmall.copyWith(
                color: color,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }

  Color _getLevelColor(String level) {
    switch (level) {
      case '985':
        return const Color(0xFF1976D2); // 深蓝
      case '211':
        return const Color(0xFF4CAF50); // 绿色
      case '双一流':
        return const Color(0xFFFF9800); // 橙色
      default:
        return AppTheme.mediumGray;
    }
  }
}
