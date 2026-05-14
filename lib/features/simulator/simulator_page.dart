import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../../core/models/volunteer_scheme.dart';
import '../../../core/constants/provinces.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/history_provider.dart';
import '../../shared/theme/app_theme.dart';
import '../../../config/app_config.dart';

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

  // 🆕 目标院校输入
  final _targetUniversityController = TextEditingController();

  String _subjectType = '理科';

  // 🆕 用户偏好设置
  String _regionPreference = 'balanced';  // 'guangdong_first' | 'outprovince_first' | 'balanced'
  List<String> _preferredCities = [];  // 目标城市列表
  bool _showPreferences = false;  // 是否展开偏好设置

  bool _isLoading = false;
  VolunteerScheme? _scheme;

  @override
  void dispose() {
    _provinceController.dispose();
    _scoreController.dispose();
    _rankController.dispose();
    _majorsController.dispose();
    _targetUniversityController.dispose();
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

      // 🆕 解析位次（必填）
      final rank = int.parse(_rankController.text.trim());

      // 调用后端API生成推荐方案
      final response = await http.post(
        Uri.parse('${AppConfig.apiBaseUrl}/api/v1/recommendation/generate'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'province': _provinceController.text.trim(),
          'score': int.parse(_scoreController.text.trim()),  // 保留分数用于展示
          'subject_type': _subjectType,
          'target_majors': targetMajors.isEmpty ? null : targetMajors,
          'rank': rank,  // 🆕 必填，用于核心推荐逻辑
          'preferences': {
            'region_preference': _regionPreference,
            'preferred_cities': _preferredCities,
            'target_university': _targetUniversityController.text.trim().isEmpty
                ? null
                : _targetUniversityController.text.trim(),
          },  // 🆕 用户偏好
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

        // 🆕 自动保存本次推荐到历史记录
        await _saveHistoryToBackend(rank, scheme);

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
            // 🆕 新算法返回的概率是0-1的小数，不需要转换
            final probability = item.containsKey('probability')
                ? (item['probability'] is int
                    ? (item['probability'] as int) / 100.0  // 兼容旧格式
                    : item['probability'] as double)  // 新格式直接使用
                : 0.3;

            // 🆕 解析ROI标签
            final roiTags = item['roi_tags'] != null
                ? List<String>.from(item['roi_tags'])
                : null;
            final roiHint = item['roi_hint'] as String?;

            // 🆕 使用位次而不是分数
            final userRank = int.tryParse(_rankController.text) ?? 0;
            final minRank = item['min_rank'] ?? userRank;

            choices.add(SchoolChoice.create(
              universityName: item['university_name'] ?? '未知院校',
              majorName: item['major'] ?? '未知专业',
              type: '冲',
              probability: probability,
              score: item.containsKey('score_gap')
                  ? (int.parse(_scoreController.text) + (item['score_gap'] as int))
                  : int.parse(_scoreController.text),
              ranking: item.containsKey('rank_gap')
                  ? (userRank + (item['rank_gap'] as int))
                  : minRank,
              roiTags: roiTags,
              roiHint: roiHint,
            ));
          }
        }

        // 解析稳妥院校
        if (recommendationData.containsKey('稳妥')) {
          final wenList = recommendationData['稳妥'] as List;
          for (var item in wenList) {
            final probability = item.containsKey('probability')
                ? (item['probability'] is int
                    ? (item['probability'] as int) / 100.0
                    : item['probability'] as double)
                : 0.6;

            final roiTags = item['roi_tags'] != null
                ? List<String>.from(item['roi_tags'])
                : null;
            final roiHint = item['roi_hint'] as String?;

            final userRank = int.tryParse(_rankController.text) ?? 0;
            final minRank = item['min_rank'] ?? userRank;

            choices.add(SchoolChoice.create(
              universityName: item['university_name'] ?? '未知院校',
              majorName: item['major'] ?? '未知专业',
              type: '稳',
              probability: probability,
              score: item.containsKey('score_gap')
                  ? (int.parse(_scoreController.text) + (item['score_gap'] as int))
                  : int.parse(_scoreController.text),
              ranking: item.containsKey('rank_gap')
                  ? (userRank + (item['rank_gap'] as int))
                  : minRank,
              roiTags: roiTags,
              roiHint: roiHint,
            ));
          }
        }

        // 解析保底院校
        if (recommendationData.containsKey('保底')) {
          final baoList = recommendationData['保底'] as List;
          for (var item in baoList) {
            final probability = item.containsKey('probability')
                ? (item['probability'] is int
                    ? (item['probability'] as int) / 100.0
                    : item['probability'] as double)
                : 0.8;

            final roiTags = item['roi_tags'] != null
                ? List<String>.from(item['roi_tags'])
                : null;
            final roiHint = item['roi_hint'] as String?;

            final userRank = int.tryParse(_rankController.text) ?? 0;
            final minRank = item['min_rank'] ?? userRank;

            choices.add(SchoolChoice.create(
              universityName: item['university_name'] ?? '未知院校',
              majorName: item['major'] ?? '未知专业',
              type: '保',
              probability: probability,
              score: item.containsKey('score_gap')
                  ? (int.parse(_scoreController.text) + (item['score_gap'] as int))
                  : int.parse(_scoreController.text),
              ranking: item.containsKey('rank_gap')
                  ? (userRank + (item['rank_gap'] as int))
                  : minRank,
              roiTags: roiTags,
              roiHint: roiHint,
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
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppTheme.spacingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 输入表单
            _buildInputForm(),
            const SizedBox(height: AppTheme.spacingMd),

            // 生成按钮和对比按钮
            Row(
              children: [
                Expanded(child: _buildGenerateButton()),
                const SizedBox(width: AppTheme.spacingMd),
                Expanded(child: _buildCompareButton()),
              ],
            ),
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
                    label: '全省位次 *',
                    child: TextFormField(
                      controller: _rankController,
                      keyboardType: TextInputType.number,
                      decoration: InputDecoration(
                        hintText: '必填，如：46000',
                        hintStyle: TextStyle(color: AppTheme.orange),
                        border: OutlineInputBorder(
                          borderSide: BorderSide(color: AppTheme.primaryBlue),
                        ),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return '请输入全省位次';
                        }
                        final rank = int.tryParse(value);
                        if (rank == null || rank <= 0) {
                          return '请输入有效的位次';
                        }
                        return null;
                      },
                    ),
                  ),
                ),
                const SizedBox(width: AppTheme.spacingMd),
                Expanded(
                  child: _buildFormField(
                    label: '目标专业（选填）',
                    child: TextFormField(
                      controller: _majorsController,
                      decoration: const InputDecoration(
                        hintText: '如：计算机科学',
                      ),
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

            // 🆕 用户偏好设置（可选）
            const SizedBox(height: AppTheme.spacingMd),
            _buildPreferencesSection(),
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

  // 🆕 新增：对比按钮
  Widget _buildCompareButton() {
    return SizedBox(
      height: 56,
      child: ElevatedButton(
        onPressed: _isLoading ? null : _showCompareModal,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppTheme.orange,
          foregroundColor: AppTheme.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppTheme.radiusLg),
          ),
          elevation: 2,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.compare_arrows_rounded, size: 20),
            const SizedBox(width: AppTheme.spacingXs),
            Text(
              '留粤VS出省',
              style: AppTheme.titleSmall,
            ),
          ],
        ),
      ),
    );
  }

  // 🆕 新增：显示对比弹窗
  Future<void> _showCompareModal() async {
    // 验证必填字段
    if (_scoreController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('请先输入高考分数'),
          backgroundColor: AppTheme.red,
        ),
      );
      return;
    }

    final score = int.tryParse(_scoreController.text.trim()) ?? 0;
    final rank = int.tryParse(_rankController.text.trim()) ?? (100000 - score * 100);

    // 显示加载中
    setState(() => _isLoading = true);

    try {
      // 调用对比API
      final response = await http.post(
        Uri.parse('${AppConfig.apiBaseUrl}/api/v1/recommend/compare'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'province': _provinceController.text.trim().isEmpty ? '广东' : _provinceController.text.trim(),
          'score': score,
          'rank': rank,
          'subject_type': _subjectType,
          'target_majors': ['计算机科学与技术'],
        }),
      ).timeout(const Duration(seconds: 15));

      setState(() => _isLoading = false);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        if (mounted && data['success'] == true) {
          _showCompareResultModal(data['data']);
        }
      } else {
        throw Exception('API错误: ${response.statusCode}');
      }
    } catch (e) {
      setState(() => _isLoading = false);

      if (mounted) {
        _showCompareResultModal(null); // 显示模拟数据
      }
    }
  }

  // 🆕 新增：显示对比结果弹窗
  void _showCompareResultModal(dynamic data) {
    final guangdongBest = data?['guangdong_best'];
    final outprovinceBest = data?['outprovince_best'];
    final suggestion = data?['suggestion'] ?? '暂无建议';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.85,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          children: [
            // 标题栏
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppTheme.primaryBlue,
                borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.compare_rounded, color: Colors.white),
                  const SizedBox(width: 12),
                  const Text(
                    '留粤VS出省对比',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),

            // 对比内容
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 留粤最优选
                    _buildCompareCard(
                      title: '🏠 留粤最优选',
                      university: guangdongBest?['university'] ?? '深圳大学',
                      level: guangdongBest?['university_level'] ?? '一本',
                      major: guangdongBest?['major'] ?? '计算机科学与技术',
                      probability: guangdongBest?['probability'] ?? 75,
                      city: guangdongBest?['city'] ?? '深圳',
                      color: AppTheme.orange,
                      roiTags: guangdongBest?['roi_tags'] != null
                          ? List<String>.from(guangdongBest['roi_tags'])
                          : [],
                    ),

                    const SizedBox(height: 20),

                    // VS图标
                    const Center(
                      child: Text(
                        'VS',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.mediumGray,
                        ),
                      ),
                    ),

                    const SizedBox(height: 20),

                    // 出省最优选
                    _buildCompareCard(
                      title: '✈️ 出省最优选',
                      university: outprovinceBest?['university'] ?? '华中科技大学',
                      level: outprovinceBest?['university_level'] ?? '985',
                      major: outprovinceBest?['major'] ?? '软件工程',
                      probability: outprovinceBest?['probability'] ?? 45,
                      city: outprovinceBest?['city'] ?? '武汉',
                      color: AppTheme.primaryBlue,
                      roiTags: outprovinceBest?['roi_tags'] != null
                          ? List<String>.from(outprovinceBest['roi_tags'])
                          : [],
                    ),

                    const SizedBox(height: 24),

                    // 学锋老师建议
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: AppTheme.infoBackground.withOpacity(0.3),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: AppTheme.primaryBlue.withOpacity(0.3)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.person, color: AppTheme.primaryBlue),
                              const SizedBox(width: 8),
                              Text(
                                '学锋老师的建议',
                                style: AppTheme.titleSmall.copyWith(
                                  color: AppTheme.primaryBlue,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Text(
                            suggestion,
                            style: AppTheme.bodyMedium,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 🆕 新增：对比卡片组件
  Widget _buildCompareCard({
    required String title,
    required String university,
    required String level,
    required String major,
    required int probability,
    required String city,
    required Color color,
    required List<String> roiTags,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color, width: 2),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.2),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: AppTheme.labelSmall.copyWith(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            university,
            style: AppTheme.titleLarge.copyWith(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '$level | $city',
            style: AppTheme.bodySmall.copyWith(
              color: AppTheme.mediumGray,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            major,
            style: AppTheme.bodyMedium.copyWith(
              color: AppTheme.darkGray,
            ),
          ),
          const SizedBox(height: 12),
          // ROI标签
          if (roiTags.isNotEmpty)
            Wrap(
              spacing: 8,
              children: roiTags.map((tag) => Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  tag,
                  style: AppTheme.bodySmall.copyWith(
                    color: color,
                    fontSize: 11,
                  ),
                ),
              )).toList(),
            ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '录取概率',
                      style: AppTheme.labelSmall.copyWith(
                        color: AppTheme.mediumGray,
                      ),
                    ),
                    Text(
                      '$probability%',
                      style: AppTheme.headlineMedium.copyWith(
                        color: color,
                        fontSize: 24,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
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

  // 🆕 新增：地域偏好Chip组件
  Widget _buildRegionChip(String label, String value, IconData icon) {
    final isSelected = _regionPreference == value;
    return FilterChip(
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: isSelected ? Colors.white : AppTheme.mediumGray),
          const SizedBox(width: 4),
          Text(label),
        ],
      ),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          _regionPreference = value;
        });
      },
      selectedColor: AppTheme.primaryBlue,
      backgroundColor: AppTheme.surfaceContainerLowest,
      labelStyle: AppTheme.bodySmall.copyWith(
        color: isSelected ? Colors.white : AppTheme.darkGray,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        side: BorderSide(
          color: isSelected ? AppTheme.primaryBlue : AppTheme.surfaceContainerHighest,
          width: 1,
        ),
      ),
    );
  }

  // 🆕 用户偏好设置部分
  Widget _buildPreferencesSection() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      decoration: BoxDecoration(
        color: AppTheme.infoBackground.withOpacity(0.3),
        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
        border: Border.all(
          color: AppTheme.infoBorder.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 展开/收起按钮
          GestureDetector(
            onTap: () {
              setState(() {
                _showPreferences = !_showPreferences;
              });
            },
            child: Row(
              children: [
                Icon(
                  Icons.tune_rounded,
                  size: 20,
                  color: AppTheme.primaryBlue,
                ),
                const SizedBox(width: AppTheme.spacingXs),
                Text(
                  '择校偏好（可选，帮助我们推荐更精准）',
                  style: AppTheme.labelSmall.copyWith(
                    color: AppTheme.primaryBlue,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Icon(
                  _showPreferences
                      ? Icons.expand_less
                      : Icons.expand_more,
                  size: 20,
                  color: AppTheme.primaryBlue,
                ),
              ],
            ),
          ),

          // 偏好设置内容
          if (_showPreferences) ...[
            const SizedBox(height: AppTheme.spacingMd),

            // 择校倾向
            _buildFormField(
              label: '你的择校倾向',
              child: Column(
                children: [
                  _buildPreferenceOption(
                    '优先留粤',
                    'guangdong_first',
                    '推荐广东院校为主，本地就业优势',
                    Icons.location_city,
                  ),
                  const SizedBox(height: AppTheme.spacingSm),
                  _buildPreferenceOption(
                    '优先出省',
                    'outprovince_first',
                    '推荐层次更高的省外院校，提升学校排名',
                    Icons.flight_takeoff,
                  ),
                  const SizedBox(height: AppTheme.spacingSm),
                  _buildPreferenceOption(
                    '不限制',
                    'balanced',
                    '自动平衡录取概率和院校质量',
                    Icons.balance,
                  ),
                ],
              ),
            ),

            const SizedBox(height: AppTheme.spacingMd),

            // 目标城市选择
            _buildFormField(
              label: '如果有特别想去的城市（选填）',
              child: Wrap(
                spacing: AppTheme.spacingXs,
                runSpacing: AppTheme.spacingXs,
                children: [
                  _buildCityChip('上海'),
                  _buildCityChip('杭州'),
                  _buildCityChip('成都'),
                  _buildCityChip('武汉'),
                  _buildCityChip('西安'),
                  _buildCityChip('北京'),
                  _buildCityChip('南京'),
                  _buildCityChip('重庆'),
                  _buildCityChip('长沙'),
                ],
              ),
            ),

            const SizedBox(height: AppTheme.spacingMd),

            // 目标院校输入
            _buildFormField(
              label: '如果有特别想去的院校（选填）',
              child: TextField(
                controller: _targetUniversityController,
                decoration: const InputDecoration(
                  hintText: '例如：清华大学、中山大学',
                  border: OutlineInputBorder(),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  // 偏好选项单选按钮
  Widget _buildPreferenceOption(
    String title,
    String value,
    String description,
    IconData icon,
  ) {
    final isSelected = _regionPreference == value;
    return GestureDetector(
      onTap: () {
        setState(() {
          _regionPreference = value;
        });
      },
      child: Container(
        padding: const EdgeInsets.all(AppTheme.spacingSm),
        decoration: BoxDecoration(
          color: isSelected
              ? AppTheme.primaryBlue.withOpacity(0.1)
              : AppTheme.surfaceContainerLowest,
          borderRadius: BorderRadius.circular(AppTheme.radiusSm),
          border: Border.all(
            color: isSelected
                ? AppTheme.primaryBlue
                : AppTheme.surfaceContainerHighest,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              size: 20,
              color: isSelected
                  ? AppTheme.primaryBlue
                  : AppTheme.mediumGray,
            ),
            const SizedBox(width: AppTheme.spacingSm),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: AppTheme.bodyMedium.copyWith(
                      color: isSelected
                          ? AppTheme.primaryBlue
                          : AppTheme.darkGray,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    description,
                    style: AppTheme.bodySmall.copyWith(
                      color: AppTheme.mediumGray,
                    ),
                  ),
                ],
              ),
            ),
            if (isSelected)
              Icon(
                Icons.check_circle,
                color: AppTheme.primaryBlue,
                size: 24,
              ),
          ],
        ),
      ),
    );
  }

  // 城市选择Chip
  Widget _buildCityChip(String cityName) {
    final isSelected = _preferredCities.contains(cityName);
    return FilterChip(
      label: Text(cityName),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          if (selected) {
            _preferredCities.add(cityName);
          } else {
            _preferredCities.remove(cityName);
          }
        });
      },
      selectedColor: AppTheme.primaryBlue.withOpacity(0.2),
      backgroundColor: AppTheme.surfaceContainerLowest,
      labelStyle: AppTheme.bodySmall.copyWith(
        color: isSelected ? AppTheme.primaryBlue : AppTheme.darkGray,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
        side: BorderSide(
          color: isSelected ? AppTheme.primaryBlue : AppTheme.surfaceContainerHighest,
          width: 1,
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
    // 🆕 解析额外的ROI信息（从后端API返回）
    final roiTags = choice.roiTags ?? [];
    final roiHint = choice.roiHint;

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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 原有内容
          Row(
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
                        // 🆕 ROI标签
                        ...roiTags.map((tag) => _buildROITag(tag)),
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

          // 🆕 ROI提示文案
          if (roiHint != null && roiHint.isNotEmpty) ...[
            const SizedBox(height: AppTheme.spacingSm),
            Container(
              padding: const EdgeInsets.all(AppTheme.spacingXs),
              decoration: BoxDecoration(
                color: AppTheme.infoBackground.withOpacity(0.5),
                borderRadius: BorderRadius.circular(AppTheme.radiusSm),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.info_outline,
                    size: 14,
                    color: AppTheme.primaryBlue,
                  ),
                  const SizedBox(width: AppTheme.spacingXs),
                  Expanded(
                    child: Text(
                      roiHint,
                      style: AppTheme.bodySmall.copyWith(
                        color: AppTheme.darkGray,
                        fontSize: 11,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  // 🆕 新增：ROI标签组件
  Widget _buildROITag(String tag) {
    Color tagColor;
    Color backgroundColor;

    switch (tag) {
      case "💰高回报":
        tagColor = AppTheme.green;
        backgroundColor = AppTheme.green.withOpacity(0.1);
        break;
      case "⚠️低回报":
        tagColor = AppTheme.red;
        backgroundColor = AppTheme.red.withOpacity(0.1);
        break;
      case "🏛️考公优势":
        tagColor = AppTheme.primaryBlue;
        backgroundColor = AppTheme.primaryBlue.withOpacity(0.1);
        break;
      case "🔥广东热门":
        tagColor = AppTheme.orange;
        backgroundColor = AppTheme.orange.withOpacity(0.1);
        break;
      case "🚫红牌专业":
        tagColor = AppTheme.red;
        backgroundColor = AppTheme.red.withOpacity(0.1);
        break;
      default:
        tagColor = AppTheme.mediumGray;
        backgroundColor = AppTheme.lightGray;
    }

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacingXs,
        vertical: 2,
      ),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
        border: Border.all(
          color: tagColor.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Text(
        tag,
        style: AppTheme.labelSmall.copyWith(
          color: tagColor,
          fontSize: 10,
        ),
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

  /// 🆕 保存推荐历史到后端
  Future<void> _saveHistoryToBackend(int rank, VolunteerScheme scheme) async {
    try {
      final authState = ref.read(authProvider);
      if (!authState.isLoggedIn || authState.token == null) {
        print('用户未登录，跳过保存历史记录');
        return;
      }

      // 解析科目列表
      List<String> subjects = [];
      if (_subjectType == '理科') {
        subjects = ['物理', '化学', '生物'];
      } else if (_subjectType == '文科') {
        subjects = ['政治', '历史', '地理'];
      } else {
        subjects = ['物理', '化学']; // 综合科默认
      }

      // 确定偏好类型
      String preference = 'balanced';
      if (_regionPreference == 'guangdong_first') {
        preference = 'conservative';
      } else if (_regionPreference == 'outprovince_first') {
        preference = 'aggressive';
      }

      // 准备推荐结果摘要
      List<Map<String, dynamic>> resultsSummary = [];
      for (var choice in scheme.choices) {
        resultsSummary.add({
          'university_name': choice.universityName,
          'major_name': choice.majorName,
          'type': choice.type,
          'probability': choice.probability,
          'score': choice.score,
          'ranking': choice.ranking,
        });
      }

      // 调用API保存历史记录
      await ref.read(historyProvider.notifier).saveHistory(
        authState.token!,
        rank,
        _provinceController.text.trim(),
        subjects,
        preference,
        resultsSummary,
      );

      print('历史记录保存成功');
    } catch (e) {
      print('保存历史记录失败: $e');
      // 静默失败，不影响推荐流程
    }
  }
}
