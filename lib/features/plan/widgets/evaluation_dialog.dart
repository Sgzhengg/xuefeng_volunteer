import 'package:flutter/material.dart';
import '../../../../shared/theme/app_theme.dart';
import '../../../../core/models/volunteer_plan.dart';

class EvaluationDialog extends StatelessWidget {
  final PlanEvaluation evaluation;

  const EvaluationDialog({
    super.key,
    required this.evaluation,
  });

  @override
  Widget build(BuildContext context) {
    // 根据风险等级获取颜色
    Color getRiskColor() {
      switch (evaluation.riskLevel) {
        case 'low':
          return AppTheme.green;
        case 'medium':
          return AppTheme.orange;
        case 'high':
          return AppTheme.red;
        default:
          return AppTheme.mediumGray;
      }
    }

    return Dialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
      ),
      child: Container(
        constraints: const BoxConstraints(
          maxWidth: 500,
          maxHeight: 600,
        ),
        padding: const EdgeInsets.all(AppTheme.spacingLg),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 标题栏
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '志愿表评估结果',
                  style: AppTheme.titleMedium.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),

            const SizedBox(height: AppTheme.spacingLg),

            // 总体评分
            _buildScoreSection(context, getRiskColor()),

            const SizedBox(height: AppTheme.spacingMd),

            // 志愿统计
            _buildStatisticsSection(),

            const SizedBox(height: AppTheme.spacingMd),

            // 风险预警
            if (evaluation.warnings.isNotEmpty) ...[
              _buildSectionTitle('⚠️ 风险预警', AppTheme.red),
              const SizedBox(height: AppTheme.spacingSm),
              ...evaluation.warnings.take(3).map((warning) => _buildWarningItem(warning)),
              if (evaluation.warnings.length > 3)
                Text(
                  '还有${evaluation.warnings.length - 3}个风险...',
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.mediumGray,
                  ),
                ),
              const SizedBox(height: AppTheme.spacingMd),
            ],

            // 改进建议
            _buildSectionTitle('💡 改进建议', AppTheme.primaryBlue),
            const SizedBox(height: AppTheme.spacingSm),
            ...evaluation.suggestions.take(3).map((suggestion) =>
              Padding(
                padding: const EdgeInsets.only(bottom: AppTheme.spacingSm),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('• ', style: TextStyle(color: AppTheme.primaryBlue)),
                    Expanded(
                      child: Text(
                        suggestion.content,
                        style: AppTheme.bodySmall,
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: AppTheme.spacingLg),

            // 确认按钮
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => Navigator.of(context).pop(),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryBlue,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                  ),
                ),
                child: const Text('知道了'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildScoreSection(BuildContext context, Color riskColor) {
    return Column(
      children: [
        Text(
          '总体评分',
          style: AppTheme.labelSmall.copyWith(
            color: AppTheme.mediumGray,
          ),
        ),
        const SizedBox(height: AppTheme.spacingSm),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 120,
                  height: 120,
                  child: CircularProgressIndicator(
                    value: evaluation.overallScore / 100,
                    valueColor: AlwaysStoppedAnimation<Color>(riskColor),
                    strokeWidth: 8,
                    backgroundColor: riskColor.withOpacity(0.1),
                  ),
                ),
                Positioned(
                  child: Text(
                    '${evaluation.overallScore}',
                    style: AppTheme.headlineMedium.copyWith(
                      color: riskColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: AppTheme.spacingSm),
        Text(
          '风险等级: ${evaluation.riskLevel.toUpperCase()}',
          style: AppTheme.bodyMedium.copyWith(
            color: riskColor,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildStatisticsSection() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        _buildStatItem('冲刺', evaluation.chongCount, AppTheme.orange),
        _buildStatItem('稳妥', evaluation.wenCount, AppTheme.primaryBlue),
        _buildStatItem('保底', evaluation.baoCount, AppTheme.green),
      ],
    );
  }

  Widget _buildStatItem(String label, int count, Color color) {
    return Column(
      children: [
        Text(
          '$count',
          style: AppTheme.headlineMedium.copyWith(
            color: color,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: AppTheme.labelSmall.copyWith(
            color: AppTheme.mediumGray,
          ),
        ),
      ],
    );
  }

  Widget _buildSectionTitle(String title, Color color) {
    return Text(
      title,
      style: AppTheme.labelSmall.copyWith(
        color: color,
        fontWeight: FontWeight.bold,
      ),
    );
  }

  Widget _buildWarningItem(Warning warning) {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingSm),
      margin: const EdgeInsets.only(bottom: AppTheme.spacingXs),
      decoration: BoxDecoration(
        color: warning.severity == 'high'
            ? AppTheme.errorBackground
            : AppTheme.warningBackground,
        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
        border: Border.all(
          color: warning.severity == 'high'
              ? AppTheme.errorBorder
              : AppTheme.warningBorder,
          width: 1,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            warning.severity == 'high' ? Icons.warning : Icons.info,
            size: 16,
            color: warning.severity == 'high' ? AppTheme.red : AppTheme.orange,
          ),
          const SizedBox(width: AppTheme.spacingXs),
          Expanded(
            child: Text(
              warning.message,
              style: AppTheme.bodySmall,
            ),
          ),
        ],
      ),
    );
  }
}
