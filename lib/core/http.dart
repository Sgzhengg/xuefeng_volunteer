import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

class ApiClient {
  static const String baseUrl = 'http://localhost:8000';

  static Future<String> _getToken() async {
    try {
      final appDocDir = await getApplicationDocumentsDirectory();
      final tokenFile = File('${appDocDir.path}/auth_token.txt');

      if (await tokenFile.exists()) {
        return await tokenFile.readAsString();
      }
      return '';
    } catch (e) {
      print('Error reading token: $e');
      return '';
    }
  }

  static Future<void> _saveToken(String token) async {
    try {
      final appDocDir = await getApplicationDocumentsDirectory();
      final tokenFile = File('${appDocDir.path}/auth_token.txt');
      await tokenFile.writeAsString(token);
    } catch (e) {
      print('Error saving token: $e');
    }
  }

  static Future<Map<String, String>> _getHeaders() async {
    final token = await _getToken();

    return {
      'Content-Type': 'application/json',
      if (token.isNotEmpty) 'Authorization': 'Bearer $token',
    };
  }

  static Future<http.Response> get(String endpoint) async {
    final headers = await _getHeaders();
    final uri = Uri.parse('$baseUrl$endpoint');

    try {
      final response = await http.get(uri, headers: headers).timeout(
        const Duration(seconds: 30),
      );
      return _handleResponse(response);
    } catch (e) {
      throw _handleError(e);
    }
  }

  static Future<http.Response> post(String endpoint, {Map<String, dynamic>? body}) async {
    final headers = await _getHeaders();
    final uri = Uri.parse('$baseUrl$endpoint');

    try {
      final response = await http.post(
        uri,
        headers: headers,
        body: body != null ? jsonEncode(body) : null,
      ).timeout(
        const Duration(seconds: 30),
      );
      return _handleResponse(response);
    } catch (e) {
      throw _handleError(e);
    }
  }

  static Future<http.Response> delete(String endpoint) async {
    final headers = await _getHeaders();
    final uri = Uri.parse('$baseUrl$endpoint');

    try {
      final response = await http.delete(uri, headers: headers).timeout(
        const Duration(seconds: 30),
      );
      return _handleResponse(response);
    } catch (e) {
      throw _handleError(e);
    }
  }

  static http.Response _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return response;
    } else {
      throw ApiException(
        'API Error: ${response.statusCode}',
        response.statusCode,
        response.body,
      );
    }
  }

  static Exception _handleError(dynamic error) {
    if (error is http.ClientException) {
      return NetworkException('Network error: ${error.message}');
    } else if (error is ApiException) {
      return error;
    } else {
      return UnknownException('Unknown error: ${error.toString()}');
    }
  }
}

class ApiException implements Exception {
  final String message;
  final int statusCode;
  final String? body;

  ApiException(this.message, this.statusCode, [this.body]);

  @override
  String toString() => message;
}

class NetworkException implements Exception {
  final String message;

  NetworkException(this.message);

  @override
  String toString() => message;
}

class UnknownException implements Exception {
  final String message;

  UnknownException(this.message);

  @override
  String toString() => message;
}
