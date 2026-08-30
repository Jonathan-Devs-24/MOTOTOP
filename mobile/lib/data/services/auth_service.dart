// mobile/lib/data/services/auth_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../core/api_constants.dart';
import '../../core/storage/secure_storage_service.dart';

class AuthService {
  String? lastErrorMessage;

  Future<bool> login(String username, String password) async {
    lastErrorMessage = null;
    final tokenUrl = Uri.parse('${ApiConstants.baseUrl}${ApiConstants.tokenObtain}');

    try {
      final tokenResponse = await http.post(
        tokenUrl,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );

      if (tokenResponse.statusCode != 200) {
        lastErrorMessage = 'Usuario o contraseña incorrectos';
        return false;
      }

      final tokenData = jsonDecode(tokenResponse.body);
      final accessToken = tokenData['access'];
      final refreshToken = tokenData['refresh'];

      // Validar si el vendedor está activo consultando /vendedores/
      final vendedoresUrl = Uri.parse('${ApiConstants.baseUrl}${ApiConstants.productos}'.replaceAll('productos', 'vendedores'));
      
      final vendResponse = await http.get(
        vendedoresUrl,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
      );

      if (vendResponse.statusCode == 200) {
        final dynamic body = jsonDecode(vendResponse.body);
        
        // DRF puede devolver una lista pura [] o paginada { "results": [] }
        final List<dynamic> vendedores = (body is Map && body.containsKey('results'))
            ? body['results']
            : (body is List ? body : []);

        // Si existe un registro con estado explícito inactivo, frenamos el acceso
        for (var v in vendedores) {
          if (v is Map && v['estado'] == 'inactivo') {
            // Si coincide el usuario o username
            lastErrorMessage = 'Tu cuenta de vendedor se encuentra inactiva.';
            await SecureStorageService.clearTokens();
            return false;
          }
        }
      }

      await SecureStorageService.saveTokens(
        access: accessToken,
        refresh: refreshToken,
      );
      return true;
    } catch (e, stackTrace) {
      print('=== ERROR EN LOGIN ===: $e');
      print(stackTrace);
      lastErrorMessage = 'Error de conexión con el servidor: $e';
      return false;
    }
  }

  Future<void> logout() async {
    await SecureStorageService.clearTokens();
  }

  Future<bool> isAuthenticated() async {
    final token = await SecureStorageService.getAccessToken();
    return token != null && token.isNotEmpty;
  }
}

