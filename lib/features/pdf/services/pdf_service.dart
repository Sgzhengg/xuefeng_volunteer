import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import '../models/pdf_report_models.dart';

class PDFService {
  /// 生成志愿建议 PDF 报告
  Future<File> generateVolunteerReport(PDFReportData reportData) async {
    final pdf = pw.Document();

    // 使用基础字体（中文字符支持有限）
    pdf.addPage(
      pw.Page(
        margin: const pw.EdgeInsets.all(32),
        build: (pw.Context context) {
          return pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [
              // 标题
              _buildTitle(reportData.title),
              pw.SizedBox(height: 20),

              // 生成时间
              _buildSubtitle("生成时间：${reportData.generatedAt}"),
              pw.SizedBox(height: 30),

              // 用户档案
              _buildSectionTitle("👤 用户档案"),
              pw.SizedBox(height: 10),
              _buildUserProfile(reportData.userProfile),
              pw.SizedBox(height: 20),

              // 数据摘要
              _buildSectionTitle("📊 数据分析"),
              pw.SizedBox(height: 10),
              _buildDataSummary(reportData.dataSummary),
              pw.SizedBox(height: 20),

              // 关键建议
              _buildSectionTitle("💡 关键建议"),
              pw.SizedBox(height: 10),
              _buildKeyRecommendations(reportData.keyRecommendations),
              pw.SizedBox(height: 20),

              // 免责声明
              _buildSectionTitle("⚠️ 免责声明"),
              pw.SizedBox(height: 10),
              _buildDisclaimer(reportData.disclaimer),
            ],
          );
        },
      ),
    );

    // 保存文件
    final output = await getTemporaryDirectory();
    final file = File("${output.path}/志愿填报建议报告_${DateTime.now().millisecondsSinceEpoch}.pdf");
    await file.writeAsBytes(await pdf.save());

    return file;
  }

  pw.Widget _buildTitle(String title) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text(
          title,
          style: pw.TextStyle(
            fontSize: 28,
            fontWeight: pw.FontWeight.bold,
            color: PdfColors.blue900,
          ),
        ),
        pw.Divider(thickness: 2, color: PdfColors.blue300),
      ],
    );
  }

  pw.Widget _buildSubtitle(String subtitle) {
    return pw.Text(
      subtitle,
      style: pw.TextStyle(
        fontSize: 12,
        color: PdfColors.grey700,
      ),
    );
  }

  pw.Widget _buildSectionTitle(String title) {
    return pw.Container(
      padding: const pw.EdgeInsets.symmetric(vertical: 8),
      child: pw.Text(
        title,
        style: pw.TextStyle(
          fontSize: 18,
          fontWeight: pw.FontWeight.bold,
          color: PdfColors.blue800,
        ),
      ),
    );
  }

  pw.Widget _buildUserProfile(UserProfileData profile) {
    return pw.Container(
      padding: const pw.EdgeInsets.all(12),
      decoration: pw.BoxDecoration(
        color: PdfColors.blue50,
        borderRadius: pw.BorderRadius.circular(8),
      ),
      child: pw.Wrap(
        spacing: 10,
        runSpacing: 10,
        children: [
          _buildInfoItem("分数", profile.score),
          _buildInfoItem("省份", profile.province),
          _buildInfoItem("选科", profile.selectedSubjects),
          _buildInfoItem("家庭背景", profile.familyBackground),
          _buildInfoItem("兴趣方向", profile.interests),
        ],
      ),
    );
  }

  pw.Widget _buildInfoItem(String label, String value) {
    return pw.Container(
      padding: const pw.EdgeInsets.all(8),
      child: pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
          pw.Text(
            label,
            style: pw.TextStyle(
              fontSize: 10,
              color: PdfColors.grey700,
            ),
          ),
          pw.SizedBox(height: 4),
          pw.Text(
            value,
            style: pw.TextStyle(
              fontSize: 14,
              fontWeight: pw.FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  pw.Widget _buildDataSummary(DataSummary summary) {
    final children = <pw.Widget>[];

    if (summary.admissionProbability != null) {
      children.add(_buildDataCard("录取概率", summary.admissionProbability!));
    }
    if (summary.universityInfo != null) {
      children.add(_buildDataCard("院校详情", summary.universityInfo!));
    }
    if (summary.majorEmployment != null) {
      children.add(_buildDataCard("专业就业", summary.majorEmployment!));
    }

    return pw.Column(
      children: children,
    );
  }

  pw.Widget _buildDataCard(String title, Map<String, dynamic> data) {
    return pw.Container(
      margin: const pw.EdgeInsets.only(bottom: 12),
      padding: const pw.EdgeInsets.all(12),
      decoration: pw.BoxDecoration(
        border: pw.Border.all(color: PdfColors.grey300),
        borderRadius: pw.BorderRadius.circular(8),
      ),
      child: pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
          pw.Text(
            title,
            style: pw.TextStyle(
              fontSize: 14,
              fontWeight: pw.FontWeight.bold,
            ),
          ),
          pw.SizedBox(height: 8),
          ...data.entries.map((entry) {
            return pw.Padding(
              padding: const pw.EdgeInsets.symmetric(vertical: 4),
              child: pw.Row(
                children: [
                  pw.Expanded(
                    child: pw.Text(
                      entry.key,
                      style: pw.TextStyle(fontSize: 12),
                    ),
                  ),
                  pw.Expanded(
                    child: pw.Text(
                      entry.value.toString(),
                      style: pw.TextStyle(
                        fontSize: 12,
                        fontWeight: pw.FontWeight.bold,
                      ),
                      textAlign: pw.TextAlign.right,
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  pw.Widget _buildKeyRecommendations(List<String> recommendations) {
    return pw.Column(
      children: recommendations.asMap().entries.map((entry) {
        return pw.Container(
          margin: const pw.EdgeInsets.only(bottom: 8),
          padding: const pw.EdgeInsets.all(12),
          decoration: pw.BoxDecoration(
            border: pw.Border.all(color: PdfColors.amber300),
            borderRadius: pw.BorderRadius.circular(8),
            color: PdfColors.amber50,
          ),
          child: pw.Row(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [
              pw.Container(
                margin: const pw.EdgeInsets.only(right: 8),
                child: pw.Text(
                  "${entry.key + 1}.",
                  style: pw.TextStyle(
                    fontSize: 14,
                    fontWeight: pw.FontWeight.bold,
                    color: PdfColors.amber800,
                  ),
                ),
              ),
              pw.Expanded(
                child: pw.Text(
                  entry.value,
                  style: pw.TextStyle(fontSize: 12),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  pw.Widget _buildDisclaimer(String disclaimer) {
    return pw.Container(
      padding: const pw.EdgeInsets.all(12),
      decoration: pw.BoxDecoration(
        color: PdfColors.orange50,
        border: pw.Border.all(color: PdfColors.orange300),
        borderRadius: pw.BorderRadius.circular(8),
      ),
      child: pw.Text(
        disclaimer,
        style: pw.TextStyle(
          fontSize: 10,
          color: PdfColors.orange900,
        ),
      ),
    );
  }

  /// 打开 PDF 文件
  Future<void> openPDF(File file) async {
    // 使用 printing package 打开 PDF
    await Printing.layoutPdf(
      onLayout: (format) => file.readAsBytes(),
      name: '志愿填报建议报告.pdf',
    );
  }

  /// 分享 PDF 文件
  Future<void> sharePDF(File file) async {
    // TODO: 实现 share_plus
  }
}
