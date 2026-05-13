import 'package:flutter/material.dart';
import '../../../../shared/theme/app_theme.dart';
import '../../../../core/models/volunteer_plan.dart';

class PlanCard extends StatelessWidget {
  final VolunteerPlan plan;
  final VoidCallback? onDelete;
  final bool isEditMode;

  const PlanCard({
    super.key,
    required this.plan,
    this.onDelete,
    this.isEditMode = false,
  });

  @override
  Widget build(BuildContext context) {
    // 根据值得指数获取颜色
    Color getRoiColor() {
      if (plan.roiScore >= 80) return AppTheme.green;
      if (plan.roiScore >= 60) return AppTheme.primaryBlue;
      if (plan.roiScore >= 40) return AppTheme.orange;
      return AppTheme.red;
    }

    // 根据录取概率获取颜色
    Color getProbabilityColor() {
      if (plan.probability >= 75) return AppTheme.green;
      if (plan.probability >= 50) return AppTheme.primaryBlue;
      if (plan.probability >= 30) return AppTheme.orange;
      return AppTheme.red;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: AppTheme.spacingSm),
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border(
          left: BorderSide(
            color: getProbabilityColor(),
            width: 4,
          ),
        ),
        boxShadow: AppTheme.shadowLight,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 院校名称和专业
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      plan.universityName,
                      style: AppTheme.titleSmall.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: AppTheme.spacingXs),
                    Text(
                      plan.majorName,
                      style: AppTheme.bodySmall.copyWith(
                        color: AppTheme.mediumGray,
                      ),
                    ),
                  ],
                ),
              ),

              // 删除按钮（编辑模式时显示或onDelete存在时显示）
              if ((isEditMode && onDelete != null) || (onDelete != null))
                IconButton(
                  icon: const Icon(Icons.close, color: AppTheme.red),
                  onPressed: onDelete,
                  tooltip: '删除',
                ),

              // 录取概率和值得指数
              if (!isEditMode) ...[
                const SizedBox(width: AppTheme.spacingSm),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    // 录取概率
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          '${plan.probability}%',
                          style: AppTheme.titleSmall.copyWith(
                            color: getProbabilityColor(),
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(width: AppTheme.spacingXs),
                        Text(
                          '概率',
                          style: AppTheme.labelSmall.copyWith(
                            color: AppTheme.mediumGray,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: AppTheme.spacingXs),
                    // 值得指数
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: AppTheme.spacingSm,
                        vertical: AppTheme.spacingXs,
                      ),
                      decoration: BoxDecoration(
                        color: getRoiColor().withOpacity(0.1),
                        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                        border: Border.all(
                          color: getRoiColor(),
                          width: 1,
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            '${plan.roiScore}分',
                            style: AppTheme.titleSmall.copyWith(
                              color: getRoiColor(),
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(width: AppTheme.spacingXs),
                          Text(
                            plan.roiLevel,
                            style: AppTheme.labelSmall.copyWith(
                              color: getRoiColor(),
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),

          const SizedBox(height: AppTheme.spacingSm),

          // 地点和类型
          Wrap(
            spacing: AppTheme.spacingXs,
            runSpacing: AppTheme.spacingXs,
            children: [
              _buildTag('${plan.city} ${plan.universityType}', AppTheme.mediumGray),
              if (plan.tag.isNotEmpty)
                _buildTag(plan.tag, getProbabilityColor()),
            ],
          ),
        ],
      ),
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
}
