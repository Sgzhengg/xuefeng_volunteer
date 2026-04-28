import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'models/gaokao_data_models.dart';

part 'gaokao_data_service.g.dart';

/// 本地后端 API 配置
class LocalAPIConfig {
  static const String baseUrl = 'http://localhost:8000/api/v1';

  /// 超时配置
  static const Duration connectTimeout = Duration(seconds: 10);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const int maxRetries = 3;
}

/// 高考数据服务（使用本地后端数据库）
@riverpod
class GaokaoDataService extends _$GaokaoDataService {
  late Dio _dio;

  @override
  void build() {
    _dio = Dio(
      BaseOptions(
        baseUrl: LocalAPIConfig.baseUrl,
        connectTimeout: LocalAPIConfig.connectTimeout,
        receiveTimeout: LocalAPIConfig.receiveTimeout,
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'XuefengCoach/1.0.0',
        },
      ),
    );

    // 添加拦截器
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          return handler.next(options);
        },
        onError: (error, handler) {
          return handler.next(error);
        },
      ),
    );
  }

  /// 查询录取概率
  ///
  /// 参数:
  /// - province: 省份名称（如 "北京"）
  /// - score: 高考分数
  /// - rank: 位次（可选）
  /// - subjectType: 科类（"理科"/"文科"/"综合"）
  /// - universityName: 院校名称（可选，为空则查询整体概率）
  /// - majorName: 专业名称（可选）
  Future<AdmissionProbabilityResponse> queryAdmissionProbability({
    required String province,
    required int score,
    int? rank,
    required String subjectType,
    String? universityName,
    String? majorName,
  }) async {
    try {
      final response = await _dio.post(
        '/gaokao/admission-probability',
        data: {
          'province': province,
          'score': score,
          if (rank != null) 'rank': rank,
          'subject_type': subjectType,
          if (universityName != null) 'university_name': universityName,
          if (majorName != null) 'major_name': majorName,
        },
      );

      return AdmissionProbabilityResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e, '查询录取概率失败');
    }
  }

  /// 查询一分一段表
  ///
  /// 参数:
  /// - province: 省份名称
  /// - year: 年份（如 2025）
  /// - score: 分数（可选，为空则返回完整表格）
  Future<OnePointSegmentResponse> queryOnePointSegment({
    required String province,
    required int year,
    int? score,
  }) async {
    try {
      final response = await _dio.get(
        '/gaokao/segment',
        queryParameters: {
          'province': province,
          'year': year,
          if (score != null) 'score': score,
        },
      );

      return OnePointSegmentResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e, '查询一分一段表失败');
    }
  }

  /// 查询院校信息
  ///
  /// 参数:
  /// - universityName: 院校名称（支持模糊搜索）
  Future<UniversityInfoResponse> queryUniversityInfo({
    required String universityName,
  }) async {
    try {
      final response = await _dio.get(
        '/gaokao/university/$universityName',
      );

      return UniversityInfoResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e, '查询院校信息失败');
    }
  }

  /// 查询省控线
  ///
  /// 参数:
  /// - province: 省份名称
  /// - year: 年份（如 2025）
  Future<ProvincialControlLineResponse> queryProvincialControlLine({
    required String province,
    required int year,
  }) async {
    try {
      final response = await _dio.get(
        '/gaokao/control-line',
        queryParameters: {
          'province': province,
          'year': year,
        },
      );

      return ProvincialControlLineResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e, '查询省控线失败');
    }
  }

  /// 查询专业就业数据
  ///
  /// 参数:
  /// - majorName: 专业名称
  Future<MajorEmploymentDataResponse> queryMajorEmploymentData({
    required String majorName,
  }) async {
    try {
      final response = await _dio.get(
        '/gaokao/major-employment/$majorName',
      );

      return MajorEmploymentDataResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e, '查询专业就业数据失败');
    }
  }

  /// 错误处理
  Exception _handleError(DioException error, String message) {
    String errorMessage = message;

    if (error.response != null) {
      try {
        final errorData = error.response?.data;
        if (errorData is Map && errorData.containsKey('detail')) {
          errorMessage = errorData['detail'];
        }
      } catch (_) {
        // 忽略解析错误
      }
    } else if (error.type == DioExceptionType.connectionTimeout) {
      errorMessage = '连接超时，请检查网络';
    } else if (error.type == DioExceptionType.receiveTimeout) {
      errorMessage = '响应超时，请稍后重试';
    } else if (error.type == DioExceptionType.connectionError) {
      errorMessage = '无法连接到服务器，请确保后端服务正在运行';
    }

    return Exception(errorMessage);
  }
}
