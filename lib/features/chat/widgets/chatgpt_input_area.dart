import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../shared/theme/chatgpt_theme.dart';

/// ChatGPT风格的输入区域
class ChatGPTInputArea extends StatelessWidget {
  final TextEditingController controller;
  final VoidCallback onSend;
  final VoidCallback onVoiceToggle;
  final bool isListening;
  final bool isLoading;

  const ChatGPTInputArea({
    super.key,
    required this.controller,
    required this.onSend,
    required this.onVoiceToggle,
    this.isListening = false,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.all(ChatGPTTheme.paddingLarge),
      decoration: BoxDecoration(
        color: isDark
            ? ChatGPTTheme.darkBackground
            : ChatGPTTheme.lightBackground,
        border: Border(
          top: BorderSide(
            color: isDark
                ? ChatGPTTheme.darkDivider
                : ChatGPTTheme.lightDivider,
            width: 1,
          ),
        ),
      ),
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 免责声明
            Container(
              margin: const EdgeInsets.only(
                  bottom: ChatGPTTheme.paddingMedium),
              padding: const EdgeInsets.symmetric(
                horizontal: ChatGPTTheme.paddingMedium,
                vertical: ChatGPTTheme.paddingSmall,
              ),
              decoration: BoxDecoration(
                color: isDark
                    ? ChatGPTTheme.darkSurface
                    : ChatGPTTheme.lightSurface,
                borderRadius:
                    BorderRadius.circular(ChatGPTTheme.radiusSmall),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.info_outline,
                    size: 14,
                    color: isDark
                        ? ChatGPTTheme.darkTextSecondary
                        : ChatGPTTheme.lightTextSecondary,
                  ),
                  const SizedBox(width: ChatGPTTheme.paddingXSmall),
                  Expanded(
                    child: Text(
                      '建议仅供参考，以官方公布为准',
                      style: TextStyle(
                        color: isDark
                            ? ChatGPTTheme.darkTextSecondary
                            : ChatGPTTheme.lightTextSecondary,
                        fontSize: 11,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // 输入框
            Container(
              decoration: BoxDecoration(
                color: isDark
                    ? ChatGPTTheme.darkInputBackground
                    : ChatGPTTheme.lightInputBackground,
                borderRadius:
                    BorderRadius.circular(ChatGPTTheme.radiusLarge),
                border: Border.all(
                  color: controller.text.isEmpty
                      ? (isDark
                          ? ChatGPTTheme.darkInputBorder
                          : ChatGPTTheme.lightInputBorder)
                      : ChatGPTTheme.chatGPTGreen,
                  width: controller.text.isEmpty ? 1 : 2,
                ),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  // 语音按钮
                  IconButton(
                    onPressed: onVoiceToggle,
                    icon: Icon(
                      isListening ? Icons.mic : Icons.mic_none,
                      color: isListening
                          ? Colors.red
                          : (isDark
                              ? ChatGPTTheme.darkTextSecondary
                              : ChatGPTTheme.lightTextSecondary),
                    ),
                    tooltip: '语音输入',
                  ),

                  // 输入框
                  Expanded(
                    child: TextField(
                      controller: controller,
                      maxLines: null,
                      minLines: 1,
                      maxLength: 2000,
                      style: TextStyle(
                        color: isDark
                            ? ChatGPTTheme.darkTextPrimary
                            : ChatGPTTheme.lightTextPrimary,
                        fontSize: 15,
                      ),
                      decoration: InputDecoration(
                        hintText: '给学锋老师发消息...',
                        hintStyle: TextStyle(
                          color: isDark
                              ? ChatGPTTheme.darkTextSecondary
                              : ChatGPTTheme.lightTextSecondary,
                          fontSize: 15,
                        ),
                        border: InputBorder.none,
                        counterText: '',
                        contentPadding: const EdgeInsets.symmetric(
                          vertical: ChatGPTTheme.paddingMedium,
                        ),
                      ),
                      textInputAction: TextInputAction.newline,
                      onSubmitted: (_) => onSend(),
                    ),
                  ),

                  // 发送按钮
                  Container(
                    margin: const EdgeInsets.all(
                        ChatGPTTheme.paddingXSmall),
                    child: IconButton(
                      onPressed:
                          controller.text.trim().isEmpty ? null : onSend,
                      icon: isLoading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                    ChatGPTTheme.chatGPTGreen),
                              ),
                            )
                          : const Icon(
                              Icons.arrow_upward,
                              color: ChatGPTTheme.chatGPTGreen,
                              size: 20,
                            ),
                      tooltip: '发送',
                      style: IconButton.styleFrom(
                        backgroundColor:
                            controller.text.trim().isEmpty
                                ? (isDark
                                    ? ChatGPTTheme.darkSurface
                                    : ChatGPTTheme.lightSurface)
                                : ChatGPTTheme.chatGPTGreen,
                        foregroundColor:
                            controller.text.trim().isEmpty
                                ? (isDark
                                    ? ChatGPTTheme.darkTextSecondary
                                    : ChatGPTTheme.lightTextSecondary)
                                : Colors.white,
                        padding: const EdgeInsets.all(
                            ChatGPTTheme.paddingSmall),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
