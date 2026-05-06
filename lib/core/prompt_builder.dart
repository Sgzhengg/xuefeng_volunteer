import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'skill_loader.dart';
import 'models/user_profile.dart';
import 'models/gaokao_data_models.dart';
import 'models/gaokao_data_context.dart';

part 'prompt_builder.g.dart';

/// Prompt 构建器
@riverpod
class PromptBuilder extends _$PromptBuilder {
  @override
  void build() {}

  /// 构建完整的系统提示
  Future<String> buildSystemPrompt({
    required UserProfile? user,
    required String skillContent,
    Map<String, dynamic>? context,
  }) async {
    // 1. 获取基础 SKILL.md 内容
    final basePrompt = SkillLoader.getSystemPrompt(
      skillContent: skillContent,
      user: user,
    );

    // 2. 添加额外的上下文信息
    String additionalContext = '';

    if (context != null) {
      if (context.containsKey('currentDate')) {
        additionalContext += '\n\n## 当前时间\n${context['currentDate']}';
      }

      if (context.containsKey('availableTools')) {
        additionalContext += '\n\n## 可用工具\n${context['availableTools']}';
      }

      if (context.containsKey('dataSource')) {
        additionalContext += '\n\n## 数据来源\n${context['dataSource']}';
      }
    }

    // 3. 添加 App 级别的约束
    final appConstraints = '''

## App 使用指南
你现在是「学锋志愿教练」App 中的 AI 教练。
- 每次回答后，自动识别是否需要追问用户信息（分数、省份、选科等）
- 如果用户提到具体专业/院校，主动调用查询工具获取最新数据
- 保持张学锋式的表达风格，但适当降低攻击性，确保用户能接受
- 重要决策建议后，提醒用户查看数据来源和免责声明
''';

    return basePrompt + additionalContext + appConstraints;
  }

  /// 构建用户消息（添加元数据）
  String buildUserMessage({
    required String content,
    Map<String, dynamic>? metadata,
  }) {
    String message = content;

    if (metadata != null && metadata.isNotEmpty) {
      message += '\n\n[元数据信息]';
      metadata.forEach((key, value) {
        message += '\n- $key: $value';
      });
    }

    return message;
  }

  /// 构建带数据上下文的系统提示（用于 Tool Calling 后）
  Future<String> buildSystemPromptWithDataContext({
    required UserProfile? user,
    required String skillContent,
    required GaokaoDataContext dataContext,
    Map<String, dynamic>? additionalContext,
  }) async {
    // 1. 获取基础提示
    final basePrompt = await buildSystemPrompt(
      user: user,
      skillContent: skillContent,
      context: additionalContext,
    );

    // 2. 构建数据上下文摘要
    final dataContextSummary = _buildDataContextSummary(dataContext);

    // 3. 添加数据使用指南
    final dataUsageGuide = '''

## 📊 实时数据分析指南
你现在拥有了来自公开数据和历史录取信息的最新高考资料。请严格遵循 SKILL.md 中的分析框架：

**就业倒推法**：
- 使用录取概率数据时，看中等概率（40%-70%），不要只看高概率
- 结合专业就业数据，给出"5年后能赚多少"的明确判断

**中位数原则**：
- 引用薪资时用中位数，不是平均值
- 展示普通毕业生的真实去向

**500强测试**：
- 结合院校层次和就业数据，判断"企业去不去这个学校招聘"

**明确结论**：
- 基于数据给出明确建议（可以报/不建议/风险太大）
- 不要说"看个人情况"，直接说"我建议XXX"或"千万别XXX"

**数据来源标注**：
- 每次使用数据后，明确说："根据公开录取数据..."
- 最后必须加免责声明："最终志愿以省考试院官方公布为准"
''';

    return basePrompt + dataContextSummary + dataUsageGuide;
  }

  /// 构建数据上下文摘要
  String _buildDataContextSummary(GaokaoDataContext context) {
    final summary = StringBuffer();

    summary.write('\n\n## 📊 最新高考数据（公开录取数据）\n');

    // 录取概率数据
    if (context.admissionProbability != null) {
      final data = context.admissionProbability!;
      summary.write('### 录取概率预测\n');
      summary.write('- 院校：${data.universityName}（${data.level}）\n');
      summary.write('- 专业：${data.majorName}\n');
      summary.write('- 录取概率：${data.probability.toStringAsFixed(1)}%\n');
      summary.write('- 预测结论：${data.prediction}\n');
      if (data.suggestion != null) {
        summary.write('- 报考建议：${data.suggestion}\n');
      }
      summary.write('\n');
    }

    // 一分一段表
    if (context.onePointSegment != null) {
      final data = context.onePointSegment!;
      summary.write('### 一分一段表\n');
      summary.write('- 省份：${data.province}（${data.year}年）\n');
      // 从录取概率数据中获取分数，如果有的话
      final targetScore = context.admissionProbability?.score;
      if (targetScore != null) {
        final segment = data.segments.firstWhere(
          (s) => s.score == targetScore,
          orElse: () => ScoreSegment(score: targetScore, rank: 0, cumulative: 0),
        );
        summary.write('- ${targetScore}分对应位次：${segment.cumulative}\n');
      }
      summary.write('\n');
    }

    // 院校信息
    if (context.universityInfo != null) {
      final info = context.universityInfo!;
      summary.write('### 院校详情\n');
      summary.write('- ${info.name}（${info.level} / ${info.type}）\n');
      summary.write('- 位置：${info.province} ${info.city}\n');
      if (info.ranking2024 != null) {
        summary.write('- 2024排名：第${info.ranking2024}名\n');
      }
      if (info.minScore2024 != null) {
        summary.write('- 2024最低分：${info.minScore2024}分\n');
      }
      if (info.employmentRate != null) {
        summary.write('- 就业率：${(info.employmentRate! * 100).toStringAsFixed(1)}%\n');
      }
      if (info.avgSalary != null) {
        summary.write('- 平均薪资：${info.avgSalary!.toStringAsFixed(0)}元/月\n');
      }
      summary.write('\n');
    }

    // 省控线
    if (context.provincialControlLine != null) {
      final line = context.provincialControlLine!;
      summary.write('### ${line.province}省控线（${line.year}年）\n');
      if (line.scienceFirst != null) {
        summary.write('- 理科一本线：${line.scienceFirst}分\n');
      }
      if (line.scienceSecond != null) {
        summary.write('- 理科二本线：${line.scienceSecond}分\n');
      }
      if (line.artsFirst != null) {
        summary.write('- 文科一本线：${line.artsFirst}分\n');
      }
      if (line.artsSecond != null) {
        summary.write('- 文科二本线：${line.artsSecond}分\n');
      }
      if (line.comprehensiveFirst != null) {
        summary.write('- 综合一本线：${line.comprehensiveFirst}分\n');
      }
      summary.write('\n');
    }

    // 专业就业数据
    if (context.majorEmployment != null) {
      final employment = context.majorEmployment!;
      summary.write('### ${employment.majorName}就业数据\n');
      summary.write('- 就业率：${(employment.employmentRate * 100).toStringAsFixed(1)}%\n');
      summary.write('- 平均薪资：${employment.avgSalary.toStringAsFixed(0)}元/月\n');
      summary.write('- 薪资增长：${(employment.salaryGrowth * 100).toStringAsFixed(1)}%\n');
      summary.write('- 就业趋势：${employment.employmentTrend}\n');
      summary.write('- AI冲击程度：${employment.aiImpact}\n');
      summary.write('- 主要岗位：${employment.topPositions.join('、')}\n');
      summary.write('\n');
    }

    return summary.toString();
  }
}
