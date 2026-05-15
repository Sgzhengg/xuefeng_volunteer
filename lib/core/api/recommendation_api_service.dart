import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../../config/app_config.dart';

/// 推荐API服务
class RecommendationApiService {
  final Dio _dio;
  static String get _baseUrl => AppConfig.apiBaseUrl;

  RecommendationApiService({Dio? dio})
      : _dio = dio ?? Dio(BaseOptions(
          baseUrl: _baseUrl,
          connectTimeout: const Duration(seconds: 30),
          receiveTimeout: const Duration(seconds: 30),
          headers: {
            'Content-Type': 'application/json',
          },
        ));

  /// 生成智能推荐方案
  Future<Map<String, dynamic>> generateRecommendation({
    required String province,
    required int score,
    String subjectType = '理科',
    List<String>? targetMajors,
    int? rank,
    Map<String, dynamic>? preferences,
  }) async {
    try {
      final response = await _dio.post(
        '/recommendation/generate',
        data: {
          'province': province,
          'score': score,
          'subject_type': subjectType,
          'target_majors': targetMajors,
          'rank': rank,
          'preferences': preferences,
        },
      );

      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      } else {
        throw Exception('推荐失败: ${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (kDebugMode) {
        print('推荐API错误: ${e.message}');
        print('错误类型: ${e.type}');
        print('错误响应: ${e.response}');
      }

      // 不再返回模拟数据，直接抛出异常
      throw Exception('API连接失败: ${e.message}');
    } catch (e) {
      if (kDebugMode) {
        print('未知错误: $e');
      }
      rethrow;
    }
  }

  /// 根据分数推荐专业
  Future<Map<String, dynamic>> suggestMajors({
    required int score,
    String subjectType = '理科',
  }) async {
    try {
      final response = await _dio.get(
        '/recommendation/majors/suggest',
        queryParameters: {
          'score': score,
          'subject_type': subjectType,
        },
      );

      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      } else {
        throw Exception('专业推荐失败: ${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (kDebugMode) {
        print('专业推荐API错误: ${e.message}');
      }
      // 不再返回模拟数据，直接抛出异常
      throw Exception('API连接失败: ${e.message}');
    } catch (e) {
      rethrow;
    }
  }

  /// 计算位次
  Future<Map<String, dynamic>> calculateRank({
    required String province,
    required int score,
  }) async {
    try {
      final response = await _dio.get(
        '/recommendation/rank/calculate',
        queryParameters: {
          'province': province,
          'score': score,
        },
      );

      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      } else {
        throw Exception('位次计算失败: ${response.statusMessage}');
      }
    } on DioException catch (e) {
      if (kDebugMode) {
        print('位次计算API错误: ${e.message}');
      }
      // 不再返回模拟数据，直接抛出异常
      throw Exception('API连接失败: ${e.message}');
    } catch (e) {
      rethrow;
    }
  }
}