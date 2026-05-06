# desktop/app/services/producto_promocion_service.py
class ProductoPromocionService:

    def __init__(self, http):
        self.http = http

    def listar(self):
        response = self.http.get("producto-promociones/")

        response.raise_for_status()

        return response.json()

    def crear(self, data):
        response = self.http.post("producto-promociones/", data)

        response.raise_for_status()

        return response.json()
    
    def eliminar(self, promocion_id):

        response = self.http.delete(
            f"producto-promociones/{promocion_id}/"
        )

        response.raise_for_status()
        
        