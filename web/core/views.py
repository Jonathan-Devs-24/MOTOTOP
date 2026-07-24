# web/core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
import requests

def home(request):
    promociones_activas = [] # Lista vacia para almacenar promociones activas
    ahora = timezone.now().date() # Obtener la fecha actual respetando zona horaria
    
    # Inicializamos la lista fuera del bloque para asegurar que exista si ocurre una excepción
    productos_en_promocion = [] 
    
    try:
        # Realiza la petición GET a la API para obtener promociones con un tiempo de espera de 5 segundos
        response_promo = requests.get(f"{settings.API_BASE_URL}promociones/", timeout=5)
        
        #verificamos que la API responda correctamente
        if response_promo.status_code == 200:
            
            # Convertimos la respuesta a JSON
            promociones = response_promo.json()
            
            # CONTROL DE SEGURIDAD: Validamos que 'promociones' sea efectivamente una lista antes de iterar
            if isinstance(promociones, list):
                
                # Recorremos cada una de las promociones devultas por el backend
                for promo in promociones:
                    
                    # Aseguramos que cada elemento interno sea un diccionario antes de usar .get()
                    if isinstance(promo, dict):
                        
                        # Obtenemos las cadena de texto correspondientes a las 
                        # fechas de inicio y fin de la promoción
                        f_inicio = promo.get('fecha_inicio')
                        f_fin = promo.get('fecha_fin')
                        
                        # Validamos que ambos campos de ehcas existan y no sean nulos
                        if f_inicio and f_fin:
                            
                            ini = timezone.datetime.strptime(f_inicio, '%Y-%m-%d').date()
                            fin = timezone.datetime.strptime(f_fin, '%Y-%m-%d').date()
                            
                            # Comprueba si la fecha actual se encuentra dentro del rango de vigencia de la promocion
                            if ini <= ahora <= fin:
                                promociones_activas.append(promo)
                        
        # Realizamos la petición GET al endpoint que vincula los productos con las promociones con un tiempo de espera de 5 segundos
        response_prod_promo = requests.get(f"{settings.API_BASE_URL}producto-promociones/", timeout=5)
        
        # Inicializa la lista donde se guardará la información final procesada de los porductos en oferta
        productos_en_promocion = []
        
        # Validamos que la petición a la API sea exitosa
        if response_prod_promo.status_code == 200 and promociones_activas:
            
            # Generamos una lista rápida con los IDs únicos de todas las promociones que estan activas
            id_promos_activas = [p['id'] for p in promociones_activas]
            
            # Copnvertimos la respuesta a un formato JSON
            relaciones = response_prod_promo.json()
            
            # Realiza una petición GET para obtener el listado completo de prodcutos
            response_productos = requests.get(f"{settings.API_BASE_URL}productos/", timeout=5)
            
            # Verificamos el OK 200
            if response_productos.status_code == 200: 
                
                # Transforma la lista de productos en un diccionario
                productos_dic = {p['id']: p for p in response_productos.json()}
                
                # Recorremos cada relacion producto promocion recibido por el backend
                if isinstance(relaciones, list):
                    for rel in relaciones:
                        if isinstance(rel, dict):
                            
                            # comprobamso si el ID de la promocionde de este vinculo forma parte de las promociones activas
                            if rel['promocion'] in id_promos_activas:
                                
                                # Obtemos el ID de la promoción involucrada en el descuento
                                prod_id = rel['producto']
                                
                                # Verificamos si el ID del prodcuto existe           
                                if prod_id in productos_dic:
                                    
                                    # Recupera la info. completa del prodcuto correspondiente
                                    prod = productos_dic[prod_id]
                                    
                                    precio_base = float(prod['precio_base'])
                                    valor_descuento = float(rel['valor_descuento'])
                                    
                                    # Determinando la lógica de cálculo evaluado si el tipo de descuento es en porcentaje
                                    if rel['tipo_descuento'].lower() == 'porcentaje':
                                        precio_final = precio_base * (1 - (valor_descuento / 100))
                                    else:
                                        precio_final = max(0.0, precio_base - valor_descuento)
                                        
                                    productos_en_promocion.append({
                                        'nombre': prod['nombre'],
                                        'imagen': prod.get('img'),
                                        'precio_base': precio_base,
                                        'precio_final': precio_final,
                                        # Genera la cadena de texto que se mostrará en la etiqueta de oferta (Ej: "15% OFF" o "$500 OFF")
                                        'descuento_str': f"{int(valor_descuento)}% OFF" if rel['tipo_descuento'].lower() == 'porcentaje' else f"${valor_descuento} OFF"
                                    })
                                    
    except requests.exceptions.RequestException:
        productos_en_promocion = []
        
    return render(request, 'core/home.html', {'productos_en_promocion': productos_en_promocion})


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
            
            