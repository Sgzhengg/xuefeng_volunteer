import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import '../../../../core/http.dart';
import '../../../../core/models/volunteer_plan.dart';

// 志愿表状态
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

// 志愿表Notifier
class PlanNotifier extends StateNotifier<PlanState> {
  PlanNotifier() : super(PlanState(plans: []));

  // 加载志愿表
  Future<void> loadPlans() async {
    state = state.copyWith(isLoading: true);

    try {
      final response = await ApiClient.get('/api/v1/plan/list');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final plansData = data['data']['plans'] as List<dynamic>?;

        if (plansData != null) {
          final plans = plansData.map((json) => VolunteerPlan.fromJson(json)).toList();
          state = state.copyWith(plans: plans, isLoading: false);
        } else {
          state = state.copyWith(plans: [], isLoading: false);
        }
      } else {
        state = state.copyWith(
          error: '加载失败',
          isLoading: false,
        );
      }
    } catch (e) {
      state = state.copyWith(
        error: e.toString(),
        isLoading: false,
        plans: [],
      );
    }
  }

  // 删除志愿
  Future<bool> removePlan(String majorId) async {
    try {
      final response = await ApiClient.delete('/api/v1/plan/remove?major_id=$majorId');

      if (response.statusCode == 200) {
        // 从本地列表中移除
        final updatedPlans = state.plans.where((plan) => plan.id != majorId).toList();
        state = state.copyWith(plans: updatedPlans);
        return true;
      } else {
        return false;
      }
    } catch (e) {
      print('删除失败: $e');
      return false;
    }
  }

  // 添加志愿
  Future<bool> addPlan(VolunteerPlan plan) async {
    try {
      final response = await ApiClient.post('/api/v1/plan/add', body: {
        'university_id': plan.id,
        'major_id': plan.id,
        'university_name': plan.universityName,
        'major_name': plan.majorName,
        'probability': plan.probability,
        'roi_score': plan.roiScore,
        'tag': plan.tag,
      });

      if (response.statusCode == 200) {
        // 添加到本地列表
        state = state.copyWith(plans: [...state.plans, plan]);
        return true;
      } else {
        return false;
      }
    } catch (e) {
      print('添加失败: $e');
      return false;
    }
  }

  // 切换编辑模式
  void toggleEditMode() {
    state = state.copyWith(isEditMode: !state.isEditMode);
  }

  // 评估志愿表
  Future<PlanEvaluation?> evaluatePlans() async {
    try {
      final response = await ApiClient.get('/api/v1/plan/evaluate');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return PlanEvaluation.fromJson(data['data']);
      } else {
        return null;
      }
    } catch (e) {
      print('评估失败: $e');
      return null;
    }
  }
}

// Provider
final planProvider = StateNotifierProvider<PlanNotifier, PlanState>((ref) {
  final notifier = PlanNotifier();
  // 自动加载
  notifier.loadPlans();
  return notifier;
});

// 用户认证状态
class AuthState {
  final String? token;
  final String? phoneNumber;
  final bool isLoggedIn;

  AuthState({
    this.token,
    this.phoneNumber,
    required this.isLoggedIn,
  });

  AuthState copyWith({
    String? token,
    String? phoneNumber,
    bool? isLoggedIn,
  }) {
    return AuthState(
      token: token ?? this.token,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      isLoggedIn: isLoggedIn ?? this.isLoggedIn,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(AuthState(isLoggedIn: false));

  Future<void> loadToken() async {
    // 从本地加载token
    final token = await ApiClient._getToken();
    state = AuthState(
      token: token.isNotEmpty ? token : null,
      phoneNumber: '',
      isLoggedIn: token.isNotEmpty,
    );
  }

  Future<bool> login(String phoneNumber, String verificationCode) async {
    // MVP阶段：验证码写死为123456
    if (verificationCode != '123456') {
      return false;
    }

    try {
      final response = await ApiClient.post('/api/v1/auth/login', body: {
        'phone_number': phoneNumber,
        'verification_code': verificationCode,
      });

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final token = data['data']['token'] as String;

        // 保存token
        await _saveToken(token);

        state = AuthState(
          token: token,
          phoneNumber: phoneNumber,
          isLoggedIn: true,
        );
        return true;
      } else {
        return false;
      }
    } catch (e) {
      print('登录失败: $e');
      return false;
    }
  }

  Future<void> logout() async {
    // 清除本地token
    try {
      final appDocDir = await getApplicationDocumentsDirectory();
      final tokenFile = File('${appDocDir.path}/auth_token.txt');
      if (await tokenFile.exists()) {
        await tokenFile.delete();
      }
    } catch (e) {
      print('清除token失败: $e');
    }

    state = AuthState(
      token: null,
      phoneNumber: null,
      isLoggedIn: false,
    );
  }
}

// Token管理函数
Future<String> _getToken() async {
  try {
    final appDocDir = await getApplicationDocumentsDirectory();
    final tokenFile = File('${appDocDir.path}/auth_token.txt');

    if (await tokenFile.exists()) {
      return await tokenFile.readAsString();
    }
    return '';
  } catch (e) {
    print('Error reading token: $e');
    return '';
  }
}

Future<void> _saveToken(String token) async {
  try {
    final appDocDir = await getApplicationDocumentsDirectory();
    final tokenFile = File('${appDocDir.path}/auth_token.txt');
    await tokenFile.writeAsString(token);
  } catch (e) {
    print('Error saving token: $e');
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final notifier = AuthNotifier();
  notifier.loadToken();
  return notifier;
});