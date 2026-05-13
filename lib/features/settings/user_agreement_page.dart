import 'package:flutter/material.dart';
import '../../shared/theme/app_theme.dart';

class UserAgreementPage extends StatelessWidget {
  const UserAgreementPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surfaceColor,
      appBar: AppBar(
        title: const Text('用户协议'),
        backgroundColor: AppTheme.primaryBlue,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(AppTheme.spacingMd),
        children: [
          // 欢迎语
          Container(
            padding: const EdgeInsets.all(AppTheme.spacingLg),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [AppTheme.primaryBlue, AppTheme.secondaryBlue],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(AppTheme.radiusLg),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '欢迎使用学锋志愿教练',
                  style: AppTheme.titleLarge.copyWith(
                    color: AppTheme.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: AppTheme.spacingSm),
                Text(
                  '请仔细阅读以下用户协议，使用本应用即表示您同意本协议的全部内容。',
                  style: AppTheme.bodyMedium.copyWith(
                    color: AppTheme.white,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 协议接受
          _buildSectionCard(
            '✅ 协议接受',
            [
              _buildParagraph(
                '您在使用学锋志愿教练（以下简称"本应用"）之前，应当仔细阅读并充分理解本协议的各项条款。'
                '如果您不同意本协议的任何内容，请立即停止使用。您的使用行为将被视为对本协议的完全接受。',
              ),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 服务内容
          _buildSectionCard(
            '📱 服务内容',
            [
              _buildBulletText('高考志愿填报智能推荐'),
              _buildBulletText('院校和专业信息查询'),
              _buildBulletText('历年录取数据参考'),
              _buildBulletText('个人档案和历史记录管理'),
              _buildBulletText('院校收藏和志愿表功能'),
              _buildBulletText('AI智能问答服务'),
              _buildParagraph(
                '本应用保留随时修改、中断或终止部分或全部服务的权利，无需对用户或第三方负责。',
              ),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 用户义务
          _buildSectionCard(
            '👤 用户义务',
            [
              _buildBulletText('提供真实、准确的个人信息'),
              _buildBulletText('妥善保管账户信息和密码'),
              _buildBulletText('不得利用本应用从事违法活动'),
              _buildBulletText('不得干扰或破坏本应用的正常运行'),
              _buildBulletText('不得侵犯他人合法权益'),
              _buildBulletText('遵守相关法律法规和政策规定'),
              _buildParagraph(
                '如违反上述义务，本应用有权暂停或终止服务，并保留追究法律责任的权利。',
              ),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 知识产权
          _buildSectionCard(
            '©️ 知识产权',
            [
              _buildParagraph(
                '本应用的所有内容，包括但不限于文字、图片、音频、视频、软件、程序、版面设计等，'
                '均受著作权法、商标法、专利法等法律保护。',
              ),
              _buildBulletText('未经授权，不得复制、传播、展示、镜像、上载、下载本应用内容'),
              _buildBulletText('尊重第三方知识产权，引用时注明来源'),
              _buildBulletText('用户上传的内容仍归用户所有，但授予本应用使用权'),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 免责声明（重要）
          Container(
            padding: const EdgeInsets.all(AppTheme.spacingLg),
            decoration: BoxDecoration(
              color: AppTheme.errorBackground,
              borderRadius: BorderRadius.circular(AppTheme.radiusLg),
              border: Border.all(
                color: AppTheme.errorBorder,
                width: 2,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.warning_amber, color: AppTheme.red, size: 28),
                    const SizedBox(width: AppTheme.spacingXs),
                    Text(
                      '⚠️ 重要免责声明',
                      style: AppTheme.titleMedium.copyWith(
                        color: AppTheme.red,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppTheme.spacingMd),
                _buildWarningText(
                  '本应用提供的数据和推荐结果仅供参考，不作为正式报考依据。'
                  '实际录取结果以各省教育考试院和高校官方公布为准。',
                ),
                _buildWarningText(
                  '因数据延迟、计算误差、政策调整等因素导致的偏差，本应用不承担责任。',
                ),
                _buildWarningText(
                  '用户基于本应用信息做出的决策，后果由用户自行承担。',
                ),
                _buildWarningText(
                  '本应用不保证服务不中断或完全安全，可能因技术故障、维护等原因暂停服务。',
                ),
                _buildWarningText(
                  '因不可抗力、网络故障、第三方原因等导致的服务中断或数据丢失，本应用不承担责任。',
                ),
              ],
            ),
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 服务变更
          _buildSectionCard(
            '📝 服务变更、中断或终止',
            [
              _buildParagraph(
                '本应用有权根据业务发展需要，变更、中断或终止部分或全部服务，'
                '且无需对用户或第三方承担任何责任。',
              ),
              _buildSubSection('可能的情况', [
                '系统维护和升级',
                '技术故障和修复',
                '业务策略调整',
                '法律法规要求',
                '不可抗力因素',
              ]),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 争议解决
          _buildSectionCard(
            '⚖️ 争议解决',
            [
              _buildParagraph(
                '本协议之订立、生效、解释、修订、补充、终止、执行与争议解决均适用中华人民共和国法律。',
              ),
              _buildBulletText('协商解决：优先通过友好协商解决争议'),
              _buildBulletText('诉讼管辖：协商不成的，向本应用所在地人民法院起诉'),
              _buildParagraph(
                '在争议处理期间，除涉及争议部分外，本协议其他条款继续有效。',
              ),
            ],
          ),

          const SizedBox(height: AppTheme.spacingMd),

          // 其他条款
          _buildSectionCard(
            '📋 其他条款',
            [
              _buildBulletText(
                '本协议构成用户与本应用之间关于使用本应用的完整协议，取代之前的口头或书面协议。',
              ),
              _buildBulletText(
                '本应用未行使本协议项下的权利，不应视为对该权利的放弃。',
              ),
              _buildBulletText(
                '如本协议的任何条款被认定为无效或不可执行，不影响其他条款的效力。',
              ),
              _buildBulletText(
                '本应用有权根据需要修改本协议，修改后的协议在应用内公布后生效。',
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

          // 生效信息
          Container(
            padding: const EdgeInsets.all(AppTheme.spacingLg),
            decoration: BoxDecoration(
              color: AppTheme.surfaceContainerLow,
              borderRadius: BorderRadius.circular(AppTheme.radiusMd),
            ),
            child: Column(
              children: [
                Text(
                  '本用户协议最后更新日期：2025年1月9日',
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.mediumGray,
                  ),
                ),
                const SizedBox(height: AppTheme.spacingXs),
                Text(
                  '继续使用本应用即表示您接受本协议的全部内容',
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.primaryBlue,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
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

  /// 构建警告文本
  Widget _buildWarningText(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppTheme.spacingSm),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('🚫 ', style: TextStyle(fontSize: 16)),
          Expanded(
            child: Text(
              text,
              style: AppTheme.bodyMedium.copyWith(
                color: AppTheme.red,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// 构建子章节
  Widget _buildSubSection(String title, List<String> items) {
    return Container(
      margin: const EdgeInsets.only(bottom: AppTheme.spacingSm),
      padding: const EdgeInsets.all(AppTheme.spacingMd),
      decoration: BoxDecoration(
        color: AppTheme.surfaceContainerLow,
        borderRadius: BorderRadius.circular(AppTheme.radiusMd),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: AppTheme.titleSmall.copyWith(
              fontWeight: FontWeight.bold,
              color: AppTheme.darkGray,
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