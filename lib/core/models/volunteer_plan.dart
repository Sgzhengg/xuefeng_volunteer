class VolunteerPlan {
  final String id;
  final String universityName;
  final String majorName;
  final int probability;
  final int roiScore;
  final String roiLevel;
  final String tag;
  final String universityType;
  final String city;

  VolunteerPlan({
    required this.id,
    required this.universityName,
    required this.majorName,
    required this.probability,
    required this.roiScore,
    required this.roiLevel,
    required this.tag,
    required this.universityType,
    required this.city,
  });

  factory VolunteerPlan.fromJson(Map<String, dynamic> json) {
    return VolunteerPlan(
      id: json['id'] ?? '',
      universityName: json['university_name'] ?? '',
      majorName: json['major_name'] ?? '',
      probability: json['probability'] ?? 0,
      roiScore: json['roi_score'] ?? 0,
      roiLevel: json['roi_level'] ?? 'B级',
      tag: json['tag'] ?? '',
      universityType: json['university_type'] ?? '',
      city: json['city'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'university_name': universityName,
      'major_name': majorName,
      'probability': probability,
      'roi_score': roiScore,
      'roi_level': roiLevel,
      'tag': tag,
      'university_type': universityType,
      'city': city,
    };
  }
}

class PlanEvaluation {
  final int overallScore;
  final String riskLevel;
  final int chongCount;
  final int wenCount;
  final int baoCount;
  final List<Warning> warnings;
  final List<Suggestion> suggestions;
  final String evaluatedAt;

  PlanEvaluation({
    required this.overallScore,
    required this.riskLevel,
    required this.chongCount,
    required this.wenCount,
    required this.baoCount,
    required this.warnings,
    required this.suggestions,
    required this.evaluatedAt,
  });

  factory PlanEvaluation.fromJson(Map<String, dynamic> json) {
    return PlanEvaluation(
      overallScore: json['overall_score'] ?? 0,
      riskLevel: json['risk_level'] ?? 'low',
      chongCount: json['chong_count'] ?? 0,
      wenCount: json['wen_count'] ?? 0,
      baoCount: json['bao_count'] ?? 0,
      warnings: (json['warnings'] as List<dynamic>?)
              ?.map((e) => Warning.fromJson(e))
              .toList() ?? [],
      suggestions: (json['suggestions'] as List<dynamic>?)
                  ?.map((e) => Suggestion.fromJson(e))
                  .toList() ?? [],
      evaluatedAt: json['evaluated_at'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'overall_score': overallScore,
      'risk_level': riskLevel,
      'chong_count': chongCount,
      'wen_count': wenCount,
      'bao_count': baoCount,
      'warnings': warnings.map((w) => w.toJson()).toList(),
      'suggestions': suggestions.map((s) => s.toJson()).toList(),
      'evaluated_at': evaluatedAt,
    };
  }
}

class Warning {
  final String type;
  final String category;
  final String message;
  final String severity;

  Warning({
    required this.type,
    required this.category,
    required this.message,
    required this.severity,
  });

  factory Warning.fromJson(Map<String, dynamic> json) {
    return Warning(
      type: json['type'] ?? '',
      category: json['category'] ?? '',
      message: json['message'] ?? '',
      severity: json['severity'] ?? 'low',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'category': category,
      'message': message,
      'severity': severity,
    };
  }
}

class Suggestion {
  final String content;

  Suggestion({required this.content});

  factory Suggestion.fromJson(Map<String, dynamic> json) {
    return Suggestion(
      content: json['content'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'content': content,
    };
  }
}

enum RiskLevel { low, medium, high }
