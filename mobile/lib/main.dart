// mobile/lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:provider/provider.dart';
import 'presentation/providers/auth_provider.dart';
import 'screens/login_screen.dart'; 

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: ".env");
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()..checkAuthStatus()),
      ],
      child: MaterialApp(
        title: 'Moto-Top',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepOrange),
          useMaterial3: true,
        ),
        home: Consumer<AuthProvider>(
          builder: (context, auth, _) {
            if (auth.isLoggedIn) {
              return Scaffold(
                appBar: AppBar(
                  title: const Text('Moto-Top Panel'),
                  actions: [
                    IconButton(
                      icon: const Icon(Icons.logout),
                      onPressed: () => context.read<AuthProvider>().logout(),
                    ),
                  ],
                ),
                body: const Center(
                  child: Text('Sesión iniciada con éxito'),
                ),
              );
            }
            return const LoginScreen();
          },
        ),
      ),
    );
  }
}