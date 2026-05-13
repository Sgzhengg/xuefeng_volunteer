import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/services.dart';
import '../../shared/theme/app_theme.dart';
import '../../providers/auth_provider.dart';

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> {
  final _phoneController = TextEditingController();
  final _codeController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  bool _isLoading = false;
  bool _canResend = true;
  int _countdown = 60;

  @override
  void dispose() {
    _phoneController.dispose();
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _sendCode() async {
    if (_phoneController.text.isEmpty) {
      _showError('请输入手机号码');
      return;
    }

    if (!RegExp(r'^1[3-9]\d{9}$').hasMatch(_phoneController.text)) {
      _showError('请输入正确的手机号码');
      return;
    }

    setState(() {
      _canResend = false;
      _countdown = 60;
    });

    // 调用API发送验证码
    final success = await ref.read(authProvider.notifier).sendCode(_phoneController.text);

    if (!success && mounted) {
      _showError('发送验证码失败，请重试');
      setState(() {
        _canResend = true;
      });
      return;
    }

    // 倒计时
    for (int i = 60; i > 0; i--) {
      await Future.delayed(const Duration(seconds: 1));
      if (mounted) {
        setState(() {
          _countdown = i - 1;
        });
      }
    }

    if (mounted) {
      setState(() {
        _canResend = true;
      });
    }
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isLoading = true);

    try {
      final success = await ref.read(authProvider.notifier).login(
            _phoneController.text,
            _codeController.text,
          );

      if (success && mounted) {
        _showSuccess('登录成功');
        Navigator.pop(context);
      } else if (mounted) {
        _showError('登录失败，请检查验证码');
      }
    } catch (e) {
      _showError('登录失败：$e');
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppTheme.red,
      ),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppTheme.green,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surfaceColor,
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(AppTheme.spacingLg),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: AppTheme.spacingXl),

                  // 返回按钮
                  GestureDetector(
                    onTap: () => Navigator.pop(context),
                    child: const Icon(
                      Icons.arrow_back,
                      color: AppTheme.primaryBlue,
                    ),
                  ),

                  const SizedBox(height: AppTheme.spacingXl * 2),

                  // 标题
                  Text(
                    '欢迎登录',
                    style: AppTheme.displayLarge.copyWith(
                      fontWeight: FontWeight.bold,
                      color: AppTheme.primaryBlue,
                    ),
                  ),

                  const SizedBox(height: AppTheme.spacingSm),

                  Text(
                    '登录以解锁完整功能',
                    style: AppTheme.bodyMedium.copyWith(
                      color: AppTheme.mediumGray,
                    ),
                  ),

                  const SizedBox(height: AppTheme.spacingXl * 2),

                  // 手机号输入
                  Text(
                    '手机号',
                    style: AppTheme.titleSmall.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),

                  const SizedBox(height: AppTheme.spacingSm),

                  TextFormField(
                    controller: _phoneController,
                    keyboardType: TextInputType.phone,
                    inputFormatters: [
                      FilteringTextInputFormatter.digitsOnly,
                      LengthLimitingTextInputFormatter(11),
                    ],
                    decoration: InputDecoration(
                      hintText: '请输入手机号',
                      prefixIcon: const Icon(Icons.phone),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                        borderSide: BorderSide(color: AppTheme.mediumGray.withOpacity(0.3)),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                        borderSide: const BorderSide(color: AppTheme.primaryBlue, width: 2),
                      ),
                    ),
                    validator: (value) {
                      if (value?.isEmpty ?? true) {
                        return '请输入手机号';
                      }
                      if (!RegExp(r'^1[3-9]\d{9}$').hasMatch(value!)) {
                        return '请输入正确的手机号';
                      }
                      return null;
                    },
                  ),

                  const SizedBox(height: AppTheme.spacingLg),

                  // 验证码输入
                  Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '验证码',
                              style: AppTheme.titleSmall.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: AppTheme.spacingSm),
                            TextFormField(
                              controller: _codeController,
                              keyboardType: TextInputType.number,
                              inputFormatters: [
                                FilteringTextInputFormatter.digitsOnly,
                                LengthLimitingTextInputFormatter(6),
                              ],
                              decoration: InputDecoration(
                                hintText: '请输入验证码',
                                prefixIcon: const Icon(Icons.lock),
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                                ),
                                enabledBorder: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                                  borderSide: BorderSide(color: AppTheme.mediumGray.withOpacity(0.3)),
                                ),
                                focusedBorder: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                                  borderSide: const BorderSide(color: AppTheme.primaryBlue, width: 2),
                                ),
                              ),
                              validator: (value) {
                                if (value?.isEmpty ?? true) {
                                  return '请输入验证码';
                                }
                                return null;
                              },
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(width: AppTheme.spacingMd),

                      // 发送验证码按钮
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          const SizedBox(height: 32), // Align with input field
                          SizedBox(
                            height: 56,
                            child: ElevatedButton(
                              onPressed: _canResend ? _sendCode : null,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: _canResend
                                    ? AppTheme.primaryBlue
                                    : AppTheme.mediumGray,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                                ),
                              ),
                              child: Text(
                                _canResend ? '发送验证码' : '${_countdown}s',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),

                  const SizedBox(height: AppTheme.spacingSm),

                  // MVP提示
                  Container(
                    padding: const EdgeInsets.all(AppTheme.spacingSm),
                    decoration: BoxDecoration(
                      color: AppTheme.warningBackground,
                      borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                      border: Border.all(
                        color: AppTheme.warningBorder,
                      ),
                    ),
                    child: Row(
                      children: [
                        const Icon(
                          Icons.info,
                          size: 16,
                          color: AppTheme.orange,
                        ),
                        const SizedBox(width: AppTheme.spacingXs),
                        Expanded(
                          child: Text(
                            'MVP阶段：验证码固定为 123456',
                            style: AppTheme.bodySmall.copyWith(
                              color: AppTheme.orange,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: AppTheme.spacingXl * 2),

                  // 登录按钮
                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _login,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.primaryBlue,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                        ),
                      ),
                      child: _isLoading
                          ? const SizedBox(
                              width: 24,
                              height: 24,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : const Text(
                              '登录',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                            ),
                    ),
                  ),

                  const SizedBox(height: AppTheme.spacingLg),

                  // 用户协议
                  Row(
                    children: [
                      Checkbox(
                        value: true,
                        onChanged: (value) {},
                        activeColor: AppTheme.primaryBlue,
                      ),
                      Expanded(
                        child: Wrap(
                          children: [
                            const Text('我已阅读并同意'),
                            GestureDetector(
                              onTap: () {
                                // TODO: 打开用户协议
                              },
                              child: const Text(
                                '《用户协议》',
                                style: TextStyle(
                                  color: AppTheme.primaryBlue,
                                  decoration: TextDecoration.underline,
                                ),
                              ),
                            ),
                            const Text('和'),
                            GestureDetector(
                              onTap: () {
                                // TODO: 打开隐私政策
                              },
                              child: const Text(
                                '《隐私政策》',
                                style: TextStyle(
                                  color: AppTheme.primaryBlue,
                                  decoration: TextDecoration.underline,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}