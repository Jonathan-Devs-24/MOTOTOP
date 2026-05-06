# desktop/app/services/compra_service.py

class CompraService:

    def __init__(self, http):
        self.http = http

    def listar(self):
        response = self.http.get("compras/")
        response.raise_for_status()
        return response.json()

    def crear(self, data):
        response = self.http.post("compras/", data)
        response.raise_for_status()
        return response.json()

    def recibir(self, compra_id):
        response = self.http.post(
            f"compras/{compra_id}/recibir/"
        )
        response.raise_for_status()
        return response.json()