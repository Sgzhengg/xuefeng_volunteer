import 'package:flutter/services.dart';
// 暂时禁用 Isar 以支持 Web 平台
// import 'package:isar/isar.dart';
import 'models/user_profile.dart';

// part 'skill_loader.g.dart';
//
// @Collection()

class SkillContent {
  late String id;
  late String name;
  late String content;
  late int loadedAt;

  SkillContent();
}

class SkillLoader {
  static const String _skillPath = 'assets/skill/SKILL.md';
  static SkillContent? _cachedSkill;

  /// 加载 SKILL.md（优先从内存缓存，否则从 Assets）
  static Future<SkillContent> loadSkill() async {
    // 1. 检查内存缓存
    if (_cachedSkill != null) {
      return _cachedSkill!;
    }

    // 2. 从 Assets 加载
    final content = await rootBundle.loadString(_skillPath);

    final skill = SkillContent()
      ..id = DateTime.now().millisecondsSinceEpoch.toString()
      ..name = 'zhangxuefeng-perspective'
      ..content = content
      ..loadedAt = DateTime.now().millisecondsSinceEpoch;

    // 3. 保存到内存缓存
    _cachedSkill = skill;
    return skill;
  }

  /// 获取用于 LLM 的完整系统提示
  static String getSystemPrompt({
    required String skillContent,
    UserProfile? user,
  }) {
    final basePrompt = skillContent;

    // 如果有用户信息，动态注入
    if (user != null) {
      final userContext = '''

## 当前用户信息
- 分数：${user.score}分（${user.province}）
- 选科：${user.selectedSubjects.join('、')}
- 家庭背景：${user.familyBackground}
- 兴趣方向：${user.interests.join('、')}
- 特殊情况：${user.specialSituation ?? '无'}
''';
      return basePrompt + userContext;
    }

    return basePrompt;
  }

  /// 清除缓存（强制重新加载）
  static void clearCache() {
    _cachedSkill = null;
  }
}
