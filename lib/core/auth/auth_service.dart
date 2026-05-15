import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../config/app_config.dart';
import '../models/user.dart';
import 'device_info_service.dart';

/// 认证服务
class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  final Dio _dio = Dio(BaseOptions(
    baseUrl: AppConfig.apiBaseUrl,
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
    headers: {
      'Content-Type': 'application/json',
    },
  ));

  final DeviceInfoService _deviceInfoService = DeviceInfoService();

  // 存储键
  static const String _tokenKey = 'auth_token';
  static const String _userIdKey = 'user_id';
  static const String _userDeviceIdKey = 'user_device_id';

  User? _currentUser;
  String? _currentToken;

  /// 当前登录用户
  User? get currentUser => _currentUser;

  /// 当前访问令牌
  String? get currentToken => _currentToken;

  /// 是否已登录
  bool get isLoggedIn => _currentUser != null && _currentToken != null;

  /// 初始化认证服务（APP启动时调用）
  Future<void> initialize() async {
    try {
      // 尝试从本地存储加载用户信息
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString(_tokenKey);
      final userId = prefs.getString(_userIdKey);
      final deviceId = prefs.getString(_userDeviceIdKey);

      if (token != null && userId != null && deviceId != null) {
        _currentToken = token;
        // 这里可以添加从后端获取用户信息的逻辑
        debugPrint('✅ 找到本地登录信息: $userId (设备: $deviceId)');
      }

      // 如果没有本地登录信息，自动进行匿名登录
      if (!isLoggedIn) {
        await anonymousLogin();
      }
    } catch (e) {
      debugPrint('❌ 初始化认证服务失败: $e');
      // 初始化失败时尝试匿名登录
      await anonymousLogin();
    }
  }

  /// 匿名登录（使用设备ID）
  Future<User> anonymousLogin() async {
    try {
      // 获取设备信息
      final loginDeviceInfo = await _deviceInfoService.getLoginDeviceInfo();
      final deviceId = loginDeviceInfo['device_id'] as String;

      debugPrint('🔐 开始匿名登录: $deviceId');

      // 调用后端匿名登录API
      final response = await _dio.post(
        '/api/v1/auth/device-login',
        data: loginDeviceInfo,
      );

      if (response.statusCode == 200) {
        final responseData = response.data as Map<String, dynamic>;

        // 检查响应码
        if (responseData['code'] != 0) {
          throw Exception('登录失败: ${responseData['message']}');
        }

        // 解析响应数据
        final data = responseData['data'] as Map<String, dynamic>;
        final user = User.fromJson(data['user']);
        final token = data['token'] as String;

        // 保存认证信息
        await _saveAuthInfo(user, token, deviceId);

        debugPrint('✅ 匿名登录成功: ${user.id}');
        return user;
      } else {
        throw Exception('登录失败: ${response.statusMessage}');
      }
    } on DioException catch (e) {
      debugPrint('❌ 匿名登录API调用失败: $e');

      // API调用失败时，创建本地匿名用户（降级处理）
      if (e.response?.statusCode == 404 || e.error is SocketException) {
        debugPrint('⚠️ 后端匿名登录API不可用，使用本地匿名用户');
        return await _createLocalAnonymousUser();
      }

      throw Exception('网络连接失败: ${e.message}');
    } catch (e) {
      debugPrint('❌ 匿名登录失败: $e');
      // 发生任何错误时，创建本地匿名用户
      return await _createLocalAnonymousUser();
    }
  }

  /// 创建本地匿名用户（降级处理）
  Future<User> _createLocalAnonymousUser() async {
    final loginDeviceInfo = await _deviceInfoService.getLoginDeviceInfo();
    final deviceId = loginDeviceInfo['device_id'] as String;
    final deviceInfo = loginDeviceInfo['device_info'] as Map<String, dynamic>;

    final user = User.createAnonymous(
      deviceId: deviceId,
      deviceInfo: deviceInfo,
    );

    // 生成临时token
    final token = 'local_token_${user.id}';

    await _saveAuthInfo(user, token, deviceId);

    debugPrint('✅ 创建本地匿名用户: ${user.id}');
    return user;
  }

  /// 保存认证信息到本地
  Future<void> _saveAuthInfo(User user, String token, String deviceId) async {
    _currentUser = user;
    _currentToken = token;

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
    await prefs.setString(_userIdKey, user.id);
    await prefs.setString(_userDeviceIdKey, deviceId);
  }

  /// 更新Dio实例的认证头
  void updateAuthHeaders() {
    if (_currentToken != null) {
      _dio.options.headers['Authorization'] = 'Bearer $_currentToken';
    }
  }

  /// 登出
  Future<void> logout() async {
    _currentUser = null;
    _currentToken = null;

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userIdKey);
    await prefs.remove(_userDeviceIdKey);

    debugPrint('✅ 用户已登出');
  }

  /// 更新用户信息
  Future<void> updateUserInfo({
    String? nickname,
    String? phoneNumber,
  }) async {
    if (_currentUser == null) return;

    try {
      final response = await _dio.put(
        '/api/v1/auth/user/profile',
        data: {
          if (nickname != null) 'nickname': nickname,
          if (phoneNumber != null) 'phone_number': phoneNumber,
        },
      );

      if (response.statusCode == 200) {
        final responseData = response.data as Map<String, dynamic>;

        // 检查响应码
        if (responseData['code'] == 0) {
          final updatedUser = User.fromJson(responseData['user']);
          _currentUser = updatedUser;
          debugPrint('✅ 用户信息已更新');
        }
      }
    } catch (e) {
      debugPrint('❌ 更新用户信息失败: $e');
      // 更新失败时，仅更新本地用户信息
      _currentUser = _currentUser!.copyWith(
        nickname: nickname ?? _currentUser!.nickname,
        phoneNumber: phoneNumber ?? _currentUser!.phoneNumber,
      );
    }
  }

  /// 获取认证后的Dio实例
  Dio get authenticatedDio {
    final dio = Dio(BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        if (_currentToken != null) 'Authorization': 'Bearer $_currentToken',
      },
    ));
    return dio;
  }
}