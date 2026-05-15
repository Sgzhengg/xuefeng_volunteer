import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:uuid/uuid.dart';

/// 设备信息服务
class DeviceInfoService {
  static final DeviceInfoService _instance = DeviceInfoService._internal();
  factory DeviceInfoService() => _instance;
  DeviceInfoService._internal();

  final DeviceInfoPlugin _deviceInfo = DeviceInfoPlugin();
  final Uuid _uuid = const Uuid();

  /// 获取设备唯一标识符
  Future<String> getDeviceId() async {
    try {
      if (kIsWeb) {
        // Web平台：使用本地存储的UUID
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
    // 这里需要使用shared_preferences来存储和读取
    // 暂时生成一个固定的ID
    return 'web_${_uuid.v4()}';
  }

  /// 生成备用设备ID
  String _generateFallbackId() {
    return 'device_${_uuid.v4()}';
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