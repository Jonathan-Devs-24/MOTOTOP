# desktop/app/services/envio_service.py

class EnvioService:

    def __init__(self, http):
        self.http = http

    # =========================
    # MÉTODOS GENÉRICOS
    # =========================

    def get(self, endpoint=""):
        response = self.http.get(f"envios/{endpoint}")
        response.raise_for_status()
        return response.json()

    def post(self, endpoint="", data=None):
        response = self.http.post(f"envios/{endpoint}", data or {})
        response.raise_for_status()
        return response.json()

    def put(self, endpoint="", data=None):
        response = self.http.put(f"envios/{endpoint}", data or {})
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint=""):
        response = self.http.delete(f"envios/{endpoint}")
        response.raise_for_status()

    # =========================
    # CRUD
    # =========================

    def listar(self):
        return self.get()

    def obtener(self, envio_id):
        return self.get(f"{envio_id}/")

    def crear(self, data):
        return self.post("", data)

    def actualizar(self, envio_id, data):
        return self.put(f"{envio_id}/", data)

    def eliminar(self, envio_id):
        self.delete(f"{envio_id}/")