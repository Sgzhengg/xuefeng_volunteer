// 暂时禁用 Isar 以支持 Web 平台
// import 'package:isar/isar.dart';
//
// part 'volunteer_scheme.g.dart';
//
// @Collection()

class VolunteerScheme {
  late String id;
  late String schemeId;
  late String userId;
  late String name;
  late List<SchoolChoice> choices;
  late String analysis;
  late int createdAt;

  // 便捷访问属性：按类型分组
  List<SchoolChoice> get chong => choices.where((c) => c.type == '冲').toList();
  List<SchoolChoice> get wen => choices.where((c) => c.type == '稳').toList();
  List<SchoolChoice> get bao => choices.where((c) => c.type == '保').toList();
  List<SchoolChoice> get dian => choices.where((c) => c.type == '垫').toList();

  VolunteerScheme();

  VolunteerScheme.create({
    required this.schemeId,
    required this.userId,
    required this.name,
    required this.choices,
    required this.analysis,
    required this.createdAt,
  });
}

// 暂时禁用 Isar 的 @embedded 注解以支持 Web 平台
// @embedded
class SchoolChoice {
  late String universityName;
  late String majorName;
  late String type; // '冲', '稳', '保', '垫'
  late double probability;
  late int score;
  late int ranking;

  SchoolChoice();

  SchoolChoice.create({
    required this.universityName,
    required this.majorName,
    required this.type,
    required this.probability,
    required this.score,
    required this.ranking,
  });
}
