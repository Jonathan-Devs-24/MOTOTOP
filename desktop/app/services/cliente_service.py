class ClienteService:

    def __init__(self, http):
        self.http = http

    def listar(self):
        response = self.http.get("clientes/")
        response.raise_for_status()
        return response.json()

    def crear(self, data):
        response = self.http.post("clientes/", data)
        response.raise_for_status()
        return response.json()

    def actualizar(self, cliente_id, data):
        response = self.http.put(f"clientes/{cliente_id}/", data)
        response.raise_for_status()
        return response.json()

    def eliminar(self, cliente_id):
        response = self.http.delete(f"clientes/{cliente_id}/")
        response.raise_for_status()
        return True
