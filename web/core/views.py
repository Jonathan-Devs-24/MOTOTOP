# web/core/views.py
from django.shortcuts import render
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
