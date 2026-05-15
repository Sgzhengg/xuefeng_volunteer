/// 用户模型
class User {
  final String id;
  final String deviceId;
  final bool isAnonymous;
  final String? nickname;
  final String? phoneNumber;
  final DateTime createdAt;
  final DateTime? lastLoginAt;
  final Map<String, dynamic>? deviceInfo;

  User({
    required this.id,
    required this.deviceId,
    this.isAnonymous = true,
    this.nickname,
    this.phoneNumber,
    required this.createdAt,
    this.lastLoginAt,
    this.deviceInfo,
  });

  /// 从JSON创建用户实例
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      deviceId: json['device_id'] as String,
      isAnonymous: json['is_anonymous'] as bool? ?? true,
      nickname: json['nickname'] as String?,
      phoneNumber: json['phone_number'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      lastLoginAt: json['last_login_at'] != null
          ? DateTime.parse(json['last_login_at'] as String)
          : null,
      deviceInfo: json['device_info'] as Map<String, dynamic>?,
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'device_id': deviceId,
      'is_anonymous': isAnonymous,
      'nickname': nickname,
      'phone_number': phoneNumber,
      'created_at': createdAt.toIso8601String(),
      'last_login_at': lastLoginAt?.toIso8601String(),
      'device_info': deviceInfo,
    };
  }

  /// 创建匿名用户
  factory User.createAnonymous({
    required String deviceId,
    required Map<String, dynamic> deviceInfo,
  }) {
    return User(
      id: 'anon_${deviceId}_${DateTime.now().millisecondsSinceEpoch}',
      deviceId: deviceId,
      isAnonymous: true,
      createdAt: DateTime.now(),
      deviceInfo: deviceInfo,
    );
  }

  /// 复制并修改部分字段
  User copyWith({
    String? id,
    String? deviceId,
    bool? isAnonymous,
    String? nickname,
    String? phoneNumber,
    DateTime? createdAt,
    DateTime? lastLoginAt,
    Map<String, dynamic>? deviceInfo,
  }) {
    return User(
      id: id ?? this.id,
      deviceId: deviceId ?? this.deviceId,
      isAnonymous: isAnonymous ?? this.isAnonymous,
      nickname: nickname ?? this.nickname,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      createdAt: createdAt ?? this.createdAt,
      lastLoginAt: lastLoginAt ?? this.lastLoginAt,
      deviceInfo: deviceInfo ?? this.deviceInfo,
    );
  }

  /// 显示名称
  String get displayName {
    if (nickname != null && nickname!.isNotEmpty) {
      return nickname!;
    }
    if (isAnonymous) {
      return '游客用户';
    }
    return '用户';
  }

  /// 是否已绑定手机号
  bool get isPhoneBound => phoneNumber != null && phoneNumber!.isNotEmpty;
}