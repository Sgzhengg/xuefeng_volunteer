import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../../../shared/theme/app_theme.dart';
import '../../../shared/widgets/mentor_avatar.dart';

class MessageBubble extends StatelessWidget {
  final String content;
  final bool isUser;
  final int timestamp;

  const MessageBubble({
    super.key,
    required this.content,
    required this.isUser,
    required this.timestamp,
  });

  @override
  Widget build(BuildContext context) {
    if (isUser) {
      return _buildUserMessage();
    } else {
      return _buildAIMessage();
    }
  }

  /// AI 消息（左侧，带虚拟人头像）
  Widget _buildAIMessage() {
    return Container(
      margin: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacingMd,
        vertical: AppTheme.spacingXs,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const MentorAvatar(size: 40),
          const SizedBox(width: AppTheme.spacingSm),
          Flexible(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '学锋老师',
                  style: AppTheme.labelSmall.copyWith(
                    color: AppTheme.mediumGray,
                  ),
                ),
                const SizedBox(height: AppTheme.spacingXs),
                Container(
                  padding: const EdgeInsets.all(AppTheme.spacingMd),
                  decoration: BoxDecoration(
                    color: AppTheme.white,
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(AppTheme.spacingSm),
                      topRight: Radius.circular(AppTheme.radiusLg),
                      bottomLeft: Radius.circular(AppTheme.radiusLg),
                      bottomRight: Radius.circular(AppTheme.radiusLg),
                    ),
                    boxShadow: AppTheme.shadowLight,
                    border: Border.all(
                      color: AppTheme.surfaceContainerHighest,
                      width: 1,
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 简单的文本渲染，支持基本的换行和加粗
                      _renderContent(content),
                      const SizedBox(height: AppTheme.spacingXs),
                      Text(
                        _formatTime(timestamp),
                        style: AppTheme.labelSmall.copyWith(
                          color: AppTheme.mediumGray,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 用户消息（右侧）
  Widget _buildUserMessage() {
    return Container(
      margin: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacingMd,
        vertical: AppTheme.spacingXs,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(AppTheme.spacingMd),
              decoration: BoxDecoration(
                color: AppTheme.primaryBlue,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(AppTheme.radiusLg),
                  topRight: Radius.circular(AppTheme.spacingSm),
                  bottomLeft: Radius.circular(AppTheme.radiusLg),
                  bottomRight: Radius.circular(AppTheme.radiusLg),
                ),
                boxShadow: AppTheme.shadowLight,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    content,
                    style: AppTheme.bodyMedium.copyWith(
                      color: AppTheme.white,
                    ),
                  ),
                  const SizedBox(height: AppTheme.spacingXs),
                  Text(
                    _formatTime(timestamp),
                    style: AppTheme.labelSmall.copyWith(
                      color: AppTheme.white.withOpacity(0.7),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 使用 Markdown 渲染内容
  Widget _renderContent(String text) {
    return MarkdownBody(
      data: text,
      styleSheet: MarkdownStyleSheet(
        p: AppTheme.bodyMedium.copyWith(
          color: AppTheme.darkGray,
        ),
        h1: AppTheme.headlineMedium.copyWith(
          color: AppTheme.darkGray,
          fontWeight: FontWeight.bold,
          fontSize: 24,
        ),
        h2: AppTheme.titleMedium.copyWith(
          color: AppTheme.darkGray,
          fontWeight: FontWeight.bold,
        ),
        h3: AppTheme.titleSmall.copyWith(
          color: AppTheme.darkGray,
          fontWeight: FontWeight.bold,
        ),
        listBullet: AppTheme.bodyMedium.copyWith(
          color: AppTheme.darkGray,
        ),
        strong: AppTheme.bodyMedium.copyWith(
          color: AppTheme.darkGray,
          fontWeight: FontWeight.bold,
        ),
        code: AppTheme.bodySmall.copyWith(
          color: AppTheme.primaryBlue,
          backgroundColor: AppTheme.surfaceContainerHighest,
        ),
        blockquote: AppTheme.bodyMedium.copyWith(
          color: AppTheme.mediumGray,
          fontStyle: FontStyle.italic,
        ),
      ),
    );
  }

  String _formatTime(int milliseconds) {
    final date = DateTime.fromMillisecondsSinceEpoch(milliseconds);
    return '${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }
}
