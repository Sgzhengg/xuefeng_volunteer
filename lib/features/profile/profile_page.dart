import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/auth_provider.dart';
import '../../shared/theme/app_theme.dart';
import '../settings/settings_page.dart';

class ProfilePage extends ConsumerStatefulWidget {
  const ProfilePage({super.key});

  @override
  ConsumerState<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends ConsumerState<ProfilePage> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _scoreController = TextEditingController();
  final _provinceController = TextEditingController();
  final _rankController = TextEditingController();
  final _interestsController = TextEditingController();

  String _subjectType = '理科';
  String _familyBackground = '普通家庭';
  bool _isLoading = false;

  @override
  void dispose() {
    _nameController.dispose();
    _scoreController.dispose();
    _provinceController.dispose();
    _rankController.dispose();
    _interestsController.dispose();
    super.dispose();
  }

  Future<void> _loadProfile() async {
    setState(() => _isLoading = true);

    try {
      // TODO: 从数据库加载用户档案
      // final profile = await ref.read(profileProvider.notifier).getProfile();
      // if (profile != null) {
      //   _nameController.text = profile.name;
      //   _scoreController.text = profile.score.toString();
      //   // ... 加载其他字段
      // }
    } catch (e) {
      _showError('加载失败：$e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isLoading = true);

    try {
      // TODO: 保存到数据库
      // await ref.read(profileProvider.notifier).saveProfile(
      //   name: _nameController.text,
      //   score: int.parse(_scoreController.text),
      //   province: _provinceController.text,
      //   subjectType: _subjectType,
      //   familyBackground: _familyBackground,
      //   interests: _interestsController.text.split(','),
      // );

      _showSuccess('档案保存成功');
    } catch (e) {
      _showError('保存失败：$e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _logout() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('退出登录'),
        content: const Text('确定要退出登录吗？'),
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
      await ref.read(authProvider.notifier).logout();
      if (mounted) {
        _showSuccess('已退出登录');
      }
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppTheme.red),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppTheme.green),
    );
  }

  void _showInfo(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppTheme.primaryBlue),
    );
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('我的'),
        backgroundColor: AppTheme.primaryBlue,
        foregroundColor: Colors.white,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(AppTheme.spacingMd),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 用户信息卡片
                  _buildUserInfoCard(authState),

                  const SizedBox(height: AppTheme.spacingMd),

                  // 功能菜单
                  _buildMenuSection(authState),

                  const SizedBox(height: AppTheme.spacingMd),

                  // 个人档案表单（仅登录用户显示）
                  if (authState.isLoggedIn) ...[
                    _buildProfileForm(),
                    const SizedBox(height: AppTheme.spacingLg),
                  ],
                ],
              ),
            ),
    );
  }

  /// 构建用户信息卡片
  Widget _buildUserInfoCard(AuthState authState) {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingLg),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppTheme.primaryBlue, Color(0xFF1976D2)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        boxShadow: AppTheme.shadowLight,
      ),
      child: Row(
        children: [
          // 头像
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: AppTheme.white,
              border: Border.all(color: AppTheme.white, width: 2),
            ),
            child: Icon(
              authState.isLoggedIn ? Icons.person : Icons.login_outlined,
              size: 40,
              color: AppTheme.primaryBlue,
            ),
          ),
          const SizedBox(width: AppTheme.spacingMd),

          // 用户信息
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  authState.isLoggedIn
                      ? (authState.phoneNumber ?? '用户')
                      : '未登录',
                  style: AppTheme.titleMedium.copyWith(color: AppTheme.white),
                ),
                const SizedBox(height: AppTheme.spacingXs),
                Text(
                  authState.isLoggedIn ? '已登录' : '点击登录查看完整功能',
                  style: AppTheme.bodyMedium.copyWith(color: AppTheme.white.withOpacity(0.9)),
                ),
              ],
            ),
          ),

          // 登录/退出按钮
          if (!authState.isLoggedIn)
            IconButton(
              onPressed: () => _navigateToLogin(),
              icon: const Icon(Icons.arrow_forward, color: AppTheme.white),
            )
          else
            IconButton(
              onPressed: _logout,
              icon: const Icon(Icons.logout, color: AppTheme.white),
              tooltip: '退出登录',
            ),
        ],
      ),
    );
  }

  /// 构建功能菜单
  Widget _buildMenuSection(AuthState authState) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border.all(color: AppTheme.surfaceContainerHighest),
      ),
      child: Column(
        children: [
          if (authState.isLoggedIn) ...[
            _buildMenuItem(
              icon: Icons.school,
              title: '我的志愿表',
              subtitle: '查看已添加的志愿方案',
              onTap: () {
                Navigator.pushNamed(context, '/plans');
              },
            ),
            const Divider(height: 1),
          ],
          _buildMenuItem(
            icon: Icons.favorite,
            title: '我的收藏',
            subtitle: '查看收藏的院校和专业',
            onTap: () {
              Navigator.pushNamed(context, '/favorites');
            },
          ),
          const Divider(height: 1),
          _buildMenuItem(
            icon: Icons.history,
            title: '历史推荐',
            subtitle: '查看历史推荐记录',
            onTap: () {
              Navigator.pushNamed(context, '/history');
            },
          ),
          const Divider(height: 1),
          _buildMenuItem(
            icon: Icons.settings,
            title: '设置',
            subtitle: '应用设置和偏好',
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const SettingsPage()),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Icon(icon, color: AppTheme.primaryBlue),
      title: Text(title, style: AppTheme.titleSmall),
      subtitle: Text(subtitle, style: AppTheme.bodySmall),
      trailing: const Icon(Icons.chevron_right, color: AppTheme.mediumGray),
      onTap: onTap,
    );
  }

  /// 构建个人档案表单
  Widget _buildProfileForm() {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 基本信息卡片
          _buildSectionCard('基本信息', [
            _buildFormField('姓名', _nameController),
            _buildNumberField('高考分数', _scoreController, required: true),
            _buildFormField('省份', _provinceController, required: true),
            _buildNumberField('全省位次', _rankController),
          ]),

          const SizedBox(height: AppTheme.spacingMd),

          // 科类和背景
          _buildSectionCard('详细信息', [
            _buildDropdownField('科类', _subjectType, ['理科', '文科', '综合'], (value) {
              setState(() => _subjectType = value);
            }),
            _buildDropdownField('家庭背景', _familyBackground, ['普通家庭', '中等家庭', '富裕家庭'], (value) {
              setState(() => _familyBackground = value);
            }),
            _buildFormField('兴趣方向（逗号分隔）', _interestsController),
          ]),

          const SizedBox(height: AppTheme.spacingLg),

          // 操作按钮
          Row(
            children: [
              Expanded(
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _saveProfile,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primaryBlue,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: const Text('保存档案'),
                ),
              ),
              const SizedBox(width: AppTheme.spacingMd),
              Expanded(
                child: OutlinedButton(
                  onPressed: _isLoading ? null : _loadProfile,
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppTheme.primaryBlue,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: const Text('重新加载'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSectionCard(String title, List<Widget> children) {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingLg),
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border.all(color: AppTheme.surfaceContainerHighest),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: AppTheme.titleSmall),
          const SizedBox(height: AppTheme.spacingMd),
          ...children,
        ],
      ),
    );
  }

  Widget _buildFormField(String label, TextEditingController controller, {bool required = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppTheme.spacingMd),
      child: TextFormField(
        controller: controller,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        validator: required ? (value) => value?.isEmpty ?? true ? '请输入$label' : null : null,
      ),
    );
  }

  Widget _buildNumberField(String label, TextEditingController controller, {bool required = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppTheme.spacingMd),
      child: TextFormField(
        controller: controller,
        keyboardType: TextInputType.number,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        validator: required ? (value) => value?.isEmpty ?? true ? '请输入$label' : null : null,
      ),
    );
  }

  Widget _buildDropdownField(String label, String value, List<String> options, ValueChanged<String> onChanged) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppTheme.spacingMd),
      child: DropdownButtonFormField<String>(
        value: value,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        items: options.map((option) {
          return DropdownMenuItem(value: option, child: Text(option));
        }).toList(),
        onChanged: (value) {
          if (value != null) onChanged(value);
        },
      ),
    );
  }

  void _navigateToLogin() {
    Navigator.pushNamed(context, '/login');
  }
}