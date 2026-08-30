// mobile/lib/core/api_constants.dart
import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiConstants {
  // Toma la URL del .env o usa un fallback seguro
  static String get baseUrl => dotenv.env['API_BASE_URL'] ?? 'http://127.0.0.1:8000/api';

  static const String tokenObtain = '/token/';
  static const String tokenRefresh = '/token/refresh/';
  static const String productos = '/productos/';
  static const String clientes = '/clientes/';
  static const String pedidos = '/pedidos/';
  static const String geminiChat = '/ai/chat/';
}