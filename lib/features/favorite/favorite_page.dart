import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/theme/app_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/favorite_provider.dart';
import '../../core/api_service.dart';

class FavoritePage extends ConsumerStatefulWidget {
  const FavoritePage({super.key});

  @override
  ConsumerState<FavoritePage> createState() => _FavoritePageState();
}

class _FavoritePageState extends ConsumerState<FavoritePage> {
  @override
  void initState() {
    super.initState();
    // 页面加载时检查登录状态并加载数据
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    final authState = ref.read(authProvider);
    if (authState.isLoggedIn && authState.token != null) {
      await ref.read(favoriteProvider.notifier).loadFavorites(authState.token!);
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final favoriteState = ref.watch(favoriteProvider);

    return Scaffold(
      backgroundColor: AppTheme.surfaceColor,
      appBar: AppBar(
        title: const Text('我的收藏'),
        backgroundColor: AppTheme.primaryBlue,
        foregroundColor: Colors.white,
        actions: [
          if (authState.isLoggedIn && favoriteState.favorites.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.search),
              onPressed: () => _showSearchDialog(),
              tooltip: '搜索',
            ),
        ],
      ),
      body: _buildBody(authState, favoriteState),
    );
  }

  Widget _buildBody(AuthState authState, FavoriteState favoriteState) {
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
              '请先登录查看收藏',
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
    if (favoriteState.isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    // 空状态
    if (favoriteState.favorites.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.favorite_border,
              size: 80,
              color: AppTheme.mediumGray,
            ),
            const SizedBox(height: AppTheme.spacingLg),
            Text(
              '还没有收藏任何院校',
              style: AppTheme.titleMedium.copyWith(
                color: AppTheme.mediumGray,
              ),
            ),
            const SizedBox(height: AppTheme.spacingSm),
            Text(
              '去推荐页面看看吧',
              style: AppTheme.bodyMedium.copyWith(
                color: AppTheme.mediumGray,
              ),
            ),
          ],
        ),
      );
    }

    // 显示收藏列表
    return Column(
      children: [
        // 统计信息
        _buildStatisticsHeader(favoriteState),

        // 收藏列表
        Expanded(
          child: RefreshIndicator(
            onRefresh: _loadData,
            child: ListView.separated(
              padding: const EdgeInsets.all(AppTheme.spacingMd),
              itemCount: favoriteState.favorites.length,
              separatorBuilder: (context, index) => const SizedBox(height: AppTheme.spacingMd),
              itemBuilder: (context, index) {
                final favorite = favoriteState.favorites[index];
                return _buildFavoriteCard(favorite);
              },
            ),
          ),
        ),
      ],
    );
  }

  /// 构建统计信息头部
  Widget _buildStatisticsHeader(FavoriteState favoriteState) {
    final stats = ref.read(favoriteProvider.notifier).getStatistics();

    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingLg),
      decoration: BoxDecoration(
        color: AppTheme.primaryBlue.withOpacity(0.1),
        border: Border(
          bottom: BorderSide(
            color: AppTheme.primaryBlue.withOpacity(0.2),
            width: 1,
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildStatItem('收藏总数', '${stats['total']}', Icons.favorite),
          _buildStatItem('院校数', '${stats['universities']}', Icons.school),
          _buildStatItem('专业数', '${stats['majors']}', Icons.book),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: AppTheme.primaryBlue, size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: AppTheme.titleLarge.copyWith(
            color: AppTheme.primaryBlue,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: AppTheme.bodySmall.copyWith(
            color: AppTheme.mediumGray,
          ),
        ),
      ],
    );
  }

  /// 构建收藏卡片
  Widget _buildFavoriteCard(FavoriteItem favorite) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
      ),
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.spacingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 院校名称和删除按钮
            Row(
              children: [
                Expanded(
                  child: Text(
                    favorite.universityName,
                    style: AppTheme.titleMedium.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.delete_outline, color: AppTheme.red),
                  onPressed: () => _removeFavorite(favorite),
                  tooltip: '取消收藏',
                  constraints: const BoxConstraints(),
                  padding: EdgeInsets.zero,
                ),
              ],
            ),

            const SizedBox(height: AppTheme.spacingSm),

            // 专业名称
            Text(
              favorite.majorName,
              style: AppTheme.bodyMedium.copyWith(
                color: AppTheme.mediumGray,
              ),
            ),

            const SizedBox(height: AppTheme.spacingMd),

            // 操作按钮
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _addToPlan(favorite),
                    icon: const Icon(Icons.add_circle_outline, size: 18),
                    label: const Text('加入志愿表'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppTheme.primaryBlue,
                      side: BorderSide(color: AppTheme.primaryBlue.withOpacity(0.3)),
                    ),
                  ),
                ),
                const SizedBox(width: AppTheme.spacingSm),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      // TODO: 查看详情
                      _showInfo('详情功能开发中...');
                    },
                    icon: const Icon(Icons.info_outline, size: 18),
                    label: const Text('查看详情'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppTheme.mediumGray,
                      side: BorderSide(color: AppTheme.mediumGray.withOpacity(0.3)),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _removeFavorite(FavoriteItem favorite) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('取消收藏'),
        content: Text('确定要取消收藏「${favorite.universityName} - ${favorite.majorName}」吗？'),
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
        final success = await ref.read(favoriteProvider.notifier).removeFavorite(
              authState.token!,
              favorite.id,
            );

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(success ? '已取消收藏' : '操作失败'),
              backgroundColor: success ? AppTheme.green : AppTheme.red,
            ),
          );
        }
      }
    }
  }

  Future<void> _addToPlan(FavoriteItem favorite) async {
    final authState = ref.read(authProvider);
    if (authState.token == null) return;

    try {
      final success = await ApiService.addToPlan(
        authState.token!,
        {
          'id': favorite.id,
          'university_name': favorite.universityName,
          'major_name': favorite.majorName,
          'probability': 70, // 默认概率
          'roi_score': 75,
          'tag': '收藏',
          'university_type': '本科',
          'city': '广东',
        },
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(success ? '已加入志愿表' : '添加失败'),
            backgroundColor: success ? AppTheme.green : AppTheme.red,
          ),
        );
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

  void _showSearchDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('搜索收藏'),
        content: TextField(
          decoration: const InputDecoration(
            hintText: '输入院校或专业名称',
            prefixIcon: Icon(Icons.search),
          ),
          onChanged: (value) {
            // 搜索功能
            ref.read(favoriteProvider.notifier).searchFavorites(value);
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

  void _showInfo(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppTheme.primaryBlue,
      ),
    );
  }

  void _navigateToLogin() {
    Navigator.pushNamed(context, '/login');
  }
}