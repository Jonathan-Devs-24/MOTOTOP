# desktop/app/views/login_view.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal


class LoginView(QWidget):

    login_success = pyqtSignal()

    def __init__(self, auth_service, auth_store, http_client):
        super().__init__()

        self.auth_service = auth_service
        self.auth_store = auth_store
        self.http = http_client

        self.setWindowTitle("Login")

        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Usuario")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.button = QPushButton("Login")
        self.button.clicked.connect(self.handle_login)

        self.status = QLabel("")

        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.button)
        layout.addWidget(self.status)

        self.setLayout(layout)

    def handle_login(self):
        try:
            data = self.auth_service.login(
                self.username.text(),
                self.password.text()
            )

            self.auth_store.set_tokens(
                data["access"],
                data["refresh"]
            )

            self.http.set_token(self.auth_store.access)

            self.status.setText("Login OK")

            self.login_success.emit()

        except Exception as e:
            self.status.setText(str(e))