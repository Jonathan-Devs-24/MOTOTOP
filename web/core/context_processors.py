# web/core/context_processors.py
# Para no repetir código en las vistas, 
# se puede usar un context processor para pasar la variable a todas las 
# plantillas.
import requests
from django.conf import settings

def pedidos_cliente_context(request):
    token = request.session.get('access_token')
    username = request.session.get('username')
    tiene_pedidos = False

    if token and username:
        base_api = settings.API_BASE_URL.rstrip('/')
        if not base_api.endswith('/api'):
            base_api = f"{base_api}/api"

        headers = {'Authorization': f'Bearer {token}'}

        try:
            # 1. Obtener los clientes para identificar el ID del cliente logueado
            res_clientes = requests.get(f"{base_api}/clientes/", headers=headers, timeout=4)
            cliente_id = None
            if res_clientes.status_code == 200:
                data_c = res_clientes.json()
                lista_c = data_c.get('results', data_c) if isinstance(data_c, dict) else data_c
                for c in lista_c:
                    # Si el serializer devuelve usuario ID o datos
                    if c.get('usuario') or c.get('email'):
                        cliente_id = c.get('id')
                        break

            # 2. Consultar pedidos y verificar si existen para ese cliente
            res_pedidos = requests.get(f"{base_api}/pedidos/", headers=headers, timeout=4)
            if res_pedidos.status_code == 200:
                data_p = res_pedidos.json()
                lista_p = data_p.get('results', data_p) if isinstance(data_p, dict) else data_p
                
                # Filtrar pedidos pertenecientes al cliente
                pedidos_usuario = [
                    p for p in lista_p 
                    if isinstance(p.get('cliente'), dict) and p.get('cliente', {}).get('id') == cliente_id
                ] if cliente_id else lista_p

                tiene_pedidos = len(pedidos_usuario) > 0
        except requests.exceptions.RequestException:
            tiene_pedidos = False

    return {
        'usuario_tiene_pedidos': tiene_pedidos
    }
    



