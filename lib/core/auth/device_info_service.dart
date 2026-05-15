import 'dart:io';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// 设备信息服务
class DeviceInfoService {
  static final DeviceInfoService _instance = DeviceInfoService._internal();
  factory DeviceInfoService() => _instance;
  DeviceInfoService._internal();

  final DeviceInfoPlugin _deviceInfo = DeviceInfoPlugin();
  final Random _random = Random();

  /// 生成UUID v4格式的字符串
  String _generateUuid() {
    // 生成UUID v4格式的字符串
    final bytes = List<int>.generate(16, (i) => _random.nextInt(256));
    bytes[6] = (bytes[6] & 0x0F) | 0x40; // 版本号
    bytes[8] = (bytes[8] & 0x3F) | 0x80; // 变体

    final hex = bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
    return '${hex.substring(0, 8)}-${hex.substring(8, 12)}-${hex.substring(12, 16)}-${hex.substring(16, 20)}-${hex.substring(20, 32)}';
  }

  /// 获取设备唯一标识符
  Future<String> getDeviceId() async {
    try {
      if (kIsWeb) {
        // Web平台：从localStorage读取或生成新的UUID
        return await _getWebDeviceId();
      } else if (Platform.isAndroid) {
        // Android：使用Android ID
        final androidInfo = await _deviceInfo.androidInfo;
        return androidInfo.id; // Android ID
      } else if (Platform.isIOS) {
        // iOS：使用identifierForVendor
        final iosInfo = await _deviceInfo.iosInfo;
        return iosInfo.identifierForVendor ?? _generateFallbackId();
      } else {
        // 其他平台：生成备用ID
        return _generateFallbackId();
      }
    } catch (e) {
      debugPrint('获取设备ID失败: $e');
      return _generateFallbackId();
    }
  }

  /// 获取Web设备ID（从localStorage读取或生成新的）
  Future<String> _getWebDeviceId() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      String? deviceId = prefs.getString('web_device_id');

      if (deviceId == null || deviceId.isEmpty) {
        deviceId = 'web_${_generateUuid()}';
        await prefs.setString('web_device_id', deviceId);
      }

      return deviceId;
    } catch (e) {
      debugPrint('获取Web设备ID失败: $e');
      return 'web_${_generateUuid()}';
    }
  }

  /// 生成备用设备ID
  String _generateFallbackId() {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final random = _random.nextInt(100000);
    return 'device_${timestamp}_$random';
  }

  /// 获取设备信息
  Future<Map<String, dynamic>> getDeviceInfo() async {
    try {
      if (kIsWeb) {
        return {
          'platform': 'web',
          'user_agent': 'Web Browser',
        };
      } else if (Platform.isAndroid) {
        final androidInfo = await _deviceInfo.androidInfo;
        return {
          'platform': 'android',
          'model': androidInfo.model,
          'brand': androidInfo.brand,
          'android_version': androidInfo.version.release,
          'sdk_int': androidInfo.version.sdkInt,
        };
      } else if (Platform.isIOS) {
        final iosInfo = await _deviceInfo.iosInfo;
        return {
          'platform': 'ios',
          'model': iosInfo.model,
          'system_version': iosInfo.systemVersion,
          'device_name': iosInfo.name,
        };
      } else {
        return {
          'platform': Platform.operatingSystem,
        };
      }
    } catch (e) {
      debugPrint('获取设备信息失败: $e');
      return {
        'platform': 'unknown',
        'error': e.toString(),
      };
    }
  }

  /// 获取完整的设备信息用于登录
  Future<Map<String, dynamic>> getLoginDeviceInfo() async {
    final deviceId = await getDeviceId();
    final deviceInfo = await getDeviceInfo();

    return {
      'device_id': deviceId,
      'device_info': deviceInfo,
      'timestamp': DateTime.now().toIso8601String(),
    };
  }
}