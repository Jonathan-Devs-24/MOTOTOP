class PedidoService:

    def __init__(self, http):
        self.http = http

    def listar(self):
        response = self.http.get("pedidos/")
        response.raise_for_status()
        return response.json()

    def crear(self, data):
        response = self.http.post("pedidos/", data)
        response.raise_for_status()
        return response.json()

    def confirmar(self, pedido_id):
        response = self.http.post(f"pedidos/{pedido_id}/confirmar/")
        response.raise_for_status()
        return response.json()
