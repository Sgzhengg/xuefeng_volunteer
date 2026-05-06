import 'package:flutter/material.dart';

/// ChatGPT风格的配色方案
class ChatGPTTheme {
  // 主色调
  static const Color chatGPTGreen = Color(0xFF10a37f);
  static const Color chatGPTDarkGreen = Color(0xFF0d8a6a);

  // 浅色模式
  static const Color lightBackground = Color(0xFFFFFFFF);
  static const Color lightSurface = Color(0xFFF7F7F8);
  static const Color lightAIMessageBackground = Color(0xFFF7F7F8);
  static const Color lightUserMessageBackground = chatGPTGreen;
  static const Color lightTextPrimary = Color(0xFF2D333A);
  static const Color lightTextSecondary = Color(0xFF6E6E80);
  static const Color lightDivider = Color(0xFFE5E5E5);
  static const Color lightInputBackground = Color(0xFFFFFFFF);
  static const Color lightInputBorder = Color(0xFFD9D9E3);

  // 深色模式
  static const Color darkBackground = Color(0xFF343541);
  static const Color darkSurface = Color(0xFF444654);
  static const Color darkAIMessageBackground = Color(0xFF444654);
  static const Color darkUserMessageBackground = chatGPTGreen;
  static const Color darkTextPrimary = Color(0xFFECECF1);
  static const Color darkTextSecondary = Color(0xFF9B9B9B);
  static const Color darkDivider = Color(0xFF565869);
  static const Color darkInputBackground = Color(0xFF40414F);
  static const Color darkInputBorder = Color(0xFF565869);

  // 圆角
  static const double radiusSmall = 8.0;
  static const double radiusMedium = 12.0;
  static const double radiusLarge = 16.0;
  static const double radiusXLarge = 20.0;

  // 间距
  static const double paddingXSmall = 4.0;
  static const double paddingSmall = 8.0;
  static const double paddingMedium = 12.0;
  static const double paddingLarge = 16.0;
  static const double paddingXLarge = 20.0;

  // 阴影
  static List<BoxShadow> get lightShadow => [
        BoxShadow(
          color: Colors.black.withOpacity(0.05),
          blurRadius: 10,
          offset: const Offset(0, 2),
        ),
      ];

  static List<BoxShadow> get mediumShadow => [
        BoxShadow(
          color: Colors.black.withOpacity(0.1),
          blurRadius: 20,
          offset: const Offset(0, 4),
        ),
      ];

  /// 浅色模式主题
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      scaffoldBackgroundColor: lightBackground,
      colorScheme: const ColorScheme.light(
        primary: chatGPTGreen,
        secondary: chatGPTDarkGreen,
        surface: lightSurface,
        background: lightBackground,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: lightBackground,
        foregroundColor: lightTextPrimary,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: lightTextPrimary,
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
      ),
      textTheme: const TextTheme(
        bodyLarge: TextStyle(
          color: lightTextPrimary,
          fontSize: 16,
          height: 1.5,
        ),
        bodyMedium: TextStyle(
          color: lightTextPrimary,
          fontSize: 14,
          height: 1.5,
        ),
        bodySmall: TextStyle(
          color: lightTextSecondary,
          fontSize: 12,
          height: 1.4,
        ),
        titleMedium: TextStyle(
          color: lightTextPrimary,
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: lightDivider,
        thickness: 1,
      ),
    );
  }

  /// 深色模式主题
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: darkBackground,
      colorScheme: const ColorScheme.dark(
        primary: chatGPTGreen,
        secondary: chatGPTDarkGreen,
        surface: darkSurface,
        background: darkBackground,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: darkBackground,
        foregroundColor: darkTextPrimary,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: darkTextPrimary,
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
      ),
      textTheme: const TextTheme(
        bodyLarge: TextStyle(
          color: darkTextPrimary,
          fontSize: 16,
          height: 1.5,
        ),
        bodyMedium: TextStyle(
          color: darkTextPrimary,
          fontSize: 14,
          height: 1.5,
        ),
        bodySmall: TextStyle(
          color: darkTextSecondary,
          fontSize: 12,
          height: 1.4,
        ),
        titleMedium: TextStyle(
          color: darkTextPrimary,
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: darkDivider,
        thickness: 1,
      ),
    );
  }
}
