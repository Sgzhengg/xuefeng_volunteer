import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// 建议芯片组件
/// 用于显示快捷问题提示
class SuggestionChips extends StatelessWidget {
  final List<String> suggestions;
  final ValueChanged<String> onTap;

  const SuggestionChips({
    super.key,
    required this.suggestions,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacingMd,
        vertical: AppTheme.spacingSm,
      ),
      child: Wrap(
        spacing: AppTheme.spacingSm,
        runSpacing: AppTheme.spacingSm,
        children: suggestions.map((suggestion) {
          return _buildChip(suggestion);
        }).toList(),
      ),
    );
  }

  Widget _buildChip(String text) {
    return GestureDetector(
      onTap: () => onTap(text),
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: AppTheme.spacingMd,
          vertical: AppTheme.spacingSm,
        ),
        decoration: BoxDecoration(
          color: AppTheme.infoBackground,
          borderRadius: BorderRadius.circular(AppTheme.radiusFull),
          border: Border.all(
            color: AppTheme.surfaceContainerHighest,
            width: 1,
          ),
        ),
        child: Text(
          text,
          style: AppTheme.bodySmall.copyWith(
            color: AppTheme.darkGray,
          ),
        ),
      ),
    );
  }
}

/// 默认建议列表
class DefaultSuggestionChips extends StatelessWidget {
  final ValueChanged<String> onTap;

  const DefaultSuggestionChips({
    super.key,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final suggestions = [
      '推荐几所985院校',
      '计算机专业就业分析',
      '往年分数线查询',
      '志愿填报策略',
    ];

    return SuggestionChips(
      suggestions: suggestions,
      onTap: onTap,
    );
  }
}
