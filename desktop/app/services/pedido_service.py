# desktop/app/services/pedido_service.py
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

    def cancelar(self, pedido_id):
        response = self.http.post(f"pedidos/{pedido_id}/cancelar/")
        response.raise_for_status()
        return response.json()

    def generar_factura(self, pedido_id, tipo_comprobante='B'):
        data = {
            'pedido': pedido_id,
            'tipo_comprobante': tipo_comprobante
        }
        response = self.http.post("facturas/", data)
        response.raise_for_status()
        return response.json()

    def obtener_factura(self, pedido_id):
        response = self.http.get(f"pedidos/{pedido_id}/factura/")
        response.raise_for_status()
        return response.json()


    def obtener(self, pedido_id):
            response = self.http.get(f"pedidos/{pedido_id}/")
            response.raise_for_status()
            return response.json()