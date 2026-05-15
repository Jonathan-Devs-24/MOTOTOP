# desktop/app/services/factura_service.py

class FacturaService:

    def __init__(self, http):
        self.http = http

    def listar(self):
        response = self.http.get("facturas/")
        response.raise_for_status()
        return response.json()

    def obtener(self, factura_id):
        response = self.http.get(f"facturas/{factura_id}/")
        response.raise_for_status()
        return response.json()
