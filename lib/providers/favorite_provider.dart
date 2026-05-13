import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../core/api_service.dart';

/// 收藏项模型
class FavoriteItem {
  final String id;
  final int? universityId;
  final int? majorId;
  final String universityName;
  final String majorName;
  final String createdAt;

  FavoriteItem({
    required this.id,
    this.universityId,
    this.majorId,
    required this.universityName,
    required this.majorName,
    required this.createdAt,
  });

  factory FavoriteItem.fromJson(Map<String, dynamic> json) {
    return FavoriteItem(
      id: json['id']?.toString() ?? '',
      universityId: json['university_id'],
      majorId: json['major_id'],
      universityName: json['university_name'] ?? '',
      majorName: json['major_name'] ?? '',
      createdAt: json['created_at'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'university_id': universityId,
      'major_id': majorId,
      'university_name': universityName,
      'major_name': majorName,
      'created_at': createdAt,
    };
  }
}

/// 收藏状态
class FavoriteState {
  final List<FavoriteItem> favorites;
  final Map<String, bool> favoriteStatus; // 缓存收藏状态 {itemId: isFavorited}
  final bool isLoading;
  final String? error;

  FavoriteState({
    required this.favorites,
    this.favoriteStatus = const {},
    this.isLoading = false,
    this.error,
  });

  FavoriteState copyWith({
    List<FavoriteItem>? favorites,
    Map<String, bool>? favoriteStatus,
    bool? isLoading,
    String? error,
  }) {
    return FavoriteState(
      favorites: favorites ?? this.favorites,
      favoriteStatus: favoriteStatus ?? this.favoriteStatus,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

/// 收藏状态管理
class FavoriteNotifier extends StateNotifier<FavoriteState> {
  FavoriteNotifier() : super(FavoriteState(favorites: []));

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

  /// 加载收藏列表
  Future<void> loadFavorites(String token) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await http.get(
        Uri.parse('${ApiService.baseUrl}/favorite/list'),
        headers: _buildHeaders(token),
      );

      final result = jsonDecode(response.body);

      if (result['code'] == 0 && result['data'] != null) {
        final favoritesData = result['data']['favorites'] as List<dynamic>;
        final favorites = favoritesData
            .map((json) => FavoriteItem.fromJson(json))
            .toList();

        // 更新收藏状态缓存
        final statusMap = <String, bool>{};
        for (var item in favorites) {
          statusMap[item.id] = true;
        }

        state = state.copyWith(
          favorites: favorites,
          favoriteStatus: statusMap,
          isLoading: false,
        );
      } else {
        state = state.copyWith(
          favorites: [],
          isLoading: false,
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
        favorites: [],
      );
    }
  }

  /// 添加收藏
  Future<bool> addFavorite(String token, Map<String, dynamic> favoriteData) async {
    try {
      final itemId = '${favoriteData['university_id']}_${favoriteData['major_id']}';

      // 调用API添加收藏
      final response = await http.post(
        Uri.parse('${ApiService.baseUrl}/favorite/add'),
        headers: _buildHeaders(token),
        body: jsonEncode(favoriteData),
      );

      final result = jsonDecode(response.body);

      if (result['code'] == 0) {
        // 更新本地状态
        final newFavorite = FavoriteItem(
          id: itemId,
          universityId: favoriteData['university_id'],
          majorId: favoriteData['major_id'],
          universityName: favoriteData['university_name'],
          majorName: favoriteData['major_name'],
          createdAt: DateTime.now().toIso8601String(),
        );

        final updatedFavorites = [...state.favorites, newFavorite];
        final updatedStatus = Map<String, bool>.from(state.favoriteStatus);
        updatedStatus[itemId] = true;

        state = state.copyWith(
          favorites: updatedFavorites,
          favoriteStatus: updatedStatus,
        );

        return true;
      }

      return false;
    } catch (e) {
      state = state.copyWith(error: e.toString());
      return false;
    }
  }

  /// 取消收藏
  Future<bool> removeFavorite(String token, String itemId) async {
    try {
      // 从itemId中解析major_id
      final parts = itemId.split('_');
      final majorId = parts.length > 1 ? int.tryParse(parts[1]) : 0;

      if (majorId == null) {
        return false;
      }

      // 调用API删除收藏
      final response = await http.delete(
        Uri.parse('${ApiService.baseUrl}/favorite/remove?major_id=$majorId'),
        headers: _buildHeaders(token),
      );

      final result = jsonDecode(response.body);

      if (result['code'] == 0) {
        // 更新本地状态
        final updatedFavorites = state.favorites.where((item) => item.id != itemId).toList();
        final updatedStatus = Map<String, bool>.from(state.favoriteStatus);
        updatedStatus[itemId] = false;

        state = state.copyWith(
          favorites: updatedFavorites,
          favoriteStatus: updatedStatus,
        );

        return true;
      }

      return false;
    } catch (e) {
      state = state.copyWith(error: e.toString());
      return false;
    }
  }

  /// 检查是否已收藏
  Future<bool> checkFavorite(String token, String itemId) async {
    // 先检查本地缓存
    if (state.favoriteStatus.containsKey(itemId)) {
      return state.favoriteStatus[itemId]!;
    }

    try {
      // 从itemId中解析major_id
      final parts = itemId.split('_');
      final majorId = parts.length > 1 ? int.tryParse(parts[1]) : 0;

      if (majorId == null) {
        return false;
      }

      // 调用API检查收藏状态
      final response = await http.get(
        Uri.parse('${ApiService.baseUrl}/favorite/check?major_id=$majorId'),
        headers: _buildHeaders(token),
      );

      final result = jsonDecode(response.body);

      if (result['code'] == 0 && result['data'] != null) {
        final isFavorited = result['data']['is_favorited'] ?? false;

        // 更新缓存
        final updatedStatus = Map<String, bool>.from(state.favoriteStatus);
        updatedStatus[itemId] = isFavorited;
        state = state.copyWith(favoriteStatus: updatedStatus);

        return isFavorited;
      }

      return false;
    } catch (e) {
      return false;
    }
  }

  /// 切换收藏状态
  Future<bool> toggleFavorite(
    String token,
    String itemId,
    Map<String, dynamic> favoriteData,
  ) async {
    final isFavorited = state.favoriteStatus[itemId] ?? false;

    if (isFavorited) {
      // 取消收藏
      return await removeFavorite(token, itemId);
    } else {
      // 添加收藏
      return await addFavorite(token, favoriteData);
    }
  }

  /// 获取统计信息
  Map<String, int> getStatistics() {
    final universities = <String>{};
    for (var item in state.favorites) {
      universities.add(item.universityName);
    }

    return {
      'total': state.favorites.length,
      'universities': universities.length,
      'majors': state.favorites.length,
    };
  }

  /// 根据院校名称查找收藏项
  List<FavoriteItem> getByUniversity(String universityName) {
    return state.favorites
        .where((item) => item.universityName == universityName)
        .toList();
  }

  /// 搜索收藏项
  List<FavoriteItem> searchFavorites(String keyword) {
    if (keyword.isEmpty) {
      return state.favorites;
    }

    final lowerKeyword = keyword.toLowerCase();
    return state.favorites.where((item) {
      return item.universityName.toLowerCase().contains(lowerKeyword) ||
          item.majorName.toLowerCase().contains(lowerKeyword);
    }).toList();
  }
}

/// 收藏Provider
final favoriteProvider = StateNotifierProvider<FavoriteNotifier, FavoriteState>((ref) {
  return FavoriteNotifier();
});