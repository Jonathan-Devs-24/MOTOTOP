from core.http_client import HttpClient


class InformeService:

    def __init__(self, http: HttpClient):
        self.http = http

    def _build_query(self, fecha_inicio=None, fecha_fin=None):
        params = []
        if fecha_inicio:
            params.append(f"fecha_inicio={fecha_inicio}")
        if fecha_fin:
            params.append(f"fecha_fin={fecha_fin}")
        return f"?{'&'.join(params)}" if params else ""

    def ventas(self, fecha_inicio=None, fecha_fin=None):
        query = self._build_query(fecha_inicio, fecha_fin)
        response = self.http.get(f"informes/ventas/{query}")
        response.raise_for_status()
        return response.json()

    def venta_por_vendedor(self, fecha_inicio=None, fecha_fin=None):
        query = self._build_query(fecha_inicio, fecha_fin)
        response = self.http.get(f"informes/venta-por-vendedor/{query}")
        response.raise_for_status()
        return response.json()

    def pedidos_pendientes_envio(self):
        response = self.http.get("informes/pedidos-pendientes-envio/")
        response.raise_for_status()
        return response.json()

    def saldo_clientes(self):
        response = self.http.get("informes/saldo-clientes/")
        response.raise_for_status()
        return response.json()

    def facturas_pendientes_cobro(self):
        response = self.http.get("informes/facturas-pendientes-cobro/")
        response.raise_for_status()
        return response.json()
