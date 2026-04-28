import 'package:flutter/material.dart';
import '../../../shared/theme/app_theme.dart';
import 'probability_charts.dart';
import 'employment_charts.dart';
import 'distribution_charts.dart';
import '../../recommendation/models/recommendation_models.dart';

/// 统计概览卡片
class StatisticsOverviewCard extends StatelessWidget {
  final RecommendationResult result;

  const StatisticsOverviewCard({
    super.key,
    required this.result,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingLg),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppTheme.primaryBlue.withOpacity(0.05),
            AppTheme.surfaceContainerLowest,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border.all(
          color: AppTheme.primaryBlue.withOpacity(0.2),
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题
          Row(
            children: [
              Icon(Icons.analytics_rounded, color: AppTheme.primaryBlue, size: 24),
              const SizedBox(width: AppTheme.spacingSm),
              Text(
                '数据统计概览',
                style: AppTheme.titleSmall.copyWith(
                  color: AppTheme.primaryBlue,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppTheme.spacingLg),

          // 基本统计
          _buildBasicStats(),
          const SizedBox(height: AppTheme.spacingLg),

          // 图表区域
          _buildCharts(),
        ],
      ),
    );
  }

  Widget _buildBasicStats() {
    final totalCount = result.analysis.totalCount;

    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildStatItem(
              icon: Icons.school_rounded,
              label: '总院校',
              value: '$totalCount',
              color: AppTheme.primaryBlue,
            ),
            _buildStatItem(
              icon: Icons.location_on_rounded,
              label: '省份',
              value: result.basicInfo.province,
              color: AppTheme.green,
            ),
            _buildStatItem(
              icon: Icons.star_rounded,
              label: '专业数',
              value: '${result.basicInfo.targetMajors.length}',
              color: AppTheme.orange,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Column(
      children: [
        Icon(icon, color: color, size: 32),
        const SizedBox(height: AppTheme.spacingXs),
        Text(
          label,
          style: AppTheme.labelSmall.copyWith(
            color: AppTheme.mediumGray,
          ),
        ),
        const SizedBox(height: AppTheme.spacingXs),
        Text(
          value,
          style: AppTheme.headlineMedium.copyWith(
            color: color,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildCharts() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 院校分布图表
        UniversityDistributionChart(
          title: '院校分布',
          distribution: result.analysis.categoryCounts,
        ),
        const SizedBox(height: AppTheme.spacingMd),

        // 层次分布图表
        UniversityLevelPieChart(
          title: '层次分布',
          levelDistribution: _calculateLevelDistribution(),
        ),
        const SizedBox(height: AppTheme.spacingMd),

        // 平均录取概率环形图
        _buildAverageProbabilityChart(),
      ],
    );
  }

  Widget _buildAverageProbabilityChart() {
    final allRecs = result.getAllRecommendations();
    if (allRecs.isEmpty) {
      return const SizedBox.shrink();
    }

    final avgProbability = allRecs
        .map((r) => r.probability)
        .reduce((a, b) => a + b) / allRecs.length;

    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border.all(
          color: AppTheme.surfaceContainerHighest,
          width: 1,
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          Column(
            children: [
              Text(
                '平均录取概率',
                style: AppTheme.labelSmall.copyWith(
                  color: AppTheme.mediumGray,
                ),
              ),
              const SizedBox(height: AppTheme.spacingSm),
              ProbabilityCircularChart(
                probability: avgProbability.toInt(),
                size: 100,
              ),
            ],
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '概率分析',
                style: AppTheme.labelSmall.copyWith(
                  color: AppTheme.mediumGray,
                ),
              ),
              const SizedBox(height: AppTheme.spacingSm),
              _buildProbabilityAnalysis(allRecs),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildProbabilityAnalysis(List<UniversityRecommendation> recs) {
    final highProb = recs.where((r) => r.probability >= 75).length;
    final medProb = recs.where((r) => r.probability >= 50 && r.probability < 75).length;
    final lowProb = recs.where((r) => r.probability < 50).length;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildProbItem('高概率(≥75%)', highProb, AppTheme.green),
        const SizedBox(height: AppTheme.spacingXs),
        _buildProbItem('中概率(50-75%)', medProb, AppTheme.primaryBlue),
        const SizedBox(height: AppTheme.spacingXs),
        _buildProbItem('低概率(<50%)', lowProb, AppTheme.orange),
      ],
    );
  }

  Widget _buildProbItem(String label, int count, Color color) {
    return Row(
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: AppTheme.spacingXs),
        Text(
          label,
          style: AppTheme.labelSmall.copyWith(
            color: AppTheme.mediumGray,
          ),
        ),
        const SizedBox(width: AppTheme.spacingXs),
        Text(
          '$count',
          style: AppTheme.labelSmall.copyWith(
            color: color,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Map<String, int> _calculateLevelDistribution() {
    final levelCounts = <String, int>{};

    for (final rec in result.getAllRecommendations()) {
      final level = rec.universityLevel;
      levelCounts[level] = (levelCounts[level] ?? 0) + 1;
    }

    return levelCounts;
  }
}

/// 院校对比卡片
class UniversityComparisonCard extends StatelessWidget {
  final List<UniversityRecommendation> recommendations;
  final String? title;

  const UniversityComparisonCard({
    super.key,
    required this.recommendations,
    this.title,
  });

  @override
  Widget build(BuildContext context) {
    if (recommendations.isEmpty) {
      return const SizedBox.shrink();
    }

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
                Icon(Icons.compare_rounded, color: AppTheme.primaryBlue, size: 20),
                const SizedBox(width: AppTheme.spacingSm),
                Text(
                  title!,
                  style: AppTheme.titleSmall,
                ),
              ],
            ),
            const SizedBox(height: AppTheme.spacingMd),
          ],

          // 对比表格
          _buildComparisonTable(),
        ],
      ),
    );
  }

  Widget _buildComparisonTable() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        columnSpacing: AppTheme.spacingMd,
        horizontalMargin: 0,
        headingRowHeight: 40,
        dataRowHeight: 60,
        columns: const [
          DataColumn(
            label: Text('院校'),
          ),
          DataColumn(
            label: Text('层次'),
          ),
          DataColumn(
            label: Text('概率'),
          ),
          DataColumn(
            label: Text('分差'),
          ),
          DataColumn(
            label: Text('就业率'),
          ),
        ],
        rows: recommendations.take(5).map((rec) {
          return DataRow(
            cells: [
              DataCell(
                SizedBox(
                  width: 100,
                  child: Text(
                    rec.universityName,
                    style: AppTheme.bodySmall.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ),
              DataCell(
                _buildLevelTag(rec.universityLevel),
              ),
              DataCell(
                Text(
                  '${rec.probability}%',
                  style: AppTheme.bodySmall.copyWith(
                    color: _getProbColor(rec.probability),
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              DataCell(
                Text(
                  '${rec.scoreGap > 0 ? '+' : ''}${rec.scoreGap}',
                  style: AppTheme.bodySmall.copyWith(
                    color: rec.scoreGap > 0
                        ? AppTheme.green
                        : rec.scoreGap < -10
                            ? AppTheme.red
                            : AppTheme.orange,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              DataCell(
                Text(
                  rec.employmentInfo.employmentRate,
                  style: AppTheme.bodySmall,
                ),
              ),
            ],
          );
        }).toList(),
      ),
    );
  }

  Widget _buildLevelTag(String level) {
    Color color;

    switch (level) {
      case '985':
        color = const Color(0xFF1976D2);
        break;
      case '211':
        color = const Color(0xFF4CAF50);
        break;
      default:
        color = AppTheme.mediumGray;
    }

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacingXs,
        vertical: 2,
      ),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Text(
        level,
        style: AppTheme.labelSmall.copyWith(
          color: color,
          fontSize: 10,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Color _getProbColor(int prob) {
    if (prob >= 75) return AppTheme.green;
    if (prob >= 50) return AppTheme.primaryBlue;
    if (prob >= 30) return AppTheme.orange;
    return AppTheme.red;
  }
}
