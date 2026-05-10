import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
// 暂时禁用 Isar 以支持 Web 平台
// import 'package:isar/isar.dart';
// import 'package:isar_flutter_libs/isar_flutter_libs.dart';
// import 'package:path_provider/path_provider.dart';
import 'core/models/chat_message.dart';
import 'core/models/user_profile.dart';
import 'core/models/volunteer_scheme.dart';
import 'core/skill_loader.dart';
import 'features/chat/chatgpt_page.dart';
import 'features/simulator/simulator_page.dart';
import 'features/discover/discover_page.dart';  // 🆕 改为发现页面
import 'features/profile/profile_page.dart';  // 🆕 添加个人中心页面
import 'features/auth/login_page.dart';  // 🆕 添加登录页面
import 'features/plan/plan_page.dart';  // 🆕 添加志愿表页面
import 'features/favorite/favorite_page.dart';  // 🆕 添加收藏页面
import 'features/history/history_page.dart';  // 🆕 添加历史记录页面
import 'features/history/history_detail_page.dart';  // 🆕 添加历史详情页面
import 'features/settings/settings_page.dart';  // 🆕 添加设置页面
import 'features/settings/data_source_page.dart';  // 🆕 添加数据来源说明页面
import 'features/settings/privacy_policy_page.dart';  // 🆕 添加隐私政策页面
import 'features/settings/user_agreement_page.dart';  // 🆕 添加用户协议页面
import 'providers/auth_provider.dart';  // 🆕 添加认证provider
import 'providers/plan_provider.dart';  // 🆕 添加志愿表provider
import 'providers/favorite_provider.dart';  // 🆕 添加收藏provider
import 'providers/history_provider.dart';  // 🆕 添加历史记录provider
import 'shared/theme/chatgpt_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 暂时禁用 Isar 初始化以支持 Web 平台
  // final dir = await getApplicationDocumentsDirectory();
  // final isar = await Isar.open(
  //   [
  //     ChatMessageSchema,
  //     UserProfileSchema,
  //     VolunteerSchemeSchema,
  //     SkillContentSchema,
  //   ],
  //   directory: dir.path,
  // );

  runApp(
    const ProviderScope(
      // 暂时移除 Isar provider
      // overrides: [
      //   isarProvider.overrideWithValue(isar),
      // ],
      child: MyApp(),
    ),
  );
}

// 暂时禁用 Isar provider
// final isarProvider = Provider<Isar>((ref) {
//   throw UnimplementedError('Isar instance must be provided in main()');
// });

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '学锋志愿教练',
      debugShowCheckedModeBanner: false,
      theme: ChatGPTTheme.lightTheme,
      darkTheme: ChatGPTTheme.darkTheme,
      themeMode: ThemeMode.system,
      home: const MainNavigationPage(),
      routes: {
        '/login': (context) => const LoginPage(),
        '/plans': (context) => const PlanPage(),
        '/favorites': (context) => const FavoritePage(),
        '/history': (context) => const HistoryPage(),
        '/history_detail': (context) => const HistoryDetailPage(),
        // 设置相关页面
        '/settings': (context) => const SettingsPage(),
        '/data_source': (context) => const DataSourcePage(),
        '/privacy_policy': (context) => const PrivacyPolicyPage(),
        '/user_agreement': (context) => const UserAgreementPage(),
      },
    );
  }
}

/// 主导航页面（底部 TabBar）
class MainNavigationPage extends ConsumerStatefulWidget {
  const MainNavigationPage({super.key});

  @override
  ConsumerState<MainNavigationPage> createState() => _MainNavigationPageState();
}

class _MainNavigationPageState extends ConsumerState<MainNavigationPage> {
  int _currentIndex = 0;

  late final List<Widget> _pages = [
    const ChatGPTPage(),
    const SimulatorPage(),
    const DiscoverPage(),  // 🆕 改为发现页面
    const ProfilePage(),  // 🆕 添加个人中心页面
  ];

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      body: _pages[_currentIndex],
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: isDark
              ? ChatGPTTheme.darkBackground
              : ChatGPTTheme.lightBackground,
          border: Border(
            top: BorderSide(
              color: isDark
                  ? ChatGPTTheme.darkDivider
                  : ChatGPTTheme.lightDivider,
              width: 1,
            ),
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
          type: BottomNavigationBarType.fixed,
          backgroundColor: isDark
              ? ChatGPTTheme.darkBackground
              : ChatGPTTheme.lightBackground,
          selectedItemColor: ChatGPTTheme.chatGPTGreen,
          unselectedItemColor: isDark
              ? ChatGPTTheme.darkTextSecondary
              : ChatGPTTheme.lightTextSecondary,
          selectedLabelStyle: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
          unselectedLabelStyle: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w400,
          ),
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.chat_outlined),
              activeIcon: Icon(Icons.chat),
              label: '聊天',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.auto_awesome_outlined),
              activeIcon: Icon(Icons.auto_awesome),
              label: '推荐志愿',
            ),
            // 🆕 改为发现
            BottomNavigationBarItem(
              icon: Icon(Icons.whatshot_outlined),
              activeIcon: Icon(Icons.whatshot),
              label: '发现',
            ),
            // 🆕 添加个人中心
            BottomNavigationBarItem(
              icon: Icon(Icons.person_outline),
              activeIcon: Icon(Icons.person),
              label: '我的',
            ),
          ],
        ),
      ),
    );
  }
}
