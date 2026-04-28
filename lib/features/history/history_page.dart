import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:isar/isar.dart';
import '../../core/models/chat_message.dart';
import '../../shared/theme/app_theme.dart';

class HistoryPage extends ConsumerStatefulWidget {
  const HistoryPage({super.key});

  @override
  ConsumerState<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends ConsumerState<HistoryPage> {
  bool _isLoading = true;
  List<Map<String, dynamic>> _sessions = [];

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    setState(() => _isLoading = true);

    try {
      // TODO: 从Isar数据库加载历史记录
      // final isar = ref.read(isarProvider);
      // final messages = await isar.chatMessages.where().sortByTimestamp().findAll();
      //
      // 按会话分组
      // final Map<String, List<ChatMessage>> grouped = {};
      // for (final message in messages) {
      //   final sessionId = message.sessionId ?? 'default';
      //   grouped.putIfAbsent(sessionId, () => []).add(message);
      // }
      //
      // 转换为会话列表
      // final sessions = grouped.entries.map((entry) {
      //   final messages = entry.value;
      //   return {
      //     'id': entry.key,
      //     'title': messages.first.content.substring(0, 30),
      //     'timestamp': messages.first.timestamp,
      //     'messageCount': messages.length,
      //     'lastMessage': messages.last.content,
      //   };
      // }).toList();

      // Mock数据用于演示
      _sessions = [
        {
          'id': '1',
          'title': '关于计算机专业的咨询',
          'timestamp': DateTime.now().millisecondsSinceEpoch - 86400000,
          'messageCount': 15,
          'lastMessage': '总的来说，计算机专业是个不错的选择...',
        },
        {
          'id': '2',
          'title': '高考志愿填报建议',
          'timestamp': DateTime.now().millisecondsSinceEpoch - 172800000,
          'messageCount': 23,
          'lastMessage': '建议按照冲刺、稳妥、保底的比例...',
        },
      ];

      // 按时间倒序排序
      _sessions.sort((a, b) => (b['timestamp'] as int).compareTo(a['timestamp'] as int));

    } catch (e) {
      _showError('加载失败：$e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _deleteSession(String sessionId) async {
    // TODO: 从数据库删除会话
    // final isar = ref.read(isarProvider);
    // await isar.writeTxn(() async {
    //   await isar.chatMessages.filter().sessionIdEqualTo(sessionId).deleteAll();
    // });

    setState(() {
      _sessions.removeWhere((session) => session['id'] == sessionId);
    });

    _showSuccess('会话已删除');
  }

  void _continueChat(String sessionId) {
    // TODO: 导航到聊天页面并加载历史消息
    // Navigator.push(
    //   context,
    //   MaterialPageRoute(
    //     builder: (context) => ChatPage(sessionId: sessionId),
    //   ),
    // );

    _showInfo('继续聊天功能开发中...');
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.green),
    );
  }

  void _showInfo(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.blue),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('历史记录'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadHistory,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _sessions.isEmpty
              ? _buildEmptyState()
              : ListView.builder(
                  padding: const EdgeInsets.all(AppTheme.spacingMd),
                  itemCount: _sessions.length,
                  itemBuilder: (context, index) {
                    final session = _sessions[index];
                    return _buildSessionCard(session);
                  },
                ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.chat_bubble_outline, size: 64, color: AppTheme.mediumGray),
          const SizedBox(height: AppTheme.spacingMd),
          Text(
            '还没有历史记录',
            style: AppTheme.titleSmall.copyWith(color: AppTheme.mediumGray),
          ),
          const SizedBox(height: AppTheme.spacingSm),
          Text(
            '开始和学锋老师聊天吧！',
            style: AppTheme.bodyMedium.copyWith(color: AppTheme.mediumGray),
          ),
        ],
      ),
    );
  }

  Widget _buildSessionCard(Map<String, dynamic> session) {
    final timestamp = DateTime.fromMillisecondsSinceEpoch(session['timestamp'] as int);
    final timeStr = _formatTimestamp(timestamp);

    return Container(
      margin: const EdgeInsets.only(bottom: AppTheme.spacingMd),
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border.all(color: AppTheme.surfaceContainerHighest),
      ),
      child: InkWell(
        onTap: () => _continueChat(session['id'] as String),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    session['title'] as String,
                    style: AppTheme.titleSmall,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Text(
                  timeStr,
                  style: AppTheme.bodySmall.copyWith(color: AppTheme.mediumGray),
                ),
              ],
            ),
            const SizedBox(height: AppTheme.spacingXs),
            Text(
              session['lastMessage'] as String,
              style: AppTheme.bodySmall.copyWith(color: AppTheme.mediumGray),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: AppTheme.spacingSm),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${session['messageCount']} 条消息',
                  style: AppTheme.labelSmall.copyWith(color: AppTheme.mediumGray),
                ),
                PopupMenuButton<String>(
                  icon: const Icon(Icons.more_vert, size: 20),
                  onSelected: (value) {
                    if (value == 'delete') {
                      _showDeleteConfirmDialog(session['id'] as String);
                    }
                  },
                  itemBuilder: (context) => [
                    const PopupMenuItem(
                      value: 'delete',
                      child: Row(
                        children: [
                          Icon(Icons.delete, size: 20, color: Colors.red),
                          SizedBox(width: AppTheme.spacingXs),
                          Text('删除'),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inMinutes < 1) {
      return '刚刚';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}分钟前';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}小时前';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}天前';
    } else {
      return '${timestamp.month}月${timestamp.day}日';
    }
  }

  void _showDeleteConfirmDialog(String sessionId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认删除'),
        content: const Text('确定要删除这个会话吗？此操作无法撤销。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _deleteSession(sessionId);
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('删除'),
          ),
        ],
      ),
    );
  }
}
