import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/volunteer_scheme.dart';
import '../../shared/theme/app_theme.dart';
import '../../shared/widgets/data_source_indicator.dart';

class SimulatorPage extends ConsumerStatefulWidget {
  const SimulatorPage({super.key});

  @override
  ConsumerState<SimulatorPage> createState() => _SimulatorPageState();
}

class _SimulatorPageState extends ConsumerState<SimulatorPage> {
  final _formKey = GlobalKey<FormState>();
  final _provinceController = TextEditingController();
  final _scoreController = TextEditingController();
  final _rankController = TextEditingController();
  final _majorsController = TextEditingController();

  String _subjectType = '理科';
  bool _isLoading = false;
  VolunteerScheme? _scheme;

  @override
  void dispose() {
    _provinceController.dispose();
    _scoreController.dispose();
    _rankController.dispose();
    _majorsController.dispose();
    super.dispose();
  }

  Future<void> _generateScheme() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      // 解析目标专业（多个专业用逗号分隔）
      final majorsText = _majorsController.text.trim();
      List<String> targetMajors = [];
      if (majorsText.isNotEmpty) {
        targetMajors = majorsText.split(RegExp(r'[，,]')).map((s) => s.trim()).where((s) => s.isNotEmpty).toList();
      }

      // 创建示例志愿方案（实际应该调用后端API）
      final scheme = VolunteerScheme.create(
        schemeId: DateTime.now().millisecondsSinceEpoch.toString(),
        userId: 'current_user',
        name: '${_provinceController.text}-${_scoreController.text}分-${_subjectType}',
        choices: _generateMockChoices(),
        analysis: '这是一个基于您分数的模拟推荐方案。',
        createdAt: DateTime.now().millisecondsSinceEpoch,
      );

      setState(() {
        _scheme = scheme;
        _isLoading = false;
      });

      // 显示成功提示
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('[OK] 推荐方案生成成功！'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('[ERROR] 生成失败：$e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  // 生成模拟推荐数据
  List<SchoolChoice> _generateMockChoices() {
    final score = int.tryParse(_scoreController.text) ?? 0;
    final subject = _subjectType;

    // 模拟数据：根据分数生成冲刺、稳妥、保底学校
    return [
      SchoolChoice.create(
        universityName: '清华大学',
        majorName: '计算机科学与技术',
        type: '冲',
        probability: 0.3,
        score: score + 20,
        ranking: 1000,
      ),
      SchoolChoice.create(
        universityName: '北京大学',
        majorName: '人工智能',
        type: '冲',
        probability: 0.25,
        score: score + 25,
        ranking: 800,
      ),
      SchoolChoice.create(
        universityName: '复旦大学',
        majorName: '数据科学',
        type: '稳',
        probability: 0.6,
        score: score,
        ranking: 3000,
      ),
      SchoolChoice.create(
        universityName: '上海交通大学',
        majorName: '软件工程',
        type: '稳',
        probability: 0.65,
        score: score - 5,
        ranking: 3500,
      ),
      SchoolChoice.create(
        universityName: '浙江大学',
        majorName: '电子信息工程',
        type: '保',
        probability: 0.85,
        score: score - 20,
        ranking: 5000,
      ),
      SchoolChoice.create(
        universityName: '南京大学',
        majorName: '计算机科学',
        type: '保',
        probability: 0.9,
        score: score - 25,
        ranking: 5500,
      ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('志愿模拟器'),
        actions: const [
          Padding(
            padding: EdgeInsets.symmetric(horizontal: AppTheme.spacingMd),
            child: DataSourceIndicator(
              dataSourceType: DataSourceType.realData,
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppTheme.spacingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 数据源状态卡片
            const DataSourceStatusCard(
              dataSourceType: DataSourceType.realData,
              lastUpdateTime: '2026-04-22',
              dataCoverage: '覆盖全国2800+所院校',
            ),
            const SizedBox(height: AppTheme.spacingMd),

            // 输入表单
            _buildInputForm(),
            const SizedBox(height: AppTheme.spacingMd),

            // 生成按钮
            _buildGenerateButton(),
            const SizedBox(height: AppTheme.spacingMd),

            // 建议卡片
            _buildSuggestionCard(),
            const SizedBox(height: AppTheme.spacingMd),

            // 志愿方案结果
            if (_scheme != null) ...[
              _buildSchemeResult(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInputForm() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingLg),
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        boxShadow: AppTheme.shadowLight,
        border: Border.all(
          color: AppTheme.surfaceContainerHighest,
          width: 1,
        ),
      ),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 4,
                  height: 24,
                  decoration: const BoxDecoration(
                    color: AppTheme.primaryBlue,
                    borderRadius: BorderRadius.only(
                      topRight: Radius.circular(AppTheme.radiusSm),
                      bottomRight: Radius.circular(AppTheme.radiusSm),
                    ),
                  ),
                ),
                const SizedBox(width: AppTheme.spacingSm),
                Text(
                  '填写基本信息',
                  style: AppTheme.titleSmall,
                ),
              ],
            ),
            const SizedBox(height: AppTheme.spacingMd),

            // 省份和分数
            Row(
              children: [
                Expanded(
                  child: _buildFormField(
                    label: '所在省份',
                    child: DropdownButtonFormField<String>(
                      value: _provinceController.text.isEmpty
                          ? null
                          : _provinceController.text,
                      decoration: const InputDecoration(
                        hintText: '请选择',
                      ),
                      items: ['江苏省', '浙江省', '北京市', '上海市']
                          .map((province) {
                        return DropdownMenuItem(
                          value: province,
                          child: Text(province),
                        );
                      }).toList(),
                      onChanged: (value) {
                        _provinceController.text = value ?? '';
                      },
                    ),
                  ),
                ),
                const SizedBox(width: AppTheme.spacingMd),
                Expanded(
                  child: _buildFormField(
                    label: '高考分值',
                    child: TextFormField(
                      controller: _scoreController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        hintText: '如：600',
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return '请输入分数';
                        }
                        return null;
                      },
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: AppTheme.spacingMd),

            // 位次和目标专业
            Row(
              children: [
                Expanded(
                  child: _buildFormField(
                    label: '全省位次',
                    child: TextFormField(
                      controller: _rankController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        hintText: '可选',
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: AppTheme.spacingMd),
                Expanded(
                  child: _buildFormField(
                    label: '目标专业',
                    child: TextFormField(
                      controller: _majorsController,
                      decoration: const InputDecoration(
                        hintText: '如：计算机科学',
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return '请输入目标专业';
                        }
                        return null;
                      },
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: AppTheme.spacingMd),

            // 科类
            _buildFormField(
              label: '报考类别',
              child: Row(
                children: [
                  Expanded(
                    child: _buildRadioOption('综合类', '综合'),
                  ),
                  const SizedBox(width: AppTheme.spacingMd),
                  Expanded(
                    child: _buildRadioOption('理科', '理科'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 生成按钮（在输入表单和建议卡片之间）
  Widget _buildGenerateButton() {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: _isLoading ? null : _generateScheme,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppTheme.primaryBlue,
          foregroundColor: AppTheme.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppTheme.radiusLg),
          ),
          elevation: 2,
        ),
        child: _isLoading
            ? const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  color: AppTheme.white,
                  strokeWidth: 2,
                ),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.auto_awesome_rounded, size: 20),
                  SizedBox(width: AppTheme.spacingXs),
                  Text(
                    '生成志愿方案',
                    style: AppTheme.titleSmall,
                  ),
                ],
              ),
      ),
    );
  }

  Widget _buildFormField({required String label, required Widget child}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: AppTheme.labelSmall,
        ),
        const SizedBox(height: AppTheme.spacingXs),
        child,
      ],
    );
  }

  Widget _buildRadioOption(String label, String value) {
    final isSelected = _subjectType == value;
    return GestureDetector(
      onTap: () {
        setState(() {
          _subjectType = value;
        });
      },
      child: Container(
        height: 48,
        decoration: BoxDecoration(
          color: isSelected
              ? AppTheme.infoBackground
              : AppTheme.surfaceContainerLowest,
          borderRadius: BorderRadius.circular(AppTheme.radiusLg),
          border: Border.all(
            color: isSelected
                ? AppTheme.primaryBlue
                : AppTheme.surfaceContainerHighest,
            width: 2,
          ),
        ),
        child: Center(
          child: Text(
            label,
            style: AppTheme.bodyMedium.copyWith(
              color: isSelected
                  ? AppTheme.primaryBlue
                  : AppTheme.mediumGray,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSuggestionCard() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      decoration: BoxDecoration(
        color: AppTheme.warningBackground,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border.all(
          color: AppTheme.warningBorder,
          width: 1,
        ),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.lightbulb_rounded,
            color: AppTheme.orange,
          ),
          const SizedBox(width: AppTheme.spacingSm),
          Expanded(
            child: Text.rich(
              TextSpan(
                children: [
                  const TextSpan(
                    text: '根据你的位次，建议按照 ',
                    style: AppTheme.bodySmall,
                  ),
                  TextSpan(
                    text: '20% 冲刺',
                    style: AppTheme.bodySmall.copyWith(
                      fontWeight: FontWeight.bold,
                      color: AppTheme.darkGray,
                    ),
                  ),
                  const TextSpan(
                    text: '、',
                    style: AppTheme.bodySmall,
                  ),
                  TextSpan(
                    text: '40% 稳妥',
                    style: AppTheme.bodySmall.copyWith(
                      fontWeight: FontWeight.bold,
                      color: AppTheme.darkGray,
                    ),
                  ),
                  const TextSpan(
                    text: '、',
                    style: AppTheme.bodySmall,
                  ),
                  TextSpan(
                    text: '30% 保底',
                    style: AppTheme.bodySmall.copyWith(
                      fontWeight: FontWeight.bold,
                      color: AppTheme.darkGray,
                    ),
                  ),
                  const TextSpan(
                    text: ' 的比例填报。',
                    style: AppTheme.bodySmall,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSchemeResult() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 冲刺院校
        if (_scheme?.chong.isNotEmpty ?? false)
          _buildSchoolSection(
            icon: Icons.rocket_launch_rounded,
            title: '冲刺',
            count: _scheme!.chong.length,
            description: '高收益，低概率',
            color: AppTheme.red,
            choices: _scheme!.chong,
          ),

        const SizedBox(height: AppTheme.spacingMd),

        // 稳妥院校
        if (_scheme?.wen.isNotEmpty ?? false)
          _buildSchoolSection(
            icon: Icons.verified_user_rounded,
            title: '稳妥',
            count: _scheme!.wen.length,
            description: '稳妥选择',
            color: AppTheme.green,
            choices: _scheme!.wen,
          ),

        const SizedBox(height: AppTheme.spacingMd),

        // 保底院校
        if (_scheme?.bao.isNotEmpty ?? false)
          _buildSchoolSection(
            icon: Icons.anchor_rounded,
            title: '保底',
            count: _scheme!.bao.length,
            description: '基本没问题',
            color: AppTheme.primaryBlue,
            choices: _scheme!.bao,
          ),
      ],
    );
  }

  Widget _buildSchoolSection({
    required IconData icon,
    required String title,
    required int count,
    required String description,
    required Color color,
    required List<SchoolChoice> choices,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 20),
                const SizedBox(width: AppTheme.spacingXs),
                Text(
                  '$title ($count)',
                  style: AppTheme.titleSmall.copyWith(
                    color: color,
                  ),
                ),
              ],
            ),
            Text(
              description,
              style: AppTheme.bodySmall.copyWith(
                color: AppTheme.mediumGray,
              ),
            ),
          ],
        ),
        const SizedBox(height: AppTheme.spacingSm),
        ...choices.map((choice) {
          return _buildSchoolCard(choice, color);
        }).toList(),
      ],
    );
  }

  Widget _buildSchoolCard(SchoolChoice choice, Color color) {
    return Container(
      margin: const EdgeInsets.only(bottom: AppTheme.spacingSm),
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border(
          left: BorderSide(
            color: color,
            width: 4,
          ),
        ),
        boxShadow: AppTheme.shadowLight,
      ),
      child: Row(
        children: [
          // 院校图标
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: AppTheme.lightGray,
              borderRadius: BorderRadius.circular(AppTheme.radiusSm),
            ),
            child: const Icon(
              Icons.school_rounded,
              color: AppTheme.mediumGray,
            ),
          ),
          const SizedBox(width: AppTheme.spacingMd),

          // 院校信息
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  choice.universityName,
                  style: AppTheme.titleSmall,
                ),
                const SizedBox(height: AppTheme.spacingXs),
                Wrap(
                  spacing: AppTheme.spacingXs,
                  children: [
                    _buildTag(choice.type, color),
                    _buildTag('一本', AppTheme.mediumGray),
                  ],
                ),
                const SizedBox(height: AppTheme.spacingXs),
                Text(
                  choice.majorName,
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.mediumGray,
                  ),
                ),
              ],
            ),
          ),

          // 录取概率
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${(choice.probability * 100).toStringAsFixed(1)}%',
                style: AppTheme.headlineMedium.copyWith(
                  color: color,
                  fontSize: 20,
                ),
              ),
              const SizedBox(height: AppTheme.spacingXs),
              Text(
                '录取概率',
                style: AppTheme.labelSmall.copyWith(
                  color: AppTheme.mediumGray,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTag(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacingXs,
        vertical: 2,
      ),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Text(
        label,
        style: AppTheme.labelSmall.copyWith(
          color: color,
          fontSize: 10,
        ),
      ),
    );
  }
}
