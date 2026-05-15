import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/auth/auth_service.dart';
import '../core/models/user.dart';

/// 认证服务Provider
final authServiceProvider = Provider<AuthService>((ref) {
  return AuthService();
});

/// 当前用户Provider
final currentUserProvider = StreamProvider<User?>((ref) {
  final authService = ref.watch(authServiceProvider);
  // 这里可以返回用户状态变化的流
  return Stream.value(authService.currentUser);
});

/// 是否已登录Provider
final isLoggedInProvider = Provider<bool>((ref) {
  final authService = ref.watch(authServiceProvider);
  return authService.isLoggedIn;
});

/// 用户显示名称Provider
final userDisplayNameProvider = Provider<String>((ref) {
  final authService = ref.watch(authServiceProvider);
  return authService.currentUser?.displayName ?? '游客用户';
});

/// 是否为匿名用户Provider
final isAnonymousUserProvider = Provider<bool>((ref) {
  final authService = ref.watch(authServiceProvider);
  return authService.currentUser?.isAnonymous ?? true;
});