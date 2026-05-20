# desktop/app/services/pago_service.py

class PagoService:
    def __init__(self, http):
        self.http = http

    def listar(self):
        response = self.http.get("pagos/")
        return response.json()

    def listar_por_factura(self, factura_id):
        """
        Obtiene todos los pagos y filtra los que pertenecen
        a la factura indicada.

        La API devuelve el campo factura como ID numérico.
        Ejemplo:
        {
            "factura": 3,
            "monto": "1000.00",
            ...
        }
        """
        pagos = self.listar()

        # Si la API usa paginación DRF
        if isinstance(pagos, dict):
            pagos = pagos.get("results", [])

        pagos_filtrados = []

        for pago in pagos:
            if pago.get("factura") == factura_id:
                pagos_filtrados.append(pago)

        return pagos_filtrados

    def obtener(self, pago_id):
        response = self.http.get(f"pagos/{pago_id}/")
        return response.json()

    def crear(self, data):
        response = self.http.post("pagos/", data=data)
        return response.json()

    def actualizar(self, pago_id, data):
        response = self.http.put(f"pagos/{pago_id}/", data=data)
        return response.json()

    def eliminar(self, pago_id):
        self.http.delete(f"pagos/{pago_id}/")