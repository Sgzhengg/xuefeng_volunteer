import 'package:flutter/material.dart';
import '../../shared/theme/app_theme.dart';

class DataSourcePage extends StatelessWidget {
  const DataSourcePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surfaceColor,
      appBar: AppBar(
        title: const Text('数据来源说明'),
        backgroundColor: AppTheme.primaryBlue,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(AppTheme.spacingMd),
        children: [
          // 数据来源概述
          _buildSectionCard(
            '📊 数据来源',
            [
              _buildBulletText('广东省教育考试院官方发布数据'),
              _buildBulletText('阳光高考网（教育部高校招生阳光工程指定平台）'),
              _buildBulletText('全国各高校招生官方网站'),
              _buildBulletText('各省教育考试院公开数据'),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 数据年份
          _buildSectionCard(
            '📅 数据年份',
            [
              _buildBulletText('2023年：历史参考数据'),
              _buildBulletText('2024年：最新录取数据'),
              _buildBulletText('2025年：当年预估数据（基于往年趋势）'),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 更新频率
          _buildSectionCard(
            '🔄 更新频率',
            [
              _buildBulletText('常规更新：每年7-8月高考录取结束后'),
              _buildBulletText('数据审核：官方数据发布后1-2周内完成审核'),
              _buildBulletText('系统更新：审核通过后立即更新系统'),
              _buildBulletText('紧急更新：政策调整时即时更新'),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 数据覆盖范围
          _buildSectionCard(
            '🎓 数据覆盖范围',
            [
              _buildBulletText('全国2800+所高等院校'),
              _buildBulletText('本科+高职专科全层次覆盖'),
              _buildBulletText('31个省份（含直辖市、自治区）'),
              _buildBulletText('300-750分全分段数据'),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 数据准确性说明
          _buildSectionCard(
            '✅ 数据准确性',
            [
              _buildBulletText('本科数据：基于官方公布，准确度高'),
              _buildBulletText('专科数据：基于往年趋势估算，仅供参考'),
              _buildBulletText('所有数据均经多重校验'),
              _buildBulletText('重要数据以官方最新公布为准'),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 免责声明
          Container(
            padding: const EdgeInsets.all(AppTheme.spacingLg),
            decoration: BoxDecoration(
              color: AppTheme.errorBackground,
              borderRadius: BorderRadius.circular(AppTheme.radiusLg),
              border: Border.all(
                color: AppTheme.errorBorder,
                width: 1,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.warning_amber, color: AppTheme.red),
                    const SizedBox(width: AppTheme.spacingXs),
                    Text(
                      '免责声明',
                      style: AppTheme.titleSmall.copyWith(
                        color: AppTheme.red,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppTheme.spacingSm),
                Text(
                  '本系统提供的数据仅供参考，不作为正式报考依据。'
                  '实际录取结果以各省教育考试院和高校官方公布为准。'
                  '因数据延迟或误差造成的损失，本系统不承担责任。',
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.red,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: AppTheme.spacingLg),

          // 联系方式
          Center(
            child: Text(
              '如有疑问，请联系客服获取最新数据说明',
              style: AppTheme.bodySmall.copyWith(
                color: AppTheme.mediumGray,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建分组卡片
  Widget _buildSectionCard(String title, List<Widget> children) {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingLg),
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border.all(
          color: AppTheme.surfaceContainerHighest,
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: AppTheme.titleMedium.copyWith(
              fontWeight: FontWeight.bold,
              color: AppTheme.primaryBlue,
            ),
          ),
          const SizedBox(height: AppTheme.spacingSm),
          ...children,
        ],
      ),
    );
  }

  /// 构建列表项文本
  Widget _buildBulletText(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppTheme.spacingXs),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            margin: const EdgeInsets.only(top: 6),
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              color: AppTheme.primaryBlue,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: AppTheme.spacingSm),
          Expanded(
            child: Text(
              text,
              style: AppTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }
}