# desktop/app/services/producto_services.py
from core.http_client import HttpClient


class ProductoService:

    def __init__(self, http: HttpClient):
        self.http = http

    def listar(self, page=1):
        response = self.http.get(f"productos/?page={page}")
        response.raise_for_status()
        return response.json()

    def obtener(self, producto_id: int):
        response = self.http.get(f"productos/{producto_id}/")
        response.raise_for_status()
        return response.json()

    def actualizar(self, producto_id, data, files=None):
        r = self.http.put(
            f"productos/{producto_id}/",
            data=data,
            files=files
        )
        r.raise_for_status()
        return r.json()

    def eliminar(self, producto_id: int):
        response = self.http.delete(f"productos/{producto_id}/")
        response.raise_for_status()
        return True
    
    
    def crear(self, data, files=None):
        r = self.http.post("productos/", data=data, files=files)
        r.raise_for_status()
        return r.json()