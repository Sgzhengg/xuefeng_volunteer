import 'dart:convert';
import 'dart:async';
import 'dart:io';
import 'package:http/http.dart' as http;

void main() async {
  const apiKey = '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';
  const baseUrl = 'https://openrouter.ai/api/v1';

  print('🧪 测试 OpenRouter API 流式响应（完整版）...\n');

  final body = {
    'model': 'qwen/qwen-2.5-72b-instruct',
    'messages': [
      {
        'role': 'user',
        'content': '请详细介绍一下什么是人工智能，包括它的定义、发展历史和应用领域。',
      }
    ],
    'max_tokens': 1000,
    'temperature': 0.8,
    'stream': true,
  };

  try {
    print('📡 发送请求...');
    final request = http.Request('POST', Uri.parse('$baseUrl/chat/completions'));
    request.headers.addAll({
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $apiKey',
      'HTTP-Referer': 'https://xuefeng-coach.app',
      'X-Title': 'Xuefeng Coach',
    });
    request.body = json.encode(body);

    final stopwatch = Stopwatch()..start();

    final response = await http.Client().send(request).timeout(
      const Duration(seconds: 30),
      onTimeout: () {
        throw TimeoutException('请求超时');
      },
    );

    print('✅ 连接成功！开始接收流式响应...\n');
    print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

    String fullResponse = '';
    int chunkCount = 0;
    bool done = false;

    await for (final chunk in response.stream.transform(utf8.decoder)) {
      if (done) break;

      final lines = chunk.split('\n');

      for (final line in lines) {
        if (line.startsWith('data: ')) {
          final data = line.substring(6);

          if (data == '[DONE]') {
            done = true;
            break;
          }

          try {
            final json = jsonDecode(data);
            final choice = json['choices']?[0];
            final delta = choice?['delta'];

            if (delta != null) {
              final content = delta['content'];
              if (content != null) {
                fullResponse += content;
                chunkCount++;
                stdout.write(content);
              }
            }
          } catch (e) {
            // 忽略解析错误
          }
        }
      }
    }

    stopwatch.stop();

    print('\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    print('📊 统计信息:');
    print('  - 总耗时: ${stopwatch.elapsedMilliseconds}ms');
    print('  - 数据块数量: $chunkCount');
    print('  - 响应长度: ${fullResponse.length} 字符');
    print('\n✅ 流式响应测试成功！');

  } on TimeoutException catch (e) {
    print('❌ 请求超时: $e');
  } catch (e) {
    print('❌ 测试失败: $e');
  }
}
