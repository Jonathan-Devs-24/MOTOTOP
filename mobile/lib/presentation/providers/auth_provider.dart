// mobile/lib/presentation/providers/auth_provider.dart
import 'package:flutter/material.dart';
import '../../data/services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();
  bool _isLoading = false;
  bool _isLoggedIn = false;
  String? _errorMessage;

  bool get isLoading => _isLoading;
  bool get isLoggedIn => _isLoggedIn;
  String? get errorMessage => _errorMessage;

  Future<void> checkAuthStatus() async {
    _isLoggedIn = await _authService.isAuthenticated();
    notifyListeners();
  }

  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final success = await _authService.login(username, password);
    _isLoggedIn = success;
    _errorMessage = _authService.lastErrorMessage;
    _isLoading = false;
    notifyListeners();

    return success;
  }

  Future<void> logout() async {
    await _authService.logout();
    _isLoggedIn = false;
    notifyListeners();
  }
}

