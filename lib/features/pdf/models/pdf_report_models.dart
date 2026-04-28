import 'package:json_annotation/json_annotation.dart';

part 'pdf_report_models.g.dart';

/// PDF 报告数据模型
@JsonSerializable()
class PDFReportData {
  final String title;
  final String generatedAt;
  final UserProfileData userProfile;
  final DataSummary dataSummary;
  final List<String> keyRecommendations;
  final ChatSummary chatSummary;
  final String disclaimer;

  PDFReportData({
    required this.title,
    required this.generatedAt,
    required this.userProfile,
    required this.dataSummary,
    required this.keyRecommendations,
    required this.chatSummary,
    required this.disclaimer,
  });

  factory PDFReportData.fromJson(Map<String, dynamic> json) =>
      _$PDFReportDataFromJson(json);

  Map<String, dynamic> toJson() => _$PDFReportDataToJson(this);
}

@JsonSerializable()
class UserProfileData {
  final String score;
  final String province;
  final String selectedSubjects;
  final String familyBackground;
  final String interests;

  UserProfileData({
    required this.score,
    required this.province,
    required this.selectedSubjects,
    required this.familyBackground,
    required this.interests,
  });

  factory UserProfileData.fromJson(Map<String, dynamic> json) =>
      _$UserProfileDataFromJson(json);

  Map<String, dynamic> toJson() => _$UserProfileDataToJson(this);
}

@JsonSerializable()
class DataSummary {
  final Map<String, dynamic>? admissionProbability;
  final Map<String, dynamic>? universityInfo;
  final Map<String, dynamic>? majorEmployment;

  DataSummary({
    this.admissionProbability,
    this.universityInfo,
    this.majorEmployment,
  });

  factory DataSummary.fromJson(Map<String, dynamic> json) =>
      _$DataSummaryFromJson(json);

  Map<String, dynamic> toJson() => _$DataSummaryToJson(this);
}

@JsonSerializable()
class ChatSummary {
  final int totalMessages;
  final List<String> userQuestions;
  final List<String> keyTopics;

  ChatSummary({
    required this.totalMessages,
    required this.userQuestions,
    required this.keyTopics,
  });

  factory ChatSummary.fromJson(Map<String, dynamic> json) =>
      _$ChatSummaryFromJson(json);

  Map<String, dynamic> toJson() => _$ChatSummaryToJson(this);
}
