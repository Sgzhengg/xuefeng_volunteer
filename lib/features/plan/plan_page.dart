import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/theme/app_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/plan_provider.dart';
import '../../core/api_service.dart';
import '../../core/models/volunteer_plan.dart';
import 'widgets/plan_card.dart';
import 'widgets/evaluation_dialog.dart';

class PlanPage extends ConsumerStatefulWidget {
  const PlanPage({super.key});

  @override
  ConsumerState<PlanPage> createState() => _PlanPageState();
}

class _PlanPageState extends ConsumerState<PlanPage> {
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
      await ref.read(planProvider.notifier).loadPlans(authState.token!);
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final planState = ref.watch(planProvider);

    return Scaffold(
      backgroundColor: AppTheme.surfaceColor,
      appBar: AppBar(
        title: const Text('我的志愿表'),
        backgroundColor: AppTheme.primaryBlue,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          if (authState.isLoggedIn && planState.plans.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.assessment),
              onPressed: () => _showEvaluationDialog(),
              tooltip: '评估志愿表',
            ),
        ],
      ),
      body: _buildBody(authState, planState),
    );
  }

  Widget _buildBody(AuthState authState, PlanState planState) {
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
              '请先登录查看志愿表',
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
    if (planState.isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    // 空状态
    if (planState.plans.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.inbox_outlined,
              size: 80,
              color: AppTheme.mediumGray,
            ),
            const SizedBox(height: AppTheme.spacingLg),
            Text(
              '志愿表还是空的',
              style: AppTheme.titleMedium.copyWith(
                color: AppTheme.mediumGray,
              ),
            ),
            const SizedBox(height: AppTheme.spacingSm),
            Text(
              '去模拟页面添加志愿吧',
              style: AppTheme.bodyMedium.copyWith(
                color: AppTheme.mediumGray,
              ),
            ),
          ],
        ),
      );
    }

    // 显示志愿列表
    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView.separated(
        padding: const EdgeInsets.all(AppTheme.spacingMd),
        itemCount: planState.plans.length,
        separatorBuilder: (context, index) => const SizedBox(height: AppTheme.spacingMd),
        itemBuilder: (context, index) {
          final plan = planState.plans[index];
          return Dismissible(
            key: Key(plan.id),
            direction: DismissDirection.endToStart,
            onDismissed: (direction) async {
              await _removePlan(plan.id);
            },
            background: Container(
              alignment: Alignment.centerRight,
              padding: const EdgeInsets.only(right: AppTheme.spacingLg),
              decoration: BoxDecoration(
                color: AppTheme.red,
                borderRadius: BorderRadius.circular(AppTheme.radiusSm),
              ),
              child: const Icon(
                Icons.delete,
                color: Colors.white,
              ),
            ),
            child: PlanCard(
              plan: plan,
              onDelete: () => _removePlan(plan.id),
            ),
          );
        },
      ),
    );
  }

  Future<void> _removePlan(String planId) async {
    final authState = ref.read(authProvider);
    if (authState.token == null) return;

    try {
      final success = await ApiService.removeFromPlan(authState.token!, int.parse(planId));
      if (success) {
        await ref.read(planProvider.notifier).removePlan(planId);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('已删除'),
              backgroundColor: AppTheme.green,
            ),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('删除失败'),
              backgroundColor: AppTheme.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('删除失败：$e'),
            backgroundColor: AppTheme.red,
          ),
        );
      }
    }
  }

  Future<void> _showEvaluationDialog() async {
    final authState = ref.read(authProvider);
    if (authState.token == null) return;

    try {
      final evaluationData = await ApiService.evaluatePlan(authState.token!);

      // 将Map转换为PlanEvaluation对象
      final evaluation = PlanEvaluation.fromJson(Map<String, dynamic>.from(evaluationData));

      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => EvaluationDialog(
            evaluation: evaluation,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('评估失败：$e'),
            backgroundColor: AppTheme.red,
          ),
        );
      }
    }
  }

  void _navigateToLogin() {
    Navigator.pushNamed(context, '/login');
  }
}