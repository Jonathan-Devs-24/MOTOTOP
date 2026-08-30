// mobile/lib/core/storage/secure_storage_service.dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorageService {
  static const _storage = FlutterSecureStorage();
  static const _keyAccess = 'jwt_access_token';
  static const _keyRefresh = 'jwt_refresh_token';

  static Future<void> saveTokens({required String access, required String refresh}) async {
    await _storage.write(key: _keyAccess, value: access);
    await _storage.write(key: _keyRefresh, value: refresh);
  }

  static Future<String?> getAccessToken() async {
    return await _storage.read(key: _keyAccess);
  }

  static Future<String?> getRefreshToken() async {
    return await _storage.read(key: _keyRefresh);
  }

  static Future<void> clearTokens() async {
    await _storage.delete(key: _keyAccess);
    await _storage.delete(key: _keyRefresh);
  }
}