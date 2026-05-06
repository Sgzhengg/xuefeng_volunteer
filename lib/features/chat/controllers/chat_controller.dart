import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'dart:developer' as developer;
import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/skill_loader.dart';
import '../../../core/prompt_builder.dart';
import '../../../core/openrouter_service.dart';
import '../../../core/gaokao_data_service.dart';
import '../../../core/models/chat_message.dart';
import '../../../core/models/user_profile.dart';
import '../../../core/models/gaokao_data_models.dart';
import '../../../core/models/gaokao_data_context.dart';

part 'chat_controller.g.dart';

class ChatState {
  final List<ChatMessage> messages;
  final bool isTyping;
  final String currentStreamingMessage;
  final bool isLoadingData;

  ChatState({
    required this.messages,
    required this.isTyping,
    required this.currentStreamingMessage,
    this.isLoadingData = false,
  });

  ChatState copyWith({
    List<ChatMessage>? messages,
    bool? isTyping,
    String? currentStreamingMessage,
    bool? isLoadingData,
  }) {
    return ChatState(
      messages: messages ?? this.messages,
      isTyping: isTyping ?? this.isTyping,
      currentStreamingMessage: currentStreamingMessage ?? this.currentStreamingMessage,
      isLoadingData: isLoadingData ?? this.isLoadingData,
    );
  }
}

@riverpod
class ChatController extends _$ChatController {
  @override
  ChatState build() {
    developer.log('ChatController.build() - 开始初始化');
    // 不在 build() 中异步初始化
    return ChatState(
      messages: [],
      isTyping: false,
      currentStreamingMessage: '',
    );
  }

    Future<void> initializeChat() async {
    print('🚀 _initializeChat() - 快速初始化（不加载SKILL.md）');

    // 发送欢迎消息（立即显示，不等待）
    final welcomeMessage = ChatMessage.create(
      messageId: DateTime.now().millisecondsSinceEpoch.toString(),
      role: 'assistant',
      content: '嘿，同学/家长，我是学锋老师！有什么关于志愿填报的问题，尽管问我。',
      timestamp: DateTime.now().millisecondsSinceEpoch,
    );

    state = state.copyWith(
      messages: [welcomeMessage],
    );
    print('✅ _initializeChat() - 欢迎消息已设置');
  }

  Future<void> sendMessage(String content) async {
    developer.log('sendMessage() - 用户发送消息: "$content"');

    // 如果还没有欢迎消息，先初始化
    if (state.messages.isEmpty) {
      developer.log('sendMessage() - 首次使用，先初始化');
      await initializeChat();
    }

    // 1. 添加用户消息
    final userMessage = ChatMessage.create(
      messageId: DateTime.now().millisecondsSinceEpoch.toString(),
      role: 'user',
      content: content,
      timestamp: DateTime.now().millisecondsSinceEpoch,
    );

    state = state.copyWith(
      messages: [...state.messages, userMessage],
      isTyping: true,
    );
    developer.log('sendMessage() - 用户消息已添加到界面');

    try {
      // 2. 直接调用后端API（不再使用OpenRouter）
      developer.log('sendMessage() - 调用后端API');
      final response = await _callBackendApi(content);

      developer.log('sendMessage() - 后端API调用完成');
      developer.log('sendMessage() - 响应长度: ${response.length}');

      // 3. 添加AI回复
      if (response.isNotEmpty) {
        final assistantMessage = ChatMessage.create(
          messageId: DateTime.now().millisecondsSinceEpoch.toString(),
          role: 'assistant',
          content: response,
          timestamp: DateTime.now().millisecondsSinceEpoch,
        );

        state = state.copyWith(
          messages: [...state.messages, assistantMessage],
          isTyping: false,
        );

        developer.log('sendMessage() - AI回复已显示');
      } else {
        developer.log('sendMessage() - 警告：响应为空', level: 900);
        throw Exception('后端返回空响应');
      }

    } catch (e) {
      developer.log('sendMessage() - 错误: $e', level: 1000);
      developer.log('sendMessage() - 错误堆栈: ${StackTrace.current}', level: 1000);

      state = state.copyWith(
        isTyping: false,
        isLoadingData: false,
        currentStreamingMessage: '',
      );

      // 显示错误消息
      final errorMessage = ChatMessage.create(
        messageId: DateTime.now().millisecondsSinceEpoch.toString(),
        role: 'assistant',
        content: '哎呀，系统出了点问题。不过别担心，这不是你的问题，是我的问题。你重新发一遍试试？\n\n错误详情：$e',
        timestamp: DateTime.now().millisecondsSinceEpoch,
      );

      state = state.copyWith(
        messages: [...state.messages, errorMessage],
      );
    }
  }

  /// 执行 Tool Calling 循环（Claude/OpenRouter 风格）
  Future<void> _executeToolCallingLoop({
    required List<ChatMessage> messages,
    required String systemPrompt,
    required List<FunctionTool> tools,
    required UserProfile? user,
    required String skillContent,
    int maxIterations = 5,
  }) async {
    final promptBuilder = ref.read(promptBuilderProvider.notifier);
    final openrouter = ref.read(openRouterServiceProvider.notifier);
    final gaokaoDataService = ref.read(gaokaoDataServiceProvider.notifier);

    developer.log('_executeToolCallingLoop() - 开始，最大迭代次数: $maxIterations');

    GaokaoDataContext dataContext = GaokaoDataContext();

    for (int iteration = 0; iteration < maxIterations; iteration++) {
      developer.log('_executeToolCallingLoop() - 迭代 $iteration/$maxIterations');

      try {
        developer.log('_executeToolCallingLoop() - 调用 OpenRouter API');
        // 调用 OpenRouter API
        final responseChunks = openrouter.chatWithTools(
          messages: messages,
          systemPrompt: iteration == 0 ? systemPrompt : null,
          tools: tools,
        );
        developer.log('_executeToolCallingLoop() - OpenRouter API Stream 已创建');

        ChatResponseChunk? finalChunk;
        String fullResponse = '';
        List<ToolCall> toolCalls = [];
        int chunkCount = 0;

        developer.log('_executeToolCallingLoop() - 开始接收 Stream 数据');
        await for (final chunk in responseChunks) {
          chunkCount++;
          developer.log('_executeToolCallingLoop() - 收到 chunk #$chunkCount, type: ${chunk.type}');

          finalChunk = chunk;

          if (chunk.type == ResponseChunkType.content) {
            fullResponse += chunk.content;
            state = state.copyWith(
              currentStreamingMessage: fullResponse,
            );
            developer.log('_executeToolCallingLoop() - 累计内容长度: ${fullResponse.length}');
          } else if (chunk.type == ResponseChunkType.toolCall) {
            toolCalls = chunk.toolCalls ?? [];
            developer.log('_executeToolCallingLoop() - 收到 tool calls，数量: ${toolCalls.length}');
            break;
          } else if (chunk.type == ResponseChunkType.done) {
            developer.log('_executeToolCallingLoop() - 收到 done 信号');
            break;
          } else if (chunk.type == ResponseChunkType.error) {
            developer.log('_executeToolCallingLoop() - 收到错误: ${chunk.content}', level: 1000);
            throw Exception(chunk.content);
          }
        }

        developer.log('_executeToolCallingLoop() - Stream 结束，共收到 $chunkCount 个 chunks');

        // 如果有 Tool Calls，执行工具
        if (toolCalls.isNotEmpty) {
          developer.log('_executeToolCallingLoop() - 执行工具调用');
          state = state.copyWith(isLoadingData: true);

          for (final toolCall in toolCalls) {
            try {
              developer.log('_executeToolCallingLoop() - 执行工具: ${toolCall.name}');
              // 执行工具调用
              final result = await _executeToolCall(
                toolCall,
                gaokaoDataService,
              );

              // 将工具调用结果添加到消息历史
              final toolMessage = ChatMessage.create(
                messageId: DateTime.now().millisecondsSinceEpoch.toString(),
                role: 'assistant',
                content: '',
                functionName: toolCall.name,
                functionArgs: toolCall.arguments,
                timestamp: DateTime.now().millisecondsSinceEpoch,
              );
              messages = [...messages, toolMessage];

              final toolResponse = ChatMessage.create(
                messageId: DateTime.now().millisecondsSinceEpoch.toString(),
                role: 'user',
                content: _formatToolResult(result),
                timestamp: DateTime.now().millisecondsSinceEpoch,
              );
              messages = [...messages, toolResponse];

              // 更新数据上下文
              dataContext = _updateDataContext(toolCall.name, result, dataContext);

            } catch (e) {
              developer.log('_executeToolCallingLoop() - 工具调用失败: $e', level: 1000);
              // 工具调用失败
              final errorMessage = ChatMessage.create(
                messageId: DateTime.now().millisecondsSinceEpoch.toString(),
                role: 'user',
                content: '工具调用失败：$e',
                timestamp: DateTime.now().millisecondsSinceEpoch,
              );
              messages = [...messages, errorMessage];
            }
          }

          state = state.copyWith(isLoadingData: false);

          // 继续下一轮迭代，带着工具结果
          developer.log('_executeToolCallingLoop() - 继续下一轮迭代');
          continue;
        }

        // 没有工具调用，正常生成回复
        developer.log('_executeToolCallingLoop() - 生成最终回复，长度: ${fullResponse.length}');
        if (fullResponse.isNotEmpty) {
          // 如果有数据上下文，添加数据来源说明
          if (dataContext.hasData) {
            fullResponse += '\n\n---\n\n📊 **数据来源**：公开数据和历史录取信息\n\n⚠️ **重要提醒**：以上建议仅供参考，最终志愿填报以各省教育考试院官方公布为准。';
          }

          final assistantMessage = ChatMessage.create(
            messageId: DateTime.now().millisecondsSinceEpoch.toString(),
            role: 'assistant',
            content: fullResponse,
            timestamp: DateTime.now().millisecondsSinceEpoch,
          );

          state = state.copyWith(
            messages: [...messages, assistantMessage],
            isTyping: false,
            currentStreamingMessage: '',
          );

          developer.log('_executeToolCallingLoop() - 回复已显示给用户');
          // 保存到数据库
          await _saveMessages();
          return;
        } else {
          developer.log('_executeToolCallingLoop() - 警告：响应为空', level: 900);
        }

      } catch (e) {
        developer.log('_executeToolCallingLoop() - 迭代错误: $e', level: 1000);
        developer.log('_executeToolCallingLoop() - 错误堆栈: ${StackTrace.current}', level: 1000);

        state = state.copyWith(
          isTyping: false,
          isLoadingData: false,
          currentStreamingMessage: '',
        );

        // 显示错误消息
        final errorMessage = ChatMessage.create(
          messageId: DateTime.now().millisecondsSinceEpoch.toString(),
          role: 'assistant',
          content: '哎呀，系统出了点问题。不过别担心，这不是你的问题，是我的问题。你重新发一遍试试？\n\n错误详情：$e',
          timestamp: DateTime.now().millisecondsSinceEpoch,
        );

        state = state.copyWith(
          messages: [...messages, errorMessage],
        );
        return;
      }
    }

    developer.log('_executeToolCallingLoop() - 达到最大迭代次数');
  }

  /// 执行单个工具调用
  Future<dynamic> _executeToolCall(
    ToolCall toolCall,
    GaokaoDataService gaokaoDataService,
  ) async {
    final args = toolCall.getArguments();

    switch (toolCall.name) {
      case 'get_admission_probability':
        return await gaokaoDataService.queryAdmissionProbability(
          province: args['province'] ?? '',
          score: args['score'] ?? 0,
          rank: args['rank'],
          subjectType: args['subject_type'] ?? '综合',
          universityName: args['university_name'],
          majorName: args['major_name'],
        );

      case 'get_one_point_segment':
        return await gaokaoDataService.queryOnePointSegment(
          province: args['province'] ?? '',
          year: args['year'] ?? 2025,
          score: args['score'],
        );

      case 'get_university_info':
        return await gaokaoDataService.queryUniversityInfo(
          universityName: args['university_name'] ?? '',
        );

      case 'get_provincial_control_line':
        return await gaokaoDataService.queryProvincialControlLine(
          province: args['province'] ?? '',
          year: args['year'] ?? 2025,
        );

      case 'get_major_employment_data':
        return await gaokaoDataService.queryMajorEmploymentData(
          majorName: args['major_name'] ?? '',
        );

      default:
        throw Exception('未知工具：${toolCall.name}');
    }
  }

  /// 格式化工具调用结果
  String _formatToolResult(dynamic result) {
    if (result is AdmissionProbabilityResponse) {
      if (result.data != null) {
        final data = result.data!;
        return '录取概率：${data.probability}%，${data.prediction}';
      }
      return result.message ?? '查询失败';
    }

    if (result is OnePointSegmentResponse) {
      if (result.data != null) {
        return '查询成功：一分一段表数据已获取';
      }
      return result.message ?? '查询失败';
    }

    if (result is UniversityInfoResponse) {
      if (result.data != null) {
        final info = result.data!;
        return '院校信息：${info.name}（${info.level}/${info.type}）';
      }
      return result.message ?? '查询失败';
    }

    return result.toString();
  }

  /// 更新数据上下文
  GaokaoDataContext _updateDataContext(
    String toolName,
    dynamic result,
    GaokaoDataContext currentContext,
  ) {
    if (result is AdmissionProbabilityResponse && result.data != null) {
      return currentContext.copyWithAdmissionProbability(result.data!);
    }

    if (result is OnePointSegmentResponse && result.data != null) {
      return currentContext.copyWithOnePointSegment(result.data!);
    }

    if (result is UniversityInfoResponse && result.data != null) {
      return currentContext.copyWithUniversityInfo(result.data!);
    }

    if (result is ProvincialControlLineResponse && result.data != null) {
      return currentContext.copyWithProvincialControlLine(result.data!);
    }

    if (result is MajorEmploymentDataResponse && result.data != null) {
      return currentContext.copyWithMajorEmployment(result.data!);
    }

    return currentContext;
  }

  /// 构建 Function Tools
  List<FunctionTool> _buildFunctionTools() {
    return [
      FunctionTool(
        name: 'get_admission_probability',
        description: '查询录取概率。根据省份、分数、位次、院校、专业预测录取概率。',
        parameters: {
          'type': 'object',
          'properties': {
            'province': {
              'type': 'string',
              'description': '省份名称（如：北京、江苏）',
            },
            'score': {
              'type': 'integer',
              'description': '高考分数',
            },
            'rank': {
              'type': 'integer',
              'description': '位次（可选）',
            },
            'subject_type': {
              'type': 'string',
              'description': '科类（理科/文科/综合）',
            },
            'university_name': {
              'type': 'string',
              'description': '院校名称（可选）',
            },
            'major_name': {
              'type': 'string',
              'description': '专业名称（可选）',
            },
          },
          'required': ['province', 'score', 'subject_type'],
        },
        execute: (params) async {
          // 占位符，实际执行在 _executeToolCall
          return {};
        },
      ),

      FunctionTool(
        name: 'get_one_point_segment',
        description: '查询一分一段表。根据省份和年份查询分数对应位次。',
        parameters: {
          'type': 'object',
          'properties': {
            'province': {
              'type': 'string',
              'description': '省份名称',
            },
            'year': {
              'type': 'integer',
              'description': '年份（如：2025）',
            },
            'score': {
              'type': 'integer',
              'description': '分数（可选）',
            },
          },
          'required': ['province', 'year'],
        },
        execute: (params) async {
          return {};
        },
      ),

      FunctionTool(
        name: 'get_university_info',
        description: '查询院校信息。包括排名、录取分数、就业率、薪资等。',
        parameters: {
          'type': 'object',
          'properties': {
            'university_name': {
              'type': 'string',
              'description': '院校名称（支持模糊搜索）',
            },
          },
          'required': ['university_name'],
        },
        execute: (params) async {
          return {};
        },
      ),

      FunctionTool(
        name: 'get_provincial_control_line',
        description: '查询省控线。一本线、二本线等。',
        parameters: {
          'type': 'object',
          'properties': {
            'province': {
              'type': 'string',
              'description': '省份名称',
            },
            'year': {
              'type': 'integer',
              'description': '年份',
            },
          },
          'required': ['province', 'year'],
        },
        execute: (params) async {
          return {};
        },
      ),

      FunctionTool(
        name: 'get_major_employment_data',
        description: '查询专业就业数据。包括就业率、薪资、就业趋势、AI冲击程度等。',
        parameters: {
          'type': 'object',
          'properties': {
            'major_name': {
              'type': 'string',
              'description': '专业名称',
            },
          },
          'required': ['major_name'],
        },
        execute: (params) async {
          return {};
        },
      ),
    ];
  }

  Future<UserProfile?> _getCurrentUser() async {
    // TODO: 从数据库获取用户档案
    return null;
  }

  String _getAvailableToolsDescription() {
    return '''
- 查询录取概率（根据分数、省份、院校、专业）
- 查询一分一段表（分数对应位次）
- 查询院校信息（排名、就业率、薪资）
- 查询省控线（一本线、二本线）
- 查询专业就业数据（就业率、薪资、AI冲击）
''';
  }

  /// 调用后端API（简化版，不使用Tool Calling）
  Future<void> sendMessageViaBackend(String content) async {
    developer.log('sendMessageViaBackend() - 通过后端API发送消息');

    // 如果还没有欢迎消息，先初始化
    if (state.messages.isEmpty) {
      await initializeChat();
    }

    // 1. 添加用户消息
    final userMessage = ChatMessage.create(
      messageId: DateTime.now().millisecondsSinceEpoch.toString(),
      role: 'user',
      content: content,
      timestamp: DateTime.now().millisecondsSinceEpoch,
    );

    state = state.copyWith(
      messages: [...state.messages, userMessage],
      isTyping: true,
    );
    developer.log('sendMessageViaBackend() - 用户消息已添加');

    try {
      // 2. 调用后端API
      developer.log('sendMessageViaBackend() - 调用后端API');
      final response = await _callBackendApi(content);

      developer.log('sendMessageViaBackend() - 后端API调用完成');
      developer.log('sendMessageViaBackend() - 响应长度: ${response.length}');

      // 3. 添加AI回复
      if (response.isNotEmpty) {
        final assistantMessage = ChatMessage.create(
          messageId: DateTime.now().millisecondsSinceEpoch.toString(),
          role: 'assistant',
          content: response,
          timestamp: DateTime.now().millisecondsSinceEpoch,
        );

        state = state.copyWith(
          messages: [...state.messages, assistantMessage],
          isTyping: false,
        );

        developer.log('sendMessageViaBackend() - AI回复已显示');
      } else {
        developer.log('sendMessageViaBackend() - 警告：响应为空', level: 900);
        throw Exception('后端返回空响应');
      }

    } catch (e) {
      developer.log('sendMessageViaBackend() - 错误: $e', level: 1000);

      state = state.copyWith(
        isTyping: false,
      );

      // 显示错误消息
      final errorMessage = ChatMessage.create(
        messageId: DateTime.now().millisecondsSinceEpoch.toString(),
        role: 'assistant',
        content: '哎呀，系统出了点问题。不过别担心，这不是你的问题，是我的问题。你重新发一遍试试？\n\n错误详情：$e',
        timestamp: DateTime.now().millisecondsSinceEpoch,
      );

      state = state.copyWith(
        messages: [...state.messages, errorMessage],
      );
    }
  }

  /// 调用后端API的辅助方法
  Future<String> _callBackendApi(String message) async {
    final url = Uri.parse('http://localhost:8000/api/v1/chat');

    final requestBody = {
      'message': message,
      'context': {},
      'conversation_history': null,
    };

    try {
      final request = http.Request('POST', url);
      request.headers.addAll({
        'Content-Type': 'application/json',
      });
      request.body = json.encode(requestBody);

      // 发送请求
      final response = await request.send().timeout(
        const Duration(seconds: 120),
        onTimeout: () {
          throw TimeoutException('后端API请求超时', const Duration(seconds: 120));
        },
      );

      if (response.statusCode == 200) {
        final responseBody = await response.stream.bytesToString();
        final result = json.decode(responseBody);

        if (result['success'] == true && result['response'] != null) {
          return result['response'] as String;
        } else {
          final error = result['message'] ?? '未知错误';
          throw Exception('后端API返回错误: $error');
        }
      } else {
        throw Exception('后端API HTTP错误: ${response.statusCode}');
      }
    } catch (e) {
      developer.log('_callBackendApi() - 错误: $e', level: 1000);
      rethrow;
    }
  }

  Future<void> _saveMessages() async {
    // TODO: 保存到 Isar 数据库
  }
}
