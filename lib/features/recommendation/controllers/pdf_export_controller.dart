import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:intl/intl.dart';
import '../../../core/api/pdf_export_api_service.dart';
import '../models/recommendation_models.dart';

/// PDF Export Controller
class PDFExportController extends ChangeNotifier {
  final PDFExportApiService _apiService = PDFExportApiService();

  bool _isExporting = false;
  String? _lastExportPath;

  bool get isExporting => _isExporting;
  String? get lastExportPath => _lastExportPath;

  /// Export recommendation result as PDF
  Future<String?> exportToPDF({
    required RecommendationResult result,
    required BuildContext context,
  }) async {
    _isExporting = true;
    notifyListeners();

    try {
      // Generate PDF bytes
      final pdfBytes = await _apiService.generateEnhancedPDF(result: result);

      // Save to file
      final filePath = await _savePDFToFile(pdfBytes, result);

      _lastExportPath = filePath;
      _isExporting = false;
      notifyListeners();

      // Show success message
      if (context.mounted) {
        _showSuccessSnackBar(
          context,
          'PDF已保存到: $filePath',
        );
      }

      return filePath;
    } catch (e) {
      _isExporting = false;
      notifyListeners();

      if (context.mounted) {
        _showErrorSnackBar(
          context,
          'PDF导出失败: $e',
        );
      }

      return null;
    }
  }

  /// Export recommendation result as HTML
  Future<String?> exportToHTML({
    required RecommendationResult result,
    required BuildContext context,
  }) async {
    _isExporting = true;
    notifyListeners();

    try {
      // Generate HTML content
      final htmlContent = await _apiService.exportToHTML(result: result);

      // Save to file
      final filePath = await _saveHTMLToFile(htmlContent, result);

      _lastExportPath = filePath;
      _isExporting = false;
      notifyListeners();

      // Show success message
      if (context.mounted) {
        _showSuccessSnackBar(
          context,
          'HTML已保存到: $filePath',
        );
      }

      return filePath;
    } catch (e) {
      _isExporting = false;
      notifyListeners();

      if (context.mounted) {
        _showErrorSnackBar(
          context,
          'HTML导出失败: $e',
        );
      }

      return null;
    }
  }

  /// Share PDF report
  Future<void> sharePDF({
    required RecommendationResult result,
    required BuildContext context,
  }) async {
    _isExporting = true;
    notifyListeners();

    try {
      // Generate PDF bytes
      final pdfBytes = await _apiService.generateEnhancedPDF(result: result);

      // Save to temporary file
      final filePath = await _savePDFToTempFile(pdfBytes, result);

      _isExporting = false;
      notifyListeners();

      // Share file
      if (context.mounted) {
        await Share.shareXFiles(
          [XFile(filePath)],
          subject: '学锋志愿教练 - 推荐报告',
          text: '${result.basicInfo.province} ${result.basicInfo.score}分 志愿推荐方案',
        );
      }
    } catch (e) {
      _isExporting = false;
      notifyListeners();

      if (context.mounted) {
        _showErrorSnackBar(
          context,
          '分享失败: $e',
        );
      }
    }
  }

  /// Share HTML report
  Future<void> shareHTML({
    required RecommendationResult result,
    required BuildContext context,
  }) async {
    _isExporting = true;
    notifyListeners();

    try {
      // Generate HTML content
      final htmlContent = await _apiService.exportToHTML(result: result);

      // Save to temporary file
      final filePath = await _saveHTMLToTempFile(htmlContent, result);

      _isExporting = false;
      notifyListeners();

      // Share file
      if (context.mounted) {
        await Share.shareXFiles(
          [XFile(filePath)],
          subject: '学锋志愿教练 - 推荐报告',
          text: '${result.basicInfo.province} ${result.basicInfo.score}分 志愿推荐方案',
        );
      }
    } catch (e) {
      _isExporting = false;
      notifyListeners();

      if (context.mounted) {
        _showErrorSnackBar(
          context,
          '分享失败: $e',
        );
      }
    }
  }

  /// Save PDF to persistent storage
  Future<String> _savePDFToFile(Uint8List pdfBytes, RecommendationResult result) async {
    final directory = await getApplicationDocumentsDirectory();
    final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
    final filename = '志愿推荐_${result.basicInfo.score}分_$timestamp.pdf';
    final file = File('${directory.path}/$filename');
    await file.writeAsBytes(pdfBytes);
    return file.path;
  }

  /// Save HTML to persistent storage
  Future<String> _saveHTMLToFile(String htmlContent, RecommendationResult result) async {
    final directory = await getApplicationDocumentsDirectory();
    final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
    final filename = '志愿推荐_${result.basicInfo.score}分_$timestamp.html';
    final file = File('${directory.path}/$filename');
    await file.writeAsString(htmlContent);
    return file.path;
  }

  /// Save PDF to temporary file for sharing
  Future<String> _savePDFToTempFile(Uint8List pdfBytes, RecommendationResult result) async {
    final directory = await getTemporaryDirectory();
    final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
    final filename = '志愿推荐_${result.basicInfo.score}分_$timestamp.pdf';
    final file = File('${directory.path}/$filename');
    await file.writeAsBytes(pdfBytes);
    return file.path;
  }

  /// Save HTML to temporary file for sharing
  Future<String> _saveHTMLToTempFile(String htmlContent, RecommendationResult result) async {
    final directory = await getTemporaryDirectory();
    final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
    final filename = '志愿推荐_${result.basicInfo.score}分_$timestamp.html';
    final file = File('${directory.path}/$filename');
    await file.writeAsString(htmlContent);
    return file.path;
  }

  /// Show success snackbar
  void _showSuccessSnackBar(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(Icons.check_circle_rounded, color: Colors.white),
            SizedBox(width: 8),
            Expanded(child: Text(message)),
          ],
        ),
        backgroundColor: Colors.green,
        duration: Duration(seconds: 3),
      ),
    );
  }

  /// Show error snackbar
  void _showErrorSnackBar(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(Icons.error_rounded, color: Colors.white),
            SizedBox(width: 8),
            Expanded(child: Text(message)),
          ],
        ),
        backgroundColor: Colors.red,
        duration: Duration(seconds: 4),
      ),
    );
  }

  @override
  void dispose() {
    _apiService.dispose();
    super.dispose();
  }
}
