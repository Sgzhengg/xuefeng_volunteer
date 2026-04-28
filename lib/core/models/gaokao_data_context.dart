import 'gaokao_data_models.dart';

/// 高考数据上下文（用于注入 Prompt）
class GaokaoDataContext {
  final AdmissionProbabilityData? admissionProbability;
  final OnePointSegmentData? onePointSegment;
  final UniversityInfoData? universityInfo;
  final ProvincialControlLineData? provincialControlLine;
  final MajorEmploymentData? majorEmployment;

  GaokaoDataContext({
    this.admissionProbability,
    this.onePointSegment,
    this.universityInfo,
    this.provincialControlLine,
    this.majorEmployment,
  });

  /// 是否有任何数据
  bool get hasData =>
      admissionProbability != null ||
      onePointSegment != null ||
      universityInfo != null ||
      provincialControlLine != null ||
      majorEmployment != null;

  /// 清空所有数据
  GaokaoDataContext copyWithEmpty() {
    return GaokaoDataContext();
  }

  /// 添加录取概率数据
  GaokaoDataContext copyWithAdmissionProbability(AdmissionProbabilityData data) {
    return GaokaoDataContext(
      admissionProbability: data,
      onePointSegment: onePointSegment,
      universityInfo: universityInfo,
      provincialControlLine: provincialControlLine,
      majorEmployment: majorEmployment,
    );
  }

  /// 添加一分一段表
  GaokaoDataContext copyWithOnePointSegment(OnePointSegmentData data) {
    return GaokaoDataContext(
      admissionProbability: admissionProbability,
      onePointSegment: data,
      universityInfo: universityInfo,
      provincialControlLine: provincialControlLine,
      majorEmployment: majorEmployment,
    );
  }

  /// 添加院校信息
  GaokaoDataContext copyWithUniversityInfo(UniversityInfoData info) {
    return GaokaoDataContext(
      admissionProbability: admissionProbability,
      onePointSegment: onePointSegment,
      universityInfo: info,
      provincialControlLine: provincialControlLine,
      majorEmployment: majorEmployment,
    );
  }

  /// 添加省控线
  GaokaoDataContext copyWithProvincialControlLine(ProvincialControlLineData line) {
    return GaokaoDataContext(
      admissionProbability: admissionProbability,
      onePointSegment: onePointSegment,
      universityInfo: universityInfo,
      provincialControlLine: line,
      majorEmployment: majorEmployment,
    );
  }

  /// 添加专业就业数据
  GaokaoDataContext copyWithMajorEmployment(MajorEmploymentData data) {
    return GaokaoDataContext(
      admissionProbability: admissionProbability,
      onePointSegment: onePointSegment,
      universityInfo: universityInfo,
      provincialControlLine: provincialControlLine,
      majorEmployment: data,
    );
  }
}
