// 暂时禁用 Isar 以支持 Web 平台
// import 'package:isar/isar.dart';
//
// part 'chat_message.g.dart';
//
// @Collection()

class ChatMessage {
  // 应用使用的字符串ID
  late String id;

  late String messageId;
  late String role; // 'user' or 'assistant'
  late String content;
  late int timestamp;

  // 可选的 function call 数据
  String? functionName;
  String? functionArgs;

  ChatMessage();

  ChatMessage.create({
    required this.messageId,
    required this.role,
    required this.content,
    required this.timestamp,
    this.functionName,
    this.functionArgs,
  }) {
    id = DateTime.now().millisecondsSinceEpoch.toString() + _randomString();
  }

  static String _randomString() {
    return (DateTime.now().microsecondsSinceEpoch % 1000).toString();
  }
}
