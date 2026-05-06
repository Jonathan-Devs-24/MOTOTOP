# desktop/app/services/promocion_service.py
class PromocionService:

    def __init__(self, http):
        self.http = http

    def listar(self):
        response = self.http.get("promociones/")

        response.raise_for_status()

        return response.json()

    def crear(self, data):
        response = self.http.post("promociones/", data)

        response.raise_for_status()

        return response.json()