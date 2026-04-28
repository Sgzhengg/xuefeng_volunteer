// 暂时禁用 Isar 以支持 Web 平台
// import 'package:isar/isar.dart';
//
// part 'user_profile.g.dart';
//
// @Collection()

class UserProfile {
  late String id;
  late String userId;
  late String name;
  late int score;
  late String province;
  late List<String> selectedSubjects;
  late String familyBackground; // '普通家庭', '富裕家庭', etc.
  late List<String> interests;
  String? specialSituation;
  late int createdAt;
  late int updatedAt;

  UserProfile();

  UserProfile.create({
    required this.userId,
    required this.name,
    required this.score,
    required this.province,
    required this.selectedSubjects,
    required this.familyBackground,
    required this.interests,
    this.specialSituation,
    required this.createdAt,
    required this.updatedAt,
  });
}
