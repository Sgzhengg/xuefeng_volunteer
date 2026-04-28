import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// 数据源类型枚举
enum DataSourceType {
  /// 后端真实数据库
  realData,

  /// 模拟数据模式
  mockData,

  /// 连接失败
  connectionFailed,
}

/// 数据源状态指示器组件
/// 显示当前使用的数据源类型
class DataSourceIndicator extends StatelessWidget {
  final DataSourceType dataSourceType;
  final String? lastUpdateTime;
  final String? dataCoverage;
  final VoidCallback? onTap;
  final bool showDetails;

  const DataSourceIndicator({
    super.key,
    required this.dataSourceType,
    this.lastUpdateTime,
    this.dataCoverage,
    this.onTap,
    this.showDetails = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap ?? () => _showDataSourceDialog(context),
      child: _buildIndicator(),
    );
  }

  Widget _buildIndicator() {
    switch (dataSourceType) {
      case DataSourceType.realData:
        return _buildRealDataIndicator();
      case DataSourceType.mockData:
        return _buildMockDataIndicator();
      case DataSourceType.connectionFailed:
        return _buildFailedIndicator();
    }
  }

  /// 真实数据指示器
  Widget _buildRealDataIndicator() {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacingSm,
        vertical: AppTheme.spacingXs,
      ),
      decoration: BoxDecoration(
        color: AppTheme.successBackground,
        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
        border: Border.all(
          color: AppTheme.successBorder,
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              color: AppTheme.green,
            ),
          ),
          const SizedBox(width: AppTheme.spacingXs),
          const Text(
            '后端数据',
            style: TextStyle(
              fontSize: 12,
              color: AppTheme.green,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  /// 模拟数据指示器
  Widget _buildMockDataIndicator() {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacingSm,
        vertical: AppTheme.spacingXs,
      ),
      decoration: BoxDecoration(
        color: AppTheme.warningBackground,
        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
        border: Border.all(
          color: AppTheme.warningBorder,
          width: 1,
        ),
      ),
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.warning_amber_rounded,
            size: 16,
            color: AppTheme.orange,
          ),
          SizedBox(width: AppTheme.spacingXs),
          Text(
            '模拟数据',
            style: TextStyle(
              fontSize: 12,
              color: AppTheme.orange,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  /// 连接失败指示器
  Widget _buildFailedIndicator() {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacingSm,
        vertical: AppTheme.spacingXs,
      ),
      decoration: BoxDecoration(
        color: AppTheme.errorBackground,
        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
        border: Border.all(
          color: AppTheme.errorBorder,
          width: 1,
        ),
      ),
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.error_outline,
            size: 16,
            color: AppTheme.red,
          ),
          SizedBox(width: AppTheme.spacingXs),
          Text(
            '连接失败',
            style: TextStyle(
              fontSize: 12,
              color: AppTheme.red,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  /// 显示数据源详情对话框
  void _showDataSourceDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => _DataSourceDetailDialog(
        dataSourceType: dataSourceType,
        lastUpdateTime: lastUpdateTime,
        dataCoverage: dataCoverage,
      ),
    );
  }
}

/// 数据源详情对话框
class _DataSourceDetailDialog extends StatelessWidget {
  final DataSourceType dataSourceType;
  final String? lastUpdateTime;
  final String? dataCoverage;

  const _DataSourceDetailDialog({
    required this.dataSourceType,
    this.lastUpdateTime,
    this.dataCoverage,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('数据源状态'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildStatusInfo(),
          if (lastUpdateTime != null) ...[
            const SizedBox(height: AppTheme.spacingMd),
            _buildInfoRow(
              Icons.update_rounded,
              '最后更新',
              lastUpdateTime!,
            ),
          ],
          if (dataCoverage != null) ...[
            const SizedBox(height: AppTheme.spacingSm),
            _buildInfoRow(
              Icons.storage_rounded,
              '数据覆盖',
              dataCoverage!,
            ),
          ],
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('确定'),
        ),
      ],
    );
  }

  Widget _buildStatusInfo() {
    switch (dataSourceType) {
      case DataSourceType.realData:
        return _buildInfoRow(
          Icons.check_circle_outline,
          '状态',
          '后端真实数据库',
          AppTheme.green,
        );
      case DataSourceType.mockData:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildInfoRow(
              Icons.warning_amber_rounded,
              '状态',
              '模拟数据模式',
              AppTheme.orange,
            ),
            const SizedBox(height: AppTheme.spacingSm),
            Container(
              padding: const EdgeInsets.all(AppTheme.spacingSm),
              decoration: BoxDecoration(
                color: AppTheme.warningBackground,
                borderRadius: BorderRadius.circular(AppTheme.radiusSm),
              ),
              child: const Text(
                '当前为模拟数据，仅供测试使用\n非真实录取数据\n请切换到生产环境查看真实数据',
                style: TextStyle(
                  fontSize: 12,
                  color: AppTheme.darkGray,
                ),
              ),
            ),
          ],
        );
      case DataSourceType.connectionFailed:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildInfoRow(
              Icons.error_outline,
              '状态',
              '连接失败',
              AppTheme.red,
            ),
            const SizedBox(height: AppTheme.spacingSm),
            const Text(
              '无法连接到数据库\n请检查网络连接',
              style: TextStyle(
                fontSize: 12,
                color: AppTheme.mediumGray,
              ),
            ),
          ],
        );
    }
  }

  Widget _buildInfoRow(
    IconData icon,
    String label,
    String value, [
    Color? valueColor,
  ]) {
    return Row(
      children: [
        Icon(
          icon,
          size: 20,
          color: AppTheme.mediumGray,
        ),
        const SizedBox(width: AppTheme.spacingSm),
        Text(
          '$label：',
          style: const TextStyle(
            fontSize: 14,
            color: AppTheme.mediumGray,
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            color: valueColor ?? AppTheme.darkGray,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}

/// 数据源状态卡片（用于志愿模拟器页面）
class DataSourceStatusCard extends StatelessWidget {
  final DataSourceType dataSourceType;
  final String? lastUpdateTime;
  final String? dataCoverage;
  final VoidCallback? onTap;

  const DataSourceStatusCard({
    super.key,
    required this.dataSourceType,
    this.lastUpdateTime,
    this.dataCoverage,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final (Color bgColor, Color borderColor, IconData icon, String title, String description) = switch (dataSourceType) {
      DataSourceType.realData => (
        AppTheme.successBackground,
        AppTheme.successBorder,
        Icons.link_rounded,
        '后端真实数据库',
        '使用真实录取数据进行推荐',
      ),
      DataSourceType.mockData => (
        AppTheme.warningBackground,
        AppTheme.warningBorder,
        Icons.warning_amber_rounded,
        '模拟数据模式',
        '当前使用模拟数据，仅供参考',
      ),
      DataSourceType.connectionFailed => (
        AppTheme.errorBackground,
        AppTheme.errorBorder,
        Icons.error_outline,
        '连接失败',
        '无法连接数据库，请检查网络',
      ),
    };

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(AppTheme.spacingMd),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(AppTheme.radiusLg),
          border: Border(
            left: BorderSide(
              color: borderColor,
              width: 4,
            ),
          ),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              color: borderColor,
              size: 24,
            ),
            const SizedBox(width: AppTheme.spacingSm),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: borderColor,
                    ),
                  ),
                  if (lastUpdateTime != null) ...[
                    const SizedBox(height: AppTheme.spacingXs),
                    Text(
                      '更新：$lastUpdateTime',
                      style: AppTheme.bodySmall,
                    ),
                  ],
                  if (dataCoverage != null) ...[
                    const SizedBox(height: AppTheme.spacingXs),
                    Text(
                      dataCoverage!,
                      style: AppTheme.bodySmall,
                    ),
                  ],
                  const SizedBox(height: AppTheme.spacingXs),
                  Text(
                    description,
                    style: AppTheme.bodySmall,
                  ),
                ],
              ),
            ),
            Icon(
              Icons.chevron_right_rounded,
              color: AppTheme.mediumGray,
            ),
          ],
        ),
      ),
    );
  }
}
