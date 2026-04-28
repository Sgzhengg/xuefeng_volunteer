import 'package:flutter/material.dart';
import '../../recommendation/models/recommendation_models.dart';
import '../../../shared/theme/app_theme.dart';

/// 推荐结果详情页面
class RecommendationResultPage extends StatelessWidget {
  final RecommendationResult result;

  const RecommendationResultPage({
    super.key,
    required this.result,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('智能推荐结果'),
        actions: [
          IconButton(
            icon: const Icon(Icons.share_rounded),
            onPressed: () {
              // TODO: 分享功能
            },
          ),
          IconButton(
            icon: const Icon(Icons.download_rounded),
            onPressed: () {
              // TODO: 下载PDF功能
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppTheme.spacingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 基本信息卡片
            _buildBasicInfoCard(),
            const SizedBox(height: AppTheme.spacingMd),

            // 分析报告卡片
            _buildAnalysisCard(),
            const SizedBox(height: AppTheme.spacingMd),

            // 建议卡片
            _buildAdviceCard(),
            const SizedBox(height: AppTheme.spacingMd),

            // 推荐院校分类展示
            _buildRecommendationSection(),
          ],
        ),
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

          // 省份和分数
          _buildInfoRow('所在省份', result.basicInfo.province),
          const SizedBox(height: AppTheme.spacingSm),
          _buildInfoRow('高考分数', '${result.basicInfo.score}分'),
          const SizedBox(height: AppTheme.spacingSm),
          _buildInfoRow('全省位次', '第${result.basicInfo.rank}名'),
          const SizedBox(height: AppTheme.spacingSm),
          _buildInfoRow('报考科类', result.basicInfo.subjectType),
          const SizedBox(height: AppTheme.spacingSm),
          _buildInfoRow('目标专业', result.basicInfo.targetMajors.join('、')),
          const SizedBox(height: AppTheme.spacingSm),
          _buildInfoRow('生成时间', result.basicInfo.generatedAt),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Row(
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
    );
  }

  Widget _buildAnalysisCard() {
    final analysis = result.analysis;

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
              Icon(Icons.analytics_rounded, color: AppTheme.primaryBlue, size: 20),
              const SizedBox(width: AppTheme.spacingSm),
              Text(
                '分析报告',
                style: AppTheme.titleSmall.copyWith(
                  color: AppTheme.primaryBlue,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppTheme.spacingMd),

          // 统计信息
          Text(
            '共找到${analysis.totalCount}所院校',
            style: AppTheme.bodyMedium.copyWith(
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: AppTheme.spacingSm),

          // 类别分布
          Wrap(
            spacing: AppTheme.spacingSm,
            runSpacing: AppTheme.spacingSm,
            children: [
              _buildAnalysisChip('冲刺', analysis.categoryCounts['冲刺'] ?? 0, AppTheme.red),
              _buildAnalysisChip('稳妥', analysis.categoryCounts['稳妥'] ?? 0, AppTheme.green),
              _buildAnalysisChip('保底', analysis.categoryCounts['保底'] ?? 0, AppTheme.primaryBlue),
              _buildAnalysisChip('垫底', analysis.categoryCounts['垫底'] ?? 0, AppTheme.orange),
            ],
          ),

          // 分析点评
          if (analysis.comments.isNotEmpty) ...[
            const SizedBox(height: AppTheme.spacingMd),
            ...analysis.comments.map((comment) => Padding(
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
          ],
        ],
      ),
    );
  }

  Widget _buildAnalysisChip(String label, int count, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacingSm,
        vertical: AppTheme.spacingXs,
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
        '$label $count',
        style: AppTheme.labelSmall.copyWith(
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildAdviceCard() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingLg),
      decoration: BoxDecoration(
        color: AppTheme.successBackground,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border.all(
          color: AppTheme.successBorder,
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb_rounded, color: AppTheme.green, size: 20),
              const SizedBox(width: AppTheme.spacingSm),
              Text(
                '填报建议',
                style: AppTheme.titleSmall.copyWith(
                  color: AppTheme.green,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppTheme.spacingMd),

          ...result.advice.map((advice) => Padding(
            padding: const EdgeInsets.only(bottom: AppTheme.spacingXs),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('• ', style: AppTheme.bodySmall),
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

  Widget _buildRecommendationSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 冲刺院校
        if (result.chong.isNotEmpty) ...[
          _buildRecommendationCategory(
            icon: Icons.rocket_launch_rounded,
            title: '冲刺',
            count: result.chong.length,
            description: '高收益，低概率',
            color: AppTheme.red,
            recommendations: result.chong,
          ),
          const SizedBox(height: AppTheme.spacingMd),
        ],

        // 稳妥院校
        if (result.wen.isNotEmpty) ...[
          _buildRecommendationCategory(
            icon: Icons.verified_user_rounded,
            title: '稳妥',
            count: result.wen.length,
            description: '稳妥选择',
            color: AppTheme.green,
            recommendations: result.wen,
          ),
          const SizedBox(height: AppTheme.spacingMd),
        ],

        // 保底院校
        if (result.bao.isNotEmpty) ...[
          _buildRecommendationCategory(
            icon: Icons.anchor_rounded,
            title: '保底',
            count: result.bao.length,
            description: '基本没问题',
            color: AppTheme.primaryBlue,
            recommendations: result.bao,
          ),
          const SizedBox(height: AppTheme.spacingMd),
        ],

        // 垫底院校
        if (result.dian.isNotEmpty)
          _buildRecommendationCategory(
            icon: Icons.shield_rounded,
            title: '垫底',
            count: result.dian.length,
            description: '稳保录取',
            color: AppTheme.orange,
            recommendations: result.dian,
          ),
      ],
    );
  }

  Widget _buildRecommendationCategory({
    required IconData icon,
    required String title,
    required int count,
    required String description,
    required Color color,
    required List<UniversityRecommendation> recommendations,
  }) {
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
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(icon, color: color, size: 20),
                  const SizedBox(width: AppTheme.spacingXs),
                  Text(
                    '$title ($count)',
                    style: AppTheme.titleSmall.copyWith(
                      color: color,
                    ),
                  ),
                ],
              ),
              Text(
                description,
                style: AppTheme.bodySmall.copyWith(
                  color: AppTheme.mediumGray,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppTheme.spacingMd),

          ...recommendations.map((rec) => _buildRecommendationCard(rec, color)),
        ],
      ),
    );
  }

  Widget _buildRecommendationCard(UniversityRecommendation rec, Color color) {
    return GestureDetector(
      onTap: () {
        // TODO: 显示详细信息对话框
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
            // 院校名称和专业
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

                // 录取概率
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '${rec.probability}%',
                      style: AppTheme.headlineMedium.copyWith(
                        color: color,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: AppTheme.spacingXs),
                    Text(
                      '录取概率',
                      style: AppTheme.labelSmall.copyWith(
                        color: AppTheme.mediumGray,
                      ),
                    ),
                  ],
                ),
              ],
            ),

            const SizedBox(height: AppTheme.spacingSm),

            // 地点和层次
            Wrap(
              spacing: AppTheme.spacingXs,
              runSpacing: AppTheme.spacingXs,
              children: [
                _buildTag('${rec.province} ${rec.city}', AppTheme.mediumGray),
                _buildTag(rec.universityLevel, color),
                _buildTag(rec.universityType, AppTheme.mediumGray),
                _buildTag('一本', AppTheme.mediumGray),
              ],
            ),

            // 分数差距
            if (rec.scoreGap != 0) ...[
              const SizedBox(height: AppTheme.spacingSm),
              Text(
                '分数差距: ${rec.scoreGap > 0 ? '+' : ''}${rec.scoreGap}分',
                style: AppTheme.bodySmall.copyWith(
                  color: rec.scoreGap > 0
                      ? AppTheme.green
                      : rec.scoreGap < -10
                          ? AppTheme.red
                          : AppTheme.orange,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],

            // 建议
            if (rec.suggestions.isNotEmpty) ...[
              const SizedBox(height: AppTheme.spacingSm),
              ...rec.suggestions.take(2).map((suggestion) => Padding(
                padding: const EdgeInsets.only(bottom: AppTheme.spacingXs),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('• ', style: AppTheme.bodySmall),
                    Expanded(
                      child: Text(
                        suggestion,
                        style: AppTheme.bodySmall,
                      ),
                    ),
                  ],
                ),
              )),
            ],

            // 亮点信息
            if (rec.universityHighlights.isNotEmpty) ...[
              const SizedBox(height: AppTheme.spacingSm),
              Wrap(
                spacing: AppTheme.spacingXs,
                runSpacing: AppTheme.spacingXs,
                children: rec.universityHighlights.take(3).map((highlight) {
                  return Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: AppTheme.spacingXs,
                      vertical: 2,
                    ),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryBlue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                    ),
                    child: Text(
                      highlight,
                      style: AppTheme.labelSmall.copyWith(
                        color: AppTheme.primaryBlue,
                        fontSize: 10,
                      ),
                    ),
                  );
                }).toList(),
              ),
            ],

            // 就业信息
            if (rec.employmentInfo.topEmployers.isNotEmpty) ...[
              const SizedBox(height: AppTheme.spacingSm),
              Row(
                children: [
                  Icon(Icons.work_rounded, size: 14, color: AppTheme.mediumGray),
                  const SizedBox(width: AppTheme.spacingXs),
                  Text(
                    '主要雇主: ${rec.employmentInfo.topEmployers.take(3).join('、')}',
                    style: AppTheme.bodySmall.copyWith(
                      color: AppTheme.mediumGray,
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
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
