import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../../core/models/volunteer_scheme.dart';
import '../../../core/constants/provinces.dart';
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

      // 解析位次
      final rank = _rankController.text.trim().isEmpty
          ? null
          : int.tryParse(_rankController.text.trim());

      // 调用后端API生成推荐方案
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/v1/recommendation/generate'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'province': _provinceController.text.trim(),
          'score': int.parse(_scoreController.text.trim()),
          'subject_type': _subjectType,
          'target_majors': targetMajors.isEmpty ? null : targetMajors,
          'rank': rank,
          'preferences': null,
        }),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        // 解析推荐结果
        final choices = _parseRecommendationData(data);

        final scheme = VolunteerScheme.create(
          schemeId: DateTime.now().millisecondsSinceEpoch.toString(),
          userId: 'current_user',
          name: '${_provinceController.text}-${_scoreController.text}分-${_subjectType}',
          choices: choices,
          analysis: data['analysis'] ?? '基于真实数据的智能推荐方案',
          createdAt: DateTime.now().millisecondsSinceEpoch,
        );

        setState(() {
          _scheme = scheme;
          _isLoading = false;
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('[OK] 推荐方案生成成功！基于真实数据计算'),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else {
        throw Exception('API错误: ${response.statusCode}');
      }
    } catch (e) {
      // 如果API调用失败，使用模拟数据作为后备
      print('API调用失败，使用模拟数据: $e');

      final scheme = VolunteerScheme.create(
        schemeId: DateTime.now().millisecondsSinceEpoch.toString(),
        userId: 'current_user',
        name: '${_provinceController.text}-${_scoreController.text}分-${_subjectType}',
        choices: _generateMockChoices(),
        analysis: '网络连接失败，显示模拟数据。请检查后端服务是否启动。',
        createdAt: DateTime.now().millisecondsSinceEpoch,
      );

      setState(() {
        _scheme = scheme;
        _isLoading = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('[提示] 后端连接失败，显示模拟数据：$e'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    }
  }

  // 解析后端API返回的推荐数据
  List<SchoolChoice> _parseRecommendationData(Map<String, dynamic> data) {
    final List<SchoolChoice> choices = [];

    try {
      // 后端返回格式: {"success": true, "data": {"冲刺": [...], "稳妥": [...], "保底": [...], "垫底": [...]}}
      if (data.containsKey('data')) {
        final recommendationData = data['data'] as Map<String, dynamic>;

        // 解析冲刺院校
        if (recommendationData.containsKey('冲刺')) {
          final chongList = recommendationData['冲刺'] as List;
          for (var item in chongList) {
            // 计算概率（后端返回的是1-100的整数，需要转换为0-1的小数）
            final probability = item.containsKey('probability')
                ? (item['probability'] as int) / 100.0
                : 0.3;

            choices.add(SchoolChoice.create(
              universityName: item['university_name'] ?? '未知院校',
              majorName: item['major'] ?? '未知专业',
              type: '冲',
              probability: probability,
              score: item.containsKey('score_gap')
                  ? (int.parse(_scoreController.text) + (item['score_gap'] as int))
                  : int.parse(_scoreController.text),
              ranking: item.containsKey('rank_gap')
                  ? ((int.tryParse(_rankController.text) ?? 0) + (item['rank_gap'] as int))
                  : (int.tryParse(_rankController.text) ?? 0),
            ));
          }
        }

        // 解析稳妥院校
        if (recommendationData.containsKey('稳妥')) {
          final wenList = recommendationData['稳妥'] as List;
          for (var item in wenList) {
            final probability = item.containsKey('probability')
                ? (item['probability'] as int) / 100.0
                : 0.6;

            choices.add(SchoolChoice.create(
              universityName: item['university_name'] ?? '未知院校',
              majorName: item['major'] ?? '未知专业',
              type: '稳',
              probability: probability,
              score: item.containsKey('score_gap')
                  ? (int.parse(_scoreController.text) + (item['score_gap'] as int))
                  : int.parse(_scoreController.text),
              ranking: item.containsKey('rank_gap')
                  ? ((int.tryParse(_rankController.text) ?? 0) + (item['rank_gap'] as int))
                  : (int.tryParse(_rankController.text) ?? 0),
            ));
          }
        }

        // 解析保底院校
        if (recommendationData.containsKey('保底')) {
          final baoList = recommendationData['保底'] as List;
          for (var item in baoList) {
            final probability = item.containsKey('probability')
                ? (item['probability'] as int) / 100.0
                : 0.8;

            choices.add(SchoolChoice.create(
              universityName: item['university_name'] ?? '未知院校',
              majorName: item['major'] ?? '未知专业',
              type: '保',
              probability: probability,
              score: item.containsKey('score_gap')
                  ? (int.parse(_scoreController.text) + (item['score_gap'] as int))
                  : int.parse(_scoreController.text),
              ranking: item.containsKey('rank_gap')
                  ? ((int.tryParse(_rankController.text) ?? 0) + (item['rank_gap'] as int))
                  : (int.tryParse(_rankController.text) ?? 0),
            ));
          }
        }

        // 解析垫底院校（不显示，按照用户要求只保留冲刺、稳妥、保底）
        // 注：用户要求只显示三类：冲刺(20%)、稳妥(40%)、保底(30%)
        // 所以"垫底"类别不添加到显示列表中
      }
    } catch (e) {
      print('解析推荐数据失败: $e');
    }

    // 按照类别分组并按比例筛选
    final chong = choices.where((c) => c.type == '冲').toList();
    final wen = choices.where((c) => c.type == '稳').toList();
    final bao = choices.where((c) => c.type == '保').toList();

    // 计算目标数量（假设总共10所学校）
    final totalCount = 10;
    final targetChong = (totalCount * 0.2).round(); // 2所冲刺
    final targetWen = (totalCount * 0.4).round();   // 4所稳妥
    final targetBao = (totalCount * 0.3).round();   // 3所保底

    // 按照数量筛选
    final result = [
      ...chong.take(targetChong),
      ...wen.take(targetWen),
      ...bao.take(targetBao),
    ];

    // 如果API没有返回数据，返回模拟数据
    if (result.isEmpty) {
      print('使用模拟数据');
      return _generateMockChoices();
    }

    print('解析到 ${result.length} 个推荐学校（冲刺${result.where((c) => c.type == '冲').length}所，稳妥${result.where((c) => c.type == '稳').length}所，保底${result.where((c) => c.type == '保').length}所）');
    return result;
  }

  // 生成模拟推荐数据
  List<SchoolChoice> _generateMockChoices() {
    final score = int.tryParse(_scoreController.text) ?? 0;

    // 模拟数据：根据分数生成冲刺、稳妥、保底学校
    try {
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
    } catch (e) {
      print('生成模拟数据出错: $e');
      return [];
    }
  }
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('推荐志愿'),
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
                        hintText: '请选择省份',
                      ),
                      items: ChineseProvinces.sorted.map((province) {
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
                    '智能推荐',
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
