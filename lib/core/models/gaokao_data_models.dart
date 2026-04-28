import 'package:json_annotation/json_annotation.dart';

part 'gaokao_data_models.g.dart';

/// 录取概率预测响应
@JsonSerializable()
class AdmissionProbabilityResponse {
  final bool success;
  final String? message;
  final AdmissionProbabilityData? data;

  AdmissionProbabilityResponse({
    required this.success,
    this.message,
    this.data,
  });

  factory AdmissionProbabilityResponse.fromJson(Map<String, dynamic> json) =>
      _$AdmissionProbabilityResponseFromJson(json);

  Map<String, dynamic> toJson() => _$AdmissionProbabilityResponseToJson(this);
}

@JsonSerializable()
class AdmissionProbabilityData {
  final String province;
  final int score;
  final int? rank;
  final String universityName;
  final String majorName;
  final double probability; // 录取概率 (0-100)
  final String level; // 院校层次 (985/211/双一流/普通本科)
  final String prediction; // 预测结论
  final String? suggestion; // 报考建议
  final List<String>? similarUniversities; // 相似院校
  final List<String>? similarMajors; // 相似专业

  AdmissionProbabilityData({
    required this.province,
    required this.score,
    this.rank,
    required this.universityName,
    required this.majorName,
    required this.probability,
    required this.level,
    required this.prediction,
    this.suggestion,
    this.similarUniversities,
    this.similarMajors,
  });

  factory AdmissionProbabilityData.fromJson(Map<String, dynamic> json) =>
      _$AdmissionProbabilityDataFromJson(json);

  Map<String, dynamic> toJson() => _$AdmissionProbabilityDataToJson(this);
}

/// 一分一段表响应
@JsonSerializable()
class OnePointSegmentResponse {
  final bool success;
  final String? message;
  final OnePointSegmentData? data;

  OnePointSegmentResponse({
    required this.success,
    this.message,
    this.data,
  });

  factory OnePointSegmentResponse.fromJson(Map<String, dynamic> json) =>
      _$OnePointSegmentResponseFromJson(json);

  Map<String, dynamic> toJson() => _$OnePointSegmentResponseToJson(this);
}

@JsonSerializable()
class OnePointSegmentData {
  final String province;
  final int year;
  final List<ScoreSegment> segments;

  OnePointSegmentData({
    required this.province,
    required this.year,
    required this.segments,
  });

  factory OnePointSegmentData.fromJson(Map<String, dynamic> json) =>
      _$OnePointSegmentDataFromJson(json);

  Map<String, dynamic> toJson() => _$OnePointSegmentDataToJson(this);
}

@JsonSerializable()
class ScoreSegment {
  final int score; // 分数
  final int rank; // 该分数对应的人数
  final int cumulative; // 累计人数（位次）

  ScoreSegment({
    required this.score,
    required this.rank,
    required this.cumulative,
  });

  factory ScoreSegment.fromJson(Map<String, dynamic> json) =>
      _$ScoreSegmentFromJson(json);

  Map<String, dynamic> toJson() => _$ScoreSegmentToJson(this);
}

/// 院校信息响应
@JsonSerializable()
class UniversityInfoResponse {
  final bool success;
  final String? message;
  final UniversityInfoData? data;

  UniversityInfoResponse({
    required this.success,
    this.message,
    this.data,
  });

  factory UniversityInfoResponse.fromJson(Map<String, dynamic> json) =>
      _$UniversityInfoResponseFromJson(json);

  Map<String, dynamic> toJson() => _$UniversityInfoResponseToJson(this);
}

@JsonSerializable()
class UniversityInfoData {
  final String name; // 院校名称
  final String province; // 所在省份
  final String city; // 所在城市
  final String level; // 院校层次 (985/211/双一流/普通本科)
  final String type; // 院校类型 (综合/理工/师范/医学等)
  final List<String> tags; // 标签
  final int? ranking2024; // 2024排名
  final int? minScore2024; // 2024最低录取分
  final double? employmentRate; // 就业率
  final double? avgSalary; // 平均薪资
  final List<String> keyMajors; // 重点专业
  final String description; // 院校描述

  UniversityInfoData({
    required this.name,
    required this.province,
    required this.city,
    required this.level,
    required this.type,
    required this.tags,
    this.ranking2024,
    this.minScore2024,
    this.employmentRate,
    this.avgSalary,
    required this.keyMajors,
    required this.description,
  });

  factory UniversityInfoData.fromJson(Map<String, dynamic> json) =>
      _$UniversityInfoDataFromJson(json);

  Map<String, dynamic> toJson() => _$UniversityInfoDataToJson(this);
}

/// 省控线响应
@JsonSerializable()
class ProvincialControlLineResponse {
  final bool success;
  final String? message;
  final ProvincialControlLineData? data;

  ProvincialControlLineResponse({
    required this.success,
    this.message,
    this.data,
  });

  factory ProvincialControlLineResponse.fromJson(Map<String, dynamic> json) =>
      _$ProvincialControlLineResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ProvincialControlLineResponseToJson(this);
}

@JsonSerializable()
class ProvincialControlLineData {
  final String province;
  final int year;
  final int? scienceFirst; // 理科一本线
  final int? scienceSecond; // 理科二本线
  final int? artsFirst; // 文科一本线
  final int? artsSecond; // 文科二本线
  final int? comprehensiveFirst; // 综合一本线（新高考）
  final int? comprehensiveSecond; // 综合二本线（新高考）

  ProvincialControlLineData({
    required this.province,
    required this.year,
    this.scienceFirst,
    this.scienceSecond,
    this.artsFirst,
    this.artsSecond,
    this.comprehensiveFirst,
    this.comprehensiveSecond,
  });

  factory ProvincialControlLineData.fromJson(Map<String, dynamic> json) =>
      _$ProvincialControlLineDataFromJson(json);

  Map<String, dynamic> toJson() => _$ProvincialControlLineDataToJson(this);
}

/// 专业就业数据响应
@JsonSerializable()
class MajorEmploymentDataResponse {
  final bool success;
  final String? message;
  final MajorEmploymentData? data;

  MajorEmploymentDataResponse({
    required this.success,
    this.message,
    this.data,
  });

  factory MajorEmploymentDataResponse.fromJson(Map<String, dynamic> json) =>
      _$MajorEmploymentDataResponseFromJson(json);

  Map<String, dynamic> toJson() => _$MajorEmploymentDataResponseToJson(this);
}

@JsonSerializable()
class MajorEmploymentData {
  final String majorName; // 专业名称
  final String category; // 专业类别
  final double employmentRate; // 就业率
  final double avgSalary; // 平均薪资
  final double salaryGrowth; // 薪资增长率
  final List<String> topPositions; // 主要岗位
  final List<String> topIndustries; // 主要行业
  final String employmentTrend; // 就业趋势 (上升/稳定/下降)
  final String aiImpact; // AI冲击程度 (低/中/高)

  MajorEmploymentData({
    required this.majorName,
    required this.category,
    required this.employmentRate,
    required this.avgSalary,
    required this.salaryGrowth,
    required this.topPositions,
    required this.topIndustries,
    required this.employmentTrend,
    required this.aiImpact,
  });

  factory MajorEmploymentData.fromJson(Map<String, dynamic> json) =>
      _$MajorEmploymentDataFromJson(json);

  Map<String, dynamic> toJson() => _$MajorEmploymentDataToJson(this);
}
