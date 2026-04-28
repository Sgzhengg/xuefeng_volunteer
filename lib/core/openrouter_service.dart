import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'models/chat_message.dart';

part 'openrouter_service.g.dart';

/// OpenRouter API 配置
class OpenRouterConfig {
  static const String baseUrl = 'https://openrouter.ai/api/v1';
  static const String model = 'qwen/qwen-2.5-72b-instruct';
  static const int maxTokens = 4096;
  static const double temperature = 0.8;
  static const Duration timeout = Duration(seconds: 30);

  /// ⚠️ 生产环境应从环境变量或安全存储读取
  /// 使用 const String.fromEnvironment('OPENROUTER_API_KEY') 传入
  /// 运行时: flutter run --dart-define=OPENROUTER_API_KEY=your-key-here
  static const String apiKey = String.fromEnvironment('OPENROUTER_API_KEY',
      defaultValue: '');
}

@riverpod
class OpenRouterService extends _$OpenRouterService {
  final _client = http.Client();

  @override
  void build() {}

  /// 发送聊天请求（支持 Streaming + Tool Use）
  Stream<ChatResponseChunk> chatWithTools({
    required List<ChatMessage> messages,
    String? systemPrompt,
    List<FunctionTool>? tools,
  }) async* {
    final requestMessages = <Map<String, dynamic>>[];

    // 添加系统提示
    if (systemPrompt != null) {
      requestMessages.add({
        'role': 'system',
        'content': systemPrompt,
      });
    }

    // 添加历史消息
    for (final msg in messages) {
      requestMessages.add({
        'role': msg.role == 'user' ? 'user' : 'assistant',
        'content': msg.content,
        if (msg.functionName != null) 'name': msg.functionName,
      });
    }

    final body = {
      'model': OpenRouterConfig.model,
      'messages': requestMessages,
      'max_tokens': OpenRouterConfig.maxTokens,
      'temperature': OpenRouterConfig.temperature,
      'stream': true,
      if (tools != null && tools.isNotEmpty) 'tools': _buildTools(tools),
      'tool_choice': tools != null && tools.isNotEmpty ? 'auto' : null,
    };

    try {
      final request = http.Request('POST', Uri.parse('${OpenRouterConfig.baseUrl}/chat/completions'));
      request.headers.addAll({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${OpenRouterConfig.apiKey}',
        'HTTP-Referer': 'https://xuefeng-coach.app',
        'X-Title': 'Xuefeng Coach',
      });
      request.body = json.encode(body);

      // 添加超时
      final response = await _client.send(request).timeout(
        OpenRouterConfig.timeout,
        onTimeout: () {
          throw TimeoutException('OpenRouter API 请求超时', OpenRouterConfig.timeout);
        },
      );

      // 用于缓存不完整的JSON行
      String _buffer = '';

      await for (final chunk in response.stream.transform(utf8.decoder)) {
        // 将新数据添加到缓冲区
        _buffer += chunk;

        // 按行分割
        final lines = _buffer.split('\n');

        // 保留最后一行（可能不完整）
        _buffer = lines.removeLast();

        for (final line in lines) {
          if (line.startsWith('data: ')) {
            final data = line.substring(6);

            if (data == '[DONE]') {
              yield ChatResponseChunk(
                type: ResponseChunkType.done,
                finishReason: 'stop',
              );
              return;
            }

            try {
              final json = jsonDecode(data);
              final choice = json['choices']?[0];
              final delta = choice?['delta'];

              if (delta != null) {
                // 检查是否有 tool_calls
                final toolCalls = delta['tool_calls'];
                if (toolCalls != null) {
                  yield ChatResponseChunk(
                    type: ResponseChunkType.toolCall,
                    toolCalls: _parseToolCalls(toolCalls),
                  );
                  return; // Tool calls 完成后结束流
                }

                // 普通文本内容
                final content = delta['content'];
                if (content != null) {
                  yield ChatResponseChunk(
                    type: ResponseChunkType.content,
                    content: content,
                  );
                }
              }

              // 检查是否完成
              final finishReason = choice?['finish_reason'];
              if (finishReason != null) {
                yield ChatResponseChunk(
                  type: ResponseChunkType.done,
                  finishReason: finishReason,
                );
              }
            } catch (e) {
              // JSON 解析错误，跳过这个数据块
              // 这通常是因为 JSON 被截断，等待下一个数据块
            }
          }
        }
      }

      // 处理缓冲区中剩余的数据
      if (_buffer.trim().isNotEmpty && _buffer.trim().startsWith('data: ')) {
        final data = _buffer.trim().substring(6);
        if (data != '[DONE]') {
          try {
            final json = jsonDecode(data);
            final choice = json['choices']?[0];
            final delta = choice?['delta'];

            if (delta != null) {
              final content = delta['content'];
              if (content != null) {
                yield ChatResponseChunk(
                  type: ResponseChunkType.content,
                  content: content,
                );
              }
            }
          } catch (e) {
            // 忽略最后的解析错误
          }
        }
      }

    } catch (e) {
      yield ChatResponseChunk(
        type: ResponseChunkType.error,
        content: '❌ 哎呀，出错了：$e',
      );
      throw Exception('OpenRouter API 调用失败: $e');
    }
  }

  /// 发送聊天请求（支持 Streaming，简化版）
  Stream<String> chat({
    required List<ChatMessage> messages,
    String? systemPrompt,
    List<FunctionTool>? tools,
  }) async* {
    await for (final chunk in chatWithTools(
      messages: messages,
      systemPrompt: systemPrompt,
      tools: tools,
    )) {
      if (chunk.type == ResponseChunkType.content) {
        yield chunk.content;
      }
    }
  }

  /// 解析 tool_calls
  List<ToolCall> _parseToolCalls(dynamic toolCallsData) {
    final List<ToolCall> calls = [];

    if (toolCallsData is List) {
      for (final call in toolCallsData) {
        if (call is Map) {
          final function = call['function'];
          if (function is Map) {
            calls.add(ToolCall(
              id: call['id']?.toString() ?? '',
              name: function['name']?.toString() ?? '',
              arguments: function['arguments']?.toString() ?? '{}',
            ));
          }
        }
      }
    }

    return calls;
  }

  /// 构建 Function Calling 工具
  List<Map<String, dynamic>> _buildTools(List<FunctionTool> tools) {
    return tools.map((tool) {
      return {
        'type': 'function',
        'function': {
          'name': tool.name,
          'description': tool.description,
          'parameters': tool.parameters,
        },
      };
    }).toList();
  }

  void dispose() {
    _client.close();
  }
}

/// Function Tool 定义
class FunctionTool {
  final String name;
  final String description;
  final Map<String, dynamic> parameters;
  final Future<dynamic> Function(Map<String, dynamic>) execute;

  FunctionTool({
    required this.name,
    required this.description,
    required this.parameters,
    required this.execute,
  });
}

/// 响应块类型
enum ResponseChunkType {
  content,
  toolCall,
  done,
  error,
}

/// 聊天响应块
class ChatResponseChunk {
  final ResponseChunkType type;
  final String content;
  final List<ToolCall>? toolCalls;
  final String? finishReason;

  ChatResponseChunk({
    required this.type,
    this.content = '',
    this.toolCalls,
    this.finishReason,
  });
}

/// Tool Call 数据结构
class ToolCall {
  final String id;
  final String name;
  final String arguments;

  ToolCall({
    required this.id,
    required this.name,
    required this.arguments,
  });

  Map<String, dynamic> getArguments() {
    try {
      return json.decode(arguments) as Map<String, dynamic>;
    } catch (_) {
      return {};
    }
  }
}
