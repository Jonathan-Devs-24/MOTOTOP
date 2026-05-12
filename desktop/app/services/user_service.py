# desktop/app/services/user_service.py
class UserService:

    def __init__(self, http):
        self.http = http

    def crear(self, data):
        response = self.http.post("users/", data)
        response.raise_for_status()
        return response.json()

    def listar(self):
        response = self.http.get("users/")
        response.raise_for_status()
        return response.json()

    def obtener(self, user_id):
        response = self.http.get(f"users/{user_id}/")
        response.raise_for_status()
        return response.json()