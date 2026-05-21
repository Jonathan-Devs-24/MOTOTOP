class PagoService:

    def __init__(self, http):
        self.http = http

    def listar(self):
        response = self.http.get("pagos/")
        return response.json()

    def listar_por_factura(self, factura_id):

        pagos = self.listar()

        if isinstance(pagos, dict):
            pagos = pagos.get("results", [])

        return [
            pago
            for pago in pagos
            if pago.get("factura") == factura_id
        ]

    def obtener(self, pago_id):
        response = self.http.get(f"pagos/{pago_id}/")
        response.raise_for_status()
        return response.json()

    def crear(self, data):
        response = self.http.post(
            "pagos/",
            data=data
        )

        response.raise_for_status()

        return response.json()

    def actualizar(self, pago_id, data):

        response = self.http.put(
            f"pagos/{pago_id}/",
            data=data
        )

        response.raise_for_status()

        return response.json()

    def eliminar(self, pago_id):

        response = self.http.delete(
            f"pagos/{pago_id}/"
        )

        response.raise_for_status()