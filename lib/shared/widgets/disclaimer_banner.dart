import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'data_source_indicator.dart';

class DisclaimerBanner extends StatefulWidget {
  final bool isCollapsible;
  final DataSourceType dataSourceType;

  const DisclaimerBanner({
    super.key,
    this.isCollapsible = false,
    this.dataSourceType = DataSourceType.realData,
  });

  @override
  State<DisclaimerBanner> createState() => _DisclaimerBannerState();
}

class _DisclaimerBannerState extends State<DisclaimerBanner> {
  bool _isExpanded = true;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacingMd,
        vertical: AppTheme.spacingSm,
      ),
      decoration: BoxDecoration(
        color: AppTheme.warningBackground,
        border: const Border(
          bottom: BorderSide(
            color: AppTheme.warningBorder,
            width: 1,
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(
                Icons.warning_amber_rounded,
                color: AppTheme.orange,
                size: 20,
              ),
              const SizedBox(width: AppTheme.spacingSm),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '重要声明',
                      style: AppTheme.labelSmall.copyWith(
                        color: AppTheme.darkGray,
                      ),
                    ),
                    if (_isExpanded) ...[
                      const SizedBox(height: AppTheme.spacingXs),
                      Text(
                        _getDisclaimerText(),
                        style: AppTheme.bodySmall.copyWith(
                          color: AppTheme.darkGray,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              if (widget.isCollapsible)
                IconButton(
                  icon: Icon(
                    _isExpanded ? Icons.expand_less : Icons.expand_more,
                    color: AppTheme.mediumGray,
                  ),
                  onPressed: () {
                    setState(() {
                      _isExpanded = !_isExpanded;
                    });
                  },
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
            ],
          ),
        ],
      ),
    );
  }

  String _getDisclaimerText() {
    switch (widget.dataSourceType) {
      case DataSourceType.realData:
        return '• 数据来源：后端真实数据库\n'
            '• AI 建议仅供参考，不作为最终填报依据';
      case DataSourceType.mockData:
        return '• ⚠️ 当前为模拟数据，仅供测试使用\n'
            '• 非 真实录取数据\n'
            '• AI 建议仅供参考，不作为最终填报依据';
      case DataSourceType.connectionFailed:
        return '• ⚠️ 无法连接到数据库\n'
            '• 请检查网络连接\n'
            '• AI 建议仅供参考，不作为最终填报依据';
    }
  }
}
