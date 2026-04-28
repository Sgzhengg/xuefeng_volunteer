// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'gaokao_data_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AdmissionProbabilityResponse _$AdmissionProbabilityResponseFromJson(
        Map<String, dynamic> json) =>
    AdmissionProbabilityResponse(
      success: json['success'] as bool,
      message: json['message'] as String?,
      data: json['data'] == null
          ? null
          : AdmissionProbabilityData.fromJson(
              json['data'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$AdmissionProbabilityResponseToJson(
        AdmissionProbabilityResponse instance) =>
    <String, dynamic>{
      'success': instance.success,
      'message': instance.message,
      'data': instance.data,
    };

AdmissionProbabilityData _$AdmissionProbabilityDataFromJson(
        Map<String, dynamic> json) =>
    AdmissionProbabilityData(
      province: json['province'] as String,
      score: (json['score'] as num).toInt(),
      rank: (json['rank'] as num?)?.toInt(),
      universityName: json['universityName'] as String,
      majorName: json['majorName'] as String,
      probability: (json['probability'] as num).toDouble(),
      level: json['level'] as String,
      prediction: json['prediction'] as String,
      suggestion: json['suggestion'] as String?,
      similarUniversities: (json['similarUniversities'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      similarMajors: (json['similarMajors'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
    );

Map<String, dynamic> _$AdmissionProbabilityDataToJson(
        AdmissionProbabilityData instance) =>
    <String, dynamic>{
      'province': instance.province,
      'score': instance.score,
      'rank': instance.rank,
      'universityName': instance.universityName,
      'majorName': instance.majorName,
      'probability': instance.probability,
      'level': instance.level,
      'prediction': instance.prediction,
      'suggestion': instance.suggestion,
      'similarUniversities': instance.similarUniversities,
      'similarMajors': instance.similarMajors,
    };

OnePointSegmentResponse _$OnePointSegmentResponseFromJson(
        Map<String, dynamic> json) =>
    OnePointSegmentResponse(
      success: json['success'] as bool,
      message: json['message'] as String?,
      data: json['data'] == null
          ? null
          : OnePointSegmentData.fromJson(json['data'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$OnePointSegmentResponseToJson(
        OnePointSegmentResponse instance) =>
    <String, dynamic>{
      'success': instance.success,
      'message': instance.message,
      'data': instance.data,
    };

OnePointSegmentData _$OnePointSegmentDataFromJson(Map<String, dynamic> json) =>
    OnePointSegmentData(
      province: json['province'] as String,
      year: (json['year'] as num).toInt(),
      segments: (json['segments'] as List<dynamic>)
          .map((e) => ScoreSegment.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$OnePointSegmentDataToJson(
        OnePointSegmentData instance) =>
    <String, dynamic>{
      'province': instance.province,
      'year': instance.year,
      'segments': instance.segments,
    };

ScoreSegment _$ScoreSegmentFromJson(Map<String, dynamic> json) => ScoreSegment(
      score: (json['score'] as num).toInt(),
      rank: (json['rank'] as num).toInt(),
      cumulative: (json['cumulative'] as num).toInt(),
    );

Map<String, dynamic> _$ScoreSegmentToJson(ScoreSegment instance) =>
    <String, dynamic>{
      'score': instance.score,
      'rank': instance.rank,
      'cumulative': instance.cumulative,
    };

UniversityInfoResponse _$UniversityInfoResponseFromJson(
        Map<String, dynamic> json) =>
    UniversityInfoResponse(
      success: json['success'] as bool,
      message: json['message'] as String?,
      data: json['data'] == null
          ? null
          : UniversityInfoData.fromJson(json['data'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$UniversityInfoResponseToJson(
        UniversityInfoResponse instance) =>
    <String, dynamic>{
      'success': instance.success,
      'message': instance.message,
      'data': instance.data,
    };

UniversityInfoData _$UniversityInfoDataFromJson(Map<String, dynamic> json) =>
    UniversityInfoData(
      name: json['name'] as String,
      province: json['province'] as String,
      city: json['city'] as String,
      level: json['level'] as String,
      type: json['type'] as String,
      tags: (json['tags'] as List<dynamic>).map((e) => e as String).toList(),
      ranking2024: (json['ranking2024'] as num?)?.toInt(),
      minScore2024: (json['minScore2024'] as num?)?.toInt(),
      employmentRate: (json['employmentRate'] as num?)?.toDouble(),
      avgSalary: (json['avgSalary'] as num?)?.toDouble(),
      keyMajors:
          (json['keyMajors'] as List<dynamic>).map((e) => e as String).toList(),
      description: json['description'] as String,
    );

Map<String, dynamic> _$UniversityInfoDataToJson(UniversityInfoData instance) =>
    <String, dynamic>{
      'name': instance.name,
      'province': instance.province,
      'city': instance.city,
      'level': instance.level,
      'type': instance.type,
      'tags': instance.tags,
      'ranking2024': instance.ranking2024,
      'minScore2024': instance.minScore2024,
      'employmentRate': instance.employmentRate,
      'avgSalary': instance.avgSalary,
      'keyMajors': instance.keyMajors,
      'description': instance.description,
    };

ProvincialControlLineResponse _$ProvincialControlLineResponseFromJson(
        Map<String, dynamic> json) =>
    ProvincialControlLineResponse(
      success: json['success'] as bool,
      message: json['message'] as String?,
      data: json['data'] == null
          ? null
          : ProvincialControlLineData.fromJson(
              json['data'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$ProvincialControlLineResponseToJson(
        ProvincialControlLineResponse instance) =>
    <String, dynamic>{
      'success': instance.success,
      'message': instance.message,
      'data': instance.data,
    };

ProvincialControlLineData _$ProvincialControlLineDataFromJson(
        Map<String, dynamic> json) =>
    ProvincialControlLineData(
      province: json['province'] as String,
      year: (json['year'] as num).toInt(),
      scienceFirst: (json['scienceFirst'] as num?)?.toInt(),
      scienceSecond: (json['scienceSecond'] as num?)?.toInt(),
      artsFirst: (json['artsFirst'] as num?)?.toInt(),
      artsSecond: (json['artsSecond'] as num?)?.toInt(),
      comprehensiveFirst: (json['comprehensiveFirst'] as num?)?.toInt(),
      comprehensiveSecond: (json['comprehensiveSecond'] as num?)?.toInt(),
    );

Map<String, dynamic> _$ProvincialControlLineDataToJson(
        ProvincialControlLineData instance) =>
    <String, dynamic>{
      'province': instance.province,
      'year': instance.year,
      'scienceFirst': instance.scienceFirst,
      'scienceSecond': instance.scienceSecond,
      'artsFirst': instance.artsFirst,
      'artsSecond': instance.artsSecond,
      'comprehensiveFirst': instance.comprehensiveFirst,
      'comprehensiveSecond': instance.comprehensiveSecond,
    };

MajorEmploymentDataResponse _$MajorEmploymentDataResponseFromJson(
        Map<String, dynamic> json) =>
    MajorEmploymentDataResponse(
      success: json['success'] as bool,
      message: json['message'] as String?,
      data: json['data'] == null
          ? null
          : MajorEmploymentData.fromJson(json['data'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$MajorEmploymentDataResponseToJson(
        MajorEmploymentDataResponse instance) =>
    <String, dynamic>{
      'success': instance.success,
      'message': instance.message,
      'data': instance.data,
    };

MajorEmploymentData _$MajorEmploymentDataFromJson(Map<String, dynamic> json) =>
    MajorEmploymentData(
      majorName: json['majorName'] as String,
      category: json['category'] as String,
      employmentRate: (json['employmentRate'] as num).toDouble(),
      avgSalary: (json['avgSalary'] as num).toDouble(),
      salaryGrowth: (json['salaryGrowth'] as num).toDouble(),
      topPositions: (json['topPositions'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      topIndustries: (json['topIndustries'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      employmentTrend: json['employmentTrend'] as String,
      aiImpact: json['aiImpact'] as String,
    );

Map<String, dynamic> _$MajorEmploymentDataToJson(
        MajorEmploymentData instance) =>
    <String, dynamic>{
      'majorName': instance.majorName,
      'category': instance.category,
      'employmentRate': instance.employmentRate,
      'avgSalary': instance.avgSalary,
      'salaryGrowth': instance.salaryGrowth,
      'topPositions': instance.topPositions,
      'topIndustries': instance.topIndustries,
      'employmentTrend': instance.employmentTrend,
      'aiImpact': instance.aiImpact,
    };
