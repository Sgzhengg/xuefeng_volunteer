import 'package:flutter/material.dart';
import '../../../shared/theme/app_theme.dart';

/// 录取概率进度条
class ProbabilityProgressBar extends StatelessWidget {
  final int probability;
  final String? label;
  final bool showPercentage;
  final double? height;

  const ProbabilityProgressBar({
    super.key,
    required this.probability,
    this.label,
    this.showPercentage = true,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    final color = _getProbabilityColor(probability);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (label != null) ...[
          Text(
            label!,
            style: AppTheme.labelSmall.copyWith(
              color: AppTheme.mediumGray,
            ),
          ),
          const SizedBox(height: AppTheme.spacingXs),
        ],
        Row(
          children: [
            Expanded(
              child: Stack(
                children: [
                  Container(
                    height: height ?? 8,
                    decoration: BoxDecoration(
                      color: AppTheme.lightGray,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                  FractionallySizedBox(
                    widthFactor: probability / 100,
                    child: Container(
                      height: height ?? 8,
                      decoration: BoxDecoration(
                        color: color,
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            if (showPercentage) ...[
              const SizedBox(width: AppTheme.spacingSm),
              SizedBox(
                width: 50,
                child: Text(
                  '$probability%',
                  style: AppTheme.labelSmall.copyWith(
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.right,
                ),
              ),
            ],
          ],
        ),
      ],
    );
  }

  Color _getProbabilityColor(int prob) {
    if (prob >= 75) return AppTheme.green;
    if (prob >= 50) return AppTheme.primaryBlue;
    if (prob >= 30) return AppTheme.orange;
    return AppTheme.red;
  }
}

/// 录取概率环形图
class ProbabilityCircularChart extends StatelessWidget {
  final int probability;
  final String? centerText;
  final double size;

  const ProbabilityCircularChart({
    super.key,
    required this.probability,
    this.centerText,
    this.size = 120,
  });

  @override
  Widget build(BuildContext context) {
    final color = _getProbabilityColor(probability);

    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        children: [
          // 背景圆环
          SizedBox(
            width: size,
            height: size,
            child: CircularProgressIndicator(
              value: 1,
              strokeWidth: 12,
              backgroundColor: AppTheme.lightGray,
              valueColor: AlwaysStoppedAnimation<Color>(
                AppTheme.lightGray,
              ),
            ),
          ),
          // 进度圆环
          SizedBox(
            width: size,
            height: size,
            child: CircularProgressIndicator(
              value: probability / 100,
              strokeWidth: 12,
              backgroundColor: Colors.transparent,
              valueColor: AlwaysStoppedAnimation<Color>(color),
            ),
          ),
          // 中心文字
          Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  centerText ?? '$probability%',
                  style: AppTheme.headlineMedium.copyWith(
                    color: color,
                    fontWeight: FontWeight.bold,
                    fontSize: size * 0.15,
                  ),
                ),
                Text(
                  '录取概率',
                  style: AppTheme.labelSmall.copyWith(
                    color: AppTheme.mediumGray,
                    fontSize: size * 0.08,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Color _getProbabilityColor(int prob) {
    if (prob >= 75) return AppTheme.green;
    if (prob >= 50) return AppTheme.primaryBlue;
    if (prob >= 30) return AppTheme.orange;
    return AppTheme.red;
  }
}
