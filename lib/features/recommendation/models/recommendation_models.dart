import 'package:flutter/foundation.dart';

/// 推荐结果模型
class RecommendationResult {
  final BasicInfo basicInfo;
  final List<UniversityRecommendation> chong;
  final List<UniversityRecommendation> wen;
  final List<UniversityRecommendation> bao;
  final List<UniversityRecommendation> dian;
  final RecommendationAnalysis analysis;
  final List<String> advice;

  RecommendationResult({
    required this.basicInfo,
    required this.chong,
    required this.wen,
    required this.bao,
    required this.dian,
    required this.analysis,
    required this.advice,
  });

  factory RecommendationResult.fromJson(Map<String, dynamic> json) {
    final data = json['data'];

    return RecommendationResult(
      basicInfo: BasicInfo.fromJson(data['basic_info']),
      chong: (data['冲刺'] as List<dynamic>?)
              ?.map((e) => UniversityRecommendation.fromJson(e))
              .toList() ?? [],
      wen: (data['稳妥'] as List<dynamic>?)
            ?.map((e) => UniversityRecommendation.fromJson(e))
            .toList() ?? [],
      bao: (data['保底'] as List<dynamic>?)
            ?.map((e) => UniversityRecommendation.fromJson(e))
            .toList() ?? [],
      dian: (data['垫底'] as List<dynamic>?)
            ?.map((e) => UniversityRecommendation.fromJson(e))
            .toList() ?? [],
      analysis: RecommendationAnalysis.fromJson(data['analysis'] ?? {}),
      advice: (data['advice'] as List<dynamic>?)
             ?.map((e) => e.toString())
             .toList() ?? [],
    );
  }

  List<UniversityRecommendation> getAllRecommendations() {
    return [...chong, ...wen, ...bao, ...dian];
  }

  Map<String, dynamic> toJson() {
    return {
      'data': {
        'basic_info': basicInfo.toJson(),
        '冲刺': chong.map((e) => e.toJson()).toList(),
        '稳妥': wen.map((e) => e.toJson()).toList(),
        '保底': bao.map((e) => e.toJson()).toList(),
        '垫底': dian.map((e) => e.toJson()).toList(),
        'analysis': analysis.toJson(),
        'advice': advice,
      }
    };
  }
}

/// 基本信息
class BasicInfo {
  final String province;
  final int score;
  final int rank;
  final String subjectType;
  final List<String> targetMajors;
  final String generatedAt;

  BasicInfo({
    required this.province,
    required this.score,
    required this.rank,
    required this.subjectType,
    required this.targetMajors,
    required this.generatedAt,
  });

  factory BasicInfo.fromJson(Map<String, dynamic> json) {
    return BasicInfo(
      province: json['province'] ?? '',
      score: json['score'] ?? 0,
      rank: json['rank'] ?? 0,
      subjectType: json['subject_type'] ?? '综合',
      targetMajors: (json['target_majors'] as List<dynamic>?)
                   ?.map((e) => e.toString())
                   .toList() ?? [],
      generatedAt: json['generated_at'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'province': province,
      'score': score,
      'rank': rank,
      'subject_type': subjectType,
      'target_majors': targetMajors,
      'generated_at': generatedAt,
    };
  }
}

/// 院校推荐
class UniversityRecommendation {
  final String universityId;
  final String universityName;
  final String universityLevel;
  final String universityType;
  final String province;
  final String city;
  final String major;
  final int probability;
  final String probabilityRange;
  final String category;
  final int scoreGap;
  final int rankGap;
  final List<String> suggestions;
  final List<String> universityHighlights;
  final List<String> majorHighlights;
  final EmploymentInfo employmentInfo;
  final UniversityEmployment universityEmployment;

  // ROI相关字段
  final int roiScore; // 值得指数分数 (0-100)
  final String roiLevel; // A级/B级/C级
  final String roiColor; // green/blue/orange/red
  final String roiReason; // ROI评价理由
  final bool isRedMajor; // 是否红牌专业

  UniversityRecommendation({
    required this.universityId,
    required this.universityName,
    required this.universityLevel,
    required this.universityType,
    required this.province,
    required this.city,
    required this.major,
    required this.probability,
    required this.probabilityRange,
    required this.category,
    required this.scoreGap,
    required this.rankGap,
    required this.suggestions,
    required this.universityHighlights,
    required this.majorHighlights,
    required this.employmentInfo,
    required this.universityEmployment,
    this.roiScore = 0,
    this.roiLevel = 'B级',
    this.roiColor = 'blue',
    this.roiReason = '',
    this.isRedMajor = false,
  });

  factory UniversityRecommendation.fromJson(Map<String, dynamic> json) {
    // 解析ROI相关字段
    final roiScore = json['roi_score'] ?? 0;
    final roiLevel = json['roi_level'] ?? 'B级';
    final roiColor = json['roi_color'] ?? 'blue';
    final roiReason = json['roi_reason'] ?? '';
    final isRedMajor = json['is_red_major'] ?? false;

    return UniversityRecommendation(
      universityId: json['university_id'] ?? '',
      universityName: json['university_name'] ?? '',
      universityLevel: json['university_level'] ?? '',
      universityType: json['university_type'] ?? '',
      province: json['province'] ?? '',
      city: json['city'] ?? '',
      major: json['major'] ?? '',
      probability: json['probability'] ?? 0,
      probabilityRange: json['probability_range'] ?? '',
      category: json['category'] ?? '',
      scoreGap: json['score_gap'] ?? 0,
      rankGap: json['rank_gap'] ?? 0,
      suggestions: (json['suggestions'] as List<dynamic>?)
                  ?.map((e) => e.toString())
                  .toList() ?? [],
      universityHighlights: (json['university_highlights'] as List<dynamic>?)
                          ?.map((e) => e.toString())
                          .toList() ?? [],
      majorHighlights: (json['major_highlights'] as List<dynamic>?)
                     ?.map((e) => e.toString())
                     .toList() ?? [],
      employmentInfo: EmploymentInfo.fromJson(json['employment_info'] ?? {}),
      universityEmployment: UniversityEmployment.fromJson(json['university_employment'] ?? {}),
      roiScore: roiScore,
      roiLevel: roiLevel,
      roiColor: roiColor,
      roiReason: roiReason,
      isRedMajor: isRedMajor,
    );
  }

  /// 获取概率颜色
  String getProbabilityColor() {
    if (probability >= 75) return 'green';
    if (probability >= 50) return 'blue';
    if (probability >= 30) return 'orange';
    return 'red';
  }

  /// 获取ROI颜色
  String getRoiColor() {
    if (isRedMajor) return 'red';
    if (roiScore >= 80) return 'green';
    if (roiScore >= 60) return 'blue';
    return 'orange';
  }

  /// 获取ROI等级文字
  String getRoiLevelText() {
    if (isRedMajor) return '⚠️ 红牌专业';
    if (roiScore >= 80) return 'A级';
    if (roiScore >= 60) return 'B级';
    return 'C级';
  }

  /// 获取ROI建议
  String getRoiAdvice() {
    if (isRedMajor) return '⚠️ 教育部红牌专业，就业率偏低，建议慎重';
    if (roiScore >= 80) return '💰 回报率高，推荐';
    if (roiScore >= 60) return '📊 回报率中等，可考虑';
    return '⚠️ 回报率偏低，建议了解';
  }

  Map<String, dynamic> toJson() {
    return {
      'university_id': universityId,
      'university_name': universityName,
      'university_level': universityLevel,
      'university_type': universityType,
      'province': province,
      'city': city,
      'major': major,
      'probability': probability,
      'probability_range': probabilityRange,
      'category': category,
      'score_gap': scoreGap,
      'rank_gap': rankGap,
      'suggestions': suggestions,
      'university_highlights': universityHighlights,
      'major_highlights': majorHighlights,
      'employment_info': employmentInfo.toJson(),
      'university_employment': universityEmployment.toJson(),
      'roi_score': roiScore,
      'roi_level': roiLevel,
      'roi_color': roiColor,
      'roi_reason': roiReason,
      'is_red_major': isRedMajor,
    };
  }
}

/// 就业信息
class EmploymentInfo {
  final String employmentRate;
  final String averageSalary;
  final List<String> topEmployers;

  EmploymentInfo({
    required this.employmentRate,
    required this.averageSalary,
    required this.topEmployers,
  });

  factory EmploymentInfo.fromJson(Map<String, dynamic> json) {
    final rate = json['employment_rate'];
    return EmploymentInfo(
      employmentRate: rate is double ? '${(rate * 100).toStringAsFixed(0)}%' : (rate?.toString() ?? '未知'),
      averageSalary: json['average_salary']?.toString() ?? '未知',
      topEmployers: (json['top_employers'] as List<dynamic>?)
                   ?.map((e) => e.toString())
                   .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'employment_rate': employmentRate,
      'average_salary': averageSalary,
      'top_employers': topEmployers,
    };
  }
}

/// 院校就业信息
class UniversityEmployment {
  final String employmentRate;
  final String graduateSchoolRate;

  UniversityEmployment({
    required this.employmentRate,
    required this.graduateSchoolRate,
  });

  factory UniversityEmployment.fromJson(Map<String, dynamic> json) {
    final empRate = json['employment_rate'];
    final gradRate = json['graduate_school_rate'];

    return UniversityEmployment(
      employmentRate: empRate is double ? '${(empRate * 100).toStringAsFixed(0)}%' : (empRate?.toString() ?? '未知'),
      graduateSchoolRate: gradRate is double ? '${(gradRate * 100).toStringAsFixed(0)}%' : (gradRate?.toString() ?? '未知'),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'employment_rate': employmentRate,
      'graduate_school_rate': graduateSchoolRate,
    };
  }
}

/// 推荐分析
class RecommendationAnalysis {
  final int totalCount;
  final Map<String, int> categoryCounts;
  final List<String> comments;

  RecommendationAnalysis({
    required this.totalCount,
    required this.categoryCounts,
    required this.comments,
  });

  factory RecommendationAnalysis.fromJson(Map<String, dynamic> json) {
    final categoryCounts = <String, int>{};
    if (json['category_counts'] != null) {
      (json['category_counts'] as Map<String, dynamic>).forEach((key, value) {
        categoryCounts[key] = value as int;
      });
    }

    return RecommendationAnalysis(
      totalCount: json['total_count'] ?? 0,
      categoryCounts: categoryCounts,
      comments: (json['comments'] as List<dynamic>?)
                ?.map((e) => e.toString())
                .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_count': totalCount,
      'category_counts': categoryCounts,
      'comments': comments,
    };
  }
}

/// 推荐请求参数
class RecommendationRequest {
  final String province;
  final int score;
  final String subjectType;
  final List<String>? targetMajors;
  final int? rank;
  final Map<String, dynamic>? preferences;

  RecommendationRequest({
    required this.province,
    required this.score,
    this.subjectType = '理科',
    this.targetMajors,
    this.rank,
    this.preferences,
  });

  Map<String, dynamic> toJson() {
    return {
      'province': province,
      'score': score,
      'subject_type': subjectType,
      'target_majors': targetMajors,
      'rank': rank,
      'preferences': preferences,
    };
  }
}
