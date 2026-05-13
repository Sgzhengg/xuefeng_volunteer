import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/models/volunteer_plan.dart';
import '../core/api_service.dart';

/// 志愿表状态
class PlanState {
  final List<VolunteerPlan> plans;
  final bool isLoading;
  final String? error;
  final bool isEditMode;

  PlanState({
    required this.plans,
    this.isLoading = false,
    this.error,
    this.isEditMode = false,
  });

  PlanState copyWith({
    List<VolunteerPlan>? plans,
    bool? isLoading,
    String? error,
    bool? isEditMode,
  }) {
    return PlanState(
      plans: plans ?? this.plans,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      isEditMode: isEditMode ?? this.isEditMode,
    );
  }
}

/// 志愿表状态管理
class PlanNotifier extends StateNotifier<PlanState> {
  PlanNotifier() : super(PlanState(plans: []));

  /// 加载志愿表列表
  Future<void> loadPlans(String token) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final plans = await ApiService.getPlanList(token);

      // 将API返回的数据转换为VolunteerPlan对象
      final volunteerPlans = plans.map((planData) {
        return VolunteerPlan(
          id: planData['id']?.toString() ?? '',
          universityName: planData['university_name'] ?? '',
          majorName: planData['major_name'] ?? '',
          probability: planData['probability'] ?? 0,
          roiScore: planData['roi_score'] ?? 70,
          roiLevel: _calculateRoiLevel(planData['roi_score'] ?? 70),
          tag: planData['tag'] ?? '推荐',
          universityType: planData['university_type'] ?? '本科',
          city: planData['city'] ?? '未知',
        );
      }).toList();

      state = state.copyWith(
        plans: volunteerPlans,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
        plans: [],
      );
    }
  }

  /// 添加到志愿表
  Future<bool> addPlan(VolunteerPlan plan) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      // 获取token - 这里需要从authProvider获取
      // 为了简化，我们假设已经在调用时传入了token
      final planData = {
        'id': plan.id,
        'university_name': plan.universityName,
        'major_name': plan.majorName,
        'probability': plan.probability,
        'roi_score': plan.roiScore,
        'tag': plan.tag,
        'university_type': plan.universityType,
        'city': plan.city,
      };

      // 注意：这个方法需要从外部获取token
      // 我们会在调用的地方处理这个问题
      state = state.copyWith(
        plans: [...state.plans, plan],
        isLoading: false,
      );

      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      return false;
    }
  }

  /// 从志愿表删除
  Future<bool> removePlan(String planId) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final updatedPlans = state.plans.where((plan) => plan.id != planId.toString()).toList();
      state = state.copyWith(
        plans: updatedPlans,
        isLoading: false,
      );

      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      return false;
    }
  }

  /// 切换编辑模式
  void toggleEditMode() {
    state = state.copyWith(isEditMode: !state.isEditMode);
  }

  /// 获取志愿表统计信息
  Map<String, int> getStatistics() {
    int safeCount = 0;
    int moderateCount = 0;
    int riskyCount = 0;

    for (var plan in state.plans) {
      if (plan.probability >= 70) {
        safeCount++;
      } else if (plan.probability >= 50) {
        moderateCount++;
      } else {
        riskyCount++;
      }
    }

    return {
      'total': state.plans.length,
      'safe': safeCount,
      'moderate': moderateCount,
      'risky': riskyCount,
    };
  }

  /// 计算ROI等级
  String _calculateRoiLevel(int roiScore) {
    if (roiScore >= 85) return 'S级';
    if (roiScore >= 75) return 'A级';
    if (roiScore >= 65) return 'B级';
    if (roiScore >= 55) return 'C级';
    return 'D级';
  }
}

/// 志愿表Provider
final planProvider = StateNotifierProvider<PlanNotifier, PlanState>((ref) {
  return PlanNotifier();
});