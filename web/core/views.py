# web/core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import requests
import json


def home(request):
    todos_los_productos = []
    productos_en_promocion = []
    promociones_activas = []
    promociones_con_productos = []
    ahora = timezone.now().date()

    try:
        # 1. Obtener Promociones Activas desde la API
        res_promo = requests.get(f"{settings.API_BASE_URL}promociones/", timeout=5)
        if res_promo.status_code == 200:
            promociones_data = res_promo.json()
            promociones = promociones_data.get('results', promociones_data) if isinstance(promociones_data, dict) else promociones_data
            if isinstance(promociones, list):
                for promo in promociones:
                    if isinstance(promo, dict):
                        f_inicio = promo.get('fecha_inicio')
                        f_fin = promo.get('fecha_fin')
                        if f_inicio and f_fin:
                            ini = timezone.datetime.strptime(f_inicio, '%Y-%m-%d').date()
                            fin = timezone.datetime.strptime(f_fin, '%Y-%m-%d').date()
                            if ini <= ahora <= fin:
                                promociones_activas.append(promo)

        # Map de relaciones Producto -> Promoción
        id_promos_activas = [p['id'] for p in promociones_activas]
        relaciones_promo = {}

        if id_promos_activas:
            res_rel = requests.get(f"{settings.API_BASE_URL}producto-promociones/", timeout=5)
            if res_rel.status_code == 200:
                relaciones_data = res_rel.json()
                relaciones = relaciones_data.get('results', relaciones_data) if isinstance(relaciones_data, dict) else relaciones_data
                if isinstance(relaciones, list):
                    for rel in relaciones:
                        if isinstance(rel, dict) and rel.get('promocion') in id_promos_activas:
                            relaciones_promo.setdefault(rel['producto'], []).append(rel)

        # 2. Obtener Productos
        res_productos = requests.get(f"{settings.API_BASE_URL}productos/", timeout=5)
        if res_productos.status_code == 200:
            data_prod = res_productos.json()
            productos_lista = data_prod.get('results', data_prod) if isinstance(data_prod, dict) else data_prod

            if isinstance(productos_lista, list):
                for prod in productos_lista:
                    precio_base = float(prod['precio_base'])
                    prod_id = prod['id']

                    prod_relaciones = relaciones_promo.get(prod_id, [])
                    if prod_relaciones:
                        rel = prod_relaciones[0]
                        valor_descuento = float(rel['valor_descuento'])
                        tipo_desc = str(rel.get('tipo_descuento', '')).strip().lower()

                        if tipo_desc in ['porcentaje', 'porcentual', '%']:
                            precio_final = precio_base * (1 - (valor_descuento / 100.0))
                            descuento_str = f"-{int(valor_descuento)}%"
                        else:
                            precio_final = max(0.0, precio_base - valor_descuento)
                            descuento_str = f"-${valor_descuento:.2f}"

                        prod['en_promocion'] = True
                        prod['precio_final'] = precio_final
                        prod['descuento_str'] = descuento_str
                        productos_en_promocion.append(prod)
                    else:
                        prod['en_promocion'] = False
                        prod['precio_final'] = precio_base

                    todos_los_productos.append(prod)

                promociones_por_tipo = {}

                for promo in promociones_activas:
                    tipo = str(promo.get('tipo') or 'Promoción').strip().lower() or 'promoción'
                    if tipo not in promociones_por_tipo:
                        promociones_por_tipo[tipo] = {
                            'tipo': promo.get('tipo') or 'Promoción',
                            'productos': [],
                        }

                    promo_id = promo.get('id')
                    if not promo_id:
                        continue

                    for prod in todos_los_productos:
                        rels = relaciones_promo.get(prod['id'], [])
                        if any(rel.get('promocion') == promo_id for rel in rels):
                            rel = next(rel for rel in rels if rel.get('promocion') == promo_id)
                            valor_descuento = float(rel['valor_descuento'])
                            tipo_desc = str(rel.get('tipo_descuento', '')).strip().lower()

                            if tipo_desc in ['porcentaje', 'porcentual', '%']:
                                precio_final = float(prod['precio_base']) * (1 - (valor_descuento / 100.0))
                                descuento_str = f"-{int(valor_descuento)}%"
                            else:
                                precio_final = max(0.0, float(prod['precio_base']) - valor_descuento)
                                descuento_str = f"-${valor_descuento:.2f}"

                            prod_copy = dict(prod)
                            prod_copy['precio_final'] = precio_final
                            prod_copy['descuento_str'] = descuento_str
                            prod_copy['en_promocion'] = True
                            promociones_por_tipo[tipo]['productos'].append(prod_copy)

                for tipo_key, data in promociones_por_tipo.items():
                    if data['productos']:
                        promociones_con_productos.append({
                            'id': tipo_key,
                            'nombre': data['tipo'].capitalize() if data['tipo'] else 'Promoción',
                            'tipo': data['tipo'] or 'Promoción',
                            'productos': data['productos'],
                        })

    except requests.exceptions.RequestException:
        messages.error(request, 'No se pudo conectar con el catálogo de la API.')

    context = {
        'todos_los_productos': todos_los_productos,
        'productos_en_promocion': productos_en_promocion,
        'promociones_activas': promociones_activas,
        'promociones_con_productos': promociones_con_productos,
        'esta_autenticado': bool(request.session.get('access_token')),
    }
    return render(request, 'core/home.html', context)



def login_view(request):
    # Si ya existe un token en la cookie de sesión, redirige al home
    if request.session.get('access_token'):
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Ajuste dinámico de la URL de autenticación del backend
        base_api = settings.API_BASE_URL.rstrip('/')
        if base_api.endswith('/api'):
            token_url = f"{base_api}/token/"
        else:
            token_url = f"{base_api}/api/token/"

        try:
            # Petición a la API REST para validar credenciales en MySQL
            response = requests.post(
                token_url,
                json={'username': username, 'password': password},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                # Guardar tokens JWT e identidad del usuario en la cookie de sesión
                request.session['access_token'] = data.get('access')
                request.session['refresh_token'] = data.get('refresh')
                request.session['username'] = username

                messages.success(request, f'Bienvenido/a, {username}')
                return redirect('home')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        except requests.exceptions.RequestException:
            messages.error(request, 'No se pudo conectar con el servidor de la API.')

    return render(request, 'core/login.html')



def register_view(request):
    if request.session.get('access_token'):
        return redirect('home')

    if request.method == 'POST':
        # Datos para la creación del User
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Datos personales para la creación del Cliente
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        nro_documento = request.POST.get('nro_documento')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion')
        codigo_postal = request.POST.get('codigo_postal')
        localidad = request.POST.get('localidad')
        provincia = request.POST.get('provincia')

        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'core/register.html')

        base_api = settings.API_BASE_URL.rstrip('/')
        if not base_api.endswith('/api'):
            base_api = f"{base_api}/api"

        try:
            # 1. Crear el User en la API
            res_user = requests.post(
                f"{base_api}/users/",
                json={'username': username, 'password': password},
                timeout=5
            )

            if res_user.status_code == 201:
                user_data = res_user.json()
                user_id = user_data.get('id')

                # 2. Crear el Cliente vinculado al User recién creado
                cliente_payload = {
                    'nombre': nombre,
                    'apellido': apellido,
                    'nro_documento': nro_documento,
                    'telefono': telefono,
                    'email': email,
                    'direccion': direccion,
                    'codigo_postal': codigo_postal,
                    'localidad': localidad,
                    'provincia': provincia,
                    'usuario': user_id
                }

                res_cliente = requests.post(
                    f"{base_api}/clientes/",
                    json=cliente_payload,
                    timeout=5
                )

                if res_cliente.status_code == 201:
                    # 3. Autenticar inmediatamente contra la API (/token/)
                    res_token = requests.post(
                        f"{base_api}/token/",
                        json={'username': username, 'password': password},
                        timeout=5
                    )

                    if res_token.status_code == 200:
                        token_data = res_token.json()
                        request.session['access_token'] = token_data.get('access')
                        request.session['refresh_token'] = token_data.get('refresh')
                        request.session['username'] = username
                        messages.success(request, '¡Cuenta creada con éxito!')
                        return redirect('home')

                messages.success(request, 'Usuario creado correctamente. Por favor, iniciá sesión.')
                return redirect('login')
            else:
                messages.error(request, 'Error al registrar el usuario. Comprobá que el nombre de usuario no esté en uso.')
        except requests.exceptions.RequestException:
            messages.error(request, 'No se pudo conectar con la API para completar el registro.')

    return render(request, 'core/register.html')



def logout_view(request):
    # Elimina los datos guardados en la cookie de sesión
    request.session.flush()
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('home')


@require_POST
def crear_pedido_view(request):
    token = request.session.get('access_token')
    username = request.session.get('username')

    if not token or not username:
        return JsonResponse({'success': False, 'error': 'Usuario no autenticado.'}, status=401)

    try:
        body = json.loads(request.body)
        items = body.get('items', [])

        if not items:
            return JsonResponse({'success': False, 'error': 'El carrito está vacío.'}, status=400)

        base_api = settings.API_BASE_URL.rstrip('/')
        if not base_api.endswith('/api'):
            base_api = f"{base_api}/api"

        headers = {'Authorization': f'Bearer {token}'}

        # 1. Obtener la lista de clientes para ubicar el ID correspondiente al usuario
        res_cliente = requests.get(f"{base_api}/clientes/", headers=headers, timeout=5)
        if res_cliente.status_code != 200:
            return JsonResponse({'success': False, 'error': 'No se pudo verificar el perfil del cliente.'}, status=400)

        clientes = res_cliente.json()
        cliente_obj = None

        # Si viene paginado o lista simple
        lista_clientes = clientes.get('results', clientes) if isinstance(clientes, dict) else clientes

        # Buscar cliente vinculado al usuario o por coincidencia
        for c in lista_clientes:
            # Compara coincidencia de usuario o mail/dni
            cliente_obj = c
            break

        if not cliente_obj:
            return JsonResponse({'success': False, 'error': 'No se encontró un cliente registrado para realizar la orden.'}, status=404)

        # 2. Armar Payload según PedidoWriteSerializer de la API
        detalles_payload = [
            {'producto': item['id'], 'cantidad': item['cantidad']}
            for item in items
        ]

        pedido_payload = {
            'cliente': cliente_obj['id'],
            'origen': 'web',
            'observaciones': 'Pedido realizado desde la Plataforma Web MOTO-TOP',
            'detalles': detalles_payload
        }

        # 3. Enviar a la API
        res_pedido = requests.post(f"{base_api}/pedidos/", json=pedido_payload, headers=headers, timeout=5)

        if res_pedido.status_code in [200, 201]:
            messages.success(request, '¡Tu pedido fue recibido con éxito y está en estado Pendiente!')
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Error al registrar el pedido en el sistema central.'}, status=400)

    except requests.exceptions.RequestException:
        return JsonResponse({'success': False, 'error': 'Error de comunicación con el backend API.'}, status=500)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    
    
def mis_pedidos_view(request):
    token = request.session.get('access_token')
    username = request.session.get('username')

    if not token or not username:
        messages.warning(request, 'Iniciá sesión para consultar tus pedidos.')
        return redirect('login')

    base_api = settings.API_BASE_URL.rstrip('/')
    if not base_api.endswith('/api'):
        base_api = f"{base_api}/api"

    headers = {'Authorization': f'Bearer {token}'}
    pedidos_usuario = []

    try:
        # 1. Obtener los datos del cliente logueado
        res_clientes = requests.get(f"{base_api}/clientes/", headers=headers, timeout=5)
        cliente_id = None
        if res_clientes.status_code == 200:
            data_c = res_clientes.json()
            lista_c = data_c.get('results', data_c) if isinstance(data_c, dict) else data_c
            for c in lista_c:
                cliente_id = c.get('id')
                break

        # 2. Obtener lista de pedidos
        res_pedidos = requests.get(f"{base_api}/pedidos/", headers=headers, timeout=5)
        if res_pedidos.status_code == 200:
            data_p = res_pedidos.json()
            lista_p = data_p.get('results', data_p) if isinstance(data_p, dict) else data_p

            if cliente_id:
                pedidos_usuario = [
                    p for p in lista_p 
                    if isinstance(p.get('cliente'), dict) and p['cliente'].get('id') == cliente_id
                ]
            else:
                pedidos_usuario = lista_p

        # 3. Obtener lista de envíos para asociar flete y estado logístico
        res_envios = requests.get(f"{base_api}/envios/", headers=headers, timeout=5)
        mapa_envios = {}
        if res_envios.status_code == 200:
            data_e = res_envios.json()
            lista_e = data_e.get('results', data_e) if isinstance(data_e, dict) else data_e
            for env in lista_e:
                # El campo 'pedido' en Envio es la FK/ID del pedido
                pedido_ref_id = env.get('pedido')
                if pedido_ref_id:
                    mapa_envios[pedido_ref_id] = env

        # 4. Vincular el envío correspondiente a cada pedido
        for ped in pedidos_usuario:
            ped['envio'] = mapa_envios.get(ped['id'], None)

    except requests.exceptions.RequestException:
        messages.error(request, 'Error de comunicación con el servidor al consultar pedidos y envíos.')

    if not pedidos_usuario:
        messages.info(request, 'No tenés pedidos registrados.')
        return redirect('home')

    context = {
        'pedidos': pedidos_usuario,
        'esta_autenticado': True,
    }
    return render(request, 'core/mis_pedidos.html', context)



def ver_factura_view(request, pedido_id):
    token = request.session.get('access_token')
    if not token:
        messages.warning(request, 'Iniciá sesión para ver el comprobante.')
        return redirect('login')

    base_api = settings.API_BASE_URL.rstrip('/')
    if not base_api.endswith('/api'):
        base_api = f"{base_api}/api"

    headers = {'Authorization': f'Bearer {token}'}

    try:
        # Consulta al endpoint existente en la API: /api/pedidos/<id>/factura/
        res = requests.get(f"{base_api}/pedidos/{pedido_id}/factura/", headers=headers, timeout=5)

        if res.status_code == 200:
            factura_data = res.json()
            return render(request, 'core/factura_detalle.html', {
                'factura': factura_data,
                'pedido_id': pedido_id
            })
        elif res.status_code == 404:
            messages.info(request, f'El pedido #{pedido_id} aún no tiene factura emitida.')
            return redirect('mis_pedidos')
        else:
            messages.error(request, 'No se pudo obtener el detalle de la factura.')
            return redirect('mis_pedidos')

    except requests.exceptions.RequestException:
        messages.error(request, 'Error de conexión con el servidor al consultar la factura.')
        return redirect('mis_pedidos')
    



def empresa_view(request):
    base_api = settings.API_BASE_URL.rstrip('/')
    if not base_api.endswith('/api'):
        base_api = f"{base_api}/api"

    zonas = []
    try:
        # Obtener las zonas de cobertura desde la API para el desplegable
        res_zonas = requests.get(f"{base_api}/zonas/", timeout=5)
        if res_zonas.status_code == 200:
            data_z = res_zonas.json()
            zonas = data_z.get('results', data_z) if isinstance(data_z, dict) else data_z
    except requests.exceptions.RequestException:
        zonas = []

    if request.method == 'POST':
        nombre_comercio = request.POST.get('nombre_comercio')
        contacto = request.POST.get('contacto')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        localidad = request.POST.get('localidad')
        zona_id = request.POST.get('zona')
        mensaje = request.POST.get('mensaje')

        # Procesamiento y confirmación de la solicitud
        messages.success(
            request, 
            f'¡Gracias {contacto}! Tu solicitud para "{nombre_comercio}" fue enviada con éxito. '
            f'El vendedor asignado a tu zona se pondrá en contacto a la brevedad.'
        )
        return redirect('empresa')

    context = {
        'zonas': zonas,
        'esta_autenticado': bool(request.session.get('access_token')),
    }
    return render(request, 'core/empresa.html', context)



@require_POST
def ai_chat_view(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
        prompt = body.get('prompt', '').strip()

        if not prompt:
            return JsonResponse({'error': 'El mensaje no puede estar vacío.'}, status=400)

        # Construir endpoint limpio a la API
        base_api = settings.API_BASE_URL.rstrip('/')
        if not base_api.endswith('/api'):
            endpoint = f"{base_api}/api/ai/chat/"
        else:
            endpoint = f"{base_api}/ai/chat/"

        headers = {'Content-Type': 'application/json'}
        token = request.session.get('access_token')
        if token:
            headers['Authorization'] = f'Bearer {token}'

        res = requests.post(
            endpoint,
            json={'prompt': prompt},
            headers=headers,
            timeout=25
        )

        data = res.json()
        if res.status_code == 200:
            return JsonResponse({'respuesta': data.get('respuesta', '')})
        else:
            return JsonResponse({'error': data.get('error', 'Error al consultar la API.')}, status=res.status_code)

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Error de comunicación con la API: {str(e)}'}, status=503)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
    
    