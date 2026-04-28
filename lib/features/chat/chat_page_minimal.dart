import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'controllers/chat_controller.dart';
import '../../shared/widgets/typing_indicator.dart';
import 'widgets/message_bubble_minimal.dart';
import 'widgets/voice_input_button.dart';

/// ChatGPT极简风格聊天页面
class ChatPageMinimal extends ConsumerStatefulWidget {
  const ChatPageMinimal({super.key});

  @override
  ConsumerState<ChatPageMinimal> createState() => _ChatPageMinimalState();
}

class _ChatPageMinimalState extends ConsumerState<ChatPageMinimal> {
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
      backgroundColor: const Color(0xFFf7f7f8), // ChatGPT背景色
      appBar: AppBar(
        backgroundColor: const Color(0xFFf7f7f8),
        elevation: 0,
        title: const Text(
          '张学锋AI',
          style: TextStyle(
            color: Color(0xFF2d333a),
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // 聊天消息列表
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(vertical: 8),
              itemCount: messages.length + (isTyping ? 1 : 0),
              itemBuilder: (context, index) {
                if (index < messages.length) {
                  final msg = messages[index];
                  return MessageBubbleMinimal(
                    content: msg.content,
                    isUser: msg.role == 'user',
                    timestamp: msg.timestamp,
                  );
                } else {
                  // 显示正在输入指示器
                  return const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    child: TypingIndicator(),
                  );
                }
              },
            ),
          ),

          // 如果正在流式传输，显示当前内容
          if (chatState.currentStreamingMessage.isNotEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFececf1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  chatState.currentStreamingMessage,
                  style: const TextStyle(
                    color: Color(0xFF2d333a),
                    fontSize: 14,
                  ),
                ),
              ),
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
      decoration: const BoxDecoration(
        color: Color(0xFFf7f7f8),
        border: Border(
          top: BorderSide(
            color: Color(0xFFe5e5e5),
            width: 1,
          ),
        ),
      ),
      child: SafeArea(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            // 语音输入按钮
            VoiceInputButton(
              isListening: _isListening,
              onPressed: _toggleVoiceInput,
            ),

            const SizedBox(width: 12),

            // 文本输入框
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: const Color(0xFFe5e5e5),
                    width: 1,
                  ),
                ),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: TextField(
                  controller: _textController,
                  decoration: const InputDecoration(
                    hintText: '给张学锋发消息...',
                    hintStyle: TextStyle(
                      color: Color(0xFF8e8ea0),
                      fontSize: 15,
                    ),
                    border: InputBorder.none,
                    contentPadding: EdgeInsets.zero,
                  ),
                  maxLines: null,
                  textInputAction: TextInputAction.send,
                  onSubmitted: _handleSubmit,
                  style: const TextStyle(
                    color: Color(0xFF2d333a),
                    fontSize: 15,
                  ),
                ),
              ),
            ),

            const SizedBox(width: 8),

            // 发送按钮
            Container(
              decoration: BoxDecoration(
                color: const Color(0xFF10a37f),
                borderRadius: BorderRadius.circular(20),
              ),
              child: IconButton(
                icon: const Icon(Icons.send, color: Colors.white, size: 20),
                onPressed: () => _handleSubmit(_textController.text),
              ),
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
