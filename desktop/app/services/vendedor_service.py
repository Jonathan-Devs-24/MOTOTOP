# desktop/app/services/vendedor_service.py
class VendedorService:

    def __init__(self, http):
        self.http = http

    def listar(self):
        response = self.http.get("vendedores/")
        response.raise_for_status()
        return response.json()

    def crear(self, data):
        response = self.http.post("vendedores/", data)
        response.raise_for_status()
        return response.json()

    def actualizar(self, vendedor_id, data):
        response = self.http.put(f"vendedores/{vendedor_id}/", data)
        response.raise_for_status()
        return response.json()

    def eliminar(self, vendedor_id):
        response = self.http.delete(f"vendedores/{vendedor_id}/")
        response.raise_for_status()
        return True

    def cambiar_estado(self, vendedor_id):
        response = self.http.post(f"vendedores/{vendedor_id}/cambiar_estado/")
        response.raise_for_status()
        return response.json()