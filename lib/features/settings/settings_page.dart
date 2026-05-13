import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../shared/theme/app_theme.dart';
import 'data_source_page.dart';
import 'privacy_policy_page.dart';
import 'user_agreement_page.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  bool _notificationsEnabled = true;
  bool _dataUpdateAlertsEnabled = true;
  bool _wifiOnlyImagesEnabled = false;
  double _cacheSize = 0.0;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  /// 加载设置
  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _notificationsEnabled = prefs.getBool('notifications_enabled') ?? true;
      _dataUpdateAlertsEnabled = prefs.getBool('data_update_alerts_enabled') ?? true;
      _wifiOnlyImagesEnabled = prefs.getBool('wifi_only_images_enabled') ?? false;
    });
    _calculateCacheSize();
  }

  /// 保存设置
  Future<void> _saveSetting(String key, bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(key, value);
  }

  /// 计算缓存大小（模拟）
  Future<void> _calculateCacheSize() async {
    // TODO: 实际计算缓存大小
    setState(() {
      _cacheSize = 2.5; // 模拟 2.5MB
    });
  }

  /// 清除缓存
  Future<void> _clearCache() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('清除缓存'),
        content: const Text('确定要清除所有缓存吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.red,
            ),
            child: const Text('确定'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        // 清除 SharedPreferences
        final prefs = await SharedPreferences.getInstance();
        await prefs.clear();

        // 重新加载默认设置
        await _loadSettings();

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('✅ 缓存已清除'),
              backgroundColor: AppTheme.green,
            ),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('❌ 清除失败: $e'),
              backgroundColor: AppTheme.red,
            ),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surfaceColor,
      appBar: AppBar(
        title: const Text('设置'),
        backgroundColor: AppTheme.primaryBlue,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        children: [
          // 通知设置组
          _buildSectionHeader('通知设置'),
          _buildSwitchTile(
            icon: Icons.notifications,
            title: '消息通知',
            subtitle: '接收推送通知和重要提醒',
            value: _notificationsEnabled,
            onChanged: (value) {
              setState(() => _notificationsEnabled = value);
              _saveSetting('notifications_enabled', value);
            },
          ),
          _buildSwitchTile(
            icon: Icons.update,
            title: '数据更新提醒',
            subtitle: '接收录取数据更新通知',
            value: _dataUpdateAlertsEnabled,
            onChanged: (value) {
              setState(() => _dataUpdateAlertsEnabled = value);
              _saveSetting('data_update_alerts_enabled', value);
            },
          ),

          // 数据设置组
          _buildSectionHeader('数据设置'),
          _buildSwitchTile(
            icon: Icons.wifi,
            title: '仅WiFi下加载图片',
            subtitle: '节省移动数据流量',
            value: _wifiOnlyImagesEnabled,
            onChanged: (value) {
              setState(() => _wifiOnlyImagesEnabled = value);
              _saveSetting('wifi_only_images_enabled', value);
            },
          ),
          _buildActionTile(
            icon: Icons.cleaning_services,
            title: '清除缓存',
            subtitle: '当前缓存: ${_cacheSize.toStringAsFixed(1)}MB',
            onTap: _clearCache,
          ),

          // 关于组
          _buildSectionHeader('关于'),
          _buildNavigationTile(
            icon: Icons.source,
            title: '数据来源说明',
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const DataSourcePage()),
              );
            },
          ),
          _buildNavigationTile(
            icon: Icons.privacy_tip,
            title: '隐私政策',
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const PrivacyPolicyPage()),
              );
            },
          ),
          _buildNavigationTile(
            icon: Icons.description,
            title: '用户协议',
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const UserAgreementPage()),
              );
            },
          ),

          // 版本信息
          _buildVersionInfo(),
        ],
      ),
    );
  }

  /// 构建分组标题
  Widget _buildSectionHeader(String title) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacingMd,
        vertical: AppTheme.spacingSm,
      ),
      child: Text(
        title,
        style: AppTheme.bodySmall.copyWith(
          color: AppTheme.mediumGray,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  /// 构建开关设置项
  Widget _buildSwitchTile({
    required IconData icon,
    required String title,
    String? subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        border: Border(
          bottom: BorderSide(
            color: AppTheme.surfaceContainerHighest,
            width: 1,
          ),
        ),
      ),
      child: ListTile(
        leading: Icon(icon, color: AppTheme.primaryBlue),
        title: Text(title, style: AppTheme.titleSmall),
        subtitle: subtitle != null ? Text(subtitle, style: AppTheme.bodySmall) : null,
        trailing: Switch(
          value: value,
          onChanged: onChanged,
          activeColor: AppTheme.primaryBlue,
        ),
      ),
    );
  }

  /// 构建操作设置项
  Widget _buildActionTile({
    required IconData icon,
    required String title,
    String? subtitle,
    required VoidCallback onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        border: Border(
          bottom: BorderSide(
            color: AppTheme.surfaceContainerHighest,
            width: 1,
          ),
        ),
      ),
      child: ListTile(
        leading: Icon(icon, color: AppTheme.primaryBlue),
        title: Text(title, style: AppTheme.titleSmall),
        subtitle: subtitle != null ? Text(subtitle, style: AppTheme.bodySmall) : null,
        trailing: const Icon(Icons.chevron_right, color: AppTheme.mediumGray),
        onTap: onTap,
      ),
    );
  }

  /// 构建导航设置项
  Widget _buildNavigationTile({
    required IconData icon,
    required String title,
    required VoidCallback onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        border: Border(
          bottom: BorderSide(
            color: AppTheme.surfaceContainerHighest,
            width: 1,
          ),
        ),
      ),
      child: ListTile(
        leading: Icon(icon, color: AppTheme.primaryBlue),
        title: Text(title, style: AppTheme.titleSmall),
        trailing: const Icon(Icons.chevron_right, color: AppTheme.mediumGray),
        onTap: onTap,
      ),
    );
  }

  /// 构建版本信息
  Widget _buildVersionInfo() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingLg),
      alignment: Alignment.center,
      child: Column(
        children: [
          Text(
            '当前版本 v2.0.0',
            style: AppTheme.bodyMedium.copyWith(
              color: AppTheme.mediumGray,
            ),
          ),
          const SizedBox(height: AppTheme.spacingXs),
          Text(
            '© 2025 学锋志愿教练',
            style: AppTheme.bodySmall.copyWith(
              color: AppTheme.lightGray,
            ),
          ),
        ],
      ),
    );
  }
}