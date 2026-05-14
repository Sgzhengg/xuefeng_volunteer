import 'package:flutter/material.dart';

/// 学锋志愿教练应用主题
/// 基于 Stitch 设计系统的颜色和排版规范
class AppTheme {
  // ========== 颜色定义 ==========

  // 主色调
  static const Color primaryBlue = Color(0xFF1976D2);
  static const Color secondaryBlue = Color(0xFF2196F3);
  static const Color darkBlue = Color(0xFF005DAC);

  // 辅助色
  static const Color orange = Color(0xFFFF9800);
  static const Color green = Color(0xFF4CAF50);
  static const Color red = Color(0xFFF44336);

  // 中性色
  static const Color darkGray = Color(0xFF333333);
  static const Color mediumGray = Color(0xFF757575);
  static const Color lightGray = Color(0xFFF5F5F5);
  static const Color white = Color(0xFFFFFFFF);

  // 背景色
  static const Color surfaceColor = Color(0xFFF9F9FF);
  static const Color surfaceContainerLow = Color(0xFFF2F3FC);
  static const Color surfaceContainerHighest = Color(0xFFE0E2EA);
  static const Color surfaceContainerLowest = Color(0xFFFFFFFF);

  // 语义色
  static const Color warningBackground = Color(0xFFFFF3E0);
  static const Color warningBorder = Color(0xFFFFB74D);
  static const Color successBackground = Color(0xFFE8F5E9);
  static const Color successBorder = Color(0xFF4CAF50);
  static const Color errorBackground = Color(0xFFFFEBEE);
  static const Color errorBorder = Color(0xFFF44336);
  static const Color infoBackground = Color(0xFFE3F2FD);
  static const Color infoBorder = Color(0xFF1976D2);

  // ========== 文本样式 ==========

  static const TextStyle displayLarge = TextStyle(
    fontSize: 32,
    fontWeight: FontWeight.w700,
    height: 1.2,
    color: darkGray,
  );

  static const TextStyle headlineMedium = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.w600,
    height: 1.3,
    color: darkGray,
  );

  static const TextStyle titleLarge = TextStyle(
    fontSize: 22,
    fontWeight: FontWeight.w600,
    height: 1.3,
    color: darkGray,
  );

  static const TextStyle titleMedium = TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w600,
    height: 1.3,
    color: darkGray,
  );

  static const TextStyle titleSmall = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    height: 1.4,
    color: darkGray,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w400,
    height: 1.6,
    color: darkGray,
  );

  static const TextStyle bodySmall = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w400,
    height: 1.5,
    color: mediumGray,
  );

  static const TextStyle labelSmall = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w600,
    height: 1.0,
    letterSpacing: 0.05,
    color: mediumGray,
  );

  // ========== 间距系统 ==========

  static const double spacingXs = 4.0;
  static const double spacingSm = 8.0;
  static const double spacingMd = 16.0;
  static const double spacingLg = 24.0;
  static const double spacingXl = 32.0;

  // ========== 圆角 ==========

  static const double radiusSm = 4.0;
  static const double radiusMd = 8.0;
  static const double radiusLg = 12.0;
  static const double radiusXl = 16.0;
  static const double radiusFull = 9999.0;

  // ========== 阴影 ==========

  static List<BoxShadow> get shadowLight => [
    BoxShadow(
      color: Colors.black.withOpacity(0.1),
      offset: const Offset(0, 2),
      blurRadius: 5,
    ),
  ];

  static List<BoxShadow> get shadowMedium => [
    BoxShadow(
      color: Colors.black.withOpacity(0.15),
      offset: const Offset(0, 4),
      blurRadius: 12,
    ),
  ];

  static List<BoxShadow> get shadowHeavy => [
    BoxShadow(
      color: Colors.black.withOpacity(0.2),
      offset: const Offset(0, 8),
      blurRadius: 24,
    ),
  ];

  // ========== 主题数据 ==========

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryBlue,
        brightness: Brightness.light,
        primary: primaryBlue,
        secondary: secondaryBlue,
        surface: surfaceColor,
        error: red,
      ),

      // AppBar 主题
      appBarTheme: const AppBarTheme(
        backgroundColor: primaryBlue,
        foregroundColor: white,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w500,
          color: white,
        ),
      ),

      // 卡片主题
      cardTheme: const CardTheme(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(12)),
        ),
        color: white,
      ),

      // 输入框主题
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: white,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: spacingMd,
          vertical: 12,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          borderSide: const BorderSide(color: Color(0xFFE0E0E0)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          borderSide: const BorderSide(color: Color(0xFFE0E0E0)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          borderSide: const BorderSide(color: primaryBlue, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          borderSide: const BorderSide(color: red, width: 2),
        ),
      ),

      // 按钮主题
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryBlue,
          foregroundColor: white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(
            horizontal: spacingLg,
            vertical: 14,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(radiusMd),
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),

      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primaryBlue,
          side: const BorderSide(color: primaryBlue, width: 2),
          padding: const EdgeInsets.symmetric(
            horizontal: spacingLg,
            vertical: 12,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(radiusMd),
          ),
          textStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),

      // 底部导航栏主题
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: white,
        selectedItemColor: primaryBlue,
        unselectedItemColor: mediumGray,
        selectedLabelStyle: const TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
        unselectedLabelStyle: const TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w400,
        ),
        type: BottomNavigationBarType.fixed,
        elevation: 2,
      ),

      // 文本主题
      textTheme: const TextTheme(
        displayLarge: displayLarge,
        headlineMedium: headlineMedium,
        titleSmall: titleSmall,
        bodyMedium: bodyMedium,
        bodySmall: bodySmall,
        labelSmall: labelSmall,
      ),
    );
  }
}
