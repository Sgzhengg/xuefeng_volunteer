import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;

void main() async {
  const apiKey = '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';
  const baseUrl = 'https://openrouter.ai/api/v1';

  print('🧪 测试 Flutter Web 环境下的 OpenRouter API 调用...\n');

  final body = {
    'model': 'qwen/qwen-2.5-72b-instruct',
    'messages': [
      {
        'role': 'user',
        'content': '你好',
      }
    ],
    'max_tokens': 50,
    'temperature': 0.8,
    'stream': false,
  };

  try {
    print('📡 发送 POST 请求到 $baseUrl/chat/completions');
    print('🔑 使用 API Key: ${apiKey.substring(0, 20)}...\n');

    final stopwatch = Stopwatch()..start();

    final response = await http.post(
      Uri.parse('$baseUrl/chat/completions'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $apiKey',
        'HTTP-Referer': 'https://xuefeng-coach.app',
        'X-Title': 'Xuefeng Coach',
        'Access-Control-Allow-Origin': '*',
      },
      body: json.encode(body),
    ).timeout(
      const Duration(seconds: 10),
      onTimeout: () {
        print('⏰ 请求超时（10秒）');
        throw TimeoutException('请求超时');
      },
    );

    stopwatch.stop();

    print('✅ 响应状态码: ${response.statusCode}');
    print('⏱️  耗时: ${stopwatch.elapsedMilliseconds}ms\n');

    if (response.statusCode == 200) {
      print('📄 响应头:');
      response.headers.forEach((key, values) {
        print('  $key: $values');
      });
      print('\n📝 响应体（前500字符）:');
      final body = response.body;
      print(body.substring(0, body.length > 500 ? 500 : body.length));

      final data = json.decode(response.body);
      final content = data['choices']?[0]?['message']?['content'] ?? '';
      print('\n✅ 成功获取回复: "$content"');
    } else {
      print('❌ HTTP 错误:');
      print('  状态码: ${response.statusCode}');
      print('  响应体: ${response.body}');
    }

  } on TimeoutException catch (e) {
    print('❌ 超时错误: $e');
  } on http.ClientException catch (e) {
    print('❌ 网络错误 (ClientException): $e');
    print('\n🔍 可能的原因:');
    print('  1. CORS 跨域问题');
    print('  2. 网络连接问题');
    print('  3. OpenRouter API 不允许从浏览器直接调用');
  } catch (e) {
    print('❌ 未知错误: $e');
    print('  错误类型: ${e.runtimeType}');
  }
}
