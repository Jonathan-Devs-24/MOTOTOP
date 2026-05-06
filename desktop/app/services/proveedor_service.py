# desktop/app/services/proveedor_service.py
class ProveedorService:

    def __init__(self, http):
        self.http = http

    def listar(self):
        r = self.http.get("proveedores/")
        r.raise_for_status()
        return r.json()

    def crear(self, data):
        r = self.http.post("proveedores/", data)
        r.raise_for_status()
        return r.json()

    def eliminar(self, proveedor_id):
        r = self.http.delete(f"proveedores/{proveedor_id}/")
        r.raise_for_status()
        
    