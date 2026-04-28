import 'package:flutter/material.dart';
import '../../../shared/theme/app_theme.dart';

/// 就业数据卡片
class EmploymentInfoCard extends StatelessWidget {
  final String employmentRate;
  final String averageSalary;
  final List<String> topEmployers;
  final String? graduateSchoolRate;

  const EmploymentInfoCard({
    super.key,
    required this.employmentRate,
    required this.averageSalary,
    required this.topEmployers,
    this.graduateSchoolRate,
  });

  @override
  Widget build(BuildContext context) {
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
              Icon(Icons.work_outline_rounded, color: AppTheme.primaryBlue, size: 20),
              const SizedBox(width: AppTheme.spacingSm),
              Text(
                '就业信息',
                style: AppTheme.titleSmall,
              ),
            ],
          ),
          const SizedBox(height: AppTheme.spacingMd),

          // 就业率
          _buildEmploymentRate(),
          const SizedBox(height: AppTheme.spacingMd),

          // 薪资水平
          _buildSalaryInfo(),
          const SizedBox(height: AppTheme.spacingMd),

          // 升学率
          if (graduateSchoolRate != null) ...[
            _buildGraduationRate(),
            const SizedBox(height: AppTheme.spacingMd),
          ],

          // 主要雇主
          _buildTopEmployers(),
        ],
      ),
    );
  }

  Widget _buildEmploymentRate() {
    // 解析就业率（去掉%）
    final rateStr = employmentRate.replaceAll('%', '');
    final rate = double.tryParse(rateStr) ?? 0.0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '就业率',
              style: AppTheme.labelSmall.copyWith(
                color: AppTheme.mediumGray,
              ),
            ),
            Text(
              employmentRate,
              style: AppTheme.titleSmall.copyWith(
                color: _getRateColor(rate),
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: AppTheme.spacingSm),
        Stack(
          children: [
            Container(
              height: 8,
              decoration: BoxDecoration(
                color: AppTheme.lightGray,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            FractionallySizedBox(
              widthFactor: rate / 100,
              child: Container(
                height: 8,
                decoration: BoxDecoration(
                  color: _getRateColor(rate),
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSalaryInfo() {
    // 解析薪资范围
    final salaryStr = averageSalary.replaceAll('元/月', '');
    final parts = salaryStr.split('-');
    final minSalary = int.tryParse(parts[0].trim()) ?? 0;
    final maxSalary = parts.length > 1 ? int.tryParse(parts[1].trim()) ?? minSalary : minSalary;
    final avgSalary = (minSalary + maxSalary) / 2;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '平均薪资',
          style: AppTheme.labelSmall.copyWith(
            color: AppTheme.mediumGray,
          ),
        ),
        const SizedBox(height: AppTheme.spacingSm),
        Text(
          averageSalary,
          style: AppTheme.titleSmall.copyWith(
            color: AppTheme.green,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: AppTheme.spacingSm),
        // 薪资水平指示器
        _buildSalaryIndicator(avgSalary),
      ],
    );
  }

  Widget _buildSalaryIndicator(double avgSalary) {
    // 简单的薪资水平指示
    String level;
    Color color;
    double percentage;

    if (avgSalary >= 15000) {
      level = '非常高';
      color = AppTheme.green;
      percentage = 0.9;
    } else if (avgSalary >= 10000) {
      level = '较高';
      color = AppTheme.primaryBlue;
      percentage = 0.7;
    } else if (avgSalary >= 8000) {
      level = '中等';
      color = AppTheme.orange;
      percentage = 0.5;
    } else {
      level = '一般';
      color = AppTheme.mediumGray;
      percentage = 0.3;
    }

    return Row(
      children: [
        Text(
          '水平：',
          style: AppTheme.labelSmall.copyWith(
            color: AppTheme.mediumGray,
          ),
        ),
        Text(
          level,
          style: AppTheme.labelSmall.copyWith(
            color: color,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(width: AppTheme.spacingSm),
        Expanded(
          child: Stack(
            children: [
              Container(
                height: 4,
                decoration: BoxDecoration(
                  color: AppTheme.lightGray,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              FractionallySizedBox(
                widthFactor: percentage,
                child: Container(
                  height: 4,
                  decoration: BoxDecoration(
                    color: color,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildGraduationRate() {
    // 解析升学率
    final rateStr = graduateSchoolRate!.replaceAll('%', '');
    final rate = double.tryParse(rateStr) ?? 0.0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '考研率',
              style: AppTheme.labelSmall.copyWith(
                color: AppTheme.mediumGray,
              ),
            ),
            Text(
              graduateSchoolRate!,
              style: AppTheme.titleSmall.copyWith(
                color: AppTheme.primaryBlue,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: AppTheme.spacingSm),
        Stack(
          children: [
            Container(
              height: 6,
              decoration: BoxDecoration(
                color: AppTheme.lightGray,
                borderRadius: BorderRadius.circular(3),
              ),
            ),
            FractionallySizedBox(
              widthFactor: rate / 100,
              child: Container(
                height: 6,
                decoration: BoxDecoration(
                  color: AppTheme.primaryBlue,
                  borderRadius: BorderRadius.circular(3),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildTopEmployers() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '主要雇主 (${topEmployers.length})',
          style: AppTheme.labelSmall.copyWith(
            color: AppTheme.mediumGray,
          ),
        ),
        const SizedBox(height: AppTheme.spacingSm),
        Wrap(
          spacing: AppTheme.spacingSm,
          runSpacing: AppTheme.spacingSm,
          children: topEmployers.take(5).map((employer) {
            return Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AppTheme.spacingSm,
                vertical: AppTheme.spacingXs,
              ),
              decoration: BoxDecoration(
                color: AppTheme.primaryBlue.withOpacity(0.1),
                borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                border: Border.all(
                  color: AppTheme.primaryBlue.withOpacity(0.3),
                  width: 1,
                ),
              ),
              child: Text(
                employer,
                style: AppTheme.labelSmall.copyWith(
                  color: AppTheme.primaryBlue,
                  fontSize: 11,
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Color _getRateColor(double rate) {
    if (rate >= 95) return AppTheme.green;
    if (rate >= 90) return AppTheme.primaryBlue;
    if (rate >= 85) return AppTheme.orange;
    return AppTheme.mediumGray;
  }
}
