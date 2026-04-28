import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// "学锋老师"虚拟人头像组件
/// 显示中国男性教师形象，专业亲和
class MentorAvatar extends StatelessWidget {
  final double size;
  final VoidCallback? onTap;

  const MentorAvatar({
    super.key,
    this.size = 40,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          border: Border.all(
            color: AppTheme.surfaceContainerHighest,
            width: 2,
          ),
          boxShadow: AppTheme.shadowLight,
          color: AppTheme.infoBackground,
        ),
        child: ClipOval(
          child: _buildAvatarContent(),
        ),
      ),
    );
  }

  Widget _buildAvatarContent() {
    // 方案 1: 使用图标（如果没有图片资源）
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppTheme.infoBackground,
            AppTheme.white,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      child: Center(
        child: Icon(
          Icons.person,
          size: size * 0.6,
          color: AppTheme.primaryBlue,
        ),
      ),
    );

    // 方案 2: 如果有虚拟人图片资源，使用以下代码替代上面的返回
    // return Image.asset(
    //   'assets/images/mentor_avatar.png',
    //   fit: BoxFit.cover,
    //   errorBuilder: (context, error, stackTrace) {
    //     // 图片加载失败时显示图标
    //     return Container(
    //       decoration: const BoxDecoration(
    //         gradient: LinearGradient(
    //           colors: [
    //             AppTheme.infoBackground,
    //             AppTheme.white,
    //           ],
    //           begin: Alignment.topLeft,
    //           end: Alignment.bottomRight,
    //         ),
    //       ),
    //       child: Center(
    //         child: Icon(
    //           Icons.person,
    //           size: size * 0.6,
    //           color: AppTheme.primaryBlue,
    //         ),
    //       ),
    //     );
    //   },
    // );

    // 方案 3: 如果使用网络图片，使用以下代码
    // return Image.network(
    //   'https://example.com/mentor_avatar.png',
    //   fit: BoxFit.cover,
    //   loadingBuilder: (context, child, loadingProgress) {
    //     if (loadingProgress == null) return child;
    //     return Center(
    //       child: CircularProgressIndicator(
    //         value: loadingProgress.expectedTotalBytes != null
    //             ? loadingProgress.cumulativeBytesLoaded /
    //                 loadingProgress.expectedTotalBytes!
    //             : null,
    //       ),
    //     );
    //   },
    //   errorBuilder: (context, error, stackTrace) {
    //     return Container(
    //       decoration: const BoxDecoration(
    //         gradient: LinearGradient(
    //           colors: [
    //             AppTheme.infoBackground,
    //             AppTheme.white,
    //           ],
    //           begin: Alignment.topLeft,
    //           end: Alignment.bottomRight,
    //         ),
    //       ),
    //       child: Center(
    //         child: Icon(
    //           Icons.person,
    //           size: size * 0.6,
    //           color: AppTheme.primaryBlue,
    //         ),
    //       ),
    //     );
    //   },
    // );
  }
}

/// 虚拟人头像卡片（带名字标签）
class MentorAvatarWithName extends StatelessWidget {
  final String name;
  final double avatarSize;
  final VoidCallback? onTap;

  const MentorAvatarWithName({
    super.key,
    this.name = '学锋老师',
    this.avatarSize = 40,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        MentorAvatar(
          size: avatarSize,
          onTap: onTap,
        ),
        const SizedBox(height: AppTheme.spacingXs),
        Text(
          name,
          style: AppTheme.labelSmall.copyWith(
            color: AppTheme.mediumGray,
          ),
        ),
      ],
    );
  }
}
