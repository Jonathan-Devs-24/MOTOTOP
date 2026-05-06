# desktop/app/services/rubro_service.py
class RubroService:

    def __init__(self, http):
        self.http = http

    def listar(self):
        r = self.http.get("rubros/")
        r.raise_for_status()
        return r.json()

    def crear(self, data):
        r = self.http.post("rubros/", data)
        r.raise_for_status()
        return r.json()

    def eliminar(self, rubro_id):
        r = self.http.delete(f"rubros/{rubro_id}/")
        r.raise_for_status()