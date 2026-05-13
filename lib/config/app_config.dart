/// 应用配置
class AppConfig {
  /// 后端API基础URL
  // 开发环境: 'http://localhost:8000'
  // 生产环境: 通过 Caddy 反向代理，使用相对路径
  static const String apiBaseUrl = '';  // 空字符串表示使用相对路径

  /// 应用名称
  static const String appName = '学锋志愿教练';

  /// 应用版本
  static const String appVersion = '1.0.0';
}
