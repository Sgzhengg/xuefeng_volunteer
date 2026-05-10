import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../shared/theme/app_theme.dart';
import '../../../core/models/volunteer_scheme.dart' as simulator_models;
import '../../../core/models/volunteer_plan.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/plan_provider.dart';
import '../../../providers/favorite_provider.dart';
import '../../../core/api_service.dart';

class SchemeCard extends ConsumerWidget {
  final String title;
  final List<simulator_models.SchoolChoice> choices;
  final Color color;

  const SchemeCard({
    super.key,
    required this.title,
    required this.choices,
    required this.color,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              border: Border(
                left: BorderSide(color: color, width: 4),
              ),
            ),
            child: Row(
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: color,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${choices.length}个',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // 院校列表
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: choices.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final choice = choices[index];
              return ListTile(
                title: Text(
                  choice.universityName,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('专业：${choice.majorName}'),
                    const SizedBox(height: 4),
                    Text(
                      choice.type,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // 录取概率
                    Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          '${choice.probability.toInt()}%',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: color,
                          ),
                        ),
                        Text(
                          choice.type,
                          style: const TextStyle(
                            fontSize: 10,
                            color: Colors.grey,
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(width: 8),

                    // 收藏按钮
                    Consumer(
                      builder: (context, ref, child) {
                        final favoriteState = ref.watch(favoriteProvider);
                        final itemId = '${choice.universityName}_${choice.majorName}';
                        final isFavorited = favoriteState.favoriteStatus[itemId] ?? false;

                        return IconButton(
                          icon: Icon(
                            isFavorited ? Icons.favorite : Icons.favorite_border,
                            color: isFavorited ? AppTheme.red : AppTheme.mediumGray,
                          ),
                          onPressed: () async {
                            await _toggleFavorite(context, ref, choice);
                          },
                          tooltip: isFavorited ? '取消收藏' : '收藏',
                        );
                      },
                    ),

                    // 添加到志愿表按钮
                    IconButton(
                      icon: const Icon(Icons.add_circle_outline),
                      onPressed: () async {
                        await _addToPlan(context, ref, choice);
                      },
                      tooltip: '添加到志愿表',
                      color: AppTheme.primaryBlue,
                    ),

                    // 分享按钮
                    IconButton(
                      icon: const Icon(Icons.share),
                      onPressed: () {
                        _showShareDialog(context, choice);
                      },
                      tooltip: '分享',
                      color: AppTheme.mediumGray,
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

  Future<void> _addToPlan(BuildContext context, WidgetRef ref, simulator_models.SchoolChoice choice) async {
    try {
      // 检查登录状态
      final authState = ref.read(authProvider);
      if (!authState.isLoggedIn || authState.token == null) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('请先登录'),
              backgroundColor: AppTheme.orange,
            ),
          );
        }
        return;
      }

      // 创建志愿计划项目
      final plan = VolunteerPlan(
        id: '${choice.universityName}_${choice.majorName}',
        universityName: choice.universityName,
        majorName: choice.majorName,
        probability: choice.probability.toInt(),
        roiScore: 70,
        roiLevel: 'B级',
        tag: choice.type,
        universityType: '本科',
        city: '广东',
      );

      // 调用API添加到志愿表
      final success = await ApiService.addToPlan(
        authState.token!,
        {
          'id': plan.id,
          'university_name': plan.universityName,
          'major_name': plan.majorName,
          'probability': plan.probability,
          'roi_score': plan.roiScore,
          'tag': plan.tag,
          'university_type': plan.universityType,
          'city': plan.city,
        },
      );

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(success ? '已加入志愿表' : '添加失败，请重试'),
            backgroundColor: success ? AppTheme.green : AppTheme.red,
          ),
        );

        // 如果添加成功，刷新志愿表
        if (success) {
          await ref.read(planProvider.notifier).loadPlans(authState.token!);
        }
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('添加失败：$e'),
            backgroundColor: AppTheme.red,
          ),
        );
      }
    }
  }

  Future<void> _toggleFavorite(BuildContext context, WidgetRef ref, simulator_models.SchoolChoice choice) async {
    try {
      // 检查登录状态
      final authState = ref.read(authProvider);
      if (!authState.isLoggedIn || authState.token == null) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('请先登录'),
              backgroundColor: AppTheme.orange,
            ),
          );
        }
        return;
      }

      final itemId = '${choice.universityName}_${choice.majorName}';
      final favoriteState = ref.read(favoriteProvider);
      final isFavorited = favoriteState.favoriteStatus[itemId] ?? false;

      // 收藏数据
      final favoriteData = {
        'university_id': choice.universityName.hashCode, // 使用哈希作为ID
        'major_id': choice.majorName.hashCode,
        'university_name': choice.universityName,
        'major_name': choice.majorName,
      };

      // 切换收藏状态
      final success = await ref.read(favoriteProvider.notifier).toggleFavorite(
            authState.token!,
            itemId,
            favoriteData,
          );

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              success
                  ? (isFavorited ? '已取消收藏' : '已收藏')
                  : '操作失败，请重试',
            ),
            backgroundColor: success ? AppTheme.green : AppTheme.red,
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('操作失败：$e'),
            backgroundColor: AppTheme.red,
          ),
        );
      }
    }
  }

  void _showShareDialog(BuildContext context, simulator_models.SchoolChoice choice) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('分享推荐'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('院校：${choice.universityName}'),
            Text('专业：${choice.majorName}'),
            Text('录取概率：${choice.probability.toInt()}%'),
            Text('类型：${choice.type}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('分享功能开发中...'),
                  backgroundColor: AppTheme.orange,
                ),
              );
            },
            child: const Text('分享'),
          ),
        ],
      ),
    );
  }
}