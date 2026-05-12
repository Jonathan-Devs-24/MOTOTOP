# desktop/app/services/zona_service.py
class ZonaService:
    def __init__(self, http):
        self.http = http

    def listar(self):
        r = self.http.get("zonas/")
        r.raise_for_status()
        return r.json()

    def crear(self, data):
        r = self.http.post("zonas/", data)
        r.raise_for_status()
        return r.json()

    def actualizar(self, zona_id, data):
        r = self.http.put(f"zonas/{zona_id}/", data)
        r.raise_for_status()
        return r.json()

    def eliminar(self, zona_id):
        r = self.http.delete(f"zonas/{zona_id}/")
        r.raise_for_status()
        return True