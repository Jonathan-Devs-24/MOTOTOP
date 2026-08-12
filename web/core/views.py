# web/core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
import requests

def home(request):
    todos_los_productos = []
    productos_en_promocion = []
    promociones_activas = []
    ahora = timezone.now().date()

    try:
        # 1. Obtener Promociones Activas desde la API
        res_promo = requests.get(f"{settings.API_BASE_URL}promociones/", timeout=5)
        if res_promo.status_code == 200:
            promociones = res_promo.json()
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
                relaciones = res_rel.json()
                if isinstance(relaciones, list):
                    for rel in relaciones:
                        if isinstance(rel, dict) and rel.get('promocion') in id_promos_activas:
                            relaciones_promo[rel['producto']] = rel

        # 2. Obtener Productos
        res_productos = requests.get(f"{settings.API_BASE_URL}productos/", timeout=5)
        if res_productos.status_code == 200:
            data_prod = res_productos.json()
            productos_lista = data_prod.get('results', data_prod) if isinstance(data_prod, dict) else data_prod

            if isinstance(productos_lista, list):
                for prod in productos_lista:
                    precio_base = float(prod['precio_base'])
                    prod_id = prod['id']

                    if prod_id in relaciones_promo:
                        rel = relaciones_promo[prod_id]
                        valor_descuento = float(rel['valor_descuento'])
                        tipo_desc = str(rel.get('tipo_descuento', '')).strip().lower()

                        # Acepta '%', 'porcentaje', 'porcentual', etc.
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

    except requests.exceptions.RequestException:
        messages.error(request, 'No se pudo conectar con el catálogo de la API.')

    context = {
        'todos_los_productos': todos_los_productos,
        'productos_en_promocion': productos_en_promocion,
        'promociones_activas': promociones_activas,
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


