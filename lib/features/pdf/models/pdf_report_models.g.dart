// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pdf_report_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PDFReportData _$PDFReportDataFromJson(Map<String, dynamic> json) =>
    PDFReportData(
      title: json['title'] as String,
      generatedAt: json['generatedAt'] as String,
      userProfile:
          UserProfileData.fromJson(json['userProfile'] as Map<String, dynamic>),
      dataSummary:
          DataSummary.fromJson(json['dataSummary'] as Map<String, dynamic>),
      keyRecommendations: (json['keyRecommendations'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      chatSummary:
          ChatSummary.fromJson(json['chatSummary'] as Map<String, dynamic>),
      disclaimer: json['disclaimer'] as String,
    );

Map<String, dynamic> _$PDFReportDataToJson(PDFReportData instance) =>
    <String, dynamic>{
      'title': instance.title,
      'generatedAt': instance.generatedAt,
      'userProfile': instance.userProfile,
      'dataSummary': instance.dataSummary,
      'keyRecommendations': instance.keyRecommendations,
      'chatSummary': instance.chatSummary,
      'disclaimer': instance.disclaimer,
    };

UserProfileData _$UserProfileDataFromJson(Map<String, dynamic> json) =>
    UserProfileData(
      score: json['score'] as String,
      province: json['province'] as String,
      selectedSubjects: json['selectedSubjects'] as String,
      familyBackground: json['familyBackground'] as String,
      interests: json['interests'] as String,
    );

Map<String, dynamic> _$UserProfileDataToJson(UserProfileData instance) =>
    <String, dynamic>{
      'score': instance.score,
      'province': instance.province,
      'selectedSubjects': instance.selectedSubjects,
      'familyBackground': instance.familyBackground,
      'interests': instance.interests,
    };

DataSummary _$DataSummaryFromJson(Map<String, dynamic> json) => DataSummary(
      admissionProbability:
          json['admissionProbability'] as Map<String, dynamic>?,
      universityInfo: json['universityInfo'] as Map<String, dynamic>?,
      majorEmployment: json['majorEmployment'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$DataSummaryToJson(DataSummary instance) =>
    <String, dynamic>{
      'admissionProbability': instance.admissionProbability,
      'universityInfo': instance.universityInfo,
      'majorEmployment': instance.majorEmployment,
    };

ChatSummary _$ChatSummaryFromJson(Map<String, dynamic> json) => ChatSummary(
      totalMessages: (json['totalMessages'] as num).toInt(),
      userQuestions: (json['userQuestions'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      keyTopics:
          (json['keyTopics'] as List<dynamic>).map((e) => e as String).toList(),
    );

Map<String, dynamic> _$ChatSummaryToJson(ChatSummary instance) =>
    <String, dynamic>{
      'totalMessages': instance.totalMessages,
      'userQuestions': instance.userQuestions,
      'keyTopics': instance.keyTopics,
    };
