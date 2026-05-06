# desktop/app/services/auth_service.py
from core.http_client import HttpClient


class AuthService:

    def __init__(self, http: HttpClient):
        self.http = http

    def login(self, username: str, password: str):
        response = self.http.post("token/", {
            "username": username,
            "password": password
        })
        response.raise_for_status()
        return response.json()

    def refresh(self, refresh_token: str):
        response = self.http.post("token/refresh/", {
            "refresh": refresh_token
        })
        response.raise_for_status()
        return response.json()