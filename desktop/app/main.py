import sys
from PyQt6.QtWidgets import QApplication

from core.config import API_BASE_URL
from core.http_client import HttpClient
from core.auth_store import AuthStore
from services.auth_service import AuthService

from views.login_view import LoginView
from views.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    http = HttpClient(API_BASE_URL)
    auth_store = AuthStore()
    auth_service = AuthService(http)

    login = LoginView(auth_service, auth_store, http)
    main_window = MainWindow(http)

    def on_login_success():
        login.close()
        main_window.show()

    login.login_success.connect(on_login_success)

    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()