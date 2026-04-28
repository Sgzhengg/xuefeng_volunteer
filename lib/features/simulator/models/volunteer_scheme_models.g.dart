// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'volunteer_scheme_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

VolunteerScheme _$VolunteerSchemeFromJson(Map<String, dynamic> json) =>
    VolunteerScheme(
      province: json['province'] as String,
      score: (json['score'] as num).toInt(),
      subjectType: json['subjectType'] as String,
      generatedAt: json['generatedAt'] as String,
      chong: (json['chong'] as List<dynamic>)
          .map((e) => SchoolChoice.fromJson(e as Map<String, dynamic>))
          .toList(),
      wen: (json['wen'] as List<dynamic>)
          .map((e) => SchoolChoice.fromJson(e as Map<String, dynamic>))
          .toList(),
      bao: (json['bao'] as List<dynamic>)
          .map((e) => SchoolChoice.fromJson(e as Map<String, dynamic>))
          .toList(),
      dian: (json['dian'] as List<dynamic>)
          .map((e) => SchoolChoice.fromJson(e as Map<String, dynamic>))
          .toList(),
      advice:
          (json['advice'] as List<dynamic>).map((e) => e as String).toList(),
    );

Map<String, dynamic> _$VolunteerSchemeToJson(VolunteerScheme instance) =>
    <String, dynamic>{
      'province': instance.province,
      'score': instance.score,
      'subjectType': instance.subjectType,
      'generatedAt': instance.generatedAt,
      'chong': instance.chong,
      'wen': instance.wen,
      'bao': instance.bao,
      'dian': instance.dian,
      'advice': instance.advice,
    };

SchoolChoice _$SchoolChoiceFromJson(Map<String, dynamic> json) => SchoolChoice(
      universityName: json['universityName'] as String,
      major: json['major'] as String,
      probability: json['probability'] as String,
      suggestion: json['suggestion'] as String,
      type: json['type'] as String,
    );

Map<String, dynamic> _$SchoolChoiceToJson(SchoolChoice instance) =>
    <String, dynamic>{
      'universityName': instance.universityName,
      'major': instance.major,
      'probability': instance.probability,
      'suggestion': instance.suggestion,
      'type': instance.type,
    };
