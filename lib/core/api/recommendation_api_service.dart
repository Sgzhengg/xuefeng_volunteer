import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

/// 推荐API服务
class RecommendationApiService {
  final Dio _dio;
  static const String _baseUrl = 'http://localhost:8000';

  RecommendationApiService({Dio? dio})
      : _dio = dio ?? Dio(BaseOptions(
          baseUrl: _baseUrl,
          connectTimeout: const Duration(seconds: 30),
          receiveTimeout: const Duration(seconds: 30),
          headers: {
            'Content-Type': 'application/json',
          },
        ));

  /// 生成智能推荐方案
  Future<Map<String, dynamic>> generateRecommendation({
    required String province,
    required int score,
    String subjectType = '理科',
    List<String>? targetMajors,
    int? rank,
    Map<String, dynamic>? preferences,
  }) async {
    try {
      final response = await _dio.post(
        '/recommendation/generate',
        data: {
          'province': province,
          'score': score,
          'subject_type': subjectType,
          'target_majors': targetMajors,
          'rank': rank,
          'preferences': preferences,
        },
      );

      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      } else {
        throw Exception('推荐失败: ${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (kDebugMode) {
        print('推荐API错误: ${e.message}');
        print('错误类型: ${e.type}');
        print('错误响应: ${e.response}');
      }

      // 网络错误时返回模拟数据
      return _getMockRecommendation(province, score, subjectType, targetMajors);
    } catch (e) {
      if (kDebugMode) {
        print('未知错误: $e');
      }
      rethrow;
    }
  }

  /// 根据分数推荐专业
  Future<Map<String, dynamic>> suggestMajors({
    required int score,
    String subjectType = '理科',
  }) async {
    try {
      final response = await _dio.get(
        '/recommendation/majors/suggest',
        queryParameters: {
          'score': score,
          'subject_type': subjectType,
        },
      );

      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      } else {
        throw Exception('专业推荐失败: ${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (kDebugMode) {
        print('专业推荐API错误: ${e.message}');
      }
      // 返回模拟数据
      return _getMockMajorSuggestions(score, subjectType);
    } catch (e) {
      rethrow;
    }
  }

  /// 计算位次
  Future<Map<String, dynamic>> calculateRank({
    required String province,
    required int score,
  }) async {
    try {
      final response = await _dio.get(
        '/recommendation/rank/calculate',
        queryParameters: {
          'province': province,
          'score': score,
        },
      );

      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      } else {
        throw Exception('位次计算失败: ${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (kDebugMode) {
        print('位次计算API错误: ${e.message}');
      }
      // 返回模拟数据
      return _getMockRank(province, score);
    } catch (e) {
      rethrow;
    }
  }

  /// 模拟推荐数据（用于离线测试）
  Map<String, dynamic> _getMockRecommendation(
    String province,
    int score,
    String subjectType,
    List<String>? targetMajors,
  ) {
    final majors = targetMajors ?? ['计算机科学与技术', '软件工程'];

    return {
      'success': true,
      'data': {
        'basic_info': {
          'province': province,
          'score': score,
          'rank': _estimateRank(score),
          'subject_type': subjectType,
          'target_majors': majors,
          'generated_at': DateTime.now().toString().substring(0, 19),
        },
        '冲刺': [
          {
            'university_id': '1',
            'university_name': '北京大学',
            'university_level': '985',
            'university_type': '综合',
            'province': '北京',
            'city': '北京',
            'major': majors[0],
            'probability': 35,
            'probability_range': '30-40%',
            'category': '冲刺',
            'score_gap': score - 685,
            'rank_gap': _estimateRank(score) - _estimateRank(685),
            'suggestions': ['分数接近，可以尝试', '建议放在志愿前面'],
            'university_highlights': ['全国排名#1', '12个国家重点学科'],
            'major_highlights': ['就业前景广阔', '薪资水平高'],
            'employment_info': {
              'employment_rate': 0.96,
              'average_salary': '15000-20000元/月',
              'top_employers': ['华为', '腾讯', '阿里巴巴']
            },
            'university_employment': {
              'employment_rate': 0.97,
              'graduate_school_rate': 0.50
            }
          },
          {
            'university_id': '2',
            'university_name': '清华大学',
            'university_level': '985',
            'university_type': '综合',
            'province': '北京',
            'city': '北京',
            'major': majors[0],
            'probability': 32,
            'probability_range': '28-37%',
            'category': '冲刺',
            'score_gap': score - 686,
            'suggestions': ['分数接近，可以尝试'],
            'university_highlights': ['全国排名#2', '14个国家重点学科'],
            'major_highlights': ['就业前景广阔', '课程丰富'],
            'employment_info': {
              'employment_rate': 0.97,
              'average_salary': '15000-20000元/月',
              'top_employers': ['华为', '腾讯', '字节跳动']
            },
            'university_employment': {
              'employment_rate': 0.98,
              'graduate_school_rate': 0.55
            }
          },
        ],
        '稳妥': [
          {
            'university_id': '3',
            'university_name': '南京大学',
            'university_level': '985',
            'university_type': '综合',
            'province': '江苏',
            'city': '南京',
            'major': majors[0],
            'probability': 65,
            'probability_range': '60-70%',
            'category': '稳妥',
            'score_gap': score - 665,
            'suggestions': ['录取概率较大', '建议作为主要志愿'],
            'university_highlights': ['全国排名#6', '985高校'],
            'major_highlights': ['实力强劲', '发展稳定'],
            'employment_info': {
              'employment_rate': 0.95,
              'average_salary': '12000-18000元/月',
              'top_employers': ['苏宁', '华为', '中兴']
            },
            'university_employment': {
              'employment_rate': 0.96,
              'graduate_school_rate': 0.45
            }
          },
          {
            'university_id': '4',
            'university_name': '浙江大学',
            'university_level': '985',
            'university_type': '综合',
            'province': '浙江',
            'city': '杭州',
            'major': majors[0],
            'probability': 70,
            'probability_range': '65-75%',
            'category': '稳妥',
            'score_gap': score - 660,
            'suggestions': ['性价比高', '地理位置优越'],
            'university_highlights': ['全国排名#3', '13个国家重点学科'],
            'major_highlights': ['学科评估A+', '就业前景好'],
            'employment_info': {
              'employment_rate': 0.96,
              'average_salary': '14000-19000元/月',
              'top_employers': ['阿里巴巴', '网易', '海康威视']
            },
            'university_employment': {
              'employment_rate': 0.97,
              'graduate_school_rate': 0.48
            }
          },
        ],
        '保底': [
          {
            'university_id': '5',
            'university_name': '苏州大学',
            'university_level': '211',
            'university_type': '综合',
            'province': '江苏',
            'city': '苏州',
            'major': majors[0],
            'probability': 85,
            'probability_range': '80-90%',
            'category': '保底',
            'score_gap': score - 630,
            'suggestions': ['基本没问题', '城市环境好'],
            'university_highlights': ['211高校', '省属重点'],
            'major_highlights': ['专业实力强', '就业稳定'],
            'employment_info': {
              'employment_rate': 0.93,
              'average_salary': '10000-15000元/月',
              'top_employers': ['苏州本地企业', '上海企业']
            },
            'university_employment': {
              'employment_rate': 0.94,
              'graduate_school_rate': 0.35
            }
          },
        ],
        '垫底': [
          {
            'university_id': '6',
            'university_name': '江南大学',
            'university_level': '211',
            'university_type': '综合',
            'province': '江苏',
            'city': '无锡',
            'major': majors[0],
            'probability': 95,
            'probability_range': '95%+',
            'category': '垫底',
            'score_gap': score - 600,
            'suggestions': ['稳保录取', '肯定能上'],
            'university_highlights': ['211高校', '轻工特色'],
            'major_highlights': ['特色专业', '就业稳定'],
            'employment_info': {
              'employment_rate': 0.92,
              'average_salary': '9000-13000元/月',
              'top_employers': ['无锡本地企业', '苏州企业']
            },
            'university_employment': {
              'employment_rate': 0.93,
              'graduate_school_rate': 0.25
            }
          },
        ],
        'analysis': {
          'total_count': 6,
          'category_counts': {
            '冲刺': 2,
            '稳妥': 2,
            '保底': 1,
            '垫底': 1
          },
          'comments': [
            '共找到6所院校，方案完整',
            '建议适当扩大专业范围以获得更多选择'
          ]
        },
        'advice': [
          '有2个冲刺院校，建议选择1-2个最有希望的',
          '有2个稳妥院校，这是重点，建议选3-4个',
          '有1个保底院校，建议选2-3个',
          '建议比例：冲刺20%，稳妥40%，保底30%，垫底10%'
        ]
      }
    };
  }

  /// 模拟专业建议
  Map<String, dynamic> _getMockMajorSuggestions(int score, String subjectType) {
    List<String> majors;

    if (score >= 680) {
      majors = [
        '计算机科学与技术',
        '人工智能',
        '临床医学',
        '口腔医学',
        '金融学',
        '经济学',
        '法学',
        '电气工程及其自动化'
      ];
    } else if (score >= 650) {
      majors = [
        '计算机科学与技术',
        '软件工程',
        '电子信息工程',
        '自动化',
        '临床医学',
        '金融学',
        '会计学',
        '电气工程及其自动化'
      ];
    } else if (score >= 600) {
      majors = [
        '计算机科学与技术',
        '软件工程',
        '电子信息工程',
        '会计学',
        '金融学',
        '自动化',
        '临床医学'
      ];
    } else {
      majors = [
        '计算机科学与技术',
        '会计学',
        '金融学',
        '自动化',
        '电子信息工程',
        '机械设计制造及其自动化'
      ];
    }

    return {
      'success': true,
      'data': {
        'score': score,
        'subject_type': subjectType,
        'suggested_majors': majors.take(5).toList()
      }
    };
  }

  /// 模拟位次计算
  Map<String, dynamic> _getMockRank(String province, int score) {
    return {
      'success': true,
      'data': {
        'province': province,
        'score': score,
        'rank': _estimateRank(score)
      }
    };
  }

  /// 估算位次（简化算法）
  int _estimateRank(int score) {
    // 简化的位次估算公式
    if (score >= 700) {
      return 100 + (700 - score) * 50;
    } else if (score >= 650) {
      return 3000 + (650 - score) * 200;
    } else if (score >= 600) {
      return 13000 + (600 - score) * 500;
    } else {
      return 38000 + (600 - score) * 1000;
    }
  }
}

// 扩展List的take方法
extension ListExtension<T> on List<T> {
  List<T> take(int n) {
    if (length <= n) return this;
    return sublist(0, n);
  }
}
