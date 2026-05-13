import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../shared/theme/app_theme.dart';
import '../../config/app_config.dart';

/// 发现页面 - 热词榜和红牌专业避坑清单
class DiscoverPage extends ConsumerStatefulWidget {
  const DiscoverPage({super.key});

  @override
  ConsumerState<DiscoverPage> createState() => _DiscoverPageState();
}

class _DiscoverPageState extends ConsumerState<DiscoverPage> {
  // 热词数据
  List<Map<String, dynamic>> _heatWords = [];
  bool _isLoadingHeatWords = true;

  // 红牌专业数据
  List<Map<String, dynamic>> _redList = [];
  bool _isLoadingRedList = true;

  @override
  void initState() {
    super.initState();
    _loadHeatWords();
    _loadRedList();
  }

  /// 加载热词榜
  Future<void> _loadHeatWords() async {
    try {
      final response = await http.get(
        Uri.parse('${AppConfig.apiBaseUrl}/api/v1/heat/list'),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true) {
          final heatData = data['data'];
          setState(() {
            _heatWords = List<Map<String, dynamic>>.from(
              heatData['heat_words'].map((item) => Map<String, dynamic>.from(item))
            );
            _isLoadingHeatWords = false;
          });
          return;
        }
      }
    } catch (e) {
      print('加载热词失败: $e');
    }

    // 使用模拟数据
    setState(() {
      _heatWords = _getMockHeatWords();
      _isLoadingHeatWords = false;
    });
  }

  /// 加载红牌专业列表
  Future<void> _loadRedList() async {
    try {
      final response = await http.get(
        Uri.parse('${AppConfig.apiBaseUrl}/api/v1/roi/redlist'),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true) {
          final redListData = data['data'];
          setState(() {
            _redList = List<Map<String, dynamic>>.from(
              redListData['red_list'].map((item) => Map<String, dynamic>.from(item))
            );
            _isLoadingRedList = false;
          });
          return;
        }
      }
    } catch (e) {
      print('加载红牌列表失败: $e');
    }

    // 使用模拟数据
    setState(() {
      _redList = _getMockRedList();
      _isLoadingRedList = false;
    });
  }

  /// 模拟热词数据
  List<Map<String, dynamic>> _getMockHeatWords() {
    return [
      {"rank": 1, "word": "高考志愿填报", "heat": 125000, "trend": "up", "change": "+15%"},
      {"rank": 2, "word": "专业选择", "heat": 98000, "trend": "up", "change": "+8%"},
      {"rank": 3, "word": "就业前景", "heat": 87000, "trend": "stable", "change": "0%"},
      {"rank": 4, "word": "广东录取分数线", "heat": 76000, "trend": "up", "change": "+5%"},
      {"rank": 5, "word": "985211院校", "heat": 65000, "trend": "down", "change": "-3%"},
      {"rank": 6, "word": "计算机专业", "heat": 54000, "trend": "up", "change": "+12%"},
      {"rank": 7, "word": "法学专业就业", "heat": 43000, "trend": "down", "change": "-7%"},
      {"rank": 8, "word": "医学专业", "heat": 38000, "trend": "stable", "change": "0%"},
      {"rank": 9, "word": "师范类", "heat": 32000, "trend": "up", "change": "+4%"},
      {"rank": 10, "word": "专升本", "heat": 28000, "trend": "up", "change": "+6%"},
    ];
  }

  /// 模拟红牌专业数据
  List<Map<String, dynamic>> _getMockRedList() {
    return [
      {
        "name": "法学",
        "hint": "连续多年红牌，供过于求",
        "alternative": "建议选择：知识产权、监狱学",
        "tag": "🚫红牌专业"
      },
      {
        "name": "绘画",
        "hint": "艺术类中就业最难",
        "alternative": "建议选择：数字媒体艺术",
        "tag": "🚫红牌专业"
      },
      {
        "name": "应用心理学",
        "hint": "岗位少，需求有限",
        "alternative": "建议选择：教育学、特殊教育",
        "tag": "🚫红牌专业"
      },
      {
        "name": "公共事业管理",
        "hint": "定位模糊，企业不认可",
        "alternative": "建议选择：行政管理、人力资源管理",
        "tag": "🚫红牌专业"
      },
      {
        "name": "音乐表演",
        "hint": "市场饱和，竞争激烈",
        "alternative": "建议选择：音乐教育（可当老师）",
        "tag": "🚫红牌专业"
      },
      {
        "name": "历史学",
        "hint": "纯学术研究，岗位有限",
        "alternative": "建议选择：历史学师范（可当老师）",
        "tag": "🚫红牌专业"
      },
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('发现'),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // 打开设置页面（原"我的"页面内容）
              _showSettingsSheet();
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppTheme.spacingMd),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 热词榜卡片
            _buildHeatWordsCard(),

            const SizedBox(height: AppTheme.spacingMd),

            // 红牌专业避坑清单卡片
            _buildRedListCard(),

            const SizedBox(height: AppTheme.spacingMd),

            // 广东热门专业卡片
            _buildGuangdongHotCard(),
          ],
        ),
      ),
    );
  }

  /// 热词榜卡片
  Widget _buildHeatWordsCard() {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        boxShadow: AppTheme.shadowLight,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题栏
          Container(
            padding: const EdgeInsets.all(AppTheme.spacingMd),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [AppTheme.primaryBlue, AppTheme.primaryBlue.withOpacity(0.8)],
              ),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(AppTheme.radiusLg),
                topRight: Radius.circular(AppTheme.radiusLg),
              ),
            ),
            child: Row(
              children: [
                const Icon(Icons.whatshot, color: Colors.white),
                const SizedBox(width: AppTheme.spacingSm),
                const Text(
                  '今日高考热词榜',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Text(
                  '来源: 微博热搜 | 快手热榜',
                  style: AppTheme.bodySmall.copyWith(
                    color: Colors.white70,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),

          // 热词列表
          if (_isLoadingHeatWords)
            const Padding(
              padding: EdgeInsets.all(40),
              child: Center(child: CircularProgressIndicator()),
            )
          else
            Padding(
              padding: const EdgeInsets.all(AppTheme.spacingMd),
              child: Column(
                children: _heatWords.asMap().entries.map((entry) {
                  final index = entry.key;
                  final item = entry.value;
                  return _buildHeatWordItem(index + 1, item);
                }).toList(),
              ),
            ),
        ],
      ),
    );
  }

  /// 单个热词项
  Widget _buildHeatWordItem(int rank, Map<String, dynamic> item) {
    final trend = item['trend'];
    final change = item['change'];

    Color trendColor;
    IconData trendIcon;
    if (trend == 'up') {
      trendColor = AppTheme.red;
      trendIcon = Icons.arrow_upward;
    } else if (trend == 'down') {
      trendColor = AppTheme.green;
      trendIcon = Icons.arrow_downward;
    } else {
      trendColor = AppTheme.mediumGray;
      trendIcon = Icons.remove;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: AppTheme.spacingSm),
      padding: const EdgeInsets.all(AppTheme.spacingSm),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
        border: Border.all(color: AppTheme.surfaceContainerHighest),
      ),
      child: Row(
        children: [
          // 排名
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              color: rank <= 3 ? AppTheme.orange : AppTheme.lightGray,
              borderRadius: BorderRadius.circular(AppTheme.radiusSm),
            ),
            child: Center(
              child: Text(
                '$rank',
                style: AppTheme.labelSmall.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),

          const SizedBox(width: AppTheme.spacingSm),

          // 热词
          Expanded(
            child: Text(
              item['word'],
              style: AppTheme.bodyMedium,
            ),
          ),

          // 热度值
          Text(
            '${(item['heat'] / 10000).toStringAsFixed(1)}万',
            style: AppTheme.bodySmall.copyWith(
              color: AppTheme.mediumGray,
            ),
          ),

          const SizedBox(width: AppTheme.spacingSm),

          // 趋势
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(trendIcon, size: 14, color: trendColor),
              Text(
                change,
                style: AppTheme.bodySmall.copyWith(color: trendColor),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// 红牌专业避坑清单卡片
  Widget _buildRedListCard() {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        boxShadow: AppTheme.shadowLight,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题栏
          Container(
            padding: const EdgeInsets.all(AppTheme.spacingMd),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [AppTheme.red, AppTheme.red.withOpacity(0.8)],
              ),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(AppTheme.radiusLg),
                topRight: Radius.circular(AppTheme.radiusLg),
              ),
            ),
            child: Row(
              children: [
                const Icon(Icons.warning_rounded, color: Colors.white),
                const SizedBox(width: AppTheme.spacingSm),
                const Text(
                  '广东红牌专业避坑清单',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                GestureDetector(
                  onTap: _generateShareImage,
                  child: Row(
                    children: [
                      Icon(Icons.share, color: Colors.white70, size: 16),
                      const SizedBox(width: 4),
                      Text(
                        '生成分享图片',
                        style: AppTheme.bodySmall.copyWith(
                          color: Colors.white70,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // 红牌列表
          if (_isLoadingRedList)
            const Padding(
              padding: EdgeInsets.all(40),
              child: Center(child: CircularProgressIndicator()),
            )
          else
            Padding(
              padding: const EdgeInsets.all(AppTheme.spacingMd),
              child: Column(
                children: _redList.map((item) => _buildRedListItem(item)).toList(),
              ),
            ),
        ],
      ),
    );
  }

  /// 单个红牌专业项
  Widget _buildRedListItem(Map<String, dynamic> item) {
    return Container(
      margin: const EdgeInsets.only(bottom: AppTheme.spacingSm),
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      decoration: BoxDecoration(
        color: AppTheme.errorBackground.withOpacity(0.3),
        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
        border: Border.all(color: AppTheme.red.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                item['tag'],
                style: AppTheme.labelSmall,
              ),
              const SizedBox(width: AppTheme.spacingSm),
              Expanded(
                child: Text(
                  item['name'],
                  style: AppTheme.titleSmall.copyWith(
                    color: AppTheme.darkGray,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: AppTheme.spacingXs),
          Text(
            '⚠️ ${item['hint']}',
            style: AppTheme.bodySmall.copyWith(
              color: AppTheme.red,
            ),
          ),
          const SizedBox(height: AppTheme.spacingXs),
          Row(
            children: [
              const Icon(Icons.lightbulb_outline, size: 16, color: AppTheme.primaryBlue),
              const SizedBox(width: 4),
              Expanded(
                child: Text(
                  item['alternative'],
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.primaryBlue,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// 广东热门专业卡片
  Widget _buildGuangdongHotCard() {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        boxShadow: AppTheme.shadowLight,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题栏
          Container(
            padding: const EdgeInsets.all(AppTheme.spacingMd),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [AppTheme.orange, AppTheme.orange.withOpacity(0.8)],
              ),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(AppTheme.radiusLg),
                topRight: Radius.circular(AppTheme.radiusLg),
              ),
            ),
            child: Row(
              children: [
                const Icon(Icons.location_city, color: Colors.white),
                const SizedBox(width: AppTheme.spacingSm),
                const Text(
                  '🔥 广东热门专业',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Text(
                  '广东企业需求量大',
                  style: AppTheme.bodySmall.copyWith(
                    color: Colors.white70,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),

          // 热门专业列表
          Padding(
            padding: const EdgeInsets.all(AppTheme.spacingMd),
            child: Wrap(
              spacing: AppTheme.spacingXs,
              runSpacing: AppTheme.spacingXs,
              children: [
                '计算机科学与技术',
                '软件工程',
                '电子信息工程',
                '电气工程及其自动化',
                '自动化',
                '电子商务',
                '金融学',
                '工商管理',
              ].map((major) => Chip(
                  label: Text(major),
                  backgroundColor: AppTheme.orange.withOpacity(0.1),
                  labelStyle: AppTheme.bodySmall.copyWith(
                    color: AppTheme.darkGray,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                    side: BorderSide(color: AppTheme.orange.withOpacity(0.3)),
                  ),
                )).toList(),
            ),
          ),
        ],
      ),
    );
  }

  /// 生成分享图片
  void _generateShareImage() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('生成分享图片'),
        content: const Text('图片生成功能开发中...'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  /// 显示设置面板
  void _showSettingsSheet() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.person_outline),
              title: const Text('个人资料'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.history),
              title: const Text('历史记录'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.settings),
              title: const Text('设置'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.info_outline),
              title: const Text('关于'),
              onTap: () => Navigator.pop(context),
            ),
          ],
        ),
      ),
    );
  }
}
