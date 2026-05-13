import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/theme/app_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/history_provider.dart';
import '../../providers/plan_provider.dart';
import '../../core/api_service.dart';

class HistoryDetailPage extends ConsumerStatefulWidget {
  const HistoryDetailPage({super.key});

  @override
  ConsumerState<HistoryDetailPage> createState() => _HistoryDetailPageState();
}

class _HistoryDetailPageState extends ConsumerState<HistoryDetailPage> {
  String? historyId;
  HistoryDetail? historyDetail;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // 获取传递的历史记录ID
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args != null && args is String) {
      historyId = args as String;
      _loadDetail();
    }
  }

  Future<void> _loadDetail() async {
    if (historyId == null) return;

    final authState = ref.read(authProvider);
    if (authState.token != null) {
      final detail = await ref.read(historyProvider.notifier).getHistoryDetail(
            authState.token!,
            historyId!,
          );

      if (mounted && detail != null) {
        setState(() {
          historyDetail = detail;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surfaceColor,
      appBar: AppBar(
        title: const Text('推荐详情'),
        backgroundColor: AppTheme.primaryBlue,
        foregroundColor: Colors.white,
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    // 加载中状态
    if (historyDetail == null) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    // 按类型分组推荐结果
    final Map<String, List<Map<String, dynamic>>> groupedResults = {};
    for (var result in historyDetail!.results) {
      final type = result['type'] ?? '其他';
      groupedResults.putIfAbsent(type, () => []).add(result);
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 推荐条件信息
          _buildConditionCard(),

          const SizedBox(height: AppTheme.spacingLg),

          // 推荐结果（按类型分组显示）
          ...groupedResults.entries.map((entry) {
            return _buildRecommendationGroup(entry.key, entry.value);
          }).toList(),
        ],
      ),
    );
  }

  /// 构建推荐条件卡片
  Widget _buildConditionCard() {
    if (historyDetail == null) return const SizedBox();

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
      ),
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.spacingLg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '推荐条件',
              style: AppTheme.titleMedium.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: AppTheme.spacingMd),

            // 条件详情
            _buildConditionRow('位次', '${historyDetail!.rank}'),
            const SizedBox(height: AppTheme.spacingSm),
            _buildConditionRow('省份', historyDetail!.province),
            const SizedBox(height: AppTheme.spacingSm),
            _buildConditionRow('偏好', _getPreferenceLabel(historyDetail!.preference)),
            const SizedBox(height: AppTheme.spacingSm),
            _buildConditionRow('推荐时间', _formatDateTime(historyDetail!.createdAt)),
            const SizedBox(height: AppTheme.spacingMd),

            // 科目标签
            if (historyDetail!.subjects.isNotEmpty)
              Wrap(
                spacing: AppTheme.spacingXs,
                runSpacing: AppTheme.spacingXs,
                children: historyDetail!.subjects.map((subject) {
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
                      subject,
                      style: AppTheme.bodySmall.copyWith(
                        color: AppTheme.primaryBlue,
                      ),
                    ),
                  );
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildConditionRow(String label, String value) {
    return Row(
      children: [
        SizedBox(
          width: 80,
          child: Text(
            label,
            style: AppTheme.bodyMedium.copyWith(
              color: AppTheme.mediumGray,
            ),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: AppTheme.bodyMedium.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }

  /// 构建推荐分组（冲/稳/保/垫）
  Widget _buildRecommendationGroup(String type, List<Map<String, dynamic>> results) {
    final color = _getTypeColor(type);
    final icon = _getTypeIcon(type);

    return Card(
      margin: const EdgeInsets.only(bottom: AppTheme.spacingLg),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 分组标题
          Container(
            padding: const EdgeInsets.all(AppTheme.spacingMd),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              border: Border(
                left: BorderSide(color: color, width: 4),
              ),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(AppTheme.radiusLg),
                bottomLeft: Radius.circular(AppTheme.radiusLg),
              ),
            ),
            child: Row(
              children: [
                Icon(icon, color: color, size: 20),
                const SizedBox(width: AppTheme.spacingXs),
                Text(
                  type,
                  style: AppTheme.titleMedium.copyWith(
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(width: AppTheme.spacingXs),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: color,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${results.length}个',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // 推荐列表
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: results.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final result = results[index];
              return ListTile(
                title: Text(
                  result['university_name'] ?? '',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('专业：${result['major_name'] ?? ''}'),
                    if (result['probability'] != null)
                      Text(
                        '录取概率：${result['probability']}%',
                        style: TextStyle(
                          color: color,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                  ],
                ),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // 加入志愿表按钮
                    IconButton(
                      icon: const Icon(Icons.add_circle_outline),
                      onPressed: () => _addToPlan(result),
                      tooltip: '加入志愿表',
                      color: AppTheme.primaryBlue,
                    ),
                  ],
                ),
              );
            },
          ),
        ],
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

  IconData _getTypeIcon(String type) {
    switch (type) {
      case '冲':
        return Icons.trending_up;
      case '稳':
        return Icons.balance;
      case '保':
        return Icons.security;
      case '垫':
        return Icons.lens_blur;
      default:
        return Icons.school;
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

  String _formatDateTime(String dateTimeStr) {
    try {
      final dateTime = DateTime.parse(dateTimeStr.replaceAll(' ', 'T'));
      return '${dateTime.year}年${dateTime.month}月${dateTime.day}日 ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return dateTimeStr;
    }
  }

  Future<void> _addToPlan(Map<String, dynamic> result) async {
    final authState = ref.read(authProvider);
    if (authState.token == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('请先登录'),
            backgroundColor: AppTheme.orange,
          ),
        );
      }
      return;
    }

    try {
      // 创建志愿计划项目
      final planData = {
        'id': '${result['university_name']}_${result['major_name']}',
        'university_name': result['university_name'],
        'major_name': result['major_name'],
        'probability': (result['probability'] as num?)?.toInt() ?? 70,
        'roi_score': 75,
        'tag': '历史推荐',
        'university_type': '本科',
        'city': '广东',
      };

      // 调用API添加到志愿表
      final success = await ApiService.addToPlan(
        authState.token!,
        planData,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(success ? '已加入志愿表' : '添加失败'),
            backgroundColor: success ? AppTheme.green : AppTheme.red,
          ),
        );

        // 如果添加成功，刷新志愿表
        if (success) {
          await ref.read(planProvider.notifier).loadPlans(authState.token!);
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('添加失败：$e'),
            backgroundColor: AppTheme.red,
          ),
        );
      }
    }
  }
}
