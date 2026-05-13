import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';

/// API服务类 - 封装所有后端接口调用
class ApiService {
  static String get baseUrl => '${AppConfig.apiBaseUrl}/api/v1';

  /// 获取存储的token
  static Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('auth_token');
  }

  /// 保存token
  static Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }

  /// 清除token
  static Future<void> _clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    await prefs.remove('phone_number');
  }

  /// 获取带认证的请求头
  static Future<Map<String, String>> _getHeaders({bool needAuth = true}) async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };

    if (needAuth) {
      final token = await _getToken();
      if (token != null && token.isNotEmpty) {
        headers['Authorization'] = 'Bearer $token';
      }
    }

    return headers;
  }

  /// 处理HTTP响应
  static dynamic _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      try {
        final data = jsonDecode(response.body);
        return data;
      } catch (e) {
        return {'message': 'Success', 'data': null};
      }
    } else {
      try {
        final error = jsonDecode(response.body);
        throw Exception(error['message'] ?? '请求失败');
      } catch (e) {
        throw Exception('HTTP ${response.statusCode}: ${response.reasonPhrase}');
      }
    }
  }

  // ==================== 认证相关接口 ====================

  /// 发送验证码
  /// MVP阶段：固定返回验证码123456
  static Future<Map> sendCode(String phone) async {
    try {
      final headers = await _getHeaders(needAuth: false);
      final response = await http.post(
        Uri.parse('$baseUrl/auth/send_code'),
        headers: headers,
        body: jsonEncode({'phone_number': phone}),
      );

      return _handleResponse(response);
    } catch (e) {
      throw Exception('发送验证码失败: $e');
    }
  }

  /// 用户登录
  /// phone: 手机号
  /// code: 验证码 (MVP阶段固定为123456)
  static Future<Map> login(String phone, String code) async {
    try {
      final headers = await _getHeaders(needAuth: false);
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: headers,
        body: jsonEncode({
          'phone_number': phone,
          'verification_code': code,
        }),
      );

      final result = _handleResponse(response);

      // 登录成功后保存token
      if (result['code'] == 0 && result['data'] != null) {
        final token = result['data']['token'];
        await _saveToken(token);

        // 保存手机号
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('phone_number', phone);
      }

      return result;
    } catch (e) {
      throw Exception('登录失败: $e');
    }
  }

  /// 获取当前用户信息
  /// token: JWT认证token
  static Future<Map> getCurrentUser(String token) async {
    try {
      final headers = await _getHeaders(needAuth: true);
      final response = await http.get(
        Uri.parse('$baseUrl/auth/me'),
        headers: headers,
      );

      return _handleResponse(response);
    } catch (e) {
      throw Exception('获取用户信息失败: $e');
    }
  }

  /// 退出登录
  static Future<void> logout() async {
    try {
      await _clearToken();
    } catch (e) {
      throw Exception('退出登录失败: $e');
    }
  }

  // ==================== 志愿表相关接口 ====================

  /// 获取志愿表列表
  /// token: JWT认证token
  static Future<List> getPlanList(String token) async {
    try {
      final headers = await _getHeaders(needAuth: true);
      final response = await http.get(
        Uri.parse('$baseUrl/plan/list'),
        headers: headers,
      );

      final result = _handleResponse(response);

      if (result['code'] == 0 && result['data'] != null) {
        final plans = result['data']['plans'] as List<dynamic>;
        return plans;
      }

      return [];
    } catch (e) {
      throw Exception('获取志愿表失败: $e');
    }
  }

  /// 添加到志愿表
  /// token: JWT认证token
  /// planItem: 志愿项目数据
  static Future<bool> addToPlan(String token, Map planItem) async {
    try {
      final headers = await _getHeaders(needAuth: true);
      final response = await http.post(
        Uri.parse('$baseUrl/plan/add'),
        headers: headers,
        body: jsonEncode({
          'university_id': planItem['university_id'] ?? planItem['id'],
          'major_id': planItem['major_id'] ?? planItem['id'],
          'university_name': planItem['university_name'],
          'major_name': planItem['major_name'],
          'probability': planItem['probability'] ?? 0,
          'roi_score': planItem['roi_score'] ?? 70,
          'tag': planItem['tag'] ?? '推荐',
        }),
      );

      final result = _handleResponse(response);
      return result['code'] == 0;
    } catch (e) {
      throw Exception('添加到志愿表失败: $e');
    }
  }

  /// 从志愿表删除
  /// token: JWT认证token
  /// majorId: 专业ID
  static Future<bool> removeFromPlan(String token, int majorId) async {
    try {
      final headers = await _getHeaders(needAuth: true);
      final response = await http.delete(
        Uri.parse('$baseUrl/plan/remove?major_id=$majorId'),
        headers: headers,
      );

      final result = _handleResponse(response);
      return result['code'] == 0;
    } catch (e) {
      throw Exception('删除志愿失败: $e');
    }
  }

  /// 评估志愿表
  /// token: JWT认证token
  /// 返回评估结果：评分、风险预警、改进建议
  static Future<Map> evaluatePlan(String token) async {
    try {
      final headers = await _getHeaders(needAuth: true);
      final response = await http.get(
        Uri.parse('$baseUrl/plan/evaluate'),
        headers: headers,
      );

      final result = _handleResponse(response);

      if (result['code'] == 0 && result['data'] != null) {
        return result['data'];
      }

      throw Exception('评估失败');
    } catch (e) {
      throw Exception('评估志愿表失败: $e');
    }
  }
}