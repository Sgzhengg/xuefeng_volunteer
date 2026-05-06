import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:isar/isar.dart';
import '../../core/models/user_profile.dart';
import '../../shared/theme/app_theme.dart';

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
      // TODO: 从Isar数据库加载用户档案
      // final isar = ref.read(isarProvider);
      // final profiles = await isar.userProfiles.where().findAll();
      // if (profiles.isNotEmpty) {
      //   final profile = profiles.first;
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
      // TODO: 保存到Isar数据库
      // final isar = ref.read(isarProvider);
      // final profile = UserProfile()
      //   ..name = _nameController.text
      //   ..score = int.parse(_scoreController.text)
      //   ..province = _provinceController.text
      //   ..subjectType = _subjectType
      //   ..familyBackground = _familyBackground
      //   ..interests = _interestsController.text.split(',')
      //   ..createdAt = DateTime.now();
      //
      // await isar.writeTxn(() async {
      //   await isar.userProfiles.put(profile);
      // });

      _showSuccess('档案保存成功');
    } catch (e) {
      _showError('保存失败：$e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.green),
    );
  }

  void _showInfo(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.blue),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(AppTheme.spacingMd),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 用户信息卡片
                  _buildUserInfoCard(),

                  const SizedBox(height: AppTheme.spacingMd),

                  // 功能菜单
                  _buildMenuSection(),

                  const SizedBox(height: AppTheme.spacingMd),

                  // 个人档案表单
                  _buildProfileForm(),

                  const SizedBox(height: AppTheme.spacingLg),
                ],
              ),
            ),
    );
  }

  /// 构建用户信息卡片
  Widget _buildUserInfoCard() {
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
            child: const Icon(
              Icons.person,
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
                  _nameController.text.isEmpty ? '未设置姓名' : _nameController.text,
                  style: AppTheme.titleMedium.copyWith(color: AppTheme.white),
                ),
                const SizedBox(height: AppTheme.spacingXs),
                Text(
                  _scoreController.text.isEmpty
                      ? '请完善个人信息'
                      : '${_provinceController.text} · ${_scoreController.text}分',
                  style: AppTheme.bodyMedium.copyWith(color: AppTheme.white.withOpacity(0.9)),
                ),
              ],
            ),
          ),

          // 编辑按钮
          IconButton(
            onPressed: () {
              // 滚动到表单区域
            },
            icon: const Icon(Icons.edit, color: AppTheme.white),
          ),
        ],
      ),
    );
  }

  /// 构建功能菜单
  Widget _buildMenuSection() {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border.all(color: AppTheme.surfaceContainerHighest),
      ),
      child: Column(
        children: [
          _buildMenuItem(
            icon: Icons.school,
            title: '我的志愿方案',
            subtitle: '查看已保存的志愿填报方案',
            onTap: () {
              _showInfo('志愿方案功能开发中...');
            },
          ),
          const Divider(height: 1),
          _buildMenuItem(
            icon: Icons.favorite,
            title: '收藏的院校',
            subtitle: '查看收藏的院校和专业',
            onTap: () {
              _showInfo('收藏功能开发中...');
            },
          ),
          const Divider(height: 1),
          _buildMenuItem(
            icon: Icons.settings,
            title: '设置',
            subtitle: '应用设置和偏好',
            onTap: () {
              _showInfo('设置功能开发中...');
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
                    foregroundColor: AppTheme.white,
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
}
