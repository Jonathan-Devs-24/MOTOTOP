# desktop/app/core/http_client.py
import requests


class HttpClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None

    def set_token(self, token):
        self.token = token

    # =========================
    # HEADERS JSON
    # =========================
    def _headers(self):
        headers = {
            "Content-Type": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # =========================
    # HEADERS MULTIPART
    # =========================
    def _headers_without_json(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # =========================

    def get(self, endpoint):
        return requests.get(
            f"{self.base_url}{endpoint}",
            headers=self._headers()
        )

    def delete(self, endpoint):
        return requests.delete(
            f"{self.base_url}{endpoint}",
            headers=self._headers()
        )

    def post(self, endpoint, data=None, files=None):
        if files:
            return requests.post(
                f"{self.base_url}{endpoint}",
                data=data,
                files=files,
                headers=self._headers_without_json()
            )
        else:
            return requests.post(
                f"{self.base_url}{endpoint}",
                json=data,
                headers=self._headers()
            )
            
    def put(self, endpoint, data=None, files=None):
        return requests.put(
            f"{self.base_url}{endpoint}",
            data=data,
            files=files,
            headers=self._headers_without_json()
        )