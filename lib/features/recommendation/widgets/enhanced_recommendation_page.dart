import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/recommendation_models.dart';
import '../controllers/pdf_export_controller.dart';
import '../../../shared/theme/app_theme.dart';
import 'probability_charts.dart';
import 'employment_charts.dart';
import 'distribution_charts.dart';
import 'statistics_overview_card.dart';

/// PDF Export Controller Provider
final pdfExportControllerProvider = ChangeNotifierProvider<PDFExportController>((ref) {
  return PDFExportController();
});

/// 增强版推荐结果页面（含数据可视化）
class EnhancedRecommendationResultPage extends ConsumerWidget {
  final RecommendationResult result;

  const EnhancedRecommendationResultPage({
    super.key,
    required this.result,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pdfController = ref.watch(pdfExportControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('智能推荐结果'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () {
              // TODO: 刷新推荐
            },
          ),
          IconButton(
            icon: const Icon(Icons.share_rounded),
            onPressed: () => _showShareDialog(context, pdfController),
          ),
          IconButton(
            icon: const Icon(Icons.picture_as_pdf_rounded),
            onPressed: pdfController.isExporting
                ? null
                : () => _showExportDialog(context, pdfController),
          ),
        ],
      ),
      body: DefaultTabController(
        length: 3,
        child: Column(
          children: [
            // Tab栏
            Container(
              color: AppTheme.surfaceContainerHighest,
              child: TabBar(
                labelColor: AppTheme.mediumGray,
                unselectedLabelColor: AppTheme.mediumGray,
                indicatorColor: AppTheme.primaryBlue,
                tabs: const [
                  Tab(text: '推荐方案'),
                  Tab(text: '数据分析'),
                  Tab(text: '详细对比'),
                ],
              ),
            ),

            // Tab内容
            Expanded(
              child: TabBarView(
                children: [
                  _buildRecommendationTab(),
                  _buildAnalysisTab(),
                  _buildComparisonTab(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 推荐方案Tab
  Widget _buildRecommendationTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 统计概览
          StatisticsOverviewCard(result: result),
          const SizedBox(height: AppTheme.spacingMd),

          // 基本信息
          _buildBasicInfoCard(),
          const SizedBox(height: AppTheme.spacingMd),

          // 分析建议
          _buildAnalysisCard(),
          const SizedBox(height: AppTheme.spacingMd),

          // 推荐列表
          _buildRecommendationList(),
        ],
      ),
    );
  }

  // 数据分析Tab
  Widget _buildAnalysisTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 统计概览
          StatisticsOverviewCard(result: result),
          const SizedBox(height: AppTheme.spacingMd),

          // 就业数据统计
          _buildEmploymentStats(),
          const SizedBox(height: AppTheme.spacingMd),

          // 概率分布统计
          _buildProbabilityStats(),
        ],
      ),
    );
  }

  // 详细对比Tab
  Widget _buildComparisonTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 院校对比
          UniversityComparisonCard(
            title: '院校对比分析',
            recommendations: result.getAllRecommendations(),
          ),
          const SizedBox(height: AppTheme.spacingMd),

          // 按类别对比
          ...['冲刺', '稳妥', '保底', '垫底'].map((category) {
            return _buildCategoryComparison(category);
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildBasicInfoCard() {
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
          Row(
            children: [
              Container(
                width: 4,
                height: 24,
                decoration: const BoxDecoration(
                  color: AppTheme.primaryBlue,
                  borderRadius: BorderRadius.only(
                    topRight: Radius.circular(AppTheme.radiusSm),
                    bottomRight: Radius.circular(AppTheme.radiusSm),
                  ),
                ),
              ),
              const SizedBox(width: AppTheme.spacingSm),
              Text(
                '考生信息',
                style: AppTheme.titleSmall,
              ),
            ],
          ),
          const SizedBox(height: AppTheme.spacingMd),
          _buildInfoRow('所在省份', result.basicInfo.province),
          _buildInfoRow('高考分数', '${result.basicInfo.score}分'),
          _buildInfoRow('全省位次', '第${result.basicInfo.rank}名'),
          _buildInfoRow('报考科类', result.basicInfo.subjectType),
          _buildInfoRow('目标专业', result.basicInfo.targetMajors.join('、')),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppTheme.spacingSm),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: AppTheme.bodyMedium.copyWith(
                color: AppTheme.mediumGray,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: AppTheme.bodyMedium.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalysisCard() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingLg),
      decoration: BoxDecoration(
        color: AppTheme.infoBackground,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border.all(
          color: AppTheme.primaryBlue.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb_rounded, color: AppTheme.primaryBlue, size: 20),
              const SizedBox(width: AppTheme.spacingSm),
              Text(
                '分析建议',
                style: AppTheme.titleSmall.copyWith(
                  color: AppTheme.primaryBlue,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppTheme.spacingMd),

          // 分析点评
          if (result.analysis.comments.isNotEmpty)
            ...result.analysis.comments.map((comment) => Padding(
              padding: const EdgeInsets.only(bottom: AppTheme.spacingXs),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('• ', style: AppTheme.bodySmall),
                  Expanded(
                    child: Text(
                      comment,
                      style: AppTheme.bodySmall,
                    ),
                  ),
                ],
              ),
            )),

          const SizedBox(height: AppTheme.spacingMd),

          // 填报建议
          ...result.advice.take(5).map((advice) => Padding(
            padding: const EdgeInsets.only(bottom: AppTheme.spacingXs),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.check_circle_rounded,
                    size: 14, color: AppTheme.green),
                const SizedBox(width: AppTheme.spacingXs),
                Expanded(
                  child: Text(
                    advice,
                    style: AppTheme.bodySmall,
                  ),
                ),
              ],
            ),
          )),
        ],
      ),
    );
  }

  Widget _buildRecommendationList() {
    return Column(
      children: [
        // 冲刺院校
        if (result.chong.isNotEmpty) ...[
          _buildCategorySection('冲刺', result.chong, AppTheme.red, Icons.rocket_launch_rounded),
          const SizedBox(height: AppTheme.spacingMd),
        ],

        // 稳妥院校
        if (result.wen.isNotEmpty) ...[
          _buildCategorySection('稳妥', result.wen, AppTheme.green, Icons.verified_user_rounded),
          const SizedBox(height: AppTheme.spacingMd),
        ],

        // 保底院校
        if (result.bao.isNotEmpty) ...[
          _buildCategorySection('保底', result.bao, AppTheme.primaryBlue, Icons.anchor_rounded),
          const SizedBox(height: AppTheme.spacingMd),
        ],

        // 垫底院校
        if (result.dian.isNotEmpty)
          _buildCategorySection('垫底', result.dian, AppTheme.orange, Icons.shield_rounded),
      ],
    );
  }

  Widget _buildCategorySection(
    String title,
    List<UniversityRecommendation> recs,
    Color color,
    IconData icon,
  ) {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      decoration: BoxDecoration(
        color: color.withOpacity(0.05),
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border.all(
          color: color.withOpacity(0.2),
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: AppTheme.spacingXs),
              Text(
                '$title (${recs.length})',
                style: AppTheme.titleSmall.copyWith(
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppTheme.spacingMd),

          ...recs.map((rec) => _buildRecommendationCard(rec, color)),
        ],
      ),
    );
  }

  Widget _buildRecommendationCard(UniversityRecommendation rec, Color color) {
    return GestureDetector(
      onTap: () {
        // TODO: 显示详情对话框
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: AppTheme.spacingSm),
        padding: const EdgeInsets.all(AppTheme.spacingMd),
        decoration: BoxDecoration(
          color: AppTheme.surfaceContainerLowest,
          borderRadius: BorderRadius.circular(AppTheme.radiusLg),
          border: Border(
            left: BorderSide(
              color: color,
              width: 4,
            ),
          ),
          boxShadow: AppTheme.shadowLight,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 标题行
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        rec.universityName,
                        style: AppTheme.titleSmall.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: AppTheme.spacingXs),
                      Text(
                        rec.major,
                        style: AppTheme.bodySmall.copyWith(
                          color: AppTheme.mediumGray,
                        ),
                      ),
                    ],
                  ),
                ),

                // 录取概率环形图
                ProbabilityCircularChart(
                  probability: rec.probability,
                  size: 60,
                ),
              ],
            ),

            const SizedBox(height: AppTheme.spacingSm),

            // 详细信息
            _buildRecDetails(rec, color),
          ],
        ),
      ),
    );
  }

  Widget _buildRecDetails(UniversityRecommendation rec, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 地点和层次
        Wrap(
          spacing: AppTheme.spacingXs,
          runSpacing: AppTheme.spacingXs,
          children: [
            _buildTag('${rec.province} ${rec.city}', AppTheme.mediumGray),
            _buildTag(rec.universityLevel, color),
            _buildTag(rec.universityType, AppTheme.mediumGray),
          ],
        ),

        // 进度条
        const SizedBox(height: AppTheme.spacingSm),
        ProbabilityProgressBar(
          probability: rec.probability,
          height: 6,
        ),

        // 就业信息预览
        if (rec.employmentInfo.topEmployers.isNotEmpty) ...[
          const SizedBox(height: AppTheme.spacingSm),
          Row(
            children: [
              Icon(Icons.work_outline_rounded,
                  size: 14, color: AppTheme.mediumGray),
              const SizedBox(width: AppTheme.spacingXs),
              Expanded(
                child: Text(
                  '主要雇主: ${rec.employmentInfo.topEmployers.take(2).join('、')}...',
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.mediumGray,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }

  Widget _buildTag(String label, Color color) {
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
        label,
        style: AppTheme.labelSmall.copyWith(
          color: color,
          fontSize: 10,
        ),
      ),
    );
  }

  Widget _buildEmploymentStats() {
    // 汇总所有院校的就业数据
    final allRecs = result.getAllRecommendations();
    if (allRecs.isEmpty) {
      return const SizedBox.shrink();
    }

    // 计算平均就业率
    double avgEmploymentRate = 0.0;
    double avgSalary = 0.0;

    final validRecs = allRecs.where((r) =>
        r.employmentInfo.employmentRate != '未知').toList();

    if (validRecs.isNotEmpty) {
      double totalRate = 0.0;
      for (final rec in validRecs) {
        final rateStr = rec.employmentInfo.employmentRate.replaceAll('%', '');
        totalRate += double.tryParse(rateStr) ?? 0.0;
      }
      avgEmploymentRate = totalRate / validRecs.length;
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
          Row(
            children: [
              Icon(Icons.trending_up_rounded,
                  color: AppTheme.green, size: 20),
              const SizedBox(width: AppTheme.spacingSm),
              Text(
                '就业数据统计',
                style: AppTheme.titleSmall,
              ),
            ],
          ),
          const SizedBox(height: AppTheme.spacingMd),

          // 平均就业率
          _buildStatCard(
            icon: Icons.work_rounded,
            label: '平均就业率',
            value: '${avgEmploymentRate.toStringAsFixed(1)}%',
            color: AppTheme.green,
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 代表性院校就业信息
          UniversityComparisonCard(
            title: '代表性院校就业信息',
            recommendations: allRecs.take(3).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      decoration: BoxDecoration(
        color: color.withOpacity(0.05),
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border.all(
          color: color.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(width: AppTheme.spacingMd),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
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
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProbabilityStats() {
    final allRecs = result.getAllRecommendations();

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
          Row(
            children: [
              Icon(Icons.show_chart_rounded,
                  color: AppTheme.primaryBlue, size: 20),
              const SizedBox(width: AppTheme.spacingSm),
              Text(
                '录取概率统计',
                style: AppTheme.titleSmall,
              ),
            ],
          ),
          const SizedBox(height: AppTheme.spacingMd),

          // 概率分布
          UniversityDistributionChart(
            title: '概率分布',
            distribution: _calculateProbabilityDistribution(allRecs),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryComparison(String category) {
    List<UniversityRecommendation> recs;

    switch (category) {
      case '冲刺':
        recs = result.chong;
        break;
      case '稳妥':
        recs = result.wen;
        break;
      case '保底':
        recs = result.bao;
        break;
      case '垫底':
        recs = result.dian;
        break;
      default:
        recs = [];
    }

    if (recs.isEmpty) {
      return const SizedBox.shrink();
    }

    return UniversityComparisonCard(
      title: '$category院校对比',
      recommendations: recs,
    );
  }

  Map<String, int> _calculateProbabilityDistribution(List<UniversityRecommendation> recs) {
    final distribution = <String, int>{
      '高概率(≥75%)': 0,
      '中概率(50-75%)': 0,
      '低概率(<50%)': 0,
    };

    for (final rec in recs) {
      if (rec.probability >= 75) {
        distribution['高概率(≥75%)'] = distribution['高概率(≥75%)']! + 1;
      } else if (rec.probability >= 50) {
        distribution['中概率(50-75%)'] = distribution['中概率(50-75%)']! + 1;
      } else {
        distribution['低概率(<50%)'] = distribution['低概率(<50%)']! + 1;
      }
    }

    return distribution;
  }

  /// Show export dialog
  void _showExportDialog(BuildContext context, PDFExportController controller) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.picture_as_pdf_rounded, color: AppTheme.primaryBlue),
            SizedBox(width: AppTheme.spacingXs),
            Text('导出报告'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '选择导出格式：',
              style: AppTheme.bodyMedium,
            ),
            SizedBox(height: AppTheme.spacingMd),
            _buildExportOption(
              context: context,
              icon: Icons.picture_as_pdf_rounded,
              title: 'PDF 格式',
              subtitle: '专业排版，适合打印和存档',
              color: AppTheme.red,
              onTap: () {
                Navigator.of(context).pop();
                controller.exportToPDF(
                  result: result,
                  context: context,
                );
              },
            ),
            SizedBox(height: AppTheme.spacingSm),
            _buildExportOption(
              context: context,
              icon: Icons.code_rounded,
              title: 'HTML 格式',
              subtitle: '网页格式，可在浏览器中查看',
              color: AppTheme.primaryBlue,
              onTap: () {
                Navigator.of(context).pop();
                controller.exportToHTML(
                  result: result,
                  context: context,
                );
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('取消'),
          ),
        ],
      ),
    );
  }

  /// Show share dialog
  void _showShareDialog(BuildContext context, PDFExportController controller) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.share_rounded, color: AppTheme.primaryBlue),
            SizedBox(width: AppTheme.spacingXs),
            Text('分享报告'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '选择分享格式：',
              style: AppTheme.bodyMedium,
            ),
            SizedBox(height: AppTheme.spacingMd),
            _buildExportOption(
              context: context,
              icon: Icons.picture_as_pdf_rounded,
              title: 'PDF 格式',
              subtitle: '专业排版，适合分享给老师或家长',
              color: AppTheme.red,
              onTap: () {
                Navigator.of(context).pop();
                controller.sharePDF(
                  result: result,
                  context: context,
                );
              },
            ),
            SizedBox(height: AppTheme.spacingSm),
            _buildExportOption(
              context: context,
              icon: Icons.code_rounded,
              title: 'HTML 格式',
              subtitle: '网页格式，可在线查看',
              color: AppTheme.primaryBlue,
              onTap: () {
                Navigator.of(context).pop();
                controller.shareHTML(
                  result: result,
                  context: context,
                );
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('取消'),
          ),
        ],
      ),
    );
  }

  /// Build export option widget
  Widget _buildExportOption({
    required BuildContext context,
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(AppTheme.radiusLg),
      child: Container(
        padding: EdgeInsets.all(AppTheme.spacingMd),
        decoration: BoxDecoration(
          color: color.withOpacity(0.05),
          borderRadius: BorderRadius.circular(AppTheme.radiusLg),
          border: Border.all(
            color: color.withOpacity(0.2),
            width: 1,
          ),
        ),
        child: Row(
          children: [
            Icon(icon, color: color, size: 32),
            SizedBox(width: AppTheme.spacingMd),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: AppTheme.titleSmall.copyWith(
                      color: color,
                    ),
                  ),
                  SizedBox(height: AppTheme.spacingXs),
                  Text(
                    subtitle,
                    style: AppTheme.bodySmall.copyWith(
                      color: AppTheme.mediumGray,
                    ),
                  ),
                ],
              ),
            ),
            Icon(Icons.arrow_forward_ios_rounded,
                size: 16, color: AppTheme.mediumGray),
          ],
        ),
      ),
    );
  }
}
