import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../../../shared/theme/chatgpt_theme.dart';

/// ChatGPT风格的消息气泡
class ChatGPTMessageBubble extends StatelessWidget {
  final String content;
  final bool isUser;
  final int timestamp;
  final bool isStreaming;

  const ChatGPTMessageBubble({
    super.key,
    required this.content,
    required this.isUser,
    required this.timestamp,
    this.isStreaming = false,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    if (isUser) {
      return _buildUserMessage(context, isDark);
    } else {
      return _buildAIMessage(context, isDark);
    }
  }

  /// AI消息（左侧，浅灰背景）
  Widget _buildAIMessage(BuildContext context, bool isDark) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(
        horizontal: ChatGPTTheme.paddingLarge,
        vertical: ChatGPTTheme.paddingMedium,
      ),
      decoration: BoxDecoration(
        color: isDark
            ? ChatGPTTheme.darkAIMessageBackground
            : ChatGPTTheme.lightAIMessageBackground,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // AI头像
          Container(
            width: 36,
            height: 36,
            margin: const EdgeInsets.only(
                right: ChatGPTTheme.paddingMedium),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  ChatGPTTheme.chatGPTGreen,
                  ChatGPTTheme.chatGPTDarkGreen,
                ],
              ),
            ),
            child: const Icon(
              Icons.person,
              color: Colors.white,
              size: 20,
            ),
          ),

          // 消息内容
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '学锋老师',
                  style: TextStyle(
                    color: isDark
                        ? ChatGPTTheme.darkTextPrimary
                        : ChatGPTTheme.lightTextPrimary,
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: ChatGPTTheme.paddingXSmall),
                _buildMarkdownContent(isDark),
                if (!isStreaming) ...[
                  const SizedBox(height: ChatGPTTheme.paddingSmall),
                  Text(
                    _formatTime(timestamp),
                    style: TextStyle(
                      color: isDark
                          ? ChatGPTTheme.darkTextSecondary
                          : ChatGPTTheme.lightTextSecondary,
                      fontSize: 11,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 用户消息（右侧，绿色背景）
  Widget _buildUserMessage(BuildContext context, bool isDark) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(
        horizontal: ChatGPTTheme.paddingLarge,
        vertical: ChatGPTTheme.paddingMedium,
      ),
      color: isDark
          ? ChatGPTTheme.darkBackground
          : ChatGPTTheme.lightBackground,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(
                horizontal: ChatGPTTheme.paddingMedium,
                vertical: ChatGPTTheme.paddingSmall,
              ),
              decoration: BoxDecoration(
                color: ChatGPTTheme.chatGPTGreen,
                borderRadius: BorderRadius.circular(
                    ChatGPTTheme.radiusMedium),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    content,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 15,
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: ChatGPTTheme.paddingXSmall),
                  Text(
                    _formatTime(timestamp),
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.7),
                      fontSize: 11,
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

  /// 使用Markdown渲染AI消息内容
  Widget _buildMarkdownContent(bool isDark) {
    return MarkdownBody(
      data: content,
      selectable: true,
      styleSheet: MarkdownStyleSheet(
        p: TextStyle(
          color: isDark
              ? ChatGPTTheme.darkTextPrimary
              : ChatGPTTheme.lightTextPrimary,
          fontSize: 15,
          height: 1.6,
        ),
        h1: TextStyle(
          color: isDark
              ? ChatGPTTheme.darkTextPrimary
              : ChatGPTTheme.lightTextPrimary,
          fontSize: 24,
          fontWeight: FontWeight.bold,
          height: 1.3,
        ),
        h2: TextStyle(
          color: isDark
              ? ChatGPTTheme.darkTextPrimary
              : ChatGPTTheme.lightTextPrimary,
          fontSize: 20,
          fontWeight: FontWeight.bold,
          height: 1.3,
        ),
        h3: TextStyle(
          color: isDark
              ? ChatGPTTheme.darkTextPrimary
              : ChatGPTTheme.lightTextPrimary,
          fontSize: 18,
          fontWeight: FontWeight.bold,
          height: 1.3,
        ),
        listBullet: TextStyle(
          color: isDark
              ? ChatGPTTheme.darkTextPrimary
              : ChatGPTTheme.lightTextPrimary,
          fontSize: 15,
        ),
        strong: TextStyle(
          color: isDark
              ? ChatGPTTheme.darkTextPrimary
              : ChatGPTTheme.lightTextPrimary,
          fontWeight: FontWeight.bold,
        ),
        code: TextStyle(
          backgroundColor: isDark
              ? ChatGPTTheme.darkInputBackground
              : ChatGPTTheme.lightSurface,
          color: isDark
              ? ChatGPTTheme.darkTextPrimary
              : ChatGPTTheme.lightTextPrimary,
          fontSize: 13,
        ),
        blockquote: TextStyle(
          color: isDark
              ? ChatGPTTheme.darkTextSecondary
              : ChatGPTTheme.lightTextSecondary,
          fontStyle: FontStyle.italic,
          fontSize: 15,
        ),
        codeblockDecoration: BoxDecoration(
          color: isDark
              ? ChatGPTTheme.darkInputBackground
              : ChatGPTTheme.lightSurface,
          borderRadius: BorderRadius.circular(ChatGPTTheme.radiusSmall),
          border: Border.all(
            color: isDark
                ? ChatGPTTheme.darkInputBorder
                : ChatGPTTheme.lightInputBorder,
          ),
        ),
        horizontalRuleDecoration: BoxDecoration(
          border: Border(
            top: BorderSide(
              color: isDark
                  ? ChatGPTTheme.darkDivider
                  : ChatGPTTheme.lightDivider,
              width: 1,
            ),
          ),
        ),
      ),
    );
  }

  String _formatTime(int milliseconds) {
    final date = DateTime.fromMillisecondsSinceEpoch(milliseconds);
    return '${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }
}
