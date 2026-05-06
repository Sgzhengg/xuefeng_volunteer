import 'package:flutter/material.dart';
import '../../../shared/theme/chatgpt_theme.dart';

/// ChatGPT风格的建议卡片
class SuggestionCards extends StatelessWidget {
  final Function(String) onSuggestionTap;

  const SuggestionCards({
    super.key,
    required this.onSuggestionTap,
  });

  @override
  Widget build(BuildContext context) {
    final suggestions = [
      '老师，我理科620分，想报计算机专业，您觉得怎么样？',
      '广东省理科550分能上什么大学？',
      '人工智能和计算机专业哪个好？',
      '帮我分析一下我的志愿填报方案',
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 2.5,
        crossAxisSpacing: ChatGPTTheme.paddingMedium,
        mainAxisSpacing: ChatGPTTheme.paddingMedium,
      ),
      itemCount: suggestions.length,
      itemBuilder: (context, index) {
        return _buildSuggestionCard(suggestions[index]);
      },
    );
  }

  Widget _buildSuggestionCard(String suggestion) {
    return InkWell(
      onTap: () => onSuggestionTap(suggestion),
      borderRadius: BorderRadius.circular(ChatGPTTheme.radiusMedium),
      child: Container(
        padding: const EdgeInsets.all(ChatGPTTheme.paddingMedium),
        decoration: BoxDecoration(
          color: ChatGPTTheme.lightSurface,
          borderRadius: BorderRadius.circular(ChatGPTTheme.radiusMedium),
          border: Border.all(
            color: ChatGPTTheme.lightInputBorder,
            width: 1,
          ),
        ),
        child: Center(
          child: Text(
            suggestion,
            style: const TextStyle(
              color: ChatGPTTheme.lightTextPrimary,
              fontSize: 13,
              height: 1.4,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            textAlign: TextAlign.center,
          ),
        ),
      ),
    );
  }
}
