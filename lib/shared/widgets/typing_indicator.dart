import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'mentor_avatar.dart';

class TypingIndicator extends StatelessWidget {
  final String text;

  const TypingIndicator({
    super.key,
    this.text = '学锋老师正在回复...',
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacingMd,
        vertical: AppTheme.spacingSm,
      ),
      child: Row(
        children: [
          const MentorAvatar(size: 40),
          const SizedBox(width: AppTheme.spacingSm),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '学锋老师',
                style: AppTheme.labelSmall.copyWith(
                  color: AppTheme.mediumGray,
                ),
              ),
              const SizedBox(height: AppTheme.spacingXs),
              Row(
                children: [
                  _buildTypingDot(),
                  const SizedBox(width: AppTheme.spacingXs),
                  _buildTypingDot(),
                  const SizedBox(width: AppTheme.spacingXs),
                  _buildTypingDot(),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTypingDot() {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
      width: 6,
      height: 6,
      decoration: BoxDecoration(
        color: AppTheme.primaryBlue,
        shape: BoxShape.circle,
      ),
    );
  }
}

