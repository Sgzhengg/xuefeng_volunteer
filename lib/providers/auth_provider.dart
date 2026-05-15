import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/api_service.dart';

/// 认证状态
class AuthState {
  final String? token;
  final String? phoneNumber;
  final bool isLoggedIn;
  final bool isLoading;
  final String? error;

  AuthState({
    this.token,
    this.phoneNumber,
    required this.isLoggedIn,
    this.isLoading = false,
    this.error,
  });

  AuthState copyWith({
    String? token,
    String? phoneNumber,
    bool? isLoggedIn,
    bool? isLoading,
    String? error,
  }) {
    return AuthState(
      token: token ?? this.token,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      isLoggedIn: isLoggedIn ?? this.isLoggedIn,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

/// 认证状态管理
class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(AuthState(isLoggedIn: false));

  /// 初始化 - 检查本地存储的登录状态
  Future<void> initialize() async {
    state = state.copyWith(isLoading: true);

    try {
      // 这里可以调用API检查token是否仍然有效
      // 暂时先检查本地是否有token
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');
      final phoneNumber = prefs.getString('phone_number');
      final userId = prefs.getString('user_id'); // 支持匿名用户

      if (token != null && token.isNotEmpty) {
        // 有token，认为用户已登录（支持匿名用户和手机用户）
        state = AuthState(
          token: token,
          phoneNumber: phoneNumber, // 匿名用户为null
          isLoggedIn: true,
          isLoading: false,
        );
        print('✅ AuthNotifier: 用户已登录 (user_id: $userId, phone: $phoneNumber)');
      } else {
        state = AuthState(isLoggedIn: false, isLoading: false);
        print('⚠️ AuthNotifier: 未找到登录token');
      }
    } catch (e) {
      state = AuthState(
        isLoggedIn: false,
        isLoading: false,
        error: e.toString(),
      );
      print('❌ AuthNotifier初始化失败: $e');
    }
  }

  /// 发送验证码
  Future<bool> sendCode(String phone) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final result = await ApiService.sendCode(phone);
      state = state.copyWith(isLoading: false);

      return result['code'] == 0;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      return false;
    }
  }

  /// 登录
  Future<bool> login(String phone, String code) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final result = await ApiService.login(phone, code);

      if (result['code'] == 0 && result['data'] != null) {
        final token = result['data']['token'];
        final phoneNumber = result['data']['phone_number'] ?? phone;

        state = AuthState(
          token: token,
          phoneNumber: phoneNumber,
          isLoggedIn: true,
          isLoading: false,
        );

        return true;
      } else {
        state = state.copyWith(
          isLoading: false,
          error: result['message'] ?? '登录失败',
        );
        return false;
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      return false;
    }
  }

  /// 退出登录
  Future<void> logout() async {
    state = state.copyWith(isLoading: true);

    try {
      await ApiService.logout();
      await _clearLocalData();

      state = AuthState(
        isLoggedIn: false,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// 清除本地数据
  Future<void> _clearLocalData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('auth_token');
      await prefs.remove('phone_number');
    } catch (e) {
      print('清除本地数据失败: $e');
    }
  }

  /// 获取当前用户信息
  Future<Map<String, dynamic>?> getCurrentUser() async {
    if (state.token == null) {
      return null;
    }

    try {
      final result = await ApiService.getCurrentUser(state.token!);
      if (result['code'] == 0) {
        return result['data'];
      }
      return null;
    } catch (e) {
      return null;
    }
  }
}

/// 认证Provider
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final notifier = AuthNotifier();
  // 自动初始化
  notifier.initialize();
  return notifier;
});