import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'controllers/chat_controller.dart';
import '../../shared/widgets/disclaimer_banner.dart';
import '../../shared/widgets/typing_indicator.dart';
import '../../shared/widgets/suggestion_chips.dart';
import '../../shared/widgets/data_source_indicator.dart';
import '../../shared/theme/app_theme.dart';
import 'widgets/voice_input_button.dart';
import 'widgets/message_bubble.dart';

class ChatPage extends ConsumerStatefulWidget {
  const ChatPage({super.key});

  @override
  ConsumerState<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends ConsumerState<ChatPage> {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final SpeechToText _speechToText = SpeechToText();
  bool _isListening = false;

  @override
  void initState() {
    super.initState();
    _initSpeechRecognition();
    // 初始化聊天（显示欢迎消息）
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final controller = ref.read(chatControllerProvider.notifier);
      if (controller.state.messages.isEmpty) {
        controller.initializeChat();
      }
    });
  }

  void _initSpeechRecognition() {
    _speechToText.initialize(
      onError: (error) => setState(() => _isListening = false),
      onStatus: (status) => setState(() {
        _isListening = status == 'listening';
      }),
    );
  }

  void _handleSubmit(String text) {
    if (text.trim().isEmpty) return;

    // sendMessage() 已经修改为调用后端API
    ref.read(chatControllerProvider.notifier).sendMessage(text);
    _textController.clear();
  }

  void _toggleVoiceInput() async {
    if (_isListening) {
      await _speechToText.stop();
      setState(() => _isListening = false);
    } else {
      await _speechToText.listen(
        onResult: (result) {
          _textController.text = result.recognizedWords;
        },
        localeId: 'zh_CN',
      );
      setState(() => _isListening = true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatControllerProvider);
    final messages = chatState.messages;
    final isTyping = chatState.isTyping;

    return Scaffold(
      appBar: AppBar(
        title: const Text('和学锋老师聊'),
        actions: const [
          Padding(
            padding: EdgeInsets.symmetric(horizontal: AppTheme.spacingMd),
            child: DataSourceIndicator(
              dataSourceType: DataSourceType.realData,
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // 免责声明横幅（可折叠）
          const DisclaimerBanner(
            isCollapsible: true,
            dataSourceType: DataSourceType.realData,
          ),

          // 聊天消息列表
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(vertical: AppTheme.spacingSm),
              itemCount: messages.length + (isTyping ? 1 : 0),
              itemBuilder: (context, index) {
                if (index < messages.length) {
                  final msg = messages[index];
                  return MessageBubble(
                    content: msg.content,
                    isUser: msg.role == 'user',
                    timestamp: msg.timestamp,
                  );
                } else {
                  // 显示正在输入指示器
                  return const TypingIndicator();
                }
              },
            ),
          ),

          // 如果正在流式传输，显示当前内容
          if (chatState.currentStreamingMessage.isNotEmpty)
            Container(
              margin: const EdgeInsets.symmetric(
                horizontal: AppTheme.spacingMd,
                vertical: AppTheme.spacingXs,
              ),
              padding: const EdgeInsets.all(AppTheme.spacingMd),
              decoration: BoxDecoration(
                color: AppTheme.white,
                borderRadius: BorderRadius.circular(AppTheme.radiusLg),
                boxShadow: AppTheme.shadowLight,
                border: Border.all(
                  color: AppTheme.surfaceContainerHighest,
                  width: 1,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    chatState.currentStreamingMessage,
                    style: AppTheme.bodyMedium.copyWith(
                      color: AppTheme.darkGray,
                    ),
                  ),
                ],
              ),
            ),

          // 建议芯片（仅在首次或无消息时显示）
          if (messages.isEmpty)
            DefaultSuggestionChips(
              onTap: _handleSubmit,
            ),

          // 输入框
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            // 语音输入按钮
            VoiceInputButton(
              isListening: _isListening,
              onPressed: _toggleVoiceInput,
            ),

            const SizedBox(width: 12),

            // 文本输入框
            Expanded(
              child: TextField(
                controller: _textController,
                decoration: const InputDecoration(
                  hintText: '问张老师任何关于志愿的问题...',
                  border: InputBorder.none,
                ),
                maxLines: null,
                textInputAction: TextInputAction.send,
                onSubmitted: _handleSubmit,
              ),
            ),

            // 发送按钮
            IconButton(
              icon: const Icon(Icons.send),
              onPressed: () => _handleSubmit(_textController.text),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }
}
