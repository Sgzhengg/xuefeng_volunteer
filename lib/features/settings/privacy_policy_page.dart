import 'package:flutter/material.dart';
import '../../shared/theme/app_theme.dart';

class PrivacyPolicyPage extends StatelessWidget {
  const PrivacyPolicyPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surfaceColor,
      appBar: AppBar(
        title: const Text('隐私政策'),
        backgroundColor: AppTheme.primaryBlue,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(AppTheme.spacingMd),
        children: [
          // 引言
          _buildSectionCard(
            '📋 引言',
            [
              _buildParagraph(
                '欢迎使用学锋志愿教练！我们非常重视用户的隐私保护和个人信息保护。'
                '本隐私政策将帮助您了解我们收集、使用、存储和保护您个人信息的方式。',
              ),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 信息收集
          _buildSectionCard(
            '🔍 我们收集的信息',
            [
              _buildSubSection('账户信息', [
                '手机号码：用于账户注册和身份验证',
                '验证码：用于登录验证和安全保护',
              ]),
              _buildSubSection('高考信息', [
                '高考分数：用于推荐合适院校和专业',
                '全省位次：用于计算录取概率',
                '选科科目：用于匹配专业要求',
                '所在省份：用于匹配本省录取数据',
              ]),
              _buildSubSection('使用信息', [
                '浏览记录：用于优化推荐算法',
                '搜索历史：用于快速访问常用功能',
                '操作日志：用于问题排查和服务改进',
              ]),
              _buildSubSection('设备信息', [
                '设备型号：用于适配界面显示',
                '操作系统：用于功能兼容性判断',
                '网络状态：用于优化加载策略',
              ]),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 信息使用
          _buildSectionCard(
            '🎯 信息使用目的',
            [
              _buildBulletText('提供核心功能：分数查询、院校推荐、志愿填报'),
              _buildBulletText('个性化服务：基于用户情况定制推荐策略'),
              _buildBulletText('安全保护：账户安全、交易安全、风险防控'),
              _buildBulletText('服务改进：分析用户行为，优化产品体验'),
              _buildBulletText('联系客服：问题咨询、售后服务、投诉处理'),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 信息保护
          _buildSectionCard(
            '🔒 信息保护措施',
            [
              _buildSubSection('技术保护', [
                '数据加密：传输和存储均采用加密技术',
                '访问控制：严格的权限管理和身份验证',
                '安全审计：定期安全检查和漏洞修复',
                '备份机制：数据定期备份和容灾恢复',
              ]),
              _buildSubSection('管理保护', [
                '权限最小化：仅授予必要的访问权限',
                '保密协议：员工签署保密协议',
                '安全培训：定期隐私保护培训',
                '违规处理：建立违规举报和处理机制',
              ]),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 信息共享
          _buildSectionCard(
            '🤝 信息共享说明',
            [
              _buildParagraph(
                '我们承诺不会向第三方出售您的个人信息。仅在以下情况下可能共享：',
              ),
              _buildBulletText('获得用户明确同意'),
              _buildBulletText('法律法规要求或政府机关依法调取'),
              _buildBulletText('维护用户合法权益或社会公共利益'),
              _buildBulletText('与关联公司或合作伙伴共享（仅限必要范围）'),
              _buildParagraph(
                '与第三方合作时，我们将要求其遵守本隐私政策，并采取安全措施保护您的信息。',
              ),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 用户权利
          _buildSectionCard(
            '✊ 您的权利',
            [
              _buildBulletText('访问权：查看我们收集的您的个人信息'),
              _buildBulletText('更正权：要求更正不准确的个人信息'),
              _buildBulletText('删除权：要求删除您的个人信息'),
              _buildBulletText('撤回同意：撤回之前给予的同意'),
              _buildBulletText('注销账户：删除账户及相关信息'),
              _buildBulletText('投诉举报：向监管部门投诉举报'),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 未成年保护
          _buildSectionCard(
            '👶 未成年人保护',
            [
              _buildParagraph(
                '我们的服务主要面向高中阶段学生。如果您是未成年人，请在监护人的指导下使用我们的服务。'
                '如果您是未成年人的监护人，请联系我们了解未成年人的信息使用情况。',
              ),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 政策更新
          _buildSectionCard(
            '📝 政策更新',
            [
              _buildParagraph(
                '我们可能不时修订本隐私政策。修订后的政策将在应用内公布，重大变更将通过显著方式通知您。'
                '继续使用服务即表示您接受修订后的隐私政策。',
              ),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 联系方式
          _buildSectionCard(
            '📞 联系我们',
            [
              _buildBulletText('客服邮箱：support@xuefeng.com'),
              _buildBulletText('联系电话：400-123-4567'),
              _buildBulletText('工作时间：周一至周日 9:00-21:00'),
              _buildBulletText('地址：广东省广州市某某区某某大厦'),
            ],
          ),

          const SizedBox(height: AppTheme.spacingLg),

          // 生效日期
          Center(
            child: Text(
              '本隐私政策最后更新日期：2025年1月9日',
              style: AppTheme.bodySmall.copyWith(
                color: AppTheme.mediumGray,
              ),
            ),
          ),

          const SizedBox(height: AppTheme.spacingMd),
        ],
      ),
    );
  }

  /// 构建分组卡片
  Widget _buildSectionCard(String title, List<Widget> children) {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingLg),
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.radiusLg),
        border: Border.all(
          color: AppTheme.surfaceContainerHighest,
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: AppTheme.titleMedium.copyWith(
              fontWeight: FontWeight.bold,
              color: AppTheme.primaryBlue,
            ),
          ),
          const SizedBox(height: AppTheme.spacingSm),
          ...children,
        ],
      ),
    );
  }

  /// 构建段落文本
  Widget _buildParagraph(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppTheme.spacingSm),
      child: Text(
        text,
        style: AppTheme.bodyMedium,
      ),
    );
  }

  /// 构建子章节
  Widget _buildSubSection(String title, List<String> items) {
    return Container(
      margin: const EdgeInsets.only(bottom: AppTheme.spacingSm),
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      decoration: BoxDecoration(
        color: AppTheme.infoBackground,
        borderRadius: BorderRadius.circular(AppTheme.radiusMd),
        border: Border.all(
          color: AppTheme.infoBorder,
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: AppTheme.titleSmall.copyWith(
              fontWeight: FontWeight.bold,
              color: AppTheme.primaryBlue,
            ),
          ),
          const SizedBox(height: AppTheme.spacingXs),
          ...items.map((item) => Padding(
                padding: const EdgeInsets.only(left: AppTheme.spacingSm, bottom: 2),
                child: Text(
                  '• $item',
                  style: AppTheme.bodySmall,
                ),
              )),
        ],
      ),
    );
  }

  /// 构建列表项文本
  Widget _buildBulletText(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppTheme.spacingXs),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            margin: const EdgeInsets.only(top: 6),
            width: 6,
            height: 6,
            decoration: const BoxDecoration(
              color: AppTheme.primaryBlue,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: AppTheme.spacingSm),
          Expanded(
            child: Text(
              text,
              style: AppTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }
}