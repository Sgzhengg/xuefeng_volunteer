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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('用户档案'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(AppTheme.spacingMd),
              child: Form(
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
              ),
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
