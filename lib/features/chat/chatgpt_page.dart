import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'controllers/chat_controller.dart';
import '../../shared/theme/chatgpt_theme.dart';
import 'widgets/chatgpt_message_bubble.dart';
import 'widgets/chatgpt_input_area.dart';
import 'widgets/suggestion_cards.dart';

/// 完全模仿ChatGPT移动端风格的聊天页面
class ChatGPTPage extends ConsumerStatefulWidget {
  const ChatGPTPage({super.key});

  @override
  ConsumerState<ChatGPTPage> createState() => _ChatGPTPageState();
}

class _ChatGPTPageState extends ConsumerState<ChatGPTPage> {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  
  ;

  @override
  void initState() {
    super.initState();
    // 延迟初始化语音识别（不阻塞页面加载）
    Future.delayed(const Duration(milliseconds: 500), () {
      _initSpeechRecognition();
    });

    // 快速初始化聊天（显示欢迎消息）
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final controller = ref.read(chatControllerProvider.notifier);
      if (controller.state.messages.isEmpty) {
        controller.initializeChat();
      }
    });
  }

  ),
    );
  }

  void _handleSubmit(String text) {
    print('🚀🚀🚀 _handleSubmit CALLED with text: "$text"');

    if (text.trim().isEmpty) {
      print('⚠️⚠️⚠️ Text is EMPTY, returning!');
      return;
    }

    try {
      print('✅✅✅ Calling sendMessage...');
      ref.read(chatControllerProvider.notifier).sendMessage(text);
      _textController.clear();
      print('✅✅✅ Message sent and input cleared');

      // 滚动到底部
      Future.delayed(const Duration(milliseconds: 100), () {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      });
    } catch (e, stackTrace) {
      print('❌❌❌ ERROR: $e');
      print('❌❌❌ Stack: $stackTrace');

      // 显示错误给用户
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('发送失败: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

   else {
      await  {
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
      // ChatGPT风格的AppBar
      appBar: AppBar(
        elevation: 0,
        backgroundColor: ChatGPTTheme.lightBackground,
        leading: IconButton(
          icon: const Icon(Icons.menu, color: ChatGPTTheme.lightTextPrimary),
          onPressed: () {
            // 打开侧边栏菜单
            Scaffold.of(context).openDrawer();
          },
        ),
        title: const Text(
          '学锋老师',
          style: TextStyle(
            color: ChatGPTTheme.lightTextPrimary,
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(
              Icons.history,
              color: ChatGPTTheme.lightTextPrimary,
            ),
            onPressed: () {
              // 显示历史记录
            },
          ),
          IconButton(
            icon: const Icon(
              Icons.more_vert,
              color: ChatGPTTheme.lightTextPrimary,
            ),
            onPressed: () {
              // 更多选项
            },
          ),
        ],
      ),
      // 侧边栏
      drawer: _buildDrawer(context),
      body: Column(
        children: [
          // 聊天消息列表
          Expanded(
            child: _buildMessagesList(messages, isTyping),
          ),

          // 建议卡片（仅在首次或无消息时显示）
          if (messages.isEmpty && !isTyping)
            _buildSuggestionCards(),

          // 输入区域
          ChatGPTInputArea(
            controller: _textController,
            onSend: () => _handleSubmit(_textController.text),
            onVoiceToggle: _toggleVoiceInput,
            isListening: _isListening,
            isLoading: isTyping,
          ),
        ],
      ),
    );
  }

  /// 构建侧边栏
  Widget _buildDrawer(BuildContext context) {
    return Drawer(
      child: Container(
        color: ChatGPTTheme.darkBackground,
        child: SafeArea(
          child: Column(
            children: [
              // 头部
              Container(
                padding: const EdgeInsets.all(ChatGPTTheme.paddingLarge),
                decoration: const BoxDecoration(
                  border: Border(
                    bottom: BorderSide(
                      color: ChatGPTTheme.darkDivider,
                      width: 1,
                    ),
                  ),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 40,
                      height: 40,
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
                        size: 24,
                      ),
                    ),
                    const SizedBox(width: ChatGPTTheme.paddingMedium),
                    const Text(
                      '新对话',
                      style: TextStyle(
                        color: ChatGPTTheme.darkTextPrimary,
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),

              // 历史记录列表
              Expanded(
                child: Column(
                  children: [
                    // 搜索框
                    Container(
                      margin: const EdgeInsets.all(ChatGPTTheme.paddingMedium),
                      child: TextField(
                        style: const TextStyle(
                          color: ChatGPTTheme.darkTextPrimary,
                          fontSize: 14,
                        ),
                        decoration: InputDecoration(
                          hintText: '搜索历史记录...',
                          hintStyle: const TextStyle(
                            color: ChatGPTTheme.darkTextSecondary,
                            fontSize: 14,
                          ),
                          prefixIcon: const Icon(
                            Icons.search,
                            color: ChatGPTTheme.darkTextSecondary,
                            size: 20,
                          ),
                          filled: true,
                          fillColor: ChatGPTTheme.darkInputBackground,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(
                                ChatGPTTheme.radiusSmall),
                            borderSide: BorderSide.none,
                          ),
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: ChatGPTTheme.paddingSmall,
                            vertical: ChatGPTTheme.paddingSmall,
                          ),
                        ),
                      ),
                    ),

                    // 历史会话列表
                    Expanded(
                      child: ListView(
                        padding: EdgeInsets.zero,
                        children: [
                          _buildHistoryItem('高考志愿填报', '今天', 15),
                          _buildHistoryItem('专业选择建议', '昨天', 23),
                          _buildHistoryItem('院校推荐', '3天前', 8),
                          _buildHistoryItem('就业前景分析', '5天前', 12),
                          _buildHistoryItem('分数段分析', '1周前', 19),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              // 底部设置
              Container(
                padding: const EdgeInsets.all(ChatGPTTheme.paddingLarge),
                decoration: const BoxDecoration(
                  border: Border(
                    top: BorderSide(
                      color: ChatGPTTheme.darkDivider,
                      width: 1,
                    ),
                  ),
                ),
                child: Row(
                  children: [
                    const Icon(
                      Icons.settings,
                      color: ChatGPTTheme.darkTextSecondary,
                      size: 20,
                    ),
                    const SizedBox(width: ChatGPTTheme.paddingMedium),
                    const Text(
                      '设置',
                      style: TextStyle(
                        color: ChatGPTTheme.darkTextPrimary,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 构建历史记录项
  Widget _buildHistoryItem(String title, String time, int messageCount) {
    return InkWell(
      onTap: () {
        Navigator.pop(context);
        _showInfo('继续聊天功能开发中...');
      },
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: ChatGPTTheme.paddingLarge,
          vertical: ChatGPTTheme.paddingMedium,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                color: ChatGPTTheme.darkTextPrimary,
                fontSize: 14,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: ChatGPTTheme.paddingXSmall),
            Row(
              children: [
                Text(
                  time,
                  style: const TextStyle(
                    color: ChatGPTTheme.darkTextSecondary,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(width: ChatGPTTheme.paddingSmall),
                Text(
                  '$messageCount条消息',
                  style: const TextStyle(
                    color: ChatGPTTheme.darkTextSecondary,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// 构建消息列表
  Widget _buildMessagesList(List messages, bool isTyping) {
    return ListView.builder(
      controller: _scrollController,
      padding: EdgeInsets.zero,
      itemCount: messages.length + (isTyping ? 1 : 0),
      itemBuilder: (context, index) {
        if (index < messages.length) {
          final msg = messages[index];
          return ChatGPTMessageBubble(
            content: msg.content,
            isUser: msg.role == 'user',
            timestamp: msg.timestamp,
          );
        } else {
          // 显示正在输入指示器
          return _buildTypingIndicator();
        }
      },
    );
  }

  /// 构建正在输入指示器
  Widget _buildTypingIndicator() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(
        horizontal: ChatGPTTheme.paddingLarge,
        vertical: ChatGPTTheme.paddingMedium,
      ),
      decoration: const BoxDecoration(
        color: ChatGPTTheme.lightAIMessageBackground,
      ),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            margin: const EdgeInsets.only(
                right: ChatGPTTheme.paddingMedium),
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
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
          const SizedBox(width: ChatGPTTheme.paddingSmall),
          _buildDotsIndicator(),
        ],
      ),
    );
  }

  /// 构建跳动点指示器
  Widget _buildDotsIndicator() {
    return Row(
      children: List.generate(
        3,
        (index) => Container(
          margin: const EdgeInsets.symmetric(
              horizontal: ChatGPTTheme.paddingXSmall),
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: ChatGPTTheme.lightTextSecondary,
            shape: BoxShape.circle,
          ),
          child: _buildDotAnimation(index),
        ),
      ),
    );
  }

  Widget _buildDotAnimation(int index) {
    return TweenAnimationBuilder<double>(
      key: ValueKey(index),
      duration: const Duration(milliseconds: 1500),
      tween: Tween(begin: 0.3, end: 1.0),
      builder: (context, value, child) {
        return Opacity(
          opacity: value,
          child: child,
        );
      },
      child: Container(
        width: 8,
        height: 8,
        decoration: const BoxDecoration(
          color: ChatGPTTheme.lightTextSecondary,
          shape: BoxShape.circle,
        ),
      ),
    );
  }

  /// 构建建议卡片
  Widget _buildSuggestionCards() {
    return Container(
      padding: const EdgeInsets.all(ChatGPTTheme.paddingLarge),
      color: ChatGPTTheme.lightBackground,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '可以问学锋老师',
            style: TextStyle(
              color: ChatGPTTheme.lightTextPrimary,
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: ChatGPTTheme.paddingMedium),
          SuggestionCards(
            onSuggestionTap: _handleSubmit,
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _showInfo(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.blue),
    );
  }
}
