# 学锋志愿教练

一款基于学锋思维框架的高考志愿填报 AI 教练 App。

## 项目简介

这是「学锋志愿教练」—— 一个让你和"学锋老师"直接聊天的高考志愿填报 App。AI 用东北大哥的吐槽式风格，基于真实就业数据给出志愿建议。

## 核心特性

- 🎭 **学锋风格对话** - 基于 SKILL.md 的完整思维操作系统
- 📊 **Mock 模式支持** - 无需 API Key 即可体验完整功能
- 🤖 **智能 Tool Calling** - AI自动调用工具获取最新数据，基于真实指标给出建议
- 📈 **就业数据分析** - 专业就业率、薪资、AI冲击程度等实时数据
- 🎤 **语音输入** - 支持语音和文字双通道输入
- 💬 **实时流式响应** - 打字机效果，体验流畅
- 📱 **跨平台** - Flutter 支持 iOS/Android/鸿蒙
- 🎯 **自动化优化系统** - 基于karpathy/autoresearch方法论的提示词优化（[详见](./autoresearch/README.md)）
- 🎨 **ChatGPT极简风格UI** - 现代化的用户界面设计（[配置](./lib/config/ui_config.dart)）

> **🚀 最新**：新增 **自动化优化系统** + **ChatGPT极简风格UI**！详见 [完整使用指南](./autoresearch/COMPLETE_GUIDE.md)

## 技术栈

- **前端**: Flutter 3.24+ (Riverpod + GoRouter)
- **本地存储**: Isar NoSQL 数据库
- **AI 模型**: OpenRouter + Qwen 2.5 72B (支持 Tool Use)
- **数据源**: 咕咕数据 API (录取概率、一分一段表、院校信息)
- **网络**: Dio + HTTP (支持重试、超时、错误处理)
- **语音识别**: Speech-to-Text

## 项目结构

```
lib/
├── core/                   # 核心基础设施
│   ├── skill_loader.dart   # SKILL.md 加载器
│   ├── openrouter_service.dart  # OpenRouter API 封装
│   ├── prompt_builder.dart # 动态 Prompt 构建器
│   └── models/             # 数据模型
├── features/               # 功能模块
│   ├── chat/              # 聊天功能
│   ├── simulator/         # 志愿模拟器
│   ├── profile/           # 用户档案
│   └── dashboard/         # 数据看板
└── shared/                # 共享组件

autoresearch/              # 自动化优化系统 ⭐ NEW
├── evaluators/            # 评估器（风格、实用性、数据准确性）
├── scenarios/             # 测试场景（20个）
├── agents/                # 优化Agent
├── dashboard/             # 监控Dashboard
├── report/                # HTML报告生成器
└── run_optimization.py    # 主优化程序

backend/
├── app/
│   ├── api/               # API路由
│   └── services/          # 服务层（AI聊天服务）
└── data/                  # 数据文件（录取分数线等）
```

## 安装与运行

### 🚀 快速开始（Mock 模式，推荐）

**无需任何配置，直接运行！**

```bash
# 1. 安装依赖
flutter pub get

# 2. 生成代码
flutter pub run build_runner build

# 3. 运行 App
flutter run
```

> ✅ App 会自动检测到没有 API Key，启用 Mock 模式。

### 📊 真实数据模式（需要 API Key）

如果你有咕咕数据 API Key：

```bash
# 运行时传入 API Key
flutter run --dart-define=GUGUDATA_APPKEY=sk-your-appkey-here
```

**获取 AppKey**：
- 访问 [咕咕数据官网](https://gugudata.com)
- 或使用其他数据源（见 [Mock 模式指南](./MOCK_MODE_GUIDE.md)）

### 📝 生成代码

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

## 配置说明

### OpenRouter API Key

已配置在 `lib/core/openrouter_service.dart`（仅用于开发）。

**⚠️ 生产环境**：应从环境变量读取：

```dart
static String apiKey = String.fromEnvironment('OPENROUTER_API_KEY');
```

### 咕咕数据 AppKey

**必需**：用于查询真实高考数据。

1. 访问 [咕咕数据官网](https://gugudata.com)
2. 注册账号 → 控制台 → API管理 → 创建密钥
3. 配置环境变量（见上方"安装与运行"）

**详细配置指南**：查看 [DATA_INTEGRATION_GUIDE.md](./DATA_INTEGRATION_GUIDE.md)

## SKILL.md 说明

本项目使用 `assets/skill/SKILL.md` 作为 AI 教练的核心系统提示。

该文件基于张学锋生前全部公开言论深度提炼，包含：
- 5 个核心心智模型
- 8 条决策启发式
- 完整的表达 DNA
- Agentic 工作流

## 免责声明

- 本 App 中的 AI 教练基于张学锋公开言论的模拟，非其本人观点
- 所有建议仅供参考，最终志愿填报以省教育考试院官方信息为准
- 数据来源于阳光高考网、各高校官方发布的公开信息
- 我们不对基于本建议做出的决策承担任何责任

## 开发路线图

### Phase 1: 基础聊天 ✅
- [x] 基础聊天功能
- [x] SKILL.md 集成
- [x] OpenRouter API 接入
- [x] 实时流式响应

### Phase 2: 数据集成 ✅
- [x] 咕咕数据 API 接入
- [x] Tool Calling 支持
- [x] 录取概率预测
- [x] 一分一段表查询
- [x] 院校信息查询
- [x] 专业就业数据

### Phase 3: 高级功能（开发中）
- [ ] PDF 报告生成
- [ ] 志愿模拟器（冲稳保垫）
- [ ] 历史记录同步
- [ ] 数据可视化

### Phase 4: 优化与上线（待规划）
- [ ] 性能优化
- [ ] 支付功能
- [ ] App Store 上线

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

---

**注意**: 本项目仅用于学习交流，请勿用于商业用途。
