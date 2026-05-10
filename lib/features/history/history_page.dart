import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/theme/app_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/history_provider.dart';

class HistoryPage extends ConsumerStatefulWidget {
  const HistoryPage({super.key});

  @override
  ConsumerState<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends ConsumerState<HistoryPage> {
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    // 页面加载时检查登录状态并加载数据
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
      _setupScrollListener();
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _setupScrollListener() {
    _scrollController.addListener(() {
      if (_scrollController.position.pixels >=
          _scrollController.position.maxScrollExtent - 200) {
        _loadMore();
      }
    });
  }

  Future<void> _loadData() async {
    final authState = ref.read(authProvider);
    if (authState.isLoggedIn && authState.token != null) {
      await ref.read(historyProvider.notifier).loadHistories(authState.token!, 1);
    }
  }

  Future<void> _loadMore() async {
    final authState = ref.read(authProvider);
    if (authState.isLoggedIn && authState.token != null) {
      await ref.read(historyProvider.notifier).loadMore(authState.token!);
    }
  }

  Future<void> _refresh() async {
    final authState = ref.read(authProvider);
    if (authState.isLoggedIn && authState.token != null) {
      await ref.read(historyProvider.notifier).refresh(authState.token!);
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final historyState = ref.watch(historyProvider);

    return Scaffold(
      backgroundColor: AppTheme.surfaceColor,
      appBar: AppBar(
        title: const Text('历史推荐'),
        backgroundColor: AppTheme.primaryBlue,
        foregroundColor: Colors.white,
        actions: [
          if (authState.isLoggedIn && historyState.histories.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.search),
              onPressed: () => _showSearchDialog(),
              tooltip: '搜索',
            ),
        ],
      ),
      body: _buildBody(authState, historyState),
    );
  }

  Widget _buildBody(AuthState authState, HistoryState historyState) {
    // 未登录状态
    if (!authState.isLoggedIn) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.login_outlined,
              size: 80,
              color: AppTheme.mediumGray,
            ),
            const SizedBox(height: AppTheme.spacingLg),
            Text(
              '请先登录查看历史推荐',
              style: AppTheme.titleMedium.copyWith(
                color: AppTheme.mediumGray,
              ),
            ),
            const SizedBox(height: AppTheme.spacingLg),
            ElevatedButton(
              onPressed: () => _navigateToLogin(),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryBlue,
                padding: const EdgeInsets.symmetric(
                  horizontal: AppTheme.spacingXl,
                  vertical: AppTheme.spacingMd,
                ),
              ),
              child: const Text(
                '去登录',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ),
          ],
        ),
      );
    }

    // 加载中状态
    if (historyState.isLoading && historyState.histories.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    // 空状态
    if (historyState.histories.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.history_outlined,
              size: 80,
              color: AppTheme.mediumGray,
            ),
            const SizedBox(height: AppTheme.spacingLg),
            Text(
              '还没有历史推荐记录',
              style: AppTheme.titleMedium.copyWith(
                color: AppTheme.mediumGray,
              ),
            ),
            const SizedBox(height: AppTheme.spacingSm),
            Text(
              '去推荐页面生成志愿方案吧',
              style: AppTheme.bodyMedium.copyWith(
                color: AppTheme.mediumGray,
              ),
            ),
          ],
        ),
      );
    }

    // 显示历史列表
    return RefreshIndicator(
      onRefresh: _refresh,
      child: ListView.separated(
        controller: _scrollController,
        padding: const EdgeInsets.all(AppTheme.spacingMd),
        itemCount: historyState.histories.length + (historyState.currentPage < historyState.totalPages ? 1 : 0),
        separatorBuilder: (context, index) => const SizedBox(height: AppTheme.spacingMd),
        itemBuilder: (context, index) {
          // 加载更多指示器
          if (index >= historyState.histories.length) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(AppTheme.spacingLg),
                child: CircularProgressIndicator(),
              ),
            );
          }

          final history = historyState.histories[index];
          return _buildHistoryCard(history);
        },
      ),
    );
  }

  /// 构建历史记录卡片
  Widget _buildHistoryCard(HistoryItem history) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
      ),
      child: InkWell(
        onTap: () => _navigateToDetail(history),
        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
        child: Padding(
          padding: const EdgeInsets.all(AppTheme.spacingMd),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 时间和删除按钮
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // 时间
                  Text(
                    _formatDate(history.createdAt),
                    style: AppTheme.bodySmall.copyWith(
                      color: AppTheme.mediumGray,
                    ),
                  ),

                  // 删除按钮
                  IconButton(
                    icon: const Icon(Icons.delete_outline, color: AppTheme.red),
                    onPressed: () => _deleteHistory(history),
                    tooltip: '删除记录',
                    constraints: const BoxConstraints(),
                    padding: EdgeInsets.zero,
                  ),
                ],
              ),

              const SizedBox(height: AppTheme.spacingSm),

              // 推荐条件
              Row(
                children: [
                  _buildInfoChip('位次', '${history.rank}'),
                  const SizedBox(width: AppTheme.spacingXs),
                  _buildInfoChip('省份', history.province),
                  const SizedBox(width: AppTheme.spacingXs),
                  _buildInfoChip('偏好', _getPreferenceLabel(history.preference)),
                ],
              ),

              if (history.subjects.isNotEmpty) ...[
                const SizedBox(height: AppTheme.spacingSm),
                Wrap(
                  spacing: AppTheme.spacingXs,
                  runSpacing: AppTheme.spacingXs,
                  children: history.subjects.take(3).map((subject) {
                    return _buildInfoChip('科目', subject);
                  }).toList(),
                ),
              ],

              const SizedBox(height: AppTheme.spacingMd),

              // 推荐结果预览
              Row(
                children: [
                  const Icon(
                    Icons.recommend,
                    color: AppTheme.primaryBlue,
                    size: 16,
                  ),
                  const SizedBox(width: AppTheme.spacingXs),
                  Text(
                    '推荐了 ${history.resultsCount} 个志愿方案',
                    style: AppTheme.bodyMedium.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),

              // 预览前3个推荐
              if (history.resultsSummary.isNotEmpty) ...[
                const SizedBox(height: AppTheme.spacingSm),
                ...history.resultsSummary.take(3).map((result) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      children: [
                        Container(
                          width: 4,
                          height: 4,
                          decoration: BoxDecoration(
                            color: AppTheme.primaryBlue,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: AppTheme.spacingXs),
                        Expanded(
                          child: Text(
                            '${result['university_name']} - ${result['major_name']}',
                            style: AppTheme.bodySmall.copyWith(
                              color: AppTheme.mediumGray,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        if (result['type'] != null)
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 6,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: _getTypeColor(result['type']).withOpacity(0.1),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              result['type'],
                              style: AppTheme.bodySmall.copyWith(
                                color: _getTypeColor(result['type']),
                                fontSize: 10,
                              ),
                            ),
                          ),
                      ],
                    ),
                  );
                }).toList(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInfoChip(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 8,
        vertical: 4,
      ),
      decoration: BoxDecoration(
        color: AppTheme.primaryBlue.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: AppTheme.primaryBlue.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Text(
        '$label: $value',
        style: AppTheme.bodySmall.copyWith(
          color: AppTheme.primaryBlue,
          fontSize: 11,
        ),
      ),
    );
  }

  Color _getTypeColor(String type) {
    switch (type) {
      case '冲':
        return AppTheme.red;
      case '稳':
        return AppTheme.green;
      case '保':
        return AppTheme.primaryBlue;
      case '垫':
        return AppTheme.mediumGray;
      default:
        return AppTheme.mediumGray;
    }
  }

  String _formatDate(String dateTimeStr) {
    try {
      final dateTime = DateTime.parse(dateTimeStr.replaceAll(' ', 'T'));
      final now = DateTime.now();
      final difference = now.difference(dateTime);

      if (difference.inDays == 0) {
        if (difference.inHours == 0) {
          return '刚刚';
        }
        return '${difference.inHours}小时前';
      } else if (difference.inDays == 1) {
        return '昨天';
      } else if (difference.inDays < 7) {
        return '${difference.inDays}天前';
      } else {
        return '${dateTime.month}月${dateTime.day}日';
      }
    } catch (e) {
      return dateTimeStr;
    }
  }

  String _getPreferenceLabel(String preference) {
    switch (preference) {
      case 'balanced':
        return '均衡型';
      case 'aggressive':
        return '冲刺型';
      case 'conservative':
        return '保守型';
      default:
        return preference;
    }
  }

  Future<void> _deleteHistory(HistoryItem history) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('删除记录'),
        content: Text('确定要删除${_formatDate(history.createdAt)}的推荐记录吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.red,
            ),
            child: const Text('确定'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      final authState = ref.read(authProvider);
      if (authState.token != null) {
        final success = await ref.read(historyProvider.notifier).deleteHistory(
              authState.token!,
              history.id,
            );

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(success ? '已删除记录' : '操作失败'),
              backgroundColor: success ? AppTheme.green : AppTheme.red,
            ),
          );
        }
      }
    }
  }

  void _showSearchDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('搜索历史'),
        content: TextField(
          decoration: const InputDecoration(
            hintText: '输入省份、科目或偏好类型',
            prefixIcon: Icon(Icons.search),
          ),
          onChanged: (value) {
            // 搜索功能
            ref.read(historyProvider.notifier).searchHistories(value);
          },
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
        ],
      ),
    );
  }

  void _navigateToDetail(HistoryItem history) {
    Navigator.pushNamed(
      context,
      '/history_detail',
      arguments: history.id,
    );
  }

  void _navigateToLogin() {
    Navigator.pushNamed(context, '/login');
  }
}
