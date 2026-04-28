import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

/// ChatGPT极简风格消息气泡
class MessageBubbleMinimal extends StatelessWidget {
  final String content;
  final bool isUser;
  final int timestamp;

  const MessageBubbleMinimal({
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

  /// AI消息（左侧，简洁风格）
  Widget _buildAIMessage() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFececf1), // ChatGPT AI消息背景色
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          MarkdownBody(
            data: content,
            styleSheet: MarkdownStyleSheet(
              p: const TextStyle(
                color: Color(0xFF2d333a),
                fontSize: 15,
                height: 1.6,
              ),
              h1: const TextStyle(
                color: Color(0xFF2d333a),
                fontSize: 24,
                fontWeight: FontWeight.bold,
                height: 1.3,
              ),
              h2: const TextStyle(
                color: Color(0xFF2d333a),
                fontSize: 20,
                fontWeight: FontWeight.bold,
                height: 1.3,
              ),
              h3: const TextStyle(
                color: Color(0xFF2d333a),
                fontSize: 18,
                fontWeight: FontWeight.bold,
                height: 1.3,
              ),
              listBullet: const TextStyle(
                color: Color(0xFF2d333a),
                fontSize: 15,
              ),
              strong: const TextStyle(
                color: Color(0xFF2d333a),
                fontWeight: FontWeight.bold,
              ),
              code: const TextStyle(
                color: Color(0xFF2d333a),
                backgroundColor: Color(0xFFd4d4d8),
                fontSize: 14,
              ),
              blockquote: const TextStyle(
                color: Color(0xFF6e6e80),
                fontStyle: FontStyle.italic,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 用户消息（右侧，简洁风格）
  Widget _buildUserMessage() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: const Color(0xFF10a37f), // ChatGPT用户消息背景色
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                content,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 15,
                  height: 1.6,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
