# pasarela_mercadopago/pagos/views.py
import os
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from dotenv import load_dotenv
from django.shortcuts import redirect
from .services import crear_preferencia_pago

# Carga las variables de entorno desde el archivo .env 
load_dotenv()

def feedback_view(request):
    """
    Recibe al usuario cuando vuelve de la interfaz de Mercado Pago.
    Lee los datos que vienen por la URL y registra el cobro en el ViewSet.
    """
    # Mercado Pago envía estos parámetros en la URL (Query Params) tras el pago
    status_mp = request.GET.get('status')              # 'approved', 'rejected', 'pending'
    payment_id = request.GET.get('payment_id')          # ID único de la transacción en MP
    factura_id = request.GET.get('external_reference')  # El ID de la Factura que le enviamos
    merchant_order_id = request.GET.get('merchant_order_id')

    # Si el pago no fue aprobado, se frena el flujo y se notifica al frontend
    if status_mp != 'approved':
        return render(request, 'pagos/resultado.html', {
            'estado': 'error',
            'mensaje': f'El pago no pudo ser procesado. Estado: {status_mp}'
        })

    # Datos estructurados para enviar al endpoint interno de tu PagoViewSet
    payload_pago = {
        "factura": int(factura_id),
        "monto": request.GET.get('preference_id'), # NOTA: En producción acá se consulta el monto real vía API de MP con el payment_id
        "metodo_pago": "tarjeta",
        "referencia": payment_id  # Se guarda el payment_id de MP para el control de duplicados
    }

    # Se realiza la petición interna al método aislado '@action(url_path="registrar-pago-web")'
    try:
        # 1. Leemos la URL base desde el .env (ej: http://127.0.0.1:8000/api/)
        api_base = os.getenv("API_BASE_URL")
        
        # 2. Construimos la URL del endpoint concatenando el recurso específico de forma limpia
        # Nos aseguramos de que no queden dobles barras (//) si la variable termina en barra
        if api_base.endswith('/'):
            url_endpoint = f"{api_base}pagos/registrar-pago-web/"
        else:
            url_endpoint = f"{api_base}/pagos/registrar-pago-web/"
        
        # 3. Enviamos la petición POST al backend
        response = requests.post(url_endpoint, json=payload_pago)
        
        if response.status_code in [200, 201]:
            # El PagoViewSet aceptó el registro o ignoró un duplicado de red de forma segura
            return render(request, 'pagos/resultado.html', {
                'estado': 'exito',
                'factura_id': factura_id,
                'pago_id': payment_id
            })
        else:
            # Captura errores de validación del backend sin tumbar la ejecución
            return render(request, 'pagos/resultado.html', {
                'estado': 'error',
                'mensaje': f'Error al asentar el pago en el sistema: {response.text}'
            })
            
    except requests.exceptions.RequestException as e:
        return render(request, 'pagos/resultado.html', {
            'estado': 'error',
            'mensaje': f'No se pudo conectar con la API de facturación: {e}'
        })
        

def iniciar_pago_view(request, factura_id):
    """
    Punto de entrada para la web.
    Recibe el ID de la factura, arma el concepto y genera el enlace de Mercado Pago.
    """
    # NOTA: En un flujo integrado, aquí deberías consultar tu modelo Factura o Base de Datos
    # para obtener el monto real y el detalle de los repuestos.
    # Por ahora simulamos un ítem genérico con un valor de prueba o capturado por parámetro.
    
    monto_factura = request.GET.get('monto', 1500.00) # Valor fallback si no viene en la query string

    # Estructura obligatoria estricta que exige el SDK de Mercado Pago
    items_pago = [
        {
            "id": f"FAC-{factura_id}",
            "title": f"Pago de Factura Nro {factura_id} - MOTO-TOP",
            "quantity": 1,
            "currency_id": "ARS", # Moneda local
            "unit_price": float(monto_factura)
        }
    ]

    # Invocamos la función de services.py pasando el ID de la factura como external_reference
    preferencia = crear_preferencia_pago(items=items_pago, external_reference=factura_id)

    if preferencia and "init_point" in preferencia:
        # 'init_point' es la URL oficial de Mercado Pago para procesar tarjetas/efectivo.
        # Redirigimos al usuario inmediatamente allí.
        return redirect(preferencia["init_point"])
    else:
        # Si la API de MP falla, notificamos el error usando el template de control
        return render(request, 'pagos/resultado.html', {
            'estado': 'error',
            'mensaje': 'No se pudo generar la orden de pago en Mercado Pago. Reintente más tarde.'
        })
        
        