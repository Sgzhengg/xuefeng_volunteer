import 'package:json_annotation/json_annotation.dart';

part 'volunteer_scheme_models.g.dart';

/// 志愿方案
@JsonSerializable()
class VolunteerScheme {
  final String province;
  final int score;
  final String subjectType;
  final String generatedAt;
  final List<SchoolChoice> chong; // 冲刺
  final List<SchoolChoice> wen; // 稳妥
  final List<SchoolChoice> bao; // 保底
  final List<SchoolChoice> dian; // 垫底
  final List<String> advice;

  VolunteerScheme({
    required this.province,
    required this.score,
    required this.subjectType,
    required this.generatedAt,
    required this.chong,
    required this.wen,
    required this.bao,
    required this.dian,
    required this.advice,
  });

  factory VolunteerScheme.fromJson(Map<String, dynamic> json) =>
      _$VolunteerSchemeFromJson(json);

  Map<String, dynamic> toJson() => _$VolunteerSchemeToJson(this);
}

/// 院校选择
@JsonSerializable()
class SchoolChoice {
  final String universityName;
  final String major;
  final String probability;
  final String suggestion;
  final String type;

  SchoolChoice({
    required this.universityName,
    required this.major,
    required this.probability,
    required this.suggestion,
    required this.type,
  });

  factory SchoolChoice.fromJson(Map<String, dynamic> json) =>
      _$SchoolChoiceFromJson(json);

  Map<String, dynamic> toJson() => _$SchoolChoiceToJson(this);
}

/// 志愿模拟器请求
class VolunteerSchemeRequest {
  final String province;
  final int score;
  final String subjectType;
  final List<String> targetMajors;
  final int? rank;
  final Map<String, dynamic>? preferences;

  VolunteerSchemeRequest({
    required this.province,
    required this.score,
    required this.subjectType,
    required this.targetMajors,
    this.rank,
    this.preferences,
  });

  Map<String, dynamic> toJson() {
    return {
      'province': province,
      'score': score,
      'subject_type': subjectType,
      'target_majors': targetMajors,
      if (rank != null) 'rank': rank,
      if (preferences != null) 'preferences': preferences,
    };
  }
}
