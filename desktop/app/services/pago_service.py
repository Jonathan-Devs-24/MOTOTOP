class PagoService:

    def __init__(self, http):
        self.http = http

    def listar(self):
        response = self.http.get("pagos/")
        return response.json()

    def obtener(self, pago_id):
        response = self.http.get(f"pagos/{pago_id}/")
        return response.json()

    def crear(self, data):
        response = self.http.post("pagos/", data=data)
        return response.json()

    def actualizar(self, pago_id, data):
        response = self.http.put(
            f"pagos/{pago_id}/",
            data=data
        )
        return response.json()

    def eliminar(self, pago_id):
        self.http.delete(f"pagos/{pago_id}/")
        
        
    def listar_por_factura(self, factura_id):

        response = self.http.get(
            f"pagos/?factura={factura_id}"
        )

        response.raise_for_status()

        return response.json()