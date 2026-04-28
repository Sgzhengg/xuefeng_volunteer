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
import 'features/chat/chat_page.dart';
import 'features/chat/chat_page_minimal.dart';
import 'features/simulator/simulator_page.dart';
import 'config/ui_config.dart';
import 'features/profile/profile_page.dart';
import 'features/history/history_page.dart';
import 'shared/theme/app_theme.dart';

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
      theme: AppTheme.lightTheme,
      home: const MainNavigationPage(),
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
    UIConfig.useMinimalStyle ? const ChatPageMinimal() : const ChatPage(),
    const SimulatorPage(),
    const HistoryPage(),
    const ProfilePage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_currentIndex],
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          boxShadow: AppTheme.shadowLight,
          border: const Border(
            top: BorderSide(
              color: AppTheme.surfaceContainerHighest,
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
          backgroundColor: AppTheme.white,
          selectedItemColor: AppTheme.primaryBlue,
          unselectedItemColor: AppTheme.mediumGray,
          selectedLabelStyle: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w500,
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
              icon: Icon(Icons.architecture_outlined),
              activeIcon: Icon(Icons.architecture),
              label: '模拟器',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.history_outlined),
              activeIcon: Icon(Icons.history),
              label: '历史',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_outline),
              activeIcon: Icon(Icons.person),
              label: '档案',
            ),
          ],
        ),
      ),
    );
  }
}
