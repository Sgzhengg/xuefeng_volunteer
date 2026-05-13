import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../core/api_service.dart';

/// 历史记录项模型
class HistoryItem {
  final String id;
  final int rank;
  final String province;
  final List<String> subjects;
  final String preference;
  final List<Map<String, dynamic>> resultsSummary;
  final int resultsCount;
  final String createdAt;

  HistoryItem({
    required this.id,
    required this.rank,
    required this.province,
    required this.subjects,
    required this.preference,
    required this.resultsSummary,
    required this.resultsCount,
    required this.createdAt,
  });

  factory HistoryItem.fromJson(Map<String, dynamic> json) {
    return HistoryItem(
      id: json['id']?.toString() ?? '',
      rank: json['rank'] ?? 0,
      province: json['province'] ?? '',
      subjects: (json['subjects'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ?? [],
      preference: json['preference'] ?? 'balanced',
      resultsSummary: (json['results_summary'] as List<dynamic>?)
              ?.map((e) => Map<String, dynamic>.from(e))
              .toList() ?? [],
      resultsCount: json['results_count'] ?? 0,
      createdAt: json['created_at'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'rank': rank,
      'province': province,
      'subjects': subjects,
      'preference': preference,
      'results_summary': resultsSummary,
      'results_count': resultsCount,
      'created_at': createdAt,
    };
  }
}

/// 历史详情模型
class HistoryDetail {
  final String id;
  final int rank;
  final String province;
  final List<String> subjects;
  final String preference;
  final List<Map<String, dynamic>> results;
  final int resultsCount;
  final String createdAt;

  HistoryDetail({
    required this.id,
    required this.rank,
    required this.province,
    required this.subjects,
    required this.preference,
    required this.results,
    required this.resultsCount,
    required this.createdAt,
  });

  factory HistoryDetail.fromJson(Map<String, dynamic> json) {
    return HistoryDetail(
      id: json['id']?.toString() ?? '',
      rank: json['rank'] ?? 0,
      province: json['province'] ?? '',
      subjects: (json['subjects'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ?? [],
      preference: json['preference'] ?? 'balanced',
      results: (json['results'] as List<dynamic>?)
              ?.map((e) => Map<String, dynamic>.from(e))
              .toList() ?? [],
      resultsCount: json['results_count'] ?? 0,
      createdAt: json['created_at'] ?? '',
    );
  }
}

/// 历史记录状态
class HistoryState {
  final List<HistoryItem> histories;
  final bool isLoading;
  final String? error;
  final int currentPage;
  final int totalPages;
  final int total;

  HistoryState({
    required this.histories,
    this.isLoading = false,
    this.error,
    this.currentPage = 1,
    this.totalPages = 1,
    this.total = 0,
  });

  HistoryState copyWith({
    List<HistoryItem>? histories,
    bool? isLoading,
    String? error,
    int? currentPage,
    int? totalPages,
    int? total,
  }) {
    return HistoryState(
      histories: histories ?? this.histories,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      currentPage: currentPage ?? this.currentPage,
      totalPages: totalPages ?? this.totalPages,
      total: total ?? this.total,
    );
  }
}

/// 历史记录状态管理
class HistoryNotifier extends StateNotifier<HistoryState> {
  HistoryNotifier() : super(HistoryState(histories: []));

  /// 构建带认证的请求头
  Map<String, String> _buildHeaders(String token) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };
    if (token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  /// 保存本次推荐结果
  Future<bool> saveHistory(
    String token,
    int rank,
    String province,
    List<String> subjects,
    String preference,
    List<Map<String, dynamic>> results,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiService.baseUrl}/history/save'),
        headers: _buildHeaders(token),
        body: jsonEncode({
          'rank': rank,
          'province': province,
          'subjects': subjects,
          'preference': preference,
          'results': results,
        }),
      );

      final result = jsonDecode(response.body);

      if (result['code'] == 0) {
        // 重新加载历史列表
        await loadHistories(token, 1);
        return true;
      }

      return false;
    } catch (e) {
      state = state.copyWith(error: e.toString());
      return false;
    }
  }

  /// 加载历史列表
  Future<void> loadHistories(String token, int page) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await http.get(
        Uri.parse('${ApiService.baseUrl}/history/list?page=$page&limit=10'),
        headers: _buildHeaders(token),
      );

      final result = jsonDecode(response.body);

      if (result['code'] == 0 && result['data'] != null) {
        final historiesData = result['data']['histories'] as List<dynamic>;
        final histories = historiesData
            .map((json) => HistoryItem.fromJson(json))
            .toList();

        final pagination = result['data']['pagination'] ?? {};

        state = state.copyWith(
          histories: page == 1 ? histories : [...state.histories, ...histories],
          isLoading: false,
          currentPage: page,
          totalPages: pagination['total_pages'] ?? 1,
          total: pagination['total'] ?? 0,
        );
      } else {
        state = state.copyWith(
          histories: [],
          isLoading: false,
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
        histories: [],
      );
    }
  }

  /// 获取历史详情
  Future<HistoryDetail?> getHistoryDetail(String token, String historyId) async {
    try {
      final response = await http.get(
        Uri.parse('${ApiService.baseUrl}/history/detail/$historyId'),
        headers: _buildHeaders(token),
      );

      final result = jsonDecode(response.body);

      if (result['code'] == 0 && result['data'] != null) {
        return HistoryDetail.fromJson(result['data']);
      }

      return null;
    } catch (e) {
      state = state.copyWith(error: e.toString());
      return null;
    }
  }

  /// 删除历史记录
  Future<bool> deleteHistory(String token, String historyId) async {
    try {
      final response = await http.delete(
        Uri.parse('${ApiService.baseUrl}/history/delete/$historyId'),
        headers: _buildHeaders(token),
      );

      final result = jsonDecode(response.body);

      if (result['code'] == 0) {
        // 从本地列表中移除
        final updatedHistories = state.histories.where((item) => item.id != historyId).toList();
        state = state.copyWith(
          histories: updatedHistories,
          total: state.total - 1,
        );
        return true;
      }

      return false;
    } catch (e) {
      state = state.copyWith(error: e.toString());
      return false;
    }
  }

  /// 加载更多
  Future<void> loadMore(String token) async {
    if (state.currentPage < state.totalPages) {
      await loadHistories(token, state.currentPage + 1);
    }
  }

  /// 刷新
  Future<void> refresh(String token) async {
    await loadHistories(token, 1);
  }

  /// 根据日期查找历史记录
  List<HistoryItem> getByDate(String date) {
    return state.histories.where((item) {
      return item.createdAt.startsWith(date);
    }).toList();
  }

  /// 搜索历史记录
  List<HistoryItem> searchHistories(String keyword) {
    if (keyword.isEmpty) {
      return state.histories;
    }

    final lowerKeyword = keyword.toLowerCase();
    return state.histories.where((item) {
      return item.province.toLowerCase().contains(lowerKeyword) ||
          item.preference.toLowerCase().contains(lowerKeyword) ||
          item.subjects.any((subject) => subject.toLowerCase().contains(lowerKeyword));
    }).toList();
  }
}

/// 历史记录Provider
final historyProvider = StateNotifierProvider<HistoryNotifier, HistoryState>((ref) {
  return HistoryNotifier();
});